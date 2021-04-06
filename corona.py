import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)

# Unpivot the data
date1 = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"], value_vars=date1,
                                 var_name="date", value_name="confirmed")

date2 = deaths.columns[4:]
total_deaths = deaths.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"], value_vars=date2,
                           var_name="date", value_name="death")

date3 = recovered.columns[4:]
total_recovered = recovered.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"], value_vars=date3,
                                 var_name="date", value_name="recovered")

# Merging data frames

covid_data = total_confirmed.merge(right=total_deaths, how="left",
                                   on=["Province/State", "Country/Region", "date", "Lat", "Long"])
covid_data = covid_data.merge(right=total_recovered, how="left",
                              on=["Province/State", "Country/Region", "date", "Lat", "Long"])

# converting date column from string to proper date format
covid_data["date"] = pd.to_datetime(covid_data["date"])

# check how many missing values naN
covid_data.isna().sum()

# Replace naN with 0
covid_data["recovered"] = covid_data["recovered"].fillna(0)

# create new column
covid_data["active"] = covid_data["confirmed"] - covid_data["death"] - covid_data["recovered"]

covid_data_1 = covid_data.groupby(["date"])[["confirmed", "death", "recovered", "active"]].sum().reset_index()

# create dictionary of list
covid_data_list = covid_data[['Country/Region', 'Lat', 'Long']]
dict_of_locations = covid_data_list.set_index('Country/Region')[['Lat', 'Long']].T.to_dict('dict')

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url("corona-logo-1.jpg"),
                     id="corona-image",
                     style={"height": "60px",
                            "width": "auto",
                            "margin-bottom": "25px"})

        ], className="one-third column"),

        html.Div([
            html.Div([
                html.H3("Covid-19", style={"margin-bottom": "0px", "color": "white"}),
                html.H5("Track Covid-19 Cases", style={"margin-bottom": "0px", "color": "white"})
            ])

        ], className="one-half column", id="title"),

        html.Div([
            html.H6("Last Updated: " + str(covid_data["date"].iloc[-1].strftime("%B %d, %Y")),
                    style={"color": "orange"})

        ], className="one-third column", id="title1")

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),


    html.Div([
        html.Div([
            html.P("Select Country:", className="fix_label", style={"color": "white"}),
            dcc.Dropdown(id="w_countries",
                         multi=False,
                         searchable=True,
                         value="US",
                         placeholder="Select Country",
                         options=[{"label": c, "value": c}
                                  for c in (covid_data["Country/Region"].unique())], className="dcc_compon"),
            html.P('New Cases: ' + '' + str(covid_data["date"].iloc[-1].strftime("%B %d, %Y")),
                   className="fix_label", style={"text-align": "center", "color": "white"}),
            dcc.Graph(id="confirmed", config={"displayModeBar": False}, className="dcc-compon",
                      style={"margin-top": '20px'}),

        ], className="create_container three columns"),


    ], className="row flex-display"),


], id="mainContainer", style={"display": "flex", "flex-direction": "column"})


@app.callback(Output('confirmed', 'figure'),
              [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(["date", "Country/Region"])[
        ["confirmed", "death", "recovered", "active"]].sum().reset_index()
    value_confirmed = covid_data_2[covid_data_2["Country/Region"] == w_countries]['confirmed'].iloc[-1] - \
                      covid_data_2[covid_data_2["Country/Region"] == w_countries]['confirmed'].iloc[-2]
    # delta_confirmed = covid_data_2[covid_data_2["Country/Region"] == w_countries]['confirmed'].iloc[-2] - \
    #                   covid_data_2[covid_data_2["Country/Region"] == w_countries]['confirmed'].iloc[-3]

    return {
        'data': [go.Indicator(
            mode='number',
            value=value_confirmed,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #        'font': {'size': 15}},
            number={'valueformat': ',',
                    'font': {'size': 20}},
            domain={'y': [0, 1], 'x': [0, 1]}
        )],

        'layout': go.Layout(
            title={'text': 'confirmed',
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,

        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)