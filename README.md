# Rebucket

A research-oriented implementation of the Rebucket clustering algorithm.

- English: see [English](#english)
- 中文：见 [中文](#中文)

---

# English

## Overview

This repository provides:

- A C++ shared library (`librebucket`) implementing a single-pass clustering routine for stack traces
- A Python runner (`rebucket/test/test.py`) using `ctypes` to load the shared library and run on datasets
- A dataset generator (`generate_dataset.py`) to extract Java stack traces from bugrepo CSV and emit JSON

The implementation is intended for research/experimentation, not production.

## Features

- Single-pass clustering API: `single_pass_clustering(const char*) -> const char*`
- Deterministic behavior (fixed a historical OpenMP data race)
- Robust JSON input validation (invalid input returns empty string instead of crashing)
- Test entrypoints: CTest + Python `--self-test`

## Requirements

- CMake (recommended >= 3.x; minimum supported by this repo: `2.8.12`)
- A C++ compiler with OpenMP support
- Python 3

## Build

From the repository root:

```bash
cmake -S rebucket -B rebucket/build
cmake --build rebucket/build -j
```

This produces:

- `rebucket/build/librebucket.so` (Linux)
- `rebucket/build/librebucket.dylib` (macOS)
- `rebucket/build/librebucket.dll` (Windows)

## Usage (Python runner)

The runner loads `./librebucket.*` from the current working directory, so run it inside `rebucket/build`:

```bash
cd rebucket/build
python3 test.py -d ../../dataset/Firefox/df_mozilla_firefox.json
```

## C API

See `rebucket/include/rebucket.h:26`.

- `const char* single_pass_clustering(const char* stack_json)`
  - `stack_json` format: `{"stack_id":"...","stack_arr":["frame1","frame2", ...]}`
  - Returns: bucket id as a NUL-terminated string
  - Invalid input: returns empty string
  - Lifetime: valid until the next call in the same thread
- `void rebucket_reset()` clears internal global buckets
- `size_t rebucket_bucket_count()` returns current bucket count

## Dataset

Raw dataset source: `https://github.com/logpai/bugrepo`.

This repository stores processed datasets as JSON arrays under `dataset/*/*.json`:

```json
[
  {
    "stack_id": "...",
    "duplicated_stack": "...",
    "stack_arr": [
      {"symbol": "a.b.C.m", "file": "C.java", "line": 123}
    ]
  }
]
```

Note: the C++ clustering core uses only the `symbol` sequence. The Python runner converts each `stack_arr` into `{"stack_arr":["symbol", ...]}` before calling into the shared library.

## Generate dataset (optional)

`generate_dataset.py` extracts Java stack traces from bugrepo CSV and emits the JSON format above.

The CSV must contain at least these columns:

- `Issue_id`
- `Duplicated_issue`
- `Description`

Current script uses fixed input/output path arrays (see `generate_dataset.py:186`). After placing CSV files accordingly:

```bash
python3 generate_dataset.py
```

## Tests

```bash
ctest --test-dir rebucket/build --output-on-failure

cd rebucket/build
python3 test.py --self-test
```

## Troubleshooting

- `test.py` cannot find shared library: run it in `rebucket/build` so it can load `./librebucket.*`
- OpenMP not found: install OpenMP runtime (`libgomp`/`libomp`) and ensure CMake can `find_package(OpenMP)`

---

# 中文

## 项目介绍

本仓库包含：

- C++ 动态库 `librebucket`：提供单次扫描（single-pass）的堆栈聚类接口
- Python 驱动脚本 `rebucket/test/test.py`：通过 `ctypes` 加载动态库并跑数据集
- 数据集生成脚本 `generate_dataset.py`：从 bugrepo 的 CSV 中提取 Java 堆栈并生成 JSON

定位是研究/实验用途，不是生产级服务。

## 功能点

- 提供 `single_pass_clustering(const char*) -> const char*` 的 C ABI
- 修复历史 OpenMP 竞态，保证结果稳定
- JSON 输入做了完整校验（非法输入返回空串，不崩溃）
- 提供 CTest + Python 自检入口，便于回归

## 依赖

- CMake（建议 >= 3.x；本仓库最低兼容 `2.8.12`）
- 支持 OpenMP 的 C++ 编译器
- Python 3

## 构建

在仓库根目录执行：

```bash
cmake -S rebucket -B rebucket/build
cmake --build rebucket/build -j
```

产物位于 `rebucket/build`，典型包括：

- Linux：`librebucket.so`
- macOS：`librebucket.dylib`
- Windows：`librebucket.dll`

## 使用（Python 跑数据集）

脚本默认从当前目录加载 `./librebucket.*`，因此需要在 `rebucket/build` 目录下运行：

```bash
cd rebucket/build
python3 test.py -d ../../dataset/Firefox/df_mozilla_firefox.json
```

## C 接口说明

接口定义见 `rebucket/include/rebucket.h:26`。

- `single_pass_clustering(stack_json)`：输入一条堆栈（JSON），返回其所属的 bucket id
  - 输入格式：`{"stack_id":"...","stack_arr":["frame1","frame2", ...]}`
  - 非法输入：返回空串
  - 返回值生命周期：同一线程内“下一次调用之前”有效
- `rebucket_reset()`：清空内部桶状态
- `rebucket_bucket_count()`：获取当前桶数量

## 数据集

原始数据集来源：`https://github.com/logpai/bugrepo`。

本仓库 `dataset/*/*.json` 为处理后的数据集，格式为数组，每个元素包含一个 issue 的堆栈：

```json
[
  {
    "stack_id": "...",
    "duplicated_stack": "...",
    "stack_arr": [
      {"symbol": "a.b.C.m", "file": "C.java", "line": 123}
    ]
  }
]
```

说明：C++ 核心聚类只使用 `symbol` 序列；`rebucket/test/test.py` 会把每条记录的 `stack_arr` 转为 symbol 字符串数组后再调用动态库。

## 生成数据集（可选）

`generate_dataset.py` 从 bugrepo 的 CSV 中提取 `Description` 里的 Java 堆栈并生成上述 JSON。
CSV 至少需要三列：`Issue_id`、`Duplicated_issue`、`Description`。

当前脚本使用固定的输入/输出路径数组（见 `generate_dataset.py:186`），把 CSV 放到对应路径后运行：

```bash
python3 generate_dataset.py
```

## 测试

```bash
ctest --test-dir rebucket/build --output-on-failure

cd rebucket/build
python3 test.py --self-test
```

## 常见问题

- `test.py` 找不到动态库：请确认在 `rebucket/build` 目录下执行（脚本加载 `./librebucket.*`）
- OpenMP 未找到：请安装 OpenMP 运行库（如 `libgomp`/`libomp`），并确保 CMake 能 `find_package(OpenMP)`
