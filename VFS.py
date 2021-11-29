from collections import namedtuple
from anytree import Node, RenderTree, Resolver, ResolverError, NodeMixin
from pathoutil import *
from os.path import splitext, basename

FileHeader = namedtuple("FileHeader", ["name", "size", "datemodified", "offset"])
DirectoryHeader = namedtuple("DirectoryHeader", ["name", "num_subdirs", "num_files"])

class File(NodeMixin):
    def __init__(self, name, size, datemodified, offset=None, parent=None, children=None):
        self.name = name
        self.size = size
        self.datemodified = datemodified
        self.offset = offset

class Directory(NodeMixin):
    def __init__(self, name, parent=None, children=None):
        self.name = name


class VFS:
    def __init__(self, vfs_path):
        self.path = vfs_path
        self.name = basename(splitext(vfs_path)[0])
        self.load_headers()
        self.resolver = Resolver("name")             
    
    def __read_file_header(self, fh, parent):
        filename_len = read_int8(fh)
        filename = read_string(fh, filename_len)
        len = read_int(fh)
        offset = read_int(fh)
        time = read_filetime(fh)

        return File(filename, len, time, offset, parent)

    def __read_directory_header(self, fh, parent):
        dirname = None
        if not parent:
            assert read_int(fh) == 0x4331504C, "Magic number mismatch"
            dirname = self.name
        else:
            name_len = read_int8(fh)
            dirname = read_string(fh, name_len)
        num_subdirs = read_int(fh)
        num_files = read_int(fh)
        return DirectoryHeader(dirname, num_subdirs, num_files)
    
    def __load_directory(self, fh, parent=None):
        dir_header = self.__read_directory_header(fh, parent)
        dir_node = Directory(dir_header.name)
        
        for i in range(dir_header.num_files):
            self.__read_file_header(fh, dir_node)
        
        for i in range(dir_header.num_subdirs):
            self.__load_directory(fh, dir_node)
        
        return dir_node
    
    def __get_file(self, path):
        try:
            return self.resolver.get(self.tree, path)
        except ResolverError:
            return None


    def load_headers(self):
        with open(self.path, "rb") as fh:
            # read root directory info
            self.tree = self.__load_directory(fh)

    def read_file(self, path):
        file = self.__get_file(path)
        if file == None:
            raise Exception("File \"%s\" does not exist." % path)
        file = file.header
        buf = None
        with open(self.path, "rb") as fh:
            fh.seek(file.offset)
            buf = fh.read(file.file.size)
        return buf
    
    def print_tree(self):
        for pre, _, node in RenderTree(self.tree):
            print("%s%s" % (pre, node.name))

    def make_directory(self, path):
        pass

    def write_file(self, path, data):
        pass

    def sync_with_vfs(self):

        pass
