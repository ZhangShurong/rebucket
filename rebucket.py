'''
Usage:
python rebucket -s stack_json -b bucket_json

if there is no bucket_json, it will be created and all stack will be clustered and writen into.
if bucket file is not empty, stacks in stack_json will be appended into bucket_json file
'''
import json
import math

class Frame(object):
    def __init__(self, frame_dict):
        self.symbol = frame_dict['symbol']
        self.line = frame_dict['line']
        self.file_path = frame_dict['file']
'''
# TODO Do we need rewrite function '=='?
    def __eq__(self, other):
        pass
'''

def load_stack(stack_json):
    with open(stack_json) as f:
        apm_dict = json.load(f)
    all_stack = []
    for _hits_item in apm_dict['hits']['hits']:
        if _hits_item['_source']['feature'] is None:
            continue
        frames = _hits_item['_source']['feature'][0]['frame']
        stack = []
        for frame_dict in frames:
            frame = Frame(frame_dict)
            stack.append(frame)
        all_stack.append(stack)
    return all_stack

def load_buckets(bucket_json):
    return []

def get_dist(stack1, stack2):
    # FIXME set resonable c and o
    c = 0.1
    o = 0.2

    stack_len1 = len(stack1)
    stack_len2 = len(stack2)

    # TODO Why return 1?
    if stack_len1 == 1:
        return 1.0
    if stack_len2 == 1:
        return 1.0
    M = [[0. for i in range(len(stack2) + 1)] for j in range(len(stack1) + 1)]
    for i in xrange(1, len(stack1) + 1):
        for j in xrange(1, len(stack2) + 1):
            if stack1[i - 1].symbol == stack2[j - 1].symbol:
                x = (math.e ** (-c * min(i-1, j-1))) * (math.e ** (-o * abs(i-j)))
            else:
                x = 0.
            M[i][j] = max(M[i-1][j-1] + x, M[i-1][j], M[i][j-1])
    sig = 0.
    for i in range(min(stack_len1, stack_len2)):
        sig += math.e ** (-c * i)

    sim = M[stack_len1][stack_len2] / sig
    return 1 - sim

def clustering(all_stack):
    sim = []
    for i in range(len(all_stack) - 1):
        for j in range(i + 1, len(all_stack)):
            res = get_dist(all_stack[i], all_stack[j])
            sim.append(res)
    print sim
    
    return []

def rebucket(all_stack, buckets):
    for stack in all_stack:
        for frame in stack:
            print frame.symbol
        print '---------'
    clustering(all_stack)
    return []

def write_buckets(bucket_json):
    pass

def main():
    stack_json = 'apm_data/df_log_android-2018-10-01.json'
    bucket_json = 'apm_data/bucket.json'
    all_stack = load_stack(stack_json)
    buckets = load_buckets(bucket_json)
    new_buckets = rebucket(all_stack, buckets)
    write_buckets(new_buckets)

if __name__ == "__main__":
    main()
