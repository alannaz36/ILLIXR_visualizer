import plotly.offline as po
import plotly.graph_objs as go

import pandas as pd # data
import sqlite3      # data
import plotly.express as px #<-- must come after pandas
 
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
 

# This overwrite method was obtained from: https://stackoverflow.com/questions/66078893/plotly-express-timeline-for-gantt-chart-with-integer-xaxis
def integer_process_dataframe_timeline(args):
    """
    Overwrite conversion to datetime input for px.timeline()
    """
    print("Processing x-axis data as an integer rather than a datetime")
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
    app = QtWidgets.QApplication(sys.argv)
    
    # Some code for obtaining databases from user
    
    # Read plugin_names from database
    name_connection = sqlite3.connect("metrics/plugin_name.sqlite")
    plugin_name_sql = 'SELECT * FROM plugin_name'
    plugin_name_df = pd.read_sql(plugin_name_sql, con=name_connection, index_col="plugin_id")
    name_connection.close()
    # plugin_id and plugin_name columns
    
    # Read plugin run_time data from database
    #  switchboard_callback.sqlite with table switchboard_callback
    #  threadloop_iteration.sqlite with table threadloop_iteration
    data_connection = sqlite3.connect("metrics/switchboard_callback.sqlite")
    sql = ('SELECT ' +
        'plugin_id, ' +
        'cpu_time_start, ' +
        'cpu_time_stop ' +
        'FROM ' +
        'switchboard_callback'
    )
    df = pd.read_sql(sql, con=data_connection)
    data_connection.close()
    
    # Replace plugin_id with plugin_name
    df = df.rename(columns={'plugin_id': 'plugin_name'}, errors="raise")
    df = df.replace(to_replace=plugin_name_df.to_dict())
    
    # Sort by cpu_time_start   
    df = df.sort_values(by=['cpu_time_start'])
    
    # Specify custom dataframe processor method to avoid plotly express' auto-use of datetime objects
    px._core.process_dataframe_timeline = integer_process_dataframe_timeline
    fig = px.timeline(df.head(n=5), x_start="cpu_time_start", x_end="cpu_time_stop", y="plugin_name", color="plugin_name", labels={'plugin_name': 'Plugin Name', 'cpu_time_start': 'Start Time (ns)', 'cpu_time_stop': 'End Time (ns)'}) 
    fig.layout.xaxis.type = 'linear'
    fig.layout.xaxis.title = 'Time (ns)'
    fig_view = show_qt(fig) 
    
    sys.exit(app.exec_())
