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
    def compare(self, cfrom, cend, cto):
        diffs = []

        for a in range(cfrom, cend):
            org = self.peek(self.active_page, a)
            dist_pointer = cfrom if cto + a == cfrom else cto + a - cfrom - 1

            dist = self.peek(self.active_page, dist_pointer)
            if org != dist:
                diffs.append('%04X' % self.active_page + ":" + '%04X' % a + " " +
                             '%02X' % org + " " + '%02X' % dist + " " +
                             '%04X' % self.active_page + ":" + '%04X' % dist_pointer)

        return diffs

    @dispatch(int, int, int)
    def move(self, from_begin, from_end, destination):
        if destination > from_end:
            for source in range(from_begin, from_end):
                dist_pointer = from_begin \
                    if destination + source == from_begin else destination + source - from_begin - 1
                self.poke(self.active_page, dist_pointer, self.peek(self.active_page, source))
                print(f"{from_end - from_begin} byte/s copied.")
        else:
            print("Invalid value.")

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

    @dispatch(int, int)
    def display(self, addrb, addrn):
        page = self.active_page
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            print(f"{'%04X' % self.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = self.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)

            print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    print(f"{'%04X' % self.active_page}:{'%04X' % (pointer + addrb)} ", end="", flush=True)

                byte = self.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                print(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    @dispatch(int, int, str)
    def fill(self, start, end, pattern):
        cursor = 0
        for idx in range(start, end):
            self.poke(self.active_page, idx, ord(pattern[cursor]))
            cursor += 1
            if cursor > len(pattern) - 1:
                cursor = 0

    @dispatch(int, str)
    def search(self, start, pattern):
        found_list = []
        pointer = start
        while pointer < self._offsets:
            idx = 0

            # Did I find the first char of the pattern? If so, let's search for the rest
            if self.peek(self.active_page, pointer) == ord(pattern[idx]):
                pointer_aux = pointer
                while idx < len(pattern) and pointer_aux < self._offsets and \
                        self.peek(self.active_page, pointer_aux) == ord(pattern[idx]):
                    idx += 1
                    pointer_aux += 1

                if pointer_aux - pointer == len(pattern):
                    found_list.append(f"{'%04X' % self.active_page}:{'%04X' % pointer}")

            pointer += 1

        return found_list

    @dispatch(int, int, str)
    def load_into(self, page, start, text):
        for idx in range(0, len(text) - 1):
            self.poke(page, start + idx, ord(text[idx]))
