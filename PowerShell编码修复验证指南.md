# PowerShell 编码修复验证指南

## 📋 修复内容总结

### 1. PowerShell 配置文件
**位置**：`C:\Users\温柔的男子啊\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`

**功能**：
- 自动设置 UTF-8 编码
- 设置代码页为 65001
- 配置 PowerShell 默认编码参数

### 2. Cursor settings.json 配置
**位置**：`C:\Users\温柔的男子啊\AppData\Roaming\Cursor\User\settings.json`

**配置项**：
- 默认终端：Command Prompt（更稳定）
- 终端编码：UTF-8
- CMD 启动参数：`chcp 65001`
- PowerShell 启动参数：完整的 UTF-8 编码设置

### 3. 备用方案
**批处理启动器**：`C:\Users\温柔的男子啊\Desktop\运行桌面整理.bat`

用于在 PowerShell 仍有问题时直接运行 Python 脚本。

## ✅ 验证步骤

### 步骤 1：重启 Cursor
**重要**：所有配置修改后必须重启 Cursor 才能生效。

1. 完全关闭 Cursor（确保所有窗口都关闭）
2. 重新打开 Cursor
3. 打开新的终端窗口

### 步骤 2：检查代码页
在新终端中运行：

```cmd
chcp
```

**预期结果**：
```
活动代码页: 65001
```

如果显示 `936`，说明配置未生效，请检查：
- PowerShell 配置文件是否存在
- settings.json 配置是否正确
- 是否已重启 Cursor

### 步骤 3：测试中文输出
运行测试脚本：

```cmd
python "圆心工作/工具和脚本/工具脚本/测试编码.py"
```

**预期结果**：
- ✅ 中文正常显示
- ✅ 中文路径正常读取
- ✅ 文件操作正常
- ✅ 编码信息正确

### 步骤 4：测试实际脚本
运行桌面整理脚本：

```cmd
python "桌面整理脚本.py"
```

或使用批处理启动器：
```cmd
运行桌面整理.bat
```

## 🔧 故障排除

### 问题 1：代码页仍然是 936

**解决方案**：
1. 检查 PowerShell 配置文件是否存在：
   ```powershell
   Test-Path $PROFILE
   ```
2. 如果不存在，手动创建：
   ```powershell
   New-Item -Path $PROFILE -ItemType File -Force
   ```
3. 将配置内容复制到文件中
4. 检查 PowerShell 执行策略：
   ```powershell
   Get-ExecutionPolicy
   ```
5. 如果受限，运行：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### 问题 2：Cursor 终端仍显示乱码

**解决方案**：
1. 确认 settings.json 配置正确
2. 完全重启 Cursor（关闭所有窗口）
3. 尝试切换到 CMD 终端（更稳定）
4. 检查系统区域设置是否为中文

### 问题 3：Python 脚本执行失败

**解决方案**：
1. 使用批处理启动器（`运行桌面整理.bat`）
2. 直接在 CMD 中运行（绕过 PowerShell）
3. 检查 Python 环境是否正确

## 📝 配置检查清单

- [ ] PowerShell 配置文件已创建
- [ ] settings.json 配置已更新
- [ ] Cursor 已完全重启
- [ ] 代码页显示 65001
- [ ] 中文输出正常
- [ ] 中文路径正常
- [ ] 测试脚本全部通过

## 🎯 预期效果

修复成功后，您应该能够：
- ✅ 在终端中正常显示中文
- ✅ 使用中文路径执行命令
- ✅ 运行包含中文的 Python 脚本
- ✅ 文件操作正常，无编码错误

## 📞 如果问题仍然存在

如果按照以上步骤操作后问题仍然存在，请：
1. 运行测试脚本并记录输出
2. 检查 PowerShell 配置文件内容
3. 检查 settings.json 配置
4. 尝试使用 CMD 作为默认终端（更稳定）

---

**最后更新**：2026-01-04
**版本**：V1.0


