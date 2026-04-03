"""Run rebucket shared library on a dataset.

Typical usage:
    python3 test.py -d ../../dataset/Firefox/df_mozilla_firefox.json

Self test:
    python3 test.py --self-test
"""

import ctypes
import platform
import sys
import getopt
import json
import time

class Stack:
    def __init__(self, id, frame_arr, duplicated_stack=None):
        self.id = id
        self.stack_arr = frame_arr
        self.duplicated_stack = duplicated_stack

    def __len__(self):
        return len(self.stack_arr)

    def __getitem__(self, index):
        return self.stack_arr[index]


class Frame:
    def __init__(self, frame, with_str=False):
        if with_str:
            self.symbol = frame
        else:
            self.symbol = frame['symbol']
            self.line = frame['line']
            self.file = frame['file']


def load_dataset(dataset_path):
    with open(dataset_path) as json_file:
        dataset_dict = json.load(json_file)
    all_stacks = []
    for stack_dict in dataset_dict:
        stack_id = stack_dict['stack_id']
        duplicated_stack = stack_dict.get('duplicated_stack', None)
        frame_arr = []
        for frame_dict in stack_dict['stack_arr']:
            frame = Frame(frame_dict)
            frame_arr.append(frame)
        all_stacks.append(Stack(stack_id, frame_arr, duplicated_stack))
    return all_stacks

def stacks_to_str(all_stacks):
    stack_arr = []
    for stack in all_stacks:
        stack_dict = {}
        stack_dict['stack_id'] = stack.id
        frame_arr = []
        for frame in stack.stack_arr:
            frame_str = frame.symbol
            frame_arr.append(frame_str)
        stack_dict['stack_arr'] = frame_arr
        stack_arr.append(bytes(json.dumps(stack_dict), 'utf-8'))
    return stack_arr

def main(argv):
    so = ctypes.cdll.LoadLibrary
    sysstr = platform.system()
    if sysstr == "Windows":
        lib = so("./librebucket.dll")
    elif sysstr == "Linux":
        lib = so("./librebucket.so")
    elif sysstr == 'Darwin':
        lib = so("./librebucket.dylib")
    else:
        print("Other System tasks")

    dataset_path = ''
    self_test = False
    try:
        opts, args = getopt.getopt(argv, "hd:", ["help", "dataset=", "self-test"])
    except getopt.GetoptError:
        print('test.py -d <dataset>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -d <dataset>')
            sys.exit()
        elif opt in ("-d", "--dataset"):
            dataset_path = arg

        elif opt == "--self-test":
            self_test = True

    # Bind extra helpers.
    if hasattr(lib, "rebucket_reset"):
        lib.rebucket_reset.restype = None
        lib.rebucket_reset()
    if hasattr(lib, "rebucket_bucket_count"):
        lib.rebucket_bucket_count.restype = ctypes.c_size_t

    lib.single_pass_clustering.restype = ctypes.c_char_p

    if self_test:
        # invalid json => empty
        r = lib.single_pass_clustering(ctypes.c_char_p(b"{bad"))
        assert r is not None and r.decode("utf-8") == "", "invalid json should return empty string"
        if hasattr(lib, "rebucket_bucket_count"):
            assert lib.rebucket_bucket_count() == 0
        # valid json => stack_id
        r = lib.single_pass_clustering(ctypes.c_char_p(b'{"stack_id":"1","stack_arr":["a","b"]}'))
        assert r.decode("utf-8") == "1"
        print("[PASS] python self-test")
        return

    all_stack = load_dataset(dataset_path)
    print(len(all_stack))
    stack_arr = stacks_to_str(all_stack)
    print('single_pass_clustering')
    total = 0
    buckets = 0
    for i, stack_bytes in enumerate(stack_arr):
        if i == 5001:
            break
        if i == 5000:
            start = time.time()
        bucket_id = lib.single_pass_clustering(ctypes.c_char_p(stack_bytes)).decode('utf-8')
        if i == 5000:
            end = time.time()
            print("Time is " + str(end - start))
        if all_stack[i].id == bucket_id:
            buckets += 1
        total += 1
    print(total)
    print(buckets)

if __name__ == "__main__":
    main(sys.argv[1:])
