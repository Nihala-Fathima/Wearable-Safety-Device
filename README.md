# Wearable-Safety-Device
A smart, portable, and real-time safety device designed to ensure women's security in emergency situations. This wearable gadget features GPS tracking, GSM-based alerts, fall detection, and heart rate monitoring—all integrated into a compact system powered by the ESP32 microcontroller.

⚙️ Working Prototype

🔧 Hardware Components
ESP32 Dev Board

SIM800L GSM Module

NEO-6M GPS Module

Pulse Sensor (MAX30100/MAX30102)

Accelerometer (e.g., ADXL345)

16x2 LCD Display with I2C

18650 Li-ion Battery with TP4056 Charger Module

Buzzer

Push Button (SOS Trigger)

On and Off Button


🚀 Key Features
📍 Live GPS Tracking

📲 SMS Alert with Location Link

📞 Auto-Call Trigger During Emergency

🔔 Buzzer  Feedback

❤️ Heart Rate Monitoring with Emergency Trigger on Abnormal BPM

🤕 Fall Detection with Accelerometer and Auto Alert

🔄 How It Works
1. 🆘 Emergency Activation via SOS Button
When the SOS switch is pressed, the ESP32 detects the signal and activates emergency mode.

The system fetches GPS location and sends an SMS alert via the GSM module.

Optionally, it makes an automatic call to the trusted contact.

2. 📡 GPS Live Tracking
The NEO-6M GPS module fetches precise coordinates.

The ESP32 continuously processes and updates the location.

3. 🚔 Alert Reception by Emergency Contact
Trusted person receives SMS with a clickable Google Maps link.

They can take immediate action or share location with authorities.

4. ⚠️ Fall Detection with Accelerometer
Detects sudden motion or falls.

ESP32 triggers SMS and call alerts automatically.

5. 💓 Heart Rate Monitoring
Constantly tracks heartbeats per minute (BPM).

Sends alert if abnormal pulse is detected.


