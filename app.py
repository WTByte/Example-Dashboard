import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import datetime
import requests
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

version = '1.0'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

def get_form_data():
    """
    Downloads a google sheet.
    :return: pandas dataframe
    """
    sheet_id = "1e654j6GAyeM7lkZuFNpqHTYUz9P1EnIqE95BdpyJ2g0"
    sheet_name = "Sheet1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    url = url.replace(' ', '%20')

    data = pd.read_csv(url)

    return data


def get_live_update():

    def get_now():
        current_time = datetime.datetime.now()
        current_time = datetime.datetime.strftime(current_time, '%Y-%m-%d %H:%M:%S')
        return current_time

    sheet_id = "1e654j6GAyeM7lkZuFNpqHTYUz9P1EnIqE95BdpyJ2g0"
    sheet_name = "Form Responses 1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    url = url.replace(' ', '%20')

    r = requests.head(url)
    r.status_code

    return [html.P('Last updated: ' + str(get_now()) +' with status: ' + str(r.status_code))]