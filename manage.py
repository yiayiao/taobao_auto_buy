import argparse
import os

from bin.tb import Taobao
from bin.tm_market import TM_Market
from lib.utils import read, welcome


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str, help="商品网站链接")
    parser.add_argument("-t", "--time", type=str, help="抢购时间, 格式参考 2020-01-09 20:00:00")
    args = parser.parse_args()

    if args.url and args.time:
        welcome("Command Line 参数读取成功", args.url, args.time)
        config = {"target_url": args.url, "buy_time": args.time}
    else:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config/config.json"))
        config = read(config_path)
        welcome("Config Json 参数读取成功", config["target_url"], config["buy_time"])

    if "tmail" in config["target_url"]:
        chaoshi = TM_Market(**config)
        chaoshi.start()
    else:
        taobao = Taobao(**config)
        taobao.start()


if __name__ == "__main__":
    main()
