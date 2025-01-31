from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan():
    print("Starting application")
    # await run_bot()
    yield
    print("Stopping application")

app = FastAPI(lifespan=lifespan)
# app.include_router(imei_router)