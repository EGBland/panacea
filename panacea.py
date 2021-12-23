from VFS import VFS
from ModManager import Mod
import sys

if __name__ == "__main__":
    mod1 = Mod("LesbianClara.zip")
    mod2 = Mod("Textures.zip")

    mod1.tree.print_tree()
    mod2.tree.print_tree()

    mod1.tree.merge(mod2.tree)
    mod1.tree.print_tree()

    vfs = VFS("Textures.vfs")
    vfs.load()
    print(vfs.get_headers_length())
    vfs.add_mod(mod1)
    
    vfs.save()

