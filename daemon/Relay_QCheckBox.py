#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
import numpy as np

import sys

class Relay_QCheckBox(QtGui.QCheckBox):
    def __init__(self, parent=None, relay_id = 0, name = '', reltype = 0, value = 0):
        super(Relay_QCheckBox, self).__init__()
        self.parent = parent
        self.relay_id = relay_id
        self.value = value
        self.name = ''
        if (name != ''): self.name = name
        else: self.name = str(relay_id)

        self.type = 0
        if reltype == 0: self.type = 'SPDT'
        else: self.type = 'DPDT'

        self.initUI()
        
    def initUI(self):
        self.cb1 = QtGui.QCheckBox(self.name, self)
        self.CheckState = False
        #cb1.move(20, 20)
        #cb1.toggle()
        self.cb1.setStyleSheet("QCheckBox {  font-size: 12px; \
                                        font-weight:bold; \
                                        background-color:rgb(0,0,0); \
                                        color:rgb(0,255,0); }")
       
        self.cb1.stateChanged.connect(self.state_change)
        #self.parent.catchCheckBoxEvent(self.reltype, self.relay_id, self.value)

    def setCheckState(self, checkState):
        self.cb1.setCheckState(checkState)

    def state_change(self, state):
        self.CheckState = (state == QtCore.Qt.Checked)
        if self.CheckState == True:
            self.cb1.setStyleSheet("QCheckBox {  font-size: 12px; \
                                        font-weight:bold; \
                                        background-color:rgb(0,0,0); \
                                        color:rgb(255,0,0); }")
            #print self.type + ' ' + str(self.relay_id) + " Checked, " + "+" + str(self.value)
            self.parent.catchCheckBoxEvent(self.type, self.relay_id, self.value)
            
        else:
            self.cb1.setStyleSheet("QCheckBox {  font-size: 12px; \
                                        font-weight:bold; \
                                        background-color:rgb(0,0,0); \
                                        color:rgb(0,255,0); }")
            #print self.type + ' ' + str(self.relay_id) + " Unchecked, " + "-" + str(self.value)
            self.parent.catchCheckBoxEvent(self.type, self.relay_id, -1*self.value)

