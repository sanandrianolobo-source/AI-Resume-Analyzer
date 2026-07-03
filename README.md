# 🚀 Enterprise Smart ATS (AI Resume Analyzer)

Aplikasi *Applicant Tracking System* (ATS) cerdas berskala *Enterprise* yang dirancang untuk mengotomatisasi proses *screening* CV menggunakan kecerdasan buatan (AI) dan Natural Language Processing (NLP).

## 🌟 Fitur Utama
- **AI-Powered Classification:** Menggunakan model Deep Learning (LSTM) yang telah di-tuning untuk mengklasifikasikan kategori profesi dari CV secara otomatis.
- **AI Semantic Scoring (NLP):** Memanfaatkan Kecerdasan Buatan (*Sentence Transformers*) untuk memahami konteks bahasa dan menghitung persentase kecocokan (skor relevansi) antara CV dan *Job Description*, melampaui batasan pencocokan *keyword* tradisional.
- **Enterprise Architecture:** Dibangun dengan arsitektur *Microservice* yang memisahkan antarmuka pengguna (Streamlit) dan mesin pemroses AI (FastAPI).
- **Automated Database:** Menyimpan riwayat CV kandidat dan metrik keputusan AI secara otomatis menggunakan SQLite & SQLAlchemy.
- **CI/CD Pipeline:** Terintegrasi dengan GitHub Actions untuk otomatisasi pengujian sistem (*Continuous Integration*).

## 🛠️ Teknologi yang Digunakan
- **Frontend:** Streamlit
- **Backend:** FastAPI, Uvicorn
- **AI/ML:** TensorFlow (Keras), SentenceTransformers, NumPy, pdfplumber
- **Database:** SQLite, SQLAlchemy
- **DevOps:** GitHub Actions, Git

## 📂 Struktur Arsitektur
- `app.py`: *Client-side application* (Antarmuka pengguna interaktif).
- `api.py`: *Server-side application* (Mesin pemroses AI dan jembatan database).
- `ats_database.db`: Penyimpanan riwayat analitik lokal.

## 👨‍💻 Tentang Proyek
Proyek ini dikembangkan sebagai implementasi nyata pemanfaatan AI dalam mengoptimalkan dan mengotomatisasi alur kerja rekrutmen di dunia industri (HR Tech).
