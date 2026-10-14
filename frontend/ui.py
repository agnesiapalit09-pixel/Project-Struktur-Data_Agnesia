import csv
import os
import time
import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)
from m2_antrean import M2Manager
def find_csv_path():
    """Cari CSV baik UI diletakkan di root project maupun di folder frontend."""
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(here, "database", "pesanan.csv"),
        os.path.join(os.path.dirname(here), "database", "pesanan.csv"),
        os.path.join(os.path.dirname(os.path.dirname(here)), "database", "pesanan.csv"),
        os.path.join(here, "pesanan.csv"),
        os.path.join(os.path.dirname(here), "pesanan.csv"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]
CSV_PATH = find_csv_path()
GREEN_DARK = "#245b45"
GREEN = "#4f9b72"
GREEN_LIGHT = "#e6f4ea"
PINK = GREEN
PINK_LIGHT = GREEN_LIGHT
BG = "#f7f7f2"
TEXT = "#26352c"
WHITE = "#ffffff"
def load_csv():
    rows = []
    if not os.path.isfile(CSV_PATH):
        raise FileNotFoundError(
            "File pesanan.csv tidak ditemukan. Letakkan file di folder database/pesanan.csv "
            "pada root project. Lokasi yang dicari: " + CSV_PATH
        )
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) >= 9:
                rows.append(row)
    return rows
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
class LinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0
    def append(self, value):
        node = Node(value)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1
    def get(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Indeks tidak valid")
        node = self.head
        for _ in range(index):
            node = node.next
        return node.value
    def insert(self, index, value):
        if index < 0 or index > self.size:
            raise IndexError("Indeks tidak valid")
        node = Node(value)
        if index == 0:
            node.next = self.head
            self.head = node
            if self.size == 0:
                self.tail = node
        elif index == self.size:
            self.tail.next = node
            self.tail = node
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next
            node.next = prev.next
            prev.next = node
        self.size += 1
    def delete(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Indeks tidak valid")
        if index == 0:
            node = self.head
            self.head = node.next
            if self.size == 1:
                self.tail = None
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next
            node = prev.next
            prev.next = node.next
            if node == self.tail:
                self.tail = prev
        self.size -= 1
        return node.value
def tokenize_expression(expression):
    """Memecah ekspresi infix menjadi daftar token untuk ditampilkan di UI."""
    tokens, number = [], ""
    for char in expression:
        if char.isdigit():
            number += char
        else:
            if number:
                tokens.append(number)
                number = ""
            if char in "+-*/()":
                tokens.append(char)
            elif not char.isspace():
                raise ValueError("Karakter tidak dikenal: " + char)
    if number:
        tokens.append(number)
    if not tokens:
        raise ValueError("Ekspresi tidak boleh kosong")
    return tokens
def infix_to_postfix(expression):
    tokens, number = [], ""
    for char in expression:
        if char.isdigit():
            number += char
        else:
            if number:
                tokens.append(number)
                number = ""
            if char in "+-*/()":
                tokens.append(char)
            elif not char.isspace():
                raise ValueError("Karakter tidak dikenal: " + char)
    if number:
        tokens.append(number)
    stack, output = [], []
    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Tanda kurung tidak sesuai")
            stack.pop()
        else:
            while stack and stack[-1] != "(":
                p_top = 2 if stack[-1] in "*/" else 1
                p_now = 2 if token in "*/" else 1
                if p_top >= p_now:
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
    while stack:
        if stack[-1] == "(":
            raise ValueError("Tanda kurung tidak sesuai")
        output.append(stack.pop())
    return " ".join(output)
def evaluate_postfix(postfix):
    stack = []
    for token in postfix.split():
        if token.lstrip("-").isdigit():
            stack.append(int(token))
        else:
            if len(stack) < 2:
                raise ValueError("Ekspresi postfix tidak valid")
            b, a = stack.pop(), stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                if b == 0:
                    raise ValueError("Tidak bisa membagi dengan nol")
                stack.append(a / b)
            else:
                raise ValueError("Operator tidak dikenal")
    if len(stack) != 1:
        raise ValueError("Ekspresi postfix tidak valid")
    return stack[0]
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2EZ4U Food Delivery")
        self.geometry("1180x740")
        self.minsize(980, 620)
        self.configure(bg=BG)
        try:
            self.rows = load_csv()
            load_error = None
        except Exception as error:
            self.rows = []
            load_error = str(error)
        self.array = self.rows.copy()
        self.linked = LinkedList()
        for row in self.rows:
            self.linked.append(row)
        self.queue = self.rows.copy()
        self.m2 = M2Manager(self.rows)
        self.queue_circular = self.m2.circular
        self.undo_stack = self.m2.undo_stack
        self.redo_stack = self.m2.redo_stack
        self.current_action = "Load"
        self._style()
        self._build_layout()
        self.show_page("Load")
        if load_error:
            self.log("CSV belum dimuat: " + load_error)
        else:
            self.log(f"Load -> M1: Array + Linked List | {len(self.rows)} data")
    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 9))
        style.configure("TLabelframe", background=BG, foreground=GREEN_DARK)
        style.configure("TLabelframe.Label", background=BG, foreground=GREEN_DARK,
                        font=("Segoe UI", 9, "bold"))
        style.configure("TEntry", padding=5)
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 9),
                        background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background=GREEN_LIGHT, foreground=GREEN_DARK)
        style.map("Treeview.Heading", background=[("active", GREEN)])
        style.configure("TButton", padding=5, font=("Segoe UI", 9))
    def _build_layout(self):
        header = tk.Frame(self, bg=GREEN_DARK, height=48)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="2EZ4U Food Delivery", bg=GREEN_DARK, fg=WHITE,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=14)
        tk.Label(header, text="PESANAN • STACK & QUEUE • SORT & SEARCH",
                 bg=GREEN_DARK, fg="#e5f5e9",
                 font=("Segoe UI", 9)).pack(side="right", padx=14)
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=8)
        side = tk.Frame(body, bg=PINK_LIGHT, width=255, bd=1, relief="solid")
        side.pack(side="left", fill="y", padx=(0, 8))
        side.pack_propagate(False)
        tk.Label(side, text="MENU UTAMA", bg=PINK, fg=GREEN_DARK,
                 font=("Segoe UI", 10, "bold"), anchor="w", padx=10, pady=8).pack(fill="x")
        menu_canvas = tk.Canvas(side, bg=PINK_LIGHT, highlightthickness=0, bd=0)
        menu_scrollbar = ttk.Scrollbar(side, orient="vertical", command=menu_canvas.yview)
        menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        menu_scrollbar.pack(side="right", fill="y")
        menu_canvas.pack(side="left", fill="both", expand=True)
        menu_content = tk.Frame(menu_canvas, bg=PINK_LIGHT)
        menu_window = menu_canvas.create_window((0, 0), window=menu_content, anchor="nw")
        def update_menu_scrollregion(_event=None):
            menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        def resize_menu_content(event):
            menu_canvas.itemconfigure(menu_window, width=event.width)
        menu_content.bind("<Configure>", update_menu_scrollregion)
        menu_canvas.bind("<Configure>", resize_menu_content)
        def menu_mousewheel(event):
            if event.delta:
                menu_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def menu_linux_scroll_up(_event):
            menu_canvas.yview_scroll(-1, "units")
        def menu_linux_scroll_down(_event):
            menu_canvas.yview_scroll(1, "units")
        menu_canvas.bind_all("<MouseWheel>", menu_mousewheel)
        menu_canvas.bind_all("<Button-4>", menu_linux_scroll_up)
        menu_canvas.bind_all("<Button-5>", menu_linux_scroll_down)
        menu_groups = [
            ("DATA", [("Load / Muat Ulang", "Load")]),
            ("M1 - DATA PESANAN", [
                ("Array - Lihat Pesanan", "M1 Lihat Array"),
                ("Array - Tambah Reguler", "M1 Tambah Reguler"),
                ("Array - Tambah Prioritas", "M1 Tambah Prioritas"),
                ("Array - Tambah VIP", "M1 Tambah VIP"),
                ("Array - Hapus Pesanan", "M1 Hapus Array"),
                ("Linked List - Lihat Pesanan", "M1 Lihat Linked"),
                ("Linked List - Tambah Reguler", "LL Tambah Reguler"),
                ("Linked List - Tambah Prioritas", "LL Tambah Prioritas"),
                ("Linked List - Tambah VIP", "LL Tambah VIP"),
                ("Linked List - Hapus Pesanan", "M1 Hapus Linked"),
            ]),
            ("M2 - STACK & QUEUE", [
                ("Stack - Postfix (Kasir)", "M2 Kalkulator"),
                ("Queue - Enqueue", "M2 Enqueue"),
                ("Queue - Dequeue Naif", "M2 Dequeue Naif"),
                ("Queue - Dequeue Circular", "M2 Dequeue Circular"),
                ("Stack - Undo", "M2 Undo"),
                ("Stack - Redo Aksi", "M2 Redo"),
            ]),
            ("M3 - SORT & SEARCH", [
                ("Sort - Insertion Sort", "M3 Insertion"),
                ("Sort - Merge Sort", "M3 Merge"),
                ("Search - Linear Search", "M3 Linear"),
                ("Search - Binary Search", "M3 Binary"),
            ]),
        ]
        for heading, items in menu_groups:
            tk.Label(menu_content, text=heading, bg=PINK_LIGHT, fg=GREEN_DARK,
                     font=("Segoe UI", 8, "bold"), anchor="w", padx=8, pady=4).pack(fill="x")
            for label, action in items:
                tk.Button(
                    menu_content, text=label, anchor="w", padx=8, pady=4,
                    bg=WHITE, fg=TEXT, activebackground=GREEN_LIGHT,
                    activeforeground=GREEN_DARK, relief="groove", bd=1,
                    font=("Segoe UI", 8),
                    command=lambda a=action: self.show_page(a)
                ).pack(fill="x", padx=6, pady=1)
        self.ready = tk.Label(side, text="● siap", bg=GREEN_DARK, fg=WHITE,
                              anchor="w", padx=10, pady=7, font=("Segoe UI", 9, "bold"))
        self.ready.pack(side="bottom", fill="x")
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self.title_label = tk.Label(right, text="Array: lihat pesanan",
                                    bg=GREEN_LIGHT, fg=GREEN_DARK,
                                    font=("Segoe UI", 13, "bold"), anchor="w", padx=12, pady=9)
        self.title_label.pack(fill="x")
        self.description = tk.Label(right, text="Pilih menu di sebelah kiri.",
                                    bg=BG, fg="#627168", anchor="w", padx=12, pady=5)
        self.description.pack(fill="x")
        self.form = tk.Frame(right, bg=BG, padx=10, pady=8)
        self.form.pack(fill="x")
        self.result_frame = tk.Frame(right, bg=WHITE, bd=1, relief="solid")
        self.result_frame.pack(fill="both", expand=True, padx=4, pady=(4, 8))
        self.result = tk.Text(self.result_frame, wrap="word", font=("Consolas", 10),
                              bg=WHITE, fg=TEXT, relief="flat", padx=10, pady=8)
        result_scroll = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result.yview)
        self.result.configure(yscrollcommand=result_scroll.set)
        self.result.pack(side="left", fill="both", expand=True)
        result_scroll.pack(side="right", fill="y")
        self.sort_table_frame = tk.Frame(self.result_frame, bg=WHITE)
        self.sort_columns = ("no", "id", "harga", "selesai", "resto", "menu")
        self.sort_table = ttk.Treeview(
            self.sort_table_frame, columns=self.sort_columns,
            show="headings", height=12
        )
        headings = {
            "no": ("#", 45), "id": ("ID PESANAN", 110),
            "harga": ("HARGA", 95), "selesai": ("WAKTU SELESAI", 135),
            "resto": ("RESTORAN", 160), "menu": ("MENU", 180)
        }
        for col, (heading, width) in headings.items():
            self.sort_table.heading(col, text=heading)
            self.sort_table.column(col, width=width, minwidth=55, anchor="w")
        self.sort_table_scroll = ttk.Scrollbar(
            self.sort_table_frame, orient="vertical", command=self.sort_table.yview
        )
        self.sort_table.configure(yscrollcommand=self.sort_table_scroll.set)
        self.sort_table.pack(side="left", fill="both", expand=True)
        self.sort_table_scroll.pack(side="right", fill="y")
        self.m2_table_frame = tk.Frame(self.result_frame, bg=WHITE)
        self.m2_table = ttk.Treeview(
            self.m2_table_frame, columns=("kolom", "isi"), show="headings", height=12
        )
        self.m2_table.heading("kolom", text="kolom")
        self.m2_table.heading("isi", text="isi")
        self.m2_table.column("kolom", width=180, minwidth=120, anchor="w")
        self.m2_table.column("isi", width=500, minwidth=180, anchor="w")
        self.m2_table_scroll = ttk.Scrollbar(
            self.m2_table_frame, orient="vertical", command=self.m2_table.yview
        )
        self.m2_table.configure(yscrollcommand=self.m2_table_scroll.set)
        self.m2_table.pack(side="left", fill="both", expand=True)
        self.m2_table_scroll.pack(side="right", fill="y")
        command_frame = tk.LabelFrame(right, text="COMMAND / RIWAYAT AKSI",
                                      bg=BG, fg=GREEN_DARK, padx=5, pady=4)
        command_frame.pack(fill="x", padx=4, pady=(0, 2))
        self.command = tk.Text(command_frame, height=4, wrap="word",
                               font=("Consolas", 8), bg=PINK_LIGHT, fg=TEXT,
                               relief="flat")
        self.command.pack(fill="x")
    def clear_form(self):
        for child in self.form.winfo_children():
            child.destroy()
    def set_result(self, text):
        self.sort_table_frame.pack_forget()
        self.m2_table_frame.pack_forget()
        if not self.result.winfo_manager():
            self.result.pack(side="left", fill="both", expand=True)
        self.result.delete("1.0", "end")
        self.result.insert("end", text)
    def show_m2_details(self, summary, item=None, extra=None):
        """Tampilkan ringkasan operasi dan detail pesanan dalam tabel kolom/isi."""
        self.sort_table_frame.pack_forget()
        self.result.pack_forget()
        self.m2_table_frame.pack(fill="both", expand=True)
        self.m2_table.delete(*self.m2_table.get_children())
        if summary:
            self.m2_table.insert("", "end", values=("hasil operasi", summary))
        if item is not None:
            fields = [
                ("id", item[0] if len(item) > 0 else ""),
                ("pelanggan", item[1] if len(item) > 1 else ""),
                ("resto", item[2] if len(item) > 2 else ""),
                ("menu", item[3] if len(item) > 3 else ""),
                ("harga", "Rp" + str(item[4]) if len(item) > 4 else ""),
                ("prioritas", item[5] if len(item) > 5 else ""),
                ("masuk", item[6] if len(item) > 6 else ""),
                ("selesai", item[7] if len(item) > 7 and item[7] else "—"),
                ("status", item[8] if len(item) > 8 else ""),
            ]
            for key, value in fields:
                self.m2_table.insert("", "end", values=(key, value))
        for key, value in (extra or {}).items():
            self.m2_table.insert("", "end", values=(key, value))
    def show_sort_table(self, rows, limit=None):
        self.result.pack_forget()
        self.sort_table_frame.pack(fill="both", expand=True)
        self.sort_table.delete(*self.sort_table.get_children())
        shown = rows if limit is None else rows[:limit]
        for i, row in enumerate(shown, 1):
            self.sort_table.insert("", "end", values=(
                i, row[0], row[4], row[7] or "—", row[2], row[3]
            ))
    def log(self, text):
        if hasattr(self, "command"):
            self.command.insert("end", f"{time.strftime('%H:%M:%S')}  {text}\n")
            self.command.see("end")
    def show_page(self, action):
        self.current_action = action
        self.clear_form()
        self.title_label.config(text=action)
        self.description.config(text="Pilih operasi, isi parameter, lalu tekan tombol proses.")
        self.set_result("")
        self.ready.config(text="● siap")
        if action == "Load":
            self.description.config(text="Memuat data pesanan dari database/pesanan.csv.")
            ttk.Button(self.form, text="LOAD / MUAT ULANG DATA", command=self.reload_data).pack(anchor="w")
            self.show_data_preview("Data saat ini")
        elif action in ("M1 Lihat Array", "M1 Lihat Linked"):
            mode = "Array" if action.endswith("Array") else "Linked List"
            self.description.config(text=f"Cari pesanan berdasarkan ID pada {mode}.")
            self.make_entry("ID pesanan", "id")
            ttk.Button(self.form, text="CARI PESANAN", command=lambda m=mode: self.find_order(m)).pack(anchor="w", pady=5)
            self.show_rows()
        elif action.startswith("M1 Tambah") or action.startswith("LL Tambah"):
            if action.endswith("Reguler"):
                priority = 3
            elif action.endswith("Prioritas"):
                priority = 2
            else:
                priority = 1
            mode = "Linked List" if action.startswith("LL") else "Array"
            self.description.config(text=f"Tambah pesanan {self.priority_name(priority)} melalui {mode}.")
            self.make_entry("Nama pelanggan", "pelanggan")
            self.make_entry("Nama restoran", "resto")
            self.make_entry("Nama menu", "menu")
            self.make_entry("Harga (angka)", "harga")
            ttk.Button(self.form, text="TAMBAH PESANAN",
                       command=lambda p=priority, m=mode: self.add_order(p, m)).pack(anchor="w", pady=5)
        elif action.startswith("M1 Hapus"):
            mode = "Linked List" if action.endswith("Linked") else "Array"
            self.description.config(text=f"Hapus pesanan berdasarkan ID dari {mode}.")
            self.make_entry("ID pesanan", "id")
            ttk.Button(self.form, text="HAPUS PESANAN",
                       command=lambda m=mode: self.delete_order(m)).pack(anchor="w", pady=5)
            self.show_rows()
        elif action == "M2 Kalkulator":
            self.description.config(text="Masukkan ekspresi matematika. Contoh: (3*12000)+(2*8500)-5000")
            self.make_entry("Ekspresi infix", "expr", "(3*12000)+(2*8500)-5000")
            ttk.Button(self.form, text="KONVERSI & HITUNG", command=self.calculate).pack(anchor="w", pady=5)
        elif action == "M2 Enqueue":
            self.description.config(text="Masukkan nama pelanggan. Sistem membuat ID pesanan dan menambahkannya ke belakang kedua antrean.")
            self.make_entry("Nama pelanggan", "pelanggan")
            ttk.Button(self.form, text="ENQUEUE", command=self.enqueue).pack(anchor="w", pady=5)
            self.show_m2_details(
                f"Panjang antrean saat ini: {len(self.m2.naif):,}. Isi nama pelanggan lalu tekan ENQUEUE.",
                extra={"struktur": "Queue Naif + Queue Circular", "aksi": "menambahkan ke belakang"}
            )
        elif action in ("M2 Dequeue Naif", "M2 Dequeue Circular"):
            mode = "naif" if action.endswith("Naif") else "circular"
            self.description.config(text=f"Ambil pesanan paling depan menggunakan Queue {mode.title()}.")
            ttk.Button(self.form, text="DEQUEUE", command=lambda m=mode: self.dequeue(m)).pack(anchor="w", pady=5)
            self.show_m2_details(
                f"Panjang antrean: {len(self.m2.naif):,}. Tekan DEQUEUE untuk mengambil pesanan paling depan.",
                extra={"metode": "Queue " + mode.title(), "posisi pengambilan": "depan antrean"}
            )
        elif action in ("M2 Undo", "M2 Redo"):
            self.description.config(text="Kelola pembatalan aksi, pengulangan aksi, dan riwayat.")
            if action == "M2 Undo":
                ttk.Button(self.form, text="UNDO AKSI TERAKHIR", command=self.undo).pack(anchor="w")
            elif action == "M2 Redo":
                ttk.Button(self.form, text="REDO AKSI TERAKHIR", command=self.redo).pack(anchor="w")
        elif action in ("M3 Insertion", "M3 Merge"):
            mode = "insertion" if action.endswith("Insertion") else "merge"
            self.description.config(
                text="Setiap elemen diurutkan menurut parameter yang dipilih. "
                     "Pilih jumlah baris dan kunci pengurutan, lalu tekan URUTKAN."
            )
            controls = tk.Frame(self.form, bg=BG)
            controls.pack(fill="x", pady=3)
            tk.Label(controls, text="Jumlah baris diurutkan", bg=BG, fg=TEXT).grid(
                row=0, column=0, sticky="w", padx=(0, 8), pady=3
            )
            self.sort_count_var = tk.StringVar(value="10")
            ttk.Combobox(
                controls, textvariable=self.sort_count_var, state="readonly",
                values=("10", "100", "1000", "Semua"), width=10
            ).grid(row=0, column=1, sticky="w", padx=(0, 18), pady=3)
            tk.Label(controls, text="Diurutkan menurut", bg=BG, fg=TEXT).grid(
                row=0, column=2, sticky="w", padx=(0, 8), pady=3
            )
            self.sort_key_var = tk.StringVar(value="harga")
            ttk.Combobox(
                controls, textvariable=self.sort_key_var, state="readonly",
                values=("harga", "waktu selesai", "ID pesanan", "restoran", "menu"),
                width=16
            ).grid(row=0, column=3, sticky="w", pady=3)
            ttk.Button(
                controls, text="URUTKAN",
                command=lambda m=mode: self.run_sort(m)
            ).grid(row=0, column=4, sticky="w", padx=(18, 0), pady=3)
            self.set_result("Pilih jumlah baris dan parameter pengurutan, lalu tekan URUTKAN.")
            self.show_sort_table([])
        elif action in ("M3 Linear", "M3 Binary"):
            mode = "linear" if action.endswith("Linear") else "binary"
            self.description.config(text=f"Cari ID pesanan menggunakan {mode.title()} Search.")
            self.make_entry("ID pesanan", "target")
            ttk.Button(self.form, text="CARI", command=lambda m=mode: self.search(m)).pack(anchor="w", pady=5)
    def make_entry(self, label, key, default=""):
        line = tk.Frame(self.form, bg=BG)
        line.pack(fill="x", pady=2)
        tk.Label(line, text=label, bg=BG, fg=TEXT, width=20, anchor="w").pack(side="left")
        entry = ttk.Entry(line, width=42)
        entry.pack(side="left", fill="x", expand=True)
        if default:
            entry.insert(0, default)
        setattr(self, "entry_" + key, entry)
    @staticmethod
    def priority_name(priority):
        return "VIP" if priority == 1 else "PRIORITAS" if priority == 2 else "REGULER"
    def show_rows(self):
        self.set_result(f"Jumlah pesanan: {len(self.array)}\n\n")
        for row in self.array[:100]:
            self.result.insert("end", f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | Rp{row[4]} | {row[8]}\n")
        if len(self.array) > 100:
            self.result.insert("end", f"\n... {len(self.array) - 100} data lainnya tidak ditampilkan.")
    def show_data_preview(self, heading="Data pesanan"):
        """Tampilkan ringkasan dan sebagian data CSV di panel hasil."""
        total = len(self.array)
        limit = min(total, 100)
        lines = [
            f"{heading}: {total:,} pesanan.",
            f"Menampilkan {limit:,} data pertama agar UI tetap responsif.",
            "",
            f"{'NO.':<6} {'ID PESANAN':<14} {'PELANGGAN':<22} {'RESTORAN':<22} {'MENU':<26} {'HARGA':>12} {'STATUS':<12}",
            "-" * 120,
        ]
        for i, row in enumerate(self.array[:limit], 1):
            oid = row[0] if len(row) > 0 else ""
            pelanggan = row[1] if len(row) > 1 else ""
            resto = row[2] if len(row) > 2 else ""
            menu = row[3] if len(row) > 3 else ""
            harga = row[4] if len(row) > 4 else ""
            status = row[8] if len(row) > 8 else ""
            lines.append(f"{i:<6} {oid[:13]:<14} {pelanggan[:21]:<22} {resto[:21]:<22} {menu[:25]:<26} {harga:>12} {status[:11]:<12}")
        if total > limit:
            lines.extend(["", f"... {total - limit:,} pesanan lainnya tidak ditampilkan.",
                          "Gunakan M1 untuk mencari, atau gunakan Load untuk memuat ulang data."])
        self.set_result("\n".join(lines))
    def reload_data(self):
        try:
            self.rows = load_csv()
            self.array = self.rows.copy()
            self.linked = LinkedList()
            for row in self.rows:
                self.linked.append(row)
            self.queue = self.rows.copy()
            self.m2 = M2Manager(self.rows)
            self.queue_circular = self.m2.circular
            self.show_data_preview("Data berhasil dimuat")
            self.log(f"Load -> M1: Array + Linked List | {len(self.rows)} data")
            self.ready.config(text="● data loaded")
        except Exception as error:
            messagebox.showerror("Gagal memuat data", str(error))
    def add_order(self, priority, mode):
        try:
            customer = self.entry_pelanggan.get().strip()
            resto = self.entry_resto.get().strip()
            menu = self.entry_menu.get().strip()
            harga = int(self.entry_harga.get())
            if not customer or not resto or not menu or harga < 0:
                raise ValueError("Semua data harus diisi dan harga tidak boleh negatif.")
        except ValueError as error:
            messagebox.showerror("Input tidak valid", str(error))
            return
        largest = 0
        for row in self.array:
            if row[0].startswith("O-"):
                try:
                    largest = max(largest, int(row[0][2:]))
                except ValueError:
                    pass
        row = [f"O-{largest + 1:06d}", customer, resto, menu, str(harga),
               str(priority), str(time.time()), "", "ANTRE"]
        index = 0 if priority == 1 else len(self.array) // 2 if priority == 2 else len(self.array)
        if mode == "Array":
            self.array.insert(index, row)
            self.linked.insert(index, row)
        else:
            self.linked.insert(index, row)
            self.array.insert(index, row)
        self.set_result("Pesanan berhasil ditambahkan:\n\n" + " | ".join(row))
        self.log(f"M1 {mode} tambah {self.priority_name(priority)} {row[0]}")
        self.ready.config(text="● berhasil")
        messagebox.showinfo("Berhasil", f"Pesanan {row[0]} berhasil ditambahkan.")
    def find_order(self, mode):
        target = self.entry_id.get().strip()
        start = time.perf_counter()
        found = None
        if mode == "Array":
            for row in self.array:
                if row[0] == target:
                    found = row
                    break
        else:
            for i in range(self.linked.size):
                row = self.linked.get(i)
                if row[0] == target:
                    found = row
                    break
        elapsed = (time.perf_counter() - start) * 1000
        self.set_result(("Pesanan ditemukan:\n\n" + " | ".join(found) if found else "Pesanan tidak ditemukan.")
                        + f"\n\nWaktu {mode}: {elapsed:.4f} ms")
        self.log(f"M1 lihat/cari {mode} {target}: {elapsed:.4f} ms")
    def delete_order(self, mode):
        target = self.entry_id.get().strip()
        index = -1
        for i, row in enumerate(self.array):
            if row[0] == target:
                index = i
                break
        if index < 0:
            messagebox.showwarning("Tidak ditemukan", "ID pesanan tidak ditemukan.")
            return
        if not messagebox.askyesno("Konfirmasi", f"Hapus pesanan {target}?"):
            return
        start = time.perf_counter()
        self.array.pop(index)
        self.linked.delete(index)
        elapsed = (time.perf_counter() - start) * 1000
        self.set_result(f"Pesanan {target} berhasil dihapus.\nWaktu operasi: {elapsed:.4f} ms")
        self.log(f"M1 hapus {mode} {target}: {elapsed:.4f} ms")
    def calculate(self):
        try:
            expression = self.entry_expr.get().strip()
            tokens, postfix, trace1 = self.m2_infix_trace(expression)
            result, trace2 = self.m2_postfix_trace(postfix)
            lines = [
                f"Struk belanja (infix): {expression}",
                f"Token   : {tokens}",
                f"Postfix : {postfix}",
                f"TOTAL   : Rp{result:,.0f}",
                "",
                f"{'langkah':<9} {'token':<8} {'tindakan':<39} {'stack':<24} output",
                "-" * 115,
            ]
            for row in trace1 + trace2:
                lines.append(
                    f"{row['langkah']:<9} {row['token']:<8} "
                    f"{row['tindakan'][:38]:<39} {row['stack'][:23]:<24} {row['output']}"
                )
            self.set_result("\n".join(lines))
            self.log(f"stack_postfix -> M2 - stack | postfix={postfix} | total=Rp{result:,.0f}")
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Ekspresi tidak valid", str(error))
    @staticmethod
    def m2_infix_trace(expression):
        tokens = tokenize_expression(expression)
        stack, output, trace = [], [], []
        for step, token in enumerate(tokens, 1):
            if token.isdigit():
                output.append(token)
                action = "Angka langsung ke output"
            elif token == "(":
                stack.append(token)
                action = "Push '(' ke stack"
            elif token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Tanda kurung tidak sesuai")
                stack.pop()
                action = "Pop operator sampai '('"
            else:
                while stack and stack[-1] != "(":
                    p_top = 2 if stack[-1] in "*/" else 1
                    p_now = 2 if token in "*/" else 1
                    if p_top >= p_now:
                        output.append(stack.pop())
                    else:
                        break
                stack.append(token)
                action = "Pop operator sesuai prioritas, lalu push token"
            trace.append({
                "langkah": f"1.{step}", "token": token, "tindakan": action,
                "stack": " ".join(stack) if stack else "kosong",
                "output": " ".join(output) if output else "kosong",
            })
        while stack:
            if stack[-1] == "(":
                raise ValueError("Tanda kurung tidak sesuai")
            output.append(stack.pop())
            trace.append({
                "langkah": f"1.{len(trace)+1}", "token": "—",
                "tindakan": "Pop sisa operator ke output",
                "stack": " ".join(stack) if stack else "kosong",
                "output": " ".join(output),
            })
        return tokens, " ".join(output), trace
    @staticmethod
    def m2_postfix_trace(postfix):
        stack, trace = [], []
        for step, token in enumerate(postfix.split(), 1):
            if token.isdigit():
                stack.append(int(token))
                action = f"Push angka {token}"
            else:
                if len(stack) < 2:
                    raise ValueError("Ekspresi postfix tidak valid")
                b, a = stack.pop(), stack.pop()
                if token == "+":
                    value = a + b
                elif token == "-":
                    value = a - b
                elif token == "*":
                    value = a * b
                elif token == "/":
                    if b == 0:
                        raise ValueError("Tidak bisa membagi dengan nol")
                    value = a / b
                else:
                    raise ValueError("Operator tidak dikenal: " + token)
                stack.append(value)
                action = f"Hitung {a} {token} {b} = {value}"
            trace.append({
                "langkah": f"2.{step}", "token": token, "tindakan": action,
                "stack": " ".join(map(str, stack)) if stack else "kosong",
                "output": str(stack[-1]) if stack else "kosong",
            })
        if len(stack) != 1:
            raise ValueError("Ekspresi postfix tidak valid")
        return stack[0], trace
    def enqueue(self):
        customer = self.entry_pelanggan.get().strip()
        if not customer:
            messagebox.showerror("Input tidak valid", "Nama pelanggan wajib diisi.")
            return
        largest = 0
        for row in self.m2.naif.data:
            if row and str(row[0]).startswith("O-"):
                try:
                    largest = max(largest, int(str(row[0])[2:]))
                except ValueError:
                    pass
        oid = f"O-{largest + 1:06d}"
        now = str(time.time())
        row = [oid, customer, "kafe-teknik", "roti-bakar", "12000", "3", now, "", "ANTRE"]
        self.m2.enqueue(row)
        self.queue = self.m2.naif.data
        self.queue_circular = self.m2.circular
        self.undo_stack = self.m2.undo_stack
        self.redo_stack = self.m2.redo_stack
        queue_length = len(self.m2.naif)
        self.show_m2_details(
            f"{oid} masuk ke bagian paling belakang pada KEDUA antrean. Panjang sekarang: {queue_length:,}.",
            item=row,
            extra={
                "aksi": "ENQUEUE",
                "posisi": f"belakang (urutan ke-{queue_length:,})",
                "panjang queue naif": f"{len(self.m2.naif):,}",
                "panjang queue circular": f"{len(self.m2.circular):,}",
            }
        )
        self.log(f"M2 queue_enqueue -> {oid} | pelanggan={customer} | panjang={queue_length:,}")
        self.ready.config(text="● enqueue berhasil")
    def dequeue(self, mode):
        before = len(self.m2.naif)
        start = time.perf_counter()
        item, elapsed, shifts = self.m2.dequeue(mode)
        self.queue = self.m2.naif.data
        self.queue_circular = self.m2.circular
        if item is None:
            messagebox.showinfo("Antrean kosong", "Tidak ada pesanan di antrean.")
            self.show_m2_details("Antrean kosong. Tidak ada pesanan yang dapat dikeluarkan.")
            return
        after = len(self.m2.naif)
        self.show_m2_details(
            f"Pesanan {item[0]} berhasil diambil dari depan Queue {mode.title()}. Panjang antrean: {before:,} → {after:,}.",
            item=item,
            extra={
                "aksi": "DEQUEUE " + mode.upper(),
                "panjang sebelum": f"{before:,}",
                "panjang sesudah": f"{after:,}",
                "elemen bergeser (naif)": shifts,
                "waktu operasi": f"{elapsed:.4f} ms",
            }
        )
        self.log(f"M2 queue_dequeue_{mode} -> {item[0]} | {elapsed:.4f} ms | sisa={after:,}")
        self.ready.config(text="● dequeue berhasil")
    def undo(self):
        if not self.m2.undo():
            messagebox.showinfo("Undo", "Belum ada aksi yang bisa dibatalkan.")
            return
        self.queue = self.m2.naif.data
        self.queue_circular = self.m2.circular
        self.show_m2_details(
            f"Undo berhasil. Panjang antrean sekarang: {len(self.m2.naif):,}.",
            extra={"aksi": "UNDO", "undo depth": len(self.m2.undo_stack), "redo depth": len(self.m2.redo_stack)}
        )
        self.log(f"M2 undo berhasil | panjang={len(self.m2.naif):,}")
    def redo(self):
        if not self.m2.redo():
            messagebox.showinfo("Redo", "Tidak ada aksi untuk diulang.")
            return
        self.queue = self.m2.naif.data
        self.queue_circular = self.m2.circular
        self.show_m2_details(
            f"Redo berhasil. Panjang antrean sekarang: {len(self.m2.naif):,}.",
            extra={"aksi": "REDO", "undo depth": len(self.m2.undo_stack), "redo depth": len(self.m2.redo_stack)}
        )
        self.log(f"M2 redo berhasil | panjang={len(self.m2.naif):,}")
    def run_sort(self, mode):
        rows = self.array.copy()
        if not rows:
            self.set_result("Data masih kosong. Klik Load / Muat Ulang Data terlebih dahulu.")
            return
        count_choice = getattr(self, "sort_count_var", None)
        count_choice = count_choice.get() if count_choice else "10"
        if count_choice == "Semua":
            selected_rows = rows
        else:
            selected_rows = rows[:min(int(count_choice), len(rows))]
        key_choice = getattr(self, "sort_key_var", None)
        key_choice = key_choice.get() if key_choice else "harga"
        key_columns = {
            "harga": 4, "waktu selesai": 7, "ID pesanan": 0,
            "restoran": 2, "menu": 3
        }
        column = key_columns.get(key_choice, 4)
        if mode == "insertion" and len(selected_rows) > 10000:
            lanjut = messagebox.askyesno(
                "Insertion Sort akan lama",
                f"Ada {len(selected_rows):,} data. Insertion Sort memiliki kompleksitas O(n²). "
                "Tetap jalankan?\n\nPilih No untuk membatalkan atau pilih Merge Sort."
            )
            if not lanjut:
                self.set_result("Insertion Sort dibatalkan. Gunakan Merge Sort untuk data besar.")
                return
        self.set_result(f"M3 {mode.title()} Sort sedang berjalan untuk {len(selected_rows):,} data...")
        self.ready.config(text="● M3 sedang proses")
        threading.Thread(
            target=self._sort_worker,
            args=(mode, selected_rows, column, key_choice),
            daemon=True
        ).start()
    def _sort_worker(self, mode, rows, column, key_choice):
        comparisons = 0
        start = time.perf_counter()
        if mode == "insertion":
            for i in range(1, len(rows)):
                key = rows[i]
                j = i - 1
                while j >= 0:
                    comparisons += 1
                    if self._sort_key(rows[j], column) > self._sort_key(key, column):
                        rows[j + 1] = rows[j]
                        j -= 1
                    else:
                        break
                rows[j + 1] = key
        else:
            rows, comparisons = self.merge_sort(rows, column)
        elapsed = (time.perf_counter() - start) * 1000
        result_text = (
            f"{len(rows):,} pesanan diurutkan menurut {key_choice}. "
            f"{comparisons:,} perbandingan, {elapsed:.4f} ms."
        )
        def finish():
            self.show_sort_table(rows)
            self.log(
                f"M3 {mode.title()} Sort menurut {key_choice}: "
                f"{comparisons:,} perbandingan, {elapsed:.4f} ms"
            )
            self.ready.config(text="● siap")
            self.description.config(text=result_text)
        self.after(0, finish)
    @staticmethod
    def _sort_key(row, column):
        value = row[column] if column < len(row) else ""
        if column == 4:
            try:
                return (0, float(value))
            except (TypeError, ValueError):
                return (1, 0)
        if column == 7:
            if value == "":
                return (1, 0)
            try:
                return (0, float(value))
            except (TypeError, ValueError):
                return (0, str(value))
        return str(value).casefold()
    @staticmethod
    def merge_sort(rows, column):
        comparisons = [0]
        def sort(items):
            if len(items) <= 1:
                return items
            mid = len(items) // 2
            left, right = sort(items[:mid]), sort(items[mid:])
            merged, i, j = [], 0, 0
            while i < len(left) and j < len(right):
                comparisons[0] += 1
                if App._sort_key(left[i], column) <= App._sort_key(right[j], column):
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
            return merged
        return sort(rows), comparisons[0]
    def search(self, mode):
        target = self.entry_target.get().strip()
        rows = self.array
        if not rows:
            self.set_result("Data masih kosong. Klik Load / Muat Ulang Data terlebih dahulu.")
            return
        if not target:
            messagebox.showwarning("ID kosong", "Masukkan ID pesanan, contoh O-000001.")
            return
        comparisons = 0
        start = time.perf_counter()
        if mode == "linear":
            index = -1
            for i, row in enumerate(rows):
                comparisons += 1
                if row[0] == target:
                    index = i
                    break
        else:
            rows, _ = self.merge_sort(rows.copy(), 0)
            left, right, index = 0, len(rows) - 1, -1
            while left <= right:
                mid = (left + right) // 2
                comparisons += 1
                if rows[mid][0] == target:
                    index = mid
                    break
                if rows[mid][0] < target:
                    left = mid + 1
                else:
                    right = mid - 1
        elapsed = (time.perf_counter() - start) * 1000
        if index >= 0:
            row = rows[index]
            detail = (f"\n\nID: {row[0]}\nPelanggan: {row[1]}\nRestoran: {row[2]}"
                      f"\nMenu: {row[3]}\nHarga: Rp{row[4]}\nStatus: {row[8]}")
        else:
            detail = "\n\nPesanan tidak ditemukan."
        self.set_result(f"{mode.title()} Search\nTarget: {target}\n"
                        f"Perbandingan: {comparisons}\nWaktu: {elapsed:.4f} ms{detail}")
        self.log(f"M3 {mode.title()} Search {target}: {comparisons} perbandingan, {elapsed:.4f} ms")
def main():
    app = App()
    app.mainloop()
if __name__ == "__main__":
    main()
