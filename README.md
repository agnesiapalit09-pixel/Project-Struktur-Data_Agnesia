# Project-Struktur-Data_Agnesia
Project Layanan Pengantaran Makanan/Barang

A. Deskripsi Proyek

Proyek ini merupakan program untuk mengelola pesanan, antrean, dan laporan pesanan. Tujuan dari proyek ini adalah untuk mengelola pesanan, antrean, dan laporan secara terstruktur. Proyek ini dibuat dengan menggunakan bahasa pemrograman Python, csv, dan struktur data.
    
B. Fitur Utama

Pengelolaan data pesanan
Pengelolaan antrean pesanan
Penyimpanan dan pengolahan data pesanan
Pengurutan data menggunakan sorting
UI pengguna untuk menjalankan fitur program


C. Struktur Repository

README.md
backend
    m1_pesanan.py
    m2_antrean.py
    m3_laporan.py
frontend
    ui.py
database
    pesanan.csv
    peta.csv
app.py

D. Teknologi yang DIgunakan

Bahasa pemrograman Python dan penyimpanan data CSV

E. Cara Menjalankan

Download setiap file ke komputer, cek apakah versi Python sesuai, lalu jalankan dari file ui.py dengan bahasa Python

F. Flowchart Sistem

<img width="196" height="526" alt="image" src="https://github.com/user-attachments/assets/c4ab8e5c-38a6-4519-89ab-6a6582649a8c" />

G. Screenshot 

Main Menu <img width="1185" height="718" alt="image" src="https://github.com/user-attachments/assets/1452a115-e84b-49d4-9bf7-dd90893d085c" />

Pengelolaan Pesanan <img width="1144" height="700" alt="image" src="https://github.com/user-attachments/assets/bd26eb53-a214-46fd-b607-5245b22c3e41" /> <img width="1182" height="743" alt="image" src="https://github.com/user-attachments/assets/ad560fea-f3e2-4e9b-8c1d-5cbe967a15b8" />

Pengelolaan Antrean <img width="1147" height="697" alt="image" src="https://github.com/user-attachments/assets/15b25450-af7a-4cb0-997c-e74c1a85f6ff" /> <img width="1182" height="698" alt="image" src="https://github.com/user-attachments/assets/e3a7a367-abeb-4e42-afa0-c1fcff3b26e2" />

Laporan dan Sorting <img width="1157" height="697" alt="image" src="https://github.com/user-attachments/assets/f0c7e159-4c93-4375-88eb-80df2f5cbfc3" /> <img width="1146" height="707" alt="image" src="https://github.com/user-attachments/assets/5103bd03-7dd7-4e4b-9fed-853f1450120c" />


H. Circular Queue

Circular queue menggunakan variabel front dan rear untuk menunjukkan posisi elemen dalam antrean. Namun, ketika hanya menggunakan kedua variabel tersebut, kondisi kosong dan penuh dapat sama-sama menghasilkan front == rear. Penggunaan count dipilih karena kondisi kosong dan penuh dapat diketahui secara langsung. Selain itu, seluruh slot array dapat digunakan tanpa perlu menyisakan satu slot kosong.

I. Perbandingan Insertion vs Merge

<img width="815" height="97" alt="image" src="https://github.com/user-attachments/assets/6f3f0e1a-e98b-44f8-b836-03209db06c26" />







    
