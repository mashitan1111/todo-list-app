#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent工作质量自动评分系统
功能：自动对生成的内容进行评分，低于80分自动触发重新工作
"""

import re
import os
import json
from datetime import datetime

class QualityScorer:
    """质量评分器"""
    
    def __init__(self):
        self.min_score = 80  # 最低合格分数
        self.target_score = 98  # 目标分数
        self.max_iterations = 3  # 最大迭代次数
        
        # 加载违禁词清单
        self.forbidden_words = self._load_forbidden_words()
        
        # 加载安全话术替换表
        self.safe_replacements = self._load_safe_replacements()
    
    def _load_forbidden_words(self):
        """加载违禁词清单"""
        forbidden_file = '圆心工作/RAG知识库/02_合规风控库/01_违禁词完整清单.md'
        if os.path.exists(forbidden_file):
            with open(forbidden_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取违禁词（简化处理）
                words = re.findall(r'[-•]\s*([^\n]+)', content)
                return [w.strip() for w in words if w.strip()]
        return []
    
    def _load_safe_replacements(self):
        """加载安全话术替换表"""
        replacement_file = '圆心工作/RAG知识库/02_合规风控库/02_安全话术替换表.md'
        if os.path.exists(replacement_file):
            with open(replacement_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取替换表（简化处理）
                replacements = {}
                lines = content.split('\n')
                for line in lines:
                    if '→' in line or '->' in line:
                        parts = re.split(r'[→->]', line)
                        if len(parts) == 2:
                            old = parts[0].strip()
                            new = parts[1].strip()
                            replacements[old] = new
                return replacements
        return {}
    
    def check_forbidden_words(self, content):
        """检查违禁词"""
        found_words = []
        for word in self.forbidden_words:
            if word in content:
                found_words.append(word)
        return found_words
    
    def check_safe_replacements(self, content):
        """检查安全话术替换"""
        not_replaced = []
        for old_word, new_word in self.safe_replacements.items():
            if old_word in content and new_word not in content:
                not_replaced.append(old_word)
        return not_replaced
    
    def count_speech_words(self, content):
        """统计逐字稿说话内容字数"""
        # 提取引号内的内容
        speech_lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                speech_text = line[1:-1]  # 去掉引号
                if speech_text.strip():
                    speech_lines.append(speech_text)
        
        total_chars = sum(len(s) for s in speech_lines)
        return total_chars, len(speech_lines)
    
    def score_content_quality(self, content):
        """评分：内容质量（30分）"""
        score = 0
        
        # 1.1 痛点共鸣度（10分）
        pain_keywords = ['深夜', '绝望', '门缝', '卑微', '羞耻', '小心翼翼', '凌晨', '眼泪']
        pain_count = sum(1 for kw in pain_keywords if kw in content)
        if pain_count >= 6:
            score += 10
        elif pain_count >= 4:
            score += 8
        elif pain_count >= 2:
            score += 6
        else:
            score += 4
        
        # 1.2 理论体系完整性（10分）
        epd_keywords = ['E模块', 'P模块', 'D模块', '情绪阻断', '模式重构', '动力激活', 'EPD系统']
        epd_count = sum(1 for kw in epd_keywords if kw in content)
        if epd_count >= 6:
            score += 10
        elif epd_count >= 4:
            score += 8
        elif epd_count >= 2:
            score += 6
        else:
            score += 4
        
        # 1.3 价值交付清晰度（10分）
        value_keywords = ['12.9', '12980', '价值', '得到', '专家', '诊断', '电话']
        value_count = sum(1 for kw in value_keywords if kw in content)
        if value_count >= 4:
            score += 10
        elif value_count >= 3:
            score += 8
        elif value_count >= 2:
            score += 6
        else:
            score += 4
        
        return score
    
    def score_conversion_design(self, content):
        """评分：转化设计（25分）"""
        score = 0
        
        # 2.1 转化节点设计（10分）
        conversion_keywords = ['报名', '链接', '已拍', '想报名', '想抢', '转化']
        conversion_count = sum(1 for kw in conversion_keywords if kw in content)
        if conversion_count >= 3:
            score += 10
        elif conversion_count >= 2:
            score += 8
        elif conversion_count >= 1:
            score += 6
        else:
            score += 4
        
        # 2.2 心理策略应用（10分）
        psychology_keywords = ['恐惧', '沉没成本', '稀缺', '紧迫', '倒计时', '仅限']
        psychology_count = sum(1 for kw in psychology_keywords if kw in content)
        if psychology_count >= 4:
            score += 10
        elif psychology_count >= 3:
            score += 8
        elif psychology_count >= 2:
            score += 6
        else:
            score += 4
        
        # 2.3 稀缺性与紧迫感（5分）
        scarcity_keywords = ['仅限', '名额', '最后', '错过', '倒计时']
        scarcity_count = sum(1 for kw in scarcity_keywords if kw in content)
        if scarcity_count >= 3:
            score += 5
        elif scarcity_count >= 2:
            score += 4
        elif scarcity_count >= 1:
            score += 3
        else:
            score += 1
        
        return score
    
    def score_compliance(self, content):
        """评分：合规性（20分）"""
        score = 0
        
        # 3.1 违禁词检查（10分）
        forbidden_words = self.check_forbidden_words(content)
        if len(forbidden_words) == 0:
            score += 10
        elif len(forbidden_words) <= 2:
            score += 8
        elif len(forbidden_words) <= 5:
            score += 6
        else:
            score += 4
        
        # 3.2 安全话术替换（10分）
        not_replaced = self.check_safe_replacements(content)
        if len(not_replaced) == 0:
            score += 10
        elif len(not_replaced) <= 2:
            score += 8
        elif len(not_replaced) <= 5:
            score += 6
        else:
            score += 4
        
        return score
    
    def score_interaction_design(self, content):
        """评分：互动设计（15分）"""
        score = 0
        
        # 4.1 公屏互动设计（8分）
        interaction_keywords = ['打在公屏上', '扣1', '互动', '想救', '想了解', '能做到']
        interaction_count = sum(1 for kw in interaction_keywords if kw in content)
        if interaction_count >= 5:
            score += 8
        elif interaction_count >= 3:
            score += 6
        elif interaction_count >= 2:
            score += 4
        else:
            score += 2
        
        # 4.2 视觉呈现（7分）
        visual_keywords = ['道具', '展示', '揉皱', '简历', '铁锁', '涂黑', '爱']
        visual_count = sum(1 for kw in visual_keywords if kw in content)
        if visual_count >= 4:
            score += 7
        elif visual_count >= 3:
            score += 5
        elif visual_count >= 2:
            score += 3
        else:
            score += 1
        
        return score
    
    def score_rhythm_control(self, content):
        """评分：节奏控制（10分）"""
        score = 0
        
        # 5.1 时间节点控制（5分）
        time_keywords = ['19:00', '19:10', '19:40', '20:20', '20:50', '21:00', '分钟']
        time_count = sum(1 for kw in time_keywords if kw in content)
        if time_count >= 5:
            score += 5
        elif time_count >= 3:
            score += 4
        elif time_count >= 2:
            score += 3
        else:
            score += 1
        
        # 5.2 节奏感（5分）
        rhythm_keywords = ['停顿', '语气', '动作', '强调', '互动']
        rhythm_count = sum(1 for kw in rhythm_keywords if kw in content)
        if rhythm_count >= 10:
            score += 5
        elif rhythm_count >= 7:
            score += 4
        elif rhythm_count >= 5:
            score += 3
        else:
            score += 1
        
        return score
    
    def score_word_count(self, content):
        """评分：字数充足度（10分）"""
        total_chars, speech_lines = self.count_speech_words(content)
        
        # 目标：24,000-30,000字/天
        if total_chars >= 24000:
            score = 10
        elif total_chars >= 20000:
            score = 8
        elif total_chars >= 15000:
            score = 6
        elif total_chars >= 10000:
            score = 4
        else:
            score = 2
        
        return score, total_chars, speech_lines
    
    def score(self, content):
        """综合评分"""
        scores = {}
        
        # 各维度评分
        scores['content_quality'] = self.score_content_quality(content)
        scores['conversion_design'] = self.score_conversion_design(content)
        scores['compliance'] = self.score_compliance(content)
        scores['interaction_design'] = self.score_interaction_design(content)
        scores['rhythm_control'] = self.score_rhythm_control(content)
        scores['word_count'], word_count, speech_lines = self.score_word_count(content)
        
        # 总分
        total_score = sum(scores.values())
        
        # 检查违禁词
        forbidden_words = self.check_forbidden_words(content)
        not_replaced = self.check_safe_replacements(content)
        
        return {
            'total_score': total_score,
            'scores': scores,
            'word_count': word_count,
            'speech_lines': speech_lines,
            'forbidden_words': forbidden_words,
            'not_replaced': not_replaced,
            'passed': total_score >= self.min_score
        }
    
    def generate_report(self, result, content_file):
        """生成评分报告"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file': content_file,
            'total_score': result['total_score'],
            'scores': result['scores'],
            'word_count': result['word_count'],
            'speech_lines': result['speech_lines'],
            'forbidden_words': result['forbidden_words'],
            'not_replaced': result['not_replaced'],
            'passed': result['passed'],
            'grade': self._get_grade(result['total_score'])
        }
        
        return report
    
    def _get_grade(self, score):
        """获取等级"""
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '合格'
        else:
            return '不合格'
    
    def save_report(self, report, output_file):
        """保存评分报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def print_report(self, report):
        """打印评分报告"""
        print('=' * 70)
        print('工作质量评分报告')
        print('=' * 70)
        print(f'评分时间：{report["date"]}')
        print(f'文件：{report["file"]}')
        print()
        print('【各维度得分】')
        print(f'内容质量：{report["scores"]["content_quality"]}/30分')
        print(f'转化设计：{report["scores"]["conversion_design"]}/25分')
        print(f'合规性：{report["scores"]["compliance"]}/20分')
        print(f'互动设计：{report["scores"]["interaction_design"]}/15分')
        print(f'节奏控制：{report["scores"]["rhythm_control"]}/10分')
        print(f'字数充足度：{report["scores"]["word_count"]}/10分')
        print()
        print(f'【总分】{report["total_score"]}/110分')
        print(f'【等级】{report["grade"]}')
        print(f'【是否通过】{"✅ 通过" if report["passed"] else "❌ 不通过"}')
        print()
        print(f'【字数统计】')
        print(f'逐字稿说话内容：{report["word_count"]:,} 字')
        print(f'说话内容条数：{report["speech_lines"]} 条')
        print()
        if report['forbidden_words']:
            print(f'【违禁词】{len(report["forbidden_words"])} 个')
            for word in report['forbidden_words'][:5]:
                print(f'  - {word}')
        if report['not_replaced']:
            print(f'【未替换敏感词】{len(report["not_replaced"])} 个')
            for word in report['not_replaced'][:5]:
                print(f'  - {word}')
        print('=' * 70)


def main():
    """主函数"""
    scorer = QualityScorer()
    
    # 读取内容文件
    content_file = '圆心工作/三天直播课程完整逐字稿_内部渠道版_完整内容.md'
    
    if not os.path.exists(content_file):
        print(f'❌ 文件不存在：{content_file}')
        return
    
    print(f'正在读取文件：{content_file}')
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print('正在评分...')
    result = scorer.score(content)
    
    # 生成报告
    report = scorer.generate_report(result, content_file)
    
    # 打印报告
    scorer.print_report(report)
    
    # 保存报告
    report_file = '圆心工作/质量评分报告.json'
    scorer.save_report(report, report_file)
    print(f'\n✅ 评分报告已保存：{report_file}')
    
    # 判断是否需要重新工作
    if not result['passed']:
        print(f'\n⚠️ 分数低于{scorer.min_score}分，需要重新工作！')
        print('建议：')
        print('1. 补充字数不足的内容')
        print('2. 检查并替换违禁词')
        print('3. 增加更多案例和互动环节')
        print('4. 完善转化设计')
    else:
        print(f'\n✅ 分数达到{scorer.min_score}分以上，通过！')


if __name__ == '__main__':
    main()

