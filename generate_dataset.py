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
    for line in lines:
        issue_id = line.split(',')[0]
        duplicated_issue = line.split(',')[3]
        description = line.split(',')[5]
        s = stackTraceExtractor.find_stack_traces(description)
        if len(s) is not 0:
            print s
            exit(0)
    return []

def save_json(output_json, stacks):
    pass

def main():
    ori_data_path = 'ignore/bugrepo-master/EclipsePlatform/eclipse_platform/eclipse_platform.csv'
    output_data_path = 'apm_data/df_eclipse.json'
    stacks = load_stacks(ori_data_path)
    save_json(output_data_path, stacks)
if __name__ == "__main__":
    main()
