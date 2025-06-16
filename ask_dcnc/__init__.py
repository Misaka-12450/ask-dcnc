import pathlib

# Import environment if not in Docker
if not pathlib.Path("/.dockerenv").exists():
    from dotenv import load_dotenv

    load_dotenv(override=False)

from .agent import get_agent
from .client import get_aws_keys
from .prompt import get_system_prompt
from .ui import get_time_str

__all__ = [
    "get_agent",
    "get_aws_keys",
    "get_system_prompt",
    "get_time_str"
]
