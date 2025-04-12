#include <Wire.h>
#include <Adafruit_ADXL345_U.h>
#include <Adafruit_Sensor.h>
#include <LiquidCrystal_I2C.h>
#include <PulseSensorPlayground.h>


#define SOS_BUTTON 25
#define BUZZER 26
#define PULSE_SENSOR 32
#define ACCEL_THRESHOLD 15

const int THRESHOLD = 550;       // Threshold for detecting a heartbeat

PulseSensorPlayground pulseSensor;


Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
HardwareSerial gsm(1);  // GSM on Serial1
HardwareSerial gps(2);  // GPS on Serial2
LiquidCrystal_I2C lcd(0x27, 16, 2);

int pulseThreshold = 130;
bool sosSent = false;
unsigned long lastButtonPress = 0;
unsigned long sosResetTime = 10000;
unsigned long lastHeartCheck = 0;
int pulseReadings[5] = { 0 };
int pulseIndex = 0;
String lastMessage = "";

//Messages and phone calls will be send to these numbers
String emergencyNumbers[] =  { "+9xxxxxxxxxx", "+9xxxxxxxxx" };

//Send sms
void sendSMS(String message) {
  gsm.println("AT+CMGF=1");
  delay(1000);
  for (String number : emergencyNumbers) {
    gsm.println("AT+CMGS=\"" + number + "\"");
    delay(1000);
    gsm.print(message);
    delay(1000);
    gsm.write(26);  // CTRL+Z to send
    delay(3000);
  }
}

// Function to make calls to the emergency numbers
void makeCall() {
  for (String number : emergencyNumbers) {
    Serial.print("Dialing: ");
    displayMessage("Dialing..");
    Serial.println(number);
    
    gsm.println("ATD" + number + ";");  // Dial the phone number
    delay(20000);        // Wait for the call duration (10 seconds in this case)
    
    gsm.println("ATH");  // Hang up the call
    Serial.println("Call ended.");
    displayMessage("Call ended");
    delay(2000);          // Short delay before dialing the next number
  }
}

//Returns the Latitude and Longitude of the Device
String getGPSLocation() {
  bool isAvailable = false;
  String data = "", lat = "", lon = "";
  while (gps.available()) {
    char c = gps.read();
    data += c;
    
    //Serial.print(c);
  }
  Serial.print(data);
  
    // Look for the $GPRMC sentence
    if (data.indexOf("$GPRMC") != -1) {
      int start = data.indexOf("$GPRMC");
      int commas = 0, latStart = 0, lonStart = 0;
      
      // Loop through the sentence and find the latitude and longitude fields
      for (int i = start; i < data.length(); i++) {

        if (data[i] == ',') commas++;  // Count commas to identify fields

        if(commas == 2){
          Serial.print('\n');
          Serial.print(data[start+17]);
          if(data[start+17] == 'A'){
            isAvailable = true;
           
          }
          else{
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.println("No Location");
            return "No Location";
          }
        }

        if(isAvailable){
            if (commas == 2) latStart = i+2 ;  // Latitude field starts here
            if (commas == 4) lonStart = i+2 ;  // Longitude field starts here
        }

      }
      
    // Extract latitude and longitude
    lat = data.substring(latStart, latStart + 12);  // Latitude (DDMM.MMMMM)
    lon = data.substring(lonStart, lonStart + 13); // Longitude (DDDMM.MMMMM)
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("L:"+lat);
    lcd.setCursor(0, 1);
    lcd.print("l:"+lon);
    return "Lat: " + lat + " Lon: " + lon;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.println("No GPS");
  return "NO GPS";
}

//Display Notification in LCD
void displayMessage(String message) {
  if (message != lastMessage) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(message);
    lastMessage = message;
  }
}

//Read response from GSM module
void readGSMResponse() {
  String response = "";
  while (gsm.available()) {
    char c = gsm.read();
    response += c;
  }
  if (response.length() > 0) {
    Serial.println(response);  // Print GSM response to Serial Monitor
  }
}

//GSM initialization
void initializeGSM(){
  delay(10000);

  gsm.println("AT");
  updateSerial();
  Serial.println();
  gsm.println("AT+CSQ");
  updateSerial();
  gsm.println("AT+CCID");
  updateSerial();
  gsm.println("AT+CREG?");
  updateSerial();
  gsm.println("ATI");
  updateSerial();
  gsm.println("AT+CBC");
  updateSerial();
  gsm.println("AT+CMGDA=\"DEL ALL\"");
  updateSerial();
}


void updateSerial(){
  delay(500);
  while (Serial.available())
  {
    gsm.write(Serial.read());//Forward what Serial received to Software Serial Port
  }
  while (gsm.available())
  {
    Serial.write(gsm.read());//Forward what Software Serial received to Serial Port
  }
}

void homePage(){
  lcd.clear();
  lcd.setCursor(2, 0); 
  lcd.print("Safety Watch");
  lcd.setCursor(5, 1); 
  lcd.print("Ready!");
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  gsm.begin(9600, SERIAL_8N1, 16, 17);  // GSM
  gps.begin(9600, SERIAL_8N1, 18, 19);  // GPS



  pinMode(SOS_BUTTON, INPUT_PULLUP);
  pinMode(BUZZER, OUTPUT);
  pinMode(PULSE_SENSOR, INPUT);

  
  pulseSensor.analogInput(PULSE_SENSOR);
  pulseSensor.setThreshold(THRESHOLD);

  Serial.println("Setting up pulse sensor...");

  // Begin the PulseSensor
  if (pulseSensor.begin()) {
    Serial.println("PulseSensor object created successfully!");
  } else {
    Serial.println("Failed to initialize PulseSensor.");
  }

  initializeGSM();

  lcd.begin();  // Initialize with the LCD size (16x2)
  lcd.backlight();
  homePage();

  //Beging Accelerometer
  if (!accel.begin()) {
    Serial.println("ADXL345 not found!");
    while (1)
      ;
  }
}


uint8_t senseGPS = 0;
String gpsOut = "";

void loop() {


  //Take GPS readings every 10seconds
  senseGPS++;
  if(senseGPS >= 20){

    gpsOut = getGPSLocation();

    senseGPS = 0;
    delay(2000); //delay to make sure that the gps module won't be read for the next 6 sec
    homePage();
  }

  //The function checks if 5 seconds have passed since the last heart rate check 
  int currentBPM = pulseSensor.getBeatsPerMinute();
  // Serial.println(currentBPM);
  
  delay(100);
  if (pulseSensor.sawStartOfBeat()){
    if (millis() - lastHeartCheck > 5000) {
      lastHeartCheck = millis();
      if (currentBPM > pulseThreshold) {

        Serial.println("message sending...");
        displayMessage("message sending...");
        delay(2000);
        

        sendSMS("Abnormal HeartRate!!\nLocation:"+gpsOut);
        Serial.println("message send");
        displayMessage("message send");

        delay(10000);
        
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.println("Heart ALERT!!");
        digitalWrite(BUZZER, HIGH);
        delay(1000);
        digitalWrite(BUZZER, LOW);

        homePage();
      }
    }
  }

  //SOS button for sending HELP message
  if (digitalRead(SOS_BUTTON) == LOW){
    Serial.println("message sending...");
    displayMessage("message sending...");
    delay(2000);

    sendSMS("HELP\nLocation:"+gpsOut);
    Serial.println("message send");
    displayMessage("message send");

    makeCall();
    delay(10000);
    homePage();
}

  //Fall detection using accelerometer
  sensors_event_t event;
  accel.getEvent(&event);
  if (abs(event.acceleration.x) > ACCEL_THRESHOLD || abs(event.acceleration.y) > ACCEL_THRESHOLD || abs(event.acceleration.z) > ACCEL_THRESHOLD) {
    delay(100);
    accel.getEvent(&event);
    if (abs(event.acceleration.x) > ACCEL_THRESHOLD || abs(event.acceleration.y) > ACCEL_THRESHOLD || abs(event.acceleration.z) > ACCEL_THRESHOLD) {
      displayMessage("Fall Detected!");
      Serial.println("message sending...");
      displayMessage("message sending...");
      delay(2000);
      sendSMS("Fall Detected! " + gpsOut);
      Serial.println("message send");
      displayMessage("message send");
      makeCall();
      
      digitalWrite(BUZZER, HIGH);
      delay(1000);
      digitalWrite(BUZZER, LOW);
    }
    homePage();
  }

  delay(500);
}