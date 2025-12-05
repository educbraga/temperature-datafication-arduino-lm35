const int pinLM35 = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int leituraADC = analogRead(pinLM35);

  // Converte ADC -> tensão (em volts)
  float tensao = leituraADC * (5.0 / 1023.0);

  // LM35: 10 mV por grau -> 0.01 V por grau
  float temperaturaC = tensao / 0.01;

  Serial.print("Temperatura: ");
  Serial.print(temperaturaC);
  Serial.println(" °C");

  delay(500);
}