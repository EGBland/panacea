from zipfile import ZipFile
from anytree import Resolver
from FileTree import File, Directory
from time import time
import os.path

class Mod:
    def __init__(self, path_to_zip_file):
        self.name = os.path.basename(os.path.splitext(path_to_zip_file)[0])
        archive = ZipFile(path_to_zip_file, "r")
        infolist = archive.infolist()
        #print(infolist)

        self.tree = Directory("mod")
        self.resolver = Resolver("name")
        for info in infolist:
            (head, tail) = os.path.split(info.filename)
            if tail == "":
                # directory
                (path, dirname) = os.path.split(head)
                base_node = self.resolver.get(self.tree, path)
                Directory(dirname, parent=base_node)
            else:
                # file
                base_node = self.resolver.get(self.tree, head)
                the_file = File(tail, info.file_size, time(), parent=base_node)
                fh = archive.open(info.filename)
                the_file.data = fh.read()
                fh.close()
                