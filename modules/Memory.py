import logging

from multipledispatch import dispatch

logging.basicConfig(level=logging.WARNING)

class Memory:
    """
    Class emulating paginated memory bank.

    Methods:
        peek: Retrieve the content of a memory address.
        poke: Write a value to a memory address.
    """

    def __init__(self, pages: int = 1):
        self.pages = pages
        self.offset_cursor = 0
        self.active_page = 49152  # Like the old C000
        self._offsets = 65536  # 64K per page
        self._memory = [[0b00000000] * self._offsets for _ in range(self.pages)]

    def __str__(self) -> str:
        """Overload of the str() function.

        Returns:
            str: A string with the memory pages and offsets.
        """
        return f"{self.pages} * {self._offsets}"

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
        return self.peek(self.active_page, address)
    
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
        try:
            return self.peek(int(page, 16), int(address, 16))
        except ValueError:
            logging.warning("Memory.peek(): Invalid hexadecimal address or page.")
            return -1
    
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
        if not (0 <= value <= 255) or not (0 <= page < len(self._memory)) or not (0 <= address < self._offsets):
            logging.warning("Memory.poke(): Invalid address or value.")
            return False
        self._memory[page][address] = value
        return True