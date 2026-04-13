"""UE4 binary property serializer - writes parsed property trees back to byte arrays."""
from ue4_parser import BinaryWriter


def _string_data_size(s):
    """Calculate the serialized byte size of a UE4 string (length prefix + encoded data).

    Mirrors the encoding convention in BinaryWriter.write_string():
      - None / empty: 4 bytes (int32 zero)
      - ASCII: 4 + len(utf-8) + 1  (positive length prefix + UTF-8 + null)
      - Non-ASCII: 4 + len(utf-16-le) + 2  (negative length prefix + UTF-16 LE + null×2)
    """
    if s is None or s == "":
        return 4  # just the int32 length (0)
    if s.isascii():
        return 4 + len(s.encode('utf-8')) + 1
    else:
        return 4 + len(s.encode('utf-16-le')) + 2


def serialize_properties(props):
    """Serialize a list of properties to bytes, ending with 'None' sentinel."""
    writer = BinaryWriter()
    for prop in props:
        serialize_property(writer, prop)
    writer.write_string("None")
    return writer.get_bytes()


def serialize_property(writer, prop):
    """Serialize a single property."""
    name = prop["name"]
    type_name = prop["type"]

    writer.write_string(name)
    writer.write_string(type_name)

    if type_name == "IntProperty":
        writer.write_int32(4)  # data_size
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(0)  # extra
        writer.write_int32(prop["value"])

    elif type_name == "UInt32Property":
        writer.write_int32(4)  # data_size
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(0)
        writer.write_uint32(prop["value"])

    elif type_name == "StrProperty":
        val = prop["value"]
        writer.write_int32(_string_data_size(val))
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(0)
        writer.write_string(val if val else "")

    elif type_name == "NameProperty":
        val = prop["value"]
        writer.write_int32(_string_data_size(val))
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(0)
        writer.write_string(val if val else "")

    elif type_name == "BoolProperty":
        writer.write_int32(0)  # data_size always 0
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(1 if prop["value"] else 0)
        writer.write_byte(0)  # extra

    elif type_name == "EnumProperty":
        enum_type = prop["enum_type"]
        enum_value = prop["value"]
        # data_size = enum_type_string_size + enum_value_string_size
        et_bytes = enum_type.encode('utf-8') + b'\x00'
        ev_bytes = enum_value.encode('utf-8') + b'\x00'
        data_size = 4 + len(et_bytes) + 4 + len(ev_bytes)
        # Wait - the enum_type is written BEFORE the extra byte, outside data_size
        # Recalculate: data_size only covers the enum_value string
        data_size = 4 + len(ev_bytes)
        # But also need enum_type size in the header region
        # Actually looking at the format more carefully:
        # name, type, data_size, array_index, enum_type_string, extra_byte, enum_value_string
        # data_size covers: enum_type_string + enum_value_string
        # Let me recalculate based on actual data
        # From the data: CombatBehaviourState EnumProperty size=50
        # enum_type = "EMountCombatBehaviourState" (27 chars + null = 28, + 4 len = 32 bytes... no)
        # Actually: data_size=50, enum_type="EMountCombatBehaviourState" (26+1=27 bytes for string, +4=31)
        # enum_value = "EMountCombatBehaviourState::NeutralEngagement" (46 chars)
        # 46+1=47 bytes + 4 = 51... hmm
        # Let me re-examine: the enum_type string is part of the header (before data region)
        # data_size should cover only the enum_value string
        # EMountCombatBehaviourState = 26 chars, +null = 27, string = 4+27 = 31
        # But data_size=50 and value="EMountCombatBehaviourState::NeutralEngagement" = 45+null=46, 4+46=50
        # Yes! data_size = 4 + len(enum_value) + 1
        data_size = 4 + len(ev_bytes)
        writer.write_int32(data_size)
        writer.write_int32(prop.get("array_index", 0))
        writer.write_string(enum_type)
        writer.write_byte(0)
        writer.write_string(enum_value)

    elif type_name == "StructProperty":
        serialize_struct_property(writer, prop)

    elif type_name == "ArrayProperty":
        serialize_array_property(writer, prop)

    else:
        # Unknown - write raw
        writer.write_int32(prop.get("data_size", len(prop.get("raw_data", []))))
        writer.write_int32(prop.get("array_index", 0))
        writer.write_byte(0)
        writer.write_bytes(bytes(prop.get("raw_data", [])))


def serialize_struct_property(writer, prop):
    """Serialize a StructProperty."""
    struct_type = prop["struct_type"]
    guid = bytes(prop["guid"])

    # Serialize the inner content first to calculate size
    inner_writer = BinaryWriter()

    if struct_type in ("Quat", "Quat4f"):
        v = prop["value"]
        inner_writer.write_float(v["X"])
        inner_writer.write_float(v["Y"])
        inner_writer.write_float(v["Z"])
        inner_writer.write_float(v["W"])
    elif struct_type in ("Vector", "Vector3f"):
        v = prop["value"]
        inner_writer.write_float(v["X"])
        inner_writer.write_float(v["Y"])
        inner_writer.write_float(v["Z"])
    else:
        inner_data = serialize_properties(prop.get("properties", []))
        inner_writer.write_bytes(inner_data)

    inner_bytes = inner_writer.get_bytes()
    data_size = len(inner_bytes)

    writer.write_int32(data_size)
    writer.write_int32(prop.get("array_index", 0))
    writer.write_string(struct_type)
    writer.write_bytes(guid)
    writer.write_bytes(inner_bytes)


def serialize_array_property(writer, prop):
    """Serialize an ArrayProperty."""
    inner_type = prop["inner_type"]
    count = prop.get("count", len(prop.get("elements", [])))

    # Serialize the array content to calculate data_size
    content_writer = BinaryWriter()
    content_writer.write_int32(count)

    if inner_type == "StructProperty":
        serialize_struct_array_content(content_writer, prop)
    elif inner_type == "IntProperty":
        for elem in prop.get("elements", []):
            content_writer.write_int32(elem)
    elif inner_type == "StrProperty":
        for elem in prop.get("elements", []):
            content_writer.write_string(elem)
    elif inner_type == "NameProperty":
        for elem in prop.get("elements", []):
            content_writer.write_string(elem)

    content_bytes = content_writer.get_bytes()
    data_size = len(content_bytes)

    writer.write_int32(data_size)
    writer.write_int32(prop.get("array_index", 0))
    writer.write_string(inner_type)
    writer.write_byte(0)
    writer.write_bytes(content_bytes)


def serialize_struct_array_content(writer, prop):
    """Serialize the content portion of a struct array (after count)."""
    # Write struct array header
    writer.write_string(prop["struct_field_name"])
    writer.write_string(prop["struct_field_type"])

    elements = prop.get("elements", [])

    # Serialize all elements to calculate total struct data size
    elements_writer = BinaryWriter()
    for elem_props in elements:
        elem_data = serialize_properties(elem_props)
        elements_writer.write_bytes(elem_data)
    elements_bytes = elements_writer.get_bytes()

    writer.write_int32(len(elements_bytes))  # struct_data_size
    writer.write_int32(prop.get("struct_array_index", 0))
    writer.write_string(prop["struct_type_name"])
    writer.write_bytes(bytes(prop["struct_guid"]))
    writer.write_bytes(elements_bytes)


def props_to_binary_array(props):
    """Convert parsed properties back to a list of byte values (for JSON)."""
    data = serialize_properties(props)
    # Append the trailing 4 zero bytes
    data += b'\x00\x00\x00\x00'
    return list(data)
