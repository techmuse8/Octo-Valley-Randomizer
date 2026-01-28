import sys
import random
import string
import traceback
from pathlib import Path
import shutil
import os
import hashlib
import logging
import datetime
import importlib.util
import subprocess
import configparser

import dependencycheck
from python_bpspatcher.patcher import *

globalGameDirectoryPath = '' 

def init():
    
    from PyQt5 import uic
    from PyQt5.QtGui import QIcon, QDesktopServices
    from PyQt5.QtCore import Qt, QSize, QUrl, QThread, pyqtSignal, QTimer
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QMainWindow,
        QWidget,
        QFileDialog,
        QDialog,
        QVBoxLayout,
        QLabel,
        QProgressBar,
        QMessageBox,
    )
    from packaging import version
    import requests

    import randomizer
    import hashcollection

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    class RandomizationWorker(QThread):
            progressUpdated = pyqtSignal(int)  # Emit an integer value for progress
            statusUpdated = pyqtSignal(str)     # Emit a string for status messages
            randomizationCompleted = pyqtSignal()
            randomizationFailed = pyqtSignal(str)
            def __init__(self, splatoon1DirectoryPath: str, options: dict, seed: str, parent=None):
                super().__init__(parent)
                self.splatoon1DirectoryPath = splatoon1DirectoryPath
                self.options = options
                self.seed = seed
            def run(self):
                try:
                    self.statusUpdated.emit("Randomizing: Please wait...")
                    QApplication.processEvents()

                    success = randomizer.setupRandomization(self.splatoon1DirectoryPath, self.seed, self.options)
                    if success:
                        self.randomizationCompleted.emit()
                        self.statusUpdated.emit("Randomization completed!")
                    else:
                        self.randomizationFailed.emit()
                        self.progressUpdated.emit("Randomization failed!")
                except Exception as e:
                    logging.error(f"Error in worker thread: {e}")
                    tracebackText = traceback.format_exc()
                    self.randomizationFailed.emit(tracebackText)
                    self.statusUpdated.emit("An error occurred during randomization.")
                    self.progressUpdated.emit("Randomization failed!")
                
    class ProgressDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.setWindowTitle("Randomization Progress")
            self.setModal(True)
            self.setFixedSize(300, 150)
            layout = QVBoxLayout()
            self.label = QLabel("Starting randomization...", self)
            self.label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label)
            self.progressBar = QProgressBar(self) 
            self.progressBar.setRange(0, 0)
            layout.addWidget(self.progressBar)
            self.progressBar.setAlignment(Qt.AlignCenter)
            self.setLayout(layout)

        def updateProgress(self, value):
            self.progressBar.setValue(value)
            
        def setStatus(self, message):
            self.label.setText(message)
        
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            uic.loadUi('mainUI.ui', self)

            centralWidget = self.findChild(QWidget, 'centralwidget')
            self.setCentralWidget(centralWidget)
            self.splatoon1Path.setPlaceholderText("Selected directory path will appear here.")
            self.setWindowTitle("Splatoon 1 Octo Valley Randomizer")
            self.setWindowIcon(QIcon('assets/misc/icon.png'))
            self.setGeometry(100, 100, 706, 496)
            self.setFixedSize(QSize(706, 496))
            self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
            self.browseButton.clicked.connect(self.openDirectoryDialog)
            self.generateSeedButton.clicked.connect(self.generateSeed)
            self.setCentralWidget(centralWidget)
            self.inkColorSetDropdown.setEnabled(False)
            self.itemDropSetDropdown.setEnabled(False)
            self.randomizeButton.clicked.connect(lambda: self.startRandomization(self.splatoon1Path.text() + '/content'))
            self.actionCheck_for_Updates.triggered.connect(self.checkForUpdates)
            self.actionOpen_Output_Folder.triggered.connect(self.openOutputFolder)
            self.actionDocumentation.triggered.connect(self.openDocumentationPage)
            self.gameRegion = ''
            self.randomizerVersion = '0.1.1'
            self.titleID = ''
            self.titleIDs = {
                "US": "0005000010176900",
                "EU": "0005000010176A00",
                "JP": "0005000010162B00"
                            }
            self.options = {}
            self.miscSettings = configparser.ConfigParser()
            self.miscSettings.optionxform = str
            self.inkColorCheckBox.stateChanged.connect(self.updateInkColorDropdownState)
            self.itemDropCheckBox.stateChanged.connect(self.updateItemDropDropdownState)
            
            self.checkboxes = self.findChildren(QCheckBox)
            for checkbox in self.checkboxes:
                checkbox.stateChanged.connect(self.updateRandomizeButtonState)
            
            self.updateRandomizeButtonState()

        def showErrorDialog(self, title, message):
            dlg = QMessageBox(self)
            dlg.setWindowTitle(title)
            dlg.setText(message)
            dlg.setIcon(QMessageBox.Critical)
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.exec()

        def showMessageBox(self, title, message, icon, buttons):
            dlg = QMessageBox(self)
            dlg.setWindowTitle(title)
            dlg.setText(message)
            dlg.setIcon(icon)
            dlg.setStandardButtons(buttons)
            return dlg.exec()

        def openDirectoryDialog(self):
            global globalGameDirectoryPath
            directoryPath = QFileDialog.getExistingDirectory(self, 'Select the folder containing the "code" and "content" folders of your Splatoon 1 dump.')
            if self.checkForValidGameFiles(directoryPath):
               # print(directoryPath)
               # print(self.gameRegion)
                globalGameDirectoryPath = directoryPath
                self.splatoon1Path.setText(directoryPath)
                self.updateRandomizeButtonState()
               # print(self.titleID)

        def generateSeed(self):
            characters = string.ascii_letters + string.digits
            randomString = ''.join(random.choice(characters) for i in range(10))
            self.randomizerSeedBox.setText(randomString)
            logging.info("Seed: " + randomString)

        def updateRandomizeButtonState(self):
            anyChecked = any(checkbox.isChecked() for checkbox in self.checkboxes)
            pathText = self.splatoon1Path.text().strip()
            hasValidPath = len(pathText) > 0
            self.randomizeButton.setEnabled(anyChecked and hasValidPath)

        def openOutputFolder(self):
            if not os.path.exists("output"):
                os.makedirs("output")
            QDesktopServices.openUrl(QUrl.fromLocalFile(str('output')))

        def checkForUpdates(self):
            githubResponse = requests.get("https://api.github.com/repos/techmuse8/Octo-Valley-Randomizer/releases/latest")
            currentVersion = version.parse(self.randomizerVersion)
            latestVersion = (githubResponse.json()["tag_name"])
            latestVersionStripped = version.parse(latestVersion.strip("v"))
            if latestVersionStripped > currentVersion:
                response = self.showMessageBox("Update Checker", f"Version: {latestVersionStripped} is now available! Would you like to visit the GitHub releases page to get the latest version?", 
                                            QMessageBox.Question, QMessageBox.Yes | QMessageBox.No)
                if response == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl((githubResponse.json()["html_url"])))
                
            elif latestVersionStripped == currentVersion:
                response = self.showMessageBox("Update Checker", f"You're on the latest version! ({currentVersion})", 
                                            QMessageBox.Information, QMessageBox.Yes)

        def openDocumentationPage(self):
            QDesktopServices.openUrl(QUrl("https://github.com/techmuse8/Octo-Valley-Randomizer/wiki"))
        # TODO: Make a general dropdown state updater method
        def updateInkColorDropdownState(self, state):
            if state == Qt.Checked:
                self.inkColorSetDropdown.setEnabled(True)
            else:
                self.inkColorSetDropdown.setEnabled(False)

        def updateItemDropDropdownState(self, state):
            if state == Qt.Checked:
                self.itemDropSetDropdown.setEnabled(True)
            else:
                self.itemDropSetDropdown.setEnabled(False)

        def computeMD5(self, filepath):
            """Compute the MD5 hash of a file."""
            hash_md5 = hashlib.md5()
            try:
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                    return hash_md5.hexdigest()
            except Exception as e:
                return None
        
        def checkGameFileHashes(self, codeFolder, packDir, messageDir, expected_hashes):
            """Checks if the selected Splatoon 1 dump is valid by comparing the necessary file hashes against expected ones."""
            allValid = True

            for filename, expectedHash in expected_hashes.items():
                actualFile = None

                packPath = os.path.join(packDir, filename)
                messagePath = os.path.join(messageDir, filename)

                if os.path.isfile(packPath):
                    actualFile = packPath
                elif os.path.isfile(messagePath):
                    actualFile = messagePath
                elif filename == "Gambit.rpx": # Special case for the executable
                    actualFile = os.path.join(codeFolder, filename)

                if actualFile:
                    actualHash = self.computeMD5(actualFile)
                    if actualHash != expectedHash:
                        logging.error(f"Invalid file hash for {filename}: expected {expectedHash}, got {actualHash} instead")
                        allValid = False
                    else:
                        logging.info(f"Valid {filename}")
                else:
                    logging.warning(f"Missing {filename}: Likely for another region")
            
            return allValid
                
        def checkGameRegion(self, messageDir):
            messageFiles = os.listdir(messageDir)
            for filename in messageFiles:
               # print
                if "EU" in filename:
                    return "EU"
                elif "US" in filename:
                    return "US"
                elif "JP" in filename:
                    return "JP"
                
        def getTitleID(self, region):
            """Returns a title ID based on the input region."""
            return self.titleIDs.get(region, None)

        def checkForValidGameFiles(self, gameRoot):
            """Goes through a process to ensure that a (valid) Splatoon 1 dump has been selected."""
           # print(gameRoot)
            if not os.path.isdir(os.path.join(gameRoot, 'code')) and not os.path.isdir(os.path.join(gameRoot, 'content')):
                self.showErrorDialog('Error!', 'The "code" and/or "content" folders of your Splatoon 1 dump cannot be found!')
                return False
            packFolder = os.path.join(gameRoot + '/content', 'Pack')
            messageFolder = os.path.join(gameRoot + '/content', 'Message')
            codeFolder = os.path.join(gameRoot, 'code')

            if os.path.isdir(packFolder) and os.path.isdir(messageFolder): # Check if this is a Splatoon 1 dump
                if self.checkGameFileHashes(codeFolder, packFolder, messageFolder, hashcollection.expected_hashes_2_12_1) == True: # If so, make sure that the selected dump is a valid 2.12.1 one
                    self.gameRegion = self.checkGameRegion(messageFolder)
                    self.titleID = self.getTitleID(self.gameRegion)
                    return True
                else:
                    self.showErrorDialog('Error!', 'The selected Splatoon 1 dump is invalid! Ensure that your game files are valid.')
                    return False
            else:
                self.showErrorDialog('Error!', 'Ensure that you have selected a Splatoon 1 dump!')

        def copyOutputRandomizer(self, outputRandoDir):

            os.makedirs(outputRandoDir, exist_ok=True)
            os.makedirs(f'{outputRandoDir}/Pack', exist_ok=True)
            os.makedirs(f'{outputRandoDir}/Message', exist_ok=True)

            shutil.copy('Splatoon_Rando_Files_work/Pack/Layout.pack', f'{outputRandoDir}/Pack/Layout.pack')
            shutil.copy('Splatoon_Rando_Files_work/Pack/Static.pack', f'{outputRandoDir}/Pack/Static.pack')
            for entry in os.listdir('Splatoon_Rando_Files_work/Message/'):
                fullEntryPath = os.path.join('Splatoon_Rando_Files_work/Message/', entry)
                if os.path.isfile(fullEntryPath) and 'Msg' in entry:
                    shutil.copy(f'Splatoon_Rando_Files_work/Message/{entry}', f'{outputRandoDir}/Message/')

        def updateProgress(self, message):
            """Update progress message in the textbox."""
            self.progressTextbox.setText(message)
        
        def onRandomizationError(self, tracebackText):
            """Handle any randomization errors."""
            self.progressTextbox.setStyleSheet("color: red;")

            self.progressTextbox.setText("Randomization failed!")
            self.randomizeButton.setEnabled(True)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Randomization Error")
            msg.setText("An error occurred during randomization! Check the details for more information.")
            msg.setDetailedText(tracebackText)
            msg.setSizeGripEnabled(True)
            msg.setWindowFlags(msg.windowFlags() | Qt.Window)

            result = msg.exec_()

            if result == QMessageBox.Ok:
                QTimer.singleShot(1000, self.progressDialog.close)

        def randomizationCompleted(self):
            """Handle completion of randomization."""
            self.finalizeRandomization()
            
            self.progressTextbox.setStyleSheet("color: green;")
            self.progressTextbox.setText("Randomization completed!")
            QTimer.singleShot(1000, self.progressDialog.close)
            self.randomizeButton.setEnabled(True)  # Enable the randomize button again if initially disabled

        def patchRPX(self, rpxPath, bpsPatchPath, outRPXPath):
            """Patches a Splatoon 1 RPX with custom code used in the randomizer."""
            with open(bpsPatchPath, "rb") as file:
                bpsPatch = file.read()

            patcher = BPSPatch(bpsPatch)

            os.makedirs("original_rpx", exist_ok=True)
            shutil.copy(rpxPath, "original_rpx/Gambit.rpx")

            with open(rpxPath, "rb") as file:
                rpxData = file.read()

            patchedRPX = patcher.patch_rom(rpxData)

            with open(outRPXPath, "wb") as file:
                file.write(patchedRPX)
            logging.info('RPX patched!')
        
        def finalizeRandomization(self):
            """Moves all the randomized files to a dedicated output folder."""
            if self.platformDropdown.currentIndex() == 0: # For Wii U
                
                outputRandoDir = os.path.join('output/Wii U/', f'{self.randomizerSeedBox.text()}/sdcafiine/{self.titleID}/Octo Valley Randomizer - Seed {self.randomizerSeedBox.text()}')
                
                if os.path.isdir(outputRandoDir): # Yet another cleanup check
                    shutil.rmtree(outputRandoDir)
                self.copyOutputRandomizer(outputRandoDir + '/content')

                # Add in the randomizer code patches
                shutil.copytree(f'patches/wiiu/', f'output/Wii U/{self.randomizerSeedBox.text()}/cafeloader/{self.titleID}', dirs_exist_ok=True)

            if self.platformDropdown.currentIndex() == 1: # For Cemu
                codePath = self.splatoon1Path.text() + '/code/Gambit.rpx'
                outputRandoDir = 'output/Cemu/' + f'{self.randomizerSeedBox.text()}/' + f'Octo Valley Randomizer - Seed {self.randomizerSeedBox.text()}'
                if os.path.isdir(outputRandoDir):
                    shutil.rmtree(outputRandoDir)

                self.copyOutputRandomizer(outputRandoDir + '/content')
                os.makedirs(outputRandoDir + '/code', exist_ok=True)
                self.patchRPX(codePath, "patches/cemu/cemu_rando_patches.bps", outputRandoDir + '/code/Gambit.rpx')

                with open('assets/rules.txt', 'r') as file:
                    cemuRulesTxt = file.read()
                modifiedCemuRulesTxt = cemuRulesTxt.replace("{seed}", self.randomizerSeedBox.text())
                
                with open(outputRandoDir + '/rules.txt', "x") as file:
                    file.write(modifiedCemuRulesTxt)
            
            os.mkdir(outputRandoDir + '/content/Rando')
            with open(outputRandoDir + "/content/Rando/seed.txt", 'x') as file:
                file.write(self.randomizerSeedBox.text())
                
            if self.options["heroWeapons"]:
                self.miscSettings['RandomizerSettings']['WeaponRandomizer'] = '1'

            self.miscSettings['RandomizerSettings']['SkipOctoValleyIntro'] = f"{int(self.skipOVIntroCheckBox.isChecked())}"
            self.miscSettings['RandomizerSettings']['SkipFirstNews'] = f"{int(self.skipNewsIntroCheckBox.isChecked())}"
            self.miscSettings['RandomizerSettings']['OctoValleyRestart'] = f"{int(self.addOVRestartCheckBox.isChecked())}"

            with open(outputRandoDir + '/content/Rando/config.ini', 'x') as configfile:
                self.miscSettings.write(configfile)

            
            shutil.rmtree("Splatoon_Rando_Files_work") # Cleanup

        def startRandomization(self, splatoon1DirectoryPath):
            """Intializes the randomizer."""

            self.progressDialog = ProgressDialog(self)
            currentSeed = self.randomizerSeedBox.text()
            if len(currentSeed) <= 0:
                self.generateSeed()

            self.progressDialog.show()
            self.progressTextbox.setText("Randomizing: Please wait...")
            self.progressTextbox.setStyleSheet("color: black;")
            QApplication.processEvents()
            os.makedirs("tmp", exist_ok=True)

            if os.path.isdir("Splatoon_Rando_Files_work"): # Clean up check
                shutil.rmtree("Splatoon_Rando_Files_work")

            shutil.copytree(f"{splatoon1DirectoryPath}/Pack", "Splatoon_Rando_Files_work/Pack")
            shutil.copytree(f"{splatoon1DirectoryPath}/Message", "Splatoon_Rando_Files_work/Message")
            shutil.copy(f"{splatoon1DirectoryPath}/Pack/Static.pack", './Static.pack')

            options = {
                "heroWeapons": self.heroWeaponCheckBox.isChecked(),
                "kettles": self.kettlesCheckbox.isChecked(),
                "inkColors": self.inkColorCheckBox.isChecked(),
                "inkColorSet": self.inkColorSetDropdown.currentIndex(),
                "music": self.musicCheckBox.isChecked(),
                "missionDialogue": self.missionDialogueCheckBox.isChecked(),
                "platform": self.platformDropdown.currentIndex(),
                "enemies": self.enemyCheckBox.isChecked(),
                "itemDrops": self.itemDropCheckBox.isChecked(),
                "itemDropSet": self.itemDropSetDropdown.currentIndex(),
            }

            self.options = options
            
            self.worker = RandomizationWorker("Splatoon_Rando_Files_work", options, currentSeed)
            #self.worker.progressUpdated.connect(self.progressDialog.updateProgress)
            self.worker.statusUpdated.connect(self.progressDialog.setStatus)
            self.worker.randomizationCompleted.connect(self.randomizationCompleted)
            self.worker.randomizationFailed.connect(self.onRandomizationError)
            self.worker.start()

    def exceptionHook(exctype, value, traceback):
            logging.exception("Unhandled exception:", exc_info=(exctype, value, traceback))
    
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Unexpected Error")
            sys.mainWindow.progressTextbox.setText("An error has occured!")
            sys.mainWindow.progressTextbox.setStyleSheet("color: red")
            QApplication.processEvents()
            msg.setText("An exception has occured! Please check the log file for more details.")
            msg.setDetailedText(f"{exctype.__name__}: {value}")
            msg.exec()

            sys.__excepthook__(exctype, value, traceback)

    sys.excepthook = exceptionHook

    app = QApplication(sys.argv)
    window = MainWindow()

    window.miscSettings['RandomizerSettings'] = { 
        'WeaponRandomizer': '0',
        'SkipOctoValleyIntro': '0',
        'SkipFirstNews': '0',
        'OctoValleyRestart': '0'
    }

    sys.mainWindow = window
    window.show()
    app.exec()

def main():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logFilename = f"logs/randomizer_log_{timestamp}.txt"

    if os.path.isdir("logs") == False:
        os.mkdir("logs")

    logging.basicConfig(
    filename=logFilename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Application started.")

    # Here we check if the user has all of the dependencies installed or not
    for package, license in dependencycheck.dependencies.items():
        isAllDepsInstalled = dependencycheck.checkIsMissing(package, license)

    if isAllDepsInstalled == False:
        packageString = ', '.join(dependencycheck.missingDependencies)
        response = input(f"The following dependencies are required to use this program but aren't installed: {packageString}.\nWould you like to install them now? [y/n]\n").strip().lower()
        if response == 'y': 
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages"], stdout=sys.stdout, stderr=sys.stderr) # I know there's --break-system-packages but idc
            print("\nThe required dependencies have all been installed! Please re-run the randomizer in order to use it.")
            exit()
        else:
            print('Terminating execution.')
            sys.exit()

    init()   
    

if __name__ == "__main__":
    main()