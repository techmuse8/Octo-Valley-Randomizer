import os
import random
from pathlib import Path
import shutil
import logging
import time
import io
from dataclasses import dataclass

from oeadwrappers import *
from ruamel.yaml import YAML
from concurrent.futures import ProcessPoolExecutor, as_completed
from lms.message.msbtio import read_msbt as readMSBT
from lms.message.msbtio import write_msbt as writeMSBT
from lms.message.msbtio import write_msbt_path as writeMSBTPath
from lms.message.msbt import MSBT
from lms.project.msbp import MSBP



#str(ctx.packDirPat) = ''
stageNames = []
bossStageNames = []
startLine = 5

@dataclass
class RandomizerContext:
    root: Path
    packDirPath: Path
    staticPackDir: Path
    layoutDir: Path
    mapInfoYAML: Path | None
    world00ArchivePath: Path | None = None
    isKettles: bool = False


def randomizeKettles(ctx: RandomizerContext):
    startLine = 5
    with open(f"{str(ctx.world00ArchivePath)}_extracted/Fld_World00_Wld.yaml") as f:
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

    addRandomizedKettles(f"{str(ctx.world00ArchivePath)}_extracted/Fld_World00_Wld.yaml", stageNames)
    updateStageNumbers(ctx.mapInfoYAML, stageNames)
    updateBossStageNumbers(ctx.mapInfoYAML, bossStageNames)
    updateStageIcons(ctx, ogFullStageNames, stageNames)

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

def randomizeInkColors(ctx: RandomizerContext, inkColorSetting):
    yaml = YAML()
    yaml.preserve_quotes = True

    # List of possible ink colors
    inkColors =  ['DarkBlue', 'Green', 'Lilac', 'LumiGreen', 'NightLumiGreen', 'MothGreen', 'Marigold', 'NightMarigold', 'Orange', 'Soda', 'Turquoise', 'Yellow']

    with open(ctx.mapInfoYAML, 'r') as f:
        data = yaml.load(f)

    if not isinstance(data, list):
        return

    for obj in data:
        if 'TeamColor_Msn' in obj:
            obj['TeamColor_Msn'] = random.choice(inkColors)
    if inkColorSetting == 1 or 2:
        addVSInkColors(ctx, inkColorSetting)
    with open(ctx.mapInfoYAML, 'w') as f:
        yaml.dump(data, f)

def addVSInkColors(ctx: RandomizerContext, setting):
    parameterPath = ctx.staticPackDir / "Parameter"
    workFolder = parameterPath / "work"
    os.makedirs(workFolder, exist_ok=True)
    vsInkColors = []
    msnInkColors = []

    if setting == 1 or 2:
        for file in os.listdir(parameterPath):
            if 'GfxSetting_Vss' in file:
                shutil.copy(os.path.join(parameterPath, file), (os.path.join(parameterPath, "work")))
                vsInkColors.append(file)
            elif 'GfxSetting_Msn' in file:
                msnInkColors.append(file)
        
        
        delete4RandomInkColors(workFolder)
        for i, file in enumerate(os.listdir(workFolder)):
            if setting == 1:
                shutil.move(os.path.join(workFolder, file), os.path.join(parameterPath, msnInkColors[i]))
            elif setting == 2:
                chosenColorSet = random.choice([vsInkColors, msnInkColors])
                if 'GfxSetting_Vss' in chosenColorSet[i]:
                    logging.debug('Picked a VS color')
                    shutil.move(os.path.join(workFolder, file), os.path.join(parameterPath, msnInkColors[i]))
                elif 'GfxSetting_Msn' in chosenColorSet[i]:
                    logging.debug('Picked a Msn color')
                    continue


def delete4RandomInkColors(folderPath, count=4):
    files = [f for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f))]

    if len(files) < count:
        logging.debug(f"Only found {len(files)} file(s); deleting all of them.")
        count = len(files)

    filesToDelete = random.sample(files, count)

    for file in filesToDelete:
        fullPath = os.path.join(folderPath, file)
        os.remove(fullPath)
        logging.debug(f"Deleted: {file}")


def updateStageNumbers(mapInfoYAMLPath, stageNames): # Updates the MapInfo yaml with the correct stage numbers so collecting Zapfish will work correctly
  #  print(mapInfoYAMLPath)
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

    finalMSBT = ''
    entryNames = []

    entry = msbt.entries[4]
    for item in msbt.entries:
        entryNames.append(item.name)
    message = entry.message

    random.shuffle(entryNames)

    for item2, itemShuffled in zip(msbt.entries, entryNames):
        item2.name = itemShuffled

    
    finalMSBT = writeMSBT(msbt)
    writeMSBTPath(msbtPath, msbt)

def extractMapFiles(mapFiles, mapFolderPath):
    for filename in mapFiles:
        mapFilePath = os.path.join(mapFolderPath, filename)
        logging.debug(mapFilePath)
        extractSARC(mapFilePath)
            
def processMapFile(filename):
        mapName = os.path.splitext(filename)[0]
        stageBYAMLConv = convertBYAMLToYAMLText(f'assets/patched_byamls/{mapName}.byaml')
        stageYAML = enemyRandomizer(stageBYAMLConv, mapName)
        convertYAMLTextToBYAML(stageYAML, mapName)

def enemyRandomizer(yamlText, mapName):
    """Randomizes all the enemies in a stage, with logic applied so the player won't get stuck."""
    yaml = YAML(typ='safe')
    yaml.preserve_quotes = True

    allEnemies = [
    "Enm_Ball",
    "Enm_Charge",
    "Enm_Cleaner",
    "Enm_Hohei",
    #"Enm_Rival00",
    "Enm_Stamp",
    "Enm_Takodozer",
    "Enm_Takolien",
    "Enm_TakolienEasy",
    "Enm_TakolienFixed",
    "Enm_TakolienFixedEasy",
    "Enm_Takopter",
    "Enm_TakopterBomb",
    #"Enm_TakopterTornado"
]

    restrictedEnemies = {"Enm_Cleaner", "Enm_TakolienS", "Enm_Takodozer"} # Squee-G, Diving Octarian, Flooder

    nonRestrictedEnemies = [
    e for e in allEnemies
    if e not in restrictedEnemies
]
    #with open(stageYAML, 'r', encoding='utf-8') as file:
    stageYAML = yaml.load(yamlText)

    totalRandomized = 0
    logicReplaced = []

    # Randomize all the enemies first
    for obj in stageYAML["Objs"]:
        objId = obj.get("Id", "Unknown")
        unitConfigName = obj.get("UnitConfigName", "").strip()

        if not unitConfigName.startswith("Enm_"):
            continue
        if unitConfigName == "Enm_TakopterTornado":
            continue
        if obj.get('Id') in {'obj567', 'obj253'} and 'Trance00' in mapName:
            continue

        if unitConfigName == "Enm_Rival00": # Moves the Octoling locations in areas where you can reach them for the following stages
            if "Propeller01" in mapName: # Propeller Lift Fortress
                obj['Translate']['X'] = 650.0
                obj['Translate']['Y'] = 350.0
                obj['Translate']['Z'] = 660.0

            elif "Sponge01" in mapName: # Floating Sponge Observatory
                obj['Translate']['X'] = 600.0
                obj['Translate']['Y'] = 459.0
                obj['Translate']['Z'] = -480.0

            elif "PaintingLift01" in mapName: # Spinning Spreaders
                obj['Translate']['X'] = -100.0
                obj['Translate']['Y'] = 210.0
                obj['Translate']['Z'] = 0.0

        if 'Dozer01' in mapName: # Far-Flung Flooders case
                if obj.get('Id') == 'obj116':
                    logging.debug('FFF case')
                    obj["UnitConfigName"] = 'Enm_Cleaner' # Makes it so the enemy with the key properly spawns
                    continue
                if obj.get('Id') == 'obj361':
                    obj["UnitConfigName"] = random.choice([e for e in nonRestrictedEnemies if e != "Enm_Ball"])
                    continue                

        newEnemy = random.choice(allEnemies)
        finalEnemy = newEnemy
        totalRandomized += 1

    # Then, apply logic to reroll restricted enemies with Switch links
    # so the player won't get stuck in places where they have to defeat everything to progress

        if newEnemy in restrictedEnemies:
            links = obj.get("Links", {})
            switchLinks = next((v for k, v in links.items() if k.strip().lower() == "switch"), [])
            if switchLinks:
                finalEnemy = random.choice([e for e in allEnemies if e not in restrictedEnemies])
                obj['Translate']['Y'] += 16.0 # Let's try to account for cases where enemies might get stuck in terrain and be unkillable (i.e Octoballers)
                logicReplaced.append((objId, unitConfigName, newEnemy))

    obj["UnitConfigName"] = finalEnemy
   # with open(stageYAML, 'w', encoding='utf-8') as file:
    buf = io.StringIO()
    yaml.dump(stageYAML, buf)
    yamlText = buf.getvalue()

    logging.debug(f"Total enemies randomized: {totalRandomized}", flush=True)
    if logicReplaced:
        logging.debug(f"Special logic replacements ({len(logicReplaced)}):", flush=True)
        for objId, oldEnemy, newEnemy in logicReplaced:
            logging.debug(f"  - {objId}: {oldEnemy} -> {newEnemy}", flush=True)
    return yamlText

def randomizeEnemies(mapFolderPath):
    files = [f for f in os.listdir(mapFolderPath) if f.endswith("_Msn.szs") and not f.startswith("Fld_Boss")]
    index = 0
    extractMapFiles(files, mapFolderPath)
    start = time.perf_counter()
    
    with ProcessPoolExecutor(max_workers = min(6, max(2, os.cpu_count() // 2))) as executor:
       # files = os.listdir(mapFolderPath)
        futures = [executor.submit(processMapFile, filename)
                   for filename in files]

        for fut in as_completed(futures):
            try:
                fut.result() 
            except Exception as e:
                print(f"Worker failed: {e}", flush=True)

    end = time.perf_counter()
    logging.info(f"Randomizing enemies took {end - start:.3f} seconds")

    for filename in files:
        mapName = os.path.splitext(filename)[0]
        extractedFolder = os.path.join(mapFolderPath, f'{mapName}.szs_extracted')
        mapFilePath = os.path.join(mapFolderPath, filename)

        packSARC(extractedFolder, mapFilePath, compress=True)
        shutil.rmtree(extractedFolder)

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
        
def updateStageIcons(ctx: RandomizerContext, originalStageOrder, shuffledStageOrder):
    """
    Updates the stage icons to match the current randomized stages.
    """
    stageIconLayoutContainer = ctx.packDirPath / 'Layout.pack_extracted' / 'Layout' / 'MsnStageIcon_00.szs'
    stageIconLayoutArchive = stageIconLayoutContainer.with_name(stageIconLayoutContainer.stem + '.szs_extracted') / 'MsnStageIcon_00.arc' # The archive layering here is annoying but we deal with it

    extractSARC(ctx.packDirPath / 'Layout.pack')
    extractSARC(stageIconLayoutContainer)
    extractSARC(stageIconLayoutArchive)

    stageIconLayoutArchiveExtracted = stageIconLayoutArchive.with_name(stageIconLayoutArchive.name + '_extracted')
    stageIconDir = stageIconLayoutArchiveExtracted / 'timg'

    original_index_map = {name: str(index).zfill(2) for index, name in enumerate(originalStageOrder)}
    # Maps the original stage numbers to the new one
    oldToNewStageMapping = {name: shuffledStageOrder.index(name) for name in originalStageOrder}
    remappedDir = stageIconDir / 'remapped_images'
    remappedDir.mkdir(exist_ok=True)


    logging.debug("Generated mapping:")
    for old_stage, new_index in oldToNewStageMapping.items():
        logging.debug(f"Old: {old_stage} -> New: {str(new_index).zfill(2)}")
    
    for filename in os.listdir(stageIconDir):
        if filename.endswith('^q.bflim') and filename.startswith('MsnStageIcon_'):
            ogStageNumber = filename.split('_')[1][:2]
            ogStageName = originalStageOrder[int(ogStageNumber)]
        
            newStageNumber = oldToNewStageMapping.get(ogStageName, None)
            if newStageNumber is not None:
                newFilename = filename.replace(f'_{ogStageNumber}^q', f'_{str(newStageNumber).zfill(2)}^q')
            
                oldFilePath = stageIconDir / filename
                newFilePath = remappedDir / newFilename
                oldFilePath.rename(newFilePath)

                logging.debug(f'Renamed: {filename} -> {newFilename}')
            else:
                logging.warning(f"WARNING: No new stage number found for {ogStageName}")
    
    for filePath in remappedDir.iterdir():
        shutil.move(str(filePath), str(stageIconDir))

    
    packLayoutArchives(ctx, 'MsnStageIcon_00')

def extractLayoutArchives(ctx: RandomizerContext, layoutFilename):
    """A function to make unpacking layout archives less tedious."""
    layoutContainer = (os.path.join(str(ctx.layoutDir), layoutFilename + '.szs'))
    layoutArchive = layoutContainer + f'_extracted/{layoutFilename}.arc'

    extractSARC(layoutContainer)
    extractSARC(layoutArchive)

def packLayoutArchives(ctx: RandomizerContext, layoutFilename):
    """A function to make packing layout archives less tedious."""
    layoutContainer = ctx.layoutDir / f"{layoutFilename}.szs"
    layoutContainerExtracted = layoutContainer.with_name(layoutContainer.stem + '.szs_extracted')

    layoutArchive = layoutContainer.with_name(layoutContainer.stem + '.szs_extracted') / f"{layoutFilename}.arc"
    layoutArchiveExtracted = layoutArchive.with_name(layoutArchive.stem + '.arc_extracted')

    packSARC(layoutArchiveExtracted, layoutArchive, compress=False)
    shutil.rmtree(layoutArchiveExtracted)

    packSARC(layoutContainerExtracted, layoutContainer, compress=True)
    shutil.rmtree(layoutContainerExtracted)


def rebuildStaticPack(ctx: RandomizerContext):
    staticPackPath = ctx.packDirPath / 'Static.pack'
    
    for dirpath, dirnames, filenames in os.walk(ctx.staticPackDir):
        for filename in filenames:
            if filename.endswith('.yaml'):
                filePath = os.path.join(dirpath, filename)
                try:
                    os.remove(filePath)
                    logging.debug(f"Deleted: {filePath}")
                except OSError as e:
                    logging.error(f"Error deleting {filePath}: {e}")
    if ctx.isKettles:
        packSARC(f"{str(ctx.world00ArchivePath)}_extracted", str(ctx.world00ArchivePath), compress=True)
        shutil.rmtree(f"{str(ctx.world00ArchivePath)}_extracted") # Cleanup
    time.sleep(1.5)
    packSARC(ctx.staticPackDir, staticPackPath, compress=False)

def addEditedWeaponUpgradeUI(ctx: RandomizerContext):
    """Adds in the edited weapon upgrade UI with a footnote nothing that only the Hero Shot can be upgraded."""
    extractLayoutArchives(ctx, 'Wdm_Reinforce_00')
    extWeaponUpgradeLayoutDir = ctx.layoutDir / 'Wdm_Reinforce_00.szs_extracted' / 'Wdm_Reinforce_00.arc_extracted'

    shutil.copy('assets/Weapon Upgrade UI/Wdm_Reinforce_00.bflyt', extWeaponUpgradeLayoutDir / 'blyt' / 'Wdm_Reinforce_00.bflyt')
    packLayoutArchives(ctx, 'Wdm_Reinforce_00')

def addLayoutEdits(ctx: RandomizerContext, options):
    """Adds in the randomizer logo, the custom tutorial image and text."""
    extractLayoutArchives(ctx, 'Tut_TutorialPicture_00')
    extractLayoutArchives(ctx, 'Plz_Title_00')

    extTutorialLayoutArchiveDir = ctx.layoutDir / 'Tut_TutorialPicture_00.szs_extracted' / 'Tut_TutorialPicture_00.arc_extracted'
    extTitleLayoutArchiveDir = ctx.layoutDir / 'Plz_Title_00.szs_extracted' / 'Plz_Title_00.arc_extracted'

    shutil.copy('assets/Rando Title Screen UI and Logo/GambitLogo_00^l.bflim', extTitleLayoutArchiveDir / 'timg' / 'GambitLogo_00^l.bflim')
    shutil.copy('assets/Rando Title Screen UI and Logo/Plz_Title_00.bflyt', extTitleLayoutArchiveDir / 'blyt' / 'Plz_Title_00.bflyt')
    shutil.copy('assets/Tutorial Images and Text/TutorialPic_00^o.bflim', extTutorialLayoutArchiveDir / 'timg' / 'TutorialPic_00^o.bflim')
    shutil.copy('assets/Tutorial Images and Text/TutorialPic_01^o.bflim', extTutorialLayoutArchiveDir / 'timg' / 'TutorialPic_01^o.bflim')

    packLayoutArchives(ctx, 'Tut_TutorialPicture_00')
    packLayoutArchives(ctx, 'Plz_Title_00')

    if options["heroWeapons"]:
        addEditedWeaponUpgradeUI(ctx)

    packSARC(ctx.packDirPath / 'Layout.pack_extracted', ctx.packDirPath / 'Layout.pack', compress=False)

def addCustomText(splatoonRandoFiles):
    for item in os.listdir(f"{splatoonRandoFiles}/Message"):
        if item.startswith("CommonMsg") and item.endswith(".szs"):
            extractSARC(f"{splatoonRandoFiles}/Message/{item}")
            shutil.copy("assets/Tutorial Images and Text/Narration_Tutorial.msbt", f"{splatoonRandoFiles}/Message/" + item + '_extracted/Narration/Narration_Tutorial.msbt')
            packSARC(f"{splatoonRandoFiles}/Message/" + item + '_extracted', f"{splatoonRandoFiles}/Message/" + item, compress=True)

def performFinishingTouches(ctx: RandomizerContext, options, splatoonFilesystemRoot):
    if os.path.isdir(ctx.packDirPath / 'Layout.pack_extracted'):
        addLayoutEdits(ctx, options)
        addCustomText(splatoonFilesystemRoot)
    else:
        extractSARC(ctx.packDirPath / 'Layout.pack')
        addLayoutEdits(ctx, options)
        addCustomText(splatoonFilesystemRoot)
    
def setupRandomization(splatoonFilesystemRoot, randomizerSeed, options):
    random.seed(randomizerSeed)

    ctx = RandomizerContext(
    root=Path(splatoonFilesystemRoot),
    packDirPath=Path(splatoonFilesystemRoot) / "Pack",
    staticPackDir=Path(splatoonFilesystemRoot) / "Pack/Static.pack_extracted",
    layoutDir=Path(splatoonFilesystemRoot) / "Pack/Layout.pack_extracted/Layout",
    mapInfoYAML=None
)

    mapFolderPath = ctx.root / 'Pack' / 'Static.pack_extracted' / 'Map'

    if options["kettles"] or options["inkColors"] or options["music"] or options["heroWeapons"] or options["enemies"]:
        extractSARC(str(ctx.packDirPath / 'Static.pack'))
        convertFromBYAML(str(ctx.staticPackDir / 'Mush/MapInfo.byaml'))
        ctx.mapInfoYAML = ctx.staticPackDir / 'Mush/MapInfo.yaml'
        
    if options["kettles"]:
        print("Randomizing Kettles")
        ctx.isKettles = True
        ctx.world00ArchivePath = Path(splatoonFilesystemRoot) / 'Pack' / 'Static.pack_extracted/Map/Fld_World00_Wld.szs'
        
        extractSARC(ctx.world00ArchivePath)
        convertFromBYAML(Path(f"{ctx.world00ArchivePath}_extracted") / "Fld_World00_Wld.byaml")
        randomizeKettles(ctx)
        convertToBYAML(f"{str(ctx.world00ArchivePath)}_extracted/Fld_World00_Wld.yaml")

    if options["music"]:
        print("Randomizing Music")
        randomizeMusic(ctx.mapInfoYAML)

    if options["inkColors"]:   
        print("Randomizing ink colors")
        randomizeInkColors(ctx, options["inkColorSet"])

    if options["missionDialogue"]:     
        print("Randomizing Dialogue")
        randomizeDialogue(str(ctx.root))
    
    if options["enemies"]:
        randomizeEnemies(mapFolderPath)

    if options["kettles"] or options["inkColors"] or options["music"] or options["heroWeapons"] or options["enemies"]:
        convertToBYAML(ctx.mapInfoYAML)
        rebuildStaticPack(ctx)

    

    performFinishingTouches(ctx, options, str(ctx.root))
    return True
