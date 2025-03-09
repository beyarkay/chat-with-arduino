# Chat With Arduino

Use Claude or other LLMs to control your Arduino microcontroller!

## How it works

[demo goes here]

## Features

- Control your Arduino directly through Claude
- no code writing or uploading required. Claude handles it all
- You can move motors, turn on LEDs, read sensors directly via Claude
- Claude can write it's own code and upload it to the microcontroller

## Installation

Install the desktop-based LLM app. I'll show how to use [Claude Desktop][1],
but you can also use `ollama` paired with `oterm` for fully local tool-use.

1. Install Claude Desktop either from [the website][1] or via `brew install --cask claude`
2. Install [`uv`][2]: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Tell Claude how to use Chat With Arduino:

   ```
   echo '{
   "mcpServers": {
       "chat-with-arduino": {
       "command": "/opt/homebrew/bin/uv",
       "args": [ "beyarkay/chat-with-arduino" ]
       }
   }
   }' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

Now open `Claude Desktop`, and you should see a small hammer icon on the bottom
right of the chat window:

![A small hammer icon circled in red][media/hammer.png]

You are now good to go! Claude is smart enough to figure out what commands need
to be called to do what you want it to.

## Usage

TODO

## Roadmap

- Auto-install arduino-cli
- Support for ESP32

[1]: https://claude.ai/download
[2]: https://docs.astral.sh/uv/getting-started/installation/
[3]: https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server
