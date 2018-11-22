import ctypes  
so = ctypes.cdll.LoadLibrary   
lib = so("./librebucket.dylib")   

print lib.add(1, 2)  
