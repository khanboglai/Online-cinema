""" Logger config """
import logging


""" Logger setting """
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


""" Logger initialization """
logger = logging.getLogger(__name__)
