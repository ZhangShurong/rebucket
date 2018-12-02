# rebucket
implements rebucket algorithm for research.

## How To Use? 
Usage:
python test.py

## dataset
https://github.com/logpai/bugrepo

## Implement
todo 
- [x] implements rebucket algorithm with c++
- [ ] data strcuture
------
以下为中文说明
# Rebucket算法实现
如果是南科大的小伙伴碰巧找到了本项目，可以看看issue哦。

算法本身请参见rebucket论文，本文档只说明项目相关内容
## 项目结构
rebucket  
|  
|---- dataset, 处理后的数据集  
|  
|---- rebucket, C++实现rebucket   
|  
|---- generate_dataset.py， 生成数据集的脚本  
|  
|---- test.py 测试脚本  
|  
|---- rebucket.py 算法脚本  

## 数据集处理部分
**为什么需要处理数据集**
因为原始的数据集bugrepo并不是每个记录都含有堆栈，因此需要提取出堆栈信息，声称可用的数据集。生成数据集的脚本是generate_dataset.py。生成数据集的位置在dataset中。  
数据集提取算法为：  

http://groups.csail.mit.edu/pag/pubs/bettenburg-msr-2008.pdf

**数据集格式**  
因为数据量不大且为了兼容其他项目，因此数据集采用的是json字符串存储。其格式为
```
{
    "stack_id":"堆栈ID",
    "duplicated_stack":"重复堆栈ID",
    "stack_arr":[堆栈内容，用数组表示]
}
```
## 验证算法部分
因为原始的论文中已经提供了详细的度量值，本文只简单描述如何计算分类错误数。  
假设正确的分类应该是
```
{[1,2,3],[4,5,6],[7,8]}
```
但是由于种种原因，分类错误，导致了以下分类结果：
```
{[1,2],[3],[4,5,6,7,8]}
```
上述过程的漏报数为1，因为7,8这两个堆栈均被分到了4,5,6中，意味着，有**一类**错误没有反应出来。或者换种说法，意味着生产环境中，有一类错误没有上报。  
计算漏报数非常简单，只需要对比分类结果与真实结果，找出哪一类没有被分类即可。相关代码在rebucket.py中的wrong函数中。

## 如何运行c++代码？
进入rebucket目录
```
mkdir build
cmake ..
make
```
此时，build目录下面会有动态连接库以及test.py，请执行
```
python test.py -d ../../dataset/Firefox/df_mozilla_firefox.json
```


