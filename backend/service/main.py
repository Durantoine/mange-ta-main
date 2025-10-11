from contextlib import asynccontextmanager

from fastapi import FastAPI

from service.container import Container
from service.layers.api.mange_ta_main import router
from service.layers.logger import struct_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container = Container()
    app.state.container = container
    struct_logger.info("Preloading data at startup...")
    container.data_analyzer()
    struct_logger.info("Data preloaded successfully")
    yield
    # Shutdown
    struct_logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

struct_logger.info("App starting...")

app.include_router(router)
