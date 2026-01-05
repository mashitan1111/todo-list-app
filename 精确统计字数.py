#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""精确统计三天直播逐字稿字数"""

import re
import os

# 读取文件
script_dir = os.path.dirname(os.path.abspath(__file__))
content_file = os.path.join(script_dir, '三天直播课程完整逐字稿_内部渠道版_完整内容.md')

with open(content_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 统计总字符数
total_chars = len(content)
chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

# 提取所有引号内的说话内容（逐字稿）
# 匹配模式：以"开头，以"结尾的行
speech_lines = []
for line in content.split('\n'):
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        speech_text = line[1:-1]  # 去掉引号
        if speech_text.strip():  # 确保不是空内容
            speech_lines.append(speech_text)

# 统计说话内容字数
speech_chars = sum(len(s) for s in speech_lines)

# 按天分割统计
day1_start = content.find('# Day1：破冰与归因')
day2_start = content.find('# Day2：核心逼单日')
day3_start = content.find('# Day3：答疑与清尾')

day1_content = content[day1_start:day2_start] if day2_start != -1 else content[day1_start:]
day2_content = content[day2_start:day3_start] if day3_start != -1 else content[day2_start:]
day3_content = content[day3_start:] if day3_start != -1 else ''

# 提取每天的说话内容
day1_speech = []
for line in day1_content.split('\n'):
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        speech_text = line[1:-1]
        if speech_text.strip():
            day1_speech.append(speech_text)

day2_speech = []
for line in day2_content.split('\n'):
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        speech_text = line[1:-1]
        if speech_text.strip():
            day2_speech.append(speech_text)

day3_speech = []
for line in day3_content.split('\n'):
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        speech_text = line[1:-1]
        if speech_text.strip():
            day3_speech.append(speech_text)

day1_chars = sum(len(s) for s in day1_speech)
day2_chars = sum(len(s) for s in day2_speech)
day3_chars = sum(len(s) for s in day3_speech)

# 输出结果
print('=' * 70)
print('三天直播逐字稿字数统计报告')
print('=' * 70)
print()
print('【总体统计】')
print(f'文件总字符数（含格式标记、标点、空格）: {total_chars:,} 字符')
print(f'中文字符数: {chinese_chars:,} 字')
print(f'逐字稿说话内容字数（仅引号内）: {speech_chars:,} 字')
print(f'逐字稿说话内容条数: {len(speech_lines)} 条')
print()
print('=' * 70)
print('【分天统计 - 逐字稿说话内容】')
print('=' * 70)
print(f'Day1（破冰与归因）: {day1_chars:,} 字 ({len(day1_speech)} 条)')
print(f'Day2（核心逼单日）: {day2_chars:,} 字 ({len(day2_speech)} 条)')
print(f'Day3（答疑与清尾）: {day3_chars:,} 字 ({len(day3_speech)} 条)')
print()
print('=' * 70)
print('【字数需求分析】')
print('=' * 70)
print('标准参考：')
print('  - 正常语速：200-250字/分钟')
print('  - 2小时直播 = 120分钟 × 200字/分钟 = 24,000字（最低）')
print('  - 2小时直播 = 120分钟 × 250字/分钟 = 30,000字（理想）')
print()
print('当前字数评估：')
day1_status = '✅ 充足' if day1_chars >= 20000 else '⚠️ 需要补充'
day2_status = '✅ 充足' if day2_chars >= 20000 else '⚠️ 需要补充'
day3_status = '✅ 充足' if day3_chars >= 20000 else '⚠️ 需要补充'
total_status = '✅ 充足' if speech_chars >= 60000 else '⚠️ 需要补充'

print(f'  Day1: {day1_chars:,} 字 - {day1_status} (目标: 24,000-30,000字)')
if day1_chars < 20000:
    print(f'    缺口: {20000 - day1_chars:,} - {30000 - day1_chars:,} 字')

print(f'  Day2: {day2_chars:,} 字 - {day2_status} (目标: 24,000-30,000字)')
if day2_chars < 20000:
    print(f'    缺口: {20000 - day2_chars:,} - {30000 - day2_chars:,} 字')

print(f'  Day3: {day3_chars:,} 字 - {day3_status} (目标: 24,000-30,000字)')
if day3_chars < 20000:
    print(f'    缺口: {20000 - day3_chars:,} - {30000 - day3_chars:,} 字')

print(f'  总计: {speech_chars:,} 字 - {total_status} (目标: 72,000-90,000字)')
if speech_chars < 60000:
    print(f'    总缺口: {60000 - speech_chars:,} - {90000 - speech_chars:,} 字')
print()
print('=' * 70)
print('【完成度】')
print('=' * 70)
day1_percent = (day1_chars / 24000) * 100 if day1_chars < 24000 else 100
day2_percent = (day2_chars / 24000) * 100 if day2_chars < 24000 else 100
day3_percent = (day3_chars / 24000) * 100 if day3_chars < 24000 else 100
total_percent = (speech_chars / 72000) * 100 if speech_chars < 72000 else 100

print(f'Day1完成度: {day1_percent:.1f}%')
print(f'Day2完成度: {day2_percent:.1f}%')
print(f'Day3完成度: {day3_percent:.1f}%')
print(f'总体完成度: {total_percent:.1f}%')
print()

