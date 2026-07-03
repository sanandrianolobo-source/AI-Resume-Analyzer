from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
import numpy as np
import pdfplumber
import pickle
import re
import io
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sentence_transformers import SentenceTransformer, util

# --- DATABASE SETUP (SQLAlchemy) ---
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Mengunci path secara absolut ke folder tempat api.py berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "ats_database.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Skema Tabel Database
class Candidate(Base):
    __tablename__ = "candidates_history"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    job_applied = Column(String)
    detected_category = Column(String)
    similarity_score = Column(Float)
    is_recommended = Column(Boolean)

# Buat file database & tabel secara otomatis
Base.metadata.create_all(bind=engine)
# -----------------------------------

app = FastAPI(title="Smart ATS API Endpoint")

# Variabel Global untuk menyimpan Model di RAM
lstm_model = None
tokenizer = None
label_encoder = None
sbert_model = None

@app.on_event("startup")
def load_models():
    global lstm_model, tokenizer, label_encoder, sbert_model
    print("Memuat Model AI ke dalam memori Server...")
    lstm_model = load_model('model_cv_lstm_tuned.keras')
    with open('tokenizer_cv.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    with open('label_encoder_cv.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    sbert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("✅ Semua Model Siap Beroperasi & Database Terkunci Absolut!")

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.post("/analyze")
async def analyze_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    posisi_dicari: str = Form(...),
    is_new_role: bool = Form(False)
):
    # 1. Baca PDF
    content = await file.read()
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text(layout=True) or ""
    
    teks_cv = clean_text(text)
    
    # 2. Proses Klasifikasi
    lolos_filter = False
    kategori_tebakan = "Uncategorized"
    
    if is_new_role:
        lolos_filter = True
        kategori_tebakan = "Bypass"
    else:
        seq = tokenizer.texts_to_sequences([teks_cv])
        padded = pad_sequences(seq, maxlen=800, padding='post', truncating='post')
        prediksi = lstm_model.predict(padded, verbose=0)
        top_3_indices = np.argsort(prediksi[0])[-3:]
        top_3_labels = [label_encoder.classes_[i] for i in top_3_indices]
        
        if posisi_dicari in top_3_labels:
            kategori_tebakan = posisi_dicari
            lolos_filter = True
        else:
            kategori_tebakan = label_encoder.inverse_transform([np.argmax(prediksi)])[0]
    
    # 3. Proses Skoring Kemiripan
    skor_kemiripan = 0.0
    if lolos_filter:
        vektor_jd = sbert_model.encode(job_description)
        vektor_cv = sbert_model.encode(teks_cv)
        skor_kemiripan = util.cos_sim(vektor_jd, vektor_cv).item() * 100
        
    status_rekomendasi = bool(lolos_filter and skor_kemiripan >= 30.0)

    # 4. Simpan ke Database
    db = SessionLocal()
    try:
        db_candidate = Candidate(
            filename=file.filename,
            job_applied=posisi_dicari if not is_new_role else "New Role",
            detected_category=kategori_tebakan,
            similarity_score=round(skor_kemiripan, 2),
            is_recommended=status_rekomendasi
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
    finally:
        db.close() # Menjamin file database selalu dilepaskan setelah selesai

    # 5. Kembalikan Respon ke Streamlit UI
    return {
        "filename": file.filename,
        "kategori_terdeteksi": kategori_tebakan,
        "lolos_filter_kategori": lolos_filter,
        "skor_relevansi": round(skor_kemiripan, 2)
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)