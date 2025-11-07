import binascii
import enum
import io

ENDIAN = "little"


class Action(enum.IntEnum):
    SourceRead = 0
    TargetRead = 1
    SourceCopy = 2
    TargetCopy = 3


def convert_uint(b: bytes):
    return int.from_bytes(b, ENDIAN, signed=False)


def read_number_io(b: io.BytesIO) -> int:
    data, shift = 0, 1

    # this was basically directly copied from the bps_spec
    while(True):
        x = b.read(1)
        if len(x) == 0:
            return None
        x = convert_uint(x)
        data += (x & 0x7f) * shift
        if (x & 0x80):
            break
        shift <<= 7
        data += shift

    return data


def read_number(b: bytes) -> tuple:
    """ Read a number that starts at the beginning of the bytes

    returns a tuple of the number read and remaining bytes
    """
    bio = io.BytesIO(b)
    data = read_number_io(bio)
    return data, bio.read()


class InvalidPatch(Exception):
    def __init__(self, msg):
        self.msg = msg


class BPSPatch(object):
    MAGIC_HEADER = "BPS1".encode("UTF-8")

    def __init__(self, patch: bytes):
        header = patch[:4]

        if header != self.MAGIC_HEADER:
            raise InvalidPatch(f"Magic header {header} is incorrect")

        self.source_checksum = convert_uint(patch[-4*3:-4*2])
        self.target_checksum = convert_uint(patch[-4*2:-4*1])
        self.patch_checksum = convert_uint(patch[-4*1:])

        calculated_checksum = binascii.crc32(patch[:-4])

        if self.patch_checksum != calculated_checksum:
            raise InvalidPatch(
                f"Patch Checksum {self.patch_checksum} does not match "
                f"actual checksum {calculated_checksum}"
            )

        remainder = patch[4:]

        self.source_size, remainder = read_number(remainder)
        self.target_size, remainder = read_number(remainder)
        self.metadata_size, remainder = read_number(remainder)

        self.metadata = remainder[:self.metadata_size].decode("UTF-8")

        # actions is everything else other than the header and footer
        self.actions = remainder[self.metadata_size:-12]

    def patch_rom(self, source: bytes) -> bytes:
        if len(source) != self.source_size:
            raise InvalidPatch(
                f"source size {len(source)} does not match "
                f"expected {self.source_size}")

        source_checksum = binascii.crc32(source)
        if source_checksum != self.source_checksum:
            raise InvalidPatch(
                f"source checksum {source_checksum} does not match "
                f"expected {self.source_checksum}")

        target = bytearray(self.target_size)

        actions = io.BytesIO(self.actions)

        output_offset = 0
        source_relative_offset = 0
        target_relative_offset = 0

        while(True):
            action = read_number_io(actions)
            if action is None:
                break

            command = action & 3
            length = (action >> 2) + 1

           # print(f"Command {command}, length {length}") #No need to spam the log with this

            if command == Action.SourceRead:
                # consume some number of bytes from source file
                target[output_offset:output_offset + length] = \
                    source[output_offset:output_offset + length]
                output_offset += length

            elif command == Action.TargetRead:
                # consume some number of bytes from patch file
                target[output_offset:output_offset + length] = \
                    actions.read(length)
                output_offset += length

            elif command == Action.SourceCopy:
                # consume some number of bytes from source file, but from
                # somewhere else.  This action seems unnecessarily complicated
                data = read_number_io(actions)
                source_relative_offset += (-1 if data & 1 else 1) * (data >> 1)
                target[output_offset:output_offset + length] = \
                    source[
                        source_relative_offset:source_relative_offset + length]

                output_offset += length
                source_relative_offset += length

            elif command == Action.TargetCopy:
                # consume some number of bytes from the target file
                data = read_number_io(actions)
                target_relative_offset += (-1 if data & 1 else 1) * (data >> 1)
                # unfortunately it is not safe to optimize this, as one of the
                # documented use cases is to write a single byte then duplicate
                # that byte over and over filling out an array.
                for _ in range(length):
                    target[output_offset] = target[target_relative_offset]
                    output_offset += 1
                    target_relative_offset += 1

        target_checksum = binascii.crc32(target)

        if target_checksum != self.target_checksum:
            raise InvalidPatch(
                f"target checksum {target_checksum} does not match "
                f"expected {self.target_checksum}")

        return target
