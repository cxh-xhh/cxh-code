from utils.llm_parser import MeetingParser
from utils.word_generator import WordGenerator

# 创建解析器实例
parser = MeetingParser()

# 测试文本
text = '''会议主题：项目进度讨论
时间：今天下午3点
地点：会议室A
参会人员：张三、李四、王五
会议内容：讨论了项目的进度和后续计划，确定了下一步工作安排。'''

# 解析会议内容
data = parser.parse_meeting_text(text)

# 打印结果
print('会议主题:', data.get('meeting_theme', '未找到会议主题'))
print('时间:', data.get('meeting_time', '未找到会议时间').replace('时间：', '').strip())
print('地点:', data.get('meeting_location', '未找到会议地点').replace('地点：', '').strip())
print('会议主持人:', data.get('host', '未找到主持人信息'))
print('参会人员:', data.get('participants', []))
print('参会人数:', data.get('participant_count', 0))
print('会议内容:', data.get('meeting_content', '未找到会议内容'))
print('所有提取的信息:', data)

# 生成文档
generator = WordGenerator()
buffer = generator.generate_document(data)

# 保存文档
with open('test_extraction.docx', 'wb') as f:
    f.write(buffer.getvalue())

print('文档已保存为test_extraction.docx')