from fastapi import FastAPI
from service.layers.logger import struct_logger



from service.layers.api import mange_ta_main

app = FastAPI()

app.include_router(mange_ta_main.router)

struct_logger.info("App starting...")