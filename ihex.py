
class iHEXParseException(Exception):
    pass

class iHEXEndOfFile(Exception):
    pass


class iHEX(object):
    def __init__(self, contents):
        """ Parse contents as a string containing an ihex file. """
        self.memory = {}
        self.last_address = None
        self.last_region = None
        self._parse_string(contents)


    def regions(self): # TODO: Return actual data?
        """ Return all known memory regions, identified by their start address."""
        k = self.memory.keys()
        k.sort() # Sort the list in order to program up and not randomly
        return k

    def get_region(self, region):
        """ Return the data in the form of a str(), identified by its start address."""
        return self.memory[region]

    def _memory_add(self, rectype, address, pdata):
        if rectype != 0:
            return # Extended not yet supported

        if address != self.last_address:
            # New memory region
            self.memory[address] = []
            self.last_region = self.memory[address]
        self.last_region.append(pdata)
        self.last_address = address + len(pdata)


    def _memory_join(self):
        for addr in self.memory.keys():
            self.memory[addr] = ''.join(self.memory[addr])

    def _parse_line(self, line):
        if len(line) < 4:
            raise iHEXEndOfFile()
        if line[0] != ':':
            raise iHEXParseException("Start character invalid: %r" % line)
        # Calculate CRC

        crc = 0
        for bytenum in range(1, (len(line)-1) , 2):
            crc += int(line[bytenum] + line[bytenum+1], 16)
        crc &= 0xFF
        if crc != 0:
            raise iHEXParseException("CRC in file failed")

        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        rectype = int(line[7:9], 16)
        data = line[9:-2]

        pdata = ""
        for recnum in range(0, byte_count*2, 2):
            pdata = pdata + chr(int(data[recnum] + data[recnum+1], 16))
        return byte_count, address, rectype, pdata

    def _parse_string(self, string):
        lines = string.split('\n')
        for line in lines:
            try:
                byte_count, address, rectype, pdata = self._parse_line(line)
            except iHEXEndOfFile,e:
                break
            self._memory_add(rectype, address, pdata)
        self._memory_join()



