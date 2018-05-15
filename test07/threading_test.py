import time
import threading
from queue import Queue

q = Queue()


def foo(n):
    cur_thread = threading.currentThread().name
    for i in range(10):
        print('{}===={}'.format(cur_thread, i))
        time.sleep(n)


class MyTread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        # self.name = name
        self.queue = queue
        # self.sleep = sleep
        # 可跟随主线程一起退出
        self.setDaemon(True)

    # def run(self):
    #     for i in range(5):
    #         print('{}===={}'.format(self.name, i))
    #         time.sleep(self.sleep)

    def run(self):
        for i in range(10):
            n = self.queue.get()
            print('get', n)



def main():
    # 外部函数的线程
    # for i in range(1, 4):
        # t = threading.Thread(target=foo, args=(i,))
        # t.name = 'T-{}'.format(i)
        # t.start()
    # 继承方式执行线程
    for i in range(1, 4):
        name = 'T-{}'.format(i)
        t = MyTread(name, i)
        t.start()


if __name__ == '__main__':
    main()