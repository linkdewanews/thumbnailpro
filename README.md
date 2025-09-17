# Thumbnail Generator Pro

Aplikasi desktop untuk membuat thumbnail dari file video secara massal, lengkap dengan fitur watermarking.

![App Screenshot](https://file.ahs.my.id/-Xd8xtCSyZB)  
*Catatan: Ganti URL di atas dengan URL screenshot aplikasi Anda.*

---

## 💡 Penjelasan Singkat

**Thumbnail Generator Pro** adalah sebuah alat bantu yang dirancang untuk mempercepat proses pembuatan thumbnail dari banyak video sekaligus. Aplikasi ini akan memindai sebuah folder, memproses setiap file video di dalamnya, dan menghasilkan dua jenis thumbnail (original & kolase) serta memindahkannya ke dalam subfolder yang terorganisir.

## ✨ Fitur Utama

- **Proses Batch**: Proses banyak video dari satu folder sumber secara otomatis.
- **Dua Jenis Thumbnail**: Menghasilkan thumbnail dari frame tengah (original) dan thumbnail berbentuk kolase (grid).
- **Rasio Aspek**: Mendukung output untuk rasio **Portrait (9:16)** dan **Square (1:1)**.
- **Watermark Kustom**: Tambahkan watermark berupa teks pada setiap thumbnail yang dihasilkan.
- **Pengaturan Posisi Watermark**: Pilih posisi watermark dari 5 lokasi yang tersedia (pojok-pojok atau tengah).
- **Manajemen File Otomatis**: Video yang telah diproses akan dipindahkan ke dalam subfolder masing-masing bersama dengan thumbnailnya.
- **UI Modern**: Antarmuka pengguna yang bersih dan mudah digunakan, dibangun dengan Flet.

## ⚙️ Instalasi

Pastikan Anda memiliki **Python 3.7+** terinstal di sistem Anda.

1.  **Clone atau Download Repository**
    ```bash
    git clone https://github.com/linkdewanews/thumbnailpro.git
    ```
    Atau unduh file ZIP dan ekstrak.

2.  **Masuk ke Direktori Proyek**
    ```bash
    cd thumbnailpro
    ```

3.  **Instal Dependensi**
    Semua library yang dibutuhkan sudah terdaftar di dalam file `requirements.txt`. Jalankan perintah berikut:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Menjalankan Aplikasi

Setelah semua dependensi terinstal, jalankan aplikasi dengan perintah:

```bash
python main.py
```

---
