'''
Usage:
python rebucket -s stack_json -b bucket_json

if there is no bucket_json, it will be created and all stack will be clustered and writen into.
if bucket file is not empty, stacks in stack_json will be appended into bucket_json file
'''
import json


def load_stack(stack_json):
    with open(stack_json) as f:
        apm_dict = json.load(f)
    for _hits_item in apm_dict['hits']['hits']:
        if _hits_item['_source']['feature'] is null
    print apm_dict['hits']['hits'][0]['_source']['feature'][0]['frame'][0]
    print apm_dict['hits']['hits'][0]['_source']['feature'][0]['frame_str'][0]
    return []

def load_buckets(bucket_json):
    return []

def rebucket(all_stack, buckets):
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
