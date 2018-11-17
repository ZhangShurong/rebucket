from multiprocessing import  Queue
from threading import Thread
import time
import rebucket

def read_stack(q):
    for i in range(10):
        q.put(i)
        time.sleep(0.5)
    print("end producer")

def get_stack(q):
    while 1:
        stack = q.get()
        print rebucket.query(stack)
def main():
    q = Queue()
    pro = Thread(target=read_stack, args=(q,))
    cus = Thread(target=get_stack,args=(q,))
    pro.start()
    cus.start()
    pass
if __name__ == "__main__":
    main()