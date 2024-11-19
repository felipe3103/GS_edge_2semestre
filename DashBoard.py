import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import json
import time

### Configurações MQTT
broker = "cyannomad-rryt2c.a03.euc1.aws.hivemq.cloud"
port = 8883
topic = "/agriculture/solar/data"
username = "GS_edge"
password = "Fetica31@"

# Dados para gráficos
timestamps = []
temperature_data = []
humidity_data = []
luminosity_data = []


# Callback para conexão ao broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT!")
        client.subscribe(topic)
    else:
        print(f"Falha na conexão. Código de erro: {rc}")


# Callback para receber mensagens MQTT
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        current_time = time.strftime("%H:%M:%S")

        # Adiciona os dados recebidos
        timestamps.append(current_time)
        temperature_data.append(data["temperature"])
        humidity_data.append(data["humidity"])
        luminosity_data.append(data["luminosity"])

        # Limita o histórico a 10 registros
        if len(timestamps) > 10:
            timestamps.pop(0)
            temperature_data.pop(0)
            humidity_data.pop(0)
            luminosity_data.pop(0)

        update_graphs()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")


# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(username, password)
client.tls_set()  # Configuração para conexão segura (TLS)
client.on_connect = on_connect
client.on_message = on_message

# Conectar ao broker
try:
    client.connect(broker, port, 60)
except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {e}")


# Atualiza os gráficos no dashboard
def update_graphs():
    ax_temp.clear()
    ax_hum.clear()
    ax_lum.clear()

    ax_temp.plot(timestamps, temperature_data, marker='o', label='Temperatura (°C)')
    ax_temp.set_title("Temperatura")
    ax_temp.set_ylabel("°C")
    ax_temp.set_xticks(timestamps)
    ax_temp.set_xticklabels(timestamps, rotation=45)
    ax_temp.legend()

    ax_hum.plot(timestamps, humidity_data, marker='o', label='Umidade (%)', color='green')
    ax_hum.set_title("Umidade")
    ax_hum.set_ylabel("%")
    ax_hum.set_xticks(timestamps)
    ax_hum.set_xticklabels(timestamps, rotation=45)
    ax_hum.legend()

    ax_lum.plot(timestamps, luminosity_data, marker='o', label='Luminosidade', color='orange')
    ax_lum.set_title("Luminosidade")
    ax_lum.set_ylabel("Intensidade")
    ax_lum.set_xticks(timestamps)
    ax_lum.set_xticklabels(timestamps, rotation=45)
    ax_lum.legend()

    canvas.draw()


# Interface gráfica
def create_dashboard():
    global ax_temp, ax_hum, ax_lum, canvas

    root = tk.Tk()
    root.title("Dashboard - Dados do Sensor")
    root.geometry("900x600")

    # Título
    ttk.Label(root, text="Dashboard - Sensores", font=("Helvetica", 16)).pack(pady=10)

    # Configuração do gráfico
    fig, (ax_temp, ax_hum, ax_lum) = plt.subplots(3, 1, figsize=(8, 6))
    fig.tight_layout(pad=3.0)

    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Iniciar o loop MQTT em paralelo
    root.after(100, lambda: client.loop_start())

    # Rodar o loop principal do Tkinter
    root.mainloop()


# Iniciar o dashboard
create_dashboard()
