import json
import os
from anthropic import AnthropicBedrock
import time
from datetime import date

from dotenv import load_dotenv

load_dotenv()

client = AnthropicBedrock(
    aws_access_key=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),  # optional
    aws_region=os.environ["AWS_REGION"],
)
model = "us.anthropic.claude-sonnet-4-6"

tools = [
    {
        "name": "create_calendar_event",
        "description": "Create Calendar event with attendees and optional recurrence",
        "input_schema":{
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date_time"},
                "end": {"type": "string", "format": "date_time"},
                "attendees": {
                    "type": "array", 
                    "items": {"type": "string", "format": "email"}
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "frequency": {"enum": ["daily", "weekly", "monthly"]},
                        "count": {"type": "integer", "minimum": 1},
                    },
                },
            },
            "required": ["title", "start", "end"], 
        },
    },
    {
        "name": "list_calendar_events",
        "description": "List all calendar events on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "get_current_date",
        "description": "Get the current date in YYYY-MM-DD format.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


def add_user_message(messages, data):
    user_message = {
            "role": "user",
            "content": data
        }
    messages.append(user_message)

def add_assistant_message(messages, data):
    assistant_message = {
            "role": "assistant",
            "content": data
        }
    messages.append(assistant_message)

SYSTEM_PROMPT = (
    "You are a calendar assistant. When a tool call fails or a constraint "
    "(e.g. attendee limits, permissions, conflicts) prevents you from "
    "fulfilling the request as stated, STOP and ask the user how to proceed. "
    "Do NOT invent workarounds, split events, drop attendees, or make "
    "assumptions on the user's behalf. Present the problem and any options, "
    "then wait for the user's decision."
)

def chat(messages):
    return client.messages.create(
        model = model,
        max_tokens = 1000,
        system=SYSTEM_PROMPT,
        tools=tools,
        tool_choice={"type": "auto"},
        messages = messages
    )

def run_tool(name, tool_input):
    if name == "create_calendar_event":
        if "attendees" in tool_input and len(tool_input["attendees"]) > 10:
            raise ValueError("Too Many (max 10)")
        return {"event_id": "evt_" + str(int(time.time())), "status": "created", "title": tool_input["title"]}
    if name == "list_calendar_events":
        return {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
    if name == "get_current_date":
        return {"todays_date": str(date.today())}
    return {"error": f"Unknown tool: {name}"}

messages = []

add_user_message(messages, "Schedule an all-hands with everyone Tomorrow at 10:00 AM: " + ", ".join(f"user{i}@example.com" for i in range(15)))

response = chat(messages)

while response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            try:
                result = run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
            except Exception as exc:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(exc),
                        "is_error": True,
                    }
                )


    add_assistant_message(messages, response.content)

    add_user_message(messages, tool_results)

    response = chat(messages)


print(response)
print(messages)


final_text = next(block for block in response.content if block.type == "text")
print(final_text.text)

