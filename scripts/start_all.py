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
"""
import sys
sys.path.insert(0, ".")
import argparse
import subprocess
import time
import os
from pathlib import Path


def start_spas_api():
    """启动 SPAS 核心 API"""
    print("=" * 60)
    print("  启动 SPAS Core API — http://127.0.0.1:8000")
    print("  文档: http://127.0.0.1:8000/docs")
    print("=" * 60)
    return subprocess.Popen(
        [sys.executable, "scripts/start.py", "serve"],
        cwd=Path(__file__).resolve().parent.parent,
    )


def start_academy_backend():
    """启动投资学院后端"""
    print("=" * 60)
    print("  启动 Investment Academy Backend — http://127.0.0.1:8001")
    print("  文档: http://127.0.0.1:8001/docs")
    print("=" * 60)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=Path(__file__).resolve().parent.parent / "investment_academy",
    )


def start_frontend():
    """启动 Vue2 前端 dev server"""
    frontend_dir = Path(__file__).resolve().parent.parent / "investment_academy" / "frontend"
    if not (frontend_dir / "node_modules").exists():
        print("[前端] node_modules 不存在，请先运行: cd investment_academy/frontend && npm install")
        return None

    print("=" * 60)
    print("  启动 Vue2 Frontend — http://127.0.0.1:8080")
    print("=" * 60)
    return subprocess.Popen(
        ["npm", "run", "serve"],
        cwd=frontend_dir,
        shell=True,  # Windows 下需要 shell 来解析 npm
    )


def main():
    parser = argparse.ArgumentParser(description="启动 SPAS + Investment Academy 全栈")
    parser.add_argument("--no-fe", "--no-ui", action="store_true", help="不启动前端")
    args = parser.parse_args()

    processes = []
    try:
        processes.append(("SPAS API", start_spas_api()))
        time.sleep(2)  # 让 SPAS API 先启动，Academy 后端会代理到它
        processes.append(("Academy Backend", start_academy_backend()))

        if not args.no_fe:
            time.sleep(1)
            fe_proc = start_frontend()
            if fe_proc:
                processes.append(("Vue2 Frontend", fe_proc))

        print("\n" + "=" * 60)
        print("  所有服务已启动，按 Ctrl+C 停止")
        print("=" * 60)

        # 等待所有进程
        while True:
            time.sleep(1)
            for name, p in processes:
                if p.poll() is not None:
                    print(f"[警告] {name} 已退出 (code={p.returncode})")
                    return p.returncode
    except KeyboardInterrupt:
        print("\n[停止] 正在关闭所有服务...")
        for name, p in processes:
            if p and p.poll() is None:
                print(f"  关闭 {name}...")
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("[停止] 全部关闭")


if __name__ == "__main__":
    sys.exit(main())
