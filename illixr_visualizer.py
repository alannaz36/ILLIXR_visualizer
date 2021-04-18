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

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QListWidget, QAbstractItemView
from PyQt5.QtWidgets import QToolButton, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView
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
        illixr_img = QtGui.QPixmap("illixr_icon_square.png") #.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
        icon.addPixmap(illixr_img, QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        
        self.actionUpload = QtWidgets.QAction(self)
        #self.actionUpload.setObjectName("actionUpload")
        self.actionUpload.setText("Upload Data")
        self.actionUpload.setShortcut("Ctrl+U")
        
        #self.actionPluginNames = QtWidgets.QAction(self)
        #self.actionPlugins.setObjectName("actionPluginNames")
        #self.actionPluginNames.setText("Plugin Names")
        
        #self.actionSwitchboard_Data = QtWidgets.QAction(self)
        #self.actionSwitchboard_Data.setObjectName("actionSwitchboard_Data")
        #self.actionSwitchboard_Data.setText("Switchboard Data")
        
        #self.actionThreadloop_Data = QtWidgets.QAction(self)
        #self.actionThreadloop_Data.setObjectName("actionThreadloop_Data")
        #self.actionThreadloop_Data.setText("Threadloop Data")
        
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuData.addAction(self.actionUpload)
        
        #self.menuData.addAction(self.actionPluginNames)
        #self.menuData.addAction(self.actionSwitchboard_Data)
        #self.menuData.addAction(self.actionThreadloop_Data)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuData.menuAction())
        self.menubar.addAction(self.menuPlotSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
    
    def _createDisplay(self):
        """ The display is the interactive plot of the data.
            Starts out as an instructive label. """
        self.displayLayout = QHBoxLayout()
        
        # Creates plugin list with title: self.pluginListLayout
        self._createPluginList()
        self.displayLayout.addLayout(self.pluginListLayout)

        # Create figure region: self.figureRegion
        self._createFigureRegion()
        self.displayLayout.addWidget(self.figureRegion, 1) # Only display stretches
        
        # Add full display to main window
        self.generalLayout.addLayout(self.displayLayout, 0, 0, 10, 23)
    
    def _createPluginList(self):
        """ Creates the left-hand reorderable Plugin list. """
        self.pluginListLayout = QVBoxLayout() # Overall layout of this section
        
        # Label for plugin list
        pluginLabel = QLabel("Plugins")
        boldFont = QtGui.QFont()
        boldFont.setBold(True)
        pluginLabel.setFont(boldFont)
        pluginLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.pluginListLayout.addWidget(pluginLabel)
        
        self.pluginList = QListWidget() # Orderable plugin list
        self.strList = ['No plugins provided yet.', 'Add plugin names in Data.']
        self.pluginList.addItems(self.strList);
        self.pluginList.setDragDropMode(QAbstractItemView.InternalMove)
        self.pluginListLayout.addWidget(self.pluginList)
    
    def _createFigureRegion(self):
        """ Creates the right-hand figure display. """
        # Embed figure within widget to create border
        self.figureRegion = QWidget()
        self.figureRegion.setStyleSheet("border: 1px solid darkgray")
                
        self.displaySubLayout = QVBoxLayout(self.figureRegion)
        self.displaySubLayout.setContentsMargins(1,1,1,1)

        # Create display plot region
        self.fig_view = QWebEngineView(self.figureRegion)
        start_html = '<html><head><meta charset="utf-8" />'
        start_html += '<body>'
        start_html += '<p style="font-family: sans-serif">No data provided yet. Upload data in Data menu option.</p>'
        start_html += '</body></html>'
        self.fig_view.setHtml(start_html)
        self.fig_view.raise_()
        
        # Add figure to sub layout
        self.displaySubLayout.addWidget(self.fig_view)    
    
    def _createPageNav(self):
        """ Creates the navigation bar beneath the plot which
            enables the user to navigate between pages of the plot """
        self.pageNavLayout = QHBoxLayout()
        self.pageNavLayout.addStretch()
        
        # Add arrows and icon
        self.left_button = QToolButton()
        self.left_button.setArrowType(QtCore.Qt.LeftArrow)
        
        self.illixr_img = QLabel()
        pix_img = QtGui.QPixmap("illixr_icon.png").scaled(36, 36, QtCore.Qt.KeepAspectRatio)
        self.illixr_img.setPixmap(pix_img)
        
        self.right_button = QToolButton()
        self.right_button.setArrowType(QtCore.Qt.RightArrow)
        # self.right_button.clicked.connect(RIGHT FUNCTION) <-- which will actually occur in Controller, view simply must call a 'right_clicked' method
            
        self.pageNavLayout.addWidget(self.left_button)
        self.pageNavLayout.addWidget(self.illixr_img)
        self.pageNavLayout.addWidget(self.right_button)
        self.pageNavLayout.addStretch()
        
        self.generalLayout.addLayout(self.pageNavLayout, 10, 0, 1, 23)

    # END METHODS FOR INITIALIZING GUI
	
class VisualizerGUIUploadDialog(QDialog):
    """ Part of ILLIXR Visualizer's View. 
        A helper class defining the data upload menu. """
    def __init__():
        super().__init__()
        
        self.setWindowTitle("Upload Data")
        
        self.layout = QVBoxLayout()
        instructions = QLabel("Please select the database containing the plugin names. Then select the corresponding switchboard and/or threadloop databases.")
        self.layout.addWidget(instructions)
        
        

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
        
        
        
