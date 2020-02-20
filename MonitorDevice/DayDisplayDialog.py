# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DayDisplayDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(620, 397)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 301, 181))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(0, 0, 271, 16))
        self.label.setStyleSheet("font: 57 10pt \"Quicksand Medium\";\n"
"color: rgb(0, 255, 255);")
        self.label.setObjectName("label")
        self.DaySoilMqlWidget = DaySoilMqlWidget(self.frame)
        self.DaySoilMqlWidget.setGeometry(QtCore.QRect(0, 10, 301, 171))
        self.DaySoilMqlWidget.setObjectName("DaySoilMqlWidget")
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(320, 20, 291, 181))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_2 = QtWidgets.QFrame(self.verticalLayoutWidget_2)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 271, 16))
        self.label_2.setStyleSheet("color: rgb(85, 255, 255);\n"
"font: 57 10pt \"Quicksand Medium\";")
        self.label_2.setObjectName("label_2")
        self.TemperatureAndHumidityMqlWidget = TemperatureAndHumidityMqlWidget(self.frame_2)
        self.TemperatureAndHumidityMqlWidget.setGeometry(QtCore.QRect(0, 10, 289, 171))
        self.TemperatureAndHumidityMqlWidget.setObjectName("TemperatureAndHumidityMqlWidget")
        self.verticalLayout_2.addWidget(self.frame_2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(410, 260, 99, 61))
        self.pushButton.setStyleSheet("font: 57 12pt \"Quicksand Medium\";\n"
"color: rgb(85, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 210, 301, 181))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_3 = QtWidgets.QFrame(self.verticalLayoutWidget_3)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.label_3 = QtWidgets.QLabel(self.frame_3)
        self.label_3.setGeometry(QtCore.QRect(0, 0, 158, 21))
        self.label_3.setStyleSheet("font: 57 10pt \"Quicksand Medium\";\n"
"color: rgb(85, 255, 255);")
        self.label_3.setObjectName("label_3")
        self.WaterPumpMqlWidget = WaterPumpMqlWidget(self.frame_3)
        self.WaterPumpMqlWidget.setGeometry(QtCore.QRect(0, 20, 301, 161))
        self.WaterPumpMqlWidget.setObjectName("WaterPumpMqlWidget")
        self.verticalLayout_3.addWidget(self.frame_3)

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "土壌水分"))
        self.label_2.setText(_translate("Dialog", "温度・湿度"))
        self.pushButton.setText(_translate("Dialog", "OK"))
        self.label_3.setText(_translate("Dialog", "自動給水システム"))
from daysoilmqlwidget import DaySoilMqlWidget
from temperatureandhumiditymqlwidget import TemperatureAndHumidityMqlWidget
from waterpumpmqlwidget import WaterPumpMqlWidget
