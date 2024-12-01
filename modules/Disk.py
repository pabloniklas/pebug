import os

class Disk:
    """
    Class emulating a Disk.
    """

    def __init__(self, size, filename):
        """
        Class constructor. Initialize the vdisk object.

        Args:
            size (int): Size in bytes of the vdisk.
            filename (str): Real filename of the vdisk in the filesystem.
        """
        self._filename = os.path.join(os.path.expanduser("~"), "." + filename)
        self._size = size
        self._disk = [0b00000000] * self._size


    def __str__(self) -> str:
        """Overload of the str() function.

        Returns:
            str: A string with the filename and size of the disk.
        """
        return f"Filename: {self._filename} // Size: {self._size} bytes."

    def size(self) -> int:
        """Size of the virtual disk.

        Returns:
            int: Size in bytes of the virtual disk.
        """
        return self._size

    def filename(self, name: str) -> None:
        """Set the filename of the virtual disk.

        Args:
            name (str): Name of the file.
        """
        
        self._filename = name

    def write(self, sector: int, value: int) -> bool:
        """Write bytes to the virtual disk.

        Args:
            sector:  Sector where the byte is written.
            value: The byte to be written.

        Returns:
            bool: True if successful, False if not.

        """

        if sector < 0 or sector > self._size - 1:
            print("Invalid sector.")
            return False
        elif value < 0 or value > 255:
            print("Disk.write(): Invalid value.")
            return False
        else:
            self._disk[int(sector)] = value
            return True

    def read(self, sector: int) -> int:
        """Read a virtual disk sector.

        Parameters:
            sector (int): Sector to be read.

        Returns:
            int: the read byte or -1 if there were any problem.
        """
        if sector < 0 or sector > self._size - 1:
            print("Disk.read(): Invalid sector.")
            return -1
        else:
            return self._disk[int(sector)]

    def load(self) -> bool:
        """Load the virtual disk from a real file.

        Returns:
            bool: True if was successful, False if not,
        """
        try:
            with open(self._filename, 'rb') as f:
                content = f.read()
        except IOError:
            print(f"Disk.load(): Problem accessing {self._filename}")
            return False

        for i, value in enumerate(content):
            self._disk[i] = value
        return True


    def save(self) -> bool:
        """Save the virtual disk to a real file.

        Returns:
            bool: True if was successful, False if not.
        """
        try:
            with open(self._filename, 'w+b') as f:
                binary_format = bytearray(self._disk)
                bytes_written = f.write(binary_format)

            if bytes_written == self._size:
                print("Active page saved to:", self._filename)
                print("Size:", len(binary_format))
                return True
            else:
                print(f"Error: Expected to write {self._size} bytes, but only wrote {bytes_written} bytes.")
                return False

        except IOError:
            print(f"Disk.save(): Problem accessing {self._filename}")
            return False
