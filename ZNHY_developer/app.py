from flask import Flask, render_template, request, jsonify, send_file
import os
from utils.llm_parser import MeetingParser
from utils.word_generator import WordGenerator
import io

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_meeting_minutes():
    try:
        text_input = request.json.get('text', '')

        if not text_input:
            return jsonify({'error': '请输入会议内容'}), 400

        # 使用大模型解析会议内容
        parser = MeetingParser()
        meeting_data = parser.parse_meeting_text(text_input)

        # 生成Word文档
        generator = WordGenerator()
        doc_buffer = generator.generate_document(meeting_data)

        # 返回文件下载
        doc_buffer.seek(0)
        return send_file(
            doc_buffer,
            as_attachment=True,
            download_name='会议记录.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)