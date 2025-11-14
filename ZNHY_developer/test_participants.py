#!/usr/bin/env python3
"""
专门测试参会人员提取逻辑
"""

import re

def test_participants_extraction():
    """测试参会人员提取逻辑"""
    
    # 测试用的会议文本
    test_text = """
    会议主题：下季度产品推广方案
    会议时间：2023年10月15日 14:00-16:00
    会议地点：公司三楼大会议室
    主持人：张三
    参会人员：李四、王五、赵六
    会议时长：约2小时
    
    会议议程：
    1. 讨论线上广告投放预算分配
    2. 讨论新版APP研发进度
    3. 讨论下月底团建活动安排
    
    会前准备事项：提前准备相关资料
    """
    
    print("测试参会人员提取逻辑...")
    print()
    print(f"原始会议文本：\n{test_text}")
    print()
    
    # 尝试提取参会人员
    participants_match = re.search(r'参会人员[:：]?\s*([^\n]+)', test_text)
    participants = []
    
    if participants_match:
        participants_str = participants_match.group(1).strip()
        print(f"匹配到的参会人员字符串：'{participants_str}'")
        
        # 移除前缀常见词如"包括"、"有"、"为"、"以及"
        participants_str = re.sub(r'^(包括|有|为|以及)\s*', '', participants_str)
        print(f"移除前缀后的字符串：'{participants_str}'")
        
        # 支持顿号、逗号、中文逗号、"和"、"以及"分隔，并且去掉可能的空格
        participants_str = participants_str.replace('，', '、').replace(',', '、').replace('和', '、').replace('以及', '、')
        print(f"统一分隔符后的字符串：'{participants_str}'")
        
        participants = [p.strip() for p in participants_str.split('、') if p.strip()]
        print(f"分割后的参会人员列表：{participants}")
    else:
        print("未匹配到参会人员")
    
    print()
    print(f"最终提取结果：{participants}")
    print()
    
    return participants

def main():
    """主函数"""
    print("=== 参会人员提取逻辑测试 ===")
    print()
    
    participants = test_participants_extraction()
    
    if participants == ['李四', '王五', '赵六']:
        print("✅ 测试成功！参会人员提取逻辑正常")
    else:
        print("❌ 测试失败！参会人员提取逻辑存在问题")

if __name__ == "__main__":
    main()