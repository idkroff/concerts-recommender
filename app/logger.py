import logging
import os
from app.context import get_request_id


class ContextualFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()

        if not hasattr(record, 'context') or not isinstance(record.context, dict):
            record.context = {}

        record.context['SEVERITY'] = record.levelname.lower()
        record.context['REQUEST_ID'] = record.request_id
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


class SystemdCustomFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.default_fmt = "%(name)s: %(message)s"
        self.request_id_fmt = "%(name)s: %(message)s - [RequestID: %(request_id)s]"
        super().__init__(*args, **kwargs)

    def format(self, record):
        if getattr(record, "request_id", None):
            self._style._fmt = self.request_id_fmt
        else:
            self._style._fmt = self.default_fmt
        return super().format(record)


def setup_logger(level=logging.INFO, file_output=None) -> None:
    handlers = []

    use_systemd = os.getenv("LOGGING_SYSTEMD", "") == "1"

    if use_systemd:
        from systemdlogging.toolbox import check_for_systemd  # type: ignore
        from systemdlogging.toolbox import SystemdFormatter  # type: ignore
        from systemdlogging.toolbox import SystemdHandler  # type: ignore

        if not check_for_systemd:
            raise Exception('check for systemd failed')

        handler = SystemdHandler()
        handler.setFormatter(SystemdFormatter())
        handlers.append(handler)
    else:
        handlers.append(logging.StreamHandler())
        if file_output is not None:
            handlers.append(logging.FileHandler(file_output, encoding="utf-8"))

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        handlers=handlers
    )

    logging.root.setLevel(level)
    for handler in handlers:
        handler.setLevel(level)
        handler.addFilter(ContextualFilter())

        if use_systemd:
            handler.setFormatter(SystemdCustomFormatter())
        else:
            handler.setFormatter(ConditionalFormatter(
                datefmt="%Y-%m-%d %H:%M:%S"))
        logging.root.addHandler(handler)
