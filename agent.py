import json

from anthropic import Anthropic

from bq import fetch_forecast_vs_stock, fetch_recent_sales_summary

GEN_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are an inventory planning assistant for a retailer. You have tools "
    "to check recent sales and compare current stock vs. the demand forecast "
    "(BigQuery ML). Use the tools to answer with real numbers, never make up "
    "figures. Reply in English, direct and brief, like you're talking to a "
    "stock planner who already knows the business."
)

TOOLS = [
    {
        "name": "get_recent_sales_summary",
        "description": "Units sold per product category over the last N days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "How many days to look back. Default 14.",
                }
            },
        },
    },
    {
        "name": "check_overstock",
        "description": (
            "Current stock vs. the 14-day demand forecast per category. "
            "Use it to spot overstock risk (stock >> demand) or "
            "stockout risk (stock << demand)."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _execute_tool(name: str, tool_input: dict) -> list[dict]:
    if name == "get_recent_sales_summary":
        return fetch_recent_sales_summary(days=tool_input.get("days", 14))
    if name == "check_overstock":
        return fetch_forecast_vs_stock()
    raise ValueError(f"Unknown tool: {name}")


def run_turn(messages: list[dict]) -> tuple[list[dict], str, list[str]]:
    """Runs the tool-use loop for one user turn. Returns the updated message
    history, the assistant's final text reply, and the list of tools called."""
    client = Anthropic()
    tools_used = []

    while True:
        response = client.messages.create(
            model=GEN_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return messages, final_text, tools_used

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tools_used.append(block.name)
                result = _execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, default=str),
                })
        messages.append({"role": "user", "content": tool_results})
