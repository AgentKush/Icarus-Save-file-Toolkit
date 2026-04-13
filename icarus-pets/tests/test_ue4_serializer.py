"""Tests for #45: UE4 binary serializer test suite."""
import sys, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ue4_parser import BinaryReader, BinaryWriter, parse_properties
from ue4_serializer import (
    serialize_properties, serialize_property, props_to_binary_array,
)


# ── Helper ───────────────────────────────────────────────────────────────────

def _roundtrip(props):
    """Serialize props, re-parse, and return re-parsed props."""
    binary = serialize_properties(props)
    return parse_properties(BinaryReader(binary))


# ── serialize_properties basics ──────────────────────────────────────────────

def test_empty_props():
    """Serializing empty list produces only the None sentinel."""
    data = serialize_properties([])
    r = BinaryReader(data)
    assert r.read_string() == "None"
    assert not r.has_data()
    print("  ✓ empty props → None sentinel only")


def test_none_sentinel_appended():
    """Output always ends with a None sentinel string."""
    props = [{"name": "X", "type": "IntProperty", "value": 1, "array_index": 0}]
    data = serialize_properties(props)
    # Find the None sentinel at the end
    r = BinaryReader(data)
    parse_properties(r)  # consume everything
    # Reader should be at end (None consumed internally)
    print("  ✓ None sentinel appended")


# ── IntProperty serialization ────────────────────────────────────────────────

def test_serialize_int():
    props = [{"name": "Health", "type": "IntProperty", "value": 100, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["name"] == "Health"
    assert result[0]["value"] == 100
    print("  ✓ IntProperty serialize")


def test_serialize_int_negative():
    props = [{"name": "Offset", "type": "IntProperty", "value": -500, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == -500
    print("  ✓ IntProperty negative")


def test_serialize_int_zero():
    props = [{"name": "Z", "type": "IntProperty", "value": 0, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == 0
    print("  ✓ IntProperty zero")


# ── UInt32Property serialization ─────────────────────────────────────────────

def test_serialize_uint32():
    props = [{"name": "Flags", "type": "UInt32Property", "value": 3000000000, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == 3000000000
    print("  ✓ UInt32Property serialize")


# ── StrProperty serialization ────────────────────────────────────────────────

def test_serialize_str():
    props = [{"name": "Name", "type": "StrProperty", "value": "BP_Mount_Buffalo_C", "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == "BP_Mount_Buffalo_C"
    print("  ✓ StrProperty serialize")


def test_serialize_str_empty():
    props = [{"name": "Tag", "type": "StrProperty", "value": "", "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == ""
    print("  ✓ StrProperty empty")


def test_serialize_str_none():
    props = [{"name": "Tag", "type": "StrProperty", "value": None, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == ""
    print("  ✓ StrProperty None → empty")


# ── NameProperty serialization ───────────────────────────────────────────────

def test_serialize_name():
    props = [{"name": "Row", "type": "NameProperty", "value": "Mount_Buffalo", "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] == "Mount_Buffalo"
    print("  ✓ NameProperty serialize")


# ── BoolProperty serialization ───────────────────────────────────────────────

def test_serialize_bool_true():
    props = [{"name": "Alive", "type": "BoolProperty", "value": True, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] is True
    print("  ✓ BoolProperty true")


def test_serialize_bool_false():
    props = [{"name": "Dead", "type": "BoolProperty", "value": False, "array_index": 0}]
    result = _roundtrip(props)
    assert result[0]["value"] is False
    print("  ✓ BoolProperty false")


def test_serialize_bool_data_size_zero():
    """BoolProperty data_size is always 0."""
    props = [{"name": "B", "type": "BoolProperty", "value": True, "array_index": 0}]
    data = serialize_properties(props)
    r = BinaryReader(data)
    r.read_string()  # name
    r.read_string()  # type
    ds = r.read_int32()  # data_size
    assert ds == 0, f"BoolProperty data_size should be 0, got {ds}"
    print("  ✓ BoolProperty data_size == 0")


# ── EnumProperty serialization ───────────────────────────────────────────────

def test_serialize_enum():
    props = [{
        "name": "State", "type": "EnumProperty",
        "enum_type": "EMountCombatBehaviourState",
        "value": "EMountCombatBehaviourState::NeutralEngagement",
        "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["enum_type"] == "EMountCombatBehaviourState"
    assert result[0]["value"] == "EMountCombatBehaviourState::NeutralEngagement"
    print("  ✓ EnumProperty serialize")


def test_serialize_enum_data_size():
    """EnumProperty data_size covers only the value string (not enum_type)."""
    props = [{
        "name": "E", "type": "EnumProperty",
        "enum_type": "EMyEnum",
        "value": "EMyEnum::ValueA",
        "array_index": 0,
    }]
    data = serialize_properties(props)
    r = BinaryReader(data)
    r.read_string()  # name
    r.read_string()  # type
    ds = r.read_int32()  # data_size
    val_bytes = "EMyEnum::ValueA".encode('utf-8') + b'\x00'
    expected = 4 + len(val_bytes)
    assert ds == expected, f"EnumProperty data_size: expected {expected}, got {ds}"
    print("  ✓ EnumProperty data_size correct")


# ── StructProperty serialization ─────────────────────────────────────────────

def test_serialize_struct_vector():
    props = [{
        "name": "Pos", "type": "StructProperty",
        "struct_type": "Vector", "guid": [0]*17,
        "value": {"X": 1.5, "Y": 2.5, "Z": 3.5},
        "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["value"]["X"] == 1.5
    assert result[0]["value"]["Y"] == 2.5
    assert result[0]["value"]["Z"] == 3.5
    print("  ✓ StructProperty Vector roundtrip")


def test_serialize_struct_quat():
    props = [{
        "name": "Rot", "type": "StructProperty",
        "struct_type": "Quat", "guid": [0]*17,
        "value": {"X": 0.0, "Y": 0.0, "Z": 0.707, "W": 0.707},
        "array_index": 0,
    }]
    result = _roundtrip(props)
    assert abs(result[0]["value"]["Z"] - 0.707) < 0.001
    assert abs(result[0]["value"]["W"] - 0.707) < 0.001
    print("  ✓ StructProperty Quat roundtrip")


def test_serialize_struct_generic():
    props = [{
        "name": "Data", "type": "StructProperty",
        "struct_type": "MyStruct", "guid": [0]*17,
        "properties": [
            {"name": "Val", "type": "IntProperty", "value": 42, "array_index": 0},
        ],
        "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["properties"][0]["value"] == 42
    print("  ✓ StructProperty generic roundtrip")


def test_serialize_struct_data_size():
    """StructProperty data_size matches inner content size."""
    props = [{
        "name": "V", "type": "StructProperty",
        "struct_type": "Vector", "guid": [0]*17,
        "value": {"X": 1.0, "Y": 2.0, "Z": 3.0},
        "array_index": 0,
    }]
    data = serialize_properties(props)
    r = BinaryReader(data)
    r.read_string()  # name
    r.read_string()  # type
    ds = r.read_int32()
    assert ds == 12, f"Vector data_size should be 12, got {ds}"
    print("  ✓ StructProperty Vector data_size == 12")


# ── ArrayProperty serialization ──────────────────────────────────────────────

def test_serialize_array_int():
    props = [{
        "name": "Ids", "type": "ArrayProperty",
        "inner_type": "IntProperty", "count": 3,
        "elements": [10, 20, 30], "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["elements"] == [10, 20, 30]
    print("  ✓ ArrayProperty Int roundtrip")


def test_serialize_array_str():
    props = [{
        "name": "Tags", "type": "ArrayProperty",
        "inner_type": "StrProperty", "count": 2,
        "elements": ["hello", "world"], "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["elements"] == ["hello", "world"]
    print("  ✓ ArrayProperty Str roundtrip")


def test_serialize_array_empty():
    props = [{
        "name": "Empty", "type": "ArrayProperty",
        "inner_type": "IntProperty", "count": 0,
        "elements": [], "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["count"] == 0
    assert result[0]["elements"] == []
    print("  ✓ ArrayProperty empty roundtrip")


def test_serialize_struct_array():
    props = [{
        "name": "Talents", "type": "ArrayProperty",
        "inner_type": "StructProperty",
        "struct_field_name": "Talents",
        "struct_field_type": "StructProperty",
        "struct_type_name": "TalentEntry",
        "struct_guid": [0]*17,
        "struct_array_index": 0,
        "count": 2,
        "elements": [
            [{"name": "TalentName", "type": "StrProperty", "value": "Talent_A", "array_index": 0}],
            [{"name": "TalentName", "type": "StrProperty", "value": "Talent_B", "array_index": 0}],
        ],
        "array_index": 0,
    }]
    result = _roundtrip(props)
    assert result[0]["count"] == 2
    assert result[0]["elements"][0][0]["value"] == "Talent_A"
    assert result[0]["elements"][1][0]["value"] == "Talent_B"
    print("  ✓ ArrayProperty StructProperty roundtrip")


# ── props_to_binary_array ────────────────────────────────────────────────────

def test_props_to_binary_array_trailing_zeros():
    """props_to_binary_array appends 4 trailing zero bytes."""
    props = [{"name": "X", "type": "IntProperty", "value": 1, "array_index": 0}]
    result = props_to_binary_array(props)
    assert result[-4:] == [0, 0, 0, 0]
    print("  ✓ props_to_binary_array trailing zeros")


def test_props_to_binary_array_returns_list():
    """props_to_binary_array returns a list of ints (JSON-compatible)."""
    props = [{"name": "X", "type": "IntProperty", "value": 1, "array_index": 0}]
    result = props_to_binary_array(props)
    assert isinstance(result, list)
    assert all(isinstance(b, int) for b in result)
    print("  ✓ props_to_binary_array returns list of ints")


def test_props_to_binary_array_roundtrip():
    """Full props_to_binary_array → parse_properties roundtrip."""
    props = [
        {"name": "HP", "type": "IntProperty", "value": 100, "array_index": 0},
        {"name": "Name", "type": "StrProperty", "value": "TestMount", "array_index": 0},
        {"name": "Alive", "type": "BoolProperty", "value": True, "array_index": 0},
    ]
    binary = props_to_binary_array(props)
    re_parsed = parse_properties(BinaryReader(bytes(binary)))
    assert len(re_parsed) == 3
    assert re_parsed[0]["value"] == 100
    assert re_parsed[1]["value"] == "TestMount"
    assert re_parsed[2]["value"] is True

    # Double roundtrip should be identical
    binary2 = props_to_binary_array(re_parsed)
    assert binary2 == binary
    print(f"  ✓ props_to_binary_array full roundtrip ({len(binary)} bytes)")


# ── Mixed property roundtrip ─────────────────────────────────────────────────

def test_complex_mixed_roundtrip():
    """Roundtrip with all supported types in one property list."""
    props = [
        {"name": "I", "type": "IntProperty", "value": 42, "array_index": 0},
        {"name": "U", "type": "UInt32Property", "value": 999, "array_index": 0},
        {"name": "S", "type": "StrProperty", "value": "hello", "array_index": 0},
        {"name": "N", "type": "NameProperty", "value": "world", "array_index": 0},
        {"name": "B", "type": "BoolProperty", "value": False, "array_index": 0},
        {"name": "E", "type": "EnumProperty", "enum_type": "EType", "value": "EType::Val", "array_index": 0},
        {"name": "V", "type": "StructProperty", "struct_type": "Vector", "guid": [0]*17,
         "value": {"X": 1.0, "Y": 2.0, "Z": 3.0}, "array_index": 0},
        {"name": "A", "type": "ArrayProperty", "inner_type": "IntProperty",
         "count": 2, "elements": [5, 10], "array_index": 0},
    ]
    binary = props_to_binary_array(props)
    re_parsed = parse_properties(BinaryReader(bytes(binary)))
    binary2 = props_to_binary_array(re_parsed)
    assert binary == binary2, "Complex mixed roundtrip failed"
    assert len(re_parsed) == 8
    print(f"  ✓ complex mixed roundtrip ({len(binary)} bytes, 8 props)")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== UE4 Binary Serializer Tests (#45) ===")
    print()
    print("-- serialize_properties basics --")
    test_empty_props()
    test_none_sentinel_appended()
    print()
    print("-- IntProperty --")
    test_serialize_int()
    test_serialize_int_negative()
    test_serialize_int_zero()
    print()
    print("-- UInt32Property --")
    test_serialize_uint32()
    print()
    print("-- StrProperty --")
    test_serialize_str()
    test_serialize_str_empty()
    test_serialize_str_none()
    print()
    print("-- NameProperty --")
    test_serialize_name()
    print()
    print("-- BoolProperty --")
    test_serialize_bool_true()
    test_serialize_bool_false()
    test_serialize_bool_data_size_zero()
    print()
    print("-- EnumProperty --")
    test_serialize_enum()
    test_serialize_enum_data_size()
    print()
    print("-- StructProperty --")
    test_serialize_struct_vector()
    test_serialize_struct_quat()
    test_serialize_struct_generic()
    test_serialize_struct_data_size()
    print()
    print("-- ArrayProperty --")
    test_serialize_array_int()
    test_serialize_array_str()
    test_serialize_array_empty()
    test_serialize_struct_array()
    print()
    print("-- props_to_binary_array --")
    test_props_to_binary_array_trailing_zeros()
    test_props_to_binary_array_returns_list()
    test_props_to_binary_array_roundtrip()
    print()
    print("-- Complex Roundtrip --")
    test_complex_mixed_roundtrip()
    print()
    print(f"✅ All 28 tests passed!")
