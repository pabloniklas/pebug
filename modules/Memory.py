from multipledispatch import dispatch


class Memory:
    """
    Class emulating paginated memory bank.

    Methods:
        peek: Retrieve the content of a memory address.
        poke: Write a value to a memory address.
    """

    def __init__(self, pages=1):
        self.pages = pages
        self.offset_cursor = 0
        self.active_page = 49152  # Like the old one C000
        self._offsets = 65536  # 64K for page.
        self._memory = [[0b00000000] * self._offsets] * self.pages

    def __str__(self):
        return str(self.pages) + " * " + str(self._offsets)

    @dispatch(int)
    def peek(self, address: int) -> int:
        """
        peek(self, address: int) -> int
        Retrieve the content of a memory address.

        Parameters:
            address (int): Address where to peek.

        Returns:
            int: Pointed address value.
        """
        page = self.active_page
        return self.peek(page, address)

    @dispatch(int, int)
    def peek(self, page: int, address: int) -> int:
        """
        peek(self, page: int, address: int) -> int
        Retrieve the content of a memory address.

        Parameters:
            page (int): Page memory.
            address (int): Address where to peek.

        Returns:
            int: Pointed address value.
        """
        if int(page) < 0 or int(page) >= len(self._memory) or \
                int(address) < 0 or int(page) >= self._offsets:
            print("Memory.peek(): Invalid address.")
            return -1
        else:
            self.active_page = page
            return self._memory[int(page)][int(address)]

    @dispatch(str, str)
    def peek(self, page: str, address: str) -> int:
        """
        peek(self, page: str, address: str) -> int
        Retrieve the content of a memory address.

        Parameters:
            page (str): Page memory in hexadecimal.
            address (str): Address where to peek in hexadecimal.

        Returns:
            int: Pointed address value.
        """
        return self.peek(int(page, 16), int(address, 16))

    @dispatch(int, int, int)
    def poke(self, page: int, address: int, value: int) -> bool:
        """
        poke(self, page: int, address: int, value: int) -> bool
        Write a value to a memory address.

        Parameters:
            page (int): Page memory.
            address (int): Address where to poke.
            value (int): Value to set in memory.

        Returns:
            bool: Operation result.
        """
        if value < 0 or value > 255 or \
                page < 0 or page >= len(self._memory) or \
                address > self._offsets or address < 0:
            print("Memory.poke(): Invalid address or value.")
            return False
        else:
            self.active_page = page
            self._memory[page][address] = value
            return True
