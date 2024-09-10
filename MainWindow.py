# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QHBoxLayout,
    QLabel, QLayout, QListView, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1007, 746)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.startWavlengthLabel = QLabel(self.centralwidget)
        self.startWavlengthLabel.setObjectName(u"startWavlengthLabel")

        self.horizontalLayout.addWidget(self.startWavlengthLabel)

        self.startWavlengthDoubleSpinBox = QDoubleSpinBox(self.centralwidget)
        self.startWavlengthDoubleSpinBox.setObjectName(u"startWavlengthDoubleSpinBox")
        self.startWavlengthDoubleSpinBox.setMinimum(600.000000000000000)
        self.startWavlengthDoubleSpinBox.setMaximum(1750.000000000000000)
        self.startWavlengthDoubleSpinBox.setValue(1500.000000000000000)

        self.horizontalLayout.addWidget(self.startWavlengthDoubleSpinBox)

        self.stopWavelengthLabel = QLabel(self.centralwidget)
        self.stopWavelengthLabel.setObjectName(u"stopWavelengthLabel")

        self.horizontalLayout.addWidget(self.stopWavelengthLabel)

        self.stopWavelengthDoubleSpinBox = QDoubleSpinBox(self.centralwidget)
        self.stopWavelengthDoubleSpinBox.setObjectName(u"stopWavelengthDoubleSpinBox")
        self.stopWavelengthDoubleSpinBox.setMinimum(600.000000000000000)
        self.stopWavelengthDoubleSpinBox.setMaximum(1750.000000000000000)
        self.stopWavelengthDoubleSpinBox.setValue(1600.000000000000000)

        self.horizontalLayout.addWidget(self.stopWavelengthDoubleSpinBox)

        self.sensitivityLabel = QLabel(self.centralwidget)
        self.sensitivityLabel.setObjectName(u"sensitivityLabel")

        self.horizontalLayout.addWidget(self.sensitivityLabel)

        self.sensitivityComboBox = QComboBox(self.centralwidget)
        self.sensitivityComboBox.addItem("")
        self.sensitivityComboBox.addItem("")
        self.sensitivityComboBox.addItem("")
        self.sensitivityComboBox.addItem("")
        self.sensitivityComboBox.addItem("")
        self.sensitivityComboBox.setObjectName(u"sensitivityComboBox")

        self.horizontalLayout.addWidget(self.sensitivityComboBox)

        self.referenceLevelLabel = QLabel(self.centralwidget)
        self.referenceLevelLabel.setObjectName(u"referenceLevelLabel")

        self.horizontalLayout.addWidget(self.referenceLevelLabel)

        self.referenceLevelDoubleSpinBox = QDoubleSpinBox(self.centralwidget)
        self.referenceLevelDoubleSpinBox.setObjectName(u"referenceLevelDoubleSpinBox")
        self.referenceLevelDoubleSpinBox.setDecimals(1)
        self.referenceLevelDoubleSpinBox.setMinimum(-90.000000000000000)
        self.referenceLevelDoubleSpinBox.setMaximum(20.000000000000000)
        self.referenceLevelDoubleSpinBox.setSingleStep(0.100000000000000)

        self.horizontalLayout.addWidget(self.referenceLevelDoubleSpinBox)

        self.resoltuionNmLabel = QLabel(self.centralwidget)
        self.resoltuionNmLabel.setObjectName(u"resoltuionNmLabel")

        self.horizontalLayout.addWidget(self.resoltuionNmLabel)

        self.resoltuionNmDoubleSpinBox = QDoubleSpinBox(self.centralwidget)
        self.resoltuionNmDoubleSpinBox.setObjectName(u"resoltuionNmDoubleSpinBox")
        self.resoltuionNmDoubleSpinBox.setMinimum(0.050000000000000)
        self.resoltuionNmDoubleSpinBox.setMaximum(10.000000000000000)
        self.resoltuionNmDoubleSpinBox.setSingleStep(0.100000000000000)
        self.resoltuionNmDoubleSpinBox.setValue(0.100000000000000)

        self.horizontalLayout.addWidget(self.resoltuionNmDoubleSpinBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.SweepPushButton = QPushButton(self.centralwidget)
        self.SweepPushButton.setObjectName(u"SweepPushButton")

        self.horizontalLayout_2.addWidget(self.SweepPushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.plotWidget = PlotWidget(self.centralwidget)
        self.plotWidget.setObjectName(u"plotWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.plotWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.listView = QListView(self.centralwidget)
        self.listView.setObjectName(u"listView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.listView)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.DeletePushButton = QPushButton(self.centralwidget)
        self.DeletePushButton.setObjectName(u"DeletePushButton")

        self.horizontalLayout_6.addWidget(self.DeletePushButton)

        self.SavePushButton = QPushButton(self.centralwidget)
        self.SavePushButton.setObjectName(u"SavePushButton")

        self.horizontalLayout_6.addWidget(self.SavePushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")

        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.horizontalLayout_3.setStretch(0, 1)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4.setStretch(0, 4)
        self.horizontalLayout_4.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1007, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.startWavlengthLabel.setText(QCoreApplication.translate("MainWindow", u"Start Wavlength (nm)", None))
        self.stopWavelengthLabel.setText(QCoreApplication.translate("MainWindow", u"Stop Wavelength (nm)", None))
        self.sensitivityLabel.setText(QCoreApplication.translate("MainWindow", u"Sensitivity", None))
        self.sensitivityComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Hold", None))
        self.sensitivityComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Auto", None))
        self.sensitivityComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"High 1", None))
        self.sensitivityComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"High 2", None))
        self.sensitivityComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"High 3", None))

        self.referenceLevelLabel.setText(QCoreApplication.translate("MainWindow", u"Reference Level (dBm)", None))
        self.resoltuionNmLabel.setText(QCoreApplication.translate("MainWindow", u"Resoltuion (nm)", None))
        self.SweepPushButton.setText(QCoreApplication.translate("MainWindow", u"Sweep", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Visible", None))
        self.DeletePushButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.SavePushButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
    # retranslateUi

