import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_table import DataTable
from dash_table.Format import Format, Scheme
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd


from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import app, version, server, get_form_data, get_live_update
from apps import user_summary
from apps import about

# Functions
def generate_kpis(data):
    """
    Generate a list of kpis shown at the top of the page
    :param data:
    :return:
    """
    # Total Claims
    total_claims = len(data.index)

    # % Complete
    completion = round(total_claims/12800 * 100, 1)

    # Total Issues
    total_issues = data['error'].sum()

    return total_claims, completion, total_issues


def generate_fig(data):
    """
    Create a line chart of the number of inscriptions over time
    :param data:
    :return: line chart figure
    """
    dfn = pd.DataFrame(data['Timestamp'].copy(deep=True))

    dfn['count'] = 1

    dfn['Timestamp'] = pd.to_datetime(dfn['Timestamp'])

    dfn.set_index('Timestamp', inplace=True)

    daily_responses = dfn.resample('D').sum()

    daily_responses_cumsum = dfn.resample('D').sum().cumsum()

    ### Create plot
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=daily_responses.index.to_list(), y=daily_responses['count'].tolist(), name="Form Response"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=daily_responses_cumsum.index.to_list(), y=daily_responses_cumsum['count'].tolist(),
                   name="Cumulative Form Response"),
        secondary_y=False,
    )

    # Add figure title
    fig.update_layout(
        title_text="Daily Inscription Form Responses"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="Completed Form Responses", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    fig.update_layout(hovermode="x unified")

    # Add annotations
    # fig.add_annotation(x='2021-08-07', y=daily_responses.loc['2021-08-07', 'count'],
    #                    text="Open to public",
    #                    showarrow=False,
    #                    yshift=10)


    return fig

    #return {'data': fig.data, 'layout': fig.layout}, fig


# Most table/chart generating functions will generate a table and corresponding chart.
def generate_issues_table(data):
    """
    Generate an issues table and corresponding bar chart.
    :param data:
    :return: issue table and bar chart
    """

    df_issues_freq = data['error_reason'].value_counts()
    df_issues_percent = data['error_reason'].value_counts(normalize=True) * 100
    df_issues_table = pd.concat([df_issues_freq, df_issues_percent], axis=1)
    df_issues_table.loc["Total"] = df_issues_table.sum()
    df_issues_table.reset_index(inplace=True)
    df_issues_table.columns = ['Error', 'Frequency', 'Percentage']

    df_issues_table_columns = [{"name": i, "id": i} for i in df_issues_table.columns]
    df_issues_table_columns[2]['format'] = Format(precision=1, scheme=Scheme.fixed)
    df_issues_table_columns[2]['type'] = 'numeric'

    df_issues_fig = df_issues_table.drop(df_issues_table.index[-1], axis=0) # Drop total row for bar chart
    fig_issues = px.bar(df_issues_fig, y='Frequency', x='Error')

    return df_issues_table.to_dict('records'), df_issues_table_columns, fig_issues


# Initial Values
app.title = 'Example Dashboard'

data = get_form_data()

current_time = get_live_update()

kpi_total_claims, kpi_claim_completion, kpi_total_issues = generate_kpis(data)

fig = generate_fig(data)

issues_table_data, issues_table_columns, fig_issues = generate_issues_table(data)


# Bootstrap elements
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("User Summary", href="/user_summary")),
        dbc.NavItem(dbc.NavLink("About", href="/about")),
    ],
    brand="Example Dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    fluid=True,
    links_left=True
)


# Layouts
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={'marginLeft': 10, 'marginRight': 10}),
    html.Footer(id='page-footer', children=f'© 2021 WTByte - v{version}', style={'text-align':'center'})
])

index_layout = html.Div([
    dcc.Interval(
            id='interval-component-index',
            interval=3600 * 1000,  # in milliseconds
            n_intervals=0
        ),
    dbc.Row([
        dbc.Col(
            [html.H1(children='Overview'),
             html.Div(id='live-update-text-index', children=current_time),
             ])]),
    dbc.Row([
        dbc.Col([
            html.H2(children='Total Claims', style={'textAlign': 'center'}),
            html.H3(id='kpi-total-claims', children=kpi_total_claims, style={'textAlign': 'center'})
        ]),
        dbc.Col([
            html.H2(children='Total % Claimed', style={'textAlign': 'center'}),
            html.H3(id='kpi-claim-completion', children=kpi_claim_completion, style={'textAlign': 'center'})
        ]),
        dbc.Col([
            html.H2(children='Total Issues', style={'textAlign': 'center'}),
            html.H3(id='kpi-total-issues', children=kpi_total_issues, style={'textAlign': 'center'})
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='example-graph',
                figure=fig
            )]
        )
    ]),
    dbc.Row([
            dbc.Col([
                html.Label(
                    "Error Summary"
                ),
                DataTable(
                    id='issues-table',
                    columns=issues_table_columns,
                    data=issues_table_data,
                )
            ]),
            dbc.Col([
                dcc.Graph(
                    id='fig-issues',
                    figure=fig_issues
            )]),
            #dbc.Col([html.Div('Placeholder for chart 2')]),
        ]),
])

# Note the URL does not include apps/some.py but is required when returning the layout
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return index_layout
    if pathname == '/user_summary':
        return user_summary.layout
    elif pathname == '/about':
        return about.layout
    else:
        return '404 - this page does not exist!'


@app.callback([
    Output('live-update-text-index', 'children'),
    Output('kpi-total-claims', 'children'),
    Output('kpi-claim-completion', 'children'),
    Output('kpi-total-issues', 'children'),
    Output('example-graph', 'figure'),
    Output('issues-table', 'data'),
    Output('issues-table', 'columns'),
    Output('fig-issues', 'figure'),
],
    Input('interval-component-index', 'n_intervals'),
    Input('url', 'pathname'))
def update_index(n, url):

    if url == '/':
        data = get_form_data()

        live_update_text = get_live_update()

        fig = generate_fig(data)

        kpi_total_claims, kpi_claim_completion, kpi_total_issues = generate_kpis(data)

        issues_table_data, issues_table_columns, fig_issues = generate_issues_table(data)

        return live_update_text, kpi_total_claims, kpi_claim_completion, kpi_total_issues, \
               fig, \
               issues_table_data, issues_table_columns, fig_issues
    else:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=False)
