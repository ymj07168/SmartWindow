# from multiprocessing import Process, Pipe
#
# def func0(pipe):
#     pipe.send("hello world")
#     pipe.close()
#
# def func1(pipe):
#     print(pipe)
#
# if __name__ == '__main__':
#     a_pipe, b_pipe = Pipe()
#     p0 = Process(target=func0, args=(a_pipe,))
#     p0.start()
#     p1 = Process(target=func1, args=(b_pipe.recv(),))
#     p1.start()
#
#     p0.join()
#     p1.join()

from multiprocessing import Process, Pipe

is_open = 0
def f(conn):
    while 1:
        is_open = conn.recv()
        print(is_open) # prints "[31, None, 'send from parent_conn']"
        is_open = 0
        conn.send(is_open)

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    parent_conn.send(1)
    p = Process(target=f, args=(child_conn,))
    p.start()
    is_open = parent_conn.recv()
    print(is_open)   # prints "[42, None, 'send from child_conn']"
    p.join()