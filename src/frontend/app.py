from datetime import datetime, timedelta

from dash import Dash, html, Output, Input, State, callback, dcc
import plotly.graph_objs as go
import requests


app = Dash()

app.layout = [
    html.H1(children="Check energy prices"),
    html.Div(id="dropdown-div", children=[
        dcc.Dropdown(options=[], id="energy-dropdown")
    ]),
    html.Div(children=[
        html.P("Timespan"),
        dcc.RadioItems(
            id="timespan",
            options=["1 Week", "1 Month", "3 Month", "6 Month", "1 Year"],
            value="1 Week",
            inline=True
        )
    ]),
    dcc.Graph(id="base-graph", figure=go.Figure()),
    html.Div(id="error-div")
]

@callback(
    Output("energy-dropdown", "options"),
    Input("dropdown-div", "children")
)
def get_energies(_):
    response = requests.get("http://backend:8080/energies")
    if response.status_code != 200:
        return ["ERROR"]
    
    energies = [
        f"{energy['name']}, {energy['symbol']}"
        for energy in response.json()["energies"]
    ]
    return energies


@callback(
    Output("base-graph", "figure"),
    [
        Input("energy-dropdown", "value"),
        Input("timespan", "value")
    ],
    prevent_initial_call=True
)
def get_selected_energy_value(energy: str, timespan: str):
    symbol = energy.split(",")[-1].strip()

    day_differences = {
        "1 Week": 7,
        "1 Month": 30,
        "3 Month": 90,
        "6 Month": 180,
        "1 Year": 365
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=day_differences[timespan])
    
    response = requests.get(
        f"http://backend:8080/energies/time?symbol={symbol}"
        f"&start_date={start_date.strftime('%Y-%m-%d')}"
        f"&end_date={end_date.strftime('%Y-%m-%d')}"
    )
    if response.status_code != 200:
        return go.Figure()

    return go.Figure([
        go.Scatter(
            x=[date for date in response.json()["rates"]],
            y=[
                rate[symbol]["close"]
                for _, rate in response.json()["rates"].items()
            ]
        )
    ])
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
