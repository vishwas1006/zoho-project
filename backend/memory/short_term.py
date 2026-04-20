from langgraph.checkpoint.memory import MemorySaver

# LangGraph handles this via thread_id
# Each user session gets a unique thread_id
memory = MemorySaver()