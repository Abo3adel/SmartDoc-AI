# AI Document Analyzer (Full-Stack LLM API)

## 📌 Project Overview
A robust full-stack document analysis system built with **FastAPI** (Backend) and **Gradio** (Frontend), implementing Clean Architecture principles and Smart API Orchestration.

## ✨ Features
* **Modular Clean Architecture**: Separation of concerns (`api`, `services`, `schemas`).
* **Smart UI Orchestration**: The frontend gracefully handles missing data without forcing the user into rigid flows.
* **Dynamic RTL/LTR UI**: Automatic language detection to adjust text alignment and formatting for Arabic and English outputs.
* **Structured LLM Outputs**: Utilizing Pydantic models for strict JSON validation and robust error handling.

## 📂 Project Structure

```text
SmartDoc-AI/
│
├── api/                  # FastAPI routers and endpoint definitions
│   └── routes.py         # Handles /upload, /summarize, /translate, /quiz
├── core/                 # Core configurations and app settings
│   └── config.py         # Environment variables and API keys setup
├── schemas/              # Pydantic models for strict data validation
│   └── models.py         # Request/Response schemas and structured LLM outputs
├── services/             # Business logic and external API integrations
│   └── llm_service.py    # Functions handling OpenAI API communication
│
├── main.py               # FastAPI application entry point
├── front.py              # Gradio dynamic web interface (RTL/LTR support)
├── requirements.txt      # Project dependencies and libraries
├── .env                  # Environment variables (Not tracked in Git)
└── README.md             # Project documentation
```

## 🛠️ Tech Stack

This project leverages a modern, highly efficient Python ecosystem, organized by their respective roles in the system architecture:

**Backend & API Routing**
* **[FastAPI](https://fastapi.tiangolo.com/):** High-performance web framework used for building the core RESTful API.
* **Uvicorn:** Lightning-fast ASGI server implementation to serve the FastAPI application.

**Frontend & User Interface**
* **Gradio:** Rapid UI development framework used to build the interactive, dynamic (RTL/LTR) web interface.
* **Jinja2:** Templating engine for rendering robust web components.

**AI & LLM Integration**
* **OpenAI Python SDK:** The official client used for seamless communication with OpenAI's language models.

**Data Validation & Serialization**
* **Pydantic:** Guarantees data integrity and forces strict JSON schema validation for all LLM outputs and API responses.

**Core Utilities & Environment Management**
* **python-dotenv:** Secure management of environment variables and API keys.
* **Requests & HTTPX:** Handling synchronous and asynchronous HTTP requests across the network.



## 🚀 How to Run Locally

### 1. Set up the Environment Variables
Create a .env file in the root directory of the project and add your OpenAI API key:
OPENAI_API_KEY=your_api_key_here

### 2. Install Dependencies
Open your terminal (ensure your virtual environment is activated) and install the required packages:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Run the Backend Server
In your terminal, start the FastAPI server using Uvicorn:
  ```bash
  uvicorn main:app --reload
  ```


(The backend API will now be running and listening at http://127.0.0.1:8000)

### 4. Run the Frontend Interface
Open a new, separate terminal, ensure your virtual environment is active, and launch the Gradio UI:
  ```bash
  python front.py
  ```


(Click on the provided local URL in your terminal to open the web app in your browser)
