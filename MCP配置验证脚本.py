#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MCP配置验证脚本
用途：验证MCP配置是否正确
创建日期：2026-01-04
版本：V1.0
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Cursor配置文件路径
CURSOR_SETTINGS_FILE = Path(r"C:\Users\温柔的男子啊\AppData\Roaming\Cursor\User\settings.json")

# 验证结果文件路径
VERIFICATION_RESULT_FILE = Path(r"C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\工具文档\MCP配置验证结果.md")


def read_settings():
    """读取Cursor配置文件"""
    try:
        with open(CURSOR_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None


def check_nodejs():
    """检查Node.js是否已安装"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Node.js未安装或无法运行"
    except FileNotFoundError:
        return False, "Node.js未安装"
    except Exception as e:
        return False, f"检查Node.js时出错: {e}"


def check_npx():
    """检查npx是否可用"""
    try:
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "npx不可用"
    except FileNotFoundError:
        return False, "npx未安装"
    except Exception as e:
        return False, f"检查npx时出错: {e}"


def verify_mcp_config(settings):
    """验证MCP配置"""
    results = {
        "检查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "检查项": [],
        "总体状态": "未知"
    }
    
    # 检查1：配置文件是否存在
    if settings is None:
        results["检查项"].append({
            "名称": "配置文件检查",
            "状态": "失败",
            "详情": "配置文件不存在或无法读取"
        })
        results["总体状态"] = "失败"
        return results
    
    results["检查项"].append({
        "名称": "配置文件检查",
        "状态": "通过",
        "详情": "配置文件存在且可读"
    })
    
    # 检查2：MCP配置是否存在
    if "mcpServers" not in settings:
        results["检查项"].append({
            "名称": "MCP配置检查",
            "状态": "失败",
            "详情": "配置文件中没有mcpServers配置"
        })
        results["总体状态"] = "失败"
        return results
    
    mcp_servers = settings["mcpServers"]
    results["检查项"].append({
        "名称": "MCP配置检查",
        "状态": "通过",
        "详情": f"找到 {len(mcp_servers)} 个MCP服务器配置"
    })
    
    # 检查3：检查每个MCP服务器配置
    required_servers = ["filesystem", "sqlite", "markdown"]
    for server_name in required_servers:
        if server_name in mcp_servers:
            server_config = mcp_servers[server_name]
            status = "通过"
            details = f"配置完整"
            
            # 检查必要字段
            if "command" not in server_config:
                status = "失败"
                details = "缺少command字段"
            elif "args" not in server_config:
                status = "失败"
                details = "缺少args字段"
            
            results["检查项"].append({
                "名称": f"{server_name} MCP服务器",
                "状态": status,
                "详情": details,
                "配置": server_config
            })
        else:
            results["检查项"].append({
                "名称": f"{server_name} MCP服务器",
                "状态": "失败",
                "详情": "未配置"
            })
    
    # 检查4：Node.js环境
    nodejs_ok, nodejs_info = check_nodejs()
    results["检查项"].append({
        "名称": "Node.js环境检查",
        "状态": "通过" if nodejs_ok else "失败",
        "详情": nodejs_info
    })
    
    # 检查5：npx可用性
    npx_ok, npx_info = check_npx()
    results["检查项"].append({
        "名称": "npx可用性检查",
        "状态": "通过" if npx_ok else "失败",
        "详情": npx_info
    })
    
    # 总体状态判断
    all_passed = all(item["状态"] == "通过" for item in results["检查项"])
    results["总体状态"] = "通过" if all_passed else "失败"
    
    return results


def generate_verification_report(results):
    """生成验证报告"""
    report = f"""# MCP配置验证结果

## 【元数据】
- **验证时间**：{results["检查时间"]}
- **总体状态**：{'✅ 通过' if results['总体状态'] == '通过' else '❌ 失败'}
- **版本**：V1.0

---

## 📊 检查结果

### 总体状态
- **状态**：{results["总体状态"]}
- **检查项总数**：{len(results["检查项"])}
- **通过项数**：{sum(1 for item in results["检查项"] if item["状态"] == "通过")}
- **失败项数**：{sum(1 for item in results["检查项"] if item["状态"] == "失败")}

### 详细检查项

"""
    
    for i, item in enumerate(results["检查项"], 1):
        status_icon = "✅" if item["状态"] == "通过" else "❌"
        report += f"""#### {i}. {item["名称"]} {status_icon}

- **状态**：{item["状态"]}
- **详情**：{item["详情"]}

"""
        if "配置" in item:
            report += f"- **配置**：```json\n{json.dumps(item["配置"], indent=2, ensure_ascii=False)}\n```\n\n"
    
    report += """---

## 📋 下一步操作

### 如果检查通过
1. ✅ 重启Cursor
2. ✅ 在命令面板中搜索"MCP"验证服务器状态
3. ✅ 测试MCP工具是否正常工作

### 如果检查失败
1. ❌ 检查失败项的具体原因
2. ❌ 参考`MCP配置安装指南.md`修复问题
3. ❌ 确保Node.js已正确安装

---

## ⚠️ 注意事项

### 前置要求
1. **Node.js必须已安装**
   - 检查方法：打开命令行，输入 `node --version`
   - 如果未安装，访问 https://nodejs.org/ 下载安装

2. **网络连接**
   - MCP服务器首次运行需要下载npm包
   - 确保网络连接正常

---

**最后更新**：""" + results["检查时间"] + """  
**版本**：V1.0  
**维护者**：自动化脚本
"""
    
    return report


def main():
    """主函数"""
    print("=" * 60)
    print("MCP配置验证脚本")
    print("=" * 60)
    print()
    
    # 读取配置
    print("正在读取Cursor配置文件...")
    settings = read_settings()
    
    if settings is None:
        print("❌ 无法读取配置文件")
        return
    
    print("✅ 配置文件读取成功")
    print()
    
    # 验证配置
    print("正在验证MCP配置...")
    results = verify_mcp_config(settings)
    
    # 生成报告
    print("正在生成验证报告...")
    report = generate_verification_report(results)
    
    # 保存报告
    try:
        VERIFICATION_RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(VERIFICATION_RESULT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 验证报告已保存到: {VERIFICATION_RESULT_FILE}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return
    
    # 输出结果
    print()
    print("=" * 60)
    print("验证结果")
    print("=" * 60)
    print(f"总体状态: {results['总体状态']}")
    print(f"检查项总数: {len(results['检查项'])}")
    print(f"通过项数: {sum(1 for item in results['检查项'] if item['状态'] == '通过')}")
    print(f"失败项数: {sum(1 for item in results['检查项'] if item['状态'] == '失败')}")
    print()
    
    # 显示详细结果
    for item in results["检查项"]:
        status_icon = "✅" if item["状态"] == "通过" else "❌"
        print(f"{status_icon} {item['名称']}: {item['状态']} - {item['详情']}")
    
    print()
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)
    print()
    print(f"详细报告请查看: {VERIFICATION_RESULT_FILE}")


if __name__ == "__main__":
    main()

