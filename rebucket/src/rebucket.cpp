#include "rebucket.h"
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace rapidjson;
int add(int a, int b)
{
    return a + b;
}

int sub(int a, int b)
{
    return a - b;
}
Stack json_to_stack(const char* json)
{
    Stack stack;
    return stack;
}
double get_dist(Stack stack1, Stack stack2)
{
    return 0.3;
}

const char* single_pass_clustering(const char* stack_json)
{
    Document d;
    d.Parse(stack_json);
    // 2. 利用 DOM 作出修改。
    Value& s = d["stack_id"];
    s.SetString("changed");
    // 3. 把 DOM 转换（stringify）成 JSON。
    StringBuffer buffer;
    Writer<StringBuffer> writer(buffer);
    d.Accept(writer);
    // Output {"project":"rapidjson","stars":11}
    char* res = new char[strlen(buffer.GetString())];
    strcpy(res, buffer.GetString());
    return res;
}
void free_buffer(const char* str_ptr)
{
    if(!str_ptr) {
        return;
    }
    delete [] str_ptr;
}