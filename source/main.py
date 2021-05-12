import requests
import io
import datetime
import dash  # (version 1.12.0)
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import traceback

def load_data():
    url = "https://telemetry-query-{placeholder:workspaceid}.platform.quix.ai/parameters/data"
    token = "{placeholder:token}"
    head = {'Authorization': 'Bearer {}'.format(token), 'Accept': "application/csv"}
    payload = {
        'numericParameters': [
            {
                'parameterName': 'Speed',
                'aggregationType': 'None'
            }
        ],
        'streamIds': [
        ],
        'groupBy': []
    }

    response = requests.post(url, headers=head, json=payload)

    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))

    if df.size > 0:
        # We convert nanoseconds epoch to datetime for better readability.
        df["Timestamp"] = df["Timestamp"].apply(lambda x: str(datetime.datetime.fromtimestamp(x / 1000000000)))
    return df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Test dashboard'),
    html.Div(children='''
        Car speed
    '''),
    dcc.Graph(
        id='graph',

    ),
    dcc.Interval(
        id='interval_component',
        interval=5000,
        n_intervals=0,
        
    )
])


@app.callback(Output('graph', 'figure'), [Input('interval_component', 'n_intervals')])
def update_data(n_intervals):
    try:
        data = load_data()

        scatter = go.Scatter(x=data["Timestamp"].to_numpy(), y=data["Speed"].to_numpy())

        # tuple is (dict of new data, target trace index, number of points to keep)
        fig = go.Figure(
            data=[scatter]
        )
        return fig

    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
