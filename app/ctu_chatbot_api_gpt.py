from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import re
import openai

# Load biến môi trường
load_dotenv()

from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# Khởi tạo RAG
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="../vectordb", embedding_function=embeddings)
llm = OpenAI(temperature=0)
qa = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

# Hàm lấy thời tiết từ OpenWeatherMap
def get_weather(city):
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        return "Chưa cấu hình API key cho thời tiết."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=vi"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("cod") != 200:
            return f"Xin lỗi, không tìm thấy thông tin thời tiết cho {city}."
        weather = data['weather'][0]['description'].capitalize()
        temp = data['main']['temp']
        feels = data['main'].get('feels_like', '')
        hum = data['main'].get('humidity', '')
        return f"Thời tiết {city} hôm nay: {weather}, nhiệt độ {temp}°C, cảm giác như {feels}°C, độ ẩm {hum}%."
    except Exception as e:
        print("Lỗi lấy thời tiết:", e)
        return "Xin lỗi, không thể truy cập dữ liệu thời tiết lúc này."

# Fallback GPT-4o (OpenAI chuẩn mới)
def ask_gpt(question):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

def is_noanswer(text):
    if not text or not text.strip():
        return True
    text_lower = text.strip().lower()
    keywords = [
        "không biết", "không rõ", "xin lỗi", "tôi không chắc", "không đủ thông tin",
        "i don't know", "sorry", "i am not sure", "i do not have enough information",
        "i have no information", "not sure", "cannot answer", "don't have information",
        "tôi không có thông tin", "tôi không thể trả lời", "tôi không chắc chắn"
    ]
    if len(text_lower) < 10:
        return True
    for kw in keywords:
        if kw in text_lower:
            return True
    return False

def ask_ctu(question):
    # Nhận diện câu hỏi thời tiết
    q_lower = question.lower()
    if "thời tiết" in q_lower:
        city_match = re.search(r"thời tiết (.+?) hôm nay", q_lower)
        if city_match:
            city = city_match.group(1).strip().title()
            return get_weather(city)
        else:
            return "Bạn muốn hỏi thời tiết ở tỉnh/thành nào hôm nay?"

    # RAG nội bộ
    result = qa.invoke({"query": question})["result"]
    print("Kết quả từ RetrievalQA:", repr(result))
    if is_noanswer(result):
        print("==> Không tìm thấy câu trả lời nội bộ, chuyển qua GPT-4o.")
        gpt_result = ask_gpt(question)
        return f"(Nguồn ChatGPT - Internet)\n{gpt_result}"
    else:
        return f"(Nguồn nội bộ CTU)\n{result}"

# Flask app
app = Flask(__name__)
CORS(app)

# Route cho trang chủ, GET sẽ không còn lỗi 404
@app.route("/", methods=["GET"])
def home():
    return (
        "<h2>CTU Chatbot API is running.</h2>"
        "<p>Sử dụng <b>POST /chat</b> để hỏi trợ lý AI Đại học Cần Thơ.<br>"
        "Ví dụ curl: <code>curl -X POST https://ctuchatbot.onrender.com/chat -H 'Content-Type: application/json' -d '{\"message\": \"Đại học Cần Thơ ở đâu?\"}'</code></p>"
    )

@app.route('/chat', methods=['POST'])
def chat():
    try:
        question = request.json['message']
        answer = ask_ctu(question)
        return jsonify({"answer": answer})
    except Exception as e:
        import traceback
        print("Lỗi:", e)
        traceback.print_exc()
        return jsonify({"answer": "Xin lỗi, hệ thống lỗi!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
