import ctypes
import platform

def main():
    so = ctypes.cdll.LoadLibrary
    sysstr = platform.system()
    if(sysstr =="Windows"):
        lib = so("./librebucket.dll")
    elif(sysstr == "Linux"):
        lib = so("./librebucket.so")
    elif(sysstr == 'Darwin'):
        lib = so("./librebucket.dylib")
    else:
        print ("Other System tasks")

    
    
    # passString
    print('single_pass_clustering')
    test_stack1 = b"{\"stack_id\":\"1\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}"
    test_stack2 = b"{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"a\",\"b\",\"c\",\"d\"]}"
    lib.single_pass_clustering.restype = ctypes.c_char_p
    print(str(lib.single_pass_clustering(ctypes.c_char_p(test_stack1))) + ' in python')
    print('--------------------')
    print(str(lib.single_pass_clustering(ctypes.c_char_p(test_stack2))) + ' in python')

if __name__ == "__main__":
    main()