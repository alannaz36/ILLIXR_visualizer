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
from PyQt5 import QtCore, QtGui

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
        self.resize(1000, 600)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("illixr_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
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
        
        
        
