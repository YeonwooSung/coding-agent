# Coding Agent

AI-agent for coding.

## Pre-requisite

First, create the config for LLM call.
```bash
cd config

cp config.example.toml config.toml
```

Then, update the config.toml with your LLM configs (i.e. OpenAI API key, etc).

Next, install the dependencies:
```bash
# Install dependencies
python3 -m pip install -r requirements.txt
```

### Additional requirements (for UI components)

Also, install `playwright` for UI component:
```bash
playwright install
```

## Running instructions

```bash
python3 main.py
```
