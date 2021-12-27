from VFS import VFS
from ModManager import Mod
import sys
import os
import os.path as path
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--patho-dir", type=str, default="data", help="specify the Pathologic data directory")
    parser.add_argument("-m", "--mod-dir", type=str, default="mods", help="specify the mod directory")
    args = parser.parse_args()

    # get vfs files
    #patho_dir = r"D:\games\steam\steamapps\common\Pathologic Classic HD\data"

    print("Finding VFS files in %s" % args.patho_dir)
    patho_vfs_files = {path.basename(path.splitext(x)[0]): VFS(path.join(args.patho_dir, x)) for x in os.listdir(args.patho_dir) if path.splitext(x)[1] == ".vfs"}
    patho_vfs_changes = {x: False for x in patho_vfs_files}
    print("Found %d VFS file(s): %s" % (len(patho_vfs_files), ", ".join(patho_vfs_files)))
    for file in patho_vfs_files:
        print("Loading %s.vfs" % file)
        patho_vfs_files[file].load()

    print("Finding mods in %s" % args.mod_dir)
    mods = [Mod(path.join(args.mod_dir, x)) for x in os.listdir(args.mod_dir) if path.splitext(x)[1] == ".zip"]
    print("Found %d mod(s): %s" % (len(mods), ", ".join([x.name for x in mods])))
    for mod in mods:
        vfses = mod.get_vfses_to_modify(str(x) for x in patho_vfs_files)
        for v in vfses:
            patho_vfs_files[v].add_mod(mod)
            patho_vfs_changes[v] = True
    
    
    for k in [x for x in patho_vfs_changes if patho_vfs_changes[x]]:
        print("Saving %s" % k)
        patho_vfs_files[k].save()
