# 在 Cursor 中安装 Python 扩展

## 方法 1：通过扩展市场安装（推荐）

1. **打开扩展面板**
   - 按 `Ctrl + Shift + X` 
   - 或点击左侧边栏的扩展图标（四个方块的图标）

2. **搜索 Python**
   - 在搜索框中输入：`Python`
   - 找到 **"Python"** 扩展（由 Microsoft 发布）

3. **安装**
   - 点击 "Install" 按钮
   - 等待安装完成

4. **重启 Cursor**
   - 安装完成后，可能需要重启 Cursor

## 方法 2：通过命令面板安装

1. **打开命令面板**
   - 按 `Ctrl + Shift + P`

2. **输入命令**
   - 输入：`Extensions: Install Extensions`
   - 回车

3. **搜索并安装 Python 扩展**

## 方法 3：手动安装（如果上述方法不行）

1. **访问扩展市场**
   - 打开：https://marketplace.visualstudio.com/items?itemName=ms-python.python

2. **下载并安装**
   - 点击 "Install" 按钮
   - 选择 "Open in Cursor" 或手动安装

## 配置 Python 解释器

安装扩展后，需要配置 Python 解释器：

1. **打开命令面板**
   - 按 `Ctrl + Shift + P`

2. **选择解释器**
   - 输入：`Python: Select Interpreter`
   - 选择你的 Python 版本（应该是 3.14.2）

3. **验证**
   - 打开任意 Python 文件
   - 右下角应该显示 Python 版本

## 解决"无法解析导入"警告

安装 Python 扩展后：
1. 扩展会自动检测已安装的包
2. 如果还有警告，可能需要：
   - 在项目根目录创建 `requirements.txt`
   - 或配置 Python 路径

