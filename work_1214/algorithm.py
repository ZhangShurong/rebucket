# -*- coding: UTF-8 -*-
# 有两种算法。一种是Trie一种是栈模拟。

class Trie:
    def __init__(self, frame = ""):
        self.path = {}
        self.frame = frame
        self.value = [0]
        self.depth = 0
        self.sequence = -1

    def addstack(self, stack, sequence = -1, depth = 0):
        # 根结点
        if sequence == -1:
            sequence = self.sequence + 1
            self.sequence = sequence

        head = stack[0]
        if head in self.path:
            node = self.path[head]
        else:
            node = Trie(head)
            self.path[head] = node

        if len(stack) > 1:
            remains = stack[1:]
            node.addstack(remains, sequence, depth + 1)

        if sequence - node.sequence > 1 and max(node.value) != 0:
            node.value.append(1)
        else:
            node.value[-1] += 1

        node.sequence = sequence
        node.depth = depth

    def get_func(self, count):
        child_indexes = self.path.keys()
        res_list = []
        for child_index in child_indexes:
            print("(%s, %s)" % (child_index, self.path[child_index].value))
            child = self.path[child_index]
            res = child.get_func(count)
            if res:
                res_list.append(res)

        if len(res_list) is 0:
            if max(self.value) >= count:
                return self
        else:
            max_depth = -1
            best_node = None
            for node in res_list:
                if node.depth > max_depth:
                    best_node = node
                    max_depth = node.depth
                elif node.depth == max_depth:
                    if max(node.value) > max(best_node.value):
                        best_node = node
            return best_node
        return None


def main(stacks, count=2):
    test = Trie()
    for stack in stacks:
        test.addstack(stack)
    print test.get_func(count).frame

if __name__=='__main__':

    stack1 = ['1','2','3','4']
    stack2 = ['1','5','6','7']
    stack3 = ['1','2','3','4']
    stack4 = ['1','2','3','4']

    test_stacks1 = [stack1, stack2, stack3, stack4]
    main(test_stacks1)

    stack1 = ['1','2','3','4','5']
    stack2 = ['1','2','3','4','5']
    stack3 = ['1','2','3','4','6']
    stack4 = ['1','2','3','7','8']
    stack5 = ['1','2','3','9','10']
    stack6 = ['1','2','3','9','11', '13']
    stack7 = ['1','2','3','9','12']
    stack8 = ['1','2','3','9','13']
    stack9 = ['1','2','3','9','14']

    test_stacks1 = [stack1, stack2, stack3, stack4, stack5,
            stack6, stack7, stack8, stack9]
    main(test_stacks1)

    stack1 = ['1','2','3','4','5']
    stack2 = ['1','2','3','4','5']
    stack3 = ['1','2','3','4','6']
    stack4 = ['1','2','3','7','8']
    stack5 = ['1','2','3','9','10']
    stack6 = ['1','2','3','9','11', '13']
    stack7 = ['1','2','3','9','12']
    stack8 = ['1','2','3','9','13']
    stack9 = ['1','2','3','9','14']
    stack10 = ['15','2','3','9','14']
    test_stacks2 = [stack1, stack2, stack3, stack4, stack5,
            stack6, stack7, stack8, stack9, stack10]
    main(test_stacks2, 3)

    stack1 = ['1','2','3','4','5']
    stack2 = ['1','2','3','4','5']
    stack3 = ['1','2','3','4','6']
    stack4 = ['1','2','3','7','8']
    stack5 = ['1','2','3','9','10']
    stack6 = ['1','2','3','9','11', '13']
    stack7 = ['1','2','3','9','12']
    stack8 = ['1','2','3','9','14','15']
    stack9 = ['1','2','3','9','14','15']
    stack10 = ['1','2','3','9','14','15']
    test_stacks2 = [stack1, stack2, stack3, stack4, stack5,
            stack6, stack7, stack8, stack9, stack10]
    main(test_stacks2)

    stack1 = ['1','2','3','4','5']
    stack2 = ['1','2','3','4','5']
    stack3 = ['1','2','3','4','6']
    stack4 = ['1','2','3','7','8']
    stack5 = ['1','2','3','9','10']
    stack6 = ['1','2','3','9','11', '13']
    stack7 = ['1','2','3','9','12']
    stack8 = ['1','2','3','9','14']
    stack9 = ['1','2','3','9','19']
    stack10 = ['1','2','3','9','14']
    test_stacks2 = [stack1, stack2, stack3, stack4, stack5,
            stack6, stack7, stack8, stack9, stack10]
    main(test_stacks2)



