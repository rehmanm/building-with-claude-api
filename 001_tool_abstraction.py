import json
import os
import time
from anthropic import Anthropic, beta_tool
from datetime import date

from dotenv import load_dotenv

load_dotenv()

### Tool Runner is not available for Anthropic Bedrock

client = Anthropic(
    aws_access_key=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),  # optional
    aws_region=os.environ["AWS_REGION"],
)
model = "us.anthropic.claude-sonnet-4-6"

@beta_tool
def create_calendar_events(
    title: str,
    start: str,
    end: str,
    attendees: list[str] = None,
    recurrences: dict | None = None
) -> str:
    """Create a calendar event with attendees and optional recurrence.

    Args:
        title: Event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        attendees: Email addresses to invite.
        recurrence: Dict with 'frequency' (daily, weekly, monthly) and 'count'.
    """

    if attendees and len(attendees) > 10:
        raise ValueError("Too Many (max 10)")
    
    return {"event_id": "evt_" + str(int(time.time())), "status": "created", "title": title}

@beta_tool
def get_current_date() -> str:
    return {"todays_date": str(date.today())}

@beta_tool
def list_calendar_events(date: str) -> str:
    """List all calendar events on a given date.

    Args:
        date: Date in YYYY-MM-DD format.
    """
    return json.dumps({"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]})


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
    return client.beta.messages.tool_runner(
        model = model,
        max_tokens = 1000,
        tools=[create_calendar_events, list_calendar_events, get_current_date],
        messages = messages
    ).until_done()

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