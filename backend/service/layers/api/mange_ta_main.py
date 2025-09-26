from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from service.layers.domain.mange_ta_main import SERVICE_PREFIX

router = APIRouter(prefix="/" + SERVICE_PREFIX)


@router.get("/", response_class=PlainTextResponse)
async def root() -> str:
    return "My name is mange_ta_main!"
