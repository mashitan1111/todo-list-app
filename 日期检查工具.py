#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日期检查工具
用途：扫描所有RAG文件，识别过期内容
创建日期：2026-01-04
版本：V1.0
"""

import re
from pathlib import Path
from datetime import datetime

# 基础目录
BASE_DIR = Path(__file__).parent.parent.parent
RAG_DIR = BASE_DIR / "圆心工作" / "RAG知识库"

# 当前日期
CURRENT_DATE = datetime(2026, 1, 4)
EXPIRY_THRESHOLD_DAYS = 365  # 超过1年视为过期

# 内容有效期配置（天）
CONTENT_EXPIRY = {
    "合规风控库": 90,  # 3个月
    "核心基础库": 180,  # 6个月
    "直播课程库": 180,  # 6个月
    "其他": 365,  # 12个月
}

def extract_date_from_content(content):
    """从文件内容中提取日期"""
    dates = []
    
    # 匹配各种日期格式
    patterns = [
        r'更新日期[：:]\s*(\d{4}-\d{2}-\d{2})',
        r'最后更新[：:]\s*(\d{4}-\d{2}-\d{2})',
        r'创建日期[：:]\s*(\d{4}-\d{2}-\d{2})',
        r'(\d{4}-\d{2}-\d{2})',  # 通用日期格式
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            try:
                date = datetime.strptime(match, "%Y-%m-%d")
                dates.append(date)
            except:
                pass
    
    return dates

def get_library_name(file_path):
    """根据文件路径判断所属库"""
    path_str = str(file_path)
    if "01_核心基础库" in path_str:
        return "核心基础库"
    elif "02_合规风控库" in path_str:
        return "合规风控库"
    elif "04_直播课程库" in path_str:
        return "直播课程库"
    else:
        return "其他"

def check_file_dates(file_path):
    """检查单个文件的日期"""
    try:
        content = file_path.read_text(encoding='utf-8')
        dates = extract_date_from_content(content)
        
        if not dates:
            return {
                "file": str(file_path.relative_to(BASE_DIR / "圆心工作")),
                "status": "no_date",
                "message": "未找到日期信息"
            }
        
        # 取最新的日期
        latest_date = max(dates)
        days_old = (CURRENT_DATE - latest_date).days
        
        library = get_library_name(file_path)
        expiry_days = CONTENT_EXPIRY.get(library, CONTENT_EXPIRY["其他"])
        
        if days_old > expiry_days:
            return {
                "file": str(file_path.relative_to(BASE_DIR / "圆心工作")),
                "status": "expired",
                "date": latest_date.strftime("%Y-%m-%d"),
                "days_old": days_old,
                "expiry_days": expiry_days,
                "library": library,
                "message": f"已过期 {days_old - expiry_days} 天"
            }
        elif days_old > expiry_days - 30:  # 提前30天预警
            return {
                "file": str(file_path.relative_to(BASE_DIR / "圆心工作")),
                "status": "warning",
                "date": latest_date.strftime("%Y-%m-%d"),
                "days_old": days_old,
                "expiry_days": expiry_days,
                "library": library,
                "message": f"即将过期（{expiry_days - days_old} 天后）"
            }
        else:
            return {
                "file": str(file_path.relative_to(BASE_DIR / "圆心工作")),
                "status": "ok",
                "date": latest_date.strftime("%Y-%m-%d"),
                "days_old": days_old,
                "library": library
            }
    except Exception as e:
        return {
            "file": str(file_path.relative_to(BASE_DIR / "圆心工作")),
            "status": "error",
            "message": f"读取失败: {str(e)}"
        }

def scan_rag_files():
    """扫描所有RAG文件"""
    print("🚀 开始扫描RAG知识库文件...")
    print(f"扫描目录: {RAG_DIR}")
    print("-" * 60)
    
    results = {
        "expired": [],
        "warning": [],
        "no_date": [],
        "ok": [],
        "error": []
    }
    
    # 扫描所有.md文件
    md_files = list(RAG_DIR.rglob("*.md"))
    print(f"找到 {len(md_files)} 个Markdown文件")
    print("-" * 60)
    
    for file_path in md_files:
        result = check_file_dates(file_path)
        results[result["status"]].append(result)
    
    return results

def generate_report(results):
    """生成检查报告"""
    report = f"""# RAG知识库日期检查报告

## 【元数据】
- **检查日期**：{CURRENT_DATE.strftime("%Y-%m-%d")}
- **检查工具**：日期检查工具.py
- **版本**：V1.0

---

## 📊 检查统计

- **总文件数**：{sum(len(v) for v in results.values())}
- **已过期**：{len(results['expired'])} 个
- **即将过期**：{len(results['warning'])} 个
- **无日期信息**：{len(results['no_date'])} 个
- **正常**：{len(results['ok'])} 个
- **错误**：{len(results['error'])} 个

---

## ❌ 已过期文件（必须立即更新）

"""
    
    if results['expired']:
        for item in results['expired']:
            report += f"- **{item['file']}**\n"
            report += f"  - 最后更新：{item['date']}\n"
            report += f"  - 已过期：{item['days_old']} 天（标准：{item['expiry_days']} 天）\n"
            report += f"  - 所属库：{item['library']}\n"
            report += f"  - 状态：{item['message']}\n\n"
    else:
        report += "✅ 无过期文件\n\n"
    
    report += "---\n\n## ⚠️ 即将过期文件（建议提前更新）\n\n"
    
    if results['warning']:
        for item in results['warning']:
            report += f"- **{item['file']}**\n"
            report += f"  - 最后更新：{item['date']}\n"
            report += f"  - 剩余有效期：{item['expiry_days'] - item['days_old']} 天\n"
            report += f"  - 所属库：{item['library']}\n\n"
    else:
        report += "✅ 无即将过期文件\n\n"
    
    report += "---\n\n## 📝 无日期信息文件（需要添加日期）\n\n"
    
    if results['no_date']:
        for item in results['no_date']:
            report += f"- **{item['file']}**\n"
            report += f"  - 状态：{item['message']}\n\n"
    else:
        report += "✅ 所有文件都有日期信息\n\n"
    
    report += "---\n\n## ✅ 正常文件\n\n"
    report += f"共 {len(results['ok'])} 个文件日期正常\n\n"
    
    if results['error']:
        report += "---\n\n## ❌ 读取错误文件\n\n"
        for item in results['error']:
            report += f"- **{item['file']}**\n"
            report += f"  - 错误：{item['message']}\n\n"
    
    report += "---\n\n## 📋 建议行动\n\n"
    report += "### P0 - 最高优先级（立即处理）\n"
    report += "- [ ] 更新所有已过期文件日期为当前日期\n"
    report += "- [ ] 验证合规风控库内容有效性\n"
    report += "- [ ] 验证核心基础库内容有效性\n\n"
    
    report += "### P1 - 高优先级（本周处理）\n"
    report += "- [ ] 更新即将过期文件\n"
    report += "- [ ] 为无日期文件添加日期信息\n\n"
    
    report += "### P2 - 中优先级（本月处理）\n"
    report += "- [ ] 建立定期检查机制\n"
    report += "- [ ] 建立过期预警系统\n\n"
    
    return report

def main():
    """主函数"""
    print("\n" + "="*60)
    print("📅 RAG知识库日期检查工具")
    print("="*60)
    
    # 扫描文件
    results = scan_rag_files()
    
    # 生成报告
    report = generate_report(results)
    
    # 保存报告
    report_path = BASE_DIR / "圆心工作" / "工作记录系统" / f"RAG知识库日期检查报告_{CURRENT_DATE.strftime('%Y%m%d')}.md"
    report_path.write_text(report, encoding='utf-8')
    
    print("\n" + "="*60)
    print("✅ 检查完成！")
    print("="*60)
    print(f"📊 检查统计:")
    print(f"   - 已过期：{len(results['expired'])} 个")
    print(f"   - 即将过期：{len(results['warning'])} 个")
    print(f"   - 无日期信息：{len(results['no_date'])} 个")
    print(f"   - 正常：{len(results['ok'])} 个")
    print(f"\n📄 详细报告已保存至：{report_path.relative_to(BASE_DIR / '圆心工作')}")
    
    # 打印过期文件列表
    if results['expired']:
        print("\n❌ 已过期文件列表：")
        for item in results['expired'][:10]:  # 只显示前10个
            print(f"   - {item['file']} ({item['date']}, {item['message']})")
        if len(results['expired']) > 10:
            print(f"   ... 还有 {len(results['expired']) - 10} 个文件")

if __name__ == "__main__":
    main()

