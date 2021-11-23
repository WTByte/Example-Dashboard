import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H1('About'),
    dcc.Markdown('''
    
    Thanks for checking out the dashboard! 
    
    This dashboard was created to conveniently and quickly view the inscription data. Data is updated every time the 
    page is refreshed or every hour on the same page - whichever comes first. 
    
    In this example I've used a static Google sheet to retrieve the data but it is possible to use other sources like 
    a MySQL database. 

    '''),
    html.Div([
        html.Img(src='https://avatars.githubusercontent.com/u/23630294?v=4?s=400')
    ], style={'textAlign': 'center'}),

])


@app.callback(
    Output('app-1-display-value', 'children'),
    Input('app-1-dropdown', 'value'))
def display_value(value):
    return 'You have selected "{}"'.format(value)