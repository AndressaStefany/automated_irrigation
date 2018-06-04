#include <ESP8266WiFi.h>
#include "Adafruit_ADS1015.h"

#define MAX_ADC 26318

class Irrigator
{
  // Sensors 
  Adafruit_ADS1115 ads;
  float temperature= 0, humidity= 0;
  const short SDA, SCL;
  const float ads_bit_Voltage = (4.096*2)/(65535);
  const short sensor_interval= 10000;

  // Irrigation modes
  unsigned short modo= 0, minuto_irrigar= 0, intervalo_irrigar= 0, temp_min= 0, temp_max= 0, hum_min= 0, hum_max= 0;
  const int SOL;
  int estado= LOW, max_delay= 0, len= 0;
  float minuto_atual= 0, adc= 0, sync_min= 0;

  // Communication
  WiFiServer server;
  WiFiClient client;
  char buff[10];
  const short max_wait_client= 500;

  // Timestamp
  double elapsed_time= 0;

  int verbose_mode= 1;
  int i= 0;
public:
  Irrigator(int port, int sda, int scl, int sol) : server(port), ads(0x48), SDA(sda), SCL(scl), SOL(sol) {}
  void init(int v);
  void process_mode();
  void get_sensors_data();
  void do_irrigation();
  void do_loop();
};
