from multiprocessing import Process, Queue, Lock, Pool
import time
import multiprocessing
import asyncio


async def task(n: int, lock):
    async with lock:
        print(f'n={n}')
    time.sleep(0.25)


if __name__ == '__main__':
    #multiprocessing.set_start_method('forkserver')
    lock = Lock()
    processes = [Process(target=task, args=(i, lock)) for i in range(20)]
    async for process in processes:
        process.start()
    async for process in processes:
        process.join()