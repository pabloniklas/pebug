from multipledispatch import dispatch


class Memory:

    def __init__(self, pages=1):
        self.pages = pages
        self._offset_cursor = 0
        self.active_page = 49152  # Like the old one C000
        self._offsets = 65536  # 64K for page.
        self.memory = [[0b00000000] * self._offsets] * self.pages

    def __str__(self):
        return str(self.pages) + " * " + str(self._offsets)

    @dispatch(int)
    def peek(self, address):
        page = self.active_page
        return self.peek(page, address)

    @dispatch(int, int)
    def peek(self, page, address):
        if int(page) < 0 or int(page) >= len(self.memory) or \
                int(address) < 0 or int(page) >= self._offsets:
            print("Memory.peek(): Invalid address.")
            return -1
        else:
            self.active_page = page
            return self.memory[int(page)][int(address)]

    @dispatch(str, str)
    def peek(self, page, address):
        return self.peek(int(page, 16), int(address, 16))

    @dispatch(int, int, int)
    def poke(self, page, address, value):
        if value < 0 or value > 255 or \
                page < 0 or page >= len(self.memory) or \
                address > self._offsets or address < 0:
            print("Memory.poke(): Invalid address or value.")
            return -1
        else:
            self.active_page = page
            self.memory[page][address] = value
