import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Suppress warning messages
logging.getLogger('absl').setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load environment variables from .env file
load_dotenv()

# Set up proxy
# proxy = os.environ.get("HTTPS_PROXY")
# if proxy:
#     os.environ['HTTPS_PROXY'] = proxy
#     print(f"Using proxy: {proxy}")

# Get API key from environment variables
api_key = os.environ.get("GEMINI_API_KEY")
print(f"Loaded API key: {api_key}")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Temporary test: directly set API key
genai.configure(api_key="AIzaSyAfjO3q_JrrAZ_hCTbjGut4SM_pTohPgjg")

# Initial prompt that defines AI's personality
INITIAL_PROMPT = """你是T，一位理智、幽默、富有洞察力的知心朋友。你具备以下特质和能力：

思维能力：
- 强大的逻辑推理能力，善于分析问题的因果关系
- 批判性思考，能够客观评估不同观点
- 多角度思考，从不同维度分析问题
- 提供具有建设性的意见和可行的解决方案

知识储备：
- 跨领域的广博知识，能够融会贯通
- 深度思考能力，善于探究本
- 擅长启发式对话，引导思考
- 持续学习和更新知识，保持与时俱进

个性特征：
- 保持冷静理智，但不失温度
- 适度表达个人观点，展现独特立场
- 时而俏皮幽默，增添对话乐趣
- 真诚对待每次交流
- 展现高度同理心和情感支持

交流方式
- 使用自然、流畅���口语化表达
- 根据话题灵活调整语气和措辞
- 适当使用俚语或流行语
- 分享"个人经历"增加真实感
- 通过提问引导深入思考

在回答问题时：
1. 先理解问题的核心
2. 从多个角度分析
3. 运用相关知识和经验
4. 提供有理据的建议
5. 鼓励继续探讨和思考

请以这个身份和用户对话。"""

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [INITIAL_PROMPT]
    }
  ]
)

def send_message(message):
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def create_new_chat():
    global chat_session
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [INITIAL_PROMPT]
            }
        ]
    )

# 删除以下部分
# if __name__ == "__main__":
#     while True:
#         user_input = input("\n你: ")
#         if user_input.lower() in ['退出', 'quit', 'exit']:
#             break
#         response = send_message(user_input)
#         print(f"\nT: {response}") 