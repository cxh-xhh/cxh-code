import json
import requests
import os
from typing import Dict, Any

class MeetingParser:
    def __init__(self):
        # 配置Ollama API端点
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen:1.8b"  # 使用中文支持更好的qwen模型
        
    def parse_meeting_text(self, text: str) -> Dict[str, Any]:
        """使用大模型解析会议文本"""
        
        # 构建提示词
        prompt = self._build_prompt(text)
        
        try:
            # 尝试连接Ollama
            response = self._call_ollama(prompt)
            return self._parse_response(response, text)
        except Exception as e:
            print(f"Ollama调用失败: {e}, 使用模拟数据")
            return self._get_mock_data(text)
    
    def _build_prompt(self, text: str) -> str:
        """构建解析提示词"""
        return f"""
你是一个会议信息提取专家，请严格从以下会议内容中提取所有相关信息：

会议内容："{text}"

请从提供的会议内容中提取所有相关信息，并严格按照JSON格式输出。

特别注意：必须准确提取参会人员信息：
- 参会人员包括主持人和所有列出的参会者
- 主持人从'主持人：'关键字后提取
- 其他参会者从'参会人员：'关键字后提取（以顿号分隔）
- 将所有人员姓名作为独立元素放入participants数组，确保不遗漏任何人员

输出格式示例（仅用于说明结构，请勿直接使用示例内容）：
```json
{{
  "meeting_topic": "下季度产品推广方案",
  "meeting_time": "2023年10月15日下午3点",
  "meeting_location": "公司三楼大会议室",
  "host": "李明",
  "participants": ["李明", "张娜", "王磊", "赵晓雨"],
  "participant_count": 4,
  "meeting_duration": "约两小时",
  "topics": [
    {{
      "title": "下季度产品推广方案（线上广告投放预算分配）",
      "leader": "李明",
      "preparation": "准备相关数据"
    }},
    {{
      "title": "新版APP研发进度",
      "leader": "王磊"
    }},
    {{
      "title": "下月底团建活动安排（备选地点：近郊民宿、爬山）",
      "leader": "张娜",
      "participants": "全体参会者（赵晓雨参与讨论）"
    }}
  ],
  "pre_meeting_preparations": "提前将会议资料发到群里"
}}
```

注意事项：
1. **JSON格式要求**：必须使用英文引号，不得使用中文引号；必须是 valid JSON 格式
2. **participant_count字段要求**：必须等于participants数组的长度，为数字类型
3. 所有字段的值必须来自输入的会议内容，不得使用任何示例内容或外部信息
4. 输出仅为JSON格式，不得包含任何解释性文字或标记（如```json```等）
"""
    
    def _call_ollama(self, prompt: str) -> str:
        """调用Ollama API"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        print(f"Ollama请求参数: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(self.ollama_url, json=payload, timeout=30)
        print(f"Ollama响应状态码: {response.status_code}")
        print(f"Ollama响应头: {dict(response.headers)}")
        print(f"Ollama响应内容: {response.text}")
        response.raise_for_status()
        
        result = response.json()
        print(f"Ollama响应JSON: {json.dumps(result, ensure_ascii=False)}")
        return result.get('response', '')
    
    def _parse_response(self, response: str, text: str) -> Dict[str, Any]:
        """解析大模型的响应并格式化输出"""
        import json
        print(f"大模型原始响应: {response}")
        
        # 预处理响应：移除markdown的JSON语法糖
        if "```json" in response:
            response = response.split("```json")[1]
        if "```" in response:
            response = response.split("```")[0]
        # 去除首尾空白
        response = response.strip()
        # 将Python None转换为JSON null
        response = response.replace("None", "null")
        try:
            # 直接解析整个响应（如果响应本身是纯JSON）
            result = json.loads(response.strip())
            print(f"成功解析响应: {result}")
        except Exception as e:
            print(f"直接解析响应失败: {e}")
            # 尝试从响应中提取JSON块
            try:
                # 尝试从响应中提取JSON块（支持多行JSON）
                response_str = response.strip()
                # 找到JSON对象的起始位置（第一个'{'）
                start_idx = response_str.find('{')
                if start_idx != -1:
                    # 计算括号深度，找到对应的闭合'}'
                    depth = 1
                    end_idx = start_idx + 1
                    for char in response_str[start_idx+1:]:
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:
                                break
                        end_idx += 1
                    # 提取完整的JSON块
                    json_block = response_str[start_idx:end_idx+1]
                    # 解析JSON块
                    result = json.loads(json_block)
                    print(f"成功从响应中提取JSON块: {result}")
                else:
                    # 如果没有找到JSON对象，抛出异常
                    raise Exception("未找到JSON结构")
            except Exception as e2:
                print(f"提取JSON块失败: {e2}")
                # 如果两次解析都失败，返回模拟数据
                print("两次解析都失败，返回模拟数据")
                return self._get_mock_data(text)
        # 确保所有必需的字段都存在，缺少的字段使用模拟数据填充
        mock_data = self._get_mock_data(text)
        # 创建一个新的结果字典，优先使用大模型的响应，缺少的字段使用模拟数据
        complete_result = mock_data.copy()
        complete_result.update(result)
        
        participants = complete_result.get("participants", [])
        fixed_participants = []
        for p in participants:
            name = None
            if isinstance(p, dict):
                # 处理对象数组
                if "participant_name" in p:
                    name = p["participant_name"].strip()
                elif "name" in p:
                    name = p["name"].strip()
                elif "person" in p:
                    name = p["person"].strip()
                # 处理格式问题，如name字段值包含冒号的情况
                if name and name.startswith(":"):
                    name = name[1:].strip()
            elif isinstance(p, str):
                # 处理字符串数组
                name = p.strip()
                # 处理字符串中包含字典结构的情况
                if name.startswith("{") and name.endswith("}"):
                    try:
                        p_dict = json.loads(name)
                        if "participant_name" in p_dict:
                            name = p_dict["participant_name"].strip()
                        elif "name" in p_dict:
                            name = p_dict["name"].strip()
                        elif "person" in p_dict:
                            name = p_dict["person"].strip()
                        # 处理格式问题，如name字段值包含冒号的情况
                        if name and name.startswith(":"):
                            name = name[1:].strip()
                    except:
                        pass  # 解析失败则保留原始字符串
            # 过滤掉明显不是人名的字符串
            if name:
                # 排除包含时间、地点、主题等关键词的字符串
                invalid_keywords = ["讨论", "今天", "下午", "上午", "时间", "地点", "会议室", "项目", "进度", "主题", "议程", "参与人员", "参会人员", "主持人"]
                if not any(keyword in name for keyword in invalid_keywords):
                    fixed_participants.append(name)
        # 确保主持人也在参与者列表中
        host = complete_result.get("host", "")
        if host and host not in fixed_participants:
            fixed_participants.append(host)
        
        # 如果过滤后没有参与者，使用模拟数据填充
        if not fixed_participants:
            fixed_participants = self._get_mock_data(text).get("participants", [])
        
        complete_result["participants"] = fixed_participants
        complete_result["participant_count"] = len(fixed_participants)
        
        print(f"完整的解析结果: {complete_result}")
        return complete_result
    
    def _get_mock_data(self, text: str) -> Dict[str, Any]:
        """获取模拟数据（用于演示）"""
        # 根据输入文本生成个性化的模拟数据
        import re
        
        # 从输入文本中提取可能的会议主题
        theme_match = re.search(r'主题[:：]?\s*([^\n]+)', text) or re.search(r'会议[:：]?\s*([^\n]+)', text)
        meeting_theme = theme_match.group(1).strip() if theme_match else "会议讨论"
        
        # 从输入文本中提取可能的时间
        time_match = re.search(r'时间[:：]?\s*([^\n]+)', text) or re.search(r'(\d{4}-\d{2}-\d{2}.*?)|(\d{1,2}月\d{1,2}日.*?)|(下[周月]\w+.*?)', text)
        if time_match:
            # 如果有捕获组内容（比如"时间：今天下午3点"中的"今天下午3点"）
            if time_match.group(1):
                meeting_time = time_match.group(1).strip()
            elif time_match.group(2):
                meeting_time = time_match.group(2).strip()
            elif time_match.group(3):
                meeting_time = time_match.group(3).strip()
            else:
                # 否则直接使用匹配的整个内容
                meeting_time = time_match.group(0).strip()
        else:
            meeting_time = "待定"
        
        # 从输入文本中提取可能的地点
        location_match = re.search(r'地点[:：]?\s*([^\n]+)', text) or re.search(r'(会议室\d+|办公室|线上会议)', text)
        if location_match:
            # 如果有捕获组内容（比如"地点：会议室A"中的"会议室A"）
            if location_match.group(1):
                meeting_location = location_match.group(1).strip()
            else:
                # 否则直接使用匹配的整个内容
                meeting_location = location_match.group(0).strip()
        else:
            meeting_location = "公司会议室"
        
        # 从输入文本中提取可能的参会人员
        participants_match = re.search(r'参会人员[:：]?\s*([^\n]+)', text)
        participants = []
        if participants_match:
            participants_str = participants_match.group(1).strip()
            # 移除前缀常见词如"包括"、"有"、"为"、"以及"
            participants_str = re.sub(r'^(包括|有|为|以及)\s*', '', participants_str)
            # 支持顿号、逗号、中文逗号、"和"、"以及"分隔，并且去掉可能的空格
            participants_str = participants_str.replace('，', '、').replace(',', '、').replace('和', '、').replace('以及', '、')
            participants = [p.strip() for p in participants_str.split('、') if p.strip()]
        
        # 如果没有提取到参会人员，尝试匹配所有可能的人名
        if not participants:
            # 改进的人名匹配正则表达式，支持更多分隔符
            name_pattern = r'[\u4e00-\u9fa5]{2,4}(?:[、,，和以及][\u4e00-\u9fa5]{2,4})*'
            name_matches = re.findall(name_pattern, text)
            if name_matches:
                # 合并所有匹配到的人名并处理多种分隔符
                all_names = []
                for match in name_matches:
                    # 处理多种分隔符
                    separated_names = re.split(r'[、,，和以及]', match)
                    all_names.extend([p.strip() for p in separated_names if p.strip()])
                # 去重
                participants = list(set(all_names))
        
        # 如果还是没有提取到，使用默认值
        if not participants:
            participants = ["参会人员1", "参会人员2"]
        
        # 从输入文本中提取可能的议程
        agenda_items = []
        agenda_matches = re.findall(r'议[题程][:：]?\s*([^\n]+)', text)
        if agenda_matches:
            for topic in agenda_matches:
                agenda_items.append({
                    "topic": topic.strip(),
                    "responsible_person": participants[0] if participants else "负责人",
                    "preparation": "准备相关资料",
                    "notes": ""
                })
        
        # 如果没有提取到议程，使用默认值
        if not agenda_items:
            agenda_match = re.search(r'(讨论|议题|事项)[:：]?\s*([^\n]+)', text)
            agenda_topic = agenda_match.group(0).strip() if agenda_match else "会议议程"
            agenda_items.append({
                "topic": agenda_topic,
                "responsible_person": participants[0] if participants else "负责人",
                "preparation": "准备相关资料",
                "notes": ""
            })
        
        # 提取会议内容
        content_pattern = r'会议内容[:：]?\s*([\s\S]*)'
        content_match = re.search(content_pattern, text)
        if content_match:
            meeting_content = content_match.group(1).strip()
        else:
            # 如果没有明确的内容部分，使用整个文本
            meeting_content = text.strip()
        
        # 将 agenda_items 转换为符合模板要求的 topics 格式
        topics = []
        for item in agenda_items:
            topic_dict = {
                "title": item["topic"],
                "leader": item["responsible_person"],
                "preparation": item["preparation"]
            }
            topics.append(topic_dict)

        # 尝试提取会前准备事项
        pre_meeting_preparations = ""
        pre_match = re.search(r'会前准备事项[:：]?\s*([^\n]+)', text)
        if pre_match:
            pre_meeting_preparations = pre_match.group(1).strip()
        elif "提前准备" in text:
            pre_meeting_preparations = "提前准备相关资料"

        # 计算会议时长
        duration = "约1小时"
        duration_match = re.search(r'时长[:：]?\s*([^\n]+)', text) or re.search(r'约(\d+小时)', text)
        if duration_match:
            duration = duration_match.group(1).strip() if duration_match.group(1) else duration_match.group(0).strip()

        mock_data = {
            "meeting_topic": meeting_theme,
            "meeting_time": meeting_time,
            "meeting_location": meeting_location,
            "host": participants[0] if participants else "主持人",
            "participants": participants,
            "participant_count": len(participants),
            "meeting_duration": duration,
            "topics": topics,
            "pre_meeting_preparations": pre_meeting_preparations
        }
        return mock_data