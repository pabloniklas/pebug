from multipledispatch import dispatch


class Memory:

    def __init__(self, pages=1):

        self.pages = pages
        self.page_cursor = 0
        self._offsets = 65536  # 64K for page.
        self.memory = [[0b00000000] * self._offsets] * self.pages

    def __str__(self):
        return str(self.pages) + " * " + str(self._offsets)

    @dispatch(int, int)
    def peek(self, page, address):

        if int(page) < 0 or int(page) >= len(self.memory) or \
                int(address) < 0 or int(page) >= self._offsets:
            print("Memory.peek(): Value error.")
            return -1
        else:
            self.page_cursor = page
            return self.memory[int(page)][int(address)]

    @dispatch(str, str)
    def peek(self, page, address):
        return self.peek(int(page, 16), int(address, 16))

    @dispatch(int, int, int)
    def poke(self, page, address, value):

        if value < 0 or value > 255 or \
                page < 0 or page >= len(self.memory) or \
                address > self._offsets or address < 0:
            print("Memory.poke(): Value error.")
            return -1
        else:
            self.page_cursor = page
            self.memory[page][address] = value

    @dispatch(int, int)
    def display(self, addrb, addrn):

        page = self.page_cursor
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row: # One single row
            print(f"{'%04X' % self.page_cursor}:{'%04X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = self.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)

            print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else: # two or more rows
            while (pointer + addrb < addrn):
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    print(f"{'%04X' % self.page_cursor}:{'%04X' % (pointer + addrb)} ", end="", flush=True)

                byte = self.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    @dispatch(int, int, str)
    def load_into(self, page, start, text):
        for idx in range(0, len(text) - 1):
            self.poke(page, start + idx, ord(text[idx]))
