"""Generate rebucket dataset from bugrepo csv.

Bug report CSV format (header expected):
    Issue_id,Priority,Component,Duplicated_issue,Title,Description,Status,Resolution,Version,Created_time,Resolved_time

Output JSON format:
    [{"stack_id": "...", "duplicated_stack": "...", "stack_arr": [{"symbol":...,"file":...,"line":...}, ...]}, ...]

This script:
    1) read raw bug report csv
    2) extract Java stack traces from Description
    3) generate a cleaned dataset json
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


@dataclass
class Frame:
    """One stack frame."""

    symbol: str
    file: str
    line: int


@dataclass
class Stack:
    """One stack trace sample."""

    id: str
    stack_arr: List[Frame]
    duplicated_stack: Optional[str] = None

class StackTraceExtractor:
    def __init__(self):
        self.JAVA_TRACE = r'\s*?at\s+([\w<>\$_]+\.)+([\w<>\$_]+)\s*\((.+?)\.java:?(-\d+|\d+)?\)'

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

def _pick_duplicated_stack(raw: str) -> Optional[str]:
    """Pick one duplicated issue id from bugrepo field.

    bugrepo's duplicated issue field may contain multiple ids separated by '.', and can include '0'.
    For dataset generation we keep at most one id to keep downstream logic simple.
    """

    raw = (raw or "").strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split('.') if p.strip() and p.strip() != '0']
    if not parts:
        return None
    return parts[0]


def load_stacks(bug_report_csv: str) -> List[Stack]:
    with open(bug_report_csv, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []

    header = [h.strip() for h in rows[0]]
    index = {name: i for i, name in enumerate(header)}
    required = ["Issue_id", "Duplicated_issue", "Description"]
    for name in required:
        if name not in index:
            raise ValueError("CSV missing required column: %s" % name)

    stackTraceExtractor = StackTraceExtractor()
    stacks = []
    for row in rows[1:]:
        if len(row) < len(header):
            # Skip malformed rows.
            continue

        issue_id = row[index["Issue_id"]].strip()
        duplicated_issue = row[index["Duplicated_issue"]]
        duplicates_id = _pick_duplicated_stack(duplicated_issue)
        description = row[index["Description"]]
        ori_frames = stackTraceExtractor.find_stack_traces(description)
        frames = []
        if len(ori_frames) == 0:
            continue

        for ori_frame in ori_frames:
            frame_dict = dict()
            frame_dict['symbol'] = ori_frame[0].strip()
            frame_dict['file'] = ori_frame[1].split(':')[0]
            try:
                frame_dict['line'] = int(ori_frame[1].split(':')[1])
            except ValueError:
                frame_dict['line'] = 0
            frame = Frame(symbol=frame_dict['symbol'], file=frame_dict['file'], line=frame_dict['line'])
            frames.append(frame)
        stack = Stack(issue_id, frames, duplicates_id)
        stacks.append(stack)
    return stacks

def save_json(output_json: str, stacks: Sequence[Stack]) -> None:
    with open(output_json, 'w', encoding='utf-8') as fb_output:
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
        json.dump(output_json_arr, fb_output, ensure_ascii=False)

def compare_stack(stack1: Stack, stack2: Stack) -> bool:
    min_len = min([len(stack1.stack_arr),len(stack2.stack_arr)])
    for i in range(0, min_len):
        if stack1.stack_arr[i].symbol != stack2.stack_arr[i].symbol:
            return False
    return True

def same_filter(stacks: List[Stack]) -> List[Stack]:
    duplicated_stack_arr = []

    for i, stack in enumerate(stacks):
        for j in range(i + 1, len(stacks)):
            if compare_stack(stack, stacks[j]):
                if stack.duplicated_stack in duplicated_stack_arr:
                    continue
                if stack.duplicated_stack:
                    continue
                duplicated_stack_arr.append(stack.id)
                stacks[j].duplicated_stack = stack.id
    return stacks
        
def generate_realbuckets(stacks: Sequence[Stack]):

    real_buckets = []

    for stack in stacks:
        found = False
        for bucket in real_buckets:
            if stack.id in bucket and stack.duplicated_stack in bucket:
                found = True
                break
            if stack.id not in bucket and stack.duplicated_stack not in bucket:
                continue
                # real_buckets.append([stack.id])
            if stack.id in bucket:
                for d_stack in stacks:
                    if d_stack.id == stack.duplicated_stack:
                        bucket.append(d_stack.id)
            else:
                bucket.append(stack.id)
            found = True
        if not found:
            real_buckets.append([stack.id])
            if stack.duplicated_stack:
                for d_stack in stacks:
                    if d_stack.id == stack.duplicated_stack:
                        real_buckets[-1].append(d_stack.id)
    return real_buckets
def main():
    input_arr = ['dataset/Thunderbird/mozilla_thunderbird.csv', 'dataset/Firefox/mozilla_firefox.csv',
    'dataset/eclipse/eclipse_platform.csv', 'dataset/JDT/eclipse_jdt.csv', 'dataset/mozilla_core/mozilla_core.csv']
    output_arr = ['dataset/Thunderbird/df_mozilla_thunderbird.json', 'dataset/Firefox/df_mozilla_firefox.json',
    'dataset/eclipse/df_eclipse.json', 'dataset/JDT/df_eclipse_jdt.json', 'dataset/mozilla_core/df_mozilla_core.json']
    # ori_data_path = 'dataset/Thunderbird/mozilla_thunderbird.csv'
    # output_data_path = 'dataset/Thunderbird/df_mozilla_thunderbird.json'
    # ori_data_path = 'dataset/Firefox/mozilla_firefox.csv'
    # output_data_path = 'dataset/Firefox/df_mozilla_firefox.json'
    # ori_data_path = 'dataset/eclipse/eclipse_platform.csv'
    # output_data_path = 'dataset/eclipse/df_eclipse.json'
    # ori_data_path = 'dataset/JDT/eclipse_jdt.csv'
    # output_data_path = 'dataset/JDT/df_eclipse_jdt.json'
    # ori_data_path = 'dataset/mozilla_core/mozilla_core.csv'
    # output_data_path = 'dataset/mozilla_core/df_mozilla_core.json'

    for index, input_csv in enumerate(input_arr):
        stacks = load_stacks(input_csv)
        print(len(generate_realbuckets(stacks)))
        stacks = same_filter(stacks)
        print(len(generate_realbuckets(stacks)))
        save_json(output_arr[index], stacks)
        
if __name__ == "__main__":
    main()
