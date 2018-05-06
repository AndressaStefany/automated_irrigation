#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>        // Include the mDNS library

const char* ssid     = "Ramos";
const char* password = "D_yP7xuC6";

WiFiServer server(5780);

char buff[3];
uint8_t x= 0;
int estado= LOW;

void setup() {
  buff[2]= '\0';
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
  Serial.println("Server started");
}


void loop() {
  // put your main code here, to run repeatedly:
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
  Serial.println("new client");
  int max_delay= 0;
  while(!client.available() && max_delay<=500){
    delay(1);
    max_delay++;
  }
  if(max_delay < 500)
  {
    Serial.println("Disponivel");
    client.setNoDelay(true);
    double t1= 0;
    while(client.connected())
    {
      if(millis()-t1>500)
      {
        Serial.println(x);
        client.write(x);
        client.flush();
        x++;
        t1= millis();
      }
      
      int len= client.read((uint8_t*)&buff[0], 2);
      if(len>0)
      {
        Serial.print(buff);
        Serial.print(" ");
        Serial.println(len);
        if(buff[0] == 'o')
        {
          Serial.println("Dados sensor recebido");
        }
        else if(buff[0] == 'k')
        {
          estado= buff[1]-'0';
          digitalWrite(D1, estado);
        }
        client.flush();
        buff[0]= 0;
        buff[1]= 0;
      }
      delay(20);
    }
  }
}
