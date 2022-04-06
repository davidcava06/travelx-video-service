import json
from typing import Any, Optional, Type, Union

from marshmallow import Schema
from starlette.requests import Request
from starlette.responses import JSONResponse

from api import exceptions, config, logging

log = logging.get_logger(__name__)


class APIResponse(JSONResponse):
    media_type = "application/json"

    def __init__(self, schema: Optional[Schema] = None, *args, **kwargs):
        self.schema = schema
        super().__init__(*args, **kwargs)

    def render(self, content: Any):
        if self.schema is not None:
            content = self.schema.dump(content)

        if content is None:
            return b""
        return super().render(content)


async def deserialize_payload(
    request: Request, schema: Union[Schema, Type[Schema]], partial=False
):
    """Loads the JSON payload and deserializes it using a schema.

    :param request Request: The Starlette request.
    :param schema Schema: The Marshmallow schema.
    :returns: The deserialized payload.
    :raises: BadRequest if no payload and ValidationError on deserialization error.
    """
    json_data = await get_payload_from_request(request)
    if not isinstance(schema, Schema):
        # instantiante the schema if necessary
        schema = schema()

    return schema.load(json_data, partial=partial)


async def get_payload_from_request(request: Request):
    """Retrives the JSON payload from the request.

    Raises BadRequest on errors.
    """
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        raise exceptions.BadRequest("Body must be json")
    else:
        return json_data
