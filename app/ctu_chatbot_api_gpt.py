from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 1. Nạp biến môi trường từ file .env (nếu có)
load_dotenv()  # OPENAI_API_KEY sẽ tự được nạp vào os.environ

from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# 2. Khởi tạo các thành phần RAG
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="../vectordb", embedding_function=embeddings)
llm = OpenAI(temperature=0)
qa = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

def ask_ctu(question):
    # Sử dụng .invoke chuẩn mới, tránh deprecated warning!
    return qa.invoke({"query": question})["result"]

# 3. Flask app
app = Flask(__name__)
CORS(app)  # Bật CORS cho phép gọi API từ mọi website

@app.route("/", methods=["GET"])
def index():
    return "CTU Chatbot API is running.<br>Sử dụng POST /chat để hỏi trợ lý AI Đại học Cần Thơ."

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Lấy message, kiểm tra input hợp lệ
        question = request.json.get('message', '').strip()
        if not question:
            return jsonify({"answer": "Vui lòng nhập câu hỏi!"})
        print(f"User hỏi: {question}")  # Log giúp debug
        answer = ask_ctu(question)
        return jsonify({"answer": answer})
    except Exception as e:
        print("Lỗi trong quá trình xử lý câu hỏi:", e)
        return jsonify({"answer": "Xin lỗi, hệ thống lỗi!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

