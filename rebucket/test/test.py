import ctypes  
so = ctypes.cdll.LoadLibrary   
lib = so("./librebucket.dylib")   
# passString
print('single_pass_clustering')
test_stack1 = b"{\"stack_id\":\"1\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}"
test_stack1 = b"{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}"
lib.single_pass_clustering.restype = ctypes.c_char_p
print(str(lib.single_pass_clustering(ctypes.c_char_p(test_stack1))) + ' in python')
print('--------------------')
print lib.add(1, 2)  
