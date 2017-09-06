# coding=utf-8
import json
from queue import Queue
from threading import Thread
import requests
from retrying import retry


class ZhuiShu:
    def __init__(self):
        self.url = "http://api.zhuishushenqi.com/ranking/564d8494fe996c25652644d2"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36"
            }
        self.json_queue = Queue()
        self.content_list_queue = Queue()

    @retry(stop_max_attempt_number=3)
    def parse_url(self):
        response = requests.get(self.url, headers=self.headers)
        json_str =  response.content.decode()
        # 把返回的ｊｓｏｎ放到之前创建的ｊｓｏｎ队列中
        self.json_queue.put(json_str)

    def get_content_list(self):
        while True:
            # 从ｊｓｏｎ队列中拿到返回的ｊｓｏｎ
            json_str = self.json_queue.get()
            content_list = []
            # 将获得的ｊｓｏｎ数据转换成字典
            json_dict = json.loads(json_str)
            data_list = json_dict["ranking"]["books"]
            for data in data_list:
                book_info = {}
                book_info["书名"] = data["title"]
                book_info["作者"] = data["author"]
                book_info["追书人数"] = data["latelyFollower"]
                book_info["读者存留率"] = str(data["retentionRatio"])+"%"
                book_info["简介"] = data["shortIntro"]
                content_list.append(book_info)
            # 把拿到的每一本书的详细数据放到之前创建恶毒队列中
            self.content_list_queue.put(content_list)
            self.json_queue.task_done()

    def save(self):
        while True:
            content_list = self.content_list_queue.get()
            with open("追书神器.json", "w", encoding="utf-8") as f:
                for data in content_list:
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
                    f.write("\n")
            print("保存成功")
            self.content_list_queue.task_done()

    def run(self):
        for i in range(4):
            t_parse = Thread(target=self.parse_url)
            t_parse.start()

        for i in range(2):
            t_content_list = Thread(target=self.get_content_list)
            t_content_list.start()
            # t_content_list.join()
        t_save = Thread(target=self.save)
        t_save.start()
        # t_save.join()


if __name__ == '__main__':
    zuishu = ZhuiShu()
    zuishu.run()