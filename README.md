
# Persona Adaptive AI Chat Application

This is a Flask web application that replicates some of the basic features of ChatGPT, a popular AI-powered conversational assistant. The application allows users to register, log in, create new conversations with a chatbot, and view their conversation history.

## Features

- User registration and authentication
- Create your own personas
- Upload Knowledge Base
- Create new conversations
- View conversation history
- AI Chatting

## Prerequisites

Before running the application, make sure you have the required libraries installed. You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Quickstart


1. Navigate to the project directory:

```bash
cd app
```

2. Set the `OPENAI_API_KEY` environment variable with your OpenAI key:

```bash
export SECRET_KEY=sk-********
```

5. Run the application:

```bash
python app.py
```

The application should now be running at `http://localhost:5000`.

## Usage

1. Register a new account by clicking the "Register" link on the home page.
2. Log in with your credentials.
3. On the "Data" page, click the "Upload Data" button to upload a new knowledge base.
4. On the "Persona" page, click the "Create New Persona" button to create a new persona. Optionally, connect a knowledge base to the persona.
5. In the "Chat" page, click the "Start New Chat" button to start a new conversation and select the persona of your choice. Give a name to your conversation.
6. Type your message in the input field and send to chat with the chatbot.


## License

This project is licensed under the [MIT License](LICENSE).
