#!/usr/bin/env python
"""SPAS + Investment Academy 一键关闭脚本

用法：
  python scripts/stop_all.py           # 关闭 PID 文件中记录的全部服务
  python scripts/stop_all.py --force   # 额外按端口扫描并关闭 8000/8001/8080
"""
import sys
import os
import json
import time
import subprocess
from pathlib import Path


PID_FILE = Path(__file__).resolve().parent.parent / ".spas-services.pid"
DEFAULT_PORTS = [8000, 8001, 8080]


def _log(msg):
    print(f"[stop_all] {msg}")


def _process_alive(pid: int) -> bool:
    """Windows 下检查进程是否仍在运行。"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, check=False
        )
        return str(pid) in result.stdout
    except Exception:
        return False


def _kill_pid(pid: int, force: bool = False) -> bool:
    """尝试关闭指定 PID。先优雅关闭，失败再强制。"""
    if not _process_alive(pid):
        return True

    args = ["taskkill", "/PID", str(pid)]
    if force:
        args.append("/F")
    try:
        subprocess.run(args, check=False, capture_output=True)
    except Exception as e:
        _log(f"关闭 PID {pid} 时出错: {e}")
        return False

    # 等待进程退出
    for _ in range(10):
        if not _process_alive(pid):
            return True
        time.sleep(0.2)
    return False


def _kill_by_port(port: int) -> list[int]:
    """Windows 下通过 netstat 找到占用端口的进程并关闭。"""
    killed = []
    try:
        result = subprocess.run(
            f"netstat -ano | findstr :{port}",
            shell=True, capture_output=True, text=True, check=False
        )
        if result.returncode != 0 or not result.stdout:
            return killed

        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if not parts:
                continue
            # 最后一段是 PID
            try:
                pid = int(parts[-1])
            except ValueError:
                continue
            if pid <= 0:
                continue
            # 只关闭 LISTENING/ESTABLISHED 中端口精确匹配的行
            local_addr = parts[1] if len(parts) > 1 else ""
            if not local_addr.endswith(f":{port}"):
                continue
            if _kill_pid(pid, force=True):
                killed.append(pid)
    except Exception as e:
        _log(f"按端口 {port} 扫描失败: {e}")
    return killed


def load_pid_records() -> list[dict]:
    if not PID_FILE.exists():
        return []
    try:
        data = json.loads(PID_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return [data] if isinstance(data, dict) else []
    except Exception as e:
        _log(f"读取 PID 文件失败: {e}")
        return []


def stop_services(force_scan: bool = False):
    records = load_pid_records()
    killed = set()

    if records:
        _log(f"从 PID 文件读取到 {len(records)} 个服务")
        for rec in records:
            name = rec.get("name", "未知")
            pid = rec.get("pid")
            port = rec.get("port")
            if not pid:
                continue
            _log(f"正在关闭 {name} (PID {pid}, port {port})")
            if _kill_pid(pid, force=False):
                killed.add(pid)
                _log(f"  ✓ {name} 已关闭")
            else:
                _log(f"  强制关闭 {name} (PID {pid})")
                if _kill_pid(pid, force=True):
                    killed.add(pid)
    else:
        _log("PID 文件不存在，将按端口扫描")
        force_scan = True

    if force_scan:
        for port in DEFAULT_PORTS:
            pids = _kill_by_port(port)
            if pids:
                killed.update(pids)
                _log(f"  ✓ 端口 {port} 上的进程已关闭: {pids}")

    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
            _log("已清理 PID 文件")
        except Exception as e:
            _log(f"清理 PID 文件失败: {e}")

    _log(f"总计关闭 {len(killed)} 个进程")
    return 0 if (records or force_scan) else 1


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    sys.exit(stop_services(force_scan=force))
