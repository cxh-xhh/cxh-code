import requests
import json

# 测试数据
test_cases = [
    "会议主题：项目进度讨论 时间：今天下午3点 地点：会议室A 参会人员：张三、李四、王五 议程：讨论项目当前进度和下一步计划",
    "今天上午十点召开产品评审会，地点在公司三楼会议室，参会人员包括产品经理、开发人员和测试人员。主要评审新产品的设计方案和功能需求。",
    "会议主题：团队建设活动 时间：下周五下午2点 地点：市中心公园 参会人员：全体团队成员 议程：讨论团建活动的具体安排"
]

for i, input_text in enumerate(test_cases, 1):
    print(f"\n测试第 {i} 次：")
    print(f"输入: {input_text[:50]}...")
    
    response = requests.post(
    "http://localhost:5000/generate",
    json={"text": input_text},
    stream=True
)
    
    if response.status_code == 200:
        print(f"请求成功，返回文件大小: {len(response.content)} bytes")
        
        # 保存文件以便查看
        with open(f"test_output_{i}.docx", "wb") as f:
            f.write(response.content)
        print(f"生成的文档已保存为: test_output_{i}.docx")
    else:
        print(f"请求失败，状态码: {response.status_code}")

print("\n所有测试完成！")