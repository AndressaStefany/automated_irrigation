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
int estado= LOW, max_delay= 0, len;
unsigned short hora, duracao;

void process_mode()
{
  //Serial.print(buff);
  Serial.print("Tamanho: ");
  Serial.println(len);
  if(buff[0] == 1)
  {
    Serial.print("Modo 1 ");
    hora= *((unsigned short*)&buff[1]); // buff[2]+(buff[1]<<8);
    duracao= *((unsigned short*)&buff[3]);//buff[4]+(buff[3]<<8);

    Serial.print(hora);
    Serial.print(" ");
    Serial.print(duracao);
  }
  else if(buff[0] == 2)
  {
    Serial.println("Modo 2");
  }
  else if(buff[0] == 3)
  {
    Serial.println("Modo 3");
  }
  else if(buff[0] == 4)
  {
    Serial.println("Modo 4");
  }
  else if(buff[0] == 5)
  {
    Serial.println("Modo 5");
  }
  else if(buff[0] == 6)
  {
    Serial.println("Modo 6");
  }
  Serial.println("");
  client.flush();
  for(int i=0; i<5; i++)
    buff[i]= 0;
}

void get_sensors_data()
{
  Serial.print("Temperatura ");
  Serial.print(temperature);
  Serial.print(" Umidade ");
  Serial.println(humidity);
  temperature+=0.125;
  humidity+=0.125;
}

void setup()
{
  pinMode(D1, OUTPUT);
  digitalWrite(D1, HIGH);
  
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
          unsigned char* ptr_temp= (unsigned char *)&temperature;
          unsigned char* ptr_umi= (unsigned char *)&humidity;
          for(int i=0; i<4; i++)
          {
            buff[i]= int(ptr_temp[i]);
            buff[i+4]= int(ptr_umi[i]); 
          }
          client.write((uint8_t*)&buff[0], 8);
          client.flush();
          t1= millis();
        }
        len= client.read((uint8_t*)&buff[0], 5);
        if(len>0) // process received data
        {
          process_mode();
        }
        
        delay(20);
      }
    }
  }
}
