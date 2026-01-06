# 🌀 Deep Travel Research Agent
An AI-powered travel consultant built with **LangGraph**, **Streamlit**, and **PostgreSQL**. This agent uses multi-agent orchestration to scope travel intents, perform deep web research via DuckDuckGo, and synthesize custom itineraries.

## ✨ Key Features
* **Three-Dimension Scoping:** Ensures every trip has a defined **Location, Timing, and Style** before research begins.
* **Context Stitching:** Remembers your destination (e.g., Bangkok) even if you provide details (e.g., "in December") across multiple turns.
* **Hybrid Research Modes:** * `Fast Mode`: Quick factual answers (weather, visas, cafes).
    * `Deep Mode`: Sequential web-searching and vector-embedding into Postgres.
* **Real-time Streaming UI:** Watch the agent's research plan and sub-questions update live in the Streamlit interface.

## 🛠️ Tech Stack
- **Framework:** [LangGraph](https://github.com/langchain-ai/langgraph) (Stateful Multi-Agent Orchestration)
- **Frontend:** [Streamlit](https://streamlit.io/)
- **LLM:** OpenAI GPT-4o-mini
- **Database:** PostgreSQL with `pgvector` for research memory
- **Search API:** DuckDuckGo Instant Answer API

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL instance running locally

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgres://username:password@localhost:5432/postgres
