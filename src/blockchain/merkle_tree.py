import hashlib
import logging
from typing import List


class Tree_Node:
    def __init__(self, left, right, value: str) -> None:
        self.left: Tree_Node = left
        self.right: Tree_Node = right
        self.value = value

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

    @staticmethod
    def doubleHash(val: str) -> str:
        return Tree_Node.hash(Tree_Node.hash(val))


class MerkleTree:
    def __init__(self, values: List[str]) -> None:
        self.__buildTree(values)

    def __buildTree(self, values: List[str]) -> None:
        leaves: List[Tree_Node] = [Tree_Node(None, None, Tree_Node.doubleHash(e)) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1:][0])  # duplicate last elem if odd number of elements
        self.root: Tree_Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes: List[Tree_Node]) -> Tree_Node:
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Tree_Node(nodes[0], nodes[1],
                             Tree_Node.doubleHash(nodes[0].value + nodes[1].value))

        left: Tree_Node = self.__buildTreeRec(nodes[:half])
        right: Tree_Node = self.__buildTreeRec(nodes[half:])
        value: str = Tree_Node.doubleHash(left.value + right.value)
        return Tree_Node(left, right, value)

    def printTree(self) -> None:
        self.__printTreeRec(self.root)

    def __printTreeRec(self, node) -> None:
        if node is not None:
            logging.info(node.value)
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self) -> str:
        return self.root.value
