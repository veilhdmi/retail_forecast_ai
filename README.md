# Stock Planner AI

A chat assistant for inventory planning. Instead of scrolling through dashboards to figure out what's about to run out (or what's been sitting in a warehouse too long), you just ask it in plain language and it goes and checks the real numbers in BigQuery before answering.

## Demo

![Stock Planner AI answering a question about overstock risk](assets/demo.png)

*(drop your screenshot at `assets/demo.png`)*

## Why I built this

Most "AI + data" demos I kept seeing were either a chatbot with no real data behind it, or a dashboard with no chat. I wanted to combine the two properly: a small dbt project that builds real marts on top of a public retail dataset, a BigQuery ML model that forecasts demand per category, and an agent on top that decides which query to run depending on what you asked — instead of an LLM hallucinating numbers, or me writing a rigid form with 10 filters nobody wants to touch.

## How it works

1. A companion dbt project (not in this repo) reads `bigquery-public-data.thelook_ecommerce`, a public e-commerce dataset, and builds staging models plus three marts: daily sales by category, current stock by category, and a 14-day demand forecast trained with BigQuery ML's `ARIMA_PLUS`.
2. This app is the front end for those marts. Claude (Haiku) gets two tools — "get recent sales" and "check overstock/understock" — and decides on its own which one(s) it needs based on your question.
3. The tool results (actual rows from BigQuery) get fed back to the model, which turns them into a normal, direct answer instead of a wall of numbers.
4. Everything renders in a simple Streamlit chat, so you can keep asking follow-up questions in the same conversation.

Nothing here forecasts with an LLM — that part is still plain statistical modeling in BigQuery ML, which is what it's actually good at. The LLM's only job is understanding the question and explaining the result.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_APPLICATION_CREDENTIALS=path-to-your-bigquery-service-account-key.json
GCP_PROJECT=your-gcp-project-id
```

You'll also need the dbt marts already built in your own BigQuery project (`marts.fct_daily_category_sales`, `marts.dim_current_stock`, `marts.fct_demand_forecast`) — BigQuery's free sandbox tier is enough to run all of this without a credit card.

Run it:

```bash
streamlit run app.py
```

## Stack

- **BigQuery** (free sandbox tier) + **BigQuery ML** for the forecast
- **dbt** for the staging/marts layer
- **Claude Haiku** (Anthropic API) as the tool-calling agent
- **Streamlit** for the chat UI

## Sample questions

- "¿qué categorías están en riesgo de quiebre de stock?"
- "cuáles fueron las categorías más vendidas en los últimos 30 días?"
- "hay algo con overstock que debería preocuparme?"
