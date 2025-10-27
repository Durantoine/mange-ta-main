from components.sidebar import render_sidebar
from components.tab02_duration_recipe import render_duration_recipe
from domain import BASE_URL
from logger import struct_logger

render_sidebar()
render_duration_recipe(logger=struct_logger)
