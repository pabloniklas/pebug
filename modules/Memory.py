
from multipledispatch import dispatch

if __name__ is not None and "." in __name__:
    from .Terminal import Terminal
else:
    from Terminal import Terminal

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
        self.active_page = 0
        self._offsets = 65536  # 64K per page
        self._memory = [[0b00000000] * self._offsets for _ in range(self.pages)]
        self.terminal = Terminal()

    def __str__(self) -> str:
        """Overload of the str() function.

        Returns:
            str: A string with the memory pages and offsets.
        """
        return f"{self.pages} * {self._offsets}"
    
    def get_num_memory_pages(self) -> int:
        """Get the number of memory pages.

        Returns:
            int: Number of memory pages.
        """
        return self.pages
    
    def get_num_memory_offsets(self) -> int:
        """Get the memory offsets.

        Returns:
            int: Memory offsets.
        """
        return self._offsets

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
            return self._memory[page][address]
        except (ValueError, IndexError):
            self.terminal.warning_message("Memory.peek(): Invalid hexadecimal address or page.")
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
            self.terminal.warning_message(f"Memory.poke(): Invalid address or value. {page}/{len(self._memory)}:{address}/{self._offsets}, {value}")
            return False
        self._memory[page][address] = value
        return True
    
    @dispatch(int, int, str)
    def poke(self, page: int, address: int, value: str) -> bool:
        """
        poke(self, page: int, address: int, value: str) -> bool
        Write a string to memory as a sequence of bytes.

        Parameters:
            page (int): Page memory.
            address (int): Address where to start writing.
            value (str): String to write as bytes.

        Returns:
            bool: Operation result.
        """
        if not (0 <= page < len(self._memory)) or not (0 <= address < self._offsets):
            self.terminal.warning_message(f"Memory.poke(): Invalid page/address. {page}/{len(self._memory)}:{address}/{self._offsets}")
            return False

        byte_values = value.encode("latin1")  # 1 byte per char; avoids utf-8 multibyte issues
        if address + len(byte_values) > self._offsets:
            self.terminal.warning_message(f"Memory.poke(): String too long for address range. {address} + {len(byte_values)} > {self._offsets}")
            return False

        for i, byte in enumerate(byte_values):
            self._memory[page][address + i] = byte

        return True
