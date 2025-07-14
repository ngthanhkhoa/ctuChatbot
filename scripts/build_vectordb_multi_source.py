import glob
from langchain_community.document_loaders import (
    PyPDFLoader, 
    UnstructuredPowerPointLoader, 
    UnstructuredWordDocumentLoader, 
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

all_documents = []

# Load PDF
for pdf_path in glob.glob("../data/*.pdf"):
    loader = PyPDFLoader(pdf_path)
    all_documents.extend(loader.load())

# Load PPTX
for pptx_path in glob.glob("../data/*.pptx"):
    loader = UnstructuredPowerPointLoader(pptx_path)
    all_documents.extend(loader.load())

# Load DOCX
for docx_path in glob.glob("../data/*.docx"):
    loader = UnstructuredWordDocumentLoader(docx_path)
    all_documents.extend(loader.load())

# Load TXT với fix encoding
def safe_load_text(file_path):
    for encoding in ["utf-8", "latin1", "windows-1252"]:
        try:
            loader = TextLoader(file_path, encoding=encoding)
            return loader.load()
        except Exception:
            continue
    print(f"Lỗi: Không đọc được file {file_path} với các encoding phổ biến!")
    return []

for txt_path in glob.glob("../data/*.txt"):
    all_documents.extend(safe_load_text(txt_path))

if not all_documents:
    print("Không có dữ liệu nào được load. Kiểm tra lại thư mục data/!")
    exit()

# Chunk và build vectordb
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
docs = text_splitter.split_documents(all_documents)
print(f"Tổng số đoạn chunk: {len(docs)}")

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="../vectordb", embedding_function=embeddings)

batch_size = 200
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    db.add_documents(batch)
    print(f"Đã thêm {i + len(batch)} / {len(docs)} chunk vào vectordb.")

print("Đã build xong vectordb từ PDF, PPTX, DOCX, TXT!")

