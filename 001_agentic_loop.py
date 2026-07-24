import json
import os
from anthropic import AnthropicBedrock

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
        }
    }
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

def chat(messages):
    return client.messages.create(
        model = model,
        max_tokens = 1000,
        tools=tools,
        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        messages = messages
    )

def run_tool(name, tool_input):
    if name == "create_calendar_event":
        return {"event_id": "evt_123", "status": "created", "title": tool_input["title"]}
    return {"error": f"Unknown tool: {name}"}

messages = []

add_user_message(messages, "Schedule a weekly team standup every Monday at 9am for the next 4 weeks. Invite the whole team: alice@example.com, bob@example.com, carol@example.com.")

response = chat(messages)
 

while response.stop_reason == "tool_use":
    tool_use = next(block for block in response.content if block.type == "tool_use")
    result = run_tool(tool_use.name, tool_use.input)

    add_assistant_message(messages, response.content)

    add_user_message(messages, [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
    }])

    response = chat(messages)


print(response)
print(messages)


final_text = next(block for block in response.content if block.type == "text")
print(final_text.text)

