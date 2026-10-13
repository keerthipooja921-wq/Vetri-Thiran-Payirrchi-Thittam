# Pocket Smart AI

A beginner-friendly desktop AI coding assistant for Windows. It connects to a **local Ollama model**, so no paid API key is required.

## Features

- Generate code from a natural-language request
- Explain code in beginner-friendly language
- Debug code and request corrected versions
- Improve/refactor code
- Open a local source file and send it for analysis
- Copy or save AI responses
- Check whether the selected Ollama model is available

## Requirements

- Windows 10/11
- Python 3.10 or newer (Python 3.11+ recommended)
- Ollama for Windows
- A compatible local model and enough RAM/disk space

This project uses Python's built-in `tkinter`, `urllib`, `json`, and `threading` modules. No `pip install` packages are required for the app itself.

## Setup on Windows 11

### 1. Install Python

Download Python from https://www.python.org/downloads/windows/ . During installation, enable **Add Python to PATH**. Open Command Prompt and check:

```bat
python --version
```

### 2. Install Ollama

Download and install Ollama from https://ollama.com/download . Ollama runs the local model service.

### 3. Download a coding model

Open Command Prompt or the VS Code terminal and run:

```bat
ollama pull qwen2.5-coder:3b
```

This downloads the model once. The download requires internet access and storage space. The model then runs locally. If your laptop has limited memory, close other heavy applications. You may choose another model supported by Ollama; enter its exact name in the app's model field.

Check installed models:

```bat
ollama list
```

If the Ollama command is unavailable, restart the terminal after installing Ollama. Ensure the Ollama app/service is running.

### 4. Open the project in VS Code

1. Extract the project ZIP.
2. Open VS Code.
3. Select **File → Open Folder** and choose the `PocketSmartAI` folder.
4. Open `app.py`.

### 5. Run the app

In the VS Code terminal, run:

```bat
python app.py
```

Click **Check connection**. When connected, enter a coding request and select **Generate code**, **Explain code**, **Debug code**, or **Improve code**.

## Example prompts

**Generate**
> Create a Python calculator using Tkinter with addition, subtraction, multiplication, and division.

**Explain**
> Explain this Python code line by line for a beginner: `for i in range(5): print(i)`

**Debug**
> Find and fix the errors in this code: `print("Hello"`

**Improve**
> Refactor this function to make it easier to read, without changing its behavior.

## Project structure

```text
PocketSmartAI/
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## API keys and privacy

- **No API key is required.**
- Prompts are sent to the Ollama service on your own computer at `http://localhost:11434`.
- The app does not intentionally send prompts to a cloud AI provider.
- Ollama/model installation needs an internet connection initially. Actual offline use is possible after setup if the model is downloaded and Ollama is available.
- Avoid entering passwords, private keys, or confidential information into prompts.

## Troubleshooting

**Cannot connect to localhost:11434**
- Start/reopen Ollama.
- Visit the Ollama download page if it is not installed.
- Run `ollama list` in Command Prompt.
- Try `ollama pull qwen2.5-coder:3b`, then retry.

**Model not found**
- Check the exact model name with `ollama list`.
- Enter the exact model tag in the app, such as `qwen2.5-coder:3b`.

**Responses are slow**
- The first response can take longer while the model loads.
- Smaller models generally use fewer resources, though answer quality may differ.
- Close other memory-heavy applications.

**Python cannot find tkinter**
- Use the standard Windows installer from python.org and ensure Tcl/Tk support was installed.

## Testing checklist

1. Start Ollama and confirm the model appears in `ollama list`.
2. Run `python app.py`; confirm the window opens.
3. Click **Check connection** and confirm the model is detected.
4. Generate a simple Python greeting program.
5. Ask the assistant to explain a short code snippet.
6. Ask it to debug a deliberately incomplete statement.
7. Open a local `.py` file and request an explanation.
8. Copy and save a response.
9. Test an incorrect model name and confirm the app displays troubleshooting guidance.

## Important note

AI output can be wrong or insecure. Review generated code and run tests before using it. This is a starter project, not a replacement for code review or security checks.
