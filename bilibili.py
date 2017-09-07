# coding=utf-8
import json
from queue import Queue
from threading import Thread
import requests


class BiliBili:
    def __init__(self):
        # 设置起始的url
        self.url = "https://s.search.bilibili.com/cate/search?main_ver=v3&search_type=video&view_type=hot_rank&pic_size=160x100&order=click&copy_right=-1&cate_id=32&page={}&pagesize=20&time_from=20170618&time_to=20170825"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
        }
        # 创建一个ｕｒｌ的队列
        self.url_queue = Queue()
        # 创建一个ｊｓｏｎ的队列，存放响应返回的ｊｓｏｎ数据
        self.json_queue = Queue()
        # 创建一个ｄａｔａ＿ｌｉｓｔ队列存放解析好的数据
        self.data_list_queue = Queue()

    def get_url_list(self):
        url_list = []
        # 找到ｕｒｌ变化的规律，经过遍历获得到所有的ｕｒｌ
        for i in range(1, 50):
            # 把获得的ｕｒｌ放到ｕｒｌ队列中
            self.url_queue.put(self.url.format(i))
            # url_list.append(self.url.format(i))
        # return url_list

    def parse_url(self):
        while True:
            # 从队列中拿出ｕｒｌ进行解析
            url = self.url_queue.get()
            try:
                # 接受返回的响应
                response = requests.get(url, headers=self.headers)
                # 解码，获得ｊｓｏｎ数据
                json_str = response.content.decode()
            except Exception as e:
                print(e)
                json_str = None
            # 把ｊｓｏｎ数据放到ｊｓｏｎ队列中
            self.json_queue.put(json_str)
            # 结束一次ｕｒｌ队列的获取
            self.url_queue.task_done()

    def get_data_list(self):
        while True:
            # 从ｊｓｏｎ队列中拿出ｊｓｏｎ数据
            json_str = self.json_queue.get()
            if json_str is not None:
                # 创建一个空的列表
                data_list = []
                # 将ｊｓｏｎ数据转换成字典
                json_dict = json.loads(json_str)
                # 取出字典的ｒｅｓｕｌｔ，获得的是整个数据列表
                # 遍历列表获取单个数据
                for data in json_dict["result"]:
                    # 构造一个字典,把想要获取的字段添加到字典中去
                    data_dict = {}
                    data_dict["标题"] = data["title"]
                    data_dict["分区"] = data["author"]
                    data_dict["上传时间"] = data["pubdate"]
                    data_dict["视频链接"] = data["arcurl"]
                    data_dict["描述"] = data["description"]
                    # 将添加好数据的字典放到之前建立的列表中去，一个字典代表一个单独的数据
                    data_list.append(data_dict)
                # 将整个列表添加到队列
                self.data_list_queue.put(data_list)
            # 结束
            self.json_queue.task_done()

    def save_data_list(self):
        while True:
            # 把列表从队列里拿出来
            data_list = self.data_list_queue.get()
            # 以ｊｓｏｎ格式保存文件
            with open("bilibili.json", "a", encoding="utf-8") as f:
                # 遍历整个列表，一个ｄａｔａ就是之前构造的字典
                for data in data_list:
                    # 转换格式
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
                    f.write("\n")
            print("保存成功")
            # 关闭
            self.data_list_queue.task_done()

    def run(self):
        # 创建一个线程列表
        thread_list = []
        # 创建一个获取ｕｒｌ列表的线程
        t_url = Thread(target=self.get_url_list)
        # 将线程添加到列表
        thread_list.append(t_url)
        for i in range(4):
            # 创建四个线程解析ｕｒｌ
            t_parse = Thread(target=self.parse_url)
            thread_list.append(t_parse)
        for i in range(2):
            # 创建两个线程解析数据
            t_data_list = Thread(target=self.get_data_list)
            thread_list.append(t_data_list)
        # 创建一个保存文件的线程
        t_save = Thread(target=self.save_data_list)
        thread_list.append(t_save)
        # 遍历线程列表，并逐个启动
        for t in thread_list:
            # 设置为守护线程,主线程结束,子线程结束
            t.setDaemon(True)
            t.start()

        for q in [self.url_queue, self.json_queue, self.data_list_queue]:
            # 让主线程等待队列任务
            q.join()

if __name__ == '__main__':
    bilibili = BiliBili()
    bilibili.run()