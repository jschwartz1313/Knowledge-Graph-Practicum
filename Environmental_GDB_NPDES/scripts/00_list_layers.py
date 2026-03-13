
#!/usr/bin/env python3
"""
List layers inside a FileGDB. Usage:
  python Environmental_GDB_NPDES/scripts/00_list_layers.py --gdb Environmental_GDB_NPDES/data/raw/ImpairedWaters.gdb
"""
import argparse
import fiona

p = argparse.ArgumentParser()
p.add_argument('--gdb', required=True)
args = p.parse_args()

layers = fiona.listlayers(args.gdb)
print("Layers in", args.gdb)
for i, l in enumerate(layers, 1):
    print(f"{i}. {l}")
