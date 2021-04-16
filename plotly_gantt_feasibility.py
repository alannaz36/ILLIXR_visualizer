import plotly.offline as po
import plotly.graph_objs as go

import numpy # <-- required for figure_factory
import plotly.figure_factory as ff # gantt
import pandas as pd # data
import sqlite3      # data
#import plotly.express as px <-- must come after pandas
 
# pip install numpy
# pip install pandas
# pip install PyQtWebEngine <-- got Could not find QtWebEngineProcess --> pip3 install PyQtWebEngine
# pip install plotly

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets
import sys
 
 
def show_qt(fig): # <-- treated as another button
    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
    raw_html += '<body>'
    raw_html += po.plot(fig, include_plotlyjs=False, output_type='div') # 'div'for embedding graphs in an HTML file with other graphs or HTML markup
    raw_html += '</body></html>'
 
    fig_view = QWebEngineView()
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
    fig_view.setHtml(raw_html)
    fig_view.show() # <-- only show in window
    fig_view.raise_()
    return fig_view
 
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Some code for obtaining databases from user
    
    # Read plugin_names from database
    name_connection = sqlite3.connect("metrics/plugin_name.sqlite")
    plugin_name_sql = 'SELECT * FROM plugin_name'
    plugin_name_df = pd.read_sql(plugin_name_sql, con=name_connection, index_col="plugin_id")
    # plugin_id and plugin_name columns
    
    # Read plugin run_time data from database
    connection = sqlite3.connect("metrics/switchboard_callback.sqlite")
    sql = ('SELECT ' +
        'plugin_id, ' +
        'cpu_time_start, ' +
        'cpu_time_stop ' +
        'FROM ' +
        'switchboard_callback'
    )
    df = pd.read_sql(sql, con=connection)
    
    # Replace plugin_id with plugin_name
    df = df.rename(columns={'plugin_id': 'plugin_name'}, errors="raise")
    df = df.replace(to_replace=plugin_name_df.to_dict())
    
    # SORT BY cpu_time_start    
    df = df.rename(columns={'plugin_name': 'Task', 'cpu_time_start': 'Start', 'cpu_time_stop': 'Finish'}, errors="raise")
    
    fig = ff.create_gantt(df.head(n=50), title=None, group_tasks=True, index_col='Task', show_colorbar=True)
    fig.layout.xaxis.rangeselector = None
    fig_view = show_qt(fig) 
    
    sys.exit(app.exec_())
