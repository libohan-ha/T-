from flask import Flask, render_template, request, jsonify
from ai import send_message, create_new_chat
from database import save_chat, load_chat, get_all_chats, delete_chat
import os
from datetime import datetime

app = Flask(__name__)

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
def delete_chat_route(chat_id):
    try:
        if delete_chat(chat_id):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Chat not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 