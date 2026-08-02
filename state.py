from typing import TypedDict, List, Dict

class MeetingState(TypedDict):
    transcript: str          # raw input text — set once, at the start
    topics: List[str]        # filled by the Topic Extraction Agent
    summary: str              # filled by the Meeting Summary Agent
    action_items: List[Dict[str, str]]   # each item: {"task": ..., "owner": ...}
    priority: str              # filled by the Priority Agent (may stay empty)
    final_report: str        # filled by the Final Output Node
