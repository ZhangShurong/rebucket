# Rebucket

Rebucket 算法的一个 C++ 实现（用于研究/实验），提供动态库 `librebucket`，并通过 Python `ctypes` 脚本驱动跑数据集。

## 环境依赖

- CMake（建议 >= 3.x；最低兼容 `2.8.12`）
- 支持 OpenMP 的 C++ 编译器（Linux 常见为 GCC/Clang + `libgomp/libomp`）
- Python 3（用于 `ctypes` 驱动脚本）

## 快速开始

在仓库根目录执行：

```bash
cd rebucket
mkdir -p build
cmake -S . -B build
cmake --build build -j

# 运行数据集（注意：需要在 build 目录下运行，脚本会从当前目录加载 ./librebucket.so）
cd build
python3 test.py -d ../../dataset/Firefox/df_mozilla_firefox.json
```

## 测试

```bash
# C++ 单测（在仓库根目录）
ctest --test-dir rebucket/build --output-on-failure

# Python 侧自检（不依赖数据集）
cd rebucket/build
python3 test.py --self-test
```

## 目录结构

- `dataset/`：处理后的数据集（来源于 bugrepo）
- `rebucket/`：C++ 实现 + CMake 构建脚本
- `generate_dataset.py`：从 bugrepo CSV 抽取堆栈并生成本项目使用的 JSON 数据集

## 数据集

原始数据集来自：`https://github.com/logpai/bugrepo`。

本仓库中 `dataset/*/*.json` 的格式为一个数组，每个元素包含一个 issue 的堆栈信息：

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

说明：C++ 核心聚类只使用 `symbol` 序列；`rebucket/test/test.py` 会在运行前把 `stack_arr` 转成字符串数组传入动态库。

## 常见问题

- `test.py` 找不到动态库：请确认在 `rebucket/build` 目录下执行（脚本默认加载 `./librebucket.so`）。
- OpenMP 未找到：请确认编译器/系统已安装 OpenMP 运行库（如 `libgomp1`/`libomp`），并确保 CMake 能 `find_package(OpenMP)`。

## 生成数据集（可选）

`generate_dataset.py` 用于从 bugrepo 的 CSV 中抽取 `Description` 里的 Java 堆栈并生成 `dataset/*/*.json`。
脚本要求 CSV 具备至少三列：`Issue_id`、`Duplicated_issue`、`Description`。

当前脚本使用固定的输入/输出路径数组（见 `generate_dataset.py:186`），将 bugrepo 的原始 CSV 放到对应路径后直接运行：

```bash
python3 generate_dataset.py
```
