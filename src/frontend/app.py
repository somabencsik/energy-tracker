from datetime import datetime, timedelta

from dash import (
    Dash, html, Output, Input, State, callback, dcc, dash_table, no_update
)
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
    dcc.Checklist(
        id="evaluate-indexes",
        options=[
            "Close Prices",
            "Min/Max/AVG",
            "Daily Change %",
            "Moving Average 7",
            "Moving Average 30"
        ],
        inline=True
    ),
    html.Div(id="table-indexes"),
    html.Div(id="error-div")
]

@callback(
    Output("energy-dropdown", "options"),
    Input("dropdown-div", "children")
)
def get_energies(_):
    response = requests.get("http://backend:8080/energies")
    if response.status_code != 200:
        return no_update
    
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
        return no_update

    return go.Figure([
        go.Scatter(
            x=[date for date in response.json()["rates"]],
            y=[
                rate[symbol]["close"]
                for _, rate in response.json()["rates"].items()
            ]
        )
    ])


@callback(
    Output("table-indexes", "children"),
    Input("evaluate-indexes", "value"),
    State("base-graph", "figure"),
    prevent_initial_call=True
)
def evaluate_indexes(indexes: list[str], figure):
    indexes_functions = {
        "Close Prices": get_close_prices,
        "Min/Max/AVG": get_min_max_avg,
        "Daily Change %": get_daily_changes,
        "Moving Average 7": get_ma7,
        "Moving Average 30": get_ma30
    }

    if len(figure["data"]) == 0:
        return no_update

    x_data = figure["data"][0]["x"]
    y_data = figure["data"][0]["y"]

    children = []
    for index in indexes:
        children.append(indexes_functions[index](x_data, y_data))

    return children


def get_close_prices(x_data: list[float], y_data: list[float]):
    table = dash_table.DataTable(
        id="close-prices-table",
        data=[{"Date": x, "Close Price": y} for x, y in zip(x_data, y_data)]
    )
    return table


def get_min_max_avg(x_data: list[float], y_data: list[float]):
    min_value = min(y_data)
    min_value_date = x_data[y_data.index(min_value)]
    max_value = max(y_data)
    max_value_date = x_data[y_data.index(max_value)]
    sum_value = sum(y_data) / len(y_data)

    table = dash_table.DataTable(
        id="min-max-avg-table",
        data=[{
            "Min value": f"{min_value} ({min_value_date})",
            "Max value": f"{max_value} ({max_value_date})",
            "Average value": sum_value
        }]
    )
    
    return table
    
    
def get_daily_changes(x_data: list[float], y_data: list[float]):
    data = [{"Date": x_data[0], "Daily Change %": "-"}]
    daily_changes = [
        {
            "Date": x_data[i + 1],
            "Daily Change %": f"{(y - y_data[i]) / y_data[i] * 100}%"
        }
        for i, y in enumerate(y_data[1:])
    ]
    data += daily_changes
    table = dash_table.DataTable(id="daily-changes-table", data=data)
    return table


def moving_average(values: list[float], window: int) -> list[float]:
    if len(values) < window:
        return []
    ma = []
    for i in range(len(values)):
        if i < window - 1:
            ma.append(None)
            continue
        ma.append(round(sum(values[i - window + 1 : i+1]) / window))

    return ma


def get_ma7(x_data: list[float], y_data: list[float]):
    averages = moving_average(y_data, 7)
    averages = [a if a is not None else "-" for a in averages]
    table = dash_table.DataTable(
        id="ma7-table",
        data=[{"Date": x_data[i], "Moving Average": a} for i, a in enumerate(averages)]
    )
    return table


def get_ma30(x_data: list[float], y_data: list[float]):
    averages = moving_average(y_data, 30)
    averages = [a if a is not None else "-" for a in averages]
    table = dash_table.DataTable(
        id="ma30-table",
        data=[{"Date": x_data[i], "Moving Average": a} for i, a in enumerate(averages)]
    )
    return table
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
