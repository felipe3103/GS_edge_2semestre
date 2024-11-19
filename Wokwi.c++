#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>

// Configurações do Wi-Fi
const char* ssid = "Wokwi-GUEST";  // Nome da rede Wi-Fi
const char* password = "";         // Senha da rede (Wokwi-GUEST não requer senha)

// Configurações do broker MQTT (FIWARE)
const char* mqtt_server = "871899c0f1664ed98672180cb901ec01.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_topic = "/agriculture/solar/data";
const char* mqtt_user = "GS_edge";  // Substitua pelo seu usuário MQTT
const char* mqtt_pass = "Fetica31@";   // Substitua pela sua senha MQTT

// Configurações do sensor DHT
#define DHTPIN 4       // Pino onde o sensor está conectado
#define DHTTYPE DHT22  // Tipo do sensor (DHT11 ou DHT22)
DHT dht(DHTPIN, DHTTYPE);

// Cliente Wi-Fi e MQTT
WiFiClientSecure espClient;  // Suporte a TLS
PubSubClient client(espClient);

// Função para conectar ao Wi-Fi
void connectWiFi() {
  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) { // Máximo de 20 tentativas (~20 segundos)
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi conectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar ao Wi-Fi. Reiniciando...");
    ESP.restart(); // Reinicia o ESP para tentar novamente
  }
}

// Função para conectar ao broker MQTT
void connectMQTT() {
  while (!client.connected()) {
    Serial.println("Conectando ao broker MQTT...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_pass)) { // Inclui usuário e senha
      Serial.println("Conectado ao MQTT!");
    } else {
      Serial.print("Falha na conexão. Código de erro: ");
      Serial.println(client.state());
      delay(2000); // Aguarda antes de tentar novamente
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  connectWiFi();

  // Configurações para TLS (inseguro, apenas para testes)
  espClient.setInsecure(); // Remove verificação de certificado

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }

  // Captura os dados do sensor
  float temperature = dht.readTemperature(); // Em graus Celsius
  float humidity = dht.readHumidity();       // Em porcentagem
  int luminosity = analogRead(34);           // Exemplo: leitura de um LDR no pino 34

  // Verifica se a leitura dos sensores está válida
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Erro ao ler o sensor DHT!");
    return;
  }

  // Monta o payload JSON
  String payload = "{";
  payload += "\"temperature\": " + String(temperature) + ",";
  payload += "\"humidity\": " + String(humidity) + ",";
  payload += "\"luminosity\": " + String(luminosity);
  payload += "}";

  // Publica no tópico MQTT
  if (client.publish(mqtt_topic, payload.c_str())) {
    Serial.println("Dados publicados com sucesso: " + payload);
  } else {
    Serial.println("Erro ao publicar os dados.");
  }

  delay(5000); // Aguarda 5 segundos antes de enviar novamente
}
