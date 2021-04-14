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
    url = "https://telemetry-query-quix-testdavid.platform.quix.ai/parameters/data"
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qVTBRVE01TmtJNVJqSTNOVEpFUlVSRFF6WXdRVFF4TjBSRk56SkNNekpFUWpBNFFqazBSUSJ9.eyJodHRwczovL3F1aXguYWkvcm9sZXMiOiJhZG1pbiBRdWl4QWRtaW4iLCJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeCIsImlzcyI6Imh0dHBzOi8vbG9naWNhbC1wbGF0Zm9ybS5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8YmNmZmZhNjItMTVhNC00OWVjLTk5YTQtZDUyOTk5MGQ3YjUxIiwiYXVkIjpbInF1aXgiLCJodHRwczovL2xvZ2ljYWwtcGxhdGZvcm0uZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYxODM5MzQ5NSwiZXhwIjoxNjIwOTg1NDk1LCJhenAiOiIwem1XZkpka2l1R1BpSld5cFNDQThyS2FWdmZQREtMSSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.KnQv8w2o7nPifoPgLZmgwWLsceIgkRu0NmDQLefDIfgq6yeHa1yaBQaoUH4qdmUBdhVx5cJZ5Usq4gzM3KYcDfDBo5DDctOMHG4j7LQZTEzV4q1OF_r0IENgm3qAh5TpRSX4RfU-N17jyE4XoSH_IsyiPjla7gUS3mG0lGwGqFOpU9Ons1q9S_22OQemcXbj9rR39DboII05oZc2ylfrZHTB9aiaId-XDcptGJkGD5-qjliabIe-KwfqET9afqR17c-6iW79MjqGKEyBpfHFTdUsJjYMvXqWTiCiaohIDyr0V5GBdSA55ygUZF_YkToO2TIXDdw3LPKpnQOZbUza2Q"
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

    panda_frame = pd.read_csv(io.StringIO(response.content.decode('utf-8')))

    if panda_frame.size > 0:
        # We convert nanoseconds epoch to datetime for better readability.
        panda_frame["Timestamp"] = panda_frame["Timestamp"].apply(lambda x: str(datetime.datetime.fromtimestamp(x / 1000000000)))
    return panda_frame

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
