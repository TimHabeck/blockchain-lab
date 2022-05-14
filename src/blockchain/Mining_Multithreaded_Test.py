import multiprocessing as mp
import hashlib
import time

def mine(start=0, steps=1, times=1000):
    counter = start
    for i in range(times):
        text = b"Content + {counter}"
        t_hash = hashlib.sha256(text).hexdigest()

        important_digits = t_hash[0:5]
        not_null_digits = important_digits.replace("0", "")

        if len(not_null_digits) == 0:
            return True

def setup(target):
    cpus = mp.cpu_count()

    load = int((target/cpus) - (target/cpus)%1)

    processes = []
    manager = mp.Manager()
    return_code = manager.dict()
    run = manager.Event()
    run.set()  # We should keep running.

    for i in range(cpus):
        process = mp.Process(target=mine, args=(i, cpus, load+1))
        processes.append(process)

    print(processes)

    for i in processes:
        i.start()
        print("started")
    
    for i in processes:
        i.join()
        print("ended")
    
    return True


if __name__=="__main__":
    # creating processes for each of the functions
    t1 = time.time()
    """    prc1 = mp.Process(target=mine, args=(0, 1, 300000000))
    prc1.start()
    prc1.join()"""
    setup(300000000)

    t2 = time.time()
    td = t2-t1 
    print(td)
    print("END!")

