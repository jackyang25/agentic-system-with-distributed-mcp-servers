import logging
import os
import sys
from pathlib import Path
from remote_pdb import RemotePdb


def get_logger(name: str) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name=name)

    if not logger.handlers:
        logger.setLevel(level=logging.DEBUG)

        handler: logging.StreamHandler[logging.TextIO | logging.Any] = (
            logging.StreamHandler(stream=sys.stdout)
        )
        handler.setLevel(level=logging.DEBUG)

        fmt = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt=fmt)

        logger.addHandler(hdlr=handler)

    return logger


def load_secrets() -> None:
    creds_file: Path = Path(__file__).parent.parent.joinpath(".env")
    if not creds_file.exists():
        print("No .env file found.")
        return
    with open(file=creds_file, mode="r", encoding="utf-8") as file:
        lines: list[str] = file.readlines()
        for line in lines:
            if "=" not in line:
                continue
            key, value = line.strip().split(sep="=", maxsplit=1)
            os.environ[key] = value


def get_openai_model() -> str:
    load_secrets()
    model = os.environ.get("OPENAI_MODEL")
    if not model:
        raise NotImplementedError("OPENAI_MODEL not set in environment variables.")
    return model


def get_gemini_model() -> str:
    load_secrets()
    model = os.environ.get("GEMINI_MODEL")
    if not model:
        raise NotImplementedError("GEMINI_MODEL not set in environment variables.")
    return model if model else "gpt-3.5-turbo"


def set_remote_pdb() -> None:
    RemotePdb(host="localhost", port=4444).set_trace()
