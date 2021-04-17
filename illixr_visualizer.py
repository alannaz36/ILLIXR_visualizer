# Filename: illixr_visualizer.py
""" ILLIXR Visualizer is a visualization interface for analyzing ILLIXR data
    logged in databases. It is a desktop application following an MVC
    design pattern, serving as a modular addition to the ILLIXR project.
    It is built using Python, PyQt5, and Plotly. """

import pandas as pd
import sqlite3

import plotly.offline as po
import plotly.graph_objs as go
import plotly.express as px

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5 import QtCore, QtGui, QtWidgets

import sys

__author__ = 'Alanna Zoscak'

# Subclass of QMainWindow to set up the application's GUI
class VisualizerGUI(QMainWindow):
    """ ILLIXR_Visualizer's View (GUI).
        Displays plots and interfaces with user. """
    def __init__(self):
        """ View initializer. """
        super().__init__()
        
        # Main window properties
        self.setWindowTitle("ILLIXR Visualizer")
        w = 1000
        h = 600
        self.resize(w, h)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("illixr_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        self.generalLayout = QGridLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        
        self._createMenu(w)
        self._createDisplay()
        self._createPageNav()
        
    def _createMenu(self, w):
        """ The menu bar at the top of the app.
            Exposes the functionality for uploading the databases,
            altering plot settings, and saving the plot. """
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, w, 30))
        
        self.menuFile = QtWidgets.QMenu(self.menubar)
        #self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        
        self.menuData = QtWidgets.QMenu(self.menubar)
        #self.menuData.setObjectName("menuData")
        self.menuData.setTitle("Data")
        
        self.menuPlotSettings = QtWidgets.QMenu(self.menubar)
        #self.menuPlotSettings.setObjectName("menuPlotSettings")
        self.menuPlotSettings.setTitle("Plot Settings")
        
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        #self.menuHelp.setObjectName("menuHelp")
        self.menuHelp.setTitle("Help")
        
        self.setMenuBar(self.menubar)
        
        # Add actions - sub categories of menu items
        self.actionNew = QtWidgets.QAction(self)
        #self.actionNew.setObjectName("actionNew")
        self.actionNew.setText("New")
        
        self.actionSave = QtWidgets.QAction(self)
        #self.actionSave.setObjectName("actionSave")
        self.actionSave.setText("Save")
        
        self.actionPluginNames = QtWidgets.QAction(self)
        #self.actionPlugins.setObjectName("actionPluginNames")
        self.actionPluginNames.setText("Plugin Names")
        
        self.actionSwitchboard_Data = QtWidgets.QAction(self)
        #self.actionSwitchboard_Data.setObjectName("actionSwitchboard_Data")
        self.actionSwitchboard_Data.setText("Switchboard Data")
        
        self.actionThreadloop_Data = QtWidgets.QAction(self)
        #self.actionThreadloop_Data.setObjectName("actionThreadloop_Data")
        self.actionThreadloop_Data.setText("Threadloop Data")
        
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuData.addAction(self.actionPluginNames)
        self.menuData.addAction(self.actionSwitchboard_Data)
        self.menuData.addAction(self.actionThreadloop_Data)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuData.menuAction())
        self.menubar.addAction(self.menuPlotSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
    
    def _createDisplay(self):
        """ The display is the interactive plot of the data.
            Starts out as an instructive label. """
        
    
    def _createPageNav(self):
        """ Creates the navigation bar beneath the plot which
            enables the user to navigate between pages of the plot """
        
class VisualizerController():
    """ ILLIXR Visualizer's Controller.
        Interfaces between the Model and View. """

class VisualizerData():
    """ ILLIXR Visualizer's Model. 
        Holds application settings and loaded database data. """

if __name__ == '__main__':
    illixr_visualizer = QApplication(sys.argv)
    view = VisualizerGUI()
    view.show()
    sys.exit(illixr_visualizer.exec_())
        
        
        
