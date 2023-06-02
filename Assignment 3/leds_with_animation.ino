#include <FastLED.h>

// Configuration of the LED strip
#define LED_PIN 5          // Pin connected to the LED strip
#define NUM_LEDS 21        // Total number of LEDs in the strip

// Configuration of the analog inputs
#define INPUT_PIN_1 A1     // Analog input pin 1
#define INPUT_PIN_2 A0     // Analog input pin 2

// Configuration of the LED sections
#define SECTION_1_START 0  // Start index of section 1
#define SECTION_1_LENGTH 10 // Length of section 1
#define SECTION_2_START 12 // Start index of section 2
#define SECTION_2_LENGTH 10 // Length of section 2

// Declarating the LED strip object
CRGB leds[NUM_LEDS];

// Threshold values for each input
const int THRESHOLD_1 = 500;

// Animation variables
int animationCounter = 0;
bool isAnimationActive = false;

void setup() {
  // Initialize the LED strip
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(100);

  // Initialize the serial communication
  Serial.begin(9600);
}

void loop() {
  // Read the analog inputs
  int value1 = analogRead(INPUT_PIN_1);
  int value2 = analogRead(INPUT_PIN_2);
  Serial.println(value2);

  // Map the analog values to the LED strip indices
  int section1End = SECTION_1_START + SECTION_1_LENGTH;
  int section2End = SECTION_2_START + SECTION_2_LENGTH;

  // Check if the animation should be active
  if (value1 > THRESHOLD_1) {
    isAnimationActive = true;
  } else {
    isAnimationActive = false;
  }

  // Perform the loading animation if active
  if (isAnimationActive) {
    // Increment the animation counter
    animationCounter++;

    // Update the LEDs based on the animation counter
    for (int i = 0; i < NUM_LEDS; i++) {
      if (i >= SECTION_1_START && i < section1End) {
        leds[i] = (animationCounter % 2 == 0) ? CRGB::White : CRGB::Black;
      } else if (i >= SECTION_2_START && i < section2End) {
        leds[i] = (animationCounter % 2 == 1) ? CRGB::White : CRGB::Black;
      } else {
        leds[i] = CRGB::Black;
      }
    }

    // Update the LED strip
    FastLED.show();

    // Delay between updates
    delay(200); // Adjust the delay duration to change the animation speed
  } else {
    // Turn on/off the LED sections based on the analog values and thresholds
    for (int i = 0; i < NUM_LEDS; i++) {
      if (i >= SECTION_1_START && i < section1End) {
        leds[i] = (value2 > THRESHOLD_1) ? CRGB::Green : CRGB::Black;
      } else if (i >= SECTION_2_START && i < section2End) {
        leds[i] = (value2 > THRESHOLD_1) ? CRGB::Green : CRGB::Black;
      } else {
        leds[i] = CRGB::Black;
      }
    }
    FastLED.show();

  }
}
