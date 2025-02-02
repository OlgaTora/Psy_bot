from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from config import config
from bot import results, check_imei_tg_from_api

imei_router = APIRouter(
    prefix="",
    tags=["check_imei"],
    responses={404: {"description": "Not found"}},
)


class CheckRequest(BaseModel):
    imei: str
    token: str


@imei_router.post(config.webhook_url, response_class=JSONResponse)
async def check_imei(request: CheckRequest):
    if request.token != config.telegram_bot_token:
        return {"status": "error", "message": "Wrong secret token !"}
    else:
        await check_imei_tg_from_api(request.imei)
        item = await results.get()
        return item
