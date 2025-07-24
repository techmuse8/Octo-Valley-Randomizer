import sys
import random
import string
from pathlib import Path
import shutil
import os
import hashlib
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QWidget,
    QSpinBox,
    QFileDialog,
    QMessageBox,
)
from randomizer import *
from hashcollection import *

globalGameDirectoryPath = '' 

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('mainUI.ui', self)

        centralWidget = self.findChild(QWidget, 'centralwidget')
        self.setCentralWidget(centralWidget)
        self.splatoon1Path.setPlaceholderText("Selected directory path will appear here.")
        self.setWindowTitle("Splatoon 1 Octo Valley Randomizer")
        self.setGeometry(100, 100, 706, 496)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.browseButton.clicked.connect(self.openDirectoryDialog)
        self.generateSeedButton.clicked.connect(self.generateSeed)
        self.setCentralWidget(centralWidget)
        self.inkColorSetDropdown.setEnabled(False)
        self.randomizeButton.clicked.connect(lambda: self.startRandomization(self.splatoon1Path.text()))
         
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

    def openDirectoryDialog(self):
        global globalGameDirectoryPath
        directoryPath = QFileDialog.getExistingDirectory(self, "Select the 'content' folder of your Splatoon 1 dump")
        #self.checkForValidGameFiles(directoryPath) 
        if self.checkForValidGameFiles(directoryPath):
            print(directoryPath)
            globalGameDirectoryPath = directoryPath
            self.splatoon1Path.setText(directoryPath)

    def generateSeed(self):
        characters = string.ascii_letters + string.digits
        randomString = ''.join(random.choice(characters) for i in range(10))
        self.randomizerSeedBox.setText(randomString)
        print("Seed: " + randomString)

    def updateRandomizeButtonState(self):
        anyChecked = any(checkbox.isChecked() for checkbox in self.checkboxes)
        self.randomizeButton.setEnabled(anyChecked)

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
                allValid = False

        return allValid
            

    def checkForValidGameFiles(self, gameRoot):
        """Goes through a process to ensure that a (valid) Splatoon 1 dump has been selected."""
        packFolder = os.path.join(gameRoot, 'Pack')
        messageFolder = os.path.join(gameRoot, 'Message')
        if os.path.isdir(packFolder) and os.path.isdir(messageFolder): # Check if this is a Splatoon 1 dump
            if self.checkGameFileHashes(packFolder, messageFolder, expected_hashes_2_12_1) == True: # If so, make sure that the selected dump is valid
                return True
            else:
                self.showErrorDialog('Error!', 'The selected Splatoon 1 dump is invalid! Ensure that your game files are valid.')
                return False
        else:
             self.showErrorDialog('Error!', 'Ensure that you have selected a Splatoon 1 dump!')

    def startRandomization(self, splatoon1DirectoryPath):
        try:
            shutil.copytree(f"{splatoon1DirectoryPath}/Pack", "Splatoon_Rando_Files/Pack")
            shutil.copytree(f"{splatoon1DirectoryPath}/Message", "Splatoon_Rando_Files/Message")
            shutil.copy(f"{splatoon1DirectoryPath}/Pack/Static.pack", './Static.pack')

        except FileExistsError:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning!")
            dlg.setText("An existing randomization already exists! Would you like to replace the current one!")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Warning)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                shutil.rmtree("Splatoon_Rando_Files")
                setupRandomization("Splatoon_Rando_Files", self.randomizerSeedBox.text())                
            else:
                return

        setupRandomization("Splatoon_Rando_Files", self.randomizerSeedBox.text())

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()