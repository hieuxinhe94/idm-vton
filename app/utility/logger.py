import logging
from ..config import VM

logging.basicConfig(format='[%(asctime)s][%(pathname)s:%(lineno)d][%(levelname)s]: %(message)s')
logger = logging.getLogger(VM.SYSTEM_NAME)
logger.setLevel(logging.DEBUG)
