#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
import numpy as np

import sys

class main_widget(QtGui.QWidget):
    
    def __init__(self):
        super(main_widget, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.grid.setColumnStretch(0,1)
        self.grid.setColumnStretch(1,2)

class relay_check_box(QtGui.QCheckBox):
    def __init__(self, relay_id = 0, name = '', reltype = 0):
        super(relay_check_box, self).__init__()
        self.relay_id = relay_id
        self.name = ''
        if (name != ''): self.name = name
        else: self.name = str(relay_id)

        self.type = 0
        if reltype == 0: self.type = 'SPDT'
        else: self.type = 'DPDT'

        self.initUI()
        
    def initUI(self):
        cb1 = QtGui.QCheckBox(self.name, self)
        #cb1.move(20, 20)
        #cb1.toggle()
        cb1.stateChanged.connect(self.state_change)

    def state_change(self, state):
        if state == QtCore.Qt.Checked:
            print self.type + ' ' + str(self.relay_id) + " Checked"
        else:
            print self.type + ' ' + str(self.relay_id) + " Unchecked"

class remote_relay_gui(QtGui.QMainWindow):
    def __init__(self):
        super(remote_relay_gui, self).__init__()
        self.resize(750,250)
        self.move(100,100)
        self.setWindowTitle('Remote Relay Control')
        self.setAutoFillBackground(True)
        self.main_window = main_widget()
        self.initUI()
        
    def initUI(self): 
        self.setCentralWidget(self.main_window)
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)

        exportAction = QtGui.QAction('Export', self)
        exportAction.setShortcut('Ctrl+E')
        exportAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(exportAction)
        
        #intialize Tabs
        self.Init_Tabs()  
        self.main_window.grid.addWidget(self.tabs, 0,0,4,10)
       
        #Initialize SPDT Tab Checkboxes
        self.SPDT_CheckBox_Init()
        self.spdt_tab.grid.setRowStretch(6,1)
        self.spdt_tab.setLayout(self.spdt_tab.grid)

        #Initialize DPDT Tab Checkboxes
        self.DPDT_CheckBox_Init()
        self.dpdt_tab.grid.setRowStretch(6,1)
        self.dpdt_tab.setLayout(self.dpdt_tab.grid)
        #self.dpdt_tab.grid.setRowStretch(1,1)

        #Initialize ADC Tab Labels
        self.ADC_Label_Init()
        self.adc_tab.setLayout(self.adc_tab.grid)

        #Initialize Settings Tab
        self.settings_tab.setLayout(self.settings_tab.grid)
        self.settings_tab.grid.setRowStretch(1,1)
        self.settings_tab.grid.setColumnStretch(0,1)
        self.settings_tab.grid.setColumnStretch(1,10)

        #Initialize Raw Data Tab
        #self.Raw_Tab_Init()

        self.show()

    def ADC_Label_Init(self):
        cont1 = QtGui.QLabel('ADC')
        cont1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label1 = QtGui.QLabel('Value')
        label1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label2 = QtGui.QLabel('Label')
        label2.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")

        self.adc_tab.grid.addWidget(cont1, 0, 0, 1, 1)
        self.adc_tab.grid.addWidget(label1, 0, 1, 1, 1)
        self.adc_tab.grid.addWidget(label2, 0, 2, 1, 1)

        field_name  = [ 'ADC1:', 'ADC2:', 'ADC3:', 'ADC4:', 'ADC5:', 'ADC6:', 'ADC7:', 'ADC8:']
        field_value = [ '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V' ]

        self.adc_field_labels_qlabels = []        #List containing Static field Qlabels, do not change
        self.adc_field_values_qlabels = []       #List containing the value of the field, updated per packet
        
        self.adc_tab.grid.setColumnStretch(0,1)
        self.adc_tab.grid.setColumnStretch(1,1)
        self.adc_tab.grid.setColumnStretch(2,3)

        self.adc_tab.grid.addWidget(cont1, 0, 0, 1, 1)
        self.adc_tab.grid.addWidget(label1, 0, 1, 1, 1)
        self.adc_tab.grid.addWidget(label2, 0, 2, 1, 1)

        for i in range(len(field_name)):
            self.adc_field_labels_qlabels.append(QtGui.QLabel(field_name[i]))
            self.adc_field_labels_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            self.adc_field_values_qlabels.append(QtGui.QLabel(field_value[i]))
            self.adc_field_values_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            self.adc_tab.grid.addWidget(self.adc_field_labels_qlabels[i], 2+i, 0, 1, 1)
            self.adc_tab.grid.addWidget(self.adc_field_values_qlabels[i], 2+i, 1, 1, 1)

    def SPDT_CheckBox_Init(self):
        self.spdta_gb = QtGui.QGroupBox(self)
        self.spdta_gb.setStyleSheet("QGroupBox { border:2px solid rgb(0, 0, 0); }")
        self.gb_a_grid = QtGui.QGridLayout(self.spdta_gb)

        self.spdtb_gb = QtGui.QGroupBox(self)
        self.spdtb_gb.setStyleSheet("QGroupBox { border:2px solid rgb(0, 0, 0); }")
        self.gb_b_grid = QtGui.QGridLayout(self.spdtb_gb)

        cont1 = QtGui.QLabel('Control')
        cont1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label1 = QtGui.QLabel('Relay Function')
        label1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        cont2 = QtGui.QLabel('Control')
        cont2.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label2 = QtGui.QLabel('Relay Function')
        label2.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")

        self.gb_a_grid.addWidget(cont1, 0,0,1,1)
        self.gb_a_grid.addWidget(label1, 0,1,1,1)
        self.gb_b_grid.addWidget(cont2, 0,0,1,1)
        self.gb_b_grid.addWidget(label2, 0,1,1,1)

        for i in range(8):
            self.cb = relay_check_box(i+1, 'SPDT'+str(i+1), 0)
            self.gb_a_grid.addWidget(self.cb, i+1,0,1,1)
        for i in range(8):
            self.cb = relay_check_box(8+i+1, 'SPDT'+str(8+i+1), 0)
            self.gb_b_grid.addWidget(self.cb, i+1,0,1,1)

        spdta_gb_label = QtGui.QLabel('SPDT Bank A')
        spdta_gb_label.setStyleSheet("QLabel { font-size: 18px;font-weight:bold; }")
        spdta_gb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spdt_tab.grid.addWidget(spdta_gb_label, 0,0,1,1)

        spdtb_gb_label = QtGui.QLabel('SPDT Bank B')
        spdtb_gb_label.setStyleSheet("QLabel { font-size: 18px;font-weight:bold; }")
        spdtb_gb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spdt_tab.grid.addWidget(spdtb_gb_label, 0,1,1,1)

        self.spdt_tab.grid.addWidget(self.spdta_gb, 1,0,1,1)
        self.spdt_tab.grid.addWidget(self.spdtb_gb, 1,1,1,1)

    def DPDT_CheckBox_Init(self):
        self.dpdta_gb = QtGui.QGroupBox(self)
        self.dpdta_gb.setStyleSheet("QGroupBox { border:2px solid rgb(0, 0, 0); }")
        self.gb_a_grid = QtGui.QGridLayout(self.dpdta_gb)

        self.dpdtb_gb = QtGui.QGroupBox(self)
        self.dpdtb_gb.setStyleSheet("QGroupBox { border:2px solid rgb(0, 0, 0); }")
        self.gb_b_grid = QtGui.QGridLayout(self.dpdtb_gb)

        cont1 = QtGui.QLabel('Control')
        cont1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label1 = QtGui.QLabel('Relay Function')
        label1.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        cont2 = QtGui.QLabel('Control')
        cont2.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")
        label2 = QtGui.QLabel('Relay Function')
        label2.setStyleSheet("QLabel { font-size: 16px;font-weight:bold; text-decoration:underline}")

        self.gb_a_grid.addWidget(cont1, 0,0,1,1)
        self.gb_a_grid.addWidget(label1, 0,1,1,1)
        self.gb_b_grid.addWidget(cont2, 0,2,1,1)
        self.gb_b_grid.addWidget(label2, 0,3,1,1)

        for i in range(8):
            self.cb = relay_check_box(i+1, 'DPDT'+str(i+1), 1)
            self.gb_a_grid.addWidget(self.cb, i+1,0,1,1)
        for i in range(8):
            self.cb = relay_check_box(8+i+1, 'DPDT'+str(8+i+1), 1)
            self.gb_b_grid.addWidget(self.cb, i+1,2,1,1)

        dpdta_gb_label = QtGui.QLabel('DPDT Bank A')
        dpdta_gb_label.setStyleSheet("QLabel { font-size: 18px;font-weight:bold; }")
        dpdta_gb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dpdt_tab.grid.addWidget(dpdta_gb_label, 0,0,1,1)

        dpdtb_gb_label = QtGui.QLabel('DPDT Bank B')
        dpdtb_gb_label.setStyleSheet("QLabel { font-size: 18px;font-weight:bold; }")
        dpdtb_gb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dpdt_tab.grid.addWidget(dpdtb_gb_label, 0,1,1,1)

        self.dpdt_tab.grid.addWidget(self.dpdta_gb, 1,0,1,1)
        self.dpdt_tab.grid.addWidget(self.dpdtb_gb, 1,1,1,1)

    def Init_Tabs(self):
        self.tabs = QtGui.QTabWidget()
        
        self.spdt_tab = QtGui.QWidget()	
        self.spdt_tab.grid = QtGui.QGridLayout()
        self.tabs.addTab(self.spdt_tab,"SPDT Relays")
        
        self.dpdt_tab = QtGui.QWidget()	
        self.dpdt_tab.grid = QtGui.QGridLayout()
        self.tabs.addTab(self.dpdt_tab,"DPDT Relays")

        self.adc_tab = QtGui.QWidget()	
        self.adc_tab.grid = QtGui.QGridLayout()
        self.tabs.addTab(self.adc_tab,"ADC")

        self.settings_tab = QtGui.QWidget()
        self.settings_tab.grid = QtGui.QGridLayout()	
        self.tabs.addTab(self.settings_tab,"Settings")
        

def main():
    app = QtGui.QApplication(sys.argv)
    ex = funcube_tlm_gui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()