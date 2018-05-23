#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>        // Include the mDNS library

const char* ssid     = "Ramos";
const char* password = "D_yP7xuC6";

//const char* ssid     = "Ramos2";
//const char* password = "iwsmv_73876";

WiFiServer server(5780);
WiFiClient client;

char buff[10];
float temperature= 0, humidity= 0;
int estado= LOW, max_delay= 0, len= 0;
float minuto_atual;
unsigned short modo, minuto_irrigar, intervalo_irrigar, temp_min, temp_max, hum_min, hum_max;

#define S_HUM D1
#define S_TEMP D2
#define A_SOL D3

void process_mode()
{
  Serial.print("Tamanho: ");
  Serial.println(len);
  modo= buff[0];
  if(modo == 1)
  {
    Serial.print("Modo 1 ");
    memcpy(&minuto_irrigar,&buff[1],2);
    memcpy(&intervalo_irrigar,&buff[3],2);

    Serial.print(minuto_irrigar);
    Serial.print(" ");
    Serial.print(intervalo_irrigar);
  }
  else if(modo == 2)
  {
    Serial.println("Modo 2");
    memcpy(&hum_min,&buff[1],2);
    memcpy(&hum_max,&buff[3],2);

    Serial.print(hum_min);
    Serial.print(" ");
    Serial.print(hum_max);
  }
  else if(modo == 3)
  {
    Serial.println("Modo 3");
    memcpy(&hum_min,&buff[1],2);
    memcpy(&hum_max,&buff[3],2);

    Serial.print(hum_min);
    Serial.print(" ");
    Serial.print(hum_max);
  }
  else if(modo == 4)
  {
    Serial.println("Modo 4");
    memcpy(&temp_min,&buff[1],2);
    memcpy(&temp_max,&buff[3],2);

    Serial.print(temp_min);
    Serial.print(" ");
    Serial.print(temp_max);
  }
  else if(modo == 5)
  {
    Serial.println("Modo 5");
    memcpy(&temp_max,&buff[1],2);
    memcpy(&intervalo_irrigar,&buff[3],2);

    Serial.print(temp_max);
    Serial.print(" ");
    Serial.print(intervalo_irrigar);
  }
  else if(modo == 6)
  {
    len= client.read((uint8_t*)&buff[5], 4);
    Serial.println("Modo 6");

    memcpy(&temp_min,&buff[1],2);
    memcpy(&temp_max,&buff[3],2);
    memcpy(&hum_min,&buff[5],2);
    memcpy(&hum_max,&buff[7],2);

    Serial.print(temp_min);
    Serial.print(" ");
    Serial.print(temp_max);
    Serial.print(" ");
    Serial.print(hum_min);
    Serial.print(" ");
    Serial.print(hum_max);
  }
  Serial.println("");
  client.flush();
  for(int i=0; i<10; i++)
    buff[i]= 0;
}

float adc= 0;

void get_sensors_data()
{
  digitalWrite(S_TEMP, HIGH);
  digitalWrite(S_HUM, LOW);
  delay(20);
  adc=0;
  for(int i=0; i<10; i++)
    adc+= analogRead(A0);
  adc/=10;
  
  temperature= (float)adc/(1023.0-adc)*9860;
  temperature= temperature/10000;
  temperature = log(temperature); // ln(R/Ro)
  temperature /= 3977;                   // 1/B * ln(R/Ro)
  temperature += 1.0 / (25 + 273.15); // + (1/To)
  temperature = 1.0 / temperature;                 // Inverte o valor
  temperature -= 273.15;                         // Converte para Celsius

  digitalWrite(S_TEMP, LOW);
  digitalWrite(S_HUM, HIGH);
  delay(20);
  adc=0;
  for(int i=0; i<10; i++)
    adc+= analogRead(A0);
  adc/=10;

  humidity= 10023.0/(float)adc;

  digitalWrite(S_TEMP, LOW);
  digitalWrite(S_HUM, LOW);  
  
  Serial.print("Temperatura ");
  Serial.print(temperature);
  Serial.print(" Umidade ");
  Serial.println(humidity);

  Serial.print("Tempo agora : ");
  Serial.println(minuto_atual);
}

int dt, lt;
void do_irrigation()
{
  dt= millis()-lt;
  lt= millis();
  minuto_atual+=(dt/1000.0)/60.0;
  if(modo == 1)
  {
    if((int(minuto_atual)-minuto_irrigar)%intervalo_irrigar==0)
    {
      //irrigar
    }
  }
  else if(modo == 2)
  {
    if(humidity<hum_min)
    {
      digitalWrite(A_SOL, HIGH);
    }
    if(humidity>hum_max)
    {
      digitalWrite(A_SOL, LOW);
    }
  }
  else if(modo == 3)
  {
    if(humidity<hum_min)
    {
      //irrigar pelo tempo intervalo_irrigar
    }
  }
  else if(modo == 4)
  {
    if(temperature>temp_max)
    {
      digitalWrite(A_SOL, HIGH);
    }
    if(temperature<temp_min)
    {
      digitalWrite(A_SOL, LOW);
    }
  }
  else if(modo == 5)
  {
    if(temperature>temp_max)
    {
      //irrigar pelo tempo intervalo_irrigar
    }
  }
  else if(modo == 6)
  {
    
  }
}

void setup()
{
  pinMode(S_TEMP, OUTPUT);
  pinMode(S_HUM, OUTPUT);
  pinMode(A_SOL, OUTPUT);
  digitalWrite(S_TEMP, LOW);
  digitalWrite(S_HUM, LOW);
  digitalWrite(A_SOL, LOW);
  
  Serial.begin(115200);
  delay(10);
  
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  IPAddress ip(192, 168, 0, 111); // where xx is the desired IP Address
  IPAddress gateway(192, 168, 0, 1); // set gateway to match your network
  Serial.print(F("Setting static ip to : "));
  Serial.println(ip);
  IPAddress subnet(255, 255, 255, 0); // set subnet mask to match your network
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  server.setNoDelay(true);
  Serial.println("Server started");
}


void loop()
{
  client = server.available();
  if(!client)
  {
    Serial.println("Waiting client");
    do_irrigation();
  }
  else
  {
    Serial.println("Client connected");
    max_delay= 0;
    while(!client.available() && max_delay<=500){
      delay(1);
      max_delay++;
    }
    if(max_delay < 500)
    {
      Serial.println("Available");
      client.setNoDelay(true);
      double t1= 0;
      while(client.connected())
      {
        if(millis()-t1>1000) // send sensors data
        {
          get_sensors_data();
          // pack values into buffer
          memcpy(&buff[0], &temperature, 4);
          memcpy(&buff[4], &humidity, 4);
          client.write((uint8_t*)&buff[0], 8);
          client.flush();
          t1= millis();
        }
        len= client.read((uint8_t*)&buff[0], 5);
        if(len>0) // process received data
        {
          process_mode();
        }
        do_irrigation();
        delay(20);
      }
    }
  }
}
