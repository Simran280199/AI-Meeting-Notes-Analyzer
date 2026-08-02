from state import MeetingState
from llm import llm


def extract_topics(state: MeetingState) -> MeetingState:
    transcript = state["transcript"]

    prompt = f"""You are analyzing a meeting transcript.
Identify the main discussion topics from the transcript below.
Return ONLY a numbered list of short topic phrases, nothing else.

Transcript:
{transcript}
"""

    response = llm.invoke(prompt)
    topics_text = response.content

    # Turn the numbered-list text into a clean Python list of strings
    topics = [
        line.split(".", 1)[-1].strip()
        for line in topics_text.split("\n")
        if line.strip()
    ]

    state["topics"] = topics
    return state

def summarize_meeting(state: MeetingState) -> MeetingState:
    transcript = state["transcript"]

    prompt = f"""You are summarizing a meeting transcript.
Write a concise 3-5 sentence summary covering what was discussed and any decisions made.
Do not include a list of action items or headers — just plain prose.

Transcript:
{transcript}
"""

    response = llm.invoke(prompt)
    state["summary"] = response.content.strip()
    return state

def extract_action_items(state: MeetingState) -> MeetingState:
    transcript = state["transcript"]

    prompt = f"""You are extracting action items from a meeting transcript.
List every task that someone committed to doing, along with who is responsible.

Return ONLY in this exact format, one item per line, nothing else:
Task | Owner

If no owner is mentioned for a task, write "Not specified" as the owner.
If there are no action items at all, return exactly: NONE

Transcript:
{transcript}
"""

    response = llm.invoke(prompt)
    items_text = response.content.strip()

    action_items = []

    if items_text != "NONE":
        for line in items_text.split("\n"):
            if line.strip() and "|" in line:
                task, owner = line.split("|", 1)
                action_items.append({
                    "task": task.strip(),
                    "owner": owner.strip()
                })

    state["action_items"] = action_items
    return state

def classify_priority(state: MeetingState) -> MeetingState:
    transcript = state["transcript"]
    action_items = state["action_items"]

    items_list = "\n".join(f"- {item['task']} ({item['owner']})" for item in action_items)

    prompt = f"""You are assessing the urgency of a meeting's action items.
Based on the transcript and the action items below, classify the OVERALL priority
of this meeting's tasks as exactly one word: High, Medium, or Low.

Return ONLY that single word, nothing else.

Transcript:
{transcript}

Action items:
{items_list}
"""

    response = llm.invoke(prompt)
    state["priority"] = response.content.strip()
    return state

def check_action_items(state: MeetingState) -> str:
    if state["action_items"]:
        return "has_items"
    else:
        return "no_items"

def generate_final_report(state: MeetingState) -> MeetingState:
    topics_text = "\n".join(f"- {t}" for t in state["topics"])

    if state["action_items"]:
        actions_text = "\n".join(
            f"- {item['task']} ({item['owner']})" for item in state["action_items"]
        )
        priority_text = state["priority"]
    else:
        actions_text = "No action items identified in this meeting."
        priority_text = "Not applicable"

    report = f"""MEETING NOTES SUMMARY

Topics Discussed:
{topics_text}

Summary:
{state['summary']}

Action Items:
{actions_text}

Priority:
{priority_text}
"""

    state["final_report"] = report.strip()
    return state