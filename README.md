# Chat With Arduino

Use Claude or other LLMs to control your Arduino/ESP32 microcontroller!

## How it works

[demo goes here]

## Installation

For this to work, we need three things: a desktop-based LLM app (we'll be using
[Claude Desktop][1], 2. the MCP _server_ running on the same computer as Claude
Desktop, and 3. an Arduino library that'll run on your arduino and control it.
The desktop app will manage the messages between you and the LLM, as well as
between the LLM and the MCP server. The MCP server will send Claude's requests
to your Arduino, and the Arduino library will take actions based on Claude's
requests (turning on LEDs, spinning servos, etc).

1. Install [Claude Desktop][1]
2. Download & run the MCP server: `uvx chat-with-arduino` ([install `uv`][2] if
   you haven't already)
   TODO: publish pip package
3. Install the Arduino libary (TODO: publish Arduino library)

[1]: https://claude.ai/download
[2]: https://docs.astral.sh/uv/getting-started/installation/
