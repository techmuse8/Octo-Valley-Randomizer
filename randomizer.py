import os
import random
from pathlib import Path
import shutil
import logging

from oeadwrappers import *
from ruamel.yaml import YAML
from lms.message.msbtio import read_msbt as readMSBT
from lms.message.msbtio import write_msbt as writeMSBT
from lms.message.msbt import MSBT
from lms.project.msbp import MSBP



packDirectoryPath = ''
stageNames = []
bossStageNames = []
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

    random.shuffle(stageNames)
    random.shuffle(bossStageNames)
    
    for item in bossStageNames:
        stageNames.append(item)
    stageNames.append('Fld_BossRailKing_Bos_Msn') # Make sure the final boss stage isn't randomized
    bossStageNames.append('Fld_BossRailKing_Bos_Msn')

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
        return

    for obj in data:
        if 'BGMType' in obj:
            obj['BGMType'] = random.choice(BGMTypeList)

    with open(mapInfoYAML, 'w') as f:
        yaml.dump(data, f)

def randomizeInkColors(mapInfoYAML, inkColorSetting):
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible ink colors
    inkColors =  ['DarkBlue', 'Green', 'Lilac', 'LumiGreen', 'NightLumiGreen', 'MothGreen', 'Marigold', 'NightMarigold', 'Orange', 'Soda', 'Turquoise', 'Yellow']

    with open(mapInfoYAML, 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        return

    for obj in data:
        if 'TeamColor_Msn' in obj:
            obj['TeamColor_Msn'] = random.choice(inkColors)
    if inkColorSetting == 1 or 2:
        addVSInkColors(inkColorSetting)
    with open(mapInfoYAML, 'w') as f:
        yaml.dump(data, f)

def addVSInkColors(setting):
    parameterPath = staticPackDir + os.path.join("Parameter")
    workFolder = (os.path.join(parameterPath, "work"))
    os.makedirs(workFolder, exist_ok=True)
    msnInkColors = []

    if setting == 1:
        for file in os.listdir(parameterPath):
            if 'GfxSetting_Vss' in file:
                shutil.copy(os.path.join(parameterPath, file), (os.path.join(parameterPath, "work")))
            elif 'GfxSetting_Msn' in file:
                msnInkColors.append(file)
        
        
        delete4RandomInkColors(workFolder)
        for i, file in enumerate(os.listdir(workFolder)):
            shutil.move(os.path.join(workFolder, file), os.path.join(parameterPath, msnInkColors[i]))

def delete4RandomInkColors(folderPath, count=4):
    files = [f for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f))]

    if len(files) < count:
        print(f"Only found {len(files)} file(s); deleting all of them.")
        count = len(files)

    filesToDelete = random.sample(files, count)

    for file in filesToDelete:
        fullPath = os.path.join(folderPath, file)
        os.remove(fullPath)
        print(f"Deleted: {file}")


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

def randomizeDialogue(splatoonRandoFiles):
    for file in os.listdir(f"{splatoonRandoFiles}/Message"):
        if file.startswith("CommonMsg"):
            extractSARC(f"{splatoonRandoFiles}/Message/{file}")
            dialogueRandomizer(f"{splatoonRandoFiles}/Message/" + file + '_extracted/Talk/TalkMission.msbt')
            packSARC(f"{splatoonRandoFiles}/Message/" + file + '_extracted', f"{splatoonRandoFiles}/Message/" + file, compress=True)

def dialogueRandomizer(msbtPath):
    with open (msbtPath, "rb+") as file:
        data = file.read()
        msbt = readMSBT(data)

    entryNames = []

    entry = msbt.entries[4]
    for item in msbt.entries:
        entryNames.append(item.name)
    message = entry.message

    random.shuffle(entryNames)

    for item2, itemShuffled in zip(msbt.entries, entryNames):
        item2.name = itemShuffled

    with open (msbtPath, "wb") as file:
        file = writeMSBT(msbt)

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
        
def randomizeHeroWeapon(platform):
    randomWeapon = random.randint(0, 2)
    if randomWeapon == 0:
        return
    elif randomWeapon == 1: # Hero Roller
        if platform == 0: # Patches for Wii U
            shutil.copy('patches/wiiu/HeroRollerInOctoValley.hax', 'patches/consoleWeaponPatches.hax')

        elif platform == 1: # Patches for Cemu
            shutil.copy('patches/cemu/heroRoller.txt', 'patches/cemu_OV_weapon.txt')

    elif randomWeapon == 2: # Hero Charger
        if platform == 0:
            shutil.copy('patches/wiiu/HeroChargerInOctoValley.hax', 'patches/consoleWeaponPatches.hax')
        
        elif platform == 1:
            shutil.copy('patches/cemu/heroCharger.txt', 'patches/cemu_OV_weapon.txt')

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
    
    packLayoutArchives('MsnStageIcon_00')

def extractLayoutArchives(layoutFilename):
    """A function to make unpacking layout archives less tedious."""
    layoutContainer = (os.path.join(layoutFolder, layoutFilename + '.szs'))
    layoutArchive = layoutContainer + f'_extracted/{layoutFilename}.arc'

    extractSARC(layoutContainer)
    extractSARC(layoutArchive)

def packLayoutArchives(layoutFilename):
    """A function to make packing layout archives less tedious."""
    layoutContainer = (os.path.join(layoutFolder, layoutFilename + '.szs'))
    layoutArchive = layoutContainer + f'_extracted/{layoutFilename}.arc'

    packSARC(layoutArchive + '_extracted', layoutArchive, compress=False)
    shutil.rmtree(layoutArchive + '_extracted')
    packSARC(layoutContainer + '_extracted', layoutContainer, compress=True)
    shutil.rmtree(layoutContainer + '_extracted')


def rebuildStaticPack(extractedStaticPackDir):
    for dirpath, dirnames, filenames in os.walk(extractedStaticPackDir):
        for filename in filenames:
            if filename.endswith('.yaml'):
                filePath = os.path.join(dirpath, filename)
                try:
                    os.remove(filePath)
                    print(f"Deleted: {filePath}")
                except OSError as e:
                    print(f"Error deleting {filePath}: {e}")
    if isKettles:
        packSARC(f"{World00ArchivePath}_extracted", World00ArchivePath, compress=True)
    shutil.rmtree(f"{World00ArchivePath}_extracted") # Cleanup
    packSARC(extractedStaticPackDir, packDirectoryPath + 'Static.pack', compress=False)

def addEditedWeaponUpgradeUI():
    """Adds in the edited weapon upgrade UI with a footnote nothing that only the Hero Shot can be upgraded."""
    extractLayoutArchives('Wdm_Reinforce_00')
    extWeaponUpgradeLayoutDir = layoutFolder + 'Wdm_Reinforce_00.szs_extracted/Wdm_Reinforce_00.arc_extracted/'

    shutil.copy('assets/Weapon Upgrade UI/Wdm_Reinforce_00.bflyt', extWeaponUpgradeLayoutDir + 'blyt/Wdm_Reinforce_00.bflyt')
    packLayoutArchives('Wdm_Reinforce_00')

def addLayoutEdits(options):
    """Adds in the randomizer logo and the custom tutorial image and text."""
    extractLayoutArchives('Tut_TutorialPicture_00')
    extractLayoutArchives('Plz_Title_00')

    extTutorialLayoutArchiveDir = layoutFolder + 'Tut_TutorialPicture_00.szs_extracted/Tut_TutorialPicture_00.arc_extracted/'
    extTitleLayoutArchiveDir = layoutFolder + 'Plz_Title_00.szs_extracted/Plz_Title_00.arc_extracted/'

    shutil.copy('assets/Rando Title Screen UI and Logo/GambitLogo_00^l.bflim', extTitleLayoutArchiveDir + 'timg/GambitLogo_00^l.bflim')
    shutil.copy('assets/Rando Title Screen UI and Logo/Plz_Title_00.bflyt', extTitleLayoutArchiveDir + 'blyt/Plz_Title_00.bflyt')
    shutil.copy('assets/Tutorial Images and Text/TutorialPic_00^o.bflim', extTutorialLayoutArchiveDir + 'timg/TutorialPic_00^o.bflim')
    shutil.copy('assets/Tutorial Images and Text/TutorialPic_01^o.bflim', extTutorialLayoutArchiveDir + 'timg/TutorialPic_01^o.bflim')

    packLayoutArchives('Tut_TutorialPicture_00')
    packLayoutArchives('Plz_Title_00')

    if options["heroWeapons"]:
        addEditedWeaponUpgradeUI()

    packSARC(packDirectoryPath + 'Layout.pack_extracted', packDirectoryPath + 'Layout.pack', compress=False)

def addCustomText(splatoonRandoFiles):
    for item in os.listdir(f"{splatoonRandoFiles}/Message"):
        if item.startswith("CommonMsg") and item.endswith(".szs"):
            extractSARC(f"{splatoonRandoFiles}/Message/{item}")
            shutil.copy("assets/Tutorial Images and Text/Narration_Tutorial.msbt", f"{splatoonRandoFiles}/Message/" + item + '_extracted/Narration/Narration_Tutorial.msbt')
            packSARC(f"{splatoonRandoFiles}/Message/" + item + '_extracted', f"{splatoonRandoFiles}/Message/" + item, compress=True)

def performFinishingTouches(options, splatoonFilesystemRoot):
    if os.path.isdir(packDirectoryPath + 'Layout.pack_extracted'):
        addLayoutEdits(options)
    else:
        extractSARC(packDirectoryPath + 'Layout.pack')
        addLayoutEdits(options)
        addCustomText(splatoonFilesystemRoot)
    
def setupRandomization(splatoonFilesystemRoot, randomizerSeed, options):
    random.seed(randomizerSeed)
    global World00ArchivePath, packDirectoryPath, mapInfoYAML, updatedStageNo, stageNames, staticPackDir, isKettles, layoutFolder
    updatedStageNo = []
    packDirectoryPath = splatoonFilesystemRoot + '/Pack/'
    staticPackDir = packDirectoryPath + 'Static.pack_extracted/'
    layoutFolder = packDirectoryPath + 'Layout.pack_extracted/Layout/'
    isKettles = False

    if options["kettles"] or options["inkColors"] or options["music"] or options["heroWeapons"]:
        extractSARC(splatoonFilesystemRoot + '/Pack/' + 'Static.pack')
        convertFromBYAML(packDirectoryPath + 'Static.pack_extracted/Mush/MapInfo.byaml')
        mapInfoYAML = packDirectoryPath + 'Static.pack_extracted/Mush/MapInfo.yaml'
        
    if options["kettles"]:
        print("Randomizing Kettles")
        isKettles = True
        World00ArchivePath = splatoonFilesystemRoot + '/Pack/' + 'Static.pack_extracted/Map/Fld_World00_Wld.szs'
        extractSARC(World00ArchivePath)
        convertFromBYAML(World00ArchivePath + '_extracted/Fld_World00_Wld.byaml')
        randomizeKettles()
        convertToBYAML(f"{World00ArchivePath}_extracted/Fld_World00_Wld.yaml")

    if options["music"]:
        print("Randomizing Music")
        randomizeMusic(mapInfoYAML)

    if options["inkColors"]:   
        print("Randomizing ink colors")
        randomizeInkColors(mapInfoYAML, options["inkColorSet"])

    if options["missionDialogue"]:     
        print("Randomizing Dialogue")
        randomizeDialogue(splatoonFilesystemRoot)
    
    if options["heroWeapons"]:
        print("Randomizing Hero Weapon")
        randomizeHeroWeapon(options["platform"])
    
    if options["kettles"] or options["inkColors"] or options["music"] or options["heroWeapons"]:
        convertToBYAML(mapInfoYAML)
        rebuildStaticPack(packDirectoryPath + 'Static.pack_extracted')
    
    performFinishingTouches(options, splatoonFilesystemRoot)


