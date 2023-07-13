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
from dash import ctx
import dash_bootstrap_components as dbc
from PIL import Image
from io import BytesIO
import requests

    
#%% # Function to convert a numeric value to a percentage string
def to_percent(x):
    if isinstance(x, (int, float)):
        return '{:.2%}'.format(x)
    else:
        return x
    
    
url = 'https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/'

response = requests.get(url+'immagine_iis.png', verify=False)
pil_image = Image.open(BytesIO(response.content))

fondi = pd.read_excel(url+'dati.xlsx')
names = fondi.columns[1:]

# associo ISIN a Nome Fondo per tutti i fondi
names_dict = dict(zip(fondi[fondi.columns[1:]].iloc[1], fondi.columns[1:]))
for key, value in names_dict.items():
    if 'Mediolanum Best Brands' in value:
        names_dict[key] = value.replace('Mediolanum Best Brands', 'MBB') 
    else:
        names_dict[key] = value
names_dict['-'] = '-'

isin_dict_0 = dict(zip(fondi.columns[1:], fondi[fondi.columns[1:]].iloc[1]))
isin_dict = {}
for key, value in isin_dict_0.items():
    if 'Mediolanum Best Brands' in key:
        new_key = key.replace('Mediolanum Best Brands', 'MBB')
    else:
        new_key = key
    if 'Mediolanum Best Brands' in value:
        new_value = value.replace('Mediolanum Best Brands', 'MBB')
    else:
        new_value = value
    isin_dict[new_key] = new_value

isin_dict['-'] = '-'

#sistemo dataframe fondi

fondi = fondi.set_index('DEXIA CODE')
fondi.columns = fondi.iloc[1]
fondi = fondi.iloc[2:]
fondi = fondi.apply(pd.to_numeric)

fondi_necessari = ['IE00BYZ2Y955','IE00BYZ2YB75','IE0005380518','IE0032080503','IE00B04KP775','IE00B2NLMT64','IE00B2NLMV86','IE00BCZNHK63','IE0004621052','IE0032082988','IE0030608859']     

base_dati = fondi[fondi_necessari][fondi.index >= '31/12/2019']

weekly = []
weekly.append(base_dati.index[0])

while weekly[-1] < base_dati.index[-1]:
    t = weekly.index(weekly[-1])    
    weekly.append(weekly[-1]+relativedelta(days=7))
    weekly.append(weekly[-1]+relativedelta(days=7))
    weekly.append(weekly[-1]+relativedelta(days=7))    
    weekly.append((weekly[t+3]+relativedelta(months=1)).replace(day=1) + relativedelta(days=-1))  
    
base_dati_weekly = pd.DataFrame(index = weekly, columns = base_dati.columns)

for t in base_dati_weekly.index:
    for c in   base_dati_weekly.columns:
        base_dati_weekly[c].loc[t] = base_dati[c].loc[base_dati.index[base_dati.index.get_loc(t, method='ffill')]]

base_dati_weekly = base_dati_weekly.apply(pd.to_numeric) 
#base_dati_weekly = base_dati_weekly[base_dati_weekly.index <= '21/03/2023'] 


# Define list of dates for dropdown menu
dates = list(base_dati_weekly.index)
for t in range(len(dates)):
    dates[t] = dt.strftime(dates[t], "%d/%m/%Y")

fondi_necessari = ['-','IE00BYZ2Y955','IE00BYZ2YB75','IE0005380518','IE0032080503','IE00B04KP775','IE00B2NLMT64','IE00B2NLMV86','IE00BCZNHK63','IE0004621052','IE0032082988','IE0030608859']         
nomi = [names_dict[key] for key in fondi_necessari]

performance_df = pd.DataFrame(index=[0], columns = ['Performance','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC'])
vol_df = pd.DataFrame(index=[0], columns = ['Volatilità','IIS','PIC','Effetto Strategia'])
maxdd_df = pd.DataFrame(index=[0], columns = ['Max Draw-Down','IIS','PIC','Effetto Strategia'])
step_in_df = pd.DataFrame(index=[0,1,2,3,4], columns=['Step - In', 'Conteggio'])
step_out_df = pd.DataFrame(index=[0], columns=['Step - Out', 'Conteggio']) 
stats_df = pd.DataFrame(index = performance_df.index, columns= [[' ','Performance','Performance','Performance','Performance','Performance','Performance','Performance','Performance','Volatilità','Volatilità','Volatilità','Max Draw-Down','Max Draw-Down','Max Draw-Down'],['Nome','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC','IIS','PIC','Effetto Strategia','IIS','PIC','Effetto Strategia']])

#%%

app = dash.Dash(__name__, 
                title ='Tool IIS')
server = app.server

# Add the following line to set the favicon

#use href="/assets/favicon.ico" to get favicon from local folder (named 'assets' and subdirectory) instead of github

app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>           
            <link rel="shortcut icon" href="https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/favicon.ico"  type="image/x-icon">
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
'''

# Define app layout
app.layout = html.Div([
    
    html.Div([
        html.Img(src=pil_image, style={'width': '77.39vh', 'height': '15.47vh'}),
        html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-style': 'italic', 'font-weight': 'normal','font-size': '1.85vh', 'margin-left': '0px','margin-bottom':'20px'})
        # html.Div([
        #     html.H1('Intelligent Investment Strategy', style={'color': 'blue'}),
        #     html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', style={'color': 'black', 'font-weight': 'normal', 'font-size': '18px', 'margin-left': '10px'})
        # ], style={'display': 'flex', 'align-items': 'center'})
    ],style={'margin': 'auto', 'justify-content': 'center','display': 'flex', 'align-items': 'flex-end'}),
    
    html.Div([
    html.Table([
        html.Tr([
            html.Th('Data Primo Versamento (Fine Mese)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white', 'fontSize':'0.75vw'}),
            html.Th('Importo (Min. €30.000)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white', 'fontSize':'0.75vw'}),
            html.Th('Durata', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white', 'fontSize':'0.75vw'}),
            html.Th('Importo Rata Totale', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white', 'fontSize':'0.75vw'}),
        ], style={'border': '1px solid black'}),
        
        html.Tr([
            html.Td(dcc.Dropdown(
                id='start_date',
                options=[{'label': date, 'value': date} for date in dates],
                value=dates[0]), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
            html.Td(dcc.Input(
                id='importo',
                type='number',
                min=30000,style={'position': 'sticky', 'top': '0'} ), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
           html.Td(dcc.RadioItems(
               id='durata_months',
               options=[{'label': i, 'value': i} for i in [36, 48, 60]],
               value=36,
               labelStyle={'display': 'inline-block', 'margin-right': '10px'},
               style={'display': 'inline-block', 'margin':'0px'} ), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
           html.Td(html.Div(id='installment-amount', style={'display': 'inline-block'}), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'})
           
        ],style={'border': '1px solid black'}),
        # ],style={'width': '60%', 'table-layout': 'adaptive','marginTop': '50px', 'marginLeft': '100px','border': '1px solid black'}),

        html.Tr([
            html.Th('Comparto', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white','fontSize':'0.75vw'}),
            html.Th('Ripartizione (0% - 100%)', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white','fontSize':'0.75vw'}),
            html.Th('Soglia Automatic Step-Out', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white','fontSize':'0.75vw'}),
            html.Th('Importo Rata', style={'text-align': 'center','backgroundColor': 'royalblue',
            'color': 'white','fontSize':'0.75vw'})            
        ], style={'border': '1px solid black'}),
        # table rows
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo1', options=[{'label': fondo, 'value': fondo} for fondo in nomi], value='-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            
            html.Td(dcc.Input(id='input1', type='number',min=0, value = 0), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(dcc.Dropdown(id='step_out1', options=[
                                          {'label': '-', 'value': '-'},
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}], value = '-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(id='rata1', style={'text-align': 'center','border': '1px solid black'})

        ],style={'border': '1px solid black'}),
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo2', options=[{'label': fondo, 'value': fondo} for fondo in nomi], value='-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(dcc.Input(id='input2', type='number',min=0, value = 0), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(dcc.Dropdown(id='step_out2', options=[
                                          {'label': '-', 'value': '-'},
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}], value = '-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(id='rata2', style={'text-align': 'center','border': '1px solid black',})

        ]),
        html.Tr([
            html.Td(dcc.Dropdown(id='fondo3', options=[{'label': fondo, 'value': fondo} for fondo in nomi], value='-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(dcc.Input(id='input3', type='number',min=0, value = 0), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(dcc.Dropdown(id='step_out3', options=[
                                          {'label': '-', 'value': '-'},
                                          {'label': '10%', 'value': '10%'},
                                          {'label': '20%', 'value': '20%'}], value = '-'), style={'text-align': 'center','border': '1px solid black','fontSize':'0.75vw'}),
            html.Td(id='rata3', style={'text-align': 'center','border': '1px solid black'})

        ],style={'border': '1px solid black'}),
    ],style={'width': '60%', 'table-layout': 'adaptive','marginTop': '50px','border': '1px solid black'})

    ], style={'display': 'flex', 'justify-content': 'center', 'margin-top': '10px'}), 
    
    html.Div(id='output',style={'margin': 'auto', 'justify-content': 'center','display': 'flex'}),
    
    html.Div([
        html.Div([
            html.Button('Look Through Comparto 1', id='btn-nclicks-1', style={'margin-right': '20px', 'fontSize':'0.75vw'}),
            html.Button('Look Through Comparto 2', id='btn-nclicks-2', style={'margin-right': '20px', 'fontSize':'0.75vw'}),
            html.Button('Look Through Comparto 3', id='btn-nclicks-3', style={'margin-right': '20px', 'fontSize':'0.75vw'}),
            html.Button('Complessivo', id='btn-nclicks-all', style={'fontSize':'0.75vw'})
        ], style={'display': 'flex', 'justify-content': 'center', 'margin-top': '30px'})
    ]),
    
    html.Div(children=[
    dcc.Graph(id='grafico_iis', style={'height': '70%', 'width': '100%', 'display': 'block'}, config={'displayModeBar': False}),   
    dcc.Graph(id='istogramma', style={'height': '30%', 'width': '100%', 'display': 'block', 'margin-top': '0px'}, config={'displayModeBar': False})
    ], style={'height': '1000px','justify-content': 'center'}),           
    
    
    html.Div([dash_table.DataTable(
            id='stats',
            columns=[
                {"name": [" ", "Nome"], "id": "nome"},
                {"name": ["Performance", "IIS"], "id": "perfiis"},
                {"name": ["Performance", "PIC"], "id": "perfpic"},
                {"name": ["Performance", "Effetto Strategia"], "id": "perfstra"},
                {"name": ["Performance", "Prezzo Iniziale"], "id": "perfprin"},
                {"name": ["Performance", "Prezzo Finale"], "id": "perfprfin"},   
                {"name": ["Performance", "Prezzo Medio"], "id": "perfprmed"}, 
                {"name": ["Performance", "Rimbalzo per parità IIS"], "id": "perfrimbiis"}, 
                {"name": ["Performance", "Rimbalzo per parità PIC"], "id": "perfrimbpic"}, 
                {"name": ["Volatilità", "IIS"], "id": "voliis"},
                {"name": ["Volatilità", "PIC"], "id": "volpic"},
                {"name": ["Volatilità", "Effetto Strategia"], "id": "volstra"},
                {"name": ["Max Draw-Down", "IIS"], "id": "mddiis"},
                {"name": ["Max Draw-Down", "PIC"], "id": "mddpic"},
                {"name": ["Max Draw-Down", "Effetto Strategia"], "id": "mddstra"},
            ],
            data=None,
            merge_duplicate_headers=True,
            style_table={                
                'margin': 'auto',  
            },
            style_header={
                'backgroundColor': 'royalblue',
                'color': 'white',
                'fontWeight': 'bold',
                'text-align': 'center'
            },
            style_cell={'textAlign': 'center', 'fontSize':'0.75vw'}
        )
                
    ],style={'justify-content': 'center','text-align': 'center', 'width':'100%','marginTop':'40px'}
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
                        style_cell={'textAlign': 'center', 'fontSize':'0.75vw'}
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
                        style_cell={'textAlign': 'center', 'fontSize':'0.75vw'}
                    ),
                    className="six columns",
                    style={"display": "inline-block",'text-align': 'center'}
                ),
            ],
            style={"display": "flex", 'text-align': 'center','justify-content': 'center','width':'100%','marginTop':'20px'}
        )
    ]
),

     
     html.Div(children=[html.H1("Prezzo vs Prezzo Medio di Carico vs Prezzo Medio", style={"font-size": "0.9vw","text-align": "center"}),
                        dcc.Graph(id='pmc1', style={'width': '33%','height':'80%', 'display': 'inline-block'},config={'displayModeBar': False}),
                        dcc.Graph(id='pmc2', style={'width': '33%', 'height':'80%','display': 'inline-block'},config={'displayModeBar': False}),
                        dcc.Graph(id='pmc3', style={'width': '33%', 'height':'80%','display': 'inline-block'},config={'displayModeBar': False})
                        ], style={'height': '300px', 'margin': 'auto', 'justify-content': 'center','marginTop':'40px'})
    
     ]) 


#%%         
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
    [Input('durata_months', 'value'), Input('installment-amount', 'children'), Input('input1', 'value'), Input('input2', 'value'), Input('input3', 'value'), Input('fondo1', 'value'), Input('fondo2', 'value'), Input('fondo3', 'value'), Input('step_out1', 'value'), Input('step_out2', 'value'), Input('step_out3', 'value')]
)
def update_output(durata_months,installment_amount,input1, input2, input3, fondo1, fondo2, fondo3, step_out1, step_out2, step_out3):
    
    total = input1 + input2 + input3
    rata1 = round(float(installment_amount.strip('€')) * float(input1) / 100, 2)
    rata2 = round(float(installment_amount.strip('€')) * float(input2) / 100, 2)
    rata3 = round(float(installment_amount.strip('€')) * float(input3) / 100, 2)
    
    if (input1<0) or (input2<0) or (input3<0):
        return html.Div(f'Non sono ammessi valori di ripartizione negativi.', style={'color': 'red'})
    
    elif total != 100:
        return html.Div(f'Il totale della Ripartizione deve essere 100%. Totale: {total}.', style={'color': 'red'})

    elif (rata1*durata_months <15000 and (input1 != 0 and input1 != None)) or (rata2*durata_months <15000 and (input2 != 0 and input2 != None)) or (rata3*durata_months <15000 and (input3 != 0 and input3 != None)):
        return html.Div(f'La ripartizione non permette di rispettare i minimi contrattuali', style={'color': 'red'})
    
    elif ((fondo1 != '-') and (step_out1 == '-')) or ((fondo2 != '-') and (step_out2 == '-')) or ((fondo3 != '-') and (step_out3 == '-')):
        return html.Div(f'Associare a ogni fondo una soglia Step-Out', style={'color': 'red'})
    
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


@app.callback(
    [Output('grafico_iis', 'figure'),
     Output('istogramma', 'figure'),
     Output('stats', 'data'),
     Output('step_in', 'data'),
     Output('step_out', 'data'),
     Output('pmc1', 'figure'),
     Output('pmc2', 'figure'),
     Output('pmc3', 'figure')],
    [Input('start_date', 'value'),
     Input('importo', 'value'),
     Input('durata_months', 'value'),
     Input('fondo1', 'value'),
     Input('fondo2', 'value'),
     Input('fondo3', 'value'),
     Input('input1', 'value'),
     Input('input2', 'value'),
     Input('input3', 'value'),
     Input('step_out1', 'value'),
     Input('step_out2', 'value'),
     Input('step_out3', 'value'),
     Input('btn-nclicks-1', 'n_clicks'),
     Input('btn-nclicks-2', 'n_clicks'),
     Input('btn-nclicks-3', 'n_clicks'),
     Input('btn-nclicks-all', 'n_clicks'),
     ]
)

def motore(start_date, importo, durata_months, fondo1, fondo2, fondo3, input1, input2, input3, step_out1, step_out2, step_out3, btn1, btn2, btn3, btnall ):
 
    if start_date is not None and importo is not None and durata_months is not None and fondo1 is not None and fondo2 is not None and fondo3 is not None and input1 is not None and input2 is not None and input3 is not None and step_out1 is not None and step_out2 is not None and step_out3 is not None:
        
       
        
        #%%     
        if step_out1 == '-':
            step_out1 = '%0'
        
        if step_out2 == '-':
            step_out2 = '%0'     
            
        if step_out3 == '-':
            step_out3 = '%0'            
        
        chosen_date = start_date
        start_date = dt.strptime(start_date, '%d/%m/%Y')
        
        
        # fondo1 = get_key_by_value(names_dict, fondo1)
        # fondo2 = get_key_by_value(names_dict, fondo2)
        # fondo3 = get_key_by_value(names_dict, fondo3)
        
        selected_funds = [isin_dict[c] for c in [fondo1, fondo2, fondo3]]# [fondo1, fondo2, fondo3]
        ripartizione = {selected_funds[0]: input1/100,  selected_funds[1]: input2/100, selected_funds[2]:input3/100} #scegliere ripartizione tra i 3 fondi scelti 
        importo_rata_tot = round(importo/durata_months,2) #dipende dalla durata scelta
        
        
        clicks = {'1' : 'btn-nclicks-1', '2' : 'btn-nclicks-2', '3' : 'btn-nclicks-3'}
#%% POSSIBILITA' DI SCEGLIERE MENO DI 3 FONDI
        change_1 = None
        change_2 = None

        if selected_funds[0] == '-' and ((selected_funds[1] != '-') or (selected_funds[2] != '-')):
            if selected_funds[1] != '-':
                selected_funds[0] = selected_funds[1]                
                selected_funds[1] = '-'
                
                clicks['1'] = clicks['2']
                temp = "btn-nclicks-1"            
                clicks['2'] = temp
                
                change_1 = True
                
            elif selected_funds[2] != '-':
                selected_funds[0] = selected_funds[2]
                selected_funds[2] = '-'
                
                clicks['1'] = clicks['3']
                temp = "btn-nclicks-1"            
                clicks['3'] = temp
                
                change_2 = True
                
        for c in selected_funds:
            if c == '-':
                ripartizione[c] = 0

        none_index = [i for i, x in enumerate(ripartizione[t] for t in selected_funds) if (x == 0 or x == None)]

        for i in none_index:
            selected_funds[i] = str(i)
        
        if change_1 == True:  
            soglia_step_out = {selected_funds[0]: float(step_out2.strip('%'))/100,  selected_funds[1]: float(step_out1.strip('%'))/100, selected_funds[2]:float(step_out3.strip('%'))/100}
        elif change_2 == True:  
            soglia_step_out = {selected_funds[0]: float(step_out3.strip('%'))/100,  selected_funds[1]: float(step_out2.strip('%'))/100, selected_funds[2]:float(step_out1.strip('%'))/100}
        else:
            soglia_step_out = {selected_funds[0]: float(step_out1.strip('%'))/100,  selected_funds[1]: float(step_out2.strip('%'))/100, selected_funds[2]: float(step_out3.strip('%'))/100}

        for i in none_index:    
            ripartizione[selected_funds[i]] = 0
            base_dati_weekly[str(i)] = 0
            base_dati[str(i)] = 0
            names_dict[str(i)] = str(i)
            isin_dict[str(i)] = str(i)
        
        
        #%% dipende da start_date
        date_list  = []
        date_list.append(start_date)
        
        iteration = 0
        for t in range(len(base_dati_weekly[base_dati_weekly.index > start_date])):
            iteration +=1
            if (iteration%4 == 0) and (iteration !=0):
                date_list.append(base_dati_weekly[base_dati_weekly.index > start_date].index[t])


        # creo il dataframe dinamico in base alla selezione dei fondi

        dati_calcolo = pd.DataFrame(index = date_list, columns = base_dati_weekly.columns)
        dati_calcolo[dati_calcolo.columns] = base_dati_weekly[dati_calcolo.columns]

        funds_e_liq = selected_funds.copy()
        funds_e_liq.append('IE0030608859') 
        dati_calcolo = dati_calcolo[funds_e_liq]

        # get the indices of rows that contain NaN values
        nan_rows = dati_calcolo[dati_calcolo.isna().any(axis=1)].index

        for n in nan_rows:
            for c in dati_calcolo.columns:
                dati_calcolo[c].loc[n] = base_dati[c].loc[base_dati.index[base_dati.index.get_loc(n, method='ffill')]]

        dati_calcolo = dati_calcolo[dati_calcolo.index < base_dati_weekly.index[-1]]

        # creo n dataframe a seconda dei fondi scelti (max3)

        calcolo_dict = {c : {} for c in selected_funds}
        calcolo_dict['TOTALI'] = pd.DataFrame(index = dati_calcolo.index, columns = ['CTV Fondi', 'Tot Rata ' + selected_funds[0], 'Tot Rata ' + selected_funds[1], 'Tot Rata ' + selected_funds[2]])
        calcolo_dict['MBB Euro Fixed Income LA'] = dati_calcolo['IE0030608859']
        calcolo_dict['Fondi Azionari'] = pd.DataFrame(index = dati_calcolo.index, columns= ['Fondi Azionari', 'MBB Euro Fixed Income', 'CTV Totale', 'Flussi Step-In', 'Flussi Step-Out', 'Rata Base'])

        #%%
        for c in selected_funds:
            
            calcolo_dict[c]['df'] = pd.DataFrame(index = dati_calcolo.index, columns=['QUOTA', 'RATA','RADDOPPIA_RATA'])
            calcolo_dict[c]['df']['QUOTA'] = dati_calcolo[c]                                 
            calcolo_dict[c]['Ripartizione'] = ripartizione[c]
            calcolo_dict[c]['Soglia_step_out'] = soglia_step_out[c]
            calcolo_dict[c]['Importo rata'] = calcolo_dict[c]['Ripartizione'] * importo / durata_months
            calcolo_dict[c]['Fondo liquidità'] = pd.DataFrame(index = dati_calcolo.index, columns=['Liquidità'])
            calcolo_dict[c]['NOME FONDO'] = names_dict[c]
        #1.54    
            if calcolo_dict[c]['Importo rata'] != 0:
                calcolo_dict[c]['1.54'] = 1.54
            else:
                calcolo_dict[c]['1.54'] = 0
                
            
            
            calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[0] = 1
            calcolo_dict[c]['df']['RATA'].iloc[0] = calcolo_dict[c]['Importo rata'] - calcolo_dict[c]['1.54'] * calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[0]  
            
                
            
                
            calcolo_dict[c]['df']['PMC'] = np.nan
            calcolo_dict[c]['df']['N_QUOTE'] = np.nan
            calcolo_dict[c]['df']['CTV_AZIONARIO'] = np.nan
            calcolo_dict[c]['df']['DEN_CONSOLIDA'] = np.nan
            calcolo_dict[c]['df']['CONSOLIDA_LORDA'] = np.nan
            calcolo_dict[c]['df']['CONSOLIDA_NETTA'] = np.nan
            calcolo_dict[c]['df']['CONSOLIDA_EFF'] = np.nan
            
            calcolo_dict[c]['df']['PMC'].iloc[0] = calcolo_dict[c]['df']['QUOTA'].iloc[0]
            calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[0] = calcolo_dict[c]['df']['PMC'].iloc[0]
            calcolo_dict[c]['df']['N_QUOTE'].iloc[0] = calcolo_dict[c]['df']['RATA'].iloc[0] / calcolo_dict[c]['df']['QUOTA'].iloc[0]
            calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[0] = 0
            calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[0] = 0
            calcolo_dict[c]['df']['CONSOLIDA_EFF'].iloc[0] = 0
            calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[0] = calcolo_dict[c]['df']['RATA'].iloc[0] - calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[0]
            calcolo_dict['TOTALI']['Tot Rata ' + c].iloc[0] = - calcolo_dict[c]['df']['RATA'].iloc[0] - calcolo_dict[c]['1.54']

        #%%    QUESTI FUORI DAL LOOP (FONDO_LIQUIDITà E TOTALE CTV FONDI)
               
        calcolo_dict[selected_funds[0]]['Fondo liquidità'].iloc[0] = importo         
        calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[0] = calcolo_dict[selected_funds[0]]['Fondo liquidità'].iloc[0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[0]].iloc[0] + sum([calcolo_dict[selected_funds[0]]['df']['CONSOLIDA_NETTA'].iloc[0], calcolo_dict[selected_funds[1]]['df']['CONSOLIDA_NETTA'].iloc[0], calcolo_dict[selected_funds[2]]['df']['CONSOLIDA_NETTA'].iloc[0]])           
        calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[0] = calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[1]].iloc[0]


        calcolo_dict['TOTALI']['CTV Fondi'].iloc[0] =  calcolo_dict[selected_funds[0]]['df']['CTV_AZIONARIO'].iloc[0] + calcolo_dict[selected_funds[1]]['df']['CTV_AZIONARIO'].iloc[0] + calcolo_dict[selected_funds[2]]['df']['CTV_AZIONARIO'].iloc[0]
                
        #%%
        for r in range(1,len(calcolo_dict[c]['df'])):
            # 
            
        ########################################################################################################################################################################    
            for c in selected_funds:            
            
                
        # RADDOPPIA_RATA     
                if calcolo_dict[c]['df'].index[r] <=  start_date + relativedelta(months= + durata_months):
                    if (((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) <= -0.05) & ((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) > -0.1)):
                        calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] = 2
                        
                    elif (((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) <= -0.1) & ((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) > -0.15)):
                        calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] = 3
                        
                    elif (((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) <= -0.15) & ((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) > -0.2)):
                        calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] = 4
                        
                    elif ((calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['PMC'].iloc[r-1] -1) <= -0.2):
                        calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] = 5
                        
                    else:
                        calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] = 1
         
        #FONDO LIQUIDITA       
                if r==1:
                    if c == selected_funds[0]:
                        calcolo_dict[c]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[r-1][0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[2]].iloc[r-1]
                    elif c == selected_funds[1]:                 
                        calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[0]]['Fondo liquidità'].iloc[r][0] * (calcolo_dict['MBB Euro Fixed Income LA'].iloc[r] / calcolo_dict['MBB Euro Fixed Income LA'].iloc[r-1]) + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[0]].iloc[r] + calcolo_dict[selected_funds[0]]['df']['CONSOLIDA_NETTA'].iloc[r]
                    elif c == selected_funds[2]: 
                        calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[r][0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[1]].iloc[r] + calcolo_dict[selected_funds[1]]['df']['CONSOLIDA_NETTA'].iloc[r]
                
                else:
                    if c == selected_funds[0]:
                        calcolo_dict[selected_funds[0]]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[r-1][0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[2]].iloc[r-1] + calcolo_dict[selected_funds[2]]['df']['CONSOLIDA_NETTA'].iloc[r-1]
                    elif c == selected_funds[1]:
                        calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[0]]['Fondo liquidità'].iloc[r][0] * (calcolo_dict['MBB Euro Fixed Income LA'].iloc[r] / calcolo_dict['MBB Euro Fixed Income LA'].iloc[r-1]) + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[0]].iloc[r] + calcolo_dict[selected_funds[0]]['df']['CONSOLIDA_NETTA'].iloc[r]
                    elif c == selected_funds[2]:
                        calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[r] = calcolo_dict[selected_funds[1]]['Fondo liquidità'].iloc[r][0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[1]].iloc[r] + calcolo_dict[selected_funds[1]]['df']['CONSOLIDA_NETTA'].iloc[r]


              
        # RATA
                if c == selected_funds[0]:
                    
                    if (calcolo_dict[c]['Importo rata'] * calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] - calcolo_dict[c]['1.54']) < calcolo_dict[c]['Fondo liquidità'].iloc[r][0]:            
                        calcolo_dict[c]['df']['RATA'].iloc[r] = calcolo_dict[c]['Importo rata'] * calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] - calcolo_dict[c]['1.54']
                        
                    elif (calcolo_dict[c]['Fondo liquidità'].iloc[r] * calcolo_dict['MBB Euro Fixed Income LA'].iloc[r] / calcolo_dict['MBB Euro Fixed Income LA'].iloc[r-1])[0] <= 250:
                        calcolo_dict[c]['df']['RATA'].iloc[r] = 0
                    
                    else:
                        calcolo_dict[c]['df']['RATA'].iloc[r] = calcolo_dict[c]['Fondo liquidità'].iloc[r][0] * calcolo_dict['MBB Euro Fixed Income LA'].iloc[r] / calcolo_dict['MBB Euro Fixed Income LA'].iloc[r-1] - calcolo_dict[c]['1.54']
                
                else:
                    if (calcolo_dict[c]['Importo rata'] * calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] - calcolo_dict[c]['1.54']) < calcolo_dict[c]['Fondo liquidità'].iloc[r][0]:
                        calcolo_dict[c]['df']['RATA'].iloc[r] = calcolo_dict[c]['Importo rata'] * calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[r] - calcolo_dict[c]['1.54']
                    
                    elif calcolo_dict[c]['Fondo liquidità'].iloc[r][0] <= 250:
                        calcolo_dict[c]['df']['RATA'].iloc[r] = 0
                
                    else:
                        calcolo_dict[c]['df']['RATA'].iloc[r] = calcolo_dict[c]['Fondo liquidità'].iloc[r][0] - calcolo_dict[c]['1.54']

                
        # N_QUOTE
                if calcolo_dict[c]['Importo rata'] != 0:
                    calcolo_dict[c]['df']['N_QUOTE'].iloc[r] = calcolo_dict[c]['df']['RATA'].iloc[r] / calcolo_dict[c]['df']['QUOTA'].iloc[r] + calcolo_dict[c]['df']['N_QUOTE'].iloc[r-1] - calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r-1] / calcolo_dict[c]['df']['QUOTA'].iloc[r-1]
                else:
                    calcolo_dict[c]['df']['N_QUOTE'].iloc[r] = 0



        # PMC
                if calcolo_dict[c]['Importo rata'] != 0:
                    calcolo_dict[c]['df']['PMC'].iloc[r] = ( calcolo_dict[c]['df']['PMC'].iloc[r-1] * ( calcolo_dict[c]['df']['N_QUOTE'].iloc[r-1] - calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r-1] / calcolo_dict[c]['df']['QUOTA'].iloc[r-1] ) + calcolo_dict[c]['df']['RATA'].iloc[r] ) /  calcolo_dict[c]['df']['N_QUOTE'].iloc[r]              
                else:
                    calcolo_dict[c]['df']['PMC'].iloc[r] = 0    


        # CVT_AZIONARIO
                if calcolo_dict[c]['Importo rata'] != 0:
                    calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[r] = calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[r-1] * calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['QUOTA'].iloc[r-1] + calcolo_dict[c]['df']['RATA'].iloc[r] - calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r-1]
                    
                else:
                    calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[r] = 0

            
        # DEN_CONSOLIDA
                if (calcolo_dict[c]['df']['CONSOLIDA_EFF'].iloc[r-1] == 0) & (calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r-1] == 0):
                    calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r] = calcolo_dict[c]['df']['PMC'].iloc[r]
                    
                elif (calcolo_dict[c]['df']['CONSOLIDA_EFF'].iloc[r-1] > 0) & (calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r-1] > 0):
                    calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r] = calcolo_dict[c]['df']['QUOTA'].iloc[r-1]
                    
                else:
                    calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r] = calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r-1]

                
        #CONSOLIDA_LORDA
                if calcolo_dict[c]['df'].index[r] <=  start_date + relativedelta(months= + durata_months):
                    if (calcolo_dict[c]['df']['QUOTA'].iloc[r] / calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r] -1) > calcolo_dict[c]['Soglia_step_out']:
                        calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] = (calcolo_dict[c]['df']['QUOTA'].iloc[r] - calcolo_dict[c]['df']['DEN_CONSOLIDA'].iloc[r]) * calcolo_dict[c]['df']['N_QUOTE'].iloc[r]
                    else:
                        calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] = 0
                else:
                    calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] = 0
                    
                    
        #CONSOLIDA_NETTA
                if calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] == 0:
                    calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[r] = 0
                    
                elif calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] * 0.001 <= 2.58:
                    calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[r] = calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] - 2.58
                
                elif calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] * 0.001 > 103.29:
                    calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[r] = calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] - 103.29
                else:
                    calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[r] = calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[r] * 0.999
                
        #CONSOLIDA_EFF
                calcolo_dict[c]['df']['CONSOLIDA_EFF'].iloc[r] = sum(calcolo_dict[c]['df']['CONSOLIDA_NETTA'].iloc[:r+1])
                 
        #TOTALI
                calcolo_dict['TOTALI']['CTV Fondi'].iloc[r] =  calcolo_dict[selected_funds[0]]['df']['CTV_AZIONARIO'].iloc[r] + calcolo_dict[selected_funds[1]]['df']['CTV_AZIONARIO'].iloc[r] + calcolo_dict[selected_funds[2]]['df']['CTV_AZIONARIO'].iloc[r]
                calcolo_dict['TOTALI']['Tot Rata ' + c].iloc[r] =  - calcolo_dict[c]['df']['RATA'].iloc[r] - calcolo_dict[c]['1.54'] if calcolo_dict[c]['df']['RATA'].iloc[r] > 0 else 0         
        #%%
        calcolo_dict['TOT Fondo liquidità'] = calcolo_dict[selected_funds[0]]['Fondo liquidità'].shift(-1)
        calcolo_dict['TOT Fondo liquidità'].iloc[-1] = calcolo_dict[selected_funds[2]]['Fondo liquidità'].iloc[-1][0] + calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[2]].iloc[-1] + calcolo_dict[selected_funds[2]]['df']['CONSOLIDA_NETTA'].iloc[-1]
                

        #%%
        for r in dati_calcolo.index:
           
            calcolo_dict['Fondi Azionari']['Flussi Step-In'].loc[r] = sum(calcolo_dict['TOTALI'][calcolo_dict['TOTALI'].columns[1:]].loc[r])
            calcolo_dict['Fondi Azionari']['Flussi Step-Out'].loc[r] = sum([calcolo_dict[c]['df']['CONSOLIDA_NETTA'].loc[r] for c in selected_funds])   
            calcolo_dict['Fondi Azionari']['MBB Euro Fixed Income'].loc[r] = calcolo_dict['TOT Fondo liquidità']['Liquidità'].loc[r]
            
            if calcolo_dict[selected_funds[0]]['df']['CTV_AZIONARIO'].loc[r] > 0:
                calcolo_dict['Fondi Azionari']['Fondi Azionari'].loc[r] = calcolo_dict['TOTALI']['CTV Fondi'].loc[r] - calcolo_dict['Fondi Azionari']['Flussi Step-Out'].loc[r]
                
            if calcolo_dict['Fondi Azionari']['Fondi Azionari'].loc[r] > 0:
                if r == calcolo_dict['TOTALI'].index[0]:
                    calcolo_dict['Fondi Azionari']['CTV Totale'].loc[r] = importo
                else:
                    calcolo_dict['Fondi Azionari']['CTV Totale'].loc[r] =  calcolo_dict['Fondi Azionari']['Fondi Azionari'].loc[r] + calcolo_dict['Fondi Azionari']['MBB Euro Fixed Income'].loc[r] 
                    
            if calcolo_dict['Fondi Azionari']['Fondi Azionari'].loc[r] > 0:
                if r <  start_date + relativedelta(months= + durata_months): 
                   calcolo_dict['Fondi Azionari']['Rata Base'].loc[r] = - importo_rata_tot 

        #%% CALCOLO PIC
        
        calcolo_dict['PIC'] = pd.DataFrame(index=dati_calcolo.index, columns =['PIC','PIC_ret', 'ret_'+selected_funds[0], 'ret_'+selected_funds[1], 'ret_'+selected_funds[2], 'INV_'+selected_funds[0], 'INV_'+selected_funds[1], 'INV_'+selected_funds[2]])
        calcolo_dict['PIC']['PIC'].iloc[0] = importo
        
        for c in selected_funds:
            calcolo_dict['PIC'][c] = calcolo_dict[c]['df']['QUOTA']
            calcolo_dict['PIC']['INV_'+c].iloc[0] = importo * calcolo_dict[c]['Ripartizione']
            
        calcolo_dict['PIC']['PIC_ret'] = calcolo_dict['PIC']['ret_'+selected_funds[0]] * calcolo_dict[selected_funds[0]]['Ripartizione'] + calcolo_dict['PIC']['ret_'+selected_funds[1]] * calcolo_dict[selected_funds[1]]['Ripartizione'] + calcolo_dict['PIC']['ret_'+selected_funds[2]] * calcolo_dict[selected_funds[2]]['Ripartizione']
        
        for t in range(1,len(calcolo_dict['PIC'])): 
            for c in selected_funds:
                if calcolo_dict[c]['Ripartizione'] == 0:
                    calcolo_dict['PIC']['INV_'+c].iloc[t] = 0
                else:  
                    calcolo_dict['PIC']['INV_'+c].iloc[t] = calcolo_dict['PIC']['INV_'+c].iloc[t-1] * (calcolo_dict['PIC'][c].iloc[t] / calcolo_dict['PIC'][c].iloc[t-1] )
            
            calcolo_dict['PIC']['PIC'].iloc[t] = calcolo_dict['PIC']['INV_'+selected_funds[0]].iloc[t] + calcolo_dict['PIC']['INV_'+selected_funds[1]].iloc[t] + calcolo_dict['PIC']['INV_'+selected_funds[2]].iloc[t]
        
        calcolo_dict['PIC'] = calcolo_dict['PIC'].apply(pd.to_numeric)
        
        #%% STATISTICHE IIS e PIC
        calcolo_dict['performance'] = pd.DataFrame(columns=['Performance','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC'], index=['IIS', selected_funds[0], selected_funds[1], selected_funds[2]])
        calcolo_dict['volatilità'] = pd.DataFrame(columns=['Volatilità','IIS','PIC','Effetto Strategia'], index=['IIS', selected_funds[0], selected_funds[1], selected_funds[2]])
        calcolo_dict['maxdd'] = pd.DataFrame(columns=['Max Draw-Down','IIS','PIC','Effetto Strategia'], index=['IIS', selected_funds[0], selected_funds[1], selected_funds[2]])
        calcolo_dict['step_in'] = {}
        calcolo_dict['step_out'] = {}
        calcolo_dict['ctv fondi'] = pd.DataFrame(index=dati_calcolo.index, columns=selected_funds)
        calcolo_dict['calcolo_maxdd'] = pd.DataFrame(index=dati_calcolo.index, columns=selected_funds)

        calcolo_dict['step_out']['numero attivationi'] = 0

        calcolo_dict['step_in']['numero attivazioni x2'] = 0 
        calcolo_dict['step_in']['numero attivazioni x3'] = 0 
        calcolo_dict['step_in']['numero attivazioni x4'] = 0 
        calcolo_dict['step_in']['numero attivazioni x5'] = 0 

        for c in selected_funds: 
            calcolo_dict[c]['df']['RADDOPPIA_RATA'][calcolo_dict[c]['df']['RATA'] == 0] = 0
            calcolo_dict[c]['df']['RADDOPPIA_RATA'].iloc[durata_months:] = 1

            calcolo_dict['step_out']['numero attivationi'] += len(calcolo_dict[c]['df']['CONSOLIDA_NETTA'].replace(0,np.nan).dropna())
            
            calcolo_dict['step_in']['numero attivazioni x2'] += len(calcolo_dict[c]['df']['RADDOPPIA_RATA'][calcolo_dict[c]['df']['RADDOPPIA_RATA'] == 2].replace(0,np.nan).dropna())
            calcolo_dict['step_in']['numero attivazioni x3'] += len(calcolo_dict[c]['df']['RADDOPPIA_RATA'][calcolo_dict[c]['df']['RADDOPPIA_RATA'] == 3].replace(0,np.nan).dropna())
            calcolo_dict['step_in']['numero attivazioni x4'] += len(calcolo_dict[c]['df']['RADDOPPIA_RATA'][calcolo_dict[c]['df']['RADDOPPIA_RATA'] == 4].replace(0,np.nan).dropna())
            calcolo_dict['step_in']['numero attivazioni x5'] += len(calcolo_dict[c]['df']['RADDOPPIA_RATA'][calcolo_dict[c]['df']['RADDOPPIA_RATA'] == 5].replace(0,np.nan).dropna())

        calcolo_dict['step_in']['numero attivazioni tot'] = calcolo_dict['step_in']['numero attivazioni x2'] + calcolo_dict['step_in']['numero attivazioni x3'] + calcolo_dict['step_in']['numero attivazioni x4'] + calcolo_dict['step_in']['numero attivazioni x5']

            
        ########################################################## PERFORMANCE ################################################################
        calcolo_dict['performance']['Performance'] = calcolo_dict['performance'].index

        calcolo_dict['performance']['IIS'].loc['IIS'] = (calcolo_dict['Fondi Azionari']['CTV Totale'].iloc[-1] / calcolo_dict['Fondi Azionari']['CTV Totale'].iloc[0]) -1
        calcolo_dict['performance']['PIC'].loc['IIS'] = (calcolo_dict['PIC']['PIC'].iloc[-1] / calcolo_dict['PIC']['PIC'].iloc[0]) -1
        calcolo_dict['performance']['Effetto Strategia'].loc['IIS'] = calcolo_dict['performance']['IIS'].loc['IIS'] - calcolo_dict['performance']['PIC'].loc['IIS']
        calcolo_dict['performance']['Prezzo Iniziale'].loc['IIS'] = None
        calcolo_dict['performance']['Prezzo Finale'].loc['IIS'] = None
        calcolo_dict['performance']['Prezzo Medio'].loc['IIS'] = None
        calcolo_dict['performance']['Rimbalzo per parità IIS'].loc['IIS'] = 0 if (calcolo_dict['performance']['IIS'].loc['IIS'] > 0) else (1/(1+calcolo_dict['performance']['IIS'].loc['IIS'])-1)
        calcolo_dict['performance']['Rimbalzo per parità PIC'].loc['IIS'] = 0 if (calcolo_dict['performance']['PIC'].loc['IIS'] > 0) else (1/(1+calcolo_dict['performance']['PIC'].loc['IIS'])-1)
            

        for c in selected_funds:
            if ripartizione[c] == 0:
                calcolo_dict['performance'].loc[c] = None  
            else:
                
                calcolo_dict['performance']['IIS'].loc[c] = ( calcolo_dict[c]['df']['QUOTA'].iloc[-1] / calcolo_dict[c]['df']['PMC'].iloc[-1] ) -1
                calcolo_dict['performance']['PIC'].loc[c] = ( calcolo_dict[c]['df']['QUOTA'].iloc[-1] / calcolo_dict[c]['df']['QUOTA'].iloc[0] ) -1
                calcolo_dict['performance']['Effetto Strategia'].loc[c] = calcolo_dict['performance']['IIS'].loc[c] - calcolo_dict['performance']['PIC'].loc[c]
                calcolo_dict['performance']['Prezzo Iniziale'].loc[c] = pd.to_numeric(round(calcolo_dict[c]['df']['QUOTA'].iloc[0],2))
                calcolo_dict['performance']['Prezzo Finale'].loc[c] = pd.to_numeric(round(calcolo_dict[c]['df']['QUOTA'].iloc[-1],2))
                calcolo_dict['performance']['Prezzo Medio'].loc[c] = pd.to_numeric(round(calcolo_dict[c]['df']['PMC'].iloc[-1],2))
                calcolo_dict['performance']['Rimbalzo per parità IIS'].loc[c] = 0 if (calcolo_dict['performance']['IIS'].loc[c] > 0) else (1/(1+calcolo_dict['performance']['IIS'].loc[c])-1)
                calcolo_dict['performance']['Rimbalzo per parità PIC'].loc[c] = 0 if (calcolo_dict['performance']['PIC'].loc[c] > 0) else (1/(1+calcolo_dict['performance']['PIC'].loc[c])-1)
                calcolo_dict['performance']['Performance'].loc[c] = names_dict[c]
                
        calcolo_dict['performance'] = calcolo_dict['performance'].reset_index(drop=True) 
               
        ########################################################## VOLATILITà ##########################################################
        calcolo_dict['volatilità']['Volatilità'] = calcolo_dict['volatilità'].index
        
        calcolo_dict['volatilità']['IIS'].loc['IIS'] = np.std(calcolo_dict['Fondi Azionari']['CTV Totale'].iloc[:durata_months+1].pct_change(), ddof=1) * np.sqrt(12) #volatilità annualizzata
        calcolo_dict['volatilità']['PIC'].loc['IIS'] = np.std(calcolo_dict['PIC']['PIC'].iloc[:durata_months+1].pct_change(), ddof=1) * np.sqrt(12) #volatilità annualizzata
        calcolo_dict['volatilità']['Effetto Strategia'].loc['IIS'] = calcolo_dict['volatilità']['IIS'].loc['IIS'] - calcolo_dict['volatilità']['PIC'].loc['IIS']
        
        
        for c in selected_funds:
            if ripartizione[c] == 0 or ripartizione[c] == None:
                calcolo_dict['volatilità'].loc[c] = None        
            else: 
                
                for r in range(len(dati_calcolo.index)):
                    calcolo_dict['ctv fondi'][c].iloc[r] = calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[r] + importo * ripartizione[c] + sum(calcolo_dict['TOTALI']['Tot Rata ' + c].iloc[:r+1])
                    
                alpha = list(calcolo_dict['ctv fondi'][c][:durata_months])
                alpha.insert(0,importo * ripartizione[c])
                alpha = pd.Series(alpha)
                calcolo_dict['volatilità']['IIS'].loc[c] = np.std(alpha.pct_change(), ddof=1) * np.sqrt(12) #volatilità annualizzata
                calcolo_dict['volatilità']['PIC'].loc[c] = np.std(calcolo_dict[c]['df']['QUOTA'][:durata_months+1].pct_change(), ddof=1) * np.sqrt(12) #volatilità annualizzata
                calcolo_dict['volatilità']['Effetto Strategia'].loc[c] = calcolo_dict['volatilità']['IIS'].loc[c] - calcolo_dict['volatilità']['PIC'].loc[c]
                calcolo_dict['volatilità']['Volatilità'].loc[c] = names_dict[c]
                
        calcolo_dict['volatilità'] = calcolo_dict['volatilità'].reset_index(drop=True)


        ########################################################## MAX_DRAW_DOWN ##########################################################
        calcolo_dict['maxdd']['Max Draw-Down'] = calcolo_dict['maxdd'].index

        calcolo_dict['maxdd']['IIS'].loc['IIS'] = (min(calcolo_dict['Fondi Azionari']['CTV Totale']) / calcolo_dict['Fondi Azionari']['CTV Totale'].iloc[0]) -1 #ddof=1 fa si che la volatilità sia del campione e replichi la funzione excel
        calcolo_dict['maxdd']['PIC'].loc['IIS'] = (min(calcolo_dict['PIC']['PIC']) / calcolo_dict['PIC']['PIC'].iloc[0]) -1 #ddof=1 fa si che la volatilità sia del campione e replichi la funzione excel
        calcolo_dict['maxdd']['Effetto Strategia'].loc['IIS'] =  calcolo_dict['maxdd']['IIS'].loc['IIS'] - calcolo_dict['maxdd']['PIC'].loc['IIS']

        for c in selected_funds:
            if ripartizione[c] == 0:
                calcolo_dict['maxdd'].loc[c] = None        
            else: 
                
                for r in range(len(dati_calcolo.index)):
                    calcolo_dict['calcolo_maxdd'][c].iloc[r] = calcolo_dict[c]['df']['CTV_AZIONARIO'].iloc[r] / ( sum(calcolo_dict[c]['df']['RATA'].iloc[:r+1]) - sum(calcolo_dict[c]['df']['CONSOLIDA_LORDA'].iloc[:r+1]) ) -1
                    
                
                calcolo_dict['maxdd']['IIS'].loc[c] = min(calcolo_dict['calcolo_maxdd'][c])
                calcolo_dict['maxdd']['PIC'].loc[c] = min(calcolo_dict[c]['df']['QUOTA'] / calcolo_dict[c]['df']['QUOTA'].iloc[0] -1)
                calcolo_dict['maxdd']['Effetto Strategia'].loc[c] = calcolo_dict['maxdd']['IIS'].loc[c] - calcolo_dict['maxdd']['PIC'].loc[c]
                calcolo_dict['maxdd']['Max Draw-Down'].loc[c] = names_dict[c]
                
        calcolo_dict['maxdd'] = calcolo_dict['maxdd'].reset_index(drop=True)
           
          
        #%%creo dataframes da usare per riempire tabelle nella dashboard

        #TABELLA PERFORMANCE
        calcolo_dict['performance'][['Performance','IIS','PIC','Effetto Strategia','Rimbalzo per parità IIS','Rimbalzo per parità PIC']] = calcolo_dict['performance'][['Performance','IIS','PIC','Effetto Strategia','Rimbalzo per parità IIS','Rimbalzo per parità PIC']].applymap(to_percent)
        performance = calcolo_dict['performance']

        #TABELLA VOLATILITA
        volatilita = calcolo_dict['volatilità'].applymap(to_percent)


        #TABELLA MAX DD
        max_dd = calcolo_dict['maxdd'].applymap(to_percent)
        
        #TABELLA STATS
        stats = pd.DataFrame(index = performance.index, columns= [[' ','Performance','Performance','Performance','Performance','Performance','Performance','Performance','Performance','Volatilità','Volatilità','Volatilità','Max Draw-Down','Max Draw-Down','Max Draw-Down'],['Nome','IIS','PIC','Effetto Strategia','Prezzo Iniziale','Prezzo Finale','Prezzo Medio','Rimbalzo per parità IIS','Rimbalzo per parità PIC','IIS','PIC','Effetto Strategia','IIS','PIC','Effetto Strategia']])

        for i in stats.index:
            stats.loc[i,(" ", "Nome")] = np.array(performance['Performance'])[i]
            for c in performance.columns[1:]:
                stats.loc[i,("Performance", c)] = np.array(performance[c])[i]

            for v in volatilita.columns[1:]:
                stats.loc[i,("Volatilità", v)] = np.array(volatilita[v])[i]

            for m in max_dd.columns[1:]:
                stats.loc[i,('Max Draw-Down', m)] = np.array(max_dd[m])[i]

        #TABELLA STEP IN
        step_in = pd.DataFrame(index=[0,1,2,3,4], columns=['Step - In', 'Conteggio'])
        step_in['Step - In'].iloc[0] = 'Numero Attivazione Step - In x 2'
        step_in['Step - In'].iloc[1] = 'Numero Attivazione Step - In x 3'
        step_in['Step - In'].iloc[2] = 'Numero Attivazione Step - In x 4'
        step_in['Step - In'].iloc[3] = 'Numero Attivazione Step - In x 5'
        step_in['Step - In'].iloc[4] = 'Totale'
        step_in['Conteggio'].iloc[0] = calcolo_dict['step_in']['numero attivazioni x2']
        step_in['Conteggio'].iloc[1] = calcolo_dict['step_in']['numero attivazioni x3']
        step_in['Conteggio'].iloc[2] = calcolo_dict['step_in']['numero attivazioni x4']
        step_in['Conteggio'].iloc[3] = calcolo_dict['step_in']['numero attivazioni x5']
        step_in['Conteggio'].iloc[4] = calcolo_dict['step_in']['numero attivazioni tot']


        #TABELLA STEP OUT
        step_out = pd.DataFrame(index=[0], columns=['Step - Out', 'Conteggio'])
        step_out['Step - Out'] ='Numero Attivazione Step - Out'
        step_out['Conteggio'] = calcolo_dict['step_out']['numero attivationi']
        #%% PREZZO MEDIO
        
        for c in selected_funds:
            calcolo_dict[c]['df']['PREZZO_MEDIO'] = np.nan
            
            for r in range(len(calcolo_dict[c]['df'])):
                calcolo_dict[c]['df']['PREZZO_MEDIO'].iloc[r] = calcolo_dict[c]['df']['QUOTA'].iloc[:r+1].mean()
    #%% PLOT 
            
        #GRAFICO IIS
        data_last = dati_calcolo.index[-1].strftime('%d/%m/%Y')
        iis_graph = go.Figure()
        iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['CTV Totale'], mode='lines', name='CTV Totale', line=dict(color='olivedrab')))
        iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['PIC']['PIC'], mode='lines', name='PIC', line=dict(color='purple')))
        iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['MBB Euro Fixed Income'], mode='lines', name='Fondo Liquidità', line=dict(color='orange')))
        iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['Fondi Azionari'], mode='lines', name='Fondi Azionari', line=dict(color='lightskyblue')))
        iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':f'Simulazione IIS vs PIC dal {chosen_date} al {data_last}', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)
                                ) 
                    
        #GRAFICO STEPIN/STEPOUT         
        hist = go.Figure()
        hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['Flussi Step-Out'], name='Flussi Step-Out', marker=dict(color='gold')))
        hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['Flussi Step-In'], name='Flussi Step-In', marker=dict(color='lightskyblue')))
        hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['Fondi Azionari']['Rata Base'], name='Rata Base', marker=dict(color='blue')))       
        hist.update_layout(legend=dict(orientation="h", y =-0.15, font=dict(size=15)),             
                           plot_bgcolor='white',xaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2),
                           yaxis=dict(showgrid=False),margin=dict(l=0, r=0, t=0, b=50))

####################################################### Look through con bottoni #####################################################
        if clicks['1'] == ctx.triggered_id:
            if selected_funds[0] in ['-','1','2']:
                iis_graph = go.Figure()
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':' ', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2))
                hist = go.Figure()
                hist.update_layout(plot_bgcolor='white')
            else:
                iis_graph = go.Figure()
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['PIC']['INV_'+selected_funds[0]], mode='lines', name='PIC', line=dict(color='purple')))
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[0]]['df']['CTV_AZIONARIO'], mode='lines', name='Fondi Azionari', line=dict(color='lightskyblue')))
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':f'{names_dict[selected_funds[0]]}', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)
                                        ) 
            
                hist = go.Figure()
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict[selected_funds[0]]['df']['CONSOLIDA_NETTA'], name='Flussi Step-Out', marker=dict(color='gold')))
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[0]], name='Flussi Step-In', marker=dict(color='lightskyblue')))
                hist.update_layout(legend=dict(orientation="h", y =-0.15, font=dict(size=15)),             
                                   plot_bgcolor='white',xaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2),
                                   yaxis=dict(showgrid=False),margin=dict(l=0, r=0, t=0, b=50))

        if clicks['2'] == ctx.triggered_id:
            if selected_funds[1] in ['-','1','2']:
                iis_graph = go.Figure()
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':' ', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2))
                hist = go.Figure()
                hist.update_layout(plot_bgcolor='white')
            else:
                iis_graph = go.Figure()
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['PIC']['INV_'+selected_funds[1]], mode='lines', name='PIC', line=dict(color='purple')))
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[1]]['df']['CTV_AZIONARIO'], mode='lines', name='Fondi Azionari', line=dict(color='lightskyblue')))
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':f'{names_dict[selected_funds[1]]}', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)
                                        ) 
                
                hist = go.Figure()
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict[selected_funds[1]]['df']['CONSOLIDA_NETTA'], name='Flussi Step-Out', marker=dict(color='gold')))
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[1]], name='Flussi Step-In', marker=dict(color='lightskyblue')))
                hist.update_layout(legend=dict(orientation="h", y =-0.15, font=dict(size=15)),             
                                   plot_bgcolor='white',xaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2),
                                   yaxis=dict(showgrid=False),margin=dict(l=0, r=0, t=0, b=50))
        
        if clicks['3'] == ctx.triggered_id:
            if selected_funds[2] in ['-','1','2']:
                iis_graph = go.Figure()
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':' ', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2))
                hist = go.Figure()
                hist.update_layout(plot_bgcolor='white')
            else:
                iis_graph = go.Figure()
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict['PIC']['INV_'+selected_funds[2]], mode='lines', name='PIC', line=dict(color='purple')))
                iis_graph.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[2]]['df']['CTV_AZIONARIO'], mode='lines', name='Fondi Azionari', line=dict(color='lightskyblue')))
                iis_graph.update_layout(legend=dict(orientation="h", yanchor="top", y=1.07, xanchor="center", x=0.15, font=dict(size=15)), title={'text':f'{names_dict[selected_funds[2]]}', 'font':{'size': 24}, 'x': 0.5,'y': 0.95, 'xanchor': 'center','yanchor': 'top'},
                                        plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)
                                        ) 
                
                hist = go.Figure()
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict[selected_funds[2]]['df']['CONSOLIDA_NETTA'], name='Flussi Step-Out', marker=dict(color='gold')))
                hist.add_trace(go.Bar(x=dati_calcolo.index, y=calcolo_dict['TOTALI']['Tot Rata ' + selected_funds[2]], name='Flussi Step-In', marker=dict(color='lightskyblue')))
                hist.update_layout(legend=dict(orientation="h", y =-0.15, font=dict(size=15)),             
                                   plot_bgcolor='white',xaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2),
                                   yaxis=dict(showgrid=False),margin=dict(l=0, r=0, t=0, b=50))

######################################################################################################################################

        #TABELLE STATISTICHE
        perf = performance.dropna(axis = 0, how = 'all').to_dict('records')
        vol = volatilita.dropna(axis = 0, how = 'all').to_dict('records')
        maxdd = max_dd.dropna(axis = 0, how = 'all').to_dict('records')
        stepin = step_in.dropna(axis = 0, how = 'all').to_dict('records')
        stepout = step_out.dropna(axis = 0, how = 'all').to_dict('records')
        stats = stats.dropna(axis = 0, how = 'all')
        
        stat = [{
             "nome": stats[" ", "Nome"].loc[i],
             "perfiis": stats["Performance", "IIS"].loc[i],
             "perfpic": stats["Performance", "PIC"].loc[i],
             "perfstra": stats["Performance", "Effetto Strategia"].loc[i],
             "perfprin": stats["Performance", "Prezzo Iniziale"].loc[i],
             "perfprfin": stats["Performance", "Prezzo Finale"].loc[i],
             "perfprmed": stats["Performance", "Prezzo Medio"].loc[i],
             "perfrimbiis": stats["Performance", "Rimbalzo per parità IIS"].loc[i],
             "perfrimbpic": stats["Performance", "Rimbalzo per parità PIC"].loc[i],
             "voliis": stats["Volatilità", "IIS"].loc[i],
             "volpic": stats["Volatilità", "PIC"].loc[i],
             "volstra": stats["Volatilità", "Effetto Strategia"].loc[i],
             "mddiis": stats["Max Draw-Down", "IIS"].loc[i],
             "mddpic": stats["Max Draw-Down", "PIC"].loc[i],
             "mddstra": stats["Max Draw-Down", "Effetto Strategia"].loc[i],
         }for i in stats.index] 
        #GRAFICI PMC
        
        if calcolo_dict[selected_funds[0]]['Ripartizione'] == 0:
            pmc_1 = go.Figure()
            pmc_1.update_layout(autosize=True, margin=dict(l=50, r=50, t=50, b=50), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False)) 
        else:
            pmc_1 = go.Figure()
            pmc_1.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[0]]['df']['PMC'], mode='lines', name='PMC', line=dict(color='orange')))
            pmc_1.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[0]]['df']['QUOTA'], mode='lines', name='Prezzo', line=dict(color='lightskyblue')))
            pmc_1.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[0]]['df']['PREZZO_MEDIO'], mode='lines', name='Prezzo Medio', line=dict(color='olivedrab')))
            pmc_1.update_layout(legend=dict(orientation="h", y =-0.1), title=f'{names_dict[selected_funds[0]]}', autosize=True, margin=dict(l=50, r=50, t=50, b=50), titlefont=dict(size=12), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)) 

                   
        if calcolo_dict[selected_funds[1]]['Ripartizione'] == 0:
            pmc_2 = go.Figure() 
            pmc_2.update_layout(autosize=True, margin=dict(l=50, r=50, t=50, b=50), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False)) 
        else:
            pmc_2 = go.Figure() 
            pmc_2.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[1]]['df']['PMC'], mode='lines', name='PMC', line=dict(color='orange')))
            pmc_2.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[1]]['df']['QUOTA'], mode='lines', name='Prezzo', line=dict(color='lightskyblue')))
            pmc_2.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[1]]['df']['PREZZO_MEDIO'], mode='lines', name='Prezzo Medio', line=dict(color='olivedrab')))
            pmc_2.update_layout(legend=dict(orientation="h", y =-0.1), title=f'{names_dict[selected_funds[1]]}', autosize=True, margin=dict(l=50, r=50, t=50, b=50), titlefont=dict(size=12), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)) 

            
        if calcolo_dict[selected_funds[2]]['Ripartizione'] == 0:
            pmc_3 = go.Figure()
            pmc_3.update_layout(autosize=True, margin=dict(l=50, r=50, t=50, b=50), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=False)) 
        else:
            pmc_3 = go.Figure()
            pmc_3.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[2]]['df']['PMC'], mode='lines', name='PMC', line=dict(color='orange')))
            pmc_3.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[2]]['df']['QUOTA'], mode='lines', name='Prezzo', line=dict(color='lightskyblue')))
            pmc_3.add_trace(go.Scatter(x=dati_calcolo.index, y=calcolo_dict[selected_funds[2]]['df']['PREZZO_MEDIO'], mode='lines', name='Prezzo Medio', line=dict(color='olivedrab')))
            pmc_3.update_layout(legend=dict(orientation="h", y =-0.1), title=f'{names_dict[selected_funds[2]]}', autosize=True, margin=dict(l=50, r=50, t=50, b=50), titlefont=dict(size=12), plot_bgcolor='white',xaxis=dict(showgrid=False),yaxis=dict(showgrid=True, gridcolor='lightgrey', gridwidth=1, tickwidth=2)) 

        return iis_graph, hist, stat, stepin, stepout, pmc_1, pmc_2, pmc_3
    else:
        return {}

# Run the app
if __name__ == '__main__':
    app.run_server()
    


