#include "wio_tracker.h"

WioTracker wio = WioTracker();

//Defining the LDR pin
int LIGHT_PIN = 7;
int sensorValue = 0;  // variable coming from sensor 
float voltageValue = 0.0;
String time_taken ="";

void setup() {
    wio.Power_On();
    //Connection with Pi
    Serial.begin(115200);
    SerialUSB.println("Power On!");

    //Initialise the network
    if (!wio.waitForNetworkRegister()) {
        SerialUSB.println("Network error!");
        return;
    } else {
        SerialUSB.println("Network ready!");
    }

    sendText("LTE module initialised!");
      

    pinMode(LIGHT_PIN, INPUT_ANALOG);
    

}

void loop() {
  SerialUSB.println("Waiting for message from RPi");
  
  while (Serial.available() == 0) {
  }
  SerialUSB.print("data available= ");
  SerialUSB.println(Serial.available());
  
  int nextAction = Serial.parseInt();
  SerialUSB.print("next action: ");
  SerialUSB.println(nextAction);

  switch (nextAction) {
    case 1:
      // Get data for light
      sensorValue = analogRead(LIGHT_PIN);
      voltageValue= sensorValue*3.3/4096.0;
      //Serial.print("Voltage: ");
      Serial.print(voltageValue);
      SerialUSB.println("Sent following message");
      SerialUSB.print("Voltage: ");
      SerialUSB.println(voltageValue);

      break;

    case 2:
      // Send text message for finished draining
      sendText("Pond has finished draining!");
      SerialUSB.println("Message sent for draining");
      
      break;

    case 3:
      // Send text message for finished filling
      sendText("Pond has finished filling up. It should now be clean");
      SerialUSB.println("Message sent for filling");
      
      break;


    default:
      SerialUSB.println("Please choose a valid selection");
  }
  
    
}

void sendText(String text_data)
{
  //Need to convert to a char array to send through the module.
  //This process creates a char array of the appropriate size and assigns our text to it
  String full_text=text_data;
  // Length (with one extra character for the null terminator)
  int str_len = full_text.length() + 1; 

  // Prepare the character array (the buffer) 
  char char_array[str_len];

  // Copy it over 
  full_text.toCharArray(char_array, str_len);
  
  //Insert the destination phone number here!      
  if (wio.sendSMS("0400000000", char_array)) {
    SerialUSB.println("Send ok");
  } else {
    SerialUSB.println("Send Error!");
  }
}
