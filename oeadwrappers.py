import oead
import os
from pathlib import Path

# A set of wrapper functions around oead for handling SARC and BYAML files for Splatoon 1

def extractSARC(inputSARC):
    with open(inputSARC, "rb") as f:
        sarcData = f.read()

    if oead.yaz0.get_header(sarcData):
        sarcData = oead.yaz0.decompress(sarcData)

    sarc = oead.Sarc(sarcData)

    outputDir = Path(f"{inputSARC}_extracted")
    outputDir.mkdir(exist_ok=True)

    for file in sarc.get_files():
        outputPath = outputDir / file.name
        parentDir = outputPath.parent

        if parentDir.exists() and not parentDir.is_dir():
            print(f"Removing conflicting file: {parentDir}")
            parentDir.unlink()

        parentDir.mkdir(parents=True, exist_ok=True)

        with open(outputPath, "wb") as out_file:
            out_file.write(file.data)

def packSARC(inputDir: str, outputPath: str, compress: bool = True):
    inputPath = Path(inputDir)

    builder = oead.SarcWriter(endian=oead.Endianness.Big, mode=oead.SarcWriter.Mode.Legacy)

    for filePath in inputPath.rglob("*"):
        if filePath.is_file():
            relativePath = filePath.relative_to(inputPath).as_posix()
            with open(filePath, "rb") as f:
                builder.files[relativePath] = f.read()

    sarcData = builder.write()
    
    if isinstance(sarcData, tuple):
       sarcData = sarcData[1]

    if compress:
        sarcData = oead.yaz0.compress(sarcData, 0, 7)

    with open(outputPath, "wb") as f:
        f.write(sarcData)

    print(f"Packed SARC: {outputPath}")
    
def convertFromBYAML(inputBYAML):
    # print(inputBYAML)
    with open(inputBYAML, "rb") as f:
        info = oead.byml.from_binary(f.read())
        ouputYAML = oead.byml.to_text(info)
        # print(ouputYAML)
        outputYamlName = os.path.splitext(inputBYAML)
        print(outputYamlName[0])
    with open(f"{outputYamlName[0]}.yaml", "w") as file:
        file.write(ouputYAML)
        
def convertToBYAML(inputYaml):
    with open(inputYaml, "r", encoding="utf-8") as file:
        content = file.read()
     
    convdBYAML = oead.byml.from_text(content)
    outputBYAMLName = os.path.splitext(inputYaml)
    print(outputBYAMLName[0])
    
    with open(f"{outputBYAMLName[0]}.byaml", "wb") as f:
        f.write(oead.byml.to_binary(data=convdBYAML, big_endian=True, version=1))

