import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.H1('My Dashboard'),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Bar chart'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'line', 'name': 'Line chart'},
            ],
            'layout': {
                'title': 'Graphs'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server()
    
    
