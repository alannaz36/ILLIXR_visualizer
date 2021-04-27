# Filename: illixr_visualizer.py
""" ILLIXR Visualizer is a visualization interface for analyzing ILLIXR data
    logged in databases. It is a desktop application following an MVC
    design pattern, serving as a modular addition to the ILLIXR project.
    It is built using Python, PyQt5, and Plotly. """

from math import ceil
import pandas as pd
import sqlite3

import plotly.offline as po
import plotly.graph_objs as go
import plotly.express as px

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QListWidget, QAbstractItemView
from PyQt5.QtWidgets import QToolButton, QPushButton, QLineEdit
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtGui, QtWidgets

import sys
import warnings
from pandas.core.common import SettingWithCopyWarning

__author__ = 'Alanna Zoscak'
        
class VisualizerGUILoadDialog(QDialog):
    """ Part of ILLIXR Visualizer's View. 
        A helper class defining the data upload menu. """
    def __init__(self):
        super().__init__()
        
        # Database path fields
        self.pluginDBPath = None
        self.switchboardDBPath = None
        self.threadloopDBPath = None
        self.tempPathDict = {} # Store paths until OK is clicked & paths validated
        
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
        buttons.button(QDialogButtonBox.Cancel).clicked.connect(self._cancel)
        buttons.button(QDialogButtonBox.Ok).clicked.connect(self._load)
        subLayout.addWidget(buttons, alignment=QtCore.Qt.AlignRight)
        self.layout.addLayout(subLayout, 5, 0, 1, 3)
        
        self.setLayout(self.layout)

    def _browse(self, name):
        """ Launches QFileDialog, updates paths and display """ 
        filename, _ = QFileDialog.getOpenFileName(self, "Open " + name + " Database", QtCore.QDir.currentPath(), "Database files (*.sqlite *.sql *.db)")
        if filename:
            # Set database path and display filename in QLineEdit
            if name == "Plugin":
                self.tempPathDict[name] = filename
                self.pluginDisplay.setText(filename)
            elif name == "Switchboard":
                self.tempPathDict[name] = filename
                self.switchboardDisplay.setText(filename)
            elif name == "Threadloop":
                self.tempPathDict[name] = filename
                self.threadloopDisplay.setText(filename)

    def _load(self):
        """ Stores the database paths after validating that
            necessary information has been provided """
        if self._validate():
            self.pluginDBPath = self.tempPathDict["Plugin"]
            if "Switchboard" in self.tempPathDict:
                self.switchboardDBPath = self.tempPathDict["Switchboard"]
            else:
                self.switchboardDBPath = None
            if "Threadloop" in self.tempPathDict:
                self.threadloopDBPath = self.tempPathDict["Threadloop"]
            else:
                self.threadloopDBPath = None
            self.tempPathDict= {}
            self.accept()
        else:
            # Display message with instructions for loading
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText("Additional information needed - Plugin names database and at least one log database (Switchboard or Threadloop) must be provided.")
            error_msg.setWindowTitle("Cannot Load")
            error_msg.setStandardButtons(QMessageBox.Ok)
            error_msg.exec_()

    def _cancel(self):
        """ Cancels load """
        self.tempPathDict = {}
        self.reject()

    def _validate(self):
        """ Validates that necessary databases have been provided """
        if "Plugin" in self.tempPathDict:
            return "Switchboard" in self.tempPathDict or "Threadloop" in self.tempPathDict
        return False

    def getDatabasePaths(self):
        """ Provides the database paths in a tuple where first is the plugin 
            database path and the second is a dictionary of the data 
            (switchboard and threadloop) databases paths. If plugin database
            path is not found, namePath is None. If data paths are not found,
            dataPaths is an empty dictionary. """
        namePath = None
        dataPaths = {}
        if self.pluginDBPath is not None:
            namePath = self.pluginDBPath
            if self.switchboardDBPath is not None:
                dataPaths["switchboard"] = self.switchboardDBPath
            if self.threadloopDBPath is not None:
                dataPaths["threadloop"] = self.threadloopDBPath
        return namePath, dataPaths
                

class VisualizerGUI(QMainWindow):
    """ ILLIXR_Visualizer's View (GUI).
        Defines the main window.
        Displays plots and interfaces with user. """
    # Define signals for signalling Controller
    loadSignal = QtCore.pyqtSignal()
    reorderSignal = QtCore.pyqtSignal()
    leftSignal = QtCore.pyqtSignal()
    rightSignal = QtCore.pyqtSignal()
        
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
        
        self.has_figure = False
        
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
        self.menuFile.setTitle("File")
        
        self.menuData = QtWidgets.QMenu(self.menubar)
        self.menuData.setTitle("Data")
        
        self.menuPlotSettings = QtWidgets.QMenu(self.menubar)
        self.menuPlotSettings.setTitle("Plot Settings")
        
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setTitle("Help")
        
        self.setMenuBar(self.menubar)
        
        # Add actions - sub categories of menu items
        self.actionNew = QtWidgets.QAction(self)
        self.actionNew.setText("New")
        
        self.actionSave = QtWidgets.QAction(self)
        self.actionSave.setText("Save")
        
        self.actionLoad = QtWidgets.QAction(self)
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
        
        # Orderable plugin list
        self.pluginList = QListWidget() 
        self.strList = ['No plugin names provided yet.', 'Load through Data menu option.']
        self.pluginList.addItems(self.strList);
        self.pluginList.setDragDropMode(QAbstractItemView.InternalMove)
        self.pluginListLayout.addWidget(self.pluginList)
    
        # Button to reorder plot
        reorderButton = QPushButton('Reorder Plot')
        reorderButton.clicked.connect(self._reorder_plot)
        self.pluginListLayout.addWidget(reorderButton)   	
    
    def _createFigureRegion(self):
        """ Creates the right-hand figure display. """
        # Embed figure within widget to create border
        self.figureRegion = QWidget()
        self.figureRegion.setStyleSheet("border: 1px solid darkgray")
                
        self.displaySubLayout = QVBoxLayout(self.figureRegion)
        self.displaySubLayout.setContentsMargins(1,1,1,1)

        # Create display plot region
        self.fig_view = QWebEngineView(self.figureRegion)
        self.set_display(text='No data provided yet. Load data in Data menu option.')
        
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
        self.left_button.clicked.connect(self._page_left)
        
        self.illixr_img = QLabel()
        pix_img = QtGui.QPixmap("illixr_icon.png").scaled(36, 36, QtCore.Qt.KeepAspectRatio)
        self.illixr_img.setPixmap(pix_img)
        
        self.right_button = QToolButton()
        self.right_button.setArrowType(QtCore.Qt.RightArrow)
        self.right_button.clicked.connect(self._page_right)
        
        self.pageNavLayout.addWidget(self.left_button)
        self.pageNavLayout.addWidget(self.illixr_img)
        self.pageNavLayout.addWidget(self.right_button)
        self.pageNavLayout.addStretch()
        
        self.generalLayout.addLayout(self.pageNavLayout, 10, 0, 1, 23)

    # END METHODS FOR INITIALIZING GUI
    
    def _load(self):
        """ Signals Controller to handle load. """
        self.loadSignal.emit()
       
    def set_display(self, figure=None, text=None):
        """ Embeds given figure in the display. """
        if figure is not None and text is not None:
            raise Exception("Only figure or text may be supplied.")
        
        html = '<html><head><meta charset="utf-8" />'
        if figure is not None:
            self.has_figure = True
            html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
            html += '<body>'
            # 'div' is specified for embedding the graph
            html += po.plot(figure, include_plotlyjs=False, output_type='div')
        elif text is not None and isinstance(text, str):
            html += '<body>'
            html += '<p style="font-family: sans-serif">' + text + '</p>'
        else:
            raise Exception("figure or text must be supplied.")
        html += '</body></html>'
          
        self.fig_view.setHtml(html)
        self.fig_view.raise_()
        
    def _page_left(self):
        """ Signals Controller to page left, updating the figure. """
        if self.has_figure is True:
            self.leftSignal.emit()
        
    def _page_right(self):
        """ Signals Controller to page right, updating the figure. """
        if self.has_figure is True:
            self.rightSignal.emit()
                
    def change_pagenum(self, pagenum : str):
        """ Changes the page number that is displayed in the page navigation bar. """
        self.illixr_img.clear
        self.illixr_img.setText(pagenum)
        
    def _reorder_plot(self):
        """ Signals Controller to reorder the plugins in the plot. """
        if self.has_figure is True:
            # Get the plugin names in order from list
            newPluginOrder = []
            for i in range(self.pluginList.count()):
                newPluginOrder.append(self.pluginList.item(i).text())
            self.strList = newPluginOrder
            self.reorderSignal.emit()
            
    def get_plugin_list(self):
        """ Returns the plugin list as it was last set,
            either by loading new data or clicking the 
            Reorder Plot button. """
        return self.strList
            
    def set_plugin_list(self, plugins : list):
        """ Sets the list of the plugins. """
        self.pluginList.clear()
        
        self.strList = plugins
        self.pluginList.addItems(self.strList)

class VisualizerController():
    """ ILLIXR Visualizer's Controller.
        Interfaces between the View and Model. """
    def __init__(self, view):
        """ Controller initializer. """
        self.view = view
        self.view.loadSignal.connect(self._load)
        self.view.leftSignal.connect(self._page_left)
        self.view.rightSignal.connect(self._page_right)
        self.view.reorderSignal.connect(self._reorder_fig)
        
        # Default plot settings
        self.pageSz = 1000000 # Number of nanoseconds to include per page
        self.currentPage = 0  # Starts on the first page of data
        self.totalPages  = 0  # The minimum number of pages needed to graph all the data
        
        # Configure plotly express with custom dataframe processor method 
        # to avoid plotly express' auto-use of datetime objects
        px._core.process_dataframe_timeline = integer_process_dataframe_timeline
        
        self.pluginTable = 'plugin_name' # Name of table containing plugin names 
        self.pluginID = 'plugin_id' # Name of plugin identifier attribute, shared over databases
        self.pluginName = 'plugin_name' # Name of column holding plugin names
        self.pluginOrder = {self.pluginName : []} # Dictionary specifying plugin ordering
        
        # Define SQL to extract plugin IDs and plugin names from table
        self.nameSQL = ('SELECT ' +
            self.pluginID + ', ' +
            self.pluginName +
            ' FROM ' + 
            self.pluginTable
        )
        
        # Data table names
        self.switchboardTable = 'switchboard_callback' # Name of table containing switchboard data
        self.threadloopTable  = 'threadloop_iteration' # Name of table containing threadloop data
        
        self.startTime = 'cpu_time_start' # Name of data attribute containing start times
        self.endTime   = 'cpu_time_stop'  # Name of attribute containing end times
        
        # Define base data extraction SQL statement, add data table name on use
        self.dataSQL = ('SELECT ' +
            self.pluginID  + ', ' +
            self.startTime + ', ' +
            self.endTime   +
            ' FROM '
        )
        
        # pandas DataFrames storing logged data
        self.nameDF = None
        self.dataDF = None
    
    def _load(self):
        """ Handles loading of databases. """
        # Launches VisualizerGUILoadDialog
        loadGUI = VisualizerGUILoadDialog()
        if loadGUI.exec_():
            # Successful retrieval of databases
            namePath, dataPaths = loadGUI.getDatabasePaths()
            
            # Load plugin names
            tempNameDF = self._db_to_df(
                dbPath = namePath, 
                sql_stmt = self.nameSQL,
                index_column = self.pluginID,
                contents = "plugin names",
                tableName = self.pluginTable,
                attribs = "'" + self.pluginID + "' and '" + self.pluginName + "'"
            )
            if tempNameDF is None:  # Failed to load, retry
                return self._load()
            
            # Load logged data (switchboard and threadloop)
            tempDataDF = None
            for dataType, dataPath in dataPaths.items():
                tempDF = None
                if dataType == "switchboard":
                    tempDF = self._db_to_df(
                        dbPath = dataPath,
                        sql_stmt = self.dataSQL + self.switchboardTable,
                        contents = "switchboard logs",
                        tableName = self.switchboardTable,
                        attribs = "'" + self.pluginID + "', '" + self.startTime + "' and '" + self.endTime + "'"
                    )
                elif dataType == "threadloop":
                    tempDF = self._db_to_df(
                        dbPath = dataPath,
                        sql_stmt = self.dataSQL + self.threadloopTable,
                        contents = "threadloop logs",
                        tableName = self.threadloopTable,
                        attribs = "'" + self.pluginID + "', '" + self.startTime + "' and '" + self.endTime + "'"
                    )
                if tempDF is None:  # Failed to load, retry
                    return self._load()
                    
                # Append to temporary DataFrame
                if tempDataDF is not None:
                    tempDataDF = tempDataDF.append(tempDF)
                else:
                    tempDataDF = tempDF
             
            # Set class fields
            self.nameDF = tempNameDF
            self.dataDF = tempDataDF
            
            # Replace plugin_id with plugin_name
            self.dataDF = self.dataDF.rename(columns={self.pluginID : self.pluginName}, errors="raise")
            self.dataDF = self.dataDF.replace(to_replace=self.nameDF.to_dict())
            
            # Sort data by startTime
            self.dataDF = self.dataDF.sort_values(by=[self.startTime])
            
            self.pluginOrder[self.pluginName] = self.dataDF[self.pluginName].unique().tolist()
            
            # Tell view the order of the plugins
            self.view.set_plugin_list(self.pluginOrder[self.pluginName])
            
            # Each time databases are loaded, render new figure
            self._create_fig()
            
    
    def _db_to_df(self, dbPath, sql_stmt, contents : str, tableName : str, attribs : str, index_column=None):
        """ Helper function for _load that connects to databases
            and stores data in a pandas DataFrame. """
        # Establish connection to the database
        db_uri = "file:" + dbPath + "?mode=ro"
        connection = sqlite3.connect(db_uri, uri=True)
            
        # Load data from database into pandas DataFrame
        df = None
        try:
            if index_column is not None:
                df = pd.read_sql(sql_stmt, con=connection, index_col=index_column)
            else:
                df = pd.read_sql(sql_stmt, con=connection)
        except:
            # Display error message asking to reload
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            msg = ("Please load a database with " + contents + ". Must have a '" +
                tableName + "' table with attributes " + attribs + "."
            )
            error_msg.setText(msg)
            error_msg.setWindowTitle("Malformed Database")
            error_msg.setStandardButtons(QMessageBox.Ok)
            error_msg.exec_()
        connection.close()
        return df
    
    def _create_fig(self):
        """ Generates figure for display.
            Utilizes plot settings stored in Controller. """
        # Calculate subset of data to display based on plot settings
        # Always acquire settingsLock before dfLock
        # Range of ns to include:
        # [currentPage * pageSz, currentPage * pageSz + pageSz)
        pageStart  = self.currentPage * self.pageSz
        pageEnd    = self.currentPage * self.pageSz + self.pageSz
        maxEndTime = (self.dataDF[self.endTime]).max()
        self.totalPages = ceil((maxEndTime - self.pageSz) / self.pageSz)
            
        subDF = self.dataDF[(self.dataDF[self.startTime] >= pageStart) & (self.dataDF[self.startTime] < pageEnd) |
                            (self.dataDF[self.endTime] >= pageStart) & (self.dataDF[self.endTime] < pageEnd)]
        
        # Suppress warning
        warnings.simplefilter('ignore', SettingWithCopyWarning)
            
        # if any rows have an endTime > pageEnd, replace with endTime
        subDF.loc[subDF[self.endTime] > pageEnd, self.endTime] = pageEnd
        
        # if any rows have a startTime < pageStart, replace with startTime
        subDF.loc[subDF[self.startTime] < pageStart, self.startTime] = pageStart
            
        # Specify order of plot, dependent on plugins that are in this page
        pluginSubset = subDF[self.pluginName].unique().tolist()
        pluginSubsetOrdered = [plugin for plugin in self.pluginOrder[self.pluginName] if plugin in pluginSubset]
        plotOrder = {self.pluginName : pluginSubsetOrdered}
            
        if subDF.empty:
            self.view.set_display(text='No data on this page.')
            self.view.change_pagenum(str(self.currentPage) + ' / ' + str(self.totalPages))
            return
        
        # Generate figure for display
        fig = px.timeline(subDF, 
            x_start = self.startTime,
            x_end = self.endTime, 
            y = self.pluginName, 
            color = self.pluginName, 
            labels = {self.pluginName: 'Plugin Name', self.startTime: 'Start Time (ns)', self.endTime: 'End Time (ns)'},
            category_orders = plotOrder
        ) 
        fig.layout.xaxis.type = 'linear'
        fig.layout.xaxis.title = 'Time (ns)'
        fig.layout.yaxis.title = None
        fig.layout.yaxis.showticklabels = False
        
        # Send figure to View
        self.view.set_display(figure=fig)
        self.view.change_pagenum(str(self.currentPage) + ' / ' + str(self.totalPages))
        
    def _page_left(self):
        """ Pages left, updating current settings and figure. """
        if self.currentPage > 0:
            self.currentPage -= 1
            self._create_fig()
        
    def _page_right(self):
        """ Pages right, updating current settings and figure. """
        if self.currentPage < self.totalPages:
            self.currentPage += 1
            self._create_fig()
            
    def _reorder_fig(self):
        """ Reorders the figure based on the ordering in
            the left Plugins list. """
        newPluginOrder = self.view.get_plugin_list()
        self.pluginOrder[self.pluginName] = newPluginOrder
        self._create_fig()

# This overwrite method was obtained from:
# https://stackoverflow.com/questions/66078893/plotly-express-timeline-for-gantt-chart-with-integer-xaxis
def integer_process_dataframe_timeline(args):
    """
    Overwrite conversion to datetime input for px.timeline()
    """
    # print("Processing x-axis data as an integer rather than a datetime")
    args["is_timeline"] = True
    if args["x_start"] is None or args["x_end"] is None:
        raise ValueError("Both x_start and x_end are required")
    
    x_start = args["data_frame"][args["x_start"]]
    x_end = args["data_frame"][args["x_end"]]
    
    # No columns added to the dataframe, no risk of overwrite
    args["data_frame"][args["x_end"]] = (x_end - x_start)
    args["x"] = args["x_end"]
    del args["x_end"]
    args["base"] = args["x_start"]
    del args["x_start"]
    return args


if __name__ == '__main__':
    illixr_visualizer = QApplication(sys.argv)
    view = VisualizerGUI()
    view.show()
    controller = VisualizerController(view)
    sys.exit(illixr_visualizer.exec_())
    
    
