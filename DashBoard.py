import dash
from dash import dcc, html
import plotly.graph_objs as go
from collections import deque
import paho.mqtt.client as mqtt
import json
import time

# Configuração do Dash
app = dash.Dash(__name__)
app.title = "Dashboard de Sensores"

# Armazenamento de dados
max_len = 20  # Quantidade máxima de dados armazenados
temperature_data = deque(maxlen=max_len)
humidity_data = deque(maxlen=max_len)
luminosity_data = deque(maxlen=max_len)
timestamps = deque(maxlen=max_len)

# Configuração do MQTT
MQTT_BROKER = "871899c0f1664ed98672180cb901ec01.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "/agriculture/solar/data"
MQTT_USER = "GS_edge"
MQTT_PASS = "Fetica31@"

# Configuração do cliente MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Erro ao conectar, código de retorno: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        temperature_data.append(payload["temperature"])
        humidity_data.append(payload["humidity"])
        luminosity_data.append(payload["luminosity"])
        timestamps.append(time.strftime('%H:%M:%S'))
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.tls_set()  # Conexão segura
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# Layout do Dash
app.layout = html.Div([
    html.H1("Dashboard de Sensores", style={"textAlign": "center"}),
    dcc.Graph(id="temperature-graph"),
    dcc.Graph(id="humidity-graph"),
    dcc.Graph(id="luminosity-graph"),
    dcc.Interval(
        id="update-interval",
        interval=5000,  # Atualiza a cada 5 segundos
        n_intervals=0
    )
])

# Callback para atualizar gráficos
@app.callback(
    [dash.dependencies.Output("temperature-graph", "figure"),
     dash.dependencies.Output("humidity-graph", "figure"),
     dash.dependencies.Output("luminosity-graph", "figure")],
    [dash.dependencies.Input("update-interval", "n_intervals")]
)
def update_graphs(n):
    # Gráfico de Temperatura
    temperature_fig = go.Figure()
    temperature_fig.add_trace(go.Scatter(
        x=list(timestamps),
        y=list(temperature_data),
        mode="lines+markers",
        name="Temperatura (°C)"
    ))
    temperature_fig.update_layout(title="Temperatura ao longo do tempo", xaxis_title="Tempo", yaxis_title="Temperatura (°C)")

    # Gráfico de Umidade
    humidity_fig = go.Figure()
    humidity_fig.add_trace(go.Scatter(
        x=list(timestamps),
        y=list(humidity_data),
        mode="lines+markers",
        name="Umidade (%)"
    ))
    humidity_fig.update_layout(title="Umidade ao longo do tempo", xaxis_title="Tempo", yaxis_title="Umidade (%)")

    # Gráfico de Luminosidade
    luminosity_fig = go.Figure()
    luminosity_fig.add_trace(go.Scatter(
        x=list(timestamps),
        y=list(luminosity_data),
        mode="lines+markers",
        name="Luminosidade"
    ))
    luminosity_fig.update_layout(title="Luminosidade ao longo do tempo", xaxis_title="Tempo", yaxis_title="Luminosidade")

    return temperature_fig, humidity_fig, luminosity_fig

if __name__ == "__main__":
    app.run_server(debug=True)
