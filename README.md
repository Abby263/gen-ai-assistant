# OmniAssist: All-in-One AI Personal Assistant

**Imagine an assistant that seamlessly manages your emails 📧, schedule 📅, to-do lists ✅, Slack messages 💬, conducts online research 🔍, and even answers questions from your files—all through your favorite messaging apps. Welcome to OmniAssist!**

**That's EXACTLY what this AI Personal Assistant does! 🤖✨**

<p align="center">
  <img src="flowchart/AI Assistant.png" alt="OmniAssist Architecture">
</p>

This project provides a personal assistant agent that manages tasks related to your email inbox, calendar, Notion to-do list, Slack interactions, and handles any research you may have. The assistant communicates with you via your preferred communication channel **(Telegram, Slack, or WhatsApp)**, keeping you informed about your schedule, tasks, emails, messages, and helping with research topics, people, or even companies.

The personal assistant is a **hierarchical multi-agents** system with a **supervisor agent** (manager) and several sub-agents that handle specific tasks for efficient task management.

## Overview

### Main Agent: Assistant Manager

The Assistant Manager is your personal assistant that orchestrates the tasks and communication between you and the sub-agents. The manager is responsible for:

- Receiving and analyzing your messages from your chosen communication channel.
- Delegating tasks to the appropriate sub-agent (Email, Calendar, Notion, Slack, or Researcher).
- Communicating updates, messages, and any queries back to you via your preferred channel.

### Sub-Agents

The manager agent can communicate with six specialized sub-agents:

1. **Email Agent:** Can handle all your email-related tasks, including sending emails, retrieving specific emails, and checking for important messages from your contacts list.

2. **Calendar Agent:** Can manage your calendar by creating new events and retrieving and checking your scheduled events.

3. **Notion Agent:** Can manage your to-do list in Notion, helping you add, remove, or check tasks as needed.

4. **Slack Agent:** Can manage your Slack interactions by reading messages from channels or DMs and sending messages on your behalf.

5. **Researcher Agent:** Can perform web research, scrape websites, and gather information from LinkedIn profiles to assist with research tasks.

6. **RAG Agent:** Can search and retrieve information from your knowledge base, including documents, spreadsheets, and images, providing answers with source citations.

All the sub-agents report back to the Assistant Manager after completing their respective tasks.

### Using the RAG Agent

The RAG (Retrieval Augmented Generation) agent allows you to query your personal knowledge base through any messaging channel. Here's how to use it:

1. **Set Up Your Knowledge Base**
   ```bash
   # Create the data directory structure
   mkdir -p data/{documents,images,spreadsheets}
   ```

2. **Add Your Documents**
   - Place files in appropriate directories:
     ```
     data/
     ├── documents/    # PDFs, Word docs, text files
     │   ├── reports.pdf
     │   ├── documentation.docx
     │   └── notes.txt
     ├── images/      # Images with text or diagrams
     │   ├── diagrams.png
     │   └── screenshots.jpg
     └── spreadsheets/  # Data files
         └── data.csv
     ```

3. **Query Your Knowledge Base**
   - Ask questions through your configured channel (Telegram/Slack/WhatsApp):
     ```
     "What are the key findings in the Q4 report?"
     "Show me the project timeline from the documentation"
     "What metrics are tracked in the sales spreadsheet?"
     ```

4. **Understanding Responses**
   - The RAG agent will:
     - Search relevant documents
     - Provide answers with context
     - Include source citations
     - Highlight any uncertainties

5. **Best Practices**
   - Use clear, specific questions
   - Mention document types when known
   - Ask for clarification if needed
   - Keep documents organized in correct folders

### File Type Support

The RAG agent can process:
- **Documents:** PDF (.pdf), Word (.docx), Text (.txt)
- **Spreadsheets:** CSV (.csv)
- **Images:** JPG (.jpg, .jpeg), PNG (.png)

### Limitations

- Maximum file size: 100MB per file
- Image text must be clear and readable
- Processing time varies with document size
- Some complex tables or charts may not be fully interpreted

## Tech Stack

-   **LangGraph & LangChain**: Frameworks used for building the AI agents and interacting with LLMs (GPT-4, Llama 3, Gemini).
-   **LangSmith**: For monitoring the different LLM calls and AI agents' interactions.
-   **Google APIs**: Provides access to Google services like Calendar, Contacts, and Gmail.
-   **Notion Client**: Interface for interacting with Notion to manage and update to-do lists.
-   **Slack SDK**: For interacting with Slack, sending and receiving messages.
-   **Tavily Search API**: For performing web searches.
-   **Telegram API**: Depending on your choice of communication channel.
-   **WhatsApp API via Twilio Sandbox (for testing)**: A way to integrate WhatsApp communication.
-   **ChromaDB**: Vector store for document embeddings and retrieval
-   **Unstructured**: For processing various document formats
-   **OpenAI Embeddings**: For text and image vectorization

## How to Run

### Prerequisites

-   Python 3.9+
-   Your preferred LLM provider API keys (OpenAI, Claude, Gemini, Groq,...)
-   Google API credentials (for Calendar, Contacts, and Gmail access)
-   Notion API key
-   Tavily API key (for web research)
-   Slack Bot User OAuth Token and App Token
-   Telegram Bot Token (If you want to use telegram)
-   Twilio Account SID and Auth Token (If you want to test with WhatsApp)
-   Necessary Python libraries (listed in `requirements.txt`)
-   Tesseract OCR (for image processing)
-   Sufficient storage for document embeddings

### Setup

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/Abby263/gen-ai-assistant.git
    cd gen-ai-assistant
    ```

2.  **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add your API keys, see `.env.example` to know all the parameters you will need.

5.  **Configure Google API Credentials:**
    To integrate Google Calendar, Contacts, and Gmail APIs, you'll need a `credentials.json` file containing OAuth 2.0 credentials. Follow these steps:
    
    1. **Set Up a Google Cloud Project:**
       - Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
       - Click on the project dropdown at the top and select "New Project."
       - Provide a name for your project and click "Create."
    
    2. **Enable the Required APIs:**
       - In the left-hand menu, go to **APIs & Services > Library.**
       - Search for "Google Calendar API" and click **Enable.**
       - Similarly, search for "Gmail API" and click **Enable.**
    
    3. **Configure the OAuth Consent Screen:**
       - In the **APIs & Services** menu, select **OAuth consent screen.**
       - Choose **External** for the user type and click **Create.**
       - Fill in the required fields, such as **App Name** and **User Support Email.**
       - Under **Scopes**, add the necessary scopes for Calendar, Contacts, and Gmail.
       - Save your changes.
    
    4. **Create OAuth Client Credentials:**
       - Navigate to **APIs & Services > Credentials.**
       - Click on **Create credentials** and select **OAuth client ID.**
       - Choose **Desktop app** as the application type.
       - Provide a name and click **Create.**
    
    5. **Download the `credentials.json` File:**
       - After creating the credentials, click **Download JSON** to obtain your `credentials.json` file.
       - **Important:** Do not share or commit this file publicly as it contains sensitive information.
    
    6. **Place the `credentials.json` File in Your Project:**
       - Save the `credentials.json` file securely in your project's working directory.
       - Ensure your application references this file when authenticating API requests.

6.  **Set up Communication Channel:**

    -   **Telegram:**
        **Telegram Bot Setup:**
        1. **Create a New Telegram Bot and Obtain the Bot Token:**
           - Open the Telegram app and search for [@BotFather](https://t.me/BotFather).
           - Start a chat with BotFather by sending the `/start` command.
           - Send the command `/newbot` to create a new bot.
           - Follow the prompts to choose a name and a unique username (the username must end with "bot").
           - Once completed, BotFather will provide you with a unique API token. This token is required for authenticating your bot with the Telegram API.

        2. **Obtain the Chat ID:**
           - **For a Private Chat:** Start a conversation with your bot by sending any message. Then, open your web browser and navigate to:
             ```
             https://api.telegram.org/bot<YourBotToken>/getUpdates
             ```
             (Replace `<YourBotToken>` with the token you received.) Look in the JSON response for the "chat" object and find the "id" field; this is your chat ID.
           - **For a Group Chat:** Add your bot to the group and send a message within the group. Use the same `getUpdates` method to retrieve the group chat's ID (note that group chat IDs are often negative numbers).
           - **For a Channel:** Add your bot to the channel, send a message, and retrieve the chat ID using the same method.

        3. **Configure Your Bot with the Token and Chat ID:**
           - In your project's `.env` file, update the values for `TELEGRAM_TOKEN` and `CHAT_ID`:
             ```env
             TELEGRAM_TOKEN="your_bot_token_here"
             CHAT_ID="your_chat_id_here"
             ```

        4. **Test Sending a Message Using Your Bot:**
           - Use a simple Python script to send a test message:
             ```python
             import requests

             TELEGRAM_TOKEN = "your_bot_token_here"
             CHAT_ID = "your_chat_id_here"

             def send_message(token, chat_id, text):
                 url = f"https://api.telegram.org/bot{token}/sendMessage"
                 payload = { 'chat_id': chat_id, 'text': text }
                 response = requests.post(url, data=payload)
                 return response.json()

             # Usage
             send_message(TELEGRAM_TOKEN, CHAT_ID, "Hello, World!")
             ```

By following these steps, you'll successfully set up your Telegram bot with the required token and chat ID to facilitate communication with OmniAssist.

    -   **Slack:**
        -   Create a Slack App: Follow the official Slack documentation to create a new Slack app, add the necessary OAuth scopes (refer to the provided code and documentation for the required scopes).
        -   Install the app to your workspace and obtain your Bot User OAuth Token and App-Level Token.
    -   **WhatsApp (via Twilio Sandbox for Testing):**
        - **Important Note:** Normally, interacting with the **WhatsApp Business API** requires a **Meta Business Account**. However, for **testing purposes only**, this project utilizes the Twilio WhatsApp Sandbox.
        - **Twilio Sandbox Limitations:**  As stated in the [Twilio documentation](https://www.twilio.com/docs/whatsapp/sandbox), "Use the Twilio Sandbox for WhatsApp for testing and discovery purposes only. You should not use it in production."
        - **Setup:**
          1.  Create a Twilio account and obtain your Account SID and Auth Token.
          2.  Follow Twilio's tutorial to set up the WhatsApp Sandbox: [Twilio WhatsApp Sandbox Setup](https://www.twilio.com/docs/whatsapp/sandbox).
          3.  Save your Twilio Account SID, Auth Token and Sandbox number in your `.env` file.

7.  **Run the project**:
    - For running the personal assistant on **Slack or Telegram** you'll only need to run:

      ```bash
      python app.py
      ```

    - For running the personal assistant on **whatsApp** you'll need to run:

      ```bash
      python run app_whatsapp.py
      ```

      This will spin out a local fastAPI server, to enable the communication with the Twilio servers you need to make it public using **Ngrok**:

      1. Expose the Webhook URL Using ngrok

         ```bash
         ngrok http 5000
         ```
      2. Configure Twilio Webhook

         1. Go to the Twilio Console > Messaging > Sandbox for WhatsApp.
         2. In the Sandbox settings section: Set the "WHEN A MESSAGE COMES IN" URL to your ngrok URL and save your configuration.
      
      **You're done now you can talk with your assistant via whatsApp**

### Usage

**Communicating with the Assistant**: Simply send a message to your configured communication channel (Telegram, Slack channel, or WhatsApp), and the assistant will analyze the message, delegate the tasks to the appropriate sub-agents, and report back to you with the results.