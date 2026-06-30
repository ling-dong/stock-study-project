"""共享的 pytest fixtures"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# 确保项目在 sys.path
ACADEMY_ROOT = Path(__file__).resolve().parent.parent
if str(ACADEMY_ROOT) not in sys.path:
    sys.path.insert(0, str(ACADEMY_ROOT))


@pytest.fixture
def temp_db():
    """创建临时数据库并注入到 repository"""
    from db import repository
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    old_path = repository.DB_PATH
    repository.DB_PATH = tmp.name
    yield tmp.name
    repository.DB_PATH = old_path
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)
