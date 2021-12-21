import VFS
import sys

if __name__ == "__main__":
    vfs = VFS.VFS("Textures.vfs")
    vfs.load()
    print(vfs.get_headers_length())
    vfs.save()