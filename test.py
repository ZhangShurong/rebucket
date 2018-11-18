import json
import rebucket
from rebucket import Stack
from rebucket import Frame

def read_dataset(json_path):
    with open(json_path) as json_file:
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
def main():
    json_path = 'dataset/eclipse/df_eclipse.json'
    all_stacks = read_dataset(json_path)
    print len(rebucket.clustering(all_stacks))
if __name__ == "__main__":
    main()