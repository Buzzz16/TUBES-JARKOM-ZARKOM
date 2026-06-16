# 🚀 Multi-Node Network System: Web Server, Caching Proxy, & UDP QoS Pinger

Sistem jaringan terdistribusi berbasis **3-Node Architecture** yang dirancang menggunakan *Socket Programming* tingkat rendah di Python. Proyek ini mengimplementasikan **Multi-threaded Web Server**, **Smart HTTP Caching Proxy** untuk efisiensi jaringan, serta **UDP QoS Pinger** mandiri untuk mengukur metrik performa kualitas layanan (*Quality of Service*) secara *real-time*.

---

## 🗺️ Arsitektur Jaringan & Alur Komunikasi

Sistem ini memisahkan lalu lintas data menjadi dua jalur utama berdasarkan tujuan fungsionalnya: **Jalur Distribusi Konten (TCP)** dan **Jalur Analisis Jaringan (UDP)**.

```
                  +----------------------------------------+
                  |               ALUR TCP                 |
                  v                                        |
  +-----------------------+  TCP (Port 8080)   +-----------------------+
  |       CLIENT          | =================> |     CACHING PROXY     |
  |   (ID: shahrul)       |                    |   (Port 8080 / 0.0.0) |
  +-----------------------+                    +-----------------------+
     |                                                     |
     |                                                     | TCP (Port 8000)
     |                ALUR UDP (QoS Ping)                  | (Forwarding if MISS)
     +=================================================+   |
                                                       v   v
                                               +-----------------------+
                                               |      WEB SERVER       |
                                               |  TCP: 8000 | UDP: 9000|
                                               +-----------------------+
```

### 📊 Spesifikasi Topologi Node
| Komponen | Protokol | Port Default | Status Koneksi | Peran Utama |
| :--- | :--- | :--- | :--- | :--- |
| **`client.py`** | TCP & UDP | Dinamis (OS) | Aktif (*Inisiator*) | Meminta aset web via Proxy & Menguji performa QoS ke Web Server. |
| **`proxy.py`** | TCP | `8080` | Pasif (*Listen*) & Aktif | Menjadi perantara (*Middleman*), mengelola *cache* lokal, meneruskan *miss request*. |
| **`webserver.py`**| TCP & UDP | `8000` (TCP)<br>`9000` (UDP) | Pasif (*Listen*) | Menyediakan aset statis (HTTP) & Memantulkan paket (*UDP Echo Server*). |

---

## 🔄 Cara Kerja & Mekanisme Detail Proyek

### 1. Alur HTTP Web Request & Caching (TCP)
Ketika Klien meminta file web (contoh: `/index.html`), sistem bekerja dengan mekanisme kontrol berikut:
* **Inisiasi Klien:** Klien membuka *socket* TCP (`SOCK_STREAM`) dan mengirimkan *HTTP Request Header* standar (`GET /index.html HTTP/1.1`) ke arah Proxy (Port 8080).
* **Pengecekan Proxy (Cache Handler):** Proxy menerima request, memisahkan *path* URL, dan memeriksa direktori `./cache/`.
    * **`CACHE HIT`:** Jika file sudah pernah diunduh sebelumnya (misal tersimpan sebagai `_index.html`), Proxy **langsung membaca file lokal** tersebut dan mengirimkannya ke Klien tanpa menyentuh Web Server. Waktu respons menjadi sangat minim (< 1 ms).
    * **`CACHE MISS`:** Jika file belum ada, Proxy bertindak sebagai klien baru. Ia membuka koneksi TCP ke Web Server asli (Port 8000), meminta file tersebut, menerima seluruh aliran byte data, lalu menyaring responsnya. Jika statusnya `200 OK`, Proxy **menyimpan salinannya ke folder cache** untuk kebutuhan mendatang, lalu meneruskan data tersebut kembali ke Klien asli.
* **Resiliensi & Error Handling:** Proxy dilengkapi dengan batas waktu (*timeout* 5 detik). Jika Web Server mati atau tidak merespons, Proxy secara otomatis membuat *HTTP Response* buatan berupa `540 Gateway Timeout` atau `502 Bad Gateway` agar browser/klien tidak mengalami *hang*.

### 2. Alur Pengujian Kualitas Jaringan (UDP QoS)
Untuk mengukur kesehatan infrastruktur jaringan fisik (terutama saat menggunakan skenario 3 laptop berbeda), Klien melakukan *bypass* langsung ke Web Server menggunakan UDP (`SOCK_DGRAM`):
* **Sifat Connectionless:** Klien melempar 10 paket data berisi *sequence number* dan *timestamp* presisi tinggi ke Port 9000 milik Web Server tanpa proses *handshake*.
* **Mekanisme Echo:** Sisi `webserver.py` menjalankan thread UDP pasif yang bertugas menangkap paket apa saja yang masuk ke port 9000, lalu **memantulkannya kembali secara utuh** (*echo*) ke IP dan Port pengirim asli.
* **Komputasi QoS Matematik di Sisi Klien:**
    * **RTT (Round Trip Time):** Dihitung selisih waktu dari paket dikirim hingga paket pantulan diterima kembali ($RTT = T_{recv} - T_{send}$).
    * **Jitter (Variasi Latensi):** Mengukur stabilitas delay antar-paket berurutan menggunakan rumus nilai absolut selisih RTT:
      $$Jitter = |RTT_{n} - RTT_{n-1}|$$
    * **Packet Loss:** Jika dalam 1.0 detik paket pantulan tidak kembali, socket melempar instruksi `socket.timeout`, paket dianggap hilang, dan persentase kehilangan dihitung secara akumulatif.

---

## 🛠️ Fitur-Fitur Unggulan Proyek

1. **High-Concurrency Multi-threading:** Baik Web Server maupun Proxy menggunakan modul `threading.Thread` untuk memisahkan setiap koneksi baru ke dalam *worker thread* mandiri. Server tidak akan mengalami *blocking* meskipun diakses banyak klien sekaligus.
2. **MIME-Type Intelligence:** Web Server mengenali ekstensi file (`.html`, `.css`, `.js`, `.png`, `.jpg`, dll) secara dinamis untuk menyusun *Content-Type Header* yang tepat agar dibaca sempurna oleh *engine rendering* browser.
3. **Automated Cache Sanitization:** Penamaan file cache otomatis mengonversi karakter ilegal/garis miring URL menjadi bentuk yang aman untuk dibaca oleh berkas Sistem Operasi lokal (contoh: `/images/logo.png` menjadi `_images_logo.png`).
4. **Isolated Status Directory:** Jika terjadi kegagalan pencarian berkas di server, sistem akan mencari file kustom `./status/404.html` terlebih dahulu untuk memberikan pengalaman visual *error page* yang profesional kepada pengguna.

---

## ⚙️ Panduan Instalasi & Pengujian Sistem

### A. Uji Coba Terisolasi (1 Laptop / Localhost)
Secara default, seluruh konfigurasi IP diatur ke arah `127.0.0.1`. Anda dapat langsung menjalankan ketiga terminal secara berurutan.

1. **Terminal 1 (Jalankan Web Server):**
   ```bash
   python webserver.py
   ```
2. **Terminal 2 (Jalankan Proxy Server):**
   ```bash
   python proxy.py
   ```
3. **Terminal 3 (Jalankan Client):**
   ```bash
   python client.py
   ```

### B. Uji Coba Lapangan (3 Laptop Berbeda)
Jika Anda melakukan presentasi menggunakan 3 laptop yang terhubung dalam satu jaringan Wi-Fi/LAN yang sama, ikuti perubahan konfigurasi berikut:

1. **Cari Tahu IP Masing-Masing:** Ketik `ipconfig` (Windows) atau `ifconfig` (Mac/Linux) di terminal.
2. **Konfigurasi `webserver.py`:**
   * Tetap gunakan `HOST = '0.0.0.0'` (agar mendengarkan ke semua interface kartu jaringan).
3. **Konfigurasi `proxy.py`:**
   * Ubah `WEBSERVER_HOST = 'IP_LAPTOP_WEBSERVER_KAMU'`
4. **Konfigurasi `client.py`:**
   * Ubah `PROXY_IP = 'IP_LAPTOP_PROXY_KAMU'`
   * Ubah `WEBSERVER_IP = 'IP_LAPTOP_WEBSERVER_KAMU'`
   * Sesuaikan `CLIENT_ID` jika ingin memberikan identitas unik pada log komputer Anda.

---

## 📋 Log Terminal yang Diharapkan

* **Saat Cache MISS (Pertama kali akses berkas):**
  ```text
  [PROXY LOG] 192.168.1.5 | /index.html | MISS | 12.45 ms
  [TCP LOG] 18:23:01 | 192.168.1.10 | /index.html | 200 OK
  ```
* **Saat Cache HIT (Akses kedua kali dan seterusnya):**
  ```text
  [PROXY LOG] 192.168.1.5 | /index.html | HIT | 0.15 ms
  ```
* **Statistik QoS UDP:**
  ```text
  [Client: shahrul] --- Statistik QoS UDP ---
  Min RTT   : 2.10 ms
  Max RTT   : 5.89 ms
  Avg RTT   : 3.42 ms
  Avg Jitter: 0.85 ms
  Packet Loss: 0%
  ```

---
Dibuat dengan 💻 untuk Tugas Besar Jaringan Komputer. Pastikan struktur folder `./status/` dan file `./index.html` sudah tersedia sebelum memulai pengujian!
