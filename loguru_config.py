from loguru import logger
import sys

logger.remove( )
logger.add( sink = sys.stderr, level = "INFO" )

logger.add( sink = "logs/ask-dcnc.log", rotation = "1MB", retention = "30 days", level = "INFO" )
# TODO: AI messages with human in a different file
