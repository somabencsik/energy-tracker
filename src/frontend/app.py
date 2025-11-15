from dash import Dash, html, Output, Input, callback
import requests


app = Dash()

app.layout = [
    html.H1(children="Frontend"),
    html.Button("Check backend connection", id="btn_database", n_clicks=0),
    html.Div(id="backend-response")
]

@callback(
    Output("backend-response", "children"),
    Input("btn_database", "n_clicks"),
    prevent_initial_call=True
)
def check_database(_):
    response = requests.get("http://backend:8080/")
    if response.status_code != 200:
        return "Failed to connect backend"
    return response.text


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
