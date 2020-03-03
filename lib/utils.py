import os
import json
import logging
import time
def read(config_path):
    with open(config_path, "r") as f:
        return json.load(f)

def welcome(message, url, time):
    logging.basicConfig(level = logging.INFO)
    logging.info(message)
    logging.info(f"商品链接为 : {url}")
    logging.info(f"抢购时间为 : {time}")

class BenchmarkTimer(object):

    def __init__(self, logger):
        self._start = time.time()
        self._logger = logger

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self._start
        msg = "took {time} seconds to complete"
        self._logger.info(msg.format(time=runtime))



def test():
    a = 1
    for i in range(10000):
        a+=i

def main():
    with BenchmarkTimer():
        test()

if __name__ == "__main__":
    main()
