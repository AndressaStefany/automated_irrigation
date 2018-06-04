
#include "Arduino.h"
#include "Irrigator.h"

void Irrigator::init(int v)
{
  verbose_mode= v;
  if(verbose_mode)
    Serial.begin(921600);
    
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
    if(millis()-elapsed_time>sensor_interval) // send sensors data
    {
      if(verbose_mode) Serial.println("Waiting client");
      get_sensors_data();
      elapsed_time= millis();
    }
    delay(20);
  }
  else
  {
    if(verbose_mode) Serial.println("Client connected");
    max_delay= 0;
    while(!client.available() && max_delay<=max_wait_client){
      delay(1);
      max_delay++;
    }
    if(max_delay < max_wait_client)
    {
      if(verbose_mode) Serial.println("Available");
      client.setNoDelay(true);
      elapsed_time= 0;
      while(client.connected())
      {
        if(millis()-elapsed_time>sensor_interval) // send sensors data
        {
          get_sensors_data();
          // pack values into buffer
          memcpy(&buff[0], &temperature, 4);
          memcpy(&buff[4], &humidity, 4);
          client.write((uint8_t*)&buff[0], 8);
          client.flush();
          elapsed_time= millis();
        }
        len= client.read((uint8_t*)&buff[0], 5);
        if(len==5) // process received data
        {
          process_mode();
        }
        else
        {
          if(verbose_mode)
          {
            Serial.println("Bad formad packge");
            for(i=0; i<len; i++)
              Serial.println(int(buff[i])); 
          }
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
    sync_min= aux/10.0-fmod(millis()/60000.0,1440);
    if(verbose_mode)
    {
      Serial.print("Sync time ");
      Serial.println(minuto_atual);
    }
    return;
  }
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
    digitalWrite(SOL, LOW);
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
    digitalWrite(SOL, LOW);
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
    digitalWrite(SOL, LOW);
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
    digitalWrite(SOL, LOW);
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
    digitalWrite(SOL, LOW);
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
    digitalWrite(SOL, LOW);
  }
  if(verbose_mode) Serial.println("");
  client.flush();
  for(i=0; i<10; i++)
    buff[i]= 0;
}

void Irrigator::get_sensors_data()
{
  adc=0;
  for(i=0; i<10; i++)
    adc+= ads.readADC_SingleEnded(2);
  adc/=10;
  
  //float vadc= adc*ads_bit_Voltage;
  //float i= (3.3-vadc)/9860.0;
  if(verbose_mode>1) { Serial.print("S1 : "); Serial.println(adc*ads_bit_Voltage); }
  //Serial.println("");
  
  temperature = (float)adc/(MAX_ADC-adc)*9860;
  //temperature = vadc/i;
  temperature = temperature/10000;
  temperature = log(temperature); // ln(R/Ro)
  temperature /= 3977;                   // 1/B * ln(R/Ro)
  temperature += 1.0/(25 + 273.15); // + (1/To)
  temperature = 1.0/temperature;                 // Inverte o valor
  temperature -= 273.15;                         // Converte para Celsius

  adc=0;
  for(i=0; i<10; i++)
    adc+= ads.readADC_SingleEnded(3);
  adc/=10;

//  vadc= adc*ads_bit_Voltage;
//  i= (3.3-vadc)/9860.0;
  //Serial.println(vadc);
  //humidity= i/vadc*10E6; // micro condutancia
  humidity = (MAX_ADC-adc)/(float)adc*1000;

  if(verbose_mode>1) {Serial.print("S2 : "); Serial.println(adc*ads_bit_Voltage);}
  //Serial.println("");


  if(verbose_mode)
  {
    Serial.print("Temperatura ");
    Serial.print(temperature);
    Serial.print(" Umidade ");
    Serial.println(humidity);
  
    Serial.print("Tempo agora : ");
    Serial.print(minuto_atual);
    Serial.print(" -- ");
    
    Serial.print(int(minuto_atual/60));
    Serial.print(":");
    Serial.print(int(fmod(minuto_atual,60))); 
    Serial.print(":");
    Serial.print((minuto_atual-int(minuto_atual))*60 ); 
    Serial.println("");
  }
}

void Irrigator::do_irrigation()
{
  minuto_atual= fmod(millis()/60000.0,1440)+sync_min;
  if(modo == 1)
  {
    if(minuto_atual>minuto_irrigar && minuto_atual<minuto_irrigar+intervalo_irrigar)
    {
      digitalWrite(SOL, HIGH);
    }
    else digitalWrite(SOL, LOW);
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
    static bool m3= false;
    if(minuto_atual>minuto_irrigar && minuto_atual<minuto_irrigar+intervalo_irrigar)
    {
      digitalWrite(SOL, HIGH);
    }
    else
    {
      digitalWrite(SOL, LOW);
      m3= false;
    }
    if(humidity<hum_min && !m3)
    {
       m3= true;
       minuto_irrigar= minuto_atual;
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
    static bool m5= false;
    if(minuto_atual>minuto_irrigar && minuto_atual<minuto_irrigar+intervalo_irrigar)
    {
       digitalWrite(SOL, HIGH);
    }
    else
    {
      digitalWrite(SOL, LOW);
      m5= false;
    }
    if(temperature>temp_max && !m5)
    {
      m5= true;
      minuto_irrigar= minuto_atual;
    }
  }
  else if(modo == 6)
  {
  }
}
