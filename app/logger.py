import logging
from app.context import get_request_id


class ContextualFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


class ConditionalFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.default_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.request_id_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [RequestID: %(request_id)s]"
        super().__init__(*args, **kwargs)

    def format(self, record):
        if getattr(record, "request_id", None):
            self._style._fmt = self.request_id_fmt
        else:
            self._style._fmt = self.default_fmt
        return super().format(record)


def setup_logger(level=logging.INFO, file_output=None) -> None:
    handlers = [logging.StreamHandler()]
    if file_output is not None:
        handlers.append(logging.FileHandler(file_output, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        handlers=handlers
    )

    for handler in logging.root.handlers:
        handler.addFilter(ContextualFilter())
        handler.setFormatter(ConditionalFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
