#include <ESP8266WiFi.h>
#include "Adafruit_ADS1015.h"

class Irrigator
{
  // Sensors 
  Adafruit_ADS1115 ads;
  float temperature= 0, humidity= 0;
  const int SDA, SCL;
  const float ads_bit_Voltage = (4.096*2)/(65535);

  // Irrigation modes
  unsigned short modo, minuto_irrigar, intervalo_irrigar, temp_min, temp_max, hum_min, hum_max;
  const int SOL;
  int estado= LOW, max_delay= 0, len= 0;
  float minuto_atual= 0, adc= 0, sync_min= 0;

  // Communication
  WiFiServer server;
  WiFiClient client;
  char buff[10];

  // Timestamp
  int dt, lt;
  double t1= 0;

  int verbose_mode= 1;
public:
  Irrigator(int port, int sda, int scl, int sol) : server(port), ads(0x48), SDA(sda), SCL(scl), SOL(sol) {}
  void init(int v);
  void process_mode();
  void get_sensors_data();
  void do_irrigation();
  void do_loop();
};
