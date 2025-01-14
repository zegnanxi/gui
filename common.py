import os

_current_dir = None  # 私有模块级变量用于缓存


def get_current_dir() -> str:
    """
    获取当前工作目录
    首次调用时会缓存结果,后续调用直接返回缓存值

    Returns:
        str: 当前工作目录的绝对路径
    """
    global _current_dir
    if _current_dir is None:
        _current_dir = os.getcwd()
    return _current_dir
