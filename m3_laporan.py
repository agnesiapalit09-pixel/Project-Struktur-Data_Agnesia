import csv
import os
import time

def muat_data(path):
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        pembaca = csv.reader(file)
        next(pembaca, None)
        return [baris for baris in pembaca if len(baris) >= 9]

def insertion_sort(data, kolom):
    banding = 0

    for i in range(1, len(data)):
        kunci = data[i]
        j = i - 1

        while j >= 0:
            banding += 1
            if data[j][kolom] > kunci[kolom]:
                data[j + 1] = data[j]
                j -= 1
            else:
                break

        data[j + 1] = kunci

    return banding

def merge_sort(data, kolom):
    banding = [0]

    def urutkan(data):
        if len(data) <= 1:
            return data

        tengah = len(data) // 2
        kiri = urutkan(data[:tengah])
        kanan = urutkan(data[tengah:])
        hasil = []
        i = j = 0

        while i < len(kiri) and j < len(kanan):
            banding[0] += 1

            if kiri[i][kolom] <= kanan[j][kolom]:
                hasil.append(kiri[i])
                i += 1
            else:
                hasil.append(kanan[j])
                j += 1

        hasil.extend(kiri[i:])
        hasil.extend(kanan[j:])
        return hasil

    data[:] = urutkan(data)
    return banding[0]

def linear_search(data, target):
    banding = 0

    for i in range(len(data)):
        banding += 1
        if data[i][0] == target:
            return i, banding

    return -1, banding

def binary_search(data, target):
    kiri, kanan = 0, len(data) - 1
    banding = 0

    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        banding += 1

        if data[tengah][0] == target:
            return tengah, banding
        elif data[tengah][0] < target:
            kiri = tengah + 1
        else:
            kanan = tengah - 1

    return -1, banding

def ukur_sort(data, nama, fungsi, kolom):
    salinan = data.copy()
    mulai = time.perf_counter()
    banding = fungsi(salinan, kolom)
    waktu = (time.perf_counter() - mulai) * 1000

    print(f"\n=== {nama} ===")
    print("Jumlah data  :", len(salinan))
    print("Perbandingan :", banding)
    print(f"Waktu        : {waktu:.4f} ms")

    for baris in salinan[:5]:
        print(baris[0], baris[7])

def ukur_search(data, target, fungsi, nama):
    mulai = time.perf_counter()
    indeks, banding = fungsi(data, target)
    waktu = (time.perf_counter() - mulai) * 1000

    print(f"\n=== {nama} ===")
    print("Perbandingan:", banding)
    print(f"Waktu       : {waktu:.4f} ms")

    if indeks != -1:
        p = data[indeks]
        print("ID       :", p[0])
        print("Pelanggan:", p[1])
        print("Restoran :", p[2])
        print("Menu     :", p[3])
        print("Harga    : Rp" + p[4])
        print("Selesai  :", p[7])
        print("Status   :", p[8])
    else:
        print("Pesanan tidak ditemukan.")

def main():
    path = os.path.join(
        os.path.dirname(__file__), "..", "database", "pesanan.csv"
    )

    try:
        data = muat_data(path)
    except FileNotFoundError:
        print("File database/pesanan.csv tidak ditemukan.")
        return

    print("Berhasil memuat", len(data), "pesanan.")

    while True:
        print("\n M3 SORT & SEARCH")
        print("1. Insertion Sort")
        print("2. Merge Sort")
        print("3. Linear Search")
        print("4. Binary Search")
        print("0. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            ukur_sort(data, "INSERTION SORT", insertion_sort, 7)

        elif pilihan == "2":
            ukur_sort(data, "MERGE SORT", merge_sort, 7)

        elif pilihan == "3":
            target = input("Masukkan ID pesanan: ").strip()
            ukur_search(data, target, linear_search, "LINEAR SEARCH")

        elif pilihan == "4":
            target = input("Masukkan ID pesanan: ").strip()
            salinan = data.copy()
            merge_sort(salinan, 0)
            ukur_search(salinan, target, binary_search, "BINARY SEARCH")

        elif pilihan == "0":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
