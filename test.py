from threading import Thread
import time
a = "True"  #global variable
order = "명령"
def thread1(threadname):
    while 1:
        for i in range(5):
            print(order)
        time.sleep(1)

def thread2(threadname):
        global order
        while 1:
                order = "False"
                time.sleep(1)

thread1 = Thread(target=thread1, args=("Thread-1", ))
thread2 = Thread(target=thread2, args=("Thread-2", ))

thread1.start()
thread2.start()

thread1.join()
thread2.join()