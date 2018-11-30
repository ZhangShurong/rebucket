import ctypes
import platform
import sys, getopt
import json
import time
class Stack(object):
    stack_arr = []
    id = ''
    duplicated_stack=''

    def __init__(self, id, frame_arr, duplicated_stack=None):
        self.id = id
        self.stack_arr = frame_arr
        if duplicated_stack is not None:
            self.duplicated_stack = duplicated_stack

    def __len__(self):
        return len(self.stack_arr)

    def __getitem__(self, index):
        return self.stack_arr[index]


class Frame(object):
    def __init__(self, frame, with_str = False):
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
        duplicated_stack = stack_dict['duplicated_stack']
        frame_arr = []
        for fram_dict in stack_dict['stack_arr']:
            frame = Frame(fram_dict)
            frame_arr.append(frame)
        all_stacks.append(Stack(stack_id, frame_arr, duplicated_stack))
    return all_stacks

def stacks_to_str(all_stacks):
    stack_arr = []
    for stack in all_stacks:
        stack_dict = dict()
        stack_dict['stack_id'] = stack.id
        frame_arr = []
        for frame in stack.stack_arr:
            frame_str = frame.symbol
            frame_arr.append(frame_str)
        stack_dict['stack_arr'] = frame_arr
        stack_arr.append(bytes(str(json.dumps(stack_dict))))
    return stack_arr

def main(argv):
    so = ctypes.cdll.LoadLibrary
    sysstr = platform.system()
    if(sysstr =="Windows"):
        lib = so("./librebucket.dll")
    elif(sysstr == "Linux"):
        lib = so("./librebucket.so")
    elif(sysstr == 'Darwin'):
        lib = so("./librebucket.dylib")
    else:
        print ("Other System tasks")

    dataset_path = ''
    try:
        opts, args = getopt.getopt(argv,"hd:",["help","dataset="])
    except getopt.GetoptError:
        print 'test.py -d <dataset>'
        sys.exit(2)
    # passString
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py  -d <dataset>'
            sys.exit()
        elif opt in ("-d", "--dataset"):
             dataset_path = arg
    all_stack = load_dataset(dataset_path)
    print len(all_stack)
    stack_arr =  stacks_to_str(all_stack)
    print('single_pass_clustering')
    lib.single_pass_clustering.restype = ctypes.c_char_p
    total = 0
    buckets = 0
    for i,stack_bytes in enumerate(stack_arr):
        if i == 5001:
            break
        # print("Ori = " + all_stack[i].id)
        if i == 5000:
            start = time.time()
            bucket_id = str(lib.single_pass_clustering(ctypes.c_char_p(stack_bytes)))
            end = time.time()
            print "Time is " + str(end - start)
        bucket_id = str(lib.single_pass_clustering(ctypes.c_char_p(stack_bytes)))
        # print("bucket is : " + bucket_id)
        if (all_stack[i].id == bucket_id):
            buckets += 1
        total += 1
    # print('--------------------')
    # print(str(lib.single_pass_clustering(ctypes.c_char_p(test_stack2))) + ' in python')
    print total
    print buckets
if __name__ == "__main__":
    main(sys.argv[1:])
