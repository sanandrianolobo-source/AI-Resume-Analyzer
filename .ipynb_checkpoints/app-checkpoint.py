import streamlit as st
import requests

st.set_page_config(page_title="Smart ATS Dashboard", layout="wide", page_icon="🚀")
st.title("🚀 Enterprise CV Ranking System")

# Daftar kategori (Hardcoded karena Frontend tidak lagi menyimpan model AI)
DAFTAR_KATEGORI = [
    "ACCOUNTANT", "ADVOCATE", "AGRICULTURE", "APPAREL", "ARTS",
    "AUTOMOBILE", "AVIATION", "BANKING", "BPO", "BUSINESS-DEVELOPMENT",
    "CHEF", "CONSTRUCTION", "CONSULTANT", "DESIGNER", "DIGITAL-MEDIA",
    "ENGINEERING", "FINANCE", "FITNESS", "HEALTHCARE", "HR",
    "INFORMATION-TECHNOLOGY", "PUBLIC-RELATIONS", "SALES", "TEACHER"
]

with st.sidebar:
    st.header("⚙️ Konfigurasi Lowongan")
    is_new_role = st.checkbox("Bypass Filter")
    if is_new_role:
        posisi_dicari = st.text_input("Nama Posisi Baru")
    else:
        posisi_dicari = st.selectbox("Pilih Kategori Posisi", DAFTAR_KATEGORI)
    job_description = st.text_area("Job Description Lengkap", height=200)

uploaded_files = st.file_uploader("Upload CV (Format PDF)", accept_multiple_files=True, type=['pdf'])

if st.button("Proses Kandidat", type="primary"):
    if not uploaded_files or not job_description:
        st.warning("Mohon unggah CV dan isi Job Description!")
    else:
        st.info("📡 Mengirim dokumen ke Mesin API (Backend)...")
        
        kandidat_lolos = []
        kandidat_ditolak = []
        
        # Alamat API kita (sesuai dengan terminal Anda)
        API_URL = "http://127.0.0.1:8000/analyze"
        
        # Buka progress bar
        my_bar = st.progress(0, text="Menyiapkan data...")
        
        for i, file in enumerate(uploaded_files):
            my_bar.progress((i + 1) / len(uploaded_files), text=f"Menganalisis {file.name}...")
            
            # Bungkus file dan form untuk dikirim lewat internet (lokal)
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            data = {
                "job_description": job_description,
                "posisi_dicari": posisi_dicari,
                "is_new_role": str(is_new_role).lower()
            }
            
            try:
                # Tembak API
                response = requests.post(API_URL, files=files, data=data)
                
                if response.status_code == 200:
                    hasil = response.json()
                    kategori = hasil["kategori_terdeteksi"]
                    lolos = hasil["lolos_filter_kategori"]
                    skor = hasil["skor_relevansi"]
                    
                    if lolos and skor >= 30.0:
                        kandidat_lolos.append({
                            "Nama File": file.name, 
                            "Kategori": kategori,
                            "Skor Relevansi": skor
                        })
                    elif lolos and skor < 30.0:
                        kandidat_ditolak.append({
                            "Nama File": file.name, 
                            "Kategori Terdeteksi": f"{kategori} (Skor Relevansi Terlalu Rendah: {skor})"
                        })
                    else:
                        kandidat_ditolak.append({
                            "Nama File": file.name, 
                            "Kategori Terdeteksi": kategori
                        })
                else:
                    st.error(f"Gagal memproses {file.name}: Terjadi kesalahan di server API.")
            
            except Exception as e:
                st.error("❌ Koneksi ke API terputus! Pastikan terminal API (FastAPI) sedang menyala.")
                break
                
        my_bar.empty()
        
        st.success("Pemrosesan Selesai!")
        tab1, tab2 = st.tabs(["🟢 Kandidat Direkomendasikan", "🔴 Out of Scope"])
        
        with tab1:
            if kandidat_lolos:
                st.dataframe(sorted(kandidat_lolos, key=lambda x: x['Skor Relevansi'], reverse=True), use_container_width=True)
        with tab2:
            if kandidat_ditolak:
                st.dataframe(kandidat_ditolak, use_container_width=True)