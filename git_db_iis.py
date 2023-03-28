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

url = 'https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/dati.xlsx'
fondi = pd.read_excel(url)
names = fondi.columns[1:]

# associo ISIN a Nome Fondo per tutti i fondi
names_dict = dict(zip(fondi[fondi.columns[1:]].iloc[1], fondi.columns[1:]))

#sistemo dataframe fondi

fondi = fondi.set_index('DEXIA CODE')
fondi.columns = fondi.iloc[1]
fondi = fondi.iloc[2:]
fondi = fondi.apply(pd.to_numeric)

fondi_necessari = ['IE00BYZ2Y955','IE00BYZ2YB75','IE0005380518','IE0032080503','IE00B04KP775','IE00B2NLMT64','IE00B2NLMV86','IE00BCZNHK63','IE0004621052','IE0032082988','IE0030608859']     

base_dati = fondi[fondi_necessari][fondi.index >= '31/12/2019']

weekly = pd.date_range(start=base_dati.index.min(), end=base_dati.index.max(), freq='7D')
base_dati_weekly = pd.DataFrame(index = weekly, columns = base_dati.columns)

for t in base_dati_weekly.index:
    for c in   base_dati_weekly.columns:
        base_dati_weekly[c].loc[t] = base_dati[c].loc[base_dati.index[base_dati.index.get_loc(t, method='ffill')]]

base_dati_weekly = base_dati_weekly.apply(pd.to_numeric) 

df = pd.read_excel('https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/dati.xlsx')

fondi = pd.read_excel(url)
names = fondi.columns[1:]
 
 # associo ISIN a Nome Fondo per tutti i fondi
names_dict = dict(zip(fondi[fondi.columns[1:]].iloc[1], fondi.columns[1:]))
for key, value in names_dict.items():
    names_dict[key] = value.replace('Mediolanum Best Brands', 'MBB') 
    
isin_dict_0 = dict(zip(fondi.columns[1:], fondi[fondi.columns[1:]].iloc[1]))

isin_dict = {}
for key, value in isin_dict_0.items():
    new_key = key.replace('Mediolanum Best Brands', 'MBB')
    new_value = value.replace('Mediolanum Best Brands', 'MBB')
    isin_dict[new_key] = new_value

# Define list of dates for dropdown menu

dates = list(base_dati_weekly.index)
for t in range(len(dates)):
    dates[t] = dt.strftime(dates[t], "%d/%m/%Y")
    
fondi_necessari = ['IE00BYZ2Y955','IE00BYZ2YB75','IE0005380518','IE0032080503','IE00B04KP775','IE00B2NLMT64','IE00B2NLMV86','IE00BCZNHK63','IE0004621052','IE0032082988','IE0030608859']
nomi = [names_dict[key] for key in fondi_necessari]

performance_df = pd.DataFrame(index=[0], columns = ['Performance','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC'])
vol_df = pd.DataFrame(index=[0], columns = ['Volatilità','IIS','PIC','Effetto Strategia'])
maxdd_df = pd.DataFrame(index=[0], columns = ['Max Draw-Down','IIS','PIC','Effetto Strategia'])
step_in_df = pd.DataFrame(index=[0,1,2,3,4], columns=['Step - In', 'Conteggio'])
step_out_df = pd.DataFrame(index=[0], columns=['Step - Out', 'Conteggio']) 


app = dash.Dash(__name__)

server = app.server

# Define app layout
app.layout = html.Div([
    
    html.Div([
        
        html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-style': 'italic', 'font-weight': 'normal','font-size': '18px', 'margin-left': '0px','margin-bottom':'20px'})

    ],style={'margin': 'auto','marginLeft': '200px','display': 'flex', 'align-items': 'flex-end'}),
    
    html.Div([
    dcc.Graph(id='table',
              figure=dict(data=[dict(type='table',
                                     header=dict(values=list(df.columns)),
                                     cells=dict(values=[df[col] for col in df.columns]))
                                 ])
             )
])
])


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
    
