import json

with open("Mounts.json", "r") as f:
    data = json.load(f)

for mount in data["SavedMounts"]:
    name = mount["MountName"]
    binary_array = mount["RecorderBlob"]["BinaryData"]
    with open(f"{name}.bin", "wb") as f:
        f.write(bytes(binary_array))
    print(f"Wrote {name}.bin ({len(binary_array)} bytes)")
