import os
import oead
from ruamel.yaml import YAML
import random
from pathlib import Path

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



extractSARC('Static.pack')
World00ArchivePath = 'Static.pack_extracted/Map/Fld_World00_Wld.szs'
extractSARC(World00ArchivePath)
convertFromBYAML(f"{World00ArchivePath}_extracted/Fld_World00_Wld.byaml")
convertFromBYAML('Static.pack_extracted/Mush/MapInfo.byaml')

startLine = 5

with open(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml") as f:
    lines = f.readlines()[startLine:]
    stageNames = [ # Loop through every word in the YAML and filter out all of the stage names
        word for line in lines
        for word in line.split()
        if word.endswith('_Msn') 
        ]

bossStageNames = stageNames[-5:]
bossStageNames = bossStageNames[0:4]
stageNames = stageNames[:-5]

print(bossStageNames)
print(stageNames)

def addRandomizedKettles(filePath, replacementStageNames):
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(filePath, 'r') as f:
        data = yaml.load(f)

    replacementIter = iter(replacementStageNames)
    for obj in data.get('Objs', []):
        if 'DestMapFileName' in obj:
            try:
                obj['DestMapFileName'] = next(replacementIter)
            except StopIteration:
                break

    with open(filePath, 'w') as f:
        yaml.dump(data, f)

def randomizeMusic():
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible music tracks
    BGMTypeList =  ['TakoJoban', 'TakoBase', 'Race', 'Missile', 'Rival']

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        print("Error: The YAML structure is not a list.")
        return

    for obj in data:
        if 'BGMType' in obj:
            obj['BGMType'] = random.choice(BGMTypeList)

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'w') as f:
        yaml.dump(data, f)

def randomizeInkColors():
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible ink colors
    inkColors =  ['DarkBlue', 'Green', 'Lilac', 'LumiGreen', 'NightLumiGreen', 'MothGreen', 'Marigold', 'NightMarigold', 'Orange', 'Soda', 'Turquoise', 'Yellow']

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        print("Error: The YAML structure is not a list.")
        return

    for obj in data:
        if 'TeamColor_Msn' in obj:
            obj['TeamColor_Msn'] = random.choice(inkColors)

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'w') as f:
        yaml.dump(data, f)

def updateStageNumbers(): # Updates the MapInfo yaml with the correct stage numbers so collecting Zapfish will work correctly
    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'r') as f:
        mapInfoYamlLines = f.readlines()

    updatedStageNo = []
    i = 0

    while i < len(mapInfoYamlLines):
        line = mapInfoYamlLines[i]
        updatedStageNo.append(line)

        for stages in stageNames:
            if line.strip().endswith(stages): # Check if the line ends with a stage name
                stageIndex = stageNames.index(stages)

                if i + 1 < len(mapInfoYamlLines):
                    nextLine = mapInfoYamlLines[i + 1]
                    indent = ' ' * (len(nextLine) - len(nextLine.lstrip()))
                    updatedStageNo.append(f"{indent}MsnStageNo: {stageIndex + 1}\n") # Update the stage number based on the order of the randomized stages
                    i += 1 
                break

        i += 1

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'w') as f:
        f.writelines(updatedStageNo)
        
def updateBossStageNumbers(): # Updates the MapInfo yaml with the correct boss stage numbers, this is seperate due to the different numbering pattern for bosses
                              # TODO: somehow merge this with updateStageNumber?
    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'r') as f:
        mapInfoYamlLines = f.readlines()

    updatedBossStageNo = []
    i = 0

    while i < len(mapInfoYamlLines):
        line2 = mapInfoYamlLines[i]
        updatedBossStageNo.append(line2)

        for stages in bossStageNames:
            if line2.strip().endswith(stages): # Check if the line ends with a stage name
                bossStageIndex = bossStageNames.index(stages)

                if i + 1 < len(mapInfoYamlLines):
                    nextLine = mapInfoYamlLines[i + 1]
                    indent = ' ' * (len(nextLine) - len(nextLine.lstrip()))
                    updatedBossStageNo.append(f"{indent}MsnStageNo: {bossStageIndex + 100 + 1}\n") # Update the stage number based on the order of the randomized stages
                    i += 1 
                break

        i += 1

    with open('Static.pack_extracted/Mush/MapInfo.yaml', 'w') as f:
        f.writelines(updatedBossStageNo)
        

def rebuildStaticPack():
    print('inRBSP')
    for dirpath, dirnames, filenames in os.walk('Static.pack_extracted'):
        for filename in filenames:
            if filename.endswith('.yaml'):
                filePath = os.path.join(dirpath, filename)
                try:
                    #os.remove(filePath)
                    print(f"Deleted: {filePath}")
                except OSError as e:
                    print(f"Error deleting {filePath}: {e}")
    
    packSARC(f"{World00ArchivePath}_extracted", World00ArchivePath, compress=True)
    #os.remove(f"{World00ArchivePath}_extracted") # Cleanup
    packSARC('Static.pack_extracted', 'randomized_Static.pack', compress=False)
print(stageNames)

random.shuffle(stageNames)
random.shuffle(bossStageNames)
print(stageNames)

for item in bossStageNames:
    stageNames.append(item)
bossStageNames.append('Fld_BossRailKing_Bos_Msn') # Make sure the final boss stage isn't randomized
print(bossStageNames)

addRandomizedKettles(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml", stageNames)
updateStageNumbers()
updateBossStageNumbers()
randomizeMusic()
randomizeInkColors()
convertToBYAML(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml")
convertToBYAML('Static.pack_extracted/Mush/MapInfo.yaml')
rebuildStaticPack()
