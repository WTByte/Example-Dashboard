import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_table import DataTable
from dash_table.Format import Format, Scheme
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import pycountry

from app import app, get_form_data, get_live_update


def generate_country_table(user_data):

    # If the user data cannot be retrieved, display a generic choropleth chart.
    if (user_data == None).all().all():
        df = px.data.gapminder().query("year==2007")
        fig = px.choropleth(df, locations="iso_alpha",
                            color="lifeExp",  # lifeExp is a column of gapminder
                            hover_name="country",  # column to add to hover information
                            color_continuous_scale=px.colors.sequential.Plasma,
                            title="Placeholder chart: Life Expectancy Around the World in 2007")
        return None, None, fig

    else:
        df_country_freq = user_data['country'].value_counts()
        df_country_percent = user_data['country'].value_counts(normalize=True) * 100
        df_country_table = pd.concat([df_country_freq, df_country_percent], axis=1)
        df_country_table.loc["Total"] = df_country_table.sum()
        df_country_table.reset_index(inplace=True)
        df_country_table.columns = ['Country', 'Frequency', 'Percentage']

        df_country_table_columns = [{"name": i, "id": i} for i in df_country_table.columns]
        df_country_table_columns[2]['format'] = Format(precision=1, scheme=Scheme.fixed)
        df_country_table_columns[2]['type'] = 'numeric'

        df_country_fig = df_country_table.drop(df_country_table.index[-1], axis=0)  # Drop total row for pie chart

        # TODO: FInd a better alternative to pycountry since it is missing quite a few e.g.:
        #  https://laendercode.net/en/3-letter-list.html
        country_list = df_country_fig['Country'].values.tolist()
        iso_country = []
        for c in country_list:
            if c == '0':    # for people we couldn't find
                iso_country.append(np.nan)
            elif c == 'South Korea':
                iso_country.append('KOR')
            elif c == 'Netherlands Antilles':
                iso_country.append('ANT')
            elif c == 'Macau':
                iso_country.append('MAC')
            elif c == 'Saint Helena':
                iso_country.append('SHN')
            elif c == 'Reunion':
                iso_country.append('REU')
            else:
                try:
                    # If we can't find the country via lookup, default to None for the chart.
                    iso_country.append(pycountry.countries.lookup(c).alpha_3)
                except:
                    iso_country.append(None)

        df_country_fig['iso_country'] = iso_country

        fig_country = px.choropleth(df_country_fig, locations="iso_country",
                            color="Frequency",
                            hover_name="Country",  # column to add to hover information
                            )

        return df_country_table.to_dict('records'), df_country_table_columns, fig_country


def generate_speciality_table(data):

    df_speciality_freq = data[data.columns[5]].value_counts()
    df_speciality_percent = data[data.columns[5]].value_counts(normalize=True) * 100
    df_speciality_table = pd.concat([df_speciality_freq, df_speciality_percent], axis=1)
    df_speciality_table.loc["Total"] = df_speciality_table.sum()
    df_speciality_table.reset_index(inplace=True)
    df_speciality_table.columns = ['Speciality', 'Frequency', 'Percentage']

    df_speciality_table_columns = [{"name": i, "id": i} for i in df_speciality_table.columns]
    df_speciality_table_columns[2]['format'] = Format(precision=1, scheme=Scheme.fixed)
    df_speciality_table_columns[2]['type'] = 'numeric'

    df_speciality_fig = df_speciality_table.drop(df_speciality_table.index[-1], axis=0)  # Drop total row for pie chart
    fig_speciality = px.bar(df_speciality_fig, y='Frequency', x='Speciality')

    return df_speciality_table.to_dict('records'), df_speciality_table_columns, fig_speciality


def generate_ratings(data):

    ratings_data = []

    rating_columns = ['r_stamina', 'r_tenacity', 'r_precision', 'r_reaction', 'r_accuracy', 'r_agility']
    rating_columns_clean = []

    for c in rating_columns:
        r_series = data[c].value_counts()
        r_series.name = c.split('_')[-1]
        ratings_data.append(r_series)
        rating_columns_clean.append(c.split('_')[-1])

    df_ratings = pd.concat(ratings_data, axis=1, keys=[s.name for s in ratings_data])

    df_ratings_table = df_ratings.reindex(index=['S', 'A', 'B', 'C', 'D'])
    df_ratings_table.reset_index(inplace=True)
    df_ratings_table.rename(columns={'index': 'Rating'}, inplace=True)
    df_ratings_table_columns = [{"name": i, "id": i} for i in df_ratings_table.columns]

    fig_rating = {'data': df_ratings_table,
                  'options': [{"label": x, "value": x} for x in rating_columns_clean],
                  'value': rating_columns_clean[0]
                 }

    return df_ratings_table.to_dict('records'), df_ratings_table_columns, fig_rating


def generate_ratings_fig(data_ratings, value):

    fig = px.bar(data_ratings, x="Rating", y=value)
    return fig


def generate_first_collab_table(data):
    df_first_collab_freq = data['first_collab'].value_counts()
    df_first_collab_percent = data['first_collab'].value_counts(normalize=True) * 100
    df_first_collab_table = pd.concat([df_first_collab_freq, df_first_collab_percent], axis=1)
    df_first_collab_table.loc["Total"] = df_first_collab_table.sum()
    df_first_collab_table.reset_index(inplace=True)
    df_first_collab_table.columns = ['First Collab', 'Frequency', 'Percentage']

    df_first_collab_table_columns = [{"name": i, "id": i} for i in df_first_collab_table.columns]
    df_first_collab_table_columns[2]['format'] = Format(precision=1, scheme=Scheme.fixed)
    df_first_collab_table_columns[2]['type'] = 'numeric'

    df_issues_fig = df_first_collab_table.drop(df_first_collab_table.index[-1], axis=0) # Drop total row for pie chart
    fig_first_collab = px.pie(df_issues_fig, values='Frequency', names='First Collab')

    return df_first_collab_table.to_dict('records'), df_first_collab_table_columns, fig_first_collab


data = get_form_data()

current_time = get_live_update()

country_table_data, country_table_columns, fig_country = generate_country_table(data)

speciality_table_data, speciality_table_columns, fig_speciality = generate_speciality_table(data)

rating_table_data, rating_table_columns, fig_rating_dict = generate_ratings(data)

fig_rating = generate_ratings_fig(fig_rating_dict['data'], fig_rating_dict['value'])

first_collab_table_data, first_collab_table_columns, fig_first_collab = generate_first_collab_table(data)


layout = html.Div([
    dcc.Interval(
                id='interval-component-user',
                interval=3600 * 1000,  # in milliseconds
                n_intervals=0
            ),
    dbc.Row([
        dbc.Col([
            html.H1(children='User Summary'),
            html.Div(id='live-update-text-user', children=current_time),
        ])
    ]),
    dbc.Row([
        dbc.Col([

            html.Label("Countries"),
            DataTable(
                id='country-table',
                columns=country_table_columns,
                data=country_table_data,
                page_size=10,
    )]),
        dbc.Col([
            dcc.Graph(
                id='fig-country',
                figure=fig_country
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Br()
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Label("Speciality Summary"),
            DataTable(
                id='speciality-table',
                columns=speciality_table_columns,
                data=speciality_table_data,
            )
        ]),
        dbc.Col([
            dcc.Graph(
                id='fig-speciality',
                figure=fig_speciality
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br()
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Label(
                "Rating Summary"
            ),
            DataTable(
                id='rating-table',
                columns=rating_table_columns,
                data=rating_table_data,
            )
        ]),
        dbc.Col([
            dcc.Dropdown(
                id="fig-rating-dropdown",
                options=fig_rating_dict['options'],
                value=fig_rating_dict['value'],
                clearable=False,
            ),
            dcc.Graph(
                id='fig-rating',
                figure=fig_rating
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Label(
                "First Collab"
            ),
            DataTable(
                id='first-collab-table',
                columns=first_collab_table_columns,
                data=first_collab_table_data,
            )
        ]),
        dbc.Col([
            dcc.Graph(
                id='fig-first-collab',
                figure=fig_first_collab
            )
        ])
    ]),
])

# Update all charts except rating figure (due to user interaction)
@app.callback([
    Output('live-update-text-user', 'children'),
    Output('speciality-table', 'data'),
    Output('speciality-table', 'columns'),
    Output('fig-speciality', 'figure'),
    Output('rating-table', 'data'),
    Output('rating-table', 'columns'),
    Output('first-collab-table', 'data'),
    Output('first-collab-table', 'columns'),
    Output('fig-first-collab', 'figure'),
],  Input('interval-component-user', 'n_intervals'))
def update_user_summary(n):
    data = get_form_data()

    current_time = get_live_update()

    speciality_table_data, speciality_table_columns, fig_speciality = generate_speciality_table(data)

    rating_table_data, rating_table_columns, fig_rating_dict = generate_ratings(data)

    first_collab_table_data, first_collab_table_columns, fig_first_collab = generate_first_collab_table(data)

    return current_time, \
           speciality_table_data, speciality_table_columns, fig_speciality, \
           rating_table_data, rating_table_columns, \
           first_collab_table_data, first_collab_table_columns, fig_first_collab


@app.callback(
    Output("fig-rating", "figure"),
    [Input("fig-rating-dropdown", "value")])
def update_bar_chart(value):
    data = get_form_data()

    rating_table_data, rating_table_columns, fig_rating_dict = generate_ratings(data)

    fig = generate_ratings_fig(fig_rating_dict['data'], value)

    fig.update_layout(
        title_text="Rating vs " + value
    )
    fig.update_yaxes(title_text="Frequency")

    return fig