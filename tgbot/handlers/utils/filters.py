from datetime import datetime, time
from typing import Optional, Union, Dict

from telegram import Message
from telegram.ext import MessageFilter


class TimeFilter(MessageFilter):

    def __init__(
        self,
        time_start: Optional[time] = None,
        time_end: Optional[time] = None,
        weekday: Optional[int] = None
    ):
        self.time_start = time_start
        self.time_end = time_end
        self.weekday = weekday

    def filter(self, message: Message) -> Optional[Union[bool, Dict]]:
        now = datetime.now()
        return (
            (self.time_start is None or self.time_start < now.time())
            and (self.time_end is None or now.time() >= self.time_end)
            and (self.weekday is None or self.weekday == now.weekday())
        )
