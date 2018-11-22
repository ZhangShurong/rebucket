#ifndef _MYMATH_H_
#define _MYMATH_H_
#include <iostream>
#include <vector>
using namespace std;
struct stack{
    string stack_id;
    vector<string> frames;
};
struct bucket{
    
};
extern "C" {  
int add(int a, int b);
int sub(int a, int b);
const char* single_pass_clustering(const char* stack_json);
}

#endif
