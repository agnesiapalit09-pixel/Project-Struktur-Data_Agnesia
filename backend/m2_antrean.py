import time

def tokenize_expression(expression):
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
                raise ValueError(f"Karakter tidak dikenal: {char}")
    if number:
        tokens.append(number)
    if not tokens:
        raise ValueError("Ekspresi tidak boleh kosong")
    return tokens

def infix_to_postfix(expression):
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
                top_priority = 2 if stack[-1] in "*/" else 1
                current_priority = 2 if token in "*/" else 1
                if top_priority >= current_priority:
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
            "langkah": f"1.{len(trace)+1}", "token": "—", "tindakan": "Pop sisa operator ke output", "stack": " ".join(stack) if stack else "kosong", "output": " ".join(output),
        })
    return tokens, " ".join(output), trace

def evaluate_postfix(postfix):
    stack, trace = [], []
    for step, token in enumerate(postfix.split(), 1):
        if token.lstrip("-").isdigit():
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
                raise ValueError(f"Operator tidak dikenal: {token}")
            stack.append(value)
            action = f"Hitung {a} {token} {b} = {value}"
        trace.append({
            "langkah": f"2.{step}", "token": token, "tindakan": action, "stack": " ".join(map(str, stack)) if stack else "kosong", "output": str(stack[-1]) if stack else "kosong",
        })
    if len(stack) != 1:
        raise ValueError("Ekspresi postfix tidak valid")
    return stack[0], trace


class QueueNaif:
    def __init__(self, items=None):
        self.data = list(items or [])

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        return self.data.pop(0) if self.data else None

    def __len__(self):
        return len(self.data)


class QueueCircular:
    def __init__(self, capacity=4):
        self.data = [None] * max(1, capacity)
        self.front = self.rear = self.count = 0

    def __len__(self):
        return self.count

    def _resize(self):
        expanded = [None] * (len(self.data) * 2)
        for i in range(self.count):
            expanded[i] = self.data[(self.front + i) % len(self.data)]
        self.data = expanded
        self.front, self.rear = 0, self.count

    def enqueue(self, item):
        if self.count == len(self.data):
            self._resize()
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % len(self.data)
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % len(self.data)
        self.count -= 1
        return item

    def items(self):
        return [self.data[(self.front + i) % len(self.data)] for i in range(self.count)]

class M2Manager:
    def __init__(self, items=None):
        initial = list(items or [])
        self.naif = QueueNaif(initial)
        self.circular = QueueCircular()
        for item in initial:
            self.circular.enqueue(item)
        self.undo_stack, self.redo_stack, self.history = [], [], []

    def enqueue(self, item):
        self.naif.enqueue(item)
        self.circular.enqueue(item)
        self.undo_stack.append(("enqueue", item))
        self.redo_stack.clear()
        self.history.append(f"ENQUEUE {item[0]}")

    def dequeue(self, mode="naif"):
        start = time.perf_counter()
        item = self.naif.dequeue() if mode == "naif" else self.circular.dequeue()
        elapsed = (time.perf_counter() - start) * 1000
        if item is None:
            return None, elapsed, 0
        if mode == "naif":
            self.circular.dequeue()
            shifts = len(self.naif)
        else:
            self.naif.dequeue()
            shifts = 0
        self.undo_stack.append(("dequeue", item))
        self.redo_stack.clear()
        self.history.append(f"DEQUEUE {mode.upper()} {item[0]}")
        return item, elapsed, shifts

    def _sync_circular(self):
        self.circular = QueueCircular()
        for item in self.naif.data:
            self.circular.enqueue(item)

    def undo(self):
        if not self.undo_stack:
            return False
        action, item = self.undo_stack.pop()
        if action == "enqueue":
            for i in range(len(self.naif.data) - 1, -1, -1):
                if self.naif.data[i][0] == item[0]:
                    self.naif.data.pop(i)
                    break
        else:
            self.naif.data.insert(0, item)
        self._sync_circular()
        self.redo_stack.append((action, item))
        self.history.append(f"UNDO {action.upper()} {item[0]}")
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        action, item = self.redo_stack.pop()
        if action == "enqueue":
            self.naif.enqueue(item)
        else:
            if self.naif.data:
                self.naif.data.pop(0)
        self._sync_circular()
        self.undo_stack.append((action, item))
        self.history.append(f"REDO {action.upper()} {item[0]}")
        return True

def print_queue(manager):
    print("\n--- ISI ANTREAN ---")
    if not manager.naif.data:
        print("Antrean kosong.")
    else:
        for i, row in enumerate(manager.naif.data, 1):
            print(f"{i}. {row[0]} | {row[1]} | {row[2]} | {row[3]} | Rp{row[4]}")
    print(f"Jumlah pesanan: {len(manager.naif)}")


def menu_postfix():
    print("\n=== STACK: INFIX KE POSTFIX ===")
    expression = input("Masukkan ekspresi (contoh: (3 * 12000) + (2 * 8500) - 5000): ").strip()
    try:
        tokens, postfix, trace1 = infix_to_postfix(expression)
        total, trace2 = evaluate_postfix(postfix)
    except ValueError as exc:
        print("Input tidak valid:", exc)
        return

    print("\nToken  :", tokens)
    print("Postfix:", postfix)
    print("Total  : Rp{:,.2f}".format(total) if isinstance(total, float) and not total.is_integer()
          else "Total  : Rp{:,.0f}".format(total))
    print("\nTabel langkah:")
    print(f"{'langkah':<9} {'token':<8} {'stack':<25} {'output':<30} tindakan")
    print("-" * 110)
    for row in trace1 + trace2:
        print(f"{row['langkah']:<9} {row['token']:<8} {row['stack']:<25} "
              f"{row['output']:<30} {row['tindakan']}")

def menu_enqueue(manager):
    print("\n=== QUEUE: ENQUEUE ===")
    oid = input("ID pesanan: ").strip()
    pelanggan = input("Nama pelanggan: ").strip()
    resto = input("Nama restoran: ").strip()
    menu = input("Nama menu: ").strip()
    try:
        harga = int(input("Harga (angka saja, contoh 15000): "))
        if not all([oid, pelanggan, resto, menu]) or harga < 0:
            raise ValueError
    except ValueError:
        print("Input tidak valid. Pastikan semua kolom terisi dan harga tidak negatif.")
        return
    item = [oid, pelanggan, resto, menu, str(harga), "3", str(time.time()), "", "ANTRE"]
    manager.enqueue(item)
    print(f"Pesanan {oid} berhasil masuk ke antrean.")
    print_queue(manager)


def menu_dequeue(manager, mode):
    item, elapsed, shifts = manager.dequeue(mode)
    if item is None:
        print("\nAntrean kosong, tidak ada pesanan untuk dikeluarkan.")
        return
    print(f"\n=== QUEUE: DEQUEUE {mode.upper()} ===")
    print(f"Pesanan keluar : {item[0]}")
    print(f"Pelanggan      : {item[1]}")
    print(f"Restoran       : {item[2]}")
    print(f"Menu           : {item[3]}")
    print(f"Harga          : Rp{item[4]}")
    print(f"Elemen bergeser: {shifts}")
    print(f"Waktu operasi  : {elapsed:.4f} ms")
    print_queue(manager)

def test_print():
    expression = "(3 * 12000) + (2 * 8500) - 5000"
    tokens, postfix, trace1 = infix_to_postfix(expression)
    total, trace2 = evaluate_postfix(postfix)
    print("=== TEST OTOMATIS M2 ===")
    print("Infix  :", expression)
    print("Token  :", tokens)
    print("Postfix:", postfix)
    print("Total  : Rp{:,.0f}".format(total))
    print("\nLangkah Stack:")
    print(f"{'langkah':<9} {'token':<8} {'stack':<25} {'output':<30} tindakan")
    for row in trace1 + trace2:
        print(f"{row['langkah']:<9} {row['token']:<8} {row['stack']:<25} {row['output']:<30} {row['tindakan']}")

def main():
    manager = M2Manager()
    while True:
        print("\n" + "=" * 42)
        print(" MENU M2 STACK & QUEUE")
        print("=" * 42)
        print("1. Stack - Hitung struk (Infix/Postfix)")
        print("2. Queue - Enqueue pesanan")
        print("3. Queue - Dequeue naif")
        print("4. Queue - Dequeue circular")
        print("5. Stack - Undo")
        print("6. Stack - Redo")
        print("7. Lihat isi antrean")
        print("8. Lihat history aksi")
        print("0. Keluar")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            menu_postfix()
        elif pilihan == "2":
            menu_enqueue(manager)
        elif pilihan == "3":
            menu_dequeue(manager, "naif")
        elif pilihan == "4":
            menu_dequeue(manager, "circular")
        elif pilihan == "5":
            if manager.undo():
                print("Undo berhasil.")
                print_queue(manager)
            else:
                print("Belum ada aksi yang bisa di-undo.")
        elif pilihan == "6":
            if manager.redo():
                print("Redo berhasil.")
                print_queue(manager)
            else:
                print("Belum ada aksi yang bisa di-redo.")
        elif pilihan == "7":
            print_queue(manager)
        elif pilihan == "8":
            print("\n=== HISTORY M2 ===")
            if manager.history:
                for i, action in enumerate(manager.history, 1):
                    print(f"{i}. {action}")
            else:
                print("Belum ada history.")
        elif pilihan == "0":
            print("Program M2 selesai.")
            break
        else:
            print("Pilihan tidak valid, masukkan angka 0-9.")

if __name__ == "__main__":
    main()
