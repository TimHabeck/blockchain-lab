from itertools import count
import multiprocessing as mp
import hashlib
import time

def mine(shared_dict, start=0, steps=1, times=1000000):
    counter = start
    print(f"starting to hash at {counter}")
    for i in range(times):
        text = b"Contdentd hahahahsdfasfgafawefaawerfgawrhah"
        t_hash = hashlib.sha256(text)
        t_hash.update(str(counter).encode("ASCII"))
        t_hash = t_hash.hexdigest()
        important_digits = t_hash[0:5]
        not_null_digits = important_digits.replace("0", "")

        if len(not_null_digits) == 0:
            shared_dict["nonce"] = i
            print(f"process {start} finished successfull")
            print(t_hash)
            return True

        counter += steps
    print(f"process {start} finished not successfull")

def setup(target):
    cpus = mp.cpu_count()

    load = int((target/cpus) - (target/cpus)%1)

    processes = []
    manager = mp.Manager()
    shared_dict = manager.dict()
    shared_dict["nonce"] = None
    shared_dict["finished"] = []
    run = manager.Event()
    run.set()  # We should keep running.

    for i in range(cpus):
        process = mp.Process(target=mine, args=(shared_dict, i, cpus, load+1))
        processes.append(process)

    print(processes)

    for i in processes:
        if shared_dict["nonce"] is None:
            i.start()
        else:
            break
        time.sleep(0.1)
    
    while True:
        if shared_dict["nonce"] is not None:
            print("nonce found")
            for i in processes:
                if i.is_alive():
                    i.terminate()
            break
        elif len(shared_dict["finished"]) == cpus:
            print("Nothing found")
            break
        else:
            time.sleep(0.1)

    print("something happended")
    
    return shared_dict["nonce"]


if __name__=="__main__":
    # creating processes for each of the functions
    t1 = time.time()
    print("Nonce:",setup(300000000))

    t2 = time.time()
    td = t2-t1 
    print(td)
    print("END!")

