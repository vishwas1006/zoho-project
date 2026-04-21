# backend/memory/short_term.py

from langgraph.checkpoint.memory import MemorySaver

# LangGraph uses this to remember context within a session
# Each user gets a unique thread_id (their session_id)
# Automatically remembers:
# - which project they were talking about
# - previous messages in the conversation
# - any context carried across turns

short_term_memory = MemorySaver()