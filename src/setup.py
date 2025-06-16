import logging
import os
from logging.handlers import RotatingFileHandler

import yaml


def setup_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Remove duplicate logging caused by streamlit
    logger.handlers = []
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = os.path.join(root_dir, "streamlit_agent.log")
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=1024 * 1024, backupCount=1
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def setup_config() -> tuple[dict, str, str, bool]:
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        if config["config"]["langsmith"]["enabled"]:
            os.environ["LANGCHAIN_TRACING_V2"] = config["config"]["langsmith"][
                "langchain_tracing_v2"
            ]
            os.environ["LANGCHAIN_ENDPOINT"] = config["config"]["langsmith"][
                "langchain_endpoint"
            ]
            os.environ["LANGCHAIN_API_KEY"] = config["config"]["langsmith"][
                "langchain_api_key"
            ]
            os.environ["LANGCHAIN_PROJECT"] = config["config"]["langsmith"][
                "langchain_project"
            ]

        model = config["config"]["openai"]["model"]
        api_key = config["config"]["openai"]["api_key"]
        tavily_api_key = config["config"]["tavily"]["api_key"]
        search_web_mode = config["config"]["tools"]["search_web"]
        return model, api_key, tavily_api_key, search_web_mode
    except Exception as e:
        setup_logger().debug(f"Yml load failed: {e}")
        raise
