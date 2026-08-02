from langgraph.graph import StateGraph, END
from state import MeetingState
from nodes import (
    extract_topics,
    summarize_meeting,
    extract_action_items,
    classify_priority,
    check_action_items,
    generate_final_report
)

# 1. Create a graph builder, telling it what shape our "baton" is
builder = StateGraph(MeetingState)

# 2. Register every node — giving each a name, and pointing to its function
builder.add_node("extract_topics", extract_topics)
builder.add_node("summarize_meeting", summarize_meeting)
builder.add_node("extract_action_items", extract_action_items)
builder.add_node("classify_priority", classify_priority)
builder.add_node("generate_final_report", generate_final_report)

# 3. Set the entry point — where the graph starts
builder.set_entry_point("extract_topics")

# 4. Fixed edges — always go from A to B, no decision needed
builder.add_edge("extract_topics", "summarize_meeting")
builder.add_edge("summarize_meeting", "extract_action_items")

# 5. The conditional edge — the one decision point in our whole graph
builder.add_conditional_edges(
    "extract_action_items",
    check_action_items,
    {
        "has_items": "classify_priority",
        "no_items": "generate_final_report"
    }
)

# 6. After priority classification, always go to the final report
builder.add_edge("classify_priority", "generate_final_report")

# 7. After the final report, the graph is done
builder.add_edge("generate_final_report", END)

# 8. Compile it into a runnable object
graph = builder.compile()