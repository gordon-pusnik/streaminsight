# app/utils/logging.py

import logging
import sys

# Create a logger
logger = logging.getLogger("streaminsight")
logger.setLevel(logging.INFO)

# Create a console handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to the logger
if not logger.handlers:
    logger.addHandler(handler)
