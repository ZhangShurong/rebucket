#include <iostream>
#include "rebucket.h"
using namespace std;
int main()
{
    cout << "Hello World\n";
    const char* test_stack1 = "{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}";
    cout << single_pass_clustering(test_stack1);
    return 0;
}
