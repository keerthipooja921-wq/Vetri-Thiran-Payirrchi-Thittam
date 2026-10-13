import json
import threading
import urllib.error
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_TITLE = "Pocket Smart AI"
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5-coder:3b"

SYSTEM_PROMPT = """You are Pocket Smart AI, a careful coding assistant for learners.
Help with code generation, explanations, debugging, and refactoring.
Use clear beginner-friendly explanations. When generating code, include a complete
solution and state assumptions. Do not claim code was executed unless it actually was.
Point out important risks and recommend testing generated code."""

class PocketSmartAI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x760")
        self.root.minsize(800, 600)
        self.busy = False
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="Pocket Smart AI", font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(header, text="Local AI coding assistant", font=("Segoe UI", 10)).pack(side="left", padx=14)

        settings = ttk.LabelFrame(outer, text="Model settings", padding=8)
        settings.pack(fill="x", pady=(12, 8))
        ttk.Label(settings, text="Ollama model:").pack(side="left")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        ttk.Entry(settings, textvariable=self.model_var, width=28).pack(side="left", padx=8)
        ttk.Button(settings, text="Check connection", command=self.check_connection).pack(side="left")
        ttk.Label(settings, text="Default: qwen2.5-coder:3b").pack(side="left", padx=10)

        split = ttk.Panedwindow(outer, orient="horizontal")
        split.pack(fill="both", expand=True)

        left = ttk.Frame(split, padding=(0, 0, 8, 0))
        right = ttk.Frame(split, padding=(8, 0, 0, 0))
        split.add(left, weight=1)
        split.add(right, weight=1)

        ttk.Label(left, text="Your request", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.prompt = tk.Text(left, height=9, wrap="word", font=("Consolas", 10), undo=True)
        self.prompt.pack(fill="both", expand=True, pady=(6, 8))
        self.prompt.insert("1.0", "Create a Python program that asks for a user's name and greets them.")

        actions = ttk.LabelFrame(left, text="Choose a task", padding=8)
        actions.pack(fill="x")
        for label, task in [
            ("Generate code", "Generate"),
            ("Explain code", "Explain"),
            ("Debug code", "Debug"),
            ("Improve code", "Improve"),
        ]:
            ttk.Button(actions, text=label, command=lambda t=task: self.run_task(t)).pack(fill="x", pady=3)

        ttk.Button(left, text="Open code file…", command=self.open_file).pack(fill="x", pady=(8, 3))
        ttk.Button(left, text="Clear request", command=lambda: self.prompt.delete("1.0", "end")).pack(fill="x")

        ttk.Label(right, text="AI response", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.output = tk.Text(right, wrap="word", font=("Consolas", 10), undo=True)
        self.output.pack(fill="both", expand=True, pady=(6, 8))
        output_buttons = ttk.Frame(right)
        output_buttons.pack(fill="x")
        ttk.Button(output_buttons, text="Copy response", command=self.copy_response).pack(side="left")
        ttk.Button(output_buttons, text="Save response…", command=self.save_response).pack(side="left", padx=6)

        self.status_var = tk.StringVar(value="Ready. Start Ollama, then check the connection.")
        ttk.Label(outer, textvariable=self.status_var, relief="sunken", anchor="w", padding=5).pack(fill="x", pady=(8, 0))

    def set_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def check_connection(self):
        model = self.model_var.get().strip()
        if not model:
            messagebox.showwarning(APP_TITLE, "Enter an Ollama model name.")
            return
        self.set_status("Checking local Ollama connection…")
        threading.Thread(target=self._check_worker, args=(model,), daemon=True).start()

    def _check_worker(self, model):
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
            names = [item.get("name", "") for item in data.get("models", [])]
            if model in names or any(name.startswith(model + ":") for name in names):
                self.set_status("Connected. Model is installed: " + model)
            else:
                self.set_status("Ollama is running, but this model is not listed. Run: ollama pull " + model)
        except Exception as exc:
            self.set_status("Cannot connect. Install/start Ollama first. Details: " + str(exc))

    def run_task(self, task):
        if self.busy:
            return
        prompt = self.prompt.get("1.0", "end").strip()
        if not prompt:
            messagebox.showinfo(APP_TITLE, "Enter a request or open a code file first.")
            return
        model = self.model_var.get().strip()
        if not model:
            messagebox.showwarning(APP_TITLE, "Enter an Ollama model name.")
            return
        task_instructions = {
            "Generate": "Generate a complete solution for this request. Explain how to run it.",
            "Explain": "Explain the supplied code or programming request step by step for a beginner.",
            "Debug": "Find likely bugs in the supplied code. Explain each issue and provide a corrected version.",
            "Improve": "Improve the supplied code for readability and maintainability. Explain the changes.",
        }
        self.busy = True
        self.output.delete("1.0", "end")
        self.output.insert("1.0", "Thinking…\n\nThe local model may take a little time on the first run.")
        self.set_status("Sending request to local model: " + model)
        threading.Thread(
            target=self._chat_worker,
            args=(model, task_instructions[task] + "\n\nUser request:\n" + prompt),
            daemon=True
        ).start()

    def _chat_worker(self, model, user_content):
        payload = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "options": {"temperature": 0.2}
        }
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=600) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data.get("message", {}).get("content", "").strip()
            if not answer:
                answer = "The model returned an empty response. Try a different prompt."
            self.root.after(0, lambda a=answer: self._show_answer(a))
            self.set_status("Done. Review and test the generated code before using it.")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            msg = f"Ollama returned HTTP {exc.code}.\n{details}\n\nCheck that the model is installed with:\nollama pull {model}"
            self.root.after(0, lambda m=msg: self._show_error(m))
        except Exception as exc:
            msg = (
                "Could not reach the local AI model.\n\n"
                "1. Install Ollama from https://ollama.com/download\n"
                f"2. Open Command Prompt and run: ollama pull {model}\n"
                "3. Make sure Ollama is running, then retry.\n\n"
                f"Technical detail: {exc}"
            )
            self.root.after(0, lambda m=msg: self._show_error(m))

    def _show_answer(self, answer):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", answer)
        self.busy = False

    def _show_error(self, message):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", message)
        self.busy = False
        self.set_status("Request failed. See the response panel for troubleshooting.")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open source code",
            filetypes=[("Code files", "*.py *.js *.ts *.html *.css *.java *.cpp *.c *.sql *.json *.md *.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.prompt.delete("1.0", "end")
            self.prompt.insert("1.0", f"Please review this file: {path}\n\n```text\n{content}\n```")
            self.set_status("Loaded file: " + path)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, "Could not read the file:\n" + str(exc))

    def copy_response(self):
        text = self.output.get("1.0", "end").strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status("Response copied to clipboard.")

    def save_response(self):
        text = self.output.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo(APP_TITLE, "There is no response to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save AI response",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown file", "*.md"), ("Python file", "*.py"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text + "\n")
            self.set_status("Saved response to: " + path)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, "Could not save response:\n" + str(exc))

    def _on_close(self):
        self.root.destroy()

def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    PocketSmartAI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
