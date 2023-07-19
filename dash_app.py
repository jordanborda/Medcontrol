import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Carga datos de ejemplo
data = pd.read_csv("datos_med.csv")

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id="dropdown",
        options=[
            {"label": "Género", "value": "genero"},
            {"label": "Raza", "value": "raza"},
            {"label": "Nivel Socioeconómico", "value": "nivel_socioeconomico"}
        ],
        value="genero"
    ),
    dcc.Graph(id="bar_chart"),
    dcc.Graph(id="scatter_chart")
])

@app.callback(
    Output("bar_chart", "figure"),
    [Input("dropdown", "value")]
)
def update_bar_chart(value):
    fig = px.bar(data, x=value, y="satisfaccion_paciente", color=value)
    return fig

@app.callback(
    Output("scatter_chart", "figure"),
    [Input("dropdown", "value")]
)
def update_scatter_chart(value):
    fig = px.scatter(data, x="edad", y="tasa_exito_tratamiento", color=value)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
