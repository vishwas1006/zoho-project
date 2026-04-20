from sqlalchemy.ext.asyncio import create_async_engine
from config import settings

class LongTermMemory:
    def __init__(self):
        self.engine = create_async_engine(settings.database_url)

    async def save_preference(self, user_id: str, key: str, value: str):
        # Save to DB
        pass

    async def get_preferences(self, user_id: str) -> dict:
        # Load from DB
        pass