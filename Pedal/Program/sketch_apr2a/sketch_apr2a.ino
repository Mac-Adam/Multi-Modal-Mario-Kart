#include <Wire.h>
#include <MPU6050_light.h>

// Definicja pinów I2C dla ESP32 DevKit V1
const int SDA_PIN = 21;
const int SCL_PIN = 22;

MPU6050 mpu(Wire);
unsigned long timer = 0;


double calc_throttle(double angle) 
{
  if (angle > -2.0 && angle < 2.0) {
    return 0.0;
  }

  if (angle <= -2.0) {
    double result = (angle + 2.0) / 23.0; 
    return (result < -1.0) ? -1.0 : result;
  }

  if (angle >= 2.0) {
    double result = (angle - 2.0) / 23.0;
    return (result > 1.0) ? 1.0 : result;
  }

  return 0.0;
}

void setup() {
  Serial.begin(115200);
  
  // Inicjalizacja I2C z pinami 21 i 22
  Wire.begin(SDA_PIN, SCL_PIN);
  
  byte status = mpu.begin();
  // Serial.print(F("Status MPU6050: "));
  // Serial.println(status);
  
  if(status != 0) {
    Serial.println(F("Błąd inicjalizacji czujnika!"));
    while(1); 
  }
  delay(5000);  
  Serial.println(F("Kalibracja... Nie ruszaj czujnika przez 2 sekundy!"));
  delay(1000);
  mpu.calcOffsets(); // Oblicza poprawki dla 0x68
  Serial.println(F("Gotowe!\n"));
}

double angle = 0;
double throttle = 0;

void loop() {
  mpu.update();
  
  if((millis() - timer) > 10) { // Odczyt co 100ms
    timer = millis(); // Aktualizacja czasu
    
    angle = mpu.getAngleY();
    throttle = calc_throttle(-angle); // Obliczenie wartości
    
    // Wypisanie obu wartości dla porównania
    Serial.println(throttle);
  }
}
