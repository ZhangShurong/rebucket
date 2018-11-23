#ifndef _MYMATH_H_
#define _MYMATH_H_
#include <iostream>
#include <vector>
using namespace std;
struct Stack{
    string stack_id;
    vector<string> frames;
};

struct Bucket{
    string bucket_id;
    vector<Stack> stacks;
};

extern "C" {  
const char* single_pass_clustering(const char* stack_json);
void free_buffer(const char* str_ptr);
}

#endif
