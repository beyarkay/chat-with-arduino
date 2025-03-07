
uint8_t START_OF_MESSAGE = 0xFE;
uint8_t END_OF_MESSAGE = 0xFF;

enum TctlmIds : uint8_t {
    ERR = 0,
    ACK = 1,
    DIGITAL_READ = 2,
    DIGITAL_WRITE = 3,
    PIN_MODE = 4,
    ANALOG_READ = 5,
    ANALOG_WRITE = 6,
    TONE = 7,
    NO_TONE = 8,
    DELAY = 9,
    MILLIS = 10,
};


void sendError() {
    // Send start of message, ERR TctlmId, and end of message
    Serial.write(START_OF_MESSAGE);
    Serial.write(TctlmIds::ERR);
    Serial.write(END_OF_MESSAGE);
}

void sendTctlmId(TctlmIds tctlmId) {
    // Send start of message, the provided TctlmId, and end of message
    Serial.write(START_OF_MESSAGE);
    Serial.write(tctlmId);
    Serial.write(END_OF_MESSAGE);
}

void handleAck() {
    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Send a reply back indicating that the ACK was received successfully
    sendTctlmId(TctlmIds::ACK);
}

void handleDigitalRead() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Get the digital pin value using the digitalRead function
    uint8_t pinState = digitalRead(pin);

    // Send the response back with the pin value
    Serial.write(START_OF_MESSAGE);
    Serial.write(TctlmIds::DIGITAL_READ);
    Serial.write(pinState);  // 0 or 1
    Serial.write(END_OF_MESSAGE);
}

void handleDigitalWrite() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the state (should be the third byte, 0 or 1)
    uint8_t state = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Set the digital pin state using the digitalWrite function
    digitalWrite(pin, state);

    // Send the response back indicating that the digitalWrite was executed
    Serial.write(TctlmIds::DIGITAL_WRITE);
}

void handlePinMode() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the mode (should be the third byte)
    uint8_t mode = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Check if mode is valid
    if (mode > 4) {
        sendError();
        return;
    }

    // Set the pin mode using pinMode function
    pinMode(pin, mode);

    // Send the response back indicating that the pinMode was executed
    sendTctlmId(TctlmIds::PIN_MODE);
}

void handleAnalogRead() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Read the analog value using analogRead function
    int value = analogRead(pin);

    // Send the response back with the analog value
    Serial.write(START_OF_MESSAGE);
    Serial.write(TctlmIds::ANALOG_READ);
    Serial.write((uint8_t)(value >> 8)); // Send high byte
    Serial.write((uint8_t)(value & 0xFF)); // Send low byte
    Serial.write(END_OF_MESSAGE);
}

void handleAnalogWrite() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the value to write (should be the third byte)
    uint8_t value = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Write the value using analogWrite function
    analogWrite(pin, value);

    // Send the response back indicating that the analogWrite was executed
    sendTctlmId(TctlmIds::ANALOG_WRITE);
}

void handleTone() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the frequency (should be the third byte, high byte)
    uint8_t freqHigh = Serial.read();

    // Read the frequency (should be the fourth byte, low byte)
    uint8_t freqLow = Serial.read();

    // Read the duration (should be the fifth byte, high byte)
    uint8_t durationHigh = Serial.read();

    // Read the duration (should be the sixth byte, low byte)
    uint8_t durationLow = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Combine frequency and duration bytes into full values
    long frequency = (freqHigh << 8) | freqLow;
    long duration = (durationHigh << 8) | durationLow;

    // Generate tone on the specified pin
    tone(pin, frequency, duration);

    // Send the response back indicating the tone was set
    sendTctlmId(TctlmIds::TONE);
}

void handleNoTone() {
    // Read the pin number (should be the second byte)
    uint8_t pin = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Stop tone on the specified pin
    noTone(pin);

    // Send the response back indicating the tone was stopped
    sendTctlmId(TctlmIds::NO_TONE);
}

void handleDelay() {
    // Read the delay duration (should be the second byte, high byte)
    uint8_t durationHigh = Serial.read();

    // Read the delay duration (should be the third byte, low byte)
    uint8_t durationLow = Serial.read();

    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Combine duration bytes into a full value
    long duration = (durationHigh << 8) | durationLow;

    // Perform the delay
    delay(duration);

    // Send the response back indicating the delay was executed
    sendTctlmId(TctlmIds::DELAY);
}

void handleMillis() {
    // Read the end of message byte
    uint8_t endByte = Serial.read();

    // Ensure the end byte is correct
    if (endByte != END_OF_MESSAGE) {
        sendError();
        return;
    }

    // Get the current millis value
    long millisValue = millis();

    // Send the response back with the millis value
    Serial.write(START_OF_MESSAGE);
    Serial.write(TctlmIds::MILLIS);
    Serial.write((uint8_t)(millisValue >> 8)); // Send high byte
    Serial.write((uint8_t)(millisValue & 0xFF)); // Send low byte
    Serial.write(END_OF_MESSAGE);
}

void setup() {
    // Initialize serial communication at 9600 baud rate
    Serial.begin(9600);
}

void loop() {
    // Check if there are enough bytes in the serial buffer for the message format
    if (Serial.available() < 3u) {
        return;
    }
    // Read the start of message byte
    uint8_t startByte = Serial.read();

    // Ensure the start byte is correct
    if (startByte != START_OF_MESSAGE) {
        // If it's not the expected start byte, skip the rest and wait for the next message
        while (Serial.available()) {
            Serial.read();
        }
        return;
    }

    // Read the command byte (the TctlmId)
    uint8_t command = Serial.read();

    // Handle the command based on the TctlmId
    switch (command) {
        case TctlmIds::ACK:
            handleAck();
            break;

        case TctlmIds::DIGITAL_READ:
            handleDigitalRead();
            break;

        case TctlmIds::DIGITAL_WRITE:
            handleDigitalWrite();
            break;

        case TctlmIds::PIN_MODE:
            handlePinMode();
            break;

        case TctlmIds::ANALOG_READ:
            handleAnalogRead();
            break;

        case TctlmIds::ANALOG_WRITE:
            handleAnalogWrite();
            break;

        case TctlmIds::TONE:
            handleTone();
            break;

        case TctlmIds::NO_TONE:
            handleNoTone();
            break;

        case TctlmIds::DELAY:
            handleDelay();
            break;

        case TctlmIds::MILLIS:
            handleMillis();
            break;

        default:
            // Unknown command, handle accordingly
            // Optionally send an error response back or do nothing
            sendError();
            break;
    }
}

