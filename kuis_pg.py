import streamlit as st
import pandas as pd
import os
import base64
import altair as alt

# 1. Konfigurasi Halaman (Harus Paling Atas)
st.set_page_config(page_title="Kuis Pilihan Ganda Ummuchodijah", layout="wide")

# 2. Fungsi Pemutar Audio Otomatis
def play_sound(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)

# 3. Custom CSS (Mode Gelap + Kotak Pilihan Ganda)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    
    /* Judul Utama */
    .big-title { font-size: 55px !important; font-weight: 900; text-align: center; color: #FFFFFF; text-shadow: 0px 0px 15px #4CAF50; margin-bottom: 20px; line-height: 1.2;}
    
    /* Header Kategori Kelas */
    .class-badge { background: linear-gradient(135deg, #4CAF50, #1B5E20); padding: 10px 30px; border-radius: 15px; color: #FFFFFF; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 20px; border: 2px solid #81C784;}
    
    /* Teks Pertanyaan */
    .question-number { text-align:center; font-size: 30px; font-weight: 900; color: #FFEB3B; margin-bottom: 10px; letter-spacing: 2px;}
    .question-text { font-size: 50px !important; text-align: center; font-weight: 800; color: #FFFFFF !important; line-height: 1.4; padding: 10px 20px 30px 20px;}
    .arabic-text { font-size: 70px !important; direction: rtl; text-align: center; font-family: 'Traditional Arabic', 'Amiri', serif; line-height: 1.8; color: #000000 !important; background-color: #F8F9FA; padding: 20px; border-radius: 20px; border: 4px solid #4CAF50; margin: 10px 0 30px 0;}
    
    /* --- KOTAK PILIHAN GANDA --- */
    .option-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 3px solid #81C784;
        border-radius: 15px;
        padding: 20px 30px;
        margin-bottom: 20px;
        font-size: 38px;
        font-weight: bold;
        color: #FFFFFF;
        text-align: left;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    /* Warna khusus untuk huruf A, B, C, D di dalam opsi */
    .option-letter { color: #FFEB3B; font-weight: 900; margin-right: 15px; }

    /* Notifikasi Benar/Salah */
    .status-benar { color: #4CAF50; font-size: 40px; text-align: center; font-weight: 900; margin-top: 20px; text-shadow: 0px 0px 10px rgba(76, 175, 80, 0.5);}
    .status-salah { color: #F44336; font-size: 40px; text-align: center; font-weight: 900; margin-top: 20px; text-shadow: 0px 0px 10px rgba(244, 67, 54, 0.5);}
    .kunci-jawaban { color: #81C784; font-size: 35px; font-weight: bold; text-align: center; margin-top: 10px;}
    
    /* Animasi Selebrasi Juara */
    @keyframes pulseGlow {
        0% { transform: scale(1); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
        50% { transform: scale(1.05); box-shadow: 0 0 50px rgba(255, 215, 0, 1); }
        100% { transform: scale(1); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
    }
    .winner-box { background: linear-gradient(135deg, #FFD700, #FF8C00); padding: 50px; border-radius: 30px; text-align: center; border: 5px solid #FFFFFF; animation: pulseGlow 1.5s infinite; margin: 40px 0; }
    .winner-title { font-size: 40px; color: #FFFFFF; font-weight: bold; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .winner-name { font-size: 80px; color: #FFFFFF; font-weight: 900; margin: 0; text-shadow: 3px 3px 0px #000, 5px 5px 15px rgba(0,0,0,0.5); letter-spacing: 3px; }
    </style>
    """, unsafe_allow_html=True)

# 4. DATABASE SOAL PILIHAN GANDA
# Format: "opsi" berisi 4 pilihan jawaban berurutan (A, B, C, D)
bank_soal = {
    "Fiqih (Wali Murid)": [
        {
            "tipe": "pg",
            "tanya": "Apabila terkena najis mughallazah (najis berat) seperti air liur anjing, bagaimana cara mensucikannya?",
            "opsi": ["Dibasuh air mengalir 3 kali", "Dibasuh air 7 kali, salah satunya dicampur tanah/debu", "Dicuci dengan sabun sampai hilang baunya", "Diusap dengan debu (tayammum)"],
            "jawab": "B. Dibasuh air 7 kali, salah satunya dicampur tanah/debu"
        },
        {
            "tipe": "pg",
            "tanya": "Berapakah takaran standar Zakat Fitrah yang wajib dikeluarkan untuk satu orang menurut mayoritas ulama di Indonesia?",
            "opsi": ["2,5 Kg atau 3,5 Liter beras", "3 Kg atau 4 Liter beras", "1,5 Kg beras", "Semaunya asalkan ikhlas"],
            "jawab": "A. 2,5 Kg atau 3,5 Liter beras"
        },
        {
            "tipe": "pg",
            "tanya": "Berikut ini adalah hari-hari yang diharamkan bagi umat Islam untuk berpuasa, kecuali...",
            "opsi": ["Hari Raya Idul Fitri", "Hari Raya Idul Adha", "Hari Tasyrik (11, 12, 13 Dzulhijjah)", "Hari Arafah (9 Dzulhijjah)"],
            "jawab": "D. Hari Arafah (9 Dzulhijjah)"
        },
        {
            "tipe": "pg",
            "tanya": "Apakah hukum dan sebutan bagi seseorang yang menggabungkan dua shalat fardu dalam satu waktu sekaligus meringkas jumlah rakaatnya (misal: Dzuhur dan Ashar masing-masing 2 rakaat)?",
            "opsi": ["Shalat Jamak", "Shalat Qashar", "Shalat Jamak Qashar", "Shalat Pengganti (Qadha)"],
            "jawab": "C. Shalat Jamak Qashar"
        },
        {
            "tipe": "pg",
            "tanya": "Batasan aurat bagi perempuan muslimah yang wajib ditutupi saat shalat maupun di luar rumah adalah...",
            "opsi": ["Seluruh tubuh kecuali wajah dan telapak tangan", "Dari pusar sampai lutut", "Seluruh tubuh tanpa terkecuali", "Seluruh tubuh kecuali rambut dan telapak tangan"],
            "jawab": "A. Seluruh tubuh kecuali wajah dan telapak tangan"
        },
        {
            "tipe": "pg",
            "tanya": "Apabila seseorang lupa jumlah rakaat atau lupa melakukan tahiyat awal dalam shalatnya, apa yang disunnahkan untuk dilakukan sebelum salam?",
            "opsi": ["Mengulang shalat dari awal", "Membaca istighfar 3 kali", "Sujud Tilawah", "Sujud Sahwi"],
            "jawab": "D. Sujud Sahwi"
        },
        {
            "tipe": "pg",
            "tanya": "Syarat sahnya shalat ada beberapa macam. Manakah di bawah ini yang BUKAN termasuk syarat sah shalat?",
            "opsi": ["Suci dari hadas besar dan kecil", "Menghadap kiblat", "Membaca doa qunut", "Menutup aurat"],
            "jawab": "C. Membaca doa qunut"
        },
        {
            "tipe": "pg",
            "tanya": "Seseorang diperbolehkan melakukan Tayammum sebagai pengganti wudu apabila...",
            "opsi": ["Sedang malas terkena air", "Tidak ada air atau sedang sakit yang melarang terkena air", "Hanya untuk shalat sunnah", "Waktu shalat sudah hampir habis"],
            "jawab": "B. Tidak ada air atau sedang sakit yang melarang terkena air"
        },
        {
            "tipe": "pg",
            "tanya": "Berikut ini adalah hal-hal yang mewajibkan seseorang untuk mandi wajib (mandi besar), kecuali...",
            "opsi": ["Keluarnya darah haid", "Selesai masa nifas", "Menyentuh lawan jenis yang bukan mahram", "Keluarnya mani / Junub"],
            "jawab": "C. Menyentuh lawan jenis yang bukan mahram"
        },
        {
            "tipe": "pg",
            "tanya": "Dalam wudu, hal-hal yang wajib dilakukan (Rukun Wudu) ada 6. Manakah urutan yang benar?",
            "opsi": ["Niat, cuci muka, cuci tangan, usap kepala, cuci kaki, tertib", "Niat, kumur, cuci hidung, cuci muka, cuci kaki", "Cuci muka, niat, cuci tangan, telinga, kaki", "Kumur, cuci muka, usap kepala, telinga, tertib"],
            "jawab": "A. Niat, cuci muka, cuci tangan, usap kepala, cuci kaki, tertib"
        }
    ],
    "Tauhid (Wali Murid)": [
        {
            "tipe": "pg",
            "tanya": "Inti dari ajaran Tauhid dalam agama Islam adalah...",
            "opsi": ["Meyakini adanya surga dan neraka", "Mengesakan Allah SWT dan tidak menyekutukan-Nya", "Menghafal sifat-sifat wajib Allah", "Percaya kepada Rasulullah"],
            "jawab": "B. Mengesakan Allah SWT dan tidak menyekutukan-Nya"
        },
        {
            "tipe": "pg",
            "tanya": "Dosa terbesar yang tidak akan diampuni oleh Allah SWT jika pelakunya meninggal sebelum bertaubat adalah...",
            "opsi": ["Membunuh", "Durhaka kepada orang tua", "Syirik (Menyekutukan Allah)", "Meninggalkan shalat"],
            "jawab": "C. Syirik (Menyekutukan Allah)"
        },
        {
            "tipe": "pg",
            "tanya": "Sifat wajib bagi Allah adalah 'Baqa' yang artinya kekal abadi. Maka kebalikan dari sifat tersebut (Sifat Mustahil) adalah...",
            "opsi": ["Adam (Tidak ada)", "Huduts (Baru)", "Fana (Binasa / Rusak)", "Jahlun (Bodoh)"],
            "jawab": "C. Fana (Binasa / Rusak)"
        },
        {
            "tipe": "pg",
            "tanya": "Iman kepada Qada dan Qadar berarti meyakini bahwa...",
            "opsi": ["Segala keburukan datang dari setan", "Nasib manusia ditentukan oleh usahanya sendiri", "Segala sesuatu yang terjadi di alam semesta telah ditetapkan oleh Allah SWT", "Allah hanya menetapkan takdir yang baik-baik saja"],
            "jawab": "C. Segala sesuatu yang terjadi di alam semesta telah ditetapkan oleh Allah SWT"
        },
        {
            "tipe": "pg",
            "tanya": "Malaikat yang ditugaskan oleh Allah SWT untuk mencatat amal baik dan amal buruk manusia secara berturut-turut adalah...",
            "opsi": ["Jibril dan Mikail", "Munkar dan Nakir", "Raqib dan Atid", "Malik dan Ridwan"],
            "jawab": "C. Raqib dan Atid"
        },
        {
            "tipe": "pg",
            "tanya": "Dalam hadits Jibril, beribadah kepada Allah seolah-olah kita melihat-Nya, atau jika tidak bisa melihat-Nya maka yakinlah bahwa Allah melihat kita, disebut dengan sikap...",
            "opsi": ["Iman", "Islam", "Ihsan", "Tawakkal"],
            "jawab": "C. Ihsan"
        },
        {
            "tipe": "pg",
            "tanya": "Salah satu Asmaul Husna adalah 'Ar-Rahman' dan 'Ar-Rahim'. Apa perbedaan mendasarnya?",
            "opsi": ["Ar-Rahman untuk dunia, Ar-Rahim untuk akhirat", "Ar-Rahman pengasih untuk semua makhluk, Ar-Rahim penyayang khusus untuk orang mukmin", "Keduanya sama saja tidak ada bedanya", "Ar-Rahman untuk rezeki, Ar-Rahim untuk kesehatan"],
            "jawab": "B. Ar-Rahman pengasih untuk semua makhluk, Ar-Rahim penyayang khusus untuk orang mukmin"
        },
        {
            "tipe": "pg",
            "tanya": "Contoh dari Kiamat Sugra (Kiamat Kecil) yang sering terjadi di sekitar kita adalah...",
            "opsi": ["Matahari terbit dari barat", "Turunnya Nabi Isa AS", "Kematian seseorang dan bencana alam", "Keluarnya Dajjal"],
            "jawab": "C. Kematian seseorang dan bencana alam"
        },
        {
            "tipe": "pg",
            "tanya": "Rukun Iman yang ke-4 adalah beriman kepada...",
            "opsi": ["Malaikat-malaikat Allah", "Kitab-kitab Allah", "Rasul-rasul Allah", "Hari Kiamat"],
            "jawab": "C. Rasul-rasul Allah"
        },
        {
            "tipe": "pg",
            "tanya": "Kitab suci Al-Qur'an diturunkan kepada Nabi Muhammad SAW untuk menyempurnakan kitab-kitab sebelumnya, yaitu...",
            "opsi": ["Taurat, Zabur, dan Injil", "Taurat, Suhuf Ibrahim, dan Weda", "Zabur, Injil, dan Tripitaka", "Suhuf Musa dan Injil"],
            "jawab": "A. Taurat, Zabur, dan Injil"
        }
    ],
    "Tarikh (Wali Murid)": [
        {
            "tipe": "pg",
            "tanya": "Siapakah nama Ibunda dan Ayahanda dari baginda Nabi Muhammad SAW?",
            "opsi": ["Halimah dan Abdul Muthalib", "Aminah binti Wahab dan Abdullah bin Abdul Muthalib", "Khadijah dan Abu Thalib", "Fatimah dan Abdullah"],
            "jawab": "B. Aminah binti Wahab dan Abdullah bin Abdul Muthalib"
        },
        {
            "tipe": "pg",
            "tanya": "Nabi Muhammad SAW lahir di Kota Mekkah pada tanggal...",
            "opsi": ["10 Muharram Tahun Gajah", "17 Ramadhan Tahun Gajah", "12 Rabiul Awal Tahun Gajah", "1 Syawal Tahun Gajah"],
            "jawab": "C. 12 Rabiul Awal Tahun Gajah"
        },
        {
            "tipe": "pg",
            "tanya": "Tempat Nabi Muhammad SAW menerima wahyu pertama kali (Surat Al-Alaq 1-5) dari Malaikat Jibril adalah di...",
            "opsi": ["Gua Tsur", "Gua Hira", "Masjidil Haram", "Bukit Shafa"],
            "jawab": "B. Gua Hira"
        },
        {
            "tipe": "pg",
            "tanya": "Orang perempuan pertama yang mempercayai kenabian Rasulullah SAW dan masuk Islam (Assabiqunal Awwalun) adalah...",
            "opsi": ["Aisyah binti Abu Bakar", "Fatimah Az-Zahra", "Siti Khadijah", "Sumayyah binti Khayyat"],
            "jawab": "C. Siti Khadijah"
        },
        {
            "tipe": "pg",
            "tanya": "Gelar 'Al-Amin' disematkan oleh penduduk Mekkah kepada Nabi Muhammad SAW sejak beliau muda. Apa arti dari gelar tersebut?",
            "opsi": ["Orang yang cerdas", "Orang yang mulia", "Orang yang dapat dipercaya", "Orang yang pemberani"],
            "jawab": "C. Orang yang dapat dipercaya"
        },
        {
            "tipe": "pg",
            "tanya": "Peristiwa hijrahnya Nabi Muhammad SAW dari Mekkah menuju kota Yathrib menjadi titik awal kalender Hijriah. Kota Yathrib kemudian berganti nama menjadi...",
            "opsi": ["Thaif", "Madinah Al-Munawwarah", "Syam", "Jeddah"],
            "jawab": "B. Madinah Al-Munawwarah"
        },
        {
            "tipe": "pg",
            "tanya": "Tahun di mana istri tercinta Nabi (Khadijah) dan pamannya (Abu Thalib) wafat dikenal dalam sejarah Islam sebagai 'Amul Huzni', yang berarti...",
            "opsi": ["Tahun Kemenangan", "Tahun Kesedihan (Duka Cita)", "Tahun Perdamaian", "Tahun Ujian"],
            "jawab": "B. Tahun Kesedihan (Duka Cita)"
        },
        {
            "tipe": "pg",
            "tanya": "Perintah wajib shalat lima waktu sehari semalam diturunkan langsung kepada Nabi Muhammad SAW dalam peristiwa...",
            "opsi": ["Perang Badar", "Fathu Makkah (Pembebasan Mekkah)", "Isra' dan Mi'raj", "Turunnya Lailatul Qadar"],
            "jawab": "C. Isra' dan Mi'raj"
        },
        {
            "tipe": "pg",
            "tanya": "Setelah Nabi Muhammad SAW wafat, kepemimpinan umat Islam dilanjutkan oleh Khulafaur Rasyidin. Khalifah pertama adalah...",
            "opsi": ["Umar bin Khattab", "Ali bin Abi Thalib", "Utsman bin Affan", "Abu Bakar Ash-Shiddiq"],
            "jawab": "D. Abu Bakar Ash-Shiddiq"
        },
        {
            "tipe": "pg",
            "tanya": "Saat bayi, Nabi Muhammad SAW disusui dan diasuh di perkampungan Bani Sa'ad oleh seorang wanita bernama...",
            "opsi": ["Aminah", "Ummu Aiman", "Halimah As-Sa'diyah", "Tsuwaibah"],
            "jawab": "C. Halimah As-Sa'diyah"
        }
    ],
    "Babak Final": [
        {
            "tipe": "pg", 
            "tanya": "Berapakah jumlah huruf Halq (Idzhar Halqi)?", 
            "opsi": ["4 Huruf", "5 Huruf", "6 Huruf", "7 Huruf"], 
            "jawab": "C. 6 Huruf (Hamzah, Ha', Ha, Kha, 'Ain, Ghain)"
        },
        {
            "tipe": "pg", 
            "tanya": "Di antara para ulama, KH. Hasyim Asy'ari bergelar 'Hadratus Syeikh' yang artinya...", 
            "opsi": ["Maha Guru", "Pemimpin Umat", "Pahlawan Bangsa", "Kyai Sepuh"], 
            "jawab": "A. Maha Guru"
        }
    ]
}

# 5. INISIALISASI STATE
if 'scores' not in st.session_state: 
    st.session_state.scores = {
        "Wali Murid TK A": 0,
        "Wali Murid TK B": 0,
        "Wali Murid 1A": 0, 
        "Wali Murid 1B": 0, 
        "Wali Murid 2": 0, 
        "Wali Murid 3": 0, 
        "Wali Murid 4": 0, 
        "Wali Murid 5": 0, 
        "Wali Murid 6": 0
    }
if 'progress' not in st.session_state: st.session_state.progress = {kategori: 0 for kategori in bank_soal.keys()}
if 'view' not in st.session_state: st.session_state.view = "soal"
if 'status_jawaban' not in st.session_state: st.session_state.status_jawaban = None 
if 'show_winner' not in st.session_state: st.session_state.show_winner = False

# 6. PANEL JURI (SIDEBAR)
with st.sidebar:
    st.header("🎮 PANEL JURI")
    
    kategori_aktif = st.selectbox("Pilih Kategori Soal:", list(bank_soal.keys()), on_change=lambda: st.session_state.update(status_jawaban=None, show_winner=False))
    st.divider()
    
    st.subheader("📍 Input Poin")
    tim_penerima = st.selectbox("Tim yang Menjawab:", list(st.session_state.scores.keys()))
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("✅ BENAR (+100)"):
            st.session_state.scores[tim_penerima] += 100
            st.session_state.status_jawaban = "benar"
            st.rerun()
            
    with col_c2:
        if st.button("❌ SALAH"):
            st.session_state.status_jawaban = "salah"
            st.rerun()

    st.divider()
    if st.button("⏭️ Lanjut Soal Berikutnya"):
        st.session_state.progress[kategori_aktif] += 1
        st.session_state.status_jawaban = None
        st.session_state.show_winner = False
        st.rerun()
    
    if st.button("🏆 Lihat Papan Skor"):
        st.session_state.view = "skor"
        st.session_state.status_jawaban = None
        st.session_state.show_winner = False
        st.rerun()

    st.divider()
    st.subheader("Akhir Acara")
    if st.button("🎊 UMUMKAN JUARA 🎊"):
        st.session_state.view = "skor"
        st.session_state.show_winner = True
        st.rerun()

    st.divider()
    if st.button("🔄 Reset Kuis"):
        st.session_state.clear()
        st.rerun()

# 7. TAMPILAN UTAMA (LAYAR KANAN)
if st.session_state.view == "soal":
    # Header
    col_l, col_m, col_r = st.columns([1, 4, 1])
    with col_m:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=150)
        st.markdown("<div class='big-title'>Cerdas Cermat Pilihan Ganda<br>Madrasah Ummuchodijah</div>", unsafe_allow_html=True)
    
    st.divider()
    idx_soal = st.session_state.progress.get(kategori_aktif, 0)
    daftar_soal = bank_soal.get(kategori_aktif, [])
    st.markdown(f"<div class='class-badge'>KATEGORI: {kategori_aktif.upper()}</div>", unsafe_allow_html=True)
    
    if idx_soal < len(daftar_soal):
        q = daftar_soal[idx_soal]
        st.markdown(f"<div class='question-number'>SOAL NO {idx_soal + 1}</div>", unsafe_allow_html=True)
        
        # 1. Menampilkan Teks Soal
        if q.get('tipe') == "arab":
            st.markdown(f"<div class='arabic-text'>{q['tanya']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='question-text'>{q['tanya']}</div>", unsafe_allow_html=True)
            
        # 2. Menampilkan Kotak Pilihan Ganda (A, B, C, D)
        opsi = q.get('opsi', ["-", "-", "-", "-"])
        col_opsi1, col_opsi2 = st.columns(2)
        
        with col_opsi1:
            st.markdown(f"<div class='option-box'><span class='option-letter'>A.</span> {opsi[0]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='option-box'><span class='option-letter'>C.</span> {opsi[2]}</div>", unsafe_allow_html=True)
        with col_opsi2:
            st.markdown(f"<div class='option-box'><span class='option-letter'>B.</span> {opsi[1]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='option-box'><span class='option-letter'>D.</span> {opsi[3]}</div>", unsafe_allow_html=True)
            
        # 3. Logika Notifikasi Benar/Salah
        if st.session_state.status_jawaban == "benar":
            play_sound("benar.mp3") 
            st.balloons() 
            st.markdown(f"<div class='status-benar'>🎉 {tim_penerima} BENAR! (+100 Poin) 🎉</div>", unsafe_allow_html=True)
        elif st.session_state.status_jawaban == "salah":
            play_sound("salah.mp3") 
            st.markdown("<div class='status-salah'>❌ JAWABAN SALAH! ❌</div>", unsafe_allow_html=True)

        st.write("")
        # Rahasia Juri (Kunci Jawaban)
        with st.expander("👁️ Lihat Kunci Jawaban (Hanya Juri)"):
            st.markdown(f"<div class='kunci-jawaban'>{q['jawab']}</div>", unsafe_allow_html=True)
    else:
        st.success(f"🎉 Semua soal untuk {kategori_aktif} telah dijawab!")

else:
    # --- TAMPILAN PAPAN SKOR ---
    if st.button("⬅️ Kembali ke Soal"):
        st.session_state.view = "soal"
        st.session_state.show_winner = False
        st.rerun()
        
    st.markdown("<div class='big-title'>🏆 PAPAN SKOR SEMENTARA 🏆</div>", unsafe_allow_html=True)
    
    # GRAFIK WARNA-WARNI DENGAN ALTAIR
    df = pd.DataFrame(list(st.session_state.scores.items()), columns=['Tim', 'Skor'])
    color_scale = alt.Scale(domain=list(st.session_state.scores.keys()), range=['#FFEB3B', '#4CAF50', '#F44336', '#2196F3', '#9C27B0', '#FF9800'])
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Tim', sort=None, title="", axis=alt.Axis(labelAngle=0, labelFontSize=16, labelColor='white')),
        y=alt.Y('Skor', title="Total Poin", axis=alt.Axis(labelFontSize=14, labelColor='white')),
        color=alt.Color('Tim', scale=color_scale, legend=None)
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
    
    # LOGIKA SELEBRASI JUARA
    if st.session_state.show_winner:
        max_score = max(st.session_state.scores.values())
        if max_score > 0:
            winners = [tim for tim, skor in st.session_state.scores.items() if skor == max_score]
            winner_text = " & ".join(winners)
            play_sound("juara.mp3")
            st.balloons()
            st.snow()
            st.markdown(f"""
            <div class='winner-box'>
                <div class='winner-title'>🌟 SELAMAT KEPADA PEMENANG UTAMA 🌟</div>
                <div class='winner-name'>🥇 {winner_text} 🥇</div>
                <div style='font-size: 30px; color: white; margin-top: 15px;'>Dengan Total Skor: <b>{max_score} Poin</b></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Belum ada tim yang mencetak poin!")
    
    # KOTAK SKOR ANGKA DI BAWAH
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.scores))
    for i, (tim, skr) in enumerate(st.session_state.scores.items()):
        cols[i].markdown(f"""
        <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; text-align:center; border: 2px solid #4CAF50;'>
            <h3 style='color:#FFFFFF; margin:0;'>{tim}</h3>
            <h1 style='color:#4CAF50; font-size:45px; margin:0;'>{skr}</h1>
        </div>
        """, unsafe_allow_html=True)