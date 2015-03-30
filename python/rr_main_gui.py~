#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
import numpy as np

import sys
from Relay_QCheckBox import *

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(785, 275)
        self.setFixedWidth(785)
        self.setFixedHeight(275)
        self.setWindowTitle('Remote Relay Control')
        self.setContentsMargins(0,0,0,0)
        self.spdt_cb = []   #list to hold spdt relay check boxes
        self.dpdt_cb = []   #list to hold dpdt relay check boxes
        self.spdt_a_value = 0   #SPDT BANK A Value, 0-255
        self.spdt_b_value = 0   #SPDT BANK B Value, 0-255
        self.dpdt_a_value = 0   #DPDT BANK A Value, 0-255
        self.dpdt_b_value = 0   #DPDT BANK B Value, 0-255

        self.set_relay_msg = '' # '$,R,AAA,BBB,CCC,DDD'

        self.initUI()
        self.darken()
        self.setFocus()

    def initUI(self):
        self.initFrames()
        self.initSPDTCheckBoxes()
        self.initDPDTCheckBoxes()
        self.initADC()
        self.initNet()
        self.initControls()
        self.connectSignals()

    def connectSignals(self):
        self.resetButton.clicked.connect(self.resetButtonEvent)  

    def resetButtonEvent(self):
        for i in range(16):
            if self.spdt_cb[i].CheckState==True: self.spdt_cb[i].setCheckState(QtCore.Qt.Unchecked)
            if self.dpdt_cb[i].CheckState==True: self.dpdt_cb[i].setCheckState(QtCore.Qt.Unchecked)

    def catchCheckBoxEvent(self, reltype, relay_id, value):
        #print str(reltype) + str(relay_id) + " " + str(value)
        if   (reltype == 'SPDT'):
            if (relay_id <= 8): self.spdt_a_value += value
            else:  self.spdt_b_value += value
        elif (reltype == 'DPDT'):
            if (relay_id <= 8): self.dpdt_a_value += value
            else:  self.dpdt_b_value += value
        self.formatSetRelayMsg()

        #print '$,R,' + str(self.spdt_a_value) + ',' +str(self.spdt_b_value) + ',' +str(self.dpdt_a_value) + ',' +str(self.dpdt_b_value)

    def formatSetRelayMsg(self):
        self.set_relay_msg = '$,R,'
        if   (len(str(self.spdt_a_value)) == 1): self.set_relay_msg += '00' + str(self.spdt_a_value)
        elif (len(str(self.spdt_a_value)) == 2): self.set_relay_msg += '0'  + str(self.spdt_a_value)
        elif (len(str(self.spdt_a_value)) == 3): self.set_relay_msg +=        str(self.spdt_a_value)
        self.set_relay_msg += ','

        if   (len(str(self.spdt_b_value)) == 1): self.set_relay_msg += '00' + str(self.spdt_b_value)
        elif (len(str(self.spdt_b_value)) == 2): self.set_relay_msg += '0'  + str(self.spdt_b_value)
        elif (len(str(self.spdt_b_value)) == 3): self.set_relay_msg +=        str(self.spdt_b_value)
        self.set_relay_msg += ','

        if   (len(str(self.dpdt_a_value)) == 1): self.set_relay_msg += '00' + str(self.dpdt_a_value)
        elif (len(str(self.dpdt_a_value)) == 2): self.set_relay_msg += '0'  + str(self.dpdt_a_value)
        elif (len(str(self.dpdt_a_value)) == 3): self.set_relay_msg +=        str(self.dpdt_a_value)
        self.set_relay_msg += ','

        if   (len(str(self.dpdt_b_value)) == 1): self.set_relay_msg += '00' + str(self.dpdt_b_value)
        elif (len(str(self.dpdt_b_value)) == 2): self.set_relay_msg += '0'  + str(self.dpdt_b_value)
        elif (len(str(self.dpdt_b_value)) == 3): self.set_relay_msg +=        str(self.dpdt_b_value)

        print self.set_relay_msg

    def initADC(self):
        field_name  = [ 'ADC1:', 'ADC2:', 'ADC3:', 'ADC4:', 'ADC5:', 'ADC6:', 'ADC7:', 'ADC8:']
        self.field_value = [ '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V' ]

        self.adc_field_labels_qlabels = []        #List containing Static field Qlabels, do not change
        self.adc_field_values_qlabels = []       #List containing the value of the field, updated per packet

        vbox = QtGui.QVBoxLayout()

        for i in range(len(field_name)):
            hbox = QtGui.QHBoxLayout()
            self.adc_field_labels_qlabels.append(QtGui.QLabel(field_name[i]))
            self.adc_field_labels_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            self.adc_field_values_qlabels.append(QtGui.QLabel(self.field_value[i]))
            self.adc_field_values_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            hbox.addWidget(self.adc_field_labels_qlabels[i])
            hbox.addWidget(self.adc_field_values_qlabels[i])
            vbox.addLayout(hbox)

        self.adc_fr.setLayout(vbox)

    def initNet(self):
        ipAddrTextBox = QtGui.QLineEdit()
        ipAddrTextBox.setText("192.168.42.11")
        ipAddrTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        ipAddrTextBox.setMaxLength(15)

        portTextBox = QtGui.QLineEdit()
        portTextBox.setText("2000")
        portTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        portTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        portTextBox.setMaxLength(5)
        portTextBox.setFixedWidth(50)

        label = QtGui.QLabel('Status:')
        label.setAlignment(QtCore.Qt.AlignRight)
        self.net_label = QtGui.QLabel('Disconnected')
        self.net_label.setAlignment(QtCore.Qt.AlignLeft)
        self.net_label.setFixedWidth(150)

        self.connectButton = QtGui.QPushButton("Connect")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(ipAddrTextBox)
        hbox1.addWidget(portTextBox)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(label)
        hbox2.addWidget(self.net_label)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.connectButton)
        vbox.addLayout(hbox2)

        self.net_fr.setLayout(vbox)

    def initControls(self):
        self.updateButton = QtGui.QPushButton("Update")
        self.resetButton = QtGui.QPushButton("Reset")
        self.readRelayButton = QtGui.QPushButton("Read Relay")
        self.readVoltButton = QtGui.QPushButton("Read ADCs")
        self.readStatusButton = QtGui.QPushButton("Read Status")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.readRelayButton)
        hbox1.addWidget(self.readStatusButton)
        hbox1.addWidget(self.readVoltButton)

        hbox2 = QtGui.QHBoxLayout()
        #hbox.addStretch(1)
        hbox2.addWidget(self.updateButton)
        hbox2.addWidget(self.resetButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.button_fr.setLayout(vbox)

    def initSPDTCheckBoxes(self):
        hbox1 = QtGui.QHBoxLayout()

        for i in range(8):
            self.spdt_cb.append(Relay_QCheckBox(self, i+1  , 'SPDT'+str(i+1)  , 0, pow(2,i)))
            hbox1.addWidget(self.spdt_cb[i])
        hbox2 = QtGui.QHBoxLayout()
        for i in range(8):
            self.spdt_cb.append(Relay_QCheckBox(self, i+1+8, 'SPDT'+str(i+1+8), 0, pow(2,i)))
            hbox2.addWidget(self.spdt_cb[i+8])

        #for i in range(16): print str(self.spdt_cb[i].name)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.spdt_fr.setLayout(vbox)
    
    def initDPDTCheckBoxes(self):
        hbox1 = QtGui.QHBoxLayout()
        for i in range(8):
            self.dpdt_cb.append(Relay_QCheckBox(self, i+1, 'DPDT'+str(i+1), 1, pow(2,i)))
            hbox1.addWidget(self.dpdt_cb[i])
        hbox2 = QtGui.QHBoxLayout()
        for i in range(8):
            self.dpdt_cb.append(Relay_QCheckBox(self, i+1+8, 'DPDT'+str(i+1+8), 1, pow(2,i)))
            hbox2.addWidget(self.dpdt_cb[i+8])

        #for i in range(16): print str(self.dpdt_cb[i].name)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.dpdt_fr.setLayout(vbox)

    def initFrames(self):
        self.spdt_fr = QtGui.QFrame(self)
        self.spdt_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.spdt_fr.setFixedWidth(650)

        self.dpdt_fr = QtGui.QFrame(self)
        self.dpdt_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.dpdt_fr.setFixedWidth(650)

        self.adc_fr = QtGui.QFrame(self)
        self.adc_fr.setFrameShape(QtGui.QFrame.StyledPanel)

        self.button_fr = QtGui.QFrame(self)
        self.button_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_fr.setFixedWidth(445)

        self.net_fr = QtGui.QFrame(self)
        self.net_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.net_fr.setFixedWidth(200)

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()

        hbox2.addWidget(self.net_fr)
        hbox2.addWidget(self.button_fr)        

        vbox.addWidget(self.spdt_fr)
        vbox.addWidget(self.dpdt_fr)
        vbox.addLayout(hbox2)
        
        hbox1.addLayout(vbox)
        hbox1.addWidget(self.adc_fr)

        self.setLayout(hbox1)

    def darken(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.black)
        palette.setColor(QtGui.QPalette.WindowText,QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
        self.setPalette(palette)


