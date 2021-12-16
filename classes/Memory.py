from multipledispatch import dispatch


class Memory:

    def __init__(self, pages=1):

        self.pages = pages
        self.page_cursor = 0
        self.__offsets = 65536  # 64K for page.
        self.memory = [[0b00000000] * self.__offsets] * self.pages

    def __str__(self):
        return str(self.pages) + " * " + str(self.__offsets)

    @dispatch(int, int)
    def peek(self, page, address):

        if int(page) < 0 or int(page) >= len(self.memory) or \
                int(address) < 0 or int(page) >= self.__offsets:
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
                address > self.__offsets or address < 0:
            print("Memory.poke(): Value error.")
            return -1
        else:
            self.page_cursor = page
            self.memory[page][address] = value

    @dispatch(int, int)
    def display(self, addrb, addrn):

        page = self.page_cursor

        for a in range(addrb, addrn, 15):
            ascvisual = ""
            print(f"{'%04X' % self.page_cursor}:{'%04X' % a} ", end="", flush=True)

            for b in range(0, 15):
                byte = self.peek(page, a + b)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)

            print(" " + ascvisual)

        print("")

    @dispatch(int, int, str)
    def load_into(self, page, start, text):
        for idx in range(0, len(text) - 1):
            self.poke(page, start + idx, ord(text[idx]))

