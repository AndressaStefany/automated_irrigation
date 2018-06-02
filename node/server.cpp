#include <ESP8266mDNS.h>  // Include the mDNS library
//#include <DNSServer.h>
#include "Irrigator.h"

const char* ssid     = "Ramos";
const char* password = "D_yP7xuC6";

//const char* ssid     = "Ramos2";
//const char* password = "iwsmv_73876";

#define AP 0

#define SDA D1
#define SCL D2
#define A_SOL D3
#define PORT 5780
#define MAX_ADC 26318

Irrigator node1(PORT, SDA, SCL, A_SOL);

void setup()
{
  pinMode(D0,OUTPUT);
  digitalWrite(D0,LOW);
  node1.init(1);
  
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  if(AP)
  {
    WiFi.mode(WIFI_AP);
    IPAddress apIP(192, 168, 1, 1);
    WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
    WiFi.softAP("irrigar", "1irrigar2"); 
  }
  else
  {
    WiFi.mode(WIFI_STA);
    IPAddress ip(192, 168, 0, 111); // where xx is the desired IP Address
    IPAddress gateway(192, 168, 0, 1); // set gateway to match your network
    Serial.print(F("Setting static ip to : "));
    Serial.println(ip);
    IPAddress subnet(255, 255, 255, 0); // set subnet mask to match your network
    WiFi.config(ip, gateway, subnet);
    WiFi.begin(ssid, password);
    WiFi.hostname("esp8266");
    
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    } 
  }

  if (MDNS.begin("esp8266")) {
    Serial.println("MDNS responder started");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop()
{
  node1.do_loop();
}
