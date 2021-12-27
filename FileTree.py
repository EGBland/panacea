from collections import namedtuple
from anytree import NodeMixin, Resolver, ResolverError, PreOrderIter, RenderTree

FileHeader = namedtuple("FileHeader", ["name", "size", "datemodified", "offset"])
DirectoryHeader = namedtuple("DirectoryHeader", ["name", "num_subdirs", "num_files"])

class File(NodeMixin):
    def __init__(self, name, size, datemodified, offset=None, parent=None):
        self.name = name
        self.size = size
        self.datemodified = datemodified
        self.old_offset = offset
        self.offset = offset
        self.parent = parent
        self.data = None

class Directory(NodeMixin):
    resolver = Resolver("name")

    def __init__(self, name, parent=None, children=None):
        self.name = name
        self.parent = parent
    
    def __lookup_node(self, path, root=None):
        if not root:
            root = self
        try:
            return self.resolver.get(root, path)
        except ResolverError:
            return None

    def __merge_node(self, dir, that_node, overwrite):
        # TODO check that dir is directory
        this_node = self.__lookup_node(that_node.name, dir)
        # if this node does not exist, simply move that node onto the tree
        if not this_node:
            that_node.parent = dir
            return
        
        if type(that_node) != type(this_node):
            raise Exception("Type mismatch between %s and %s" % (that_node, this_node))
        
        # if directories, do nothing now and merge files further down
        if isinstance(this_node, Directory):
            return
        
        # if files, overwrite if desired
        if overwrite:
            this_node.parent = None
            that_node.parent = dir

    def __merge(self, this_root, that_root, overwrite):
        #self.__merge_node(this_root, that_root, overwrite)
        for child in that_root.children:
            if isinstance(child, Directory):
                new_this_root = self.__lookup_node(child.name, this_root)
                if new_this_root:
                    if not isinstance(new_this_root, Directory):
                        raise Exception("Type mismatch between %s and %s" % (new_this_root, child))
                    self.__merge(new_this_root, child, overwrite)
                    continue
            self.__merge_node(this_root, child, overwrite)


    def merge(self, merging_node, overwrite=True):
            self.__merge(self, merging_node, overwrite)
    
    def print_tree(self):
        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))