#include <iostream>
#include "rebucket.h"
using namespace std;
int main()
{
    cout << "Hello World\n";
    const char* test_stack1 = "{\"stack_id\":\"1\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}";
    const char* test_stack2 = "{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}";
    cout << single_pass_clustering(test_stack1);
    cout << single_pass_clustering(test_stack2);
    return 0;
}
