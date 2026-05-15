# app/events/contracts/base.py

from pydantic import BaseModel
from typing import Literal, Optional


class BaseEvent(BaseModel):
    event_type: str
    raw: dict

