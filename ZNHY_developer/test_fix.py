import json
import requests

# 测试不同的输入内容
test_inputs = [
    "会议主题：项目进度讨论 时间：今天下午3点 地点：会议室A 参会人员：张三、李四、王五 议程：讨论项目当前进度和下一步计划",
    "今天上午十点召开产品评审会，地点在公司三楼会议室，参会人员包括产品经理、开发人员和测试人员。主要评审新产品的设计方案和功能需求。",
    "会议主题：团队建设活动 时间：下周五下午2点 地点：市中心公园 参会人员：全体团队成员 议程：讨论团建活动的具体安排"
]

# 向服务器发送请求
def test_generate(input_text):
    url = "http://localhost:5000/generate"
    headers = {"Content-Type": "application/json"}
    data = {"text": input_text}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"输入: {input_text}")
            print(f"请求成功，返回文件大小: {len(response.content)} bytes")
            print("\n")
            return True
        else:
            print(f"输入: {input_text}")
            print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
            print("\n")
            return False
    except Exception as e:
        print(f"输入: {input_text}")
        print(f"请求出错: {str(e)}")
        print("\n")
        return False

# 执行测试
for i, input_text in enumerate(test_inputs, 1):
    print(f"测试第 {i} 次：")
    test_generate(input_text)

print("所有测试完成！")