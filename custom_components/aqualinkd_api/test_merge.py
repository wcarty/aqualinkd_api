import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from util import flatten_devices, slugify

data1 = {
  "type": "devices",
  "devices": [
    {"type": "switch", "id": "Aux_3", "name": "Spill Over", "state": "off"}
  ]
}

data2 = {
  "leds": {
    "Aux_3": "off"
  }
}

merged_devices = {}
id_map = {}
name_map = {}

for source_data in [data2, data1]:  # Try loading the bad one first
    flat_source = flatten_devices(source_data)
    print(f"Flat source: {flat_source}")
    for name, dev_data in flat_source.items():
        dev_id = dev_data.get("id")
        target = None
        if dev_id and dev_id in id_map:
            target = id_map[dev_id]
        elif name in name_map:
            target = name_map[name]
        else:
            name_slug = slugify(name)
            for existing_name, existing_data in name_map.items():
                if slugify(existing_name) == name_slug:
                    target = existing_data
                    break

        if target:
            best_name = str(target.get("name", ""))
            target.update(dev_data)
            new_name = str(target.get("name", ""))
            
            if " " in best_name and " " not in new_name:
                target["name"] = best_name
            elif " " in new_name and " " not in best_name:
                target["name"] = new_name
            elif len(best_name) > len(new_name):
                target["name"] = best_name
            elif len(new_name) > len(best_name):
                target["name"] = new_name
            elif "_" not in best_name and "_" in new_name:
                target["name"] = best_name
            elif "_" not in new_name and "_" in best_name:
                target["name"] = new_name
            else:
                target["name"] = best_name
            
            if dev_id:
                id_map[dev_id] = target
        else:
            entry = dict(dev_data)
            entry.setdefault("name", name)
            name_map[name] = entry
            if dev_id:
                id_map[dev_id] = entry
print("--- FINAL ---")
for k, v in name_map.items():
    print(f"Original Key: {k} -> Final Name: {v['name']}")
