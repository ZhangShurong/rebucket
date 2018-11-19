'''
bug report csv format:
    Issue_id,Priority,Component,Duplicated_issue,Title,Description,Status,Resolution,Version,Created_time,Resolved_time

data set json format:
    {stack_id:111, bucket_id:10, stacks:[a,b,c,d,], order:1(hight-to-low), source: 'apm/eclipse'}

This script:
    1. read ori bug report
    2. extract stack trace
    3. generate dataset

'''
from rebucket import Stack, Frame
import re
import json

class StackTraceExtractor:
    def __init__(self):
        self.JAVA_TRACE = r'\s*?at\s+([\w<>\$_]+\.)+([\w<>\$_]+)\s*\((.+?)\.java:?(\d+)?\)'

        # These two are for more 'strict' stack trace finding
        self.JAVA_EXCEPTION = r'\n(([\w<>\$_]++\.?)++[\w<>\$_]*+(Exception|Error){1}(\s|:))'
        self.JAVA_CAUSE = r'(Caused by:).*?(Exception|Error)(.*?)(\s+at.*?\(.*?:\d+\))+'
        self.RE_FLAGS = re.I | re.M | re.S

    def find_stack_traces(self, s):
        stack_traces = []

        for r in re.findall(re.compile(self.JAVA_TRACE, self.RE_FLAGS), s):
            if "Native Method" not in r[2]:
                item = (r[0] + r[1], r[2] + ":" + r[3])
                if item not in stack_traces:
                    stack_traces.append(item)

        return stack_traces

def load_stacks(bug_report_csv):
    with open(bug_report_csv) as f:
        lines = f.readlines()
    stackTraceExtractor = StackTraceExtractor()
    stacks = []
    for line in lines:
        issue_id = line.split(',')[0]
        duplicated_issue = line.split(',')[3]
        duplicates_id = None
        description = line.split(',')[5]
        ori_frames = stackTraceExtractor.find_stack_traces(description)
        frames = []
        if len(ori_frames) is 0:
            continue
        if len(duplicated_issue) is not 0:
            duplicates_id = duplicated_issue.split('.')[0]
        for ori_frame in ori_frames:
            frame_dict = dict()
            frame_dict['symbol'] = ori_frame[0].strip()
            frame_dict['file'] = ori_frame[1].split(':')[0]
            try:
                frame_dict['line'] = int(ori_frame[1].split(':')[1])
            except ValueError:
                frame_dict['line'] = 0
            frame = Frame(frame_dict)
            frames.append(frame)
        stack = Stack(issue_id, frames, duplicates_id)
        stacks.append(stack)
    return stacks

def save_json(output_json, stacks):
    with open(output_json, 'w') as fb_output:
        output_json_arr = []
        for stack in stacks:
            stack_dict = dict()
            stack_dict['stack_id'] = stack.id
            stack_dict['duplicated_stack'] = stack.duplicated_stack
            stack_dict['stack_arr'] = []
            for frame in stack.stack_arr:
                frame_dict = dict()
                frame_dict['symbol'] = frame.symbol
                frame_dict['file'] = frame.file
                frame_dict['line'] = frame.line
                stack_dict['stack_arr'].append(frame_dict)
            output_json_arr.append(stack_dict)
        json.dump(output_json_arr, fb_output)

def main():
    # ori_data_path = 'dataset/Thunderbird/mozilla_thunderbird.csv'
    # output_data_path = 'dataset/Thunderbird/df_mozilla_thunderbird.json'
    ori_data_path = 'dataset/Firefox/mozilla_firefox.csv'
    output_data_path = 'dataset/Firefox/df_mozilla_firefox.json'
    stacks = load_stacks(ori_data_path)
    save_json(output_data_path, stacks)
if __name__ == "__main__":
    main()
