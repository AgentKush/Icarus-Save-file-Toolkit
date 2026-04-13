"""UE4 GVAS-style binary property parser and serializer for Icarus mount data."""
import struct

class BinaryReader:
    def __init__(self, data):
        self.data = bytes(data)
        self.pos = 0

    def read_bytes(self, n):
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def read_int32(self):
        return struct.unpack('<i', self.read_bytes(4))[0]

    def read_uint32(self):
        return struct.unpack('<I', self.read_bytes(4))[0]

    def read_int64(self):
        return struct.unpack('<q', self.read_bytes(8))[0]

    def read_float(self):
        return struct.unpack('<f', self.read_bytes(4))[0]

    def read_byte(self):
        return self.read_bytes(1)[0]

    def read_string(self):
        """Read a length-prefixed null-terminated string.

        UE4 encodes strings with a signed int32 length prefix:
          - Positive length: UTF-8 encoded, `length` bytes (including null terminator)
          - Negative length: UTF-16 LE encoded, `abs(length)` characters × 2 bytes
            (including null terminator). Used when the string contains non-ASCII
            characters (e.g., French accented names like "mâle alpha").
          - Zero: empty string
        """
        length = self.read_int32()
        if length == 0:
            return ""
        if length > 0:
            # UTF-8 path (most common)
            raw = self.read_bytes(length)
            return raw[:-1].decode('utf-8', errors='replace')  # strip null terminator
        else:
            # Negative length → UTF-16 LE encoded string
            # abs(length) = number of UTF-16 characters (including null terminator)
            char_count = -length
            raw = self.read_bytes(char_count * 2)
            # Decode UTF-16 LE and strip null terminator
            return raw[:-2].decode('utf-16-le', errors='replace')

    def has_data(self):
        return self.pos < len(self.data)


class BinaryWriter:
    def __init__(self):
        self.data = bytearray()

    def write_bytes(self, b):
        self.data.extend(b)

    def write_int32(self, val):
        self.data.extend(struct.pack('<i', val))

    def write_uint32(self, val):
        self.data.extend(struct.pack('<I', val))

    def write_int64(self, val):
        self.data.extend(struct.pack('<q', val))

    def write_float(self, val):
        self.data.extend(struct.pack('<f', val))

    def write_byte(self, val):
        self.data.append(val & 0xFF)

    def write_string(self, s):
        """Write a length-prefixed null-terminated string.

        Mirrors UE4's encoding convention:
          - ASCII-only strings: positive length, UTF-8 encoded
          - Non-ASCII strings: negative length, UTF-16 LE encoded
            (preserves binary compatibility with French-locale saves)
        """
        if s == "" or s is None:
            self.write_int32(0)
        else:
            if s.isascii():
                # UTF-8 path (most common)
                encoded = s.encode('utf-8') + b'\x00'
                self.write_int32(len(encoded))
                self.write_bytes(encoded)
            else:
                # Non-ASCII → UTF-16 LE with negative length
                encoded = s.encode('utf-16-le') + b'\x00\x00'  # null terminator (2 bytes)
                char_count = len(encoded) // 2  # number of UTF-16 chars including null
                self.write_int32(-char_count)
                self.write_bytes(encoded)

    def get_bytes(self):
        return bytes(self.data)


def parse_properties(reader):
    """Parse a sequence of UE4 properties until 'None' sentinel."""
    props = []
    while reader.has_data():
        prop = parse_property(reader)
        if prop is None:
            break
        props.append(prop)
    return props


def parse_property(reader):
    """Parse a single UE4 property. Returns None on 'None' sentinel."""
    name = reader.read_string()
    if name == "None" or name == "":
        return None

    type_name = reader.read_string()
    data_size = reader.read_int32()
    array_index = reader.read_int32()

    prop = {"name": name, "type": type_name, "data_size": data_size, "array_index": array_index}

    if type_name == "IntProperty":
        _extra = reader.read_byte()  # always 0
        prop["value"] = reader.read_int32()

    elif type_name == "UInt32Property":
        _extra = reader.read_byte()  # always 0
        prop["value"] = reader.read_uint32()

    elif type_name == "StrProperty":
        _extra = reader.read_byte()  # always 0
        prop["value"] = reader.read_string()

    elif type_name == "NameProperty":
        _extra = reader.read_byte()  # always 0
        prop["value"] = reader.read_string()

    elif type_name == "BoolProperty":
        # BoolProperty: size is 0, value is stored as a single byte before the extra byte
        prop["value"] = reader.read_byte() != 0
        _extra = reader.read_byte()

    elif type_name == "EnumProperty":
        enum_type = reader.read_string()
        _extra = reader.read_byte()
        enum_value = reader.read_string()
        prop["enum_type"] = enum_type
        prop["value"] = enum_value

    elif type_name == "StructProperty":
        prop.update(parse_struct_property(reader, data_size))

    elif type_name == "ArrayProperty":
        prop.update(parse_array_property(reader, data_size))

    else:
        # Unknown type - read raw bytes
        _extra = reader.read_byte()
        prop["raw_data"] = list(reader.read_bytes(data_size))

    return prop


def parse_struct_property(reader, data_size):
    """Parse a StructProperty's metadata and contents."""
    struct_type = reader.read_string()
    guid = list(reader.read_bytes(17))  # 16-byte GUID + 1 extra byte

    result = {"struct_type": struct_type, "guid": guid}

    if struct_type in ("Quat", "Quat4f"):
        x = reader.read_float()
        y = reader.read_float()
        z = reader.read_float()
        w = reader.read_float()
        result["value"] = {"X": x, "Y": y, "Z": z, "W": w}
    elif struct_type in ("Vector", "Vector3f"):
        x = reader.read_float()
        y = reader.read_float()
        z = reader.read_float()
        result["value"] = {"X": x, "Y": y, "Z": z}
    else:
        # Generic struct - parse inner properties
        result["properties"] = parse_properties(reader)

    return result


def parse_array_property(reader, data_size):
    """Parse an ArrayProperty."""
    inner_type = reader.read_string()
    _extra = reader.read_byte()

    result = {"inner_type": inner_type}

    count = reader.read_int32()
    result["count"] = count

    if inner_type == "StructProperty":
        result.update(parse_struct_array(reader, count))
    elif inner_type == "IntProperty":
        result["elements"] = [reader.read_int32() for _ in range(count)]
    elif inner_type == "StrProperty":
        result["elements"] = [reader.read_string() for _ in range(count)]
    elif inner_type == "NameProperty":
        result["elements"] = [reader.read_string() for _ in range(count)]
    else:
        # Fallback: we already read count, read remaining raw
        remaining = data_size - 4  # subtract the count we already read
        # Actually inner_type string was part of overhead before data_size region
        # data_size includes count + element data
        result["elements"] = []

    return result


def parse_struct_array(reader, count):
    """Parse a struct array's header and elements."""
    field_name = reader.read_string()
    field_type = reader.read_string()
    struct_data_size = reader.read_int32()
    struct_array_index = reader.read_int32()
    struct_type = reader.read_string()
    guid = list(reader.read_bytes(17))

    result = {
        "struct_field_name": field_name,
        "struct_field_type": field_type,
        "struct_data_size": struct_data_size,
        "struct_array_index": struct_array_index,
        "struct_type_name": struct_type,
        "struct_guid": guid,
    }

    elements = []
    for _ in range(count):
        element_props = parse_properties(reader)
        elements.append(element_props)

    result["elements"] = elements
    return result
