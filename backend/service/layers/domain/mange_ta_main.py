from enum import StrEnum
from typing import Annotated, Any, Union
from pydantic import BaseModel, Field
import pandas as pd

SERVICE_PREFIX = "mange_ta_main"

class PayloadTypes(StrEnum):
    TABLE = "table"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    SCATTER = "scatter"
    PIE = "pie"

class PacketTypes(StrEnum):
    UPDATE = "update"
    EVENT = "event"
    RESPONSE = "response"
    COMMAND = "command"

class DataFramePayload(BaseModel):
    name: str
    payload: Any
    type: PayloadTypes

    def to_json(self) -> str:
        return self.payload.to_json(orient="records")


class DataPacket(BaseModel):
    type: PacketTypes
    payload: Annotated[
        Union[DataFramePayload, dict, str, None],
        Field(default=None, description="The actual data payload to send.")
    ]

    def to_json(self) -> dict:
        if isinstance(self.payload, DataFramePayload):
            payload_dict = self.payload.model_dump()
            payload_dict["payload"] = self.payload.to_json()
            return {"type": self.type.value, "payload": payload_dict}
        return self.model_dump()