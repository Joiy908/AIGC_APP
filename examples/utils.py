import logging


def set_debug(*logger_names: list[str]):
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)  # 只让这个 handler 处理 DEBUG 及以上的日志
        logger.addHandler(handler)

        # 设置日志格式
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
        handler.setFormatter(formatter)