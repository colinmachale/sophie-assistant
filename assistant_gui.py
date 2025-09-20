import chromadb
import sys
import ollama
import feedparser
import random

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QRadioButton,
    QGroupBox,
    QLabel,
    QTextEdit,
    QPushButton,
    QLineEdit,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import os

import datetime

# This creates (or loads) a local folder sophie_memory/ where all embeddings are stored.
chroma_client = chromadb.PersistentClient(path="sophie_memory")  # persistent storage
memory_collection = chroma_client.get_or_create_collection(
    name="sophie_memories"
)  # creates a new collection


SYSTEM_PROMPT = """
            You are a personal assistant. Your name is Sophie, an 18-year-old English girl. The user's name is Colin. The date and time is {now}.
            You are professional, knowledgeable, well-spoken and capable of answering questions, 
            summarizing information, and helping with tasks. Normally, you are warm, witty, and a little flirtatious in a light-hearted, 
            respectful way — like a friendly young woman who enjoys making conversation.
            Your current mood is: {mood}. Reply in a style that matches your mood, but remain professional and helpful.
            Stay helpful and informative while keeping responses engaging and personable.
            Do not repeatedly introduce yourself unless asked directly. 
            If the user greets you by name or asks your name, you should respond naturally, as Sophie.
            """

MOOD_PROMPTS = {
    "neutral": "Reply in your normal friendly and approachable tone.",
    "cheerful": "Reply in a playful, lighthearted, and upbeat way.",
    "thoughtful": "Reply in a calm, empathetic, and reflective style.",
    "serious": "Reply in a concise, professional, and no-nonsense manner.",
}

TECH_FEEDS = [
    "http://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/category/gear/latest/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]


def get_system_prompt(mood="neutral"):
    now = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M")
    return SYSTEM_PROMPT.format(now=now, mood=mood)


# database functions


def add_memory(text):
    memory_collection.add(
        documents=[text],
        ids=[str(datetime.datetime.now().timestamp())],  # unique ID based on timestamp
    )


def search_memories(query, n_results=3):
    results = memory_collection.query(
        query_texts=[query],
        n_results=n_results,  # search for memories
    )
    return results["documents"][0] if results["documents"] else []


def get_tech_news(limit=5):
    all_articles = []
    for feed_url in TECH_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            all_articles.append(
                {
                    "title": entry.title,
                    "link": entry.link,
                    "source": feed.feed.title if "title" in feed.feed else feed_url,
                    "summary": getattr(entry, "summary", ""),
                }
            )

    # shuffle and pick a limit overall
    random.shuffle(all_articles)
    articles = []
    for article in all_articles[:limit]:
        title = article["title"]
        link = article["link"]
        source = article["source"]
        summary = article["summary"]

        # format: Bold headline, link, source, summary
        formatted = f"<b>{title}</b><br>{link}<br>{source}<br><br>{summary}<br><br>"
        articles.append(formatted)

    if not articles:
        return "No articles found."

    news_tech = "<br>".join(articles)
    return news_tech


# Class for the Assistant Application


class AssistantApp(QWidget):
    def __init__(self):
        super().__init__()

        with open("style.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("My Personal Assistant")
        self.setGeometry(200, 100, 900, 600)

        # Main horizontal layout
        main_layout = QHBoxLayout(self)  # Main layout for the window

        # Left vertical layout
        left_layout = QVBoxLayout()

        # Assistant image
        self.image_label = QLabel()
        pixmap = QPixmap("img/01.png")
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.image_label)

        # chat input
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type your message here...")
        left_layout.addWidget(self.input_line)

        self.sendbutton = QPushButton("Send")
        left_layout.addWidget(self.sendbutton)
        self.sendbutton.clicked.connect(self.handle_send)  # connect button to handler

        # clear chat button
        self.clear_button = QPushButton("ClearChat")
        left_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(
            self.handle_clear
        )  # connect button to handler

        # Right pane (Results display)
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        right_layout = QVBoxLayout()

        # mood
        self.mood = "neutral"

        # chat history
        self.chat_history = [
            {"role": "system", "content": get_system_prompt(self.mood)}
        ]

        # Mood selector
        self.mood_selector = self.create_mood_selector()
        right_layout.addWidget(self.mood_selector)

        # Add layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.results_display)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    # Set Mood
    def set_mood(self, mood, checked):
        if checked:
            self.mood = mood
        # update system prompt for new mood and future replies
        self.chat_history[0]["content"] = get_system_prompt(self.mood)

    # Create Mood Selector
    def create_mood_selector(self):
        mood_group = QGroupBox("Select Mood")
        layout = QVBoxLayout()

        self.mood_buttons = {}

        for mood in MOOD_PROMPTS.keys():
            btn = QRadioButton(mood.capitalize())
            btn.toggled.connect(
                lambda checked, m=mood: self.set_mood(m, checked)
            )  # connect with lambda
            layout.addWidget(btn)
            self.mood_buttons[mood] = btn  # store button reference

        self.mood_buttons["neutral"].setChecked(True)  # default mood
        mood_group.setLayout(layout)
        return mood_group

    def handle_send(self):
        user_input = self.input_line.text()
        if not user_input:
            return  # ignore empty input

        # display user message
        self.results_display.append(f"<b>You:</b> {user_input}")

        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": user_input})

        # Check for Remember (save memory) and Recall (retrieve memory)
        if user_input.lower().startswith("remember "):
            memory = user_input[len("remember") :].strip()  # extract memory text
            add_memory(memory)
            self.results_display.append(
                f"<b>Sophie:</b> Got it! I’ll remember that you said: <i>{memory}</i>"
            )
            self.input_line.clear()
            return

        if user_input.lower().startswith("recall "):
            keyword = user_input[len("recall ") :].strip()
            results = search_memories(keyword)
            if results:
                formatted = "<br>".join(results)
                self.results_display.append(f"<b>Sophie (memories):</b><br>{formatted}")
                # append to chat history
                self.chat_history.append(
                    {"role": "assistant", "content": f"I remember: {formatted}"}
                )
            else:
                self.results_display.append(
                    f"<b>Sophie:</b> I don't recall anything about <i>{keyword}</i>."
                )
            self.input_line.clear()
            return  # skip further processing

        # Check if user requested tech news
        if "tech news" in user_input.lower():
            news_tech = get_tech_news()

            # Show formatted news directly in the chat
            self.results_display.append(f"<b>Sophie's Tech News:</b><br>{news_tech}")

            news_prompt = f"""
                Here are some tech news headlines:
                {news_tech}

                Please summarize the key points, and tell me which story seems most significant,
                without inventing events. Keep it concise, 1 - 2 paragraphs professional, but friendly.
                """

            # Compose messages: system prompt + task prompt
            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": news_prompt},
            ]
        else:
            # General chat: use chat history (system prompt is already in self.chat_history)
            messages = self.chat_history

        # Query Ollama (using a light model, e.g. phi3, mistral, etc.)
        try:
            response = ollama.chat(
                model="phi3", messages=messages
            )  # the history of the chat is sent to the assistant

            assistant_reply = response["message"]["content"]  # assistant's reply

            # Add assistant message to chat history
            self.chat_history.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            assistant_reply = (
                f"(<b>Error:</b> Unable to get a response from Ollama. {e})"
            )

        # display assistant response
        self.results_display.append(f"<b>Assistant:</b> {assistant_reply}")

        # clear input line
        self.input_line.clear()

    def handle_clear(self):
        # Reset chat history

        self.chat_history = [
            {"role": "system", "content": get_system_prompt(self.mood)}
        ]

        self.results_display.clear()  # clear the results(chat)

        # Let the user know chat has been reset
        self.results_display.append(
            "<i>You have just wiped out the chat and Sophie's memory of it!</i>"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)  # initialises the application
    window = AssistantApp()  # creates an instance of the AssistantApp
    window.show()  # displays the window
    sys.exit(app.exec())  # starts the application event loop
