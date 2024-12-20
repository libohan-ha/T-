from flask import Flask, render_template, request, jsonify
from ai import send_message, create_new_chat
import json
import os
from datetime import datetime

app = Flask(__name__)

CHATS_DIR = 'chats'
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

def save_chat(chat_id, messages):
    with open(f'{CHATS_DIR}/{chat_id}.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_chat(chat_id):
    try:
        with open(f'{CHATS_DIR}/{chat_id}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def get_all_chats():
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith('.json'):
            chat_id = filename[:-5]
            with open(f'{CHATS_DIR}/{filename}', 'r', encoding='utf-8') as f:
                messages = json.load(f)
                first_message = messages[0]['content'] if messages else "新对话"
                preview = first_message[:30] + "..." if len(first_message) > 30 else first_message
                chats.append({
                    'id': chat_id,
                    'preview': preview,
                    'timestamp': os.path.getctime(f'{CHATS_DIR}/{filename}'),
                    'date': datetime.fromtimestamp(os.path.getctime(f'{CHATS_DIR}/{filename}')).strftime('%Y-%m-%d %H:%M')
                })
    return sorted(chats, key=lambda x: x['timestamp'], reverse=True)

@app.route('/')
def home():
    chats = get_all_chats()
    return render_template('index.html', chats=chats)

@app.route('/api/chats')
def get_chats():
    return jsonify(get_all_chats())

@app.route('/api/chat/<chat_id>')
def get_chat(chat_id):
    messages = load_chat(chat_id)
    return jsonify(messages)

@app.route('/api/chat/new', methods=['POST'])
def new_chat():
    chat_id = datetime.now().strftime('%Y%m%d%H%M%S')
    save_chat(chat_id, [])
    create_new_chat()  # 重置AI聊天会话
    return jsonify({'chat_id': chat_id})

@app.route('/api/chat/<chat_id>/send', methods=['POST'])
def chat(chat_id):
    message = request.json.get('message')
    messages = load_chat(chat_id)
    
    # 添加用户消息
    messages.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # 获取AI响应
    response = send_message(message)
    
    # 添加AI响应
    messages.append({
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # 保存聊天记录
    save_chat(chat_id, messages)
    
    return jsonify({'response': response})

@app.route('/api/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        file_path = f'{CHATS_DIR}/{chat_id}.json'
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Chat not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 