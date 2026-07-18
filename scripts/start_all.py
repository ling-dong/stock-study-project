#!/usr/bin/env python
"""SPAS + Investment Academy 统一启动脚本

一键启动：
- SPAS Core API (port 8000)
- Investment Academy Backend (port 8001)
- Investment Academy Vue2 Frontend dev server (port 8080, 可选)

用法：
  python scripts/start_all.py           # 启动后端 + 前端
  python scripts/start_all.py --no-fe   # 只启动后端
  python scripts/start_all.py --no-ui   # 只启动后端（同 --no-fe）

按 Ctrl+C 或运行 python scripts/stop_all.py 关闭。
"""
import sys
import os
import time
import json
import signal
import atexit
import subprocess
from pathlib import Path
from datetime import datetime


ROOT_DIR = Path(__file__).resolve().parent.parent
ACADEMY_DIR = ROOT_DIR / "investment_academy"
FRONTEND_DIR = ACADEMY_DIR / "frontend"
PID_FILE = ROOT_DIR / ".spas-services.pid"

sys.path.insert(0, str(ROOT_DIR))


def _log(msg):
    print(f"[start_all] {msg}")


def _save_pid(records: list[dict]):
    try:
        PID_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        _log(f"写入 PID 文件失败: {e}")


def _clear_pid():
    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except Exception:
            pass


def _already_running_on_port(port: int) -> bool:
    """Windows 下检查某端口是否已被占用。"""
    try:
        result = subprocess.run(
            f"netstat -ano | findstr :{port}",
            shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode != 0 or not result.stdout:
            return False
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            local_addr = parts[1]
            if local_addr.endswith(f":{port}"):
                return True
        return False
    except Exception:
        return False


def _start_spas_api():
    _log("启动 SPAS Core API — http://127.0.0.1:8000")
    if _already_running_on_port(8000):
        _log("警告：端口 8000 已被占用，可能已有 SPAS API 在运行")
    return subprocess.Popen(
        [sys.executable, "scripts/start.py", "serve"],
        cwd=ROOT_DIR,
    )


def _start_academy_backend():
    _log("启动 Investment Academy Backend — http://127.0.0.1:8001")
    if _already_running_on_port(8001):
        _log("警告：端口 8001 已被占用，可能已有 Academy Backend 在运行")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=ACADEMY_DIR,
    )


def _start_frontend():
    if not (FRONTEND_DIR / "node_modules").exists():
        _log("前端 node_modules 不存在，请先运行：")
        _log("  cd investment_academy/frontend && npm install")
        return None

    _log("启动 Vue2 Frontend — http://127.0.0.1:8080")
    if _already_running_on_port(8080):
        _log("警告：端口 8080 已被占用，可能已有 dev server 在运行")
    # Windows 下需要 shell 来解析 npm
    return subprocess.Popen(
        ["npm", "run", "serve"],
        cwd=FRONTEND_DIR,
        shell=True,
    )


def _stop_all_services():
    """导入 stop_all 的逻辑进行统一关闭。"""
    try:
        from scripts.stop_all import stop_services
        stop_services(force_scan=True)
    except Exception as e:
        _log(f"调用 stop_all 失败: {e}")
        _clear_pid()


def _register_cleanup():
    atexit.register(_stop_all_services)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="启动 SPAS + Investment Academy 全栈")
    parser.add_argument("--no-fe", "--no-ui", action="store_true", help="不启动前端")
    args = parser.parse_args()

    # 如果上次 PID 文件残留，先尝试关闭
    if PID_FILE.exists():
        _log("检测到未清理的 PID 文件，先关闭残留服务...")
        _stop_all_services()
        time.sleep(1)

    records = []
    processes = []

    try:
        spas_proc = _start_spas_api()
        processes.append(("SPAS API", spas_proc, 8000))
        records.append({"name": "SPAS API", "pid": spas_proc.pid, "port": 8000, "start_time": datetime.now().isoformat()})

        time.sleep(2)  # 让 SPAS API 先启动，Academy 后端会代理到它

        academy_proc = _start_academy_backend()
        processes.append(("Academy Backend", academy_proc, 8001))
        records.append({"name": "Academy Backend", "pid": academy_proc.pid, "port": 8001, "start_time": datetime.now().isoformat()})

        if not args.no_fe:
            time.sleep(1)
            fe_proc = _start_frontend()
            if fe_proc:
                processes.append(("Vue2 Frontend", fe_proc, 8080))
                records.append({"name": "Vue2 Frontend", "pid": fe_proc.pid, "port": 8080, "start_time": datetime.now().isoformat()})

        _save_pid(records)
        _register_cleanup()

        print("\n" + "=" * 60)
        print("  所有服务已启动")
        print("  - SPAS Core:      http://127.0.0.1:8000")
        print("  - Academy API:    http://127.0.0.1:8001")
        if not args.no_fe:
            print("  - Vue Frontend:   http://127.0.0.1:8080")
        print("\n  按 Ctrl+C 或运行 python scripts/stop_all.py 关闭")
        print("=" * 60)

        # 监控子进程，一旦有退出就提示
        while True:
            time.sleep(1)
            for name, p, port in processes:
                if p.poll() is not None:
                    _log(f"警告：{name} 已退出 (code={p.returncode})")
                    return p.returncode

    except KeyboardInterrupt:
        print("\n[start_all] 收到中断信号，正在关闭所有服务...")
        _stop_all_services()
        print("[start_all] 全部关闭")


if __name__ == "__main__":
    sys.exit(main())
