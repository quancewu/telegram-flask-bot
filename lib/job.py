import queue
import time
import threading
import queue
import logging
import concurrent.futures

from lib.fn import mytimer

class Job_Service(threading.Thread):
    _job_queue = queue.Queue(maxsize=600)
    
    @classmethod
    def _call(cls,method,chat_id,count,callback):
        cls._job_queue.put(
            (method,chat_id,count,callback)
        )

    @classmethod
    def add_job(cls,chat_id,count,callback):
        print('test for class method')
        cls._call('add_job',chat_id,count,callback)

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.pool_max = 30
        logging.info('Job Service init ...')

    def run(self):
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            while 1:
                if not Job_Service._job_queue.empty():
                    obj = Job_Service._job_queue.get()
                    if len(obj) == 4:
                        method, chat_id, count, callback = obj
                        if method == 'add_job':
                            future = executor.submit(mytimer,(chat_id,count))
                            future.add_done_callback(callback)
                else:
                    time.sleep(0.2)