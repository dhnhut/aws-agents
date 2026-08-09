import boto3
import json

from tools.weather_forecasts import weather_forecast
from tools.top_attractions import top_attractions

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "amazon.nova-lite-v1:0"

SYSTEM_PROMPT = """\
You are a helpful travel assistant. Your job is to help the user plans short trips in a city.

Ask the user about their city they want to visit.
Use the available tools to look up weather information and check top attractions before making a recommendation.
Base your recommendation on tool results only — do not invent attraction names or weather information.
Once you have weather information and attraction details, provide a clear recommendation which places to visit based on the weather and attractions."""


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "toolSpec": {
            "name": "weather_forecast",
            "description": "Returns the weather forecast for a given city.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city for which to get the weather forecast.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date for which to get the weather forecast.",
                        },
                    },
                    "required": ["city", "date"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "top_attractions",
            "description": "Returns a list of top attractions for a given city.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city for which to get top attractions.",
                        }
                    },
                    "required": ["city"],
                }
            },
        }
    }
]


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------


def execute_tool(name: str, tool_input: dict) -> dict:
    print(f"Executing tool: {name} with input: {tool_input}")
    if name == "weather_forecast":
        return {"forecast": weather_forecast(tool_input["city"], tool_input["date"])}
    elif name == "top_attractions":
        return {"attractions": top_attractions(tool_input["city"])}
    else:
        return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Converse loop
# ---------------------------------------------------------------------------
def run_chat() -> None:
    messages = []

    print("Assistant: Hi! I can help you plan a trip to a city.\nWhat city would you like to visit?\n")

    # city = input("User: ")
    city = 'Auckland'  # Hardcoded for testing purposes
    date = '2026-08-14'  # Hardcoded for testing purposes
    print("Assistant: What date are you planning to visit?\n")

    messages.append({"role": "user", "content": [{"text": f"{city} on {date}"}]})
    

    # Inner loop: keep calling Converse until the model finishes its turn.
    # The model may call multiple tools before producing a final response.
    while True:
        print("\n[Calling Converse API...]")
        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=messages,
            toolConfig={"tools": TOOLS},
        )

        stop_reason = response["stopReason"]
        output_message = response["output"]["message"]
        messages.append(output_message)

        if stop_reason == "end_turn":
            for block in output_message["content"]:
                if "text" in block:
                    print(f"\nTravel Assistant: {block['text']}\n")
            break

        elif stop_reason == "tool_use":
            tool_results = []

            for block in output_message["content"]:
                if "toolUse" in block:
                    tool_name = block["toolUse"]["name"]
                    tool_input = block["toolUse"]["input"]
                    tool_use_id = block["toolUse"]["toolUseId"]

                    print(f"  [tool call] {tool_name}({tool_input})")
                    result = execute_tool(tool_name, tool_input)
                    print(f"  [tool result] {result}")

                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": [{"json": result}],
                        }
                    })

            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    run_chat()
