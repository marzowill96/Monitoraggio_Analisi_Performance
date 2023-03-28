import pandas as pd
import numpy as np
import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
#from PIL import Image




#%%

app = dash.Dash(__name__)

server = app.server

# Define app layout
app.layout = html.Div([
    
    html.Div([
        
        html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-style': 'italic', 'font-weight': 'normal','font-size': '18px', 'margin-left': '0px','margin-bottom':'20px'})

    ],style={'margin': 'auto','marginLeft': '200px','display': 'flex', 'align-items': 'flex-end'})
    
])


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
    


