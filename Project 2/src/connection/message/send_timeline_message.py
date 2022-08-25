from __future__ import annotations
from typing import Dict, Tuple, TYPE_CHECKING

from src.connection.message.message import MessageInterface, MessageType

if TYPE_CHECKING:
    from src.api.user import User, UserData
    from src.api.timeline import TimelineMessage
    from src.connection.message.snowflake import Snowflake

class SendTimelineMessage(MessageInterface):
    def __init__(self, user : User) -> None:
        super().__init__(user)

    def build(self, message : str, snowflake : Snowflake) -> Tuple[Dict[str, UserData], TimelineMessage]:
        username = self.user.username
        snowflake_id, snowflake_time = snowflake.get_id(username, self.user.get_number_posts())
        
        signature = self.user.sign(message)
        msg = {
            'header': {
                'id': snowflake_id,
                'user': username,
                'signature': signature,
                'time': snowflake_time,
                'seen': False,
                'type': MessageType.TIMELINE_MESSAGE.value,
            },
            'content': message
        }

        return msg

    