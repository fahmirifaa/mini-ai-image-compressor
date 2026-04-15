# ⚡ ImgPress Pro v2.0

> Aplikasi kompresi gambar berbasis Streamlit — offline, cepat, dan mendukung JPEG · PNG · WebP · AVIF.

---

## 📋 Daftar Isi

- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Cara Pakai](#cara-pakai)
- [Fitur](#fitur)
- [Troubleshooting](#troubleshooting)

## Persyaratan

- **Python** 3.10 atau lebih baru
- **pip** (sudah termasuk saat install Python)
- Koneksi internet hanya diperlukan saat instalasi — aplikasi berjalan **100% offline**

Cek versi Python kamu dulu:

```bash
python --version
```

Kalau belum punya Python, download di: https://www.python.org/downloads/

## Instalasi

### 1. Download file aplikasi

Simpan file `app_kompres.py` ke folder mana saja, misalnya:

```
C:\Users\NamaKamu\Documents\imgpress\app_kompres.py
```

### 2. Buka terminal / Command Prompt

Di Windows: tekan `Win + R`, ketik `cmd`, Enter.

Masuk ke folder tempat kamu simpan file:

```bash
cd C:\Users\NamaKamu\Documents\imgpress
```

### 3. (Opsional tapi disarankan) Buat virtual environment

Virtual environment mencegah konflik antar library Python di komputer kamu.

```bash
# Buat environment baru
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Aktifkan (Mac / Linux)
source venv/bin/activate
```

Kalau berhasil, di terminal akan muncul `(venv)` di depan prompt.

### 4. Install Pillow

```bash
pip install Pillow
```

Versi minimum yang dibutuhkan: **Pillow 9.1+** (untuk dukungan AVIF).
Untuk cek versi terpasang:

```bash
python -c "import PIL; print(PIL.__version__)"
```

### 5. Install Streamlit

```bash
pip install streamlit
```

### 6. Install semua sekaligus (alternatif cepat)

Kalau mau install semuanya dalam satu perintah:

```bash
pip install streamlit Pillow
```

---

## Menjalankan Aplikasi

Pastikan kamu sudah berada di folder yang berisi `app_kompres.py`, lalu jalankan:

```bash
streamlit run app_kompres.py
```

Streamlit akan otomatis membuka browser di alamat:

```
http://localhost:8501
```

Kalau browser tidak terbuka otomatis, buka manual alamat di atas.

Untuk **menghentikan** aplikasi: tekan `Ctrl + C` di terminal.

---

## Cara Pakai

1. **Upload gambar** — drag & drop ke zona upload, atau klik dan pilih file (JPG, PNG, WebP, AVIF)
2. **Atur skala dimensi** — geser slider untuk mengecilkan resolusi (misal 50% = setengah ukuran)
3. **Tentukan target ukuran file** — masukkan batas maksimal output dalam MB
4. **Pilih format output** — JPEG, PNG, WebP lossy/lossless, atau AVIF
5. **Klik "Optimise Now"** — proses kompresi berjalan otomatis
6. **Lihat perbandingan** — tampil side-by-side gambar asli vs hasil
7. **Download** — klik tombol download untuk menyimpan hasil

---

## Fitur

| Fitur | Keterangan |
|---|---|
| Format input | JPG, JPEG, PNG, WebP, AVIF |
| Format output | JPEG, PNG (palette 256 warna), WebP lossy, WebP lossless, AVIF |
| Kompresi cerdas | Binary-search quality otomatis untuk mencapai target ukuran |
| Resize | Skala 10%–100% dengan resampling LANCZOS (atau BILINEAR untuk gambar besar) |
| Strip EXIF | Hapus metadata kamera/GPS untuk privasi dan ukuran lebih kecil |
| EXIF viewer | Lihat metadata asli sebelum diproses |
| Drag anywhere | Drag gambar ke mana saja di halaman, tidak harus ke zona upload |
| Offline | Tidak ada API eksternal, semua proses lokal |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'streamlit'`**
→ Jalankan `pip install streamlit` lalu coba lagi.

**`ModuleNotFoundError: No module named 'PIL'`**
→ Jalankan `pip install Pillow` (huruf P besar).

**`ValueError: Fast Octree ... are the only valid methods`**
→ Pastikan kamu menggunakan file `app_kompres.py` versi terbaru yang sudah dipatch.

**AVIF tidak bisa disimpan / error saat export AVIF**
→ AVIF membutuhkan Pillow 9.1+ yang dikompilasi dengan `libavif`. Coba upgrade: `pip install --upgrade Pillow`. Kalau masih error, gunakan format WebP Lossless sebagai alternatif.

**Port 8501 sudah dipakai**
→ Jalankan di port lain: `streamlit run app_kompres.py --server.port 8502`

**Aplikasi lambat saat gambar sangat besar (>16 MP)**
→ Normal — Streamlit memproses gambar di CPU. Coba kecilkan skala dimensi ke 50–70% sebelum klik Optimise.

---

## Struktur File

```
imgpress/
└── app_kompres.py   ← satu file, semua sudah di dalamnya
```

Tidak ada file konfigurasi tambahan yang dibutuhkan.

---

*ImgPress Pro v2.0 — dibuat dengan Streamlit & Pillow*
