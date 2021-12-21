from collections import namedtuple
from anytree import RenderTree, Resolver, ResolverError, NodeMixin, LevelOrderIter
from pathoutil import *
from os.path import splitext, basename
import io

FileHeader = namedtuple("FileHeader", ["name", "size", "datemodified", "offset"])
DirectoryHeader = namedtuple("DirectoryHeader", ["name", "num_subdirs", "num_files"])

class File(NodeMixin):
    def __init__(self, name, size, datemodified, offset=None, parent=None):
        self.name = name
        self.size = size
        self.datemodified = datemodified
        self.offset = offset
        self.parent = parent
        self.data = None

class Directory(NodeMixin):
    def __init__(self, name, parent=None, children=None):
        self.name = name
        self.parent = parent


class VFS:
    # VFS files have a magic number in the first four bytes
    _VFS_MAGIC_NUMBER = 0x4331504C

    # make a VFS object for the file at vfs_path
    def __init__(self, vfs_path):
        self.path = vfs_path
        self.name = basename(splitext(vfs_path)[0])
        self.resolver = Resolver("name")
    
    ########## VFS reading functions ##########

    # read file header from VFS into File node
    def __read_file_header(self, fh, parent):
        filename_len = read_int8(fh)
        filename = read_string(fh, filename_len)
        len = read_int(fh)
        offset = read_int(fh)
        time = read_filetime(fh)

        return File(filename, len, time, offset, parent)

    # read directory header from VFS into DirectoryHeader tuple
    def __read_directory_header(self, fh, parent):
        dirname = None
        if not parent:
            assert read_int(fh) == self._VFS_MAGIC_NUMBER, "Magic number mismatch"
            dirname = self.name
        else:
            name_len = read_int8(fh)
            dirname = read_string(fh, name_len)
        num_subdirs = read_int(fh)
        num_files = read_int(fh)
        return DirectoryHeader(dirname, num_subdirs, num_files)
    
    # recursively load directories then return root node as Directory
    def __load_directory(self, fh, parent=None):
        dir_header = self.__read_directory_header(fh, parent)
        dir_node = Directory(dir_header.name, parent)
        
        for i in range(dir_header.num_files):
            self.__read_file_header(fh, dir_node)
        
        for i in range(dir_header.num_subdirs):
            self.__load_directory(fh, dir_node)
        
        return dir_node

    # load a tree from a VFS file
    def load(self):
        with open(self.path, "rb") as fh:
            # read root directory info
            self.tree = self.__load_directory(fh)

    # read the data for a file from the VFS
    def read_file(self, path):
        file = self.__get_node(path)
        if file == None:
            raise Exception("File \"%s\" does not exist." % path)
        file = file.header
        buf = None
        with open(self.path, "rb") as fh:
            fh.seek(file.offset)
            buf = fh.read(file.file.size)
        return buf


    ########## Tree functions ##########

    # resolve a node, and return None if it doesn't exist
    def __get_node(self, path):
        try:
            return self.resolver.get(self.tree, path)
        except ResolverError:
            return None
    
    # get the length of the headers section of the VFS
    def get_headers_length(self, tree=None):
        if not tree:
            tree = self.tree
        
        if isinstance(tree, File):
            return 17 + len(tree.name)
        else:
            dir_info_len = 12
            if tree.parent:
                dir_info_len = len(tree.name) + 9
            return dir_info_len + sum(self.get_headers_length(x) for x in tree.children)
    
    # print the directory tree
    def print_tree(self):
        for pre, _, node in RenderTree(self.tree):
            print("%s%s" % (pre, node.name))

    # add a directory to the VFS
    def make_directory(self, path, dir_name):
        parent_node = self.__get_node(path)
        if not parent_node:
            raise Exception("Path %s does not exist." % path)
        if not isinstance(parent_node, Directory):
            raise Exception("Path %s is not a directory." % path)
        Directory(dir_name, parent_node)

    # add a file to the VFS
    def make_file(self, path, file_name, data):
        parent_node = self.__get_node(path)
        if not parent_node:
            raise Exception("Path %s does not exist." % path)
        if not isinstance(parent_node, Directory):
            raise Exception("Path %s is not a directory." % path)
        file_node = File(file_name, len(data), None)
    

    ########## VFS writing functions ##########

    # write a file or directory header to the VFS file
    def __write_header(self, fh, node, cur_offset = 0):
        if isinstance(node, File):
            write_string(fh, node.name)
            write_int(fh, node.size)
            write_int(fh, cur_offset)
            write_filetime(fh, node.datemodified)
            node.offset = cur_offset.value
        else:
            num_subdirs = len(list(filter(lambda x: isinstance(x, Directory), node.children)))
            num_files = len(node.children) - num_subdirs
            if node.parent:
                write_string(fh, node.name)
            else:
                write_int(fh, self._VFS_MAGIC_NUMBER)
            write_int(fh, num_subdirs)
            write_int(fh, num_files)

    # write the tree to the VFS file
    def __save_headers(self, fh, tree, cur_offset):
        self.__write_header(fh, tree)

        the_files = filter(lambda x: isinstance(x, File), tree.children)
        the_dirs = filter(lambda x: isinstance(x, Directory), tree.children)
        
        for file in the_files:
            self.__write_header(fh, file, cur_offset)
            cur_offset += file.size
        
        for dir in the_dirs:
            self.__save_headers(fh, dir, cur_offset)

    # save the (possibly modified) tree to a new VFS file
    def save(self, new_vfs_path="Modified.vfs"):
        with open(new_vfs_path, "wb") as fh:
            print("Writing headers...")
            self.__save_headers(fh, self.tree, MutableNum(self.get_headers_length()))

            print("Writing files... ", end="")
            files = list(filter(lambda x: isinstance(x, File), LevelOrderIter(self.tree)))
            files = sorted(files, key=lambda x: x.offset)
            print("%04d/%04d" % (0, len(files)), end="")

            i = 0
            for f in files:
                i += 1
                print("\b\b\b\b\b\b\b\b\b%04d/%04d" % (i, len(files)), end="")
                # move caret to position, and add 00 up to that point if file is too small
                caret = fh.seek(0, io.SEEK_END)
                if(f.offset > caret):
                    diff = f.offset - caret
                    fh.write([0] * diff)
                
                # get file data from old VFS if not loaded
                if not f.data:
                    with open(self.path, "rb") as vfs_fh:
                        vfs_fh.seek(f.offset)
                        f.data = vfs_fh.read(f.size)
                
                # write the data to the new VFS
                fh.write(f.data)
            print()