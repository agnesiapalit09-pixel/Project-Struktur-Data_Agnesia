import csv
import os
import time

class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai="", status="ANTRE"):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = int(harga)
        self.prioritas = int(prioritas)
        self.t_masuk = t_masuk
        self.t_selesai = t_selesai
        self.status = status

    def __str__(self):
        jenis = "VIP" if self.prioritas == 1 else (
            "PRIORITAS" if self.prioritas == 2 else "REGULER"
        )
        return (
            f"\nID: {self.oid}\n"
            f"Pelanggan: {self.pelanggan}\n"
            f"Restoran: {self.resto}\n"
            f"Menu: {self.menu}\n"
            f"Harga: Rp{self.harga}\n"
            f"Prioritas: {jenis}\n"
            f"Status: {self.status}"
        )

class ArrayPesanan:
    def __init__(self):
        self.data = [None] * 4
        self.size = 0

    def __len__(self):
        return self.size

    def get(self, indeks):
        if indeks < 0 or indeks >= self.size:
            raise IndexError("Indeks tidak valid")
        return self.data[indeks]

    def _resize(self):
        baru = [None] * (len(self.data) * 2)
        for i in range(self.size):
            baru[i] = self.data[i]
        self.data = baru

    def insert(self, indeks, pesanan):
        if indeks < 0 or indeks > self.size:
            raise IndexError("Indeks tidak valid")

        if self.size == len(self.data):
            self._resize()

        for i in range(self.size, indeks, -1):
            self.data[i] = self.data[i - 1]

        self.data[indeks] = pesanan
        self.size += 1

    def append(self, pesanan):
        self.insert(self.size, pesanan)

    def hapus(self, indeks):
        pesanan = self.get(indeks)

        for i in range(indeks, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.size -= 1
        self.data[self.size] = None
        return pesanan

class Node:
    def __init__(self, pesanan):
        self.pesanan = pesanan
        self.next = None

class LinkedListPesanan:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __len__(self):
        return self.size

    def get_node(self, indeks):
        if indeks < 0 or indeks >= self.size:
            raise IndexError("Indeks tidak valid")

        node = self.head
        for i in range(indeks):
            node = node.next
        return node

    def get(self, indeks):
        return self.get_node(indeks).pesanan

    def insert(self, indeks, pesanan):
        if indeks < 0 or indeks > self.size:
            raise IndexError("Indeks tidak valid")

        baru = Node(pesanan)

        if indeks == 0:
            baru.next = self.head
            self.head = baru
            if self.size == 0:
                self.tail = baru

        elif indeks == self.size:
            if self.tail:
                self.tail.next = baru
            else:
                self.head = baru
            self.tail = baru

        else:
            sebelumnya = self.get_node(indeks - 1)
            baru.next = sebelumnya.next
            sebelumnya.next = baru

        self.size += 1

    def append(self, pesanan):
        self.insert(self.size, pesanan)

    def hapus(self, indeks):
        if indeks < 0 or indeks >= self.size:
            raise IndexError("Indeks tidak valid")

        if indeks == 0:
            dihapus = self.head
            self.head = self.head.next
            if self.size == 1:
                self.tail = None
        else:
            sebelumnya = self.get_node(indeks - 1)
            dihapus = sebelumnya.next
            sebelumnya.next = dihapus.next
            if dihapus == self.tail:
                self.tail = sebelumnya

        self.size -= 1
        return dihapus.pesanan

def muat_pesanan_csv(path, array, linked_list):
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        pembaca = csv.reader(file)
        next(pembaca, None)

        for baris in pembaca:
            if len(baris) < 9:
                continue

            pesanan = Pesanan(
                baris[0], baris[1], baris[2], baris[3],
                baris[4], baris[5], baris[6], baris[7], baris[8]
            )
            array.append(pesanan)
            linked_list.append(pesanan)

def buat_id_pesanan(array):
    terbesar = 0

    for i in range(len(array)):
        oid = array.get(i).oid
        if oid.startswith("O-"):
            try:
                nomor = int(oid[2:])
                if nomor > terbesar:
                    terbesar = nomor
            except ValueError:
                pass

    return f"O-{terbesar + 1:06d}"

def lihat_pesanan(array, linked_list):
    try:
        indeks = int(input("Nomor pesanan: ")) - 1

        mulai = time.perf_counter()
        pesanan = array.get(indeks)
        waktu_array = (time.perf_counter() - mulai) * 1000

        mulai = time.perf_counter()
        linked_list.get(indeks)
        waktu_linked = (time.perf_counter() - mulai) * 1000

        print(pesanan)
        print(f"Waktu Array: {waktu_array:.4f} ms")
        print(f"Waktu Linked List: {waktu_linked:.4f} ms")

    except (ValueError, IndexError):
        print("Nomor pesanan tidak valid.")

def tambah_pesanan(array, linked_list, prioritas):
    pelanggan = input("Nama pelanggan: ").strip()
    resto = input("Nama restoran: ").strip()
    menu = input("Nama menu: ").strip()

    try:
        harga = int(input("Harga: Rp"))
        if not pelanggan or not resto or not menu or harga < 0:
            raise ValueError
    except ValueError:
        print("Data tidak valid.")
        return

    pesanan = Pesanan(
        buat_id_pesanan(array), pelanggan, resto, menu,
        harga, prioritas, time.time()
    )

    indeks = 0 if prioritas == 1 else (
        len(array) // 2 if prioritas == 2 else len(array)
    )

    mulai = time.perf_counter()
    array.insert(indeks, pesanan)
    waktu_array = (time.perf_counter() - mulai) * 1000

    mulai = time.perf_counter()
    linked_list.insert(indeks, pesanan)
    waktu_linked = (time.perf_counter() - mulai) * 1000

    print("\nPesanan berhasil ditambahkan!")
    print(pesanan)
    print(f"Waktu Array: {waktu_array:.4f} ms")
    print(f"Waktu Linked List: {waktu_linked:.4f} ms")

def hapus_pesanan(array, linked_list):
    try:
        indeks = int(input("Nomor pesanan yang dihapus: ")) - 1
        pesanan = array.get(indeks)

        print(pesanan)
        konfirmasi = input("Yakin hapus? (y/n): ").lower()

        if konfirmasi != "y":
            print("Penghapusan dibatalkan.")
            return

        mulai = time.perf_counter()
        array.hapus(indeks)
        waktu_array = (time.perf_counter() - mulai) * 1000

        mulai = time.perf_counter()
        linked_list.hapus(indeks)
        waktu_linked = (time.perf_counter() - mulai) * 1000

        print("Pesanan berhasil dihapus.")
        print(f"Waktu Array: {waktu_array:.4f} ms")
        print(f"Waktu Linked List: {waktu_linked:.4f} ms")

    except (ValueError, IndexError):
        print("Nomor pesanan tidak valid.")


def main():
    array = ArrayPesanan()
    linked_list = LinkedListPesanan()

    path = os.path.join(
        os.path.dirname(__file__), "..", "database", "pesanan.csv"
    )

    try:
        muat_pesanan_csv(path, array, linked_list)
        print(f"Berhasil memuat {len(array)} pesanan.")
    except FileNotFoundError:
        print("File database/pesanan.csv tidak ditemukan.")
        return

    while True:
        print("\n MENU PESANAN")
        print("1. Lihat pesanan")
        print("2. Tambah REGULER")
        print("3. Tambah PRIORITAS")
        print("4. Tambah VIP")
        print("5. Hapus pesanan")
        print("0. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            lihat_pesanan(array, linked_list)
        elif pilihan == "2":
            tambah_pesanan(array, linked_list, 3)
        elif pilihan == "3":
            tambah_pesanan(array, linked_list, 2)
        elif pilihan == "4":
            tambah_pesanan(array, linked_list, 1)
        elif pilihan == "5":
            hapus_pesanan(array, linked_list)
        elif pilihan == "0":
            print("Program selesai.")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
