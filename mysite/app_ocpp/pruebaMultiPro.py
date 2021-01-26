from threading import Thread

import time
def countdown(n):
    while n > 0:
        n -= 1

COUNT = 10000000

t1 = Thread(target=countdown,args=(COUNT,))
t2 = Thread(target=countdown,args=(COUNT,))
start = time.time()

t1.start();t2.start()
t1.join();t2.join()

end = time.time()
print (end - start)


'''
import multiprocessing
start = time.time()
with multiprocessing.Pool as pool:
    pool.map(countdown, [COUNT/2, COUNT/2])

    pool.close()
    pool.join()

end = time.time()
print(end-start)
'''