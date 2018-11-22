#ifndef _MYMATH_H_
#define _MYMATH_H_
#include <iostream>
#include <vector>
using namespace std;
struct Stack{
    string stack_id;
    vector<string> frames;
};

struct Sucket{
    string bucket_id;
    vector<string> stack_ids;
};

extern "C" {  
int add(int a, int b);
int sub(int a, int b);
const char* single_pass_clustering(const char* stack_json);
void free_buffer(const char* str_ptr);
}

#endif
