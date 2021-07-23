import os
import time

def mytimer(args):
    print(args)
    chat_id, count = args
    print('<Process% s> timer % s' %(os.getpid(),count))
    for i in range(count):
        # print(f"time wait {i}")
        time.sleep(1)
    return {'chat_id': chat_id}