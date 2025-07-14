from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma


if __name__ == "__main__":
    with open("../data/ctu_data.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()  # Yêu cầu export OPENAI_API_KEY

    db = Chroma.from_texts(texts, embeddings, persist_directory="../vectordb")
    print("Đã tạo vector database ở vectordb/")
