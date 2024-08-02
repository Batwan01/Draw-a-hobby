from flask import Flask, request, render_template, send_from_directory
from openai import OpenAI
import os

# OpenAI API 키 설정
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API 키를 설정해주세요. 환경 변수 'OPENAI_API_KEY'가 필요합니다.")

# OpenAI 클라이언트 인스턴스 생성
client = OpenAI(api_key=api_key)

# Flask 애플리케이션 생성
app = Flask(__name__)

# 대화 저장소
messages = []
user_responses = {
    "activity": "",
    "age": "",
    "location": "",
    "companions": "",
    "season": ""
}

@app.route('/', methods=['GET', 'POST'])
def index():
    global messages, user_responses
    image_url = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        messages.append({'sender': 'chat-user', 'text': user_input})

        if len(messages) == 2:
            user_responses["activity"] = user_input
            messages.append({'sender': 'chat-bot', 'text': questions[1]})
        elif len(messages) == 4:
            user_responses["age"] = user_input
            messages.append({'sender': 'chat-bot', 'text': questions[2]})
        elif len(messages) == 6:
            user_responses["location"] = user_input
            messages.append({'sender': 'chat-bot', 'text': questions[3]})
        elif len(messages) == 8:
            user_responses["companions"] = user_input
            messages.append({'sender': 'chat-bot', 'text': questions[4]})
        elif len(messages) == 10:
            user_responses["season"] = user_input
            messages.append({'sender': 'chat-bot', 'text': "설명 고마워요!! 조금만 기다려 주세요!"})

            prompt = f"A {user_responses['age']} year old having fun doing {user_responses['activity']} at a {user_responses['location']} during {user_responses['season']} with {'friends' if '친구' in user_responses['companions'] else 'alone'}."
            
            # OpenAI API 호출
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            # response['data'][0]['url']을 사용하여 이미지 URL 추출
            image_url = response.data[0].url
            messages.append({'sender': 'chat-bot', 'text': "이미지가 생성되었습니다!"})
    
    if len(messages) == 0:
        messages.append({'sender': 'chat-bot', 'text': questions[0]})
    
    return render_template('index.html', messages=messages, image_url=image_url)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 챗봇 질문 리스트
questions = [
    "안녕하세요! 과거의 추억, 취미를 말해주세요!",
    "정말 멋져요! 그때의 기억을 구체적으로 설명해 줄 수 있어요? 몇 살이었어요?",
    "고마워요! 어디에서 취미를 즐겼나요?",
    "재미있었겠네요!! 혼자 있었나요?",
    "계절은 언제였나요?",
    "설명 고마워요!! 조금만 기다려 주세요!"
]

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)