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
isin_dict = dict(zip(fondi.columns[1:], fondi[fondi.columns[1:]].iloc[1]))
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


# Define list of dates for dropdown menu

dates = list(base_dati_weekly.index)
for t in range(len(dates)):
    dates[t] = dt.strftime(dates[t], "%d/%m/%Y")
    
nomi = [names_dict[key] for key in fondi_necessari]

performance_df = pd.DataFrame(index=[0], columns = ['Performance','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC'])
vol_df = pd.DataFrame(index=[0], columns = ['Volatilità','IIS','PIC','Effetto Strategia'])
maxdd_df = pd.DataFrame(index=[0], columns = ['Max Draw-Down','IIS','PIC','Effetto Strategia'])
step_in_df = pd.DataFrame(index=[0,1,2,3,4], columns=['Step - In', 'Conteggio'])
step_out_df = pd.DataFrame(index=[0], columns=['Step - Out', 'Conteggio']) 



app = dash.Dash(__name__)

server = app.server

# Define app layout
app = dash.Dash(__name__)

server = app.server


# Define app layout
app.layout = html.Div([
    
    html.Div([
        
        html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-style': 'italic', 'font-weight': 'normal','font-size': '18px', 'margin-left': '0px','margin-bottom':'20px'})
        # html.Div([
        #     html.H1('Intelligent Investment Strategy', style={'color': 'blue'}),
        #     html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-weight': 'normal', 'font-size': '18px', 'margin-left': '10px'})
        # ], style={'display': 'flex', 'align-items': 'center'})
    ],style={'margin': 'auto','marginLeft': '200px','display': 'flex', 'align-items': 'flex-end'}),
    
    html.Table([
        html.Tr([
            html.Th('Data Primo Versamento (Fine Mese)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Importo (Min. €30.000)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Durata', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Importo Rata Totale', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
        ], style={'border': '1px solid black'}),
        
        html.Tr([
            html.Td(dcc.Dropdown(
                id='start_date',
                options=[{'label': date, 'value': date} for date in dates],
                value=dates[0]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Input(
                id='importo',
                type='number',
                min=30000,style={'position': 'sticky', 'top': '0'} ), style={'text-align': 'center','border': '1px solid black'}),
           html.Td(dcc.RadioItems(
               id='durata_months',
               options=[{'label': i, 'value': i} for i in [36, 48, 60]],
               value=36,
               style={'display': 'inline-block', 'margin':'0px'} ), style={'text-align': 'center','border': '1px solid black'}),
           html.Td(html.Div(id='installment-amount', style={'display': 'inline-block'}), style={'text-align': 'center','border': '1px solid black'})
           
        ],style={'border': '1px solid black'}),
        # ],style={'width': '60%', 'table-layout': 'adaptive','marginTop': '50px', 'marginLeft': '100px','border': '1px solid black'}),

        html.Tr([
            html.Th('Comparto', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Ripartizione (0% - 100%)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Soglia Automatic Step-Out', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'}),
            html.Th('Importo Rata', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white'})            
        ], style={'border': '1px solid black'}),
        # table rows
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo1', options=[{'label': fondo, 'value': fondo} for fondo in nomi]), style={'text-align': 'center','border': '1px solid black'}),
            
            html.Td(dcc.Input(id='input1', type='number',min=0), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Dropdown(id='step_out1', options=[
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(id='rata1', style={'text-align': 'center','border': '1px solid black'})

        ],style={'border': '1px solid black'}),
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo2', options=[{'label': fondo, 'value': fondo} for fondo in nomi]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Input(id='input2', type='number',min=0), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Dropdown(id='step_out2', options=[
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(id='rata2', style={'text-align': 'center','border': '1px solid black'})

        ]),
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo3', options=[{'label': fondo, 'value': fondo} for fondo in nomi]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Input(id='input3', type='number',min=0), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(dcc.Dropdown(id='step_out3', options=[
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}]), style={'text-align': 'center','border': '1px solid black'}),
            html.Td(id='rata3', style={'text-align': 'center','border': '1px solid black'})

        ],style={'border': '1px solid black'}),
    ],style={'width': '60%', 'table-layout': 'adaptive','marginTop': '50px', 'marginLeft': '50px','border': '1px solid black'}),
     
    html.Div(id='output',style={'margin': 'auto','marginLeft': '50px'}),
    
    
    html.Div(children=[
    dcc.Graph(id='grafico_iis', style={'height': '70%', 'width': '100%', 'display': 'block', 'max-width':'2000px'}, config={'displayModeBar': False}),   
    dcc.Graph(id='istogramma', style={'height': '30%', 'width': '100%', 'display': 'block', 'margin-top': '0px','max-width':'2000px'}, config={'displayModeBar': False})
    ], style={'height': '1000px'}),           
    
    html.Div([
        html.Div([                  
        dash_table.DataTable(
            id='performance',
            columns=[{"name": i, "id": i} for i in performance_df],
            data=performance_df.to_dict('records'),
            editable=False,
            style_table={
                'maxWidth': '10%',
                'margin': 'auto',
                'marginLeft': '20px',
            },
            style_header={
                'backgroundColor': 'royalblue',
                'color': 'white',
                'fontWeight': 'bold',
                'text-align': 'center'
            },
            style_cell={'textAlign': 'center', 'fontSize':'11px'}
        )],style={"display": "flex", 'text-align': 'center'}),

        html.Div([                          
        dash_table.DataTable(
            id='volatilita',
            columns=[{"name": i, "id": i} for i in vol_df],
            data=None,
            editable=False,
            style_table={
                'maxWidth': '10%',
                'margin': 'auto',
                'marginLeft': '20px',
            },
            style_header={
                'backgroundColor': 'royalblue',
                'color': 'white',
                'fontWeight': 'bold',
                'text-align': 'center'
            },
            style_cell={'textAlign': 'center', 'fontSize':'11px'}
        )],style={"display": "flex", 'text-align': 'center'}),
        
        html.Div([                       
        dash_table.DataTable(
            id='max_dd',
            columns=[{"name": i, "id": i} for i in maxdd_df],
            data=None,
            editable=False,
            style_table={
                'maxWidth': '10%',
                'margin': 'auto',
                'marginLeft': '20px',
            },
            style_header={
                'backgroundColor': 'royalblue',
                'color': 'white',
                'fontWeight': 'bold',
                'text-align': 'center'
            },
            style_cell={'textAlign': 'center', 'fontSize':'11px'}
        ),
    ],style={"display": "flex", 'text-align': 'center'})
        
    ],style={"display": "flex", 'text-align': 'center', 'max-width':'1600px','width':'100%','marginTop':'50px'}
),

html.Div(
    [
        html.Div(
            [
                html.Div([
                    
                    dash_table.DataTable(
                        id='step_in',
                        columns=[{"name": i, "id": i} for i in step_in_df],
                        data=None,
                        editable=False,
                        style_table={
                            'maxWidth': '10%',
                            'margin': 'auto',
                            'marginLeft': '20px',
                            'marginTop': '20px'  # add margin to the top
                        },
                        style_header={
                            'backgroundColor': 'royalblue',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'text-align': 'center'
                        },
                        style_cell={'textAlign': 'center', 'fontSize':'11px'}
                    )],
                    className="six columns",
                    style={"display": "inline-block",'text-align': 'center'}
                ),
                html.Div(
                    dash_table.DataTable(
                        id='step_out',
                        columns=[{"name": i, "id": i} for i in step_out_df],
                        data=None,
                        editable=False,
                        style_table={
                            'maxWidth': '10%',
                            'margin': 'auto',
                            'marginLeft': '20px',
                            'marginTop': '20px',
                            
                            # add margin to the top
                        },
                        style_header={
                            'backgroundColor': 'royalblue',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'text-align': 'center'
                        },
                        style_cell={'textAlign': 'center', 'fontSize':'11px'}
                    ),
                    className="six columns",
                    style={"display": "inline-block",'text-align': 'center'}
                ),
            ],
            style={"display": "flex", 'text-align': 'center'}
        )
    ]
),
    
     
     html.Div(children=[html.H1("Prezzo vs Prezzo Medio di Carico vs Prezzo Medio", style={"font-size": "16px","text-align": "center"}),
                        dcc.Graph(id='pmc1', style={'width': '33%','height':'80%', 'display': 'inline-block'},config={'displayModeBar': False}),
                        dcc.Graph(id='pmc2', style={'width': '33%', 'height':'80%','display': 'inline-block'},config={'displayModeBar': False}),
                        dcc.Graph(id='pmc3', style={'width': '33%', 'height':'80%','display': 'inline-block'},config={'displayModeBar': False})
                        ], style={'height': '300px', 'max-width':'2000px'})
    
     ])

# Define callbacks
@app.callback(
    Output('amount-error', 'children'),
    Input('importo', 'value')
)
def check_amount(amount):
    if amount is not None and amount < 30000:
        return 'Minimo investito deve essere almeno €30.000'

@app.callback(
    Output('installment-amount', 'children'),
    Input('importo', 'value'),
    Input('durata_months', 'value')
)
def calculate_installment_amount(amount, duration):
    if amount is not None and duration is not None:
        installment_amount = round(amount / duration, 2)
        return f'€{installment_amount}'

@app.callback(
    Output('output', 'children'),
    [Input('durata_months', 'value'), Input('installment-amount', 'children'), Input('input1', 'value'), Input('input2', 'value'), Input('input3', 'value')]
)
def update_output(durata_months,installment_amount,input1, input2, input3):
    
    total = input1 + input2 + input3
    rata1 = round(float(installment_amount.strip('€')) * float(input1) / 100, 2)
    rata2 = round(float(installment_amount.strip('€')) * float(input2) / 100, 2)
    rata3 = round(float(installment_amount.strip('€')) * float(input3) / 100, 2)
    
    if (input1<0) or (input2<0) or (input3<0):
        return html.Div(f'Non sono ammessi valori di ripartizione negativi.', style={'color': 'red'})
    
    elif total != 100:
        return html.Div(f'Il totale della Ripartizione deve essere 100%. Totale: {total}.', style={'color': 'red'})

    elif total != 100:
        return html.Div(f'Il totale della Ripartizione deve essere 100%. Totale: {total}.', style={'color': 'red'})

    elif (rata1*durata_months <15000) or (rata2*durata_months <15000) or (rata3*durata_months <15000):
        return html.Div(f'La ripartizione non permette di rispettare i minimi contrattuali', style={'color': 'red'})

    else:
        return html.Div(f'Totale = 100.', style={'color': 'green'})


@app.callback(
    [Output('rata1', 'children'), Output('rata2', 'children'), Output('rata3', 'children')],
    [Input('installment-amount', 'children'), Input('input1', 'value'), Input('input2', 'value'), Input('input3', 'value')]
)
def calculate_rata(installment_amount, input1, input2, input3):
    if installment_amount is not None:

        rata1 = round(float(installment_amount.strip('€')) * float(input1) / 100, 2)
        rata2 = round(float(installment_amount.strip('€')) * float(input2) / 100, 2)
        rata3 = round(float(installment_amount.strip('€')) * float(input3) / 100, 2)
        return f'€{rata1}', f'€{rata2}', f'€{rata3}'
    else:
        return None, None, None
    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
    




    



