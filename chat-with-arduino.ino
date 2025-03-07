// typedef uint8_t u8;
// typedef uint16_t u16;
// typedef uint32_t u32;
// typedef int8_t i8;
// typedef int16_t i16;
// typedef int32_t i32;



void setup() {
  // Initialize serial communication at 9600 baud rate
  Serial.begin(9600);
}

void loop() {
  // Check if there are at least 3 bytes available in the serial buffer
  if (Serial.available() >= 3u) {
    // Read the command byte
    u8 command = Serial.read();

    // Handle the command
    switch (command) {
      case 0x00: // Digital Write Command
        handleDigitalWrite();
        break;

      case 0x01: // Example: Another Command (stub)
        handleAnotherCommand();
        break;

      // Add more cases for other commands here

      default:
        // Unknown command
        // Serial.println("Error: Unknown command");
        break;
    }
  }
}

void handleDigitalWrite() {
  // Read the next two bytes: pin number and value
  if (Serial.available() >= 2u) {
    u8 pin = Serial.read();
    u8 value = Serial.read();

    // Stub: Perform the digital write action
    pinMode(pin, OUTPUT);
    digitalWrite(pin, value > 0 ? HIGH : LOW);
    // Serial.print("Digital Write: Pin ");
    // Serial.print(pin);
    // Serial.print(", Value ");
    // Serial.println(value);
  } else {
    // Serial.println("Error: Insufficient data for Digital Write command");
  }
}

void handleAnotherCommand() {
  // Stub: Handle another command
  Serial.println("Another Command Received");
  // Add your logic here
}
