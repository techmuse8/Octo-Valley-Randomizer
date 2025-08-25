import sys
import random
import string
from pathlib import Path
import shutil
import os
import hashlib
import logging
import datetime
import importlib.util
import subprocess

import dependencycheck

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
                        self.progressUpdated.emit("Randomization failed!")
                except Exception as e:
                    print(f"Error in worker thread: {e}")  
                    self.statusUpdated.emit("An error occurred during randomization.")
                    self.progressUpdated.emit(0)
                
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
            self.randomizeButton.clicked.connect(lambda: self.startRandomization(self.splatoon1Path.text()))
            self.actionCheck_for_Updates.triggered.connect(self.checkForUpdates)
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
            self.inkColorCheckBox.stateChanged.connect(self.updateInkColorDropdownState)
            
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
            directoryPath = QFileDialog.getExistingDirectory(self, "Select the 'content' folder of your Splatoon 1 dump")
            if self.checkForValidGameFiles(directoryPath):
                print(directoryPath)
                print(self.gameRegion)
                globalGameDirectoryPath = directoryPath
                self.splatoon1Path.setText(directoryPath)
                self.updateRandomizeButtonState()
                print(self.titleID)

        def generateSeed(self):
            characters = string.ascii_letters + string.digits
            randomString = ''.join(random.choice(characters) for i in range(10))
            self.randomizerSeedBox.setText(randomString)
            print("Seed: " + randomString)

        def updateRandomizeButtonState(self):
            anyChecked = any(checkbox.isChecked() for checkbox in self.checkboxes)
            pathText = self.splatoon1Path.text().strip()
            hasValidPath = len(pathText) > 0
            self.randomizeButton.setEnabled(anyChecked and hasValidPath)

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

        def updateInkColorDropdownState(self, state):
            if state == Qt.Checked:
                self.inkColorSetDropdown.setEnabled(True)
            else:
                self.inkColorSetDropdown.setEnabled(False)

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
        
        def checkGameFileHashes(self, packDir, messageDir, expected_hashes):
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

                if actualFile:
                    actualHash = self.computeMD5(actualFile)
                    if actualHash != expectedHash:
                        print(f"Invalid file hash for {filename}: expected {expectedHash}, got {actualHash} instead")
                        allValid = False
                    else:
                        print(f"Valid {filename}")
                else:
                    print(f"Missing {filename}")

            return allValid
                
        def checkGameRegion(self, messageDir):
            messageFiles = os.listdir(messageDir)
            for filename in messageFiles:
                print
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
            packFolder = os.path.join(gameRoot, 'Pack')
            messageFolder = os.path.join(gameRoot, 'Message')

            if os.path.isdir(packFolder) and os.path.isdir(messageFolder): # Check if this is a Splatoon 1 dump
                if self.checkGameFileHashes(packFolder, messageFolder, hashcollection.expected_hashes_2_12_1) == True: # If so, make sure that the selected dump is a valid 2.12.1 one
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
        
        def randomizationCompleted(self):
            """Handle completion of randomization."""
            QTimer.singleShot(1000, self.progressDialog.close)
            self.finalizeRandomization()
            
            self.progressTextbox.setStyleSheet("color: green;")
            self.progressTextbox.setText("Randomization completed!")
            self.randomizeButton.setEnabled(True)  # Enable the randomize button again if initially disabled
        
        def finalizeRandomization(self):
            """Moves all the randomized files to a dedicated output folder."""
            if self.platformDropdown.currentIndex() == 0: # For Wii U
                
                outputRandoDir = os.path.join('output/Wii U/', f'{self.randomizerSeedBox.text()}/sdcafiine/{self.titleID}/Octo Valley Randomizer - Seed {self.randomizerSeedBox.text()}')
                if os.path.isdir(outputRandoDir): # Yet another cleanup check
                    shutil.rmtree(outputRandoDir)
                self.copyOutputRandomizer(outputRandoDir + '/content')

            if self.platformDropdown.currentIndex() == 1: # For Cemu
                outputRandoDir = 'output/Cemu/' + f'{self.randomizerSeedBox.text()}/' + f'Octo Valley Randomizer - Seed {self.randomizerSeedBox.text()}'
                if os.path.isdir(outputRandoDir):
                    shutil.rmtree(outputRandoDir)
                self.copyOutputRandomizer(outputRandoDir + '/content')
                with open ('assets/rules.txt', 'r') as file:
                    cemuRulesTxt = file.read()
                modifiedCemuRulesTxt = cemuRulesTxt.replace("{seed}", self.randomizerSeedBox.text())
                
                with open (outputRandoDir + '/rules.txt', "x") as file:
                    file.write(modifiedCemuRulesTxt)
                
            if self.options["heroWeapons"]:
                if self.options["platform"] == 1:
                    if os.path.exists('patches/cemu_OV_weapon.txt'):
                        print("Copying weapon patches for Cemu")
                        shutil.move("patches/cemu_OV_weapon.txt", outputRandoDir + '/patches.txt')
                elif self.options["platform"] == 0:
                    print('Copying weapon patches for Wii U')
                    if os.path.exists('patches/consoleWeaponPatches.hax'):    
                        os.makedirs(os.path.join('output/Wii U/', f'{self.randomizerSeedBox.text()}/codepatches/{self.titleID}'))
                        shutil.move("patches/consoleWeaponPatches.hax", 'output/Wii U/' + f'{self.randomizerSeedBox.text()}/codepatches/{self.titleID}/OctoValleyWeaponPatches.hax')

            
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
            }

            self.options = options
            
            
            self.worker = RandomizationWorker("Splatoon_Rando_Files_work", options, currentSeed)
            #self.worker.progressUpdated.connect(self.progressDialog.updateProgress)
            self.worker.statusUpdated.connect(self.progressDialog.setStatus)
            self.worker.randomizationCompleted.connect(self.randomizationCompleted)
            self.worker.start()  # Start the thread

            


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
    level=logging.ERROR,
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