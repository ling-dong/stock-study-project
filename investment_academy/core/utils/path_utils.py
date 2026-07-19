"""路径/标识符安全校验工具

用于防止路径遍历、非法文件名和非法 ETF 代码进入文件系统操作。
"""
import re


SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")
MD_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_-]+\.md$")
ETF_CODE_RE = re.compile(r"^\d{6}\.[A-Z]{2}$")
VALID_TIMEFRAMES = {"day", "5min"}


def validate_content_id(value: str) -> bool:
    """阶段/实验室/章节 ID：仅允许字母、数字、下划线、中划线"""
    return bool(SAFE_ID_RE.fullmatch(value))


def validate_chapter_filename(value: str) -> bool:
    """章节 Markdown 文件名：仅允许 .md 结尾的安全文件名"""
    return bool(MD_FILENAME_RE.fullmatch(value))


def validate_etf_code(code: str) -> bool:
    """ETF 代码：6 位数字 + .SH/.SZ，防止目录遍历"""
    return bool(ETF_CODE_RE.fullmatch(code))


def validate_timeframe(timeframe: str) -> bool:
    """时间周期：仅允许 day 或 5min"""
    return timeframe in VALID_TIMEFRAMES
