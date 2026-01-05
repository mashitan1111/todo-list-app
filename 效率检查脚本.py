#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
效率检查脚本
用途：检查Agent是否遵守效率优化规则
创建日期：2026-01-04
版本：V1.0
"""

def check_batch_operation(file_count, used_script):
    """
    检查批量操作是否使用脚本
    
    参数:
        file_count: 需要操作的文件数量
        used_script: 是否使用了脚本
    
    返回:
        (是否通过, 消息)
    """
    if file_count >= 3 and not used_script:
        return False, "❌ 批量操作（≥3个文件）必须使用脚本"
    return True, "✅ 批量操作检查通过"

def check_demand_prediction(predicted):
    """
    检查是否预判了需求
    
    参数:
        predicted: 是否预判了需求
    
    返回:
        (是否通过, 消息)
    """
    if not predicted:
        return False, "❌ 必须主动预判用户需求"
    return True, "✅ 需求预判检查通过"

def check_cache_usage(checked_cache, used_cache):
    """
    检查是否使用了缓存
    
    参数:
        checked_cache: 是否检查了缓存
        used_cache: 是否使用了缓存
    
    返回:
        (是否通过, 消息)
    """
    if not checked_cache:
        return False, "❌ 必须检查缓存"
    if checked_cache and not used_cache:
        return True, "⚠️  已检查缓存，但缓存无效，已重新查询"
    return True, "✅ 缓存使用检查通过"

def efficiency_score(file_count, used_script, predicted, checked_cache, used_cache):
    """
    计算效率评分
    
    参数:
        file_count: 需要操作的文件数量
        used_script: 是否使用了脚本
        predicted: 是否预判了需求
        checked_cache: 是否检查了缓存
        used_cache: 是否使用了缓存
    
    返回:
        (总分, 批量操作消息, 需求预判消息, 缓存使用消息)
    """
    score = 25
    
    # 批量操作检查（10分）
    batch_ok, batch_msg = check_batch_operation(file_count, used_script)
    if not batch_ok:
        score -= 10
    
    # 需求预判检查（10分）
    pred_ok, pred_msg = check_demand_prediction(predicted)
    if not pred_ok:
        score -= 10
    
    # 缓存使用检查（5分）
    cache_ok, cache_msg = check_cache_usage(checked_cache, used_cache)
    if not cache_ok:
        score -= 5
    
    return score, batch_msg, pred_msg, cache_msg

def generate_report(file_count, used_script, predicted, checked_cache, used_cache):
    """
    生成效率检查报告
    
    参数:
        file_count: 需要操作的文件数量
        used_script: 是否使用了脚本
        predicted: 是否预判了需求
        checked_cache: 是否检查了缓存
        used_cache: 是否使用了缓存
    
    返回:
        报告文本
    """
    score, batch_msg, pred_msg, cache_msg = efficiency_score(
        file_count, used_script, predicted, checked_cache, used_cache
    )
    
    report = f"""
{'='*60}
效率检查报告
{'='*60}

📊 效率评分：{score}/25

📋 检查结果：
1. 批量操作：{batch_msg}
2. 需求预判：{pred_msg}
3. 缓存使用：{cache_msg}

{'='*60}
"""
    
    if score >= 20:
        report += "✅ 效率检查通过（≥20分）\n"
    else:
        report += "❌ 效率检查不通过（<20分，一票否决项）\n"
        report += "⚠️  必须重新执行任务，遵守效率优化规则\n"
    
    report += f"{'='*60}\n"
    
    return report

if __name__ == "__main__":
    # 示例使用
    print("="*60)
    print("效率检查脚本 - 示例")
    print("="*60)
    print()
    
    # 示例1：全部通过
    print("示例1：全部通过")
    print(generate_report(
        file_count=5,
        used_script=True,
        predicted=True,
        checked_cache=True,
        used_cache=True
    ))
    
    # 示例2：批量操作违规
    print("\n示例2：批量操作违规")
    print(generate_report(
        file_count=5,
        used_script=False,  # 违规：批量操作未使用脚本
        predicted=True,
        checked_cache=True,
        used_cache=True
    ))
    
    # 示例3：需求预判违规
    print("\n示例3：需求预判违规")
    print(generate_report(
        file_count=2,
        used_script=True,
        predicted=False,  # 违规：未预判需求
        checked_cache=True,
        used_cache=True
    ))

