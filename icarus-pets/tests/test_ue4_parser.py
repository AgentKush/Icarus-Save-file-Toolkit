"""Tests for #44: UE4 binary parser test suite."""
import sys, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ue4_parser import BinaryReader, BinaryWriter, parse_properties, parse_property


# ── Helper: build binary for a single property ──────────────────────────────

def _write_str(w, s):
    """Write a length-prefixed null-terminated string."""
    w.write_string(s)

def _build_property_bytes(name, type_name, build_fn):
    """Build complete binary for a property: name, type, data_size, array_index, content."""
    # Build content first to measure data_size
    content = BinaryWriter()
    build_fn(content)
    content_bytes = content.get_bytes()

    w = BinaryWriter()
    _write_str(w, name)
    _write_str(w, type_name)
    w.write_int32(len(content_bytes) - 1)  # data_size (exclude extra byte)
    w.write_int32(0)  # array_index
    w.write_bytes(content_bytes)
    _write_str(w, "None")  # sentinel
    return w.get_bytes()


# ── BinaryReader Tests ───────────────────────────────────────────────────────

def test_reader_int32():
    data = struct.pack('<i', -42)
    r = BinaryReader(data)
    assert r.read_int32() == -42
    print("  ✓ read_int32")

def test_reader_uint32():
    data = struct.pack('<I', 3000000000)
    r = BinaryReader(data)
    assert r.read_uint32() == 3000000000
    print("  ✓ read_uint32")

def test_reader_int64():
    data = struct.pack('<q', 9999999999)
    r = BinaryReader(data)
    assert r.read_int64() == 9999999999
    print("  ✓ read_int64")

def test_reader_float():
    data = struct.pack('<f', 3.14)
    r = BinaryReader(data)
    assert abs(r.read_float() - 3.14) < 0.001
    print("  ✓ read_float")

def test_reader_byte():
    r = BinaryReader(bytes([0xFF]))
    assert r.read_byte() == 255
    print("  ✓ read_byte")

def test_reader_string():
    w = BinaryWriter()
    w.write_string("Hello")
    r = BinaryReader(w.get_bytes())
    assert r.read_string() == "Hello"
    print("  ✓ read_string")

def test_reader_string_empty():
    w = BinaryWriter()
    w.write_string("")
    r = BinaryReader(w.get_bytes())
    assert r.read_string() == ""
    print("  ✓ read_string empty")

def test_reader_has_data():
    r = BinaryReader(bytes([1, 2, 3]))
    assert r.has_data()
    r.read_bytes(3)
    assert not r.has_data()
    print("  ✓ has_data")

def test_reader_position_tracking():
    data = struct.pack('<iif', 1, 2, 3.0)
    r = BinaryReader(data)
    assert r.pos == 0
    r.read_int32()
    assert r.pos == 4
    r.read_int32()
    assert r.pos == 8
    r.read_float()
    assert r.pos == 12
    print("  ✓ position tracking")


# ── BinaryWriter Tests ───────────────────────────────────────────────────────

def test_writer_roundtrip_int32():
    w = BinaryWriter()
    w.write_int32(-12345)
    r = BinaryReader(w.get_bytes())
    assert r.read_int32() == -12345
    print("  ✓ writer int32 roundtrip")

def test_writer_roundtrip_string():
    w = BinaryWriter()
    w.write_string("TestString123")
    r = BinaryReader(w.get_bytes())
    assert r.read_string() == "TestString123"
    print("  ✓ writer string roundtrip")

def test_writer_roundtrip_float():
    w = BinaryWriter()
    w.write_float(1.5)
    r = BinaryReader(w.get_bytes())
    assert r.read_float() == 1.5
    print("  ✓ writer float roundtrip")


# ── IntProperty Tests ────────────────────────────────────────────────────────

def test_parse_int_property():
    w = BinaryWriter()
    w.write_string("TestInt")
    w.write_string("IntProperty")
    w.write_int32(4)   # data_size
    w.write_int32(0)   # array_index
    w.write_byte(0)    # extra
    w.write_int32(42)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert len(props) == 1
    assert props[0]["name"] == "TestInt"
    assert props[0]["type"] == "IntProperty"
    assert props[0]["value"] == 42
    print("  ✓ IntProperty parse")

def test_parse_int_property_negative():
    w = BinaryWriter()
    w.write_string("Neg")
    w.write_string("IntProperty")
    w.write_int32(4); w.write_int32(0); w.write_byte(0)
    w.write_int32(-999)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] == -999
    print("  ✓ IntProperty negative")


# ── UInt32Property Tests ─────────────────────────────────────────────────────

def test_parse_uint32_property():
    w = BinaryWriter()
    w.write_string("TestUInt")
    w.write_string("UInt32Property")
    w.write_int32(4); w.write_int32(0); w.write_byte(0)
    w.write_uint32(3000000000)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] == 3000000000
    print("  ✓ UInt32Property parse")


# ── StrProperty Tests ────────────────────────────────────────────────────────

def test_parse_str_property():
    w = BinaryWriter()
    w.write_string("Name")
    w.write_string("StrProperty")
    val = "BP_Mount_Buffalo_C"
    val_bytes = val.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(val_bytes))  # data_size
    w.write_int32(0); w.write_byte(0)
    w.write_string(val)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] == "BP_Mount_Buffalo_C"
    print("  ✓ StrProperty parse")

def test_parse_str_property_empty():
    w = BinaryWriter()
    w.write_string("Empty")
    w.write_string("StrProperty")
    w.write_int32(4)  # data_size: just the 0-length int
    w.write_int32(0); w.write_byte(0)
    w.write_string("")
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] == ""
    print("  ✓ StrProperty empty")


# ── BoolProperty Tests ───────────────────────────────────────────────────────

def test_parse_bool_property_true():
    w = BinaryWriter()
    w.write_string("IsAlive")
    w.write_string("BoolProperty")
    w.write_int32(0)  # data_size always 0
    w.write_int32(0)  # array_index
    w.write_byte(1)   # value
    w.write_byte(0)   # extra
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] is True
    print("  ✓ BoolProperty true")

def test_parse_bool_property_false():
    w = BinaryWriter()
    w.write_string("IsDead")
    w.write_string("BoolProperty")
    w.write_int32(0); w.write_int32(0)
    w.write_byte(0)   # value
    w.write_byte(0)   # extra
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] is False
    print("  ✓ BoolProperty false")


# ── NameProperty Tests ───────────────────────────────────────────────────────

def test_parse_name_property():
    w = BinaryWriter()
    w.write_string("RowName")
    w.write_string("NameProperty")
    val = "Mount_Buffalo"
    val_bytes = val.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(val_bytes))
    w.write_int32(0); w.write_byte(0)
    w.write_string(val)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["value"] == "Mount_Buffalo"
    print("  ✓ NameProperty parse")


# ── EnumProperty Tests ───────────────────────────────────────────────────────

def test_parse_enum_property():
    w = BinaryWriter()
    w.write_string("CombatState")
    w.write_string("EnumProperty")
    enum_val = "EMountCombatBehaviourState::NeutralEngagement"
    ev_bytes = enum_val.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(ev_bytes))  # data_size covers value string
    w.write_int32(0)
    w.write_string("EMountCombatBehaviourState")  # enum_type
    w.write_byte(0)
    w.write_string(enum_val)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["enum_type"] == "EMountCombatBehaviourState"
    assert props[0]["value"] == "EMountCombatBehaviourState::NeutralEngagement"
    print("  ✓ EnumProperty parse")


# ── StructProperty Tests ─────────────────────────────────────────────────────

def test_parse_struct_vector():
    from ue4_serializer import serialize_properties
    w = BinaryWriter()
    w.write_string("Position")
    w.write_string("StructProperty")
    # Inner content: 3 floats = 12 bytes
    w.write_int32(12)
    w.write_int32(0)
    w.write_string("Vector")
    w.write_bytes(bytes(17))  # GUID
    w.write_float(1.0); w.write_float(2.0); w.write_float(3.0)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["struct_type"] == "Vector"
    assert props[0]["value"]["X"] == 1.0
    assert props[0]["value"]["Y"] == 2.0
    assert props[0]["value"]["Z"] == 3.0
    print("  ✓ StructProperty Vector")

def test_parse_struct_quat():
    w = BinaryWriter()
    w.write_string("Rotation")
    w.write_string("StructProperty")
    w.write_int32(16)  # 4 floats
    w.write_int32(0)
    w.write_string("Quat")
    w.write_bytes(bytes(17))
    w.write_float(0.0); w.write_float(0.0); w.write_float(0.0); w.write_float(1.0)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["struct_type"] == "Quat"
    assert props[0]["value"]["W"] == 1.0
    print("  ✓ StructProperty Quat")

def test_parse_struct_generic():
    from ue4_serializer import serialize_properties as ser
    # Generic struct with inner properties
    inner_w = BinaryWriter()
    inner_w.write_string("InnerVal")
    inner_w.write_string("IntProperty")
    inner_w.write_int32(4); inner_w.write_int32(0); inner_w.write_byte(0)
    inner_w.write_int32(77)
    inner_w.write_string("None")
    inner_bytes = inner_w.get_bytes()

    w = BinaryWriter()
    w.write_string("MyStruct")
    w.write_string("StructProperty")
    w.write_int32(len(inner_bytes))
    w.write_int32(0)
    w.write_string("CustomStruct")
    w.write_bytes(bytes(17))
    w.write_bytes(inner_bytes)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["struct_type"] == "CustomStruct"
    assert props[0]["properties"][0]["name"] == "InnerVal"
    assert props[0]["properties"][0]["value"] == 77
    print("  ✓ StructProperty generic with inner props")


# ── ArrayProperty Tests ──────────────────────────────────────────────────────

def test_parse_array_int():
    content_w = BinaryWriter()
    content_w.write_int32(3)  # count
    content_w.write_int32(10); content_w.write_int32(20); content_w.write_int32(30)
    content = content_w.get_bytes()

    w = BinaryWriter()
    w.write_string("IntArray")
    w.write_string("ArrayProperty")
    w.write_int32(len(content))
    w.write_int32(0)
    w.write_string("IntProperty")
    w.write_byte(0)
    w.write_bytes(content)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["inner_type"] == "IntProperty"
    assert props[0]["count"] == 3
    assert props[0]["elements"] == [10, 20, 30]
    print("  ✓ ArrayProperty IntProperty")

def test_parse_array_str():
    content_w = BinaryWriter()
    content_w.write_int32(2)  # count
    content_w.write_string("alpha")
    content_w.write_string("beta")
    content = content_w.get_bytes()

    w = BinaryWriter()
    w.write_string("StrArray")
    w.write_string("ArrayProperty")
    w.write_int32(len(content))
    w.write_int32(0)
    w.write_string("StrProperty")
    w.write_byte(0)
    w.write_bytes(content)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["elements"] == ["alpha", "beta"]
    print("  ✓ ArrayProperty StrProperty")

def test_parse_array_empty():
    content_w = BinaryWriter()
    content_w.write_int32(0)  # count = 0
    content = content_w.get_bytes()

    w = BinaryWriter()
    w.write_string("EmptyArr")
    w.write_string("ArrayProperty")
    w.write_int32(len(content))
    w.write_int32(0)
    w.write_string("IntProperty")
    w.write_byte(0)
    w.write_bytes(content)
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["count"] == 0
    assert props[0]["elements"] == []
    print("  ✓ ArrayProperty empty")


# ── Multiple Properties ──────────────────────────────────────────────────────

def test_parse_multiple_properties():
    w = BinaryWriter()
    # IntProperty
    w.write_string("Health"); w.write_string("IntProperty")
    w.write_int32(4); w.write_int32(0); w.write_byte(0); w.write_int32(100)
    # BoolProperty
    w.write_string("Alive"); w.write_string("BoolProperty")
    w.write_int32(0); w.write_int32(0); w.write_byte(1); w.write_byte(0)
    # StrProperty
    w.write_string("Name"); w.write_string("StrProperty")
    val = "TestMount"
    vb = val.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(vb)); w.write_int32(0); w.write_byte(0)
    w.write_string(val)
    # Sentinel
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert len(props) == 3
    assert props[0]["name"] == "Health" and props[0]["value"] == 100
    assert props[1]["name"] == "Alive" and props[1]["value"] is True
    assert props[2]["name"] == "Name" and props[2]["value"] == "TestMount"
    print("  ✓ multiple properties in sequence")


# ── None Sentinel ────────────────────────────────────────────────────────────

def test_none_sentinel_only():
    w = BinaryWriter()
    w.write_string("None")
    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props == []
    print("  ✓ None sentinel returns empty list")

def test_empty_data():
    props = parse_properties(BinaryReader(b''))
    assert props == []
    print("  ✓ empty data returns empty list")


# ── Unknown Property Type ────────────────────────────────────────────────────

def test_unknown_property_type():
    w = BinaryWriter()
    w.write_string("Mystery")
    w.write_string("FutureProperty")
    w.write_int32(3)   # data_size
    w.write_int32(0)
    w.write_byte(0)    # extra
    w.write_bytes(bytes([0xAA, 0xBB, 0xCC]))
    w.write_string("None")

    props = parse_properties(BinaryReader(w.get_bytes()))
    assert props[0]["type"] == "FutureProperty"
    assert props[0]["raw_data"] == [0xAA, 0xBB, 0xCC]
    print("  ✓ unknown property type → raw_data")


# ── Parse-Serialize Roundtrip Per Type ───────────────────────────────────────

def test_roundtrip_all_simple_types():
    from ue4_serializer import props_to_binary_array

    w = BinaryWriter()
    # Int
    w.write_string("V1"); w.write_string("IntProperty")
    w.write_int32(4); w.write_int32(0); w.write_byte(0); w.write_int32(42)
    # UInt32
    w.write_string("V2"); w.write_string("UInt32Property")
    w.write_int32(4); w.write_int32(0); w.write_byte(0); w.write_uint32(999)
    # Bool
    w.write_string("V3"); w.write_string("BoolProperty")
    w.write_int32(0); w.write_int32(0); w.write_byte(1); w.write_byte(0)
    # Str
    w.write_string("V4"); w.write_string("StrProperty")
    sv = "TestVal"; sb = sv.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(sb)); w.write_int32(0); w.write_byte(0); w.write_string(sv)
    # Name
    w.write_string("V5"); w.write_string("NameProperty")
    nv = "NameVal"; nb = nv.encode('utf-8') + b'\x00'
    w.write_int32(4 + len(nb)); w.write_int32(0); w.write_byte(0); w.write_string(nv)
    # Sentinel
    w.write_string("None")
    # Trailing zeros
    w.write_int32(0)

    original = list(w.get_bytes())
    props = parse_properties(BinaryReader(bytes(original)))
    rebuilt = props_to_binary_array(props)
    assert rebuilt == original, f"Roundtrip mismatch: {len(original)} vs {len(rebuilt)} bytes"
    print(f"  ✓ roundtrip all simple types ({len(original)} bytes)")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== UE4 Binary Parser Tests (#44) ===")
    print()
    print("-- BinaryReader --")
    test_reader_int32()
    test_reader_uint32()
    test_reader_int64()
    test_reader_float()
    test_reader_byte()
    test_reader_string()
    test_reader_string_empty()
    test_reader_has_data()
    test_reader_position_tracking()
    print()
    print("-- BinaryWriter Roundtrip --")
    test_writer_roundtrip_int32()
    test_writer_roundtrip_string()
    test_writer_roundtrip_float()
    print()
    print("-- IntProperty --")
    test_parse_int_property()
    test_parse_int_property_negative()
    print()
    print("-- UInt32Property --")
    test_parse_uint32_property()
    print()
    print("-- StrProperty --")
    test_parse_str_property()
    test_parse_str_property_empty()
    print()
    print("-- BoolProperty --")
    test_parse_bool_property_true()
    test_parse_bool_property_false()
    print()
    print("-- NameProperty --")
    test_parse_name_property()
    print()
    print("-- EnumProperty --")
    test_parse_enum_property()
    print()
    print("-- StructProperty --")
    test_parse_struct_vector()
    test_parse_struct_quat()
    test_parse_struct_generic()
    print()
    print("-- ArrayProperty --")
    test_parse_array_int()
    test_parse_array_str()
    test_parse_array_empty()
    print()
    print("-- Multi / Edge Cases --")
    test_parse_multiple_properties()
    test_none_sentinel_only()
    test_empty_data()
    test_unknown_property_type()
    print()
    print("-- Roundtrip --")
    test_roundtrip_all_simple_types()
    print()
    print(f"✅ All 28 tests passed!")
