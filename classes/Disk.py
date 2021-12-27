from multipledispatch import dispatch


class Disk:

    @dispatch(int, str)
    def __init__(self, size, filename):
        self._filename = filename
        self._size = size
        self._disk = 0b0 * self._size

    @property
    def size(self):
        return self._size

    @property
    def filename(self):
        return self._filename

    @dispatch(int, int)
    def write(self, sector, value):
        if sector < 0 or sector > self._size - 1:
            print("Invalid sector.")
            return
        elif value < 0 or value > 255:
            print("Invalid value.")
            return
        else:
            self._disk[sector] = value

    @dispatch(int)
    def read(self, sector):
        if sector < 0 or sector > self._size - 1:
            print("Invalid sector.")
            return -1
        else:
            return self._disk[sector]

    def load(self):
        f = open(self._filename, 'rb')
        content = f.read()
        f.close()
        for i in range(0, len(content) - 1):
            self._disk[i] = content[i]

    def save(self):
        f = open(self._filename, 'w+b')
        binary_format = bytearray(self._disk)
        f.write(binary_format)
        f.close()
