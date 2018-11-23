#include <iostream>
#include "rebucket.h"
using namespace std;
int main()
{
    cout << "Hello World\n";
    const char* test_stack1 = "{\"stack_id\":\"1\",\"stack_arr\":[\"c\",\"b\",\"a\",\"b\",\"c\",\"d\"]}";
    const char* test_stack2 = "{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}";
     const char* test_stack3 = "{\"stack_id\":\"3\",\"stack_arr\":[\"x\",\"y\",\"z\",\"b\",\"c\",\"d\"]}";
    cout << single_pass_clustering(test_stack1);
    cout << single_pass_clustering(test_stack2);
    cout << single_pass_clustering(test_stack3);
    return 0;
}
