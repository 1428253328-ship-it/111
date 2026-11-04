#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出库单自动处理桌面程序 - 主入口
=================================
基于 outbound-order-processing 技能的 GUI 版。
读取京东出库单 Excel，自动清洗、拆分、分流成多张 Anker 业务报表。

运行方式（Windows）：
    方式1：python desktop_app.py
    方式2：打包成 exe 后双击运行

界面功能：
    1. 选择输入文件（.xlsx）
    2. 选择输出保存位置（默认输入文件同目录）
    3. 点击【开始处理】，后台线程执行，界面不卡死
    4. 日志区实时显示处理进度，结束后弹出提示
"""
import os
import sys
import threading
import traceback

# 允许从打包后的 exe 或源码目录定位核心模块
try:
    # PyInstaller 打包后资源解压路径
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
except Exception:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CORE_DIR = os.path.join(BASE_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 核心处理模块（复用 process_outbound 逻辑）
from processor import process, __version__


class OutboundApp:
    """出库单自动处理桌面程序主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("出库单自动处理工具 v" + __version__)
        self.root.geometry("680x520")
        self.root.minsize(600, 480)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        self._build_ui()

    # ------------------------------------------------------------------
    # 界面构建
    # ------------------------------------------------------------------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # 标题区
        header = tk.Frame(self.root)
        header.pack(fill="x", **pad)
        tk.Label(
            header,
            text="出库单自动处理工具",
            font=("Microsoft YaHei", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="自动清洗、拆分、分流出库单 → 生成 pallets / XLC / 2C / 2c-AS220211 报表",
            fg="#666",
        ).pack(anchor="w")

        # 输入文件
        frm_in = tk.LabelFrame(self.root, text="① 输入文件")
        frm_in.pack(fill="x", **pad)
        row_in = tk.Frame(frm_in)
        row_in.pack(fill="x", **pad)
        tk.Entry(row_in, textvariable=self.input_path).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(row_in, text="浏览...", command=self._pick_input).pack(
            side="right", padx=(6, 0)
        )

        # 输出文件
        frm_out = tk.LabelFrame(self.root, text="② 输出位置（留空则保存到输入文件同目录）")
        frm_out.pack(fill="x", **pad)
        row_out = tk.Frame(frm_out)
        row_out.pack(fill="x", **pad)
        tk.Entry(row_out, textvariable=self.output_path).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(row_out, text="浏览...", command=self._pick_output).pack(
            side="right", padx=(6, 0)
        )

        # 处理按钮
        self.btn_run = tk.Button(
            self.root,
            text="🚀 开始处理",
            command=self._on_start,
            bg="#2d8cf0",
            fg="white",
            font=("Microsoft YaHei", 12, "bold"),
            height=2,
        )
        self.btn_run.pack(fill="x", **pad)

        # 日志区
        frm_log = tk.LabelFrame(self.root, text="③ 处理日志")
        frm_log.pack(fill="both", expand=True, **pad)
        self.log_box = scrolledtext.ScrolledText(
            frm_log, height=12, state="disabled", font=("Consolas", 9)
        )
        self.log_box.pack(fill="both", expand=True, **pad)

        self._log("就绪。请选择输入文件后点击【开始处理】。")

    # ------------------------------------------------------------------
    # 事件处理
    # ------------------------------------------------------------------
    def _pick_input(self):
        path = filedialog.askopenfilename(
            title="选择出库单 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
        )
        if path:
            self.input_path.set(path)
            # 若未手动设置输出，自动补默认输出路径
            if not self.output_path.get():
                default_out = path.replace(".xlsx", " - 处理完成.xlsx")
                self.output_path.set(default_out)

    def _pick_output(self):
        path = filedialog.asksaveasfilename(
            title="保存处理结果到",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
        )
        if path:
            self.output_path.set(path)

    def _on_start(self):
        in_path = self.input_path.get().strip()
        if not in_path:
            messagebox.showwarning("提示", "请先选择输入文件。")
            return
        if not os.path.isfile(in_path):
            messagebox.showerror("错误", f"输入文件不存在：\n{in_path}")
            return

        out_path = self.output_path.get().strip() or in_path.replace(
            ".xlsx", " - 处理完成.xlsx"
        )

        # 禁用按钮，防止重复点击
        self.btn_run.config(state="disabled", text="⏳ 处理中...")
        self._clear_log()

        # 后台线程执行，避免界面卡死
        t = threading.Thread(
            target=self._worker, args=(in_path, out_path), daemon=True
        )
        t.start()

    def _worker(self, in_path, out_path):
        try:
            self._log(f"📥 输入：{in_path}")
            self._log(f"📤 输出：{out_path}")
            self._log("⏳ 开始处理...\n")

            unclassified = process(in_path, out_path)

            self._log(f"\n✅ 处理完成！输出文件：\n{out_path}")
            if unclassified:
                self._log(
                    "\n⚠️ 以下服务产品编号不在分流规则内，未写入目标 sheet：\n"
                    + ", ".join(f"{k}({v})" for k, v in sorted(unclassified.items()))
                )
                self.root.after(
                    0,
                    lambda: messagebox.showwarning(
                        "处理完成（有未归类）",
                        f"处理完成！\n\n输出：{out_path}\n\n"
                        f"⚠️ 有未归类数据需人工确认：\n"
                        + ", ".join(f"{k}({v})" for k, v in sorted(unclassified.items())),
                    ),
                )
            else:
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "处理完成", f"✅ 处理完成！\n\n输出文件：\n{out_path}"
                    ),
                )
        except Exception as e:
            self._log(f"\n❌ 处理失败：{e}\n{traceback.format_exc()}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "处理失败", f"处理过程中发生错误：\n{e}"
                ),
            )
        finally:
            self.root.after(0, self._reset_btn)

    # ------------------------------------------------------------------
    # 日志辅助
    # ------------------------------------------------------------------
    def _log(self, msg):
        def _append():
            self.log_box.config(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")

        # 线程安全：通过 after 回到主线程更新 UI
        if threading.current_thread() is threading.main_thread():
            _append()
        else:
            self.root.after(0, _append)

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def _reset_btn(self):
        self.btn_run.config(state="normal", text="🚀 开始处理")


def main():
    root = tk.Tk()
    OutboundApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()