import os
import random
from pathlib import Path
import shutil

from oeadwrappers import *
from ruamel.yaml import YAML
from LMS.Message.MSBTStream import read_msbt as readMSBT
from LMS.Message.MSBTStream import write_msbt as writeMSBT
from LMS.Message.MSBT import MSBT
from LMS.Project.MSBP import MSBP

#splatoonDumpPath = input("Enter the path to your Splatoon 1 Dump: ")
splatoonRandoFiles = 'Splatoon_Rando_Files'

packDirectoryPath = ''
stageNames = []
bossStageNames = []
#shutil.copytree(f"{splatoonDumpPath}/Pack", f"{splatoonRandoFiles}/Pack")
#shutil.copytree(f"{splatoonDumpPath}/Message", f"{splatoonRandoFiles}/Message")
#shutil.copy(f"{splatoonDumpPath}/Pack/Static.pack", './Static.pack')

#exit()


#extractSARC('Static.pack')
#World00ArchivePath = 'Static.pack_extracted/Map/Fld_World00_Wld.szs'


#convertFromBYAML('Static.pack_extracted/Mush/MapInfo.byaml')

startLine = 5

def randomizeKettles():
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
    ogFullStageNames = stageNames
    stageNames = stageNames[:-5]

    #print(bossStageNames)
    #print(stageNames)

    random.shuffle(stageNames)
    random.shuffle(bossStageNames)
    
    for item in bossStageNames:
        stageNames.append(item)
    stageNames.append('Fld_BossRailKing_Bos_Msn') # Make sure the final boss stage isn't randomized

    addRandomizedKettles(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml", stageNames)
    print(bossStageNames)
    print(stageNames)
    updateStageNumbers(mapInfoYAML, stageNames)
    updateBossStageNumbers(mapInfoYAML, bossStageNames)
    updateStageIcons(ogFullStageNames, stageNames)

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

def randomizeMusic(mapInfoYAML):
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible music tracks
    BGMTypeList =  ['TakoJoban', 'TakoBase', 'Race', 'Missile', 'Rival']

    with open(mapInfoYAML, 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        print("Error: The YAML structure is not a list.")
        return

    for obj in data:
        if 'BGMType' in obj:
            obj['BGMType'] = random.choice(BGMTypeList)

    with open(mapInfoYAML, 'w') as f:
        yaml.dump(data, f)

def randomizeInkColors(mapInfoYAML):
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible ink colors
    inkColors =  ['DarkBlue', 'Green', 'Lilac', 'LumiGreen', 'NightLumiGreen', 'MothGreen', 'Marigold', 'NightMarigold', 'Orange', 'Soda', 'Turquoise', 'Yellow']

    with open(mapInfoYAML, 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        print("Error: The YAML structure is not a list.")
        return

    for obj in data:
        if 'TeamColor_Msn' in obj:
            obj['TeamColor_Msn'] = random.choice(inkColors)

    with open(mapInfoYAML, 'w') as f:
        yaml.dump(data, f)

def updateStageNumbers(mapInfoYAMLPath, stageNames): # Updates the MapInfo yaml with the correct stage numbers so collecting Zapfish will work correctly
    print(mapInfoYAMLPath)
    with open(mapInfoYAMLPath, 'r') as f:
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

    with open(mapInfoYAMLPath, 'w') as f:
        f.writelines(updatedStageNo)

def randomizeDialogue():
    for file in os.listdir(f"{splatoonRandoFiles}/Message"):
        if file.startswith("CommonMsg"):
            extractSARC(f"{splatoonRandoFiles}/Message/{file}")
            #print(f"{splatoonRandoFiles}/Message/" + file + '_extracted/Talk/TalkMission.msbt')
            dialogueRandomizer(f"{splatoonRandoFiles}/Message/" + file + '_extracted/Talk/TalkMission.msbt')
            packSARC(f"{splatoonRandoFiles}/Message/" + file + '_extracted', f"{splatoonRandoFiles}/Message/" + file, compress=True)

def dialogueRandomizer(msbtPath):
    with open (msbtPath, "rb+") as file:
        msbt = readMSBT(file)
    entryNames = []

    entry = msbt.entries[4]
    for item in msbt.entries:
        entryNames.append(item.name)
    message = entry.message

    random.shuffle(entryNames)

    for item2, itemShuffled in zip(msbt.entries, entryNames):
        item2.name = itemShuffled

    with open (msbtPath, "wb") as file:
        writeMSBT(file, msbt)

def updateBossStageNumbers(mapInfoYAML, bossStageNames): # Updates the MapInfo yaml with the correct boss stage numbers, this is seperate due to the different numbering pattern for bosses
                              # TODO: somehow merge this with updateStageNumber?
    with open(mapInfoYAML, 'r') as f:
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

    with open(mapInfoYAML, 'w') as f:
        f.writelines(updatedBossStageNo)
        

def updateStageIcons(originalStageOrder, shuffledStageOrder):
    """
    Updates the stage icons to match the current randomized stages.
    """
    stageIconLayoutContainer = packDirectoryPath + 'Layout.pack_extracted/Layout/MsnStageIcon_00.szs'
    stageIconLayoutArchive = packDirectoryPath + 'Layout.pack_extracted/Layout/MsnStageIcon_00.szs_extracted/MsnStageIcon_00.arc' # The archive layering here is annoying but we deal with it

    extractSARC(packDirectoryPath + 'Layout.pack')
    extractSARC(stageIconLayoutContainer)
    extractSARC(stageIconLayoutArchive)
    stageIconDir = packDirectoryPath + 'Layout.pack_extracted/Layout/MsnStageIcon_00.szs_extracted/MsnStageIcon_00.arc_extracted/timg'
    original_index_map = {name: str(index).zfill(2) for index, name in enumerate(originalStageOrder)}
    # Maps the original stage numbers to the new one
    oldToNewStageMapping = {name: shuffledStageOrder.index(name) for name in originalStageOrder}
    os.makedirs(stageIconDir + '/remapped_images')

    print("Generated mapping:")
    for old_stage, new_index in oldToNewStageMapping.items():
        print(f"Old: {old_stage} -> New: {str(new_index).zfill(2)}")
    
    for filename in os.listdir(stageIconDir):
        if filename.endswith('^q.bflim') and filename.startswith('MsnStageIcon_'):
            ogStageNumber = filename.split('_')[1][:2]
            ogStageName = originalStageOrder[int(ogStageNumber)]
        
            newStageNumber = oldToNewStageMapping.get(ogStageName, None)
            if newStageNumber is not None:
                newFilename = filename.replace(f'_{ogStageNumber}^q', f'_{str(newStageNumber).zfill(2)}^q')
            
                oldFilePath = os.path.join(stageIconDir, filename)
                newFilePath = os.path.join(stageIconDir + '/remapped_images', newFilename)
                os.rename(oldFilePath, newFilePath)
                print(f'Renamed: {filename} -> {newFilename}')
            else:
                print(f"WARNING: No new stage number found for {ogStageName}")
    
    for filename in os.listdir(stageIconDir + '/remapped_images'):
        print(filename)
        shutil.move(stageIconDir + '/remapped_images/' + filename, stageIconDir)
    
    packSARC(packDirectoryPath + 'Layout.pack_extracted/Layout/MsnStageIcon_00.szs_extracted/MsnStageIcon_00.arc_extracted', stageIconLayoutArchive, compress=False)
    packSARC(stageIconLayoutContainer + '_extracted', stageIconLayoutContainer, compress=True)
    
def rebuildStaticPack(extractedStaticPackDir):
    print('inRBSP')
    for dirpath, dirnames, filenames in os.walk(extractedStaticPackDir):
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
    packSARC(extractedStaticPackDir, 'randomized_Static.pack', compress=False)
print(stageNames)

def setupRandomization(splatoonFilesystemRoot, randomizerSeed):
    random.seed(randomizerSeed)
    global World00ArchivePath, packDirectoryPath, mapInfoYAML, updatedStageNo, stageNames
    updatedStageNo = []
    extractSARC(splatoonFilesystemRoot + '/Pack/' + 'Static.pack')
    World00ArchivePath = splatoonFilesystemRoot + '/Pack/' + 'Static.pack_extracted/Map/Fld_World00_Wld.szs'
    packDirectoryPath = splatoonFilesystemRoot + '/Pack/'
    extractSARC(World00ArchivePath)
    convertFromBYAML(packDirectoryPath + 'Static.pack_extracted/Mush/MapInfo.byaml')
    convertFromBYAML(World00ArchivePath + '_extracted/Fld_World00_Wld.byaml')
    mapInfoYAML = packDirectoryPath + 'Static.pack_extracted/Mush/MapInfo.yaml'
    randomizeKettles()
    randomizeMusic(mapInfoYAML)
    randomizeInkColors(mapInfoYAML)
    randomizeDialogue()
    convertToBYAML(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml")
    convertToBYAML(mapInfoYAML)
    rebuildStaticPack(packDirectoryPath + 'Static.pack_extracted')

