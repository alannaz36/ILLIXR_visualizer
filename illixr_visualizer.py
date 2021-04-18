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

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QListWidget, QAbstractItemView
from PyQt5.QtWidgets import QToolButton, QPushButton, QLineEdit
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
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
        
        self.actionLoad = QtWidgets.QAction(self)
        #self.actionUpload.setObjectName("actionUpload")
        self.actionLoad.setText("Load Data")
        self.actionLoad.setShortcut("Ctrl+L")
        self.actionLoad.triggered.connect(self._load)
        
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuData.addAction(self.actionLoad)
        
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
        self.strList = ['No plugin names provided yet.', 'Load through Data menu option.']
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
        start_html += '<p style="font-family: sans-serif">No data provided yet. Load data in Data menu option.</p>'
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
    
    def _load(self):
        # Launches VisualizerGUILoadDialog
        loadGUI = VisualizerGUILoadDialog()
        if loadGUI.exec_():
            print("Success!")
        else:
            print("Cancel!")
        
        # vvv Potentially in other method triggered by VisualizerGUILoadDialog
        # Retrieves paths from VisualizerGUILoadDialog potentially passed via dict
        # Passes paths to Controller
	
class VisualizerGUILoadDialog(QDialog):
    """ Part of ILLIXR Visualizer's View. 
        A helper class defining the data upload menu. """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Load Data")
        w = 500
        h = int(w*2/5)
        self.setFixedSize(w, h)
        self.move(400, 200)
        
        self.layout = QGridLayout()
        instructions = QLabel("Please select the database containing the plugin names. Then select the corresponding switchboard and/or threadloop databases.")
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions, 0, 0, 1, 3)

        pluginLabel = QLabel("Plugin Database:")
        self.pluginDisplay = QLineEdit()
        self.pluginDisplay.setReadOnly(True)
        self.pluginBrowseButton = QPushButton("Browse")
        self.pluginBrowseButton.clicked.connect(lambda: self._browse("Plugin"))
        
        switchboardLabel = QLabel("Switchboard Database:")
        self.switchboardDisplay = QLineEdit()
        self.switchboardDisplay.setReadOnly(True)
        self.switchboardBrowseButton = QPushButton("Browse")
        self.switchboardBrowseButton.clicked.connect(lambda: self._browse("Switchboard"))
        
        threadloopLabel = QLabel("Threadloop Database:")
        self.threadloopDisplay = QLineEdit()
        self.threadloopDisplay.setReadOnly(True)
        self.threadloopBrowseButton = QPushButton("Browse")
        self.threadloopBrowseButton.clicked.connect(lambda: self._browse("Threadloop"))
        
        self.layout.addWidget(pluginLabel, 2, 0)
        self.layout.addWidget(self.pluginDisplay, 2, 1)
        self.layout.addWidget(self.pluginBrowseButton, 2, 2)
        self.layout.addWidget(switchboardLabel, 3, 0)
        self.layout.addWidget(self.switchboardDisplay, 3, 1)
        self.layout.addWidget(self.switchboardBrowseButton, 3, 2)
        self.layout.addWidget(threadloopLabel, 4, 0) 
        self.layout.addWidget(self.threadloopDisplay, 4, 1)
        self.layout.addWidget(self.threadloopBrowseButton, 4, 2)
        
        subLayout = QVBoxLayout()
        subLayout.addSpacing(5)
        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        #cancelButton = 
        subLayout.addWidget(buttons, alignment=QtCore.Qt.AlignRight)
        self.layout.addLayout(subLayout, 5, 0, 1, 3)
        
        self.setLayout(self.layout)

    def _browse(self, name):
        """ Launches QFileDialog, updates paths and display """ 
        filename, _ = QFileDialog.getOpenFileName(self, "Open " + name + " Database", QtCore.QDir.currentPath(), "Database files (*.sqlite *.sql *.db)")
        if filename:
            # Set database path and display filename in QLineEdit
            if name == "Plugin":
                self.pluginDBPath = filename
                self.pluginDisplay.setText(filename)
            elif name == "Switchboard":
                self.switchboardDBPath = filename
                self.switchboardDisplay.setText(filename)
            elif name == "Threadloop":
                self.threadloopDBPath = filename
                self.threadloopDisplay.setText(filename)


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
        
        
        
