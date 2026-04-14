# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.NonModal)
        MainWindow.resize(788, 546)
        self.actionCheck_for_Updates = QAction(MainWindow)
        self.actionCheck_for_Updates.setObjectName(u"actionCheck_for_Updates")
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.actionOpen_Output_Folder = QAction(MainWindow)
        self.actionOpen_Output_Folder.setObjectName(u"actionOpen_Output_Folder")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(10, 0, 0, 0)
        self.generateSeedButton = QPushButton(self.tab)
        self.generateSeedButton.setObjectName(u"generateSeedButton")

        self.gridLayout.addWidget(self.generateSeedButton, 1, 2, 1, 1)

        self.browseButton = QPushButton(self.tab)
        self.browseButton.setObjectName(u"browseButton")

        self.gridLayout.addWidget(self.browseButton, 0, 2, 1, 1)

        self.randomizerSeedBox = QLineEdit(self.tab)
        self.randomizerSeedBox.setObjectName(u"randomizerSeedBox")

        self.gridLayout.addWidget(self.randomizerSeedBox, 1, 1, 1, 1)

        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.splatoon1Path = QLineEdit(self.tab)
        self.splatoon1Path.setObjectName(u"splatoon1Path")
        self.splatoon1Path.setReadOnly(True)

        self.gridLayout.addWidget(self.splatoon1Path, 0, 1, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(12, 0, -1, 8)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.kettlesCheckbox = QCheckBox(self.tab)
        self.kettlesCheckbox.setObjectName(u"kettlesCheckbox")
        self.kettlesCheckbox.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout_2.addWidget(self.kettlesCheckbox, 1, 0, 1, 1, Qt.AlignHCenter)

        self.itemDropCheckBox = QCheckBox(self.tab)
        self.itemDropCheckBox.setObjectName(u"itemDropCheckBox")

        self.gridLayout_2.addWidget(self.itemDropCheckBox, 5, 2, 1, 1, Qt.AlignHCenter)

        self.inkColorCheckBox = QCheckBox(self.tab)
        self.inkColorCheckBox.setObjectName(u"inkColorCheckBox")

        self.gridLayout_2.addWidget(self.inkColorCheckBox, 1, 1, 1, 1, Qt.AlignHCenter)

        self.missionDialogueCheckBox = QCheckBox(self.tab)
        self.missionDialogueCheckBox.setObjectName(u"missionDialogueCheckBox")

        self.gridLayout_2.addWidget(self.missionDialogueCheckBox, 1, 3, 1, 1, Qt.AlignHCenter)

        self.musicCheckBox = QCheckBox(self.tab)
        self.musicCheckBox.setObjectName(u"musicCheckBox")

        self.gridLayout_2.addWidget(self.musicCheckBox, 1, 2, 1, 1, Qt.AlignHCenter)

        self.inkColorSetDropdown = QComboBox(self.tab)
        self.inkColorSetDropdown.addItem("")
        self.inkColorSetDropdown.addItem("")
        self.inkColorSetDropdown.addItem("")
        self.inkColorSetDropdown.setObjectName(u"inkColorSetDropdown")

        self.gridLayout_2.addWidget(self.inkColorSetDropdown, 2, 1, 1, 1)

        self.heroWeaponCheckBox = QCheckBox(self.tab)
        self.heroWeaponCheckBox.setObjectName(u"heroWeaponCheckBox")

        self.gridLayout_2.addWidget(self.heroWeaponCheckBox, 5, 0, 1, 1, Qt.AlignHCenter)

        self.enemyCheckBox = QCheckBox(self.tab)
        self.enemyCheckBox.setObjectName(u"enemyCheckBox")

        self.gridLayout_2.addWidget(self.enemyCheckBox, 5, 1, 1, 1, Qt.AlignHCenter)

        self.itemDropSetDropdown = QComboBox(self.tab)
        self.itemDropSetDropdown.addItem("")
        self.itemDropSetDropdown.addItem("")
        self.itemDropSetDropdown.addItem("")
        self.itemDropSetDropdown.setObjectName(u"itemDropSetDropdown")

        self.gridLayout_2.addWidget(self.itemDropSetDropdown, 6, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.platformLayout = QHBoxLayout()
        self.platformLayout.setObjectName(u"platformLayout")
        self.platformLayout.setContentsMargins(21, 0, 0, 0)
        self.platformDropdown = QComboBox(self.tab)
        self.platformDropdown.addItem("")
        self.platformDropdown.addItem("")
        self.platformDropdown.setObjectName(u"platformDropdown")
        self.platformDropdown.setMaximumSize(QSize(170, 40))
        self.platformDropdown.setFrame(True)

        self.platformLayout.addWidget(self.platformDropdown, 0, Qt.AlignLeft)


        self.verticalLayout.addLayout(self.platformLayout)

        self.randomizeButton = QPushButton(self.tab)
        self.randomizeButton.setObjectName(u"randomizeButton")
        self.randomizeButton.setMinimumSize(QSize(250, 0))
        self.randomizeButton.setMaximumSize(QSize(250, 40))
        font = QFont()
        font.setBold(True)
        self.randomizeButton.setFont(font)

        self.verticalLayout.addWidget(self.randomizeButton, 0, Qt.AlignHCenter)

        self.progressTextbox = QLineEdit(self.tab)
        self.progressTextbox.setObjectName(u"progressTextbox")
        self.progressTextbox.setMinimumSize(QSize(400, 0))
        self.progressTextbox.setMaximumSize(QSize(400, 16777215))
        self.progressTextbox.setAlignment(Qt.AlignCenter)
        self.progressTextbox.setReadOnly(True)

        self.verticalLayout.addWidget(self.progressTextbox, 0, Qt.AlignHCenter)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(25)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(48, -1, -1, -1)
        self.skipOVIntroCheckBox = QCheckBox(self.tab_2)
        self.skipOVIntroCheckBox.setObjectName(u"skipOVIntroCheckBox")

        self.verticalLayout_3.addWidget(self.skipOVIntroCheckBox)

        self.skipNewsIntroCheckBox = QCheckBox(self.tab_2)
        self.skipNewsIntroCheckBox.setObjectName(u"skipNewsIntroCheckBox")

        self.verticalLayout_3.addWidget(self.skipNewsIntroCheckBox)

        self.addOVRestartCheckBox = QCheckBox(self.tab_2)
        self.addOVRestartCheckBox.setObjectName(u"addOVRestartCheckBox")

        self.verticalLayout_3.addWidget(self.addOVRestartCheckBox)

        self.verticalSpacer = QSpacerItem(20, 195, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.tabWidget.addTab(self.tab_2, "")

        self.horizontalLayout_3.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 788, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile_2 = QMenu(self.menubar)
        self.menuFile_2.setObjectName(u"menuFile_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile_2.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionCheck_for_Updates)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionDocumentation)
        self.menuFile_2.addAction(self.actionOpen_Output_Folder)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionCheck_for_Updates.setText(QCoreApplication.translate("MainWindow", u"Check for Updates...", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
        self.actionOpen_Output_Folder.setText(QCoreApplication.translate("MainWindow", u"Open Output Folder", None))
        self.generateSeedButton.setText(QCoreApplication.translate("MainWindow", u"Generate Seed", None))
        self.browseButton.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.randomizerSeedBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"If left blank, a seed will be randomly generated.", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Seed:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Splatoon 1 Files:", None))
#if QT_CONFIG(whatsthis)
        self.kettlesCheckbox.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.kettlesCheckbox.setText(QCoreApplication.translate("MainWindow", u"Kettles", None))
        self.itemDropCheckBox.setText(QCoreApplication.translate("MainWindow", u"Item Drops", None))
        self.inkColorCheckBox.setText(QCoreApplication.translate("MainWindow", u"Ink Colors", None))
        self.missionDialogueCheckBox.setText(QCoreApplication.translate("MainWindow", u"Mission Dialogue", None))
        self.musicCheckBox.setText(QCoreApplication.translate("MainWindow", u"Music", None))
        self.inkColorSetDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Octo Valley Ink Colors", None))
        self.inkColorSetDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Multiplayer Ink Colors", None))
        self.inkColorSetDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Octo Valley and Multiplayer Ink Colors", None))

        self.heroWeaponCheckBox.setText(QCoreApplication.translate("MainWindow", u"Hero Weapons", None))
        self.enemyCheckBox.setText(QCoreApplication.translate("MainWindow", u"Enemies", None))
        self.itemDropSetDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Favor Power Eggs", None))
        self.itemDropSetDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Favor Powerups", None))
        self.itemDropSetDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Completely Random", None))

#if QT_CONFIG(tooltip)
        self.itemDropSetDropdown.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Favor Power Eggs:</span> Makes it so that you are more likely to get Power Egg drops over specials/armor. Recommended for a more balanced experience.</p><p><span style=\" font-weight:600;\">Favor Powerups:</span> Makes it so that you are more likely to get specials/armor drops over Power Eggs. Recommended for a less balanced experience.</p><p><span style=\" font-weight:600;\">Completely Random:</span> Makes it so that the selected items are completely random. Recommended for a more chaotic experience.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.platformDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Platform: Wii U", None))
        self.platformDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Platform: Cemu", None))

        self.randomizeButton.setText(QCoreApplication.translate("MainWindow", u"Randomize", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Main", None))
        self.skipOVIntroCheckBox.setText(QCoreApplication.translate("MainWindow", u"Skip Octo Valley Intro Cutscene", None))
        self.skipNewsIntroCheckBox.setText(QCoreApplication.translate("MainWindow", u"Skip First News Intro", None))
        self.addOVRestartCheckBox.setText(QCoreApplication.translate("MainWindow", u"Add Restart Option to Octo Valley's Pause Menu", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Misc. Options", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuFile_2.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

