'''
Usage:
python rebucket -s stack_json -b bucket_json

if there is no bucket_json, it will be created and all stack will be clustered and writen into.
if bucket file is not empty, stacks in stack_json will be appended into bucket_json file
'''
import json
import math
import glob
import os
import numpy
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster, fclusterdata

class Stack(object):
    stack_arr = []
    id = ''

    def __init__(self, id, frame_arr):
        self.id = id
        self.stack_arr = frame_arr

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
            self.file_path = frame['file']    
        
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
        
        stack_id = _hits_item['_id']
        stack_arr = []
        for frame_dict in frames:
            frame = Frame(frame_dict)
            stack_arr.append(frame)
        stack = Stack(stack_id, stack_arr)
        all_stack.append(stack)
    return all_stack

def load_stack2(stack_json):
    with open(stack_json) as f:
        apm_dict = json.load(f)
    all_stack = []
    for _hits_item in apm_dict['hits']['hits']:
        if _hits_item['_source']['stack'] is None:
            continue
        stack_id = _hits_item['_id']
        stacks_str = _hits_item['_source']['stack'][1:-1]
        frames = stacks_str.split(',')

        stack_arr = []
        for frame_str in frames:
            frame = Frame(frame_str, True)
            stack_arr.append(frame)
        stack = Stack(stack_id, stack_arr)
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
    
    link = linkage(sim, method = 'complete')
    dist = 0.6
    result = fcluster(link, dist, criterion='distance', depth = 2, R=None, monocrit = None)
    print result
    maximum = max(result)
    bucket = [[] for i in range(maximum)]
    for i in range(len(result)):
        bucket[int(result[i]) - 1].append(all_stack[i])
    bucket.sort()
    return bucket

def rebucket(all_stack, buckets):
    # for stack in all_stack:
    #     for frame in stack:
    #         print frame.symbol
    #     print '---------'
    return clustering(all_stack)

def write_buckets(buckets, bucket_file):
    buckets_array = []
    for bucket in buckets:
        stack_arr = []
        for stack in bucket:
            stack_dict = dict()
            frame_arr = []
            for frame in stack.stack_arr:
                frame_arr.append(frame.symbol)
            stack_dict[stack.id] = frame_arr
            stack_arr.append(stack_dict)
        buckets_array.append(stack_arr)
    buckets_json = json.dumps(buckets_array)
    with open(bucket_file, 'w') as f:
        json.dump(buckets_json, f)

def main():
    stack_json_dir = 'apm_data'
    bucket_json = 'apm_data/bucket.json'
    json_file_list = glob.glob(stack_json_dir + os.sep + "df*.json")
    all_stack = []
    for json_file in json_file_list:
        stack = load_stack2(json_file)
        all_stack += stack
    print "We have " + str(len(all_stack)) + " Stacks Now"
    print "Clustering"
    buckets = load_buckets(bucket_json)
    new_buckets = rebucket(all_stack, buckets)
    print "We have " + str(len(new_buckets)) + " buckets Now"
    write_buckets(new_buckets, bucket_json)

if __name__ == "__main__":
    main()
