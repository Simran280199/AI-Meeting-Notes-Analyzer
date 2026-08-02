from state import MeetingState
from nodes import extract_topics, summarize_meeting, extract_action_items

sample_transcript = """John: We need to improve the website performance.
Sarah: Yes, page load time is too slow.
David: I will optimize the database queries this week.
Sarah: I will redesign the homepage layout.
John: Let's try to finish these tasks before Friday."""

initial_state: MeetingState = {
    "transcript": sample_transcript,
    "topics": [],
    "summary": "",
    "action_items": [],
    "priority": "",
    "final_report": ""
}

state_after_topics = extract_topics(initial_state)
state_after_summary = summarize_meeting(state_after_topics)
state_after_actions = extract_action_items(state_after_summary)

print("TOPICS:", state_after_actions["topics"])
print("SUMMARY:", state_after_actions["summary"])
print("ACTION ITEMS:", state_after_actions["action_items"])