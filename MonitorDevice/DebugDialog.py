# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DebugDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(414, 370)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(130, 310, 161, 51))
        self.pushButton.setAcceptDrops(False)
        self.pushButton.setStyleSheet("font: 57 12pt \"Quicksand Medium\";\n"
"color: rgb(85, 255, 255)")
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 401, 271))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("device.png"))
        self.label.setObjectName("label")
        self.label_water_connect = QtWidgets.QLabel(Dialog)
        self.label_water_connect.setGeometry(QtCore.QRect(30, 110, 75, 31))
        self.label_water_connect.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_water_connect.setText("")
        self.label_water_connect.setObjectName("label_water_connect")
        self.label_sensor_connect = QtWidgets.QLabel(Dialog)
        self.label_sensor_connect.setGeometry(QtCore.QRect(280, 50, 75, 35))
        self.label_sensor_connect.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_sensor_connect.setText("")
        self.label_sensor_connect.setObjectName("label_sensor_connect")
        self.label_fertilizer_connect = QtWidgets.QLabel(Dialog)
        self.label_fertilizer_connect.setGeometry(QtCore.QRect(300, 230, 91, 31))
        self.label_fertilizer_connect.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_fertilizer_connect.setText("")
        self.label_fertilizer_connect.setObjectName("label_fertilizer_connect")

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "OK"))
