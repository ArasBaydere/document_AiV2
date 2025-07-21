# Nokta Specification Assistant (document_AiV2)

## Project Overview

**Nokta Specification Assistant** is an AI-powered web application designed to analyze technical specification documents (.docx or text input), extract relevant product categories and key technical features, and recommend the most suitable products from a structured database. The system leverages Google Gemini LLM for advanced document understanding and product matching, providing a modern, chat-based user experience.

---

## Features

- **User Authentication:** Simple session-based login system (credentials stored in plain text for demo purposes).
- **Chat-Based Workflow:** Each user can manage multiple chat sessions, view history, rename, or delete conversations.
- **Document & Text Analysis:** Upload .docx files or enter text to extract categories and technical requirements.
- **AI-Driven Matching:** Uses Gemini API to extract categories/specs and match with products in the SQL database.
- **Hierarchical Category & Product Management:** Relational models for products and categories, supporting parent-child hierarchies.
- **Debug & Logging Panel:** In-app debug log panel for monitoring backend events and errors.
- **Modern Responsive UI:** Clean, mobile-friendly interface with real-time chat and file upload support.

---

## Architecture

- **Backend:** Python (Flask), SQLAlchemy ORM, MySQL (default, configurable), Google Gemini API integration.
- **Frontend:** HTML5, CSS3, Vanilla JS (single-page chat interface), Jinja2 templates.
- **Deployment:** Waitress WSGI server for production, Flask built-in server for development.

---

## Installation

1. **Clone the Repository**
   ```sh
   git clone https://github.com/ArasBaydere/document_AiV2.git
   cd document_AiV2
   ```

2. **Install Dependencies**
   If `requirements.txt` is missing, install manually:
   ```sh
   pip install flask flask_sqlalchemy python-docx google-generativeai pymysql waitress
   ```

3. **Database Configuration**
   - Edit `config.py` and set your MySQL connection string:
     ```python
     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://USER:PASSWORD@localhost:3306/DATABASE_NAME'
     ```
   - Tables are auto-created on first run.

4. **Gemini API Key**
   - Replace the `GEMINI_API_KEY` in `config.py` with your Google Gemini API key.
   - For production, use environment variables for secrets.

5. **Run the Application**
   - For development:
     ```sh
     python app.py
     ```
   - For production (Waitress):
     ```sh
     python run.py
     ```
   - Default ports: 5000 (dev), 8000 (prod)

---

## Usage

- **Login:** Access `/login` and authenticate with a username and password.
- **Start a Chat:** Create a new chat, upload a specification document or enter text.
- **AI Analysis:** The system extracts categories and technical specs, matches with products, and returns recommendations.
- **Debug Panel:** View backend logs and errors via the debug panel in the UI.

---

## Core Directory Structure

```
document_AiV2/
│
├── app.py                # Main Flask application entry point
├── run.py                # Production entry (Waitress WSGI)
├── config.py             # Configuration (DB, API keys, etc.)
├── models.py             # SQLAlchemy ORM models (Product, Category, Chat, Message)
├── utils.py              # Utility functions (logging, file processing, decorators)
├── services/
│   └── gemini_service.py # Google Gemini API integration and prompt logic
├── routes/
│   ├── auth.py           # Authentication routes (login/logout)
│   └── chat.py           # Chat and API endpoints (chat, message, file upload)
├── templates/
│   ├── index.html        # Main chat UI (Jinja2)
│   └── login.html        # Login page
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # Frontend logic (chat, AJAX, UI)
└── uploads/              # Uploaded files (created at runtime)
```

---

## Technical Details

- **Authentication:** Session-based, no password hashing (for demo only).
- **Database Models:**
  - `Category`: Hierarchical, supports parent-child relationships.
  - `Product`: Linked to categories, stores product code, name, features, and info.
  - `ChatSession` & `Message`: Store user chat history and messages.
- **AI Integration:**
  - `GeminiService` handles prompt engineering, category/spec extraction, and product recommendation using Google Gemini LLM.
  - Multi-stage pipeline: (1) Extract categories/specs, (2) Filter products by category/specs, (3) Final recommendation and justification.
- **File Handling:** Only `.docx` files are supported for document upload and parsing.
- **Logging:** In-memory debug log with UI panel for real-time monitoring.

---

## Security Notes

- **Passwords are stored in plain text!** Do NOT use in production without implementing secure password hashing and user management.
- **API keys and DB credentials should be managed via environment variables in production.**
- **No license specified.** Contact the author for usage or contribution.

---

## Contribution

This repository is not open source. For collaboration or feature requests, please contact the project owner.

--- 