import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from starlette.responses import RedirectResponse

from routers import imei_router
from bot import run_bot


@asynccontextmanager
async def lifespan(app):
    print("Start")
    asyncio.create_task(run_bot())
    yield
    print("Stop")


app = FastAPI(lifespan=lifespan)
app.include_router(imei_router)


@app.get('/')
async def index():
    return RedirectResponse(url='/docs')

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
