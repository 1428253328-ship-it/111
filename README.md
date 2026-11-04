# 出库单自动处理工具 — 在线打包为 Windows exe

本仓库包含出库单自动处理工具的完整源码 + GitHub Actions 打包配置。
**无需本地安装 Python，完全在网页上操作即可得到能双击的 .exe。**

## 你只需要做 3 件事（网页操作，约 5 分钟）

### 第 1 步：上传代码到 GitHub
1. 打开 <https://github.com>，登录你的账号（没有就免费注册一个）
2. 点右上角 **+ → New repository**，仓库名随意（如 `outbound-exe`），点 Create
3. 在仓库页面点 **uploading an existing file**（上传已有文件）
4. 把本目录下的这些文件全部拖进去上传：
   - `desktop_app.py`
   - `build_exe.py`
   - `core/` 文件夹（含 `processor.py`）
   - `.github/workflows/build.yml`
5. 点 **Commit changes** 提交

### 第 2 步：触发打包
代码上传后，GitHub Actions 会**自动**开始打包（约 2-3 分钟）。
你也可以手动触发：仓库页 **Actions** 标签 → 左侧 `Build Windows EXE` → 右侧 **Run workflow** → 绿色按钮。

### 第 3 步：下载 exe
1. 打包完成后，进 **Actions** 标签，点最新那条运行记录（绿色 √）
2. 页面底部 **Artifacts（成品）** 区域，点击下载 `出库单自动处理工具`
3. 解压得到 `出库单自动处理工具.exe` —— 这就是**能双击运行**的桌面程序，无需装 Python，可直接发给同事

---

## 界面说明
- **选择输入文件**：浏览选择出库单 Excel（.xlsx）
- **选择输出位置**：默认保存到输入文件同目录
- **【开始处理】按钮**：后台执行，界面不卡死
- **处理日志区**：实时显示清洗/拆分/分流进度
- 处理结束弹窗提示（含未归类数据人工确认提醒）

## 处理能力
- 自动清洗：过滤无效行、裁剪字段、去时区前缀、拆运单号、去重、按时间升序
- 分流 4 表：pallets / XLC / 2C delivery / 2c-AS220211
- 承运商自动填充、客户编码抓取、列宽调整
- 严格按业务表头输出，不改字段与顺序