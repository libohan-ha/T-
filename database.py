from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 获取 MongoDB 连接字符串
MONGODB_URI = os.getenv('MONGODB_URI')

# 创建 MongoDB 客户端
client = MongoClient(MONGODB_URI)
db = client.chatbot  # 数据库名称
chats = db.chats     # 集合名称

def save_chat(chat_id, messages):
    """保存聊天记录"""
    chat_data = {
        'chat_id': chat_id,
        'messages': messages,
        'updated_at': datetime.now()
    }
    chats.update_one(
        {'chat_id': chat_id}, 
        {'$set': chat_data}, 
        upsert=True
    )

def load_chat(chat_id):
    """加载聊天记录"""
    chat = chats.find_one({'chat_id': chat_id})
    return chat['messages'] if chat else []

def get_all_chats():
    """获取所有聊天记录"""
    all_chats = []
    for chat in chats.find().sort('updated_at', -1):
        first_message = chat['messages'][0]['content'] if chat['messages'] else "新对话"
        preview = first_message[:30] + "..." if len(first_message) > 30 else first_message
        all_chats.append({
            'id': chat['chat_id'],
            'preview': preview,
            'timestamp': chat['updated_at'].timestamp(),
            'date': chat['updated_at'].strftime('%Y-%m-%d %H:%M')
        })
    return all_chats

def delete_chat(chat_id):
    """删除聊天记录"""
    result = chats.delete_one({'chat_id': chat_id})
    return result.deleted_count > 0 