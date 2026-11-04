#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出库单自动处理工具 - 打包脚本 (Windows)
=======================================
在 Windows 上运行本脚本，一键生成独立的 .exe 桌面程序。

使用方法（Windows，已安装 Python 3.9+）：
    1. 安装依赖：   pip install pyinstaller
    2. 运行打包：   python build_exe.py
    3. 产物：       dist/出库单自动处理工具.exe

打包出的 exe 无需安装 Python，可发给任意 Windows 用户直接双击运行。
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("出库单自动处理工具 - 打包为 Windows exe")
    print("=" * 60)

    # 1. 检查 PyInstaller
    try:
        import PyInstaller  # noqa
        print("[OK] PyInstaller 已安装")
    except ImportError:
        print("[!] 未检测到 PyInstaller，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller 安装完成")

    # 2. 打包命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",           # 单文件 exe
        "--windowed",          # 无控制台窗口（GUI 程序）
        "--name", "出库单自动处理工具",
        "--add-data",
        f"{os.path.join(BASE_DIR, 'core')}{os.pathsep}core",
        os.path.join(BASE_DIR, "desktop_app.py"),
    ]

    print("\n[BUILD] 开始打包...")
    print("  ".join(cmd))
    subprocess.check_call(cmd)

    # 3. 输出结果
    exe_path = os.path.join(BASE_DIR, "dist", "出库单自动处理工具.exe")
    print("\n" + "=" * 60)
    if os.path.isfile(exe_path):
        print(f"[SUCCESS] 打包完成！")
        print(f"exe 位置：{exe_path}")
        print("可直接将此 exe 发给同事使用，无需安装 Python。")
    else:
        print("[ERROR] 打包失败，请检查上方输出。")
    print("=" * 60)


if __name__ == "__main__":
    main()