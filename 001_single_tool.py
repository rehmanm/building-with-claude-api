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

messages = []

add_user_message(messages, "Schedule a 30-minute sync with alice@example.com and bob@example.com next Monday at 10am.")

response = chat(messages)
 

# When Claude calls a tool, the response has stop_reason "tool_use"
# and the content array contains a tool_use block alongside any text.
print(f"stop_reason: {response.stop_reason}")

# Find the tool_use block. A response may contain text blocks before the
# tool_use block, so scan the content array rather than assuming position.
tool_use = next(block for block in response.content if block.type == "tool_use")
print(f"Tool: {tool_use.name}")
print(f"Input: {tool_use.input}")

# Execute the tool. In a real system this would call your calendar API.
# Here the result is hardcoded to keep the example self-contained.
result = {"event_id": "evt_123", "status": "created"}


add_assistant_message(messages, response.content)

add_user_message(messages, [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
}])

followup = chat(messages)

print(f"stop_reason: {followup.stop_reason}")
final_text = next(block for block in followup.content if block.type == "text")
print("Text", final_text.text)