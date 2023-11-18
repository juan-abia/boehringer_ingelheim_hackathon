from pathlib import Path
from langchain.globals import set_debug

CURR_DIR = Path(__file__)
SRC_DIR = CURR_DIR.parents[1]

DEBUG = True
set_debug(DEBUG)