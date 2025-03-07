# Chat With Arduino

Use Claude or other LLMs to control your Arduino/ESP32 microcontroller!

## How it works

[demo goes here]

## Features

- Control your Arduino directly through Claude, no code writing or uploading
  required. You can move motors, turn on LEDs, anything.
- Alternatively, get Claude to write Arduino code for you, and then tell Claude
  to upload the code to the Arduino

## Installation

For this to work, we need two things: a desktop-based LLM app (we'll be using
[Claude Desktop][1], and Chat With Arduino running on the same computer as Claude
Desktop.

1. Install [Claude Desktop][1]
2. Download & run the MCP server: `uvx chat-with-arduino` ([install `uv`][2] if
   you haven't already)
   TODO: publish pip package

3. You'll need to tell Claude Desktop about Chat With Arduino. Edit your
   `claude_desktop_config.json` (usually located in `~/Library/Application Support/Claude/claude_desktop_config.json`
   or `%APPDATA%\Claude\claude_desktop_config.json`, see detailed instructions
   [here][3]):

```
{
  "mcpServers": {
    "chat-with-arduino": {
      "command": "uvx",
      "args": [
        "beyarkay/chat-with-arduino"
      ]
    }
  }
}
```

## TODO

- Auto-install arduino-cli
- Provide an arduino-cli interface
- list boards by FQBN
- Auto-upload the chat-with-arduino sketch
- Install new cores
- use Claude to write a script that gets uploaded

[1]: https://claude.ai/download
[2]: https://docs.astral.sh/uv/getting-started/installation/
[3]: https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server
