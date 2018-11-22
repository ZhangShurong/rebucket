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
    return buffer.GetString();
}