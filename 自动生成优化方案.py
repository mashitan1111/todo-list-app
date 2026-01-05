#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成工作方式优化方案脚本
功能：一键生成工作方式优化方案，每次对话结束时自动执行
"""

import os
import re
from datetime import datetime
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
CONTEXT_FILE = BASE_DIR / "工作记录系统" / "工作上下文.md"
TASK_FILE = BASE_DIR / "工作记录系统" / "任务清单.md"
CACHE_FILE = BASE_DIR / "工作记录系统" / "检查缓存.md"
OUTPUT_DIR = BASE_DIR / "工作记录系统"
TEMPLATE_FILE = BASE_DIR / "RAG知识库" / "15_监管Skill库" / "04_工作方式优化Skill" / "03_工作方式优化报告模板.md"


def read_file_content(file_path):
    """读取文件内容"""
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取文件失败：{file_path}")
        print(f"   错误：{e}")
        return None


def analyze_communication_efficiency(context_content, task_content):
    """分析沟通效率"""
    analysis = {
        'understanding_accuracy': 0,
        'communication_rounds': 0,
        'repeat_confirmations': 0,
        'score': 0
    }
    
    # 分析理解准确率（简化分析）
    if context_content:
        # 检查是否主动读取了工作上下文
        if '工作上下文' in context_content or '工作状态' in context_content:
            analysis['understanding_accuracy'] += 2
        # 检查是否主动读取了任务清单
        if '任务清单' in context_content or '任务' in context_content:
            analysis['understanding_accuracy'] += 2
        # 检查是否主动分析了用户意图
        if '用户意图' in context_content or '需求' in context_content:
            analysis['understanding_accuracy'] += 2
    
    # 分析沟通轮次（简化分析，实际应该从对话历史中统计）
    # 这里假设平均3-5轮
    analysis['communication_rounds'] = 4
    
    # 分析重复确认次数（简化分析）
    if context_content:
        repeat_keywords = ['再次确认', '重复', '重新', '还是']
        analysis['repeat_confirmations'] = sum(1 for keyword in repeat_keywords if keyword in context_content)
    
    # 计算评分（简化计算）
    # 理解准确率评分（10分）
    if analysis['understanding_accuracy'] >= 6:
        understanding_score = 10
    elif analysis['understanding_accuracy'] >= 4:
        understanding_score = 8
    elif analysis['understanding_accuracy'] >= 2:
        understanding_score = 6
    else:
        understanding_score = 4
    
    # 沟通轮次评分（10分）
    if analysis['communication_rounds'] <= 3:
        rounds_score = 10
    elif analysis['communication_rounds'] <= 5:
        rounds_score = 8
    elif analysis['communication_rounds'] <= 7:
        rounds_score = 6
    else:
        rounds_score = 4
    
    # 重复确认次数评分（10分）
    if analysis['repeat_confirmations'] == 0:
        repeat_score = 10
    elif analysis['repeat_confirmations'] == 1:
        repeat_score = 8
    elif analysis['repeat_confirmations'] == 2:
        repeat_score = 6
    else:
        repeat_score = 4
    
    analysis['understanding_score'] = understanding_score
    analysis['rounds_score'] = rounds_score
    analysis['repeat_score'] = repeat_score
    analysis['score'] = understanding_score + rounds_score + repeat_score
    
    return analysis


def analyze_work_efficiency(context_content, task_content):
    """分析工作效率"""
    analysis = {
        'redundant_work': 0,
        'management_time': 0,
        'task_completion_rate': 0,
        'score': 0
    }
    
    # 分析重复工作
    if context_content:
        # 检查是否使用了检查缓存
        if '检查缓存' in context_content or '缓存' in context_content:
            analysis['redundant_work'] = 0
        else:
            analysis['redundant_work'] = 1
    
    # 分析管理时间（简化分析）
    # 检查是否使用了自动化脚本
    if context_content and ('自动化' in context_content or '脚本' in context_content):
        analysis['management_time'] = 0
    else:
        analysis['management_time'] = 1
    
    # 分析任务完成率
    if task_content:
        # 统计已完成任务
        completed_tasks = len(re.findall(r'- \*\*状态\*\*：已完成', task_content))
        # 统计总任务数
        total_tasks = len(re.findall(r'- \*\*状态\*\*：', task_content))
        if total_tasks > 0:
            analysis['task_completion_rate'] = (completed_tasks / total_tasks) * 100
        else:
            analysis['task_completion_rate'] = 0
    
    # 计算评分（简化计算）
    # 重复工作评分（10分）
    redundant_score = 10 if analysis['redundant_work'] == 0 else 6
    
    # 管理时间评分（10分）
    management_score = 10 if analysis['management_time'] == 0 else 6
    
    # 任务完成率评分（10分）
    if analysis['task_completion_rate'] >= 95:
        completion_score = 10
    elif analysis['task_completion_rate'] >= 85:
        completion_score = 8
    elif analysis['task_completion_rate'] >= 75:
        completion_score = 6
    else:
        completion_score = 4
    
    analysis['redundant_score'] = redundant_score
    analysis['management_score'] = management_score
    analysis['completion_score'] = completion_score
    analysis['score'] = redundant_score + management_score + completion_score
    
    return analysis


def analyze_work_quality(context_content, task_content):
    """分析工作质量"""
    analysis = {
        'error_rate': 0,
        'rework_rate': 0,
        'user_satisfaction': 0,
        'score': 0
    }
    
    # 分析错误率（简化分析）
    # 检查是否使用了监管Skill
    if context_content and ('监管Skill' in context_content or '监管' in context_content):
        analysis['error_rate'] = 5  # 假设使用了监管Skill，错误率较低
    else:
        analysis['error_rate'] = 15  # 假设未使用监管Skill，错误率较高
    
    # 分析返工率（简化分析）
    if context_content and ('返工' in context_content or '重新' in context_content):
        analysis['rework_rate'] = 20
    else:
        analysis['rework_rate'] = 10
    
    # 分析用户满意度（简化分析，假设为80%）
    analysis['user_satisfaction'] = 80
    
    # 计算评分（简化计算）
    # 错误率评分（10分）
    if analysis['error_rate'] < 5:
        error_score = 10
    elif analysis['error_rate'] < 10:
        error_score = 8
    elif analysis['error_rate'] < 15:
        error_score = 6
    else:
        error_score = 4
    
    # 返工率评分（10分）
    if analysis['rework_rate'] < 10:
        rework_score = 10
    elif analysis['rework_rate'] < 20:
        rework_score = 8
    elif analysis['rework_rate'] < 30:
        rework_score = 6
    else:
        rework_score = 4
    
    # 用户满意度评分（10分）
    if analysis['user_satisfaction'] >= 90:
        satisfaction_score = 10
    elif analysis['user_satisfaction'] >= 80:
        satisfaction_score = 8
    elif analysis['user_satisfaction'] >= 70:
        satisfaction_score = 6
    else:
        satisfaction_score = 4
    
    analysis['error_score'] = error_score
    analysis['rework_score'] = rework_score
    analysis['satisfaction_score'] = satisfaction_score
    analysis['score'] = error_score + rework_score + satisfaction_score
    
    return analysis


def generate_optimization_suggestions(comm_analysis, work_analysis, quality_analysis):
    """生成优化建议"""
    suggestions = {
        'p0': [],
        'p1': [],
        'p2': []
    }
    
    total_score = comm_analysis['score'] + work_analysis['score'] + quality_analysis['score']
    
    # P0级别优化建议（立即优化）
    if comm_analysis['understanding_score'] < 6:
        suggestions['p0'].append({
            'title': '提升理解准确率',
            'description': '当前理解准确率较低，需要主动读取工作上下文和任务清单',
            'action': [
                '每次对话前主动读取工作上下文',
                '每次对话前主动读取任务清单',
                '主动分析用户意图'
            ]
        })
    
    if comm_analysis['rounds_score'] < 6:
        suggestions['p0'].append({
            'title': '减少沟通轮次',
            'description': '当前沟通轮次过多，需要优化沟通方式',
            'action': [
                '使用沟通模板标准化沟通',
                '主动预判用户需求',
                '一次性提供完整方案'
            ]
        })
    
    if quality_analysis['error_score'] < 6:
        suggestions['p0'].append({
            'title': '降低错误率',
            'description': '当前错误率较高，需要加强质量检查',
            'action': [
                '使用监管Skill检查',
                '使用业务逻辑检查',
                '使用质量检查清单'
            ]
        })
    
    # P1级别优化建议（高优先级）
    if work_analysis['redundant_score'] < 8:
        suggestions['p1'].append({
            'title': '消除重复工作',
            'description': '存在重复工作，需要使用检查缓存',
            'action': [
                '使用检查缓存避免重复检查',
                '使用工作上下文避免重复分析',
                '使用任务清单避免重复规划'
            ]
        })
    
    if work_analysis['management_score'] < 8:
        suggestions['p1'].append({
            'title': '减少管理时间',
            'description': '管理时间较多，需要使用自动化脚本',
            'action': [
                '使用自动化脚本更新上下文',
                '使用自动化脚本更新任务清单',
                '使用自动化脚本更新缓存'
            ]
        })
    
    # P2级别优化建议（中优先级）
    if total_score >= 70 and total_score < 85:
        suggestions['p2'].append({
            'title': '持续优化工作方式',
            'description': '工作方式已达到基础水平，需要持续优化',
            'action': [
                '主动预判用户需求',
                '智能任务分解',
                '持续学习优化'
            ]
        })
    
    return suggestions


def generate_optimization_report(comm_analysis, work_analysis, quality_analysis, suggestions):
    """生成优化报告"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%Y-%m-%d %H:%M')
    
    total_score = comm_analysis['score'] + work_analysis['score'] + quality_analysis['score']
    
    # 确定优化等级
    if total_score >= 85:
        level = "90分"
    elif total_score >= 70:
        level = "85分"
    elif total_score >= 50:
        level = "70分"
    else:
        level = "50分"
    
    report = f"""# 工作方式优化报告

## 【元数据】
- **报告日期**：{time_str}
- **对话轮次**：{comm_analysis['communication_rounds']}轮
- **总体评分**：{total_score}/90分
- **优化等级**：{level}

---

## 📊 效率分析

### 沟通效率分析（{comm_analysis['score']}/30分）

#### 理解准确率（{comm_analysis['understanding_score']}/10分）
- **当前状态**：{comm_analysis['understanding_accuracy']}/6分
- **目标状态**：95%
- **差距分析**：需要提升理解准确率
- **优化建议**：
  - [ ] 主动读取工作上下文
  - [ ] 主动读取任务清单
  - [ ] 主动分析用户意图

#### 沟通轮次（{comm_analysis['rounds_score']}/10分）
- **当前状态**：{comm_analysis['communication_rounds']}轮
- **目标状态**：2-3轮
- **差距分析**：超出{comm_analysis['communication_rounds'] - 3}轮
- **优化建议**：
  - [ ] 使用沟通模板标准化沟通
  - [ ] 主动预判用户需求
  - [ ] 一次性提供完整方案

#### 重复确认次数（{comm_analysis['repeat_score']}/10分）
- **当前状态**：{comm_analysis['repeat_confirmations']}次
- **目标状态**：0次
- **差距分析**：需要减少{comm_analysis['repeat_confirmations']}次
- **优化建议**：
  - [ ] 主动引用相关文件
  - [ ] 主动分析上下文
  - [ ] 主动提供完整信息

---

### 工作效率分析（{work_analysis['score']}/30分）

#### 重复工作（{work_analysis['redundant_score']}/10分）
- **当前状态**：{'存在' if work_analysis['redundant_work'] > 0 else '不存在'}重复工作
- **目标状态**：无重复工作
- **差距分析**：{'需要消除重复工作' if work_analysis['redundant_work'] > 0 else '无重复工作'}
- **优化建议**：
  - [ ] 使用检查缓存避免重复检查
  - [ ] 使用工作上下文避免重复分析
  - [ ] 使用任务清单避免重复规划

#### 管理时间（{work_analysis['management_score']}/10分）
- **当前状态**：{'较多' if work_analysis['management_time'] > 0 else '较少'}管理时间
- **目标状态**：最小化
- **差距分析**：{'需要减少管理时间' if work_analysis['management_time'] > 0 else '管理时间已优化'}
- **优化建议**：
  - [ ] 使用自动化脚本更新上下文
  - [ ] 使用自动化脚本更新任务清单
  - [ ] 使用自动化脚本更新缓存

#### 任务完成率（{work_analysis['completion_score']}/10分）
- **当前状态**：{work_analysis['task_completion_rate']:.1f}%
- **目标状态**：95%
- **差距分析**：需要提升{95 - work_analysis['task_completion_rate']:.1f}%
- **优化建议**：
  - [ ] 使用任务清单跟踪任务
  - [ ] 使用检查清单确保完整
  - [ ] 使用依赖管理避免阻塞

---

### 工作质量分析（{quality_analysis['score']}/30分）

#### 错误率（{quality_analysis['error_score']}/10分）
- **当前状态**：{quality_analysis['error_rate']}%
- **目标状态**：<5%
- **差距分析**：需要降低{quality_analysis['error_rate'] - 5}%
- **优化建议**：
  - [ ] 使用监管Skill检查
  - [ ] 使用业务逻辑检查
  - [ ] 使用质量检查清单

#### 返工率（{quality_analysis['rework_score']}/10分）
- **当前状态**：{quality_analysis['rework_rate']}%
- **目标状态**：<10%
- **差距分析**：需要降低{quality_analysis['rework_rate'] - 10}%
- **优化建议**：
  - [ ] 主动预判用户需求
  - [ ] 主动提供完整方案
  - [ ] 主动检查质量

#### 用户满意度（{quality_analysis['satisfaction_score']}/10分）
- **当前状态**：{quality_analysis['user_satisfaction']}%
- **目标状态**：>90%
- **差距分析**：需要提升{90 - quality_analysis['user_satisfaction']}%
- **优化建议**：
  - [ ] 主动理解用户需求
  - [ ] 主动提供优化建议
  - [ ] 主动优化工作方式

---

## 🎯 优化建议

"""
    
    # 添加P0级别优化建议
    if suggestions['p0']:
        report += "### P0级别（立即优化）\n\n"
        for i, suggestion in enumerate(suggestions['p0'], 1):
            report += f"#### 问题{i}：{suggestion['title']}\n"
            report += f"- **影响**：{suggestion['description']}\n"
            report += "- **优化方案**：\n"
            for action in suggestion['action']:
                report += f"  - [ ] {action}\n"
            report += "\n"
    
    # 添加P1级别优化建议
    if suggestions['p1']:
        report += "### P1级别（高优先级）\n\n"
        for i, suggestion in enumerate(suggestions['p1'], 1):
            report += f"#### 问题{i}：{suggestion['title']}\n"
            report += f"- **影响**：{suggestion['description']}\n"
            report += "- **优化方案**：\n"
            for action in suggestion['action']:
                report += f"  - [ ] {action}\n"
            report += "\n"
    
    # 添加P2级别优化建议
    if suggestions['p2']:
        report += "### P2级别（中优先级）\n\n"
        for i, suggestion in enumerate(suggestions['p2'], 1):
            report += f"#### 问题{i}：{suggestion['title']}\n"
            report += f"- **影响**：{suggestion['description']}\n"
            report += "- **优化方案**：\n"
            for action in suggestion['action']:
                report += f"  - [ ] {action}\n"
            report += "\n"
    
    # 添加优化路径
    report += f"""## 📈 优化路径

### 当前状态：{total_score}分
### 目标状态：90分

### 优化路径
1. **从{total_score}分到70分**（基础优化）
   - [ ] 主动读取工作上下文
   - [ ] 使用沟通模板
   - [ ] 使用检查缓存
   - [ ] 使用任务清单

2. **从70分到85分**（进阶优化）
   - [ ] 主动预判用户需求
   - [ ] 智能任务分解
   - [ ] 自动化文件更新
   - [ ] 并行执行优化

3. **从85分到90分**（高级优化）
   - [ ] 智能上下文理解
   - [ ] 主动优化建议
   - [ ] 持续学习优化
   - [ ] 预测性优化

---

## 📋 下一步行动

"""
    
    # 添加下一步行动
    if suggestions['p0']:
        report += "### 立即行动（P0级别）\n"
        for suggestion in suggestions['p0']:
            for action in suggestion['action'][:2]:  # 只显示前2个行动
                report += f"- [ ] {action}\n"
        report += "\n"
    
    if suggestions['p1']:
        report += "### 本周行动（P1级别）\n"
        for suggestion in suggestions['p1']:
            for action in suggestion['action'][:2]:  # 只显示前2个行动
                report += f"- [ ] {action}\n"
        report += "\n"
    
    if suggestions['p2']:
        report += "### 本月行动（P2级别）\n"
        for suggestion in suggestions['p2']:
            for action in suggestion['action'][:2]:  # 只显示前2个行动
                report += f"- [ ] {action}\n"
        report += "\n"
    
    report += f"""## 📚 相关文件

### 工作记录
- `工作记录系统/工作上下文.md`
- `工作记录系统/任务清单.md`
- `工作记录系统/检查缓存.md`

### 优化工具
- `工具脚本/自动生成优化方案.py`
- `工具脚本/AI主动预判系统.py`
- `工具脚本/智能任务分解系统.py`

---

**报告生成时间**：{time_str}  
**下次检查时间**：下次对话结束时
"""
    
    return report


def main():
    """主函数"""
    print("=" * 60)
    print("自动生成工作方式优化方案")
    print("=" * 60)
    print()
    
    # 读取文件
    print("📖 正在读取工作上下文和任务清单...")
    context_content = read_file_content(CONTEXT_FILE)
    task_content = read_file_content(TASK_FILE)
    cache_content = read_file_content(CACHE_FILE)
    
    if not context_content:
        print("⚠️  警告：工作上下文文件不存在或无法读取")
        print("   将使用默认值进行分析")
        context_content = ""
    
    if not task_content:
        print("⚠️  警告：任务清单文件不存在或无法读取")
        print("   将使用默认值进行分析")
        task_content = ""
    
    # 分析效率
    print("📊 正在分析沟通效率...")
    comm_analysis = analyze_communication_efficiency(context_content, task_content)
    print(f"   沟通效率评分：{comm_analysis['score']}/30分")
    
    print("📊 正在分析工作效率...")
    work_analysis = analyze_work_efficiency(context_content, task_content)
    print(f"   工作效率评分：{work_analysis['score']}/30分")
    
    print("📊 正在分析工作质量...")
    quality_analysis = analyze_work_quality(context_content, task_content)
    print(f"   工作质量评分：{quality_analysis['score']}/30分")
    
    total_score = comm_analysis['score'] + work_analysis['score'] + quality_analysis['score']
    print(f"\n✅ 总体评分：{total_score}/90分")
    
    # 生成优化建议
    print("\n🎯 正在生成优化建议...")
    suggestions = generate_optimization_suggestions(comm_analysis, work_analysis, quality_analysis)
    print(f"   P0级别建议：{len(suggestions['p0'])}个")
    print(f"   P1级别建议：{len(suggestions['p1'])}个")
    print(f"   P2级别建议：{len(suggestions['p2'])}个")
    
    # 生成优化报告
    print("\n📝 正在生成优化报告...")
    report = generate_optimization_report(comm_analysis, work_analysis, quality_analysis, suggestions)
    
    # 保存报告
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    output_file = OUTPUT_DIR / f"工作方式优化方案_{date_str}.md"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 优化报告已保存：{output_file}")
    except Exception as e:
        print(f"❌ 保存报告失败：{e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ 工作方式优化方案生成完成！")
    print("=" * 60)
    print(f"\n📄 报告文件：{output_file}")
    print(f"📊 总体评分：{total_score}/90分")
    print(f"🎯 优化建议：P0({len(suggestions['p0'])}) P1({len(suggestions['p1'])}) P2({len(suggestions['p2'])})")
    print("\n💡 提示：此脚本已集成到Agent工作流程，每次对话结束时自动执行")


if __name__ == "__main__":
    main()

