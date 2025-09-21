# Sophie — Your Personal AI Assistant

Sophie is a desktop-based personal assistant with a GUI, built in Python using PySide6.  
She can chat naturally, change her mood, keep memories, and fetch/summarize tech news.

---

## ✨ Features
- 💬 **Conversational Assistant** — chat with Sophie in a friendly, natural style.
- 🎭 **Mood System** — selectable moods (Neutral, Cheerful, Thoughtful, Serious) that change how Sophie replies.
- 🧠 **Memory** — short-term (chat history) + long-term semantic memory powered by [ChromaDB](https://www.trychroma.com/).
- 📰 **Tech News Summaries** — fetches from multiple RSS feeds (Ars Technica, The Verge, Wired, NYT Tech) and presents a neat digest.
- 🎨 **Customizable UI** — PySide6 GUI styled with Qt stylesheets, includes avatar support.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+  
- A working [Ollama](https://ollama.ai) installation (for local LLM inference)  
- GPU with at least 6GB VRAM recommended  

### Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/colinmachale/sophie-assistant.git
cd sophie-assistant
pip install -r requirements.txt

```
### Running sophie
``` bash
python assistant_gui.py
```
## 📌Roadmap

- [x] Chat interface with PySide6  
- [x] RSS news integration + summarization  
- [x] Mood system (manual via radio buttons)  
- [x] Long-term memory with ChromaDB  
- [ ] Automatic mood detection from conversation  
- [ ] Voice output (TTS)  
- [ ] Better persona management (User’s preferences, likes/dislikes)  
- [ ] Extended skills (weather, reminders, system integration)

## 🛠 Tech Stack
- [Python](https://www.python.org/)  
- [PySide6](https://wiki.qt.io/Qt_for_Python) for GUI  
- [ChromaDB](https://www.trychroma.com/) for semantic memory  
- [feedparser](https://pypi.org/project/feedparser/) for RSS feeds  
- [Ollama](https://ollama.ai) for running LLMs locally  


## 🤝 Contributing

PRs, issues, and feature requests are welcome!
Feel free to fork this repo and experiment with Sophie’s personality and skills

## 📜 License

MIT License — free to use and modify
