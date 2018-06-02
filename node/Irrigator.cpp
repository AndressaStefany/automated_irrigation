
#include "Arduino.h"
#include "Irrigator.h"

void Irrigator::init(int v)
{
  verbose_mode= v;
  if(verbose_mode)
    Serial.begin(115200);
    
  pinMode(SOL, OUTPUT);
  digitalWrite(SOL, LOW);
  
  Wire.begin(SDA,SCL);
  ads.setGain(GAIN_ONE);
  ads.begin();
  
  server.begin();
  server.setNoDelay(true);
  if(verbose_mode) Serial.println("Server started");
}

void Irrigator::do_loop()
{
  client = server.available();
  if(!client)
  {
    do_irrigation();
    if(millis()-t1>1000) // send sensors data
    {
      if(verbose_mode) Serial.println("Waiting client");
      get_sensors_data();
      t1= millis();
    }
  }
  else
  {
    if(verbose_mode) Serial.println("Client connected");
    max_delay= 0;
    while(!client.available() && max_delay<=500){
      delay(1);
      max_delay++;
    }
    if(max_delay < 500)
    {
      //TODO Receber dados de modo anterior e tempo do rasp
      
      if(verbose_mode) Serial.println("Available");
      client.setNoDelay(true);
      t1= 0;
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
      client.flush();
    }
  }
}

void Irrigator::process_mode()
{
  if(buff[0] == 'o' && buff[1] == 'k')
    return;
  if(buff[0] == 127)
  {
    unsigned short aux;
    memcpy(&aux,&buff[1],2);
    minuto_atual= aux;
    if(verbose_mode)
    {
      Serial.print("Sync time ");
      Serial.println(minuto_atual);
    }
    return;
  }
  //Serial.print("Tamanho: ");
  //Serial.println(len);
  modo= buff[0];
  if(modo == 1)
  {
    memcpy(&minuto_irrigar,&buff[1],2);
    memcpy(&intervalo_irrigar,&buff[3],2);

    if(verbose_mode)
    {
      Serial.print("Modo 1 ");
      Serial.print(minuto_irrigar);
      Serial.print(" ");
      Serial.print(intervalo_irrigar);
    }
  }
  else if(modo == 2)
  {
    memcpy(&hum_min,&buff[1],2);
    memcpy(&hum_max,&buff[3],2);

    if(verbose_mode)
    {
      Serial.println("Modo 2");
      Serial.print(hum_min);
      Serial.print(" ");
      Serial.print(hum_max);
    }
  }
  else if(modo == 3)
  {
    memcpy(&hum_min,&buff[1],2);
    memcpy(&hum_max,&buff[3],2);

    if(verbose_mode)
    {
      Serial.println("Modo 3");
      Serial.print(hum_min);
      Serial.print(" ");
      Serial.print(hum_max); 
    }
  }
  else if(modo == 4)
  {
    memcpy(&temp_min,&buff[1],2);
    memcpy(&temp_max,&buff[3],2);

    if(verbose_mode)
    {
      Serial.println("Modo 4");
      Serial.print(temp_min);
      Serial.print(" ");
      Serial.print(temp_max);
    }
  }
  else if(modo == 5)
  {
    memcpy(&temp_max,&buff[1],2);
    memcpy(&intervalo_irrigar,&buff[3],2);

    if(verbose_mode)
    {
      Serial.println("Modo 5");
      Serial.print(temp_max);
      Serial.print(" ");
      Serial.print(intervalo_irrigar); 
    }
  }
  else if(modo == 6)
  {
    len= client.read((uint8_t*)&buff[5], 4);

    memcpy(&temp_min,&buff[1],2);
    memcpy(&temp_max,&buff[3],2);
    memcpy(&hum_min,&buff[5],2);
    memcpy(&hum_max,&buff[7],2);

    if(verbose_mode)
    {
      Serial.println("Modo 6");
      Serial.print(temp_min);
      Serial.print(" ");
      Serial.print(temp_max);
      Serial.print(" ");
      Serial.print(hum_min);
      Serial.print(" ");
      Serial.print(hum_max); 
    }
  }
  if(verbose_mode) Serial.println("");
  client.flush();
  for(int i=0; i<10; i++)
    buff[i]= 0;
}

void Irrigator::get_sensors_data()
{
  adc=0;
  for(int i=0; i<10; i++)
    adc+= ads.readADC_SingleEnded(2);
  adc/=10;
  
  float vadc= adc*ads_bit_Voltage;
  float i= (3.3-vadc)/9860.0;
  //Serial.print("S1 : "); Serial.print(adc*ads_bit_Voltage);
  //Serial.println("");
  
  //temperature = (float)adc/(MAX_ADC-adc)*9860;
  temperature = vadc/i;
  temperature = temperature/10000;
  temperature = log(temperature); // ln(R/Ro)
  temperature /= 3977;                   // 1/B * ln(R/Ro)
  temperature += 1.0/(25 + 273.15); // + (1/To)
  temperature = 1.0/temperature;                 // Inverte o valor
  temperature -= 273.15;                         // Converte para Celsius

  adc=0;
  for(int i=0; i<10; i++)
    adc+= ads.readADC_SingleEnded(3);
  adc/=10;

  vadc= adc*ads_bit_Voltage;
  i= (3.3-vadc)/9860.0;
  //Serial.println(vadc);
  humidity= i/vadc*10E6; // micro condutancia

  //Serial.print("S2 : "); Serial.print(adc*ads_bit_Voltage);
  //Serial.println("");


  if(verbose_mode)
  {
    Serial.print("Temperatura ");
    Serial.print(temperature);
    Serial.print(" Umidade ");
    Serial.println(humidity);
  
    Serial.print("Tempo agora : ");
    Serial.println(minuto_atual); 
  }
}

void Irrigator::do_irrigation()
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
      digitalWrite(SOL, HIGH);
    }
    if(humidity>hum_max)
    {
      digitalWrite(SOL, LOW);
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
      digitalWrite(SOL, HIGH);
    }
    if(temperature<temp_min)
    {
      digitalWrite(SOL, LOW);
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
