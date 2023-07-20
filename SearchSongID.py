# 利用 requests 模块，搜索歌曲，获取歌曲 ID。
# -*- coding: utf-8 -*-
import base64
import binascii
import json
import random
import string
from urllib import parse

import requests
from Crypto.Cipher import AES


class SearchID():

    def __init__(self):
        self.search_type = ''
        self.id_li = [0]

    # 1.获取加密后csrf_token的params和encSecKey参数

    # 从a-z,A-Z,0-9中随机获取16位字符
    def get_random(self):
        random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        return random_str


    # AES加密要求加密的文本长度必须是16的倍数，密钥的长度固定只能为16,24或32位，因此我们采取统一转换为16位的方法
    def lenChange(self, text):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        text = text.encode("utf-8")
        return text


    # AES加密方法
    def aes(self, text, key):
        # 首先对加密的内容进行位数补全，然后使用 CBC 模式进行加密
        iv = b'0102030405060708'
        text = self.lenChange(text)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(text)
        encrypt = base64.b64encode(encrypted).decode()
        return encrypt


    # js中的 b 函数，调用两次 AES 加密
    # text 为需要加密的文本， str 为生成的16位随机数
    def b(self, text, str):
        first_data = self.aes(text, '0CoJUm6Qyw8W8jud')
        second_data = self.aes(first_data, str)
        return second_data


    # 这就是那个巨坑的 c 函数
    def c(self, text):
        e = '010001'
        f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        text = text[::-1]
        result = pow(int(binascii.hexlify(text.encode()), 16), int(e, 16), int(f, 16))
        return format(result, 'x').zfill(131)


    # 获取最终的参数 params 和 encSecKey 的方法
    def get_final_param(self, text, str):
        params = self.b(text, str)
        encSecKey = self.c(str)
        return {'params': params, 'encSecKey': encSecKey}


    # 通过参数获取搜索歌曲的列表
    def getMusicList(self, params, encSecKey):
        url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
        payload = 'params=' + parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
        headers = {
            'authority': 'music.163.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://music.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://music.163.com/search/',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:  # 页面正常响应
            return response.text  # 返回页面源代码
        return None


    # 获取歌曲ID(for further usage)和歌曲名称(for display)等信息
    def getReply(self, params, encSecKey):
        url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
        payload = 'params=' + parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
        headers = {
            'authority': 'music.163.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://music.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://music.163.com/',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:  # 页面正常响应
            return response.text  # 返回页面源代码
        return None


    # 获取歌名和id相关的源码
    def get_src_li(self, d):
        d = json.dumps(d)
        random_param = self.get_random()
        param = self.get_final_param(d, random_param)
        src_li = self.getMusicList(param['params'], param['encSecKey'])
        return src_li, random_param


    # 获取歌曲/专辑/歌单的id
    def get_id(self, item, random_param):
        d = {"ids": "[" + str(json.loads(str(item))['id']) + "]", "level": "standard", "encodeType": "",
             "csrf_token": ""}
        d = json.dumps(d)
        param = self.get_final_param(d, random_param)
        song_info = self.getReply(param['params'], param['encSecKey'])
        if len(song_info) > 0:
            song_info = json.loads(song_info)
            song_id = json.dumps(song_info['data'][0]['id'], ensure_ascii=False)
            print('id:', song_id)
            return song_id


    def search_id(self):
    # if __name__ == '__main__':

        # "s": key_word,  "type": "1"/'10'/'1000'(分别对应歌曲、专辑、歌单),
        d = {"csrf_token": "", "hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>",
             "offset": "0",
             "total": "true", "limit": 20}
        while True:
            self.search_type = input('请指定搜索类型（1单曲，2专辑，3歌单，q/Q退出）:')
            if self.search_type == 'q' or self.search_type == 'Q':
                exit()
            if self.search_type not in ['1', '2', '3']:
                continue
            break
        key_word = input('请输入关键字: ')
        d['s'] = key_word
        if self.search_type == '1':
            # https://music.163.com/#/search/m/?s=单车&type=1
            d['type'] = '1'
            src_li, random_param = self.get_src_li(d)
            # print(src_li)
            print('搜索结果如下:')
            src_li = json.loads(src_li)['result']['songs']
            # id_li = [0]  # 序号和id相对应的列表，直接根据序号值作为索引取id
            self.id_li.clear()
            self.id_li.append(0)
            for i, item in enumerate(src_li):
                item = json.dumps(item)
                # 输出歌曲名
                print(str(i + 1) + ".", end=' ')
                print('歌名:', json.loads(str(item))['name'], end='      ')
                print('歌手:', json.loads(str(item))['ar'][0]['name'], end='      ')
                print('所属专辑:《', json.loads(str(item))['al']['name'], end='》      ')
                # 歌曲id。代码测试完毕后可不对用户展示，只展示序号、歌名、相应歌手
                id = self.get_id(item, random_param)
                self.id_li.append(id)


        if self.search_type == '2':
            d['type'] = '10'
            src_li, random_param = self.get_src_li(d)
            print('搜索结果如下:')
            src_li = json.loads(src_li)['result']['albums']
            # id_li = [0]  # 序号和id相对应的列表，直接根据序号值作为索引取id
            self.id_li.clear()
            self.id_li.append(0)
            for i, item in enumerate(src_li):
                item = json.dumps(item)
                # 输出歌曲名
                print(str(i + 1) + ".", end=' ')
                print('专辑名:', json.loads(str(item))['name'], end='      ')
                print('歌手:', json.loads(str(item))['artist']['name'], end='      ')
                # 专辑id，代码测试完毕后不对用户进行展示
                id = self.get_id(item, random_param)
                self.id_li.append(id)

        if self.search_type == '3':
            d['type'] = '1000'
            src_li, random_param = self.get_src_li(d)
            print('搜索结果如下:')
            src_li = json.loads(src_li)['result']['playlists']
            # id_li = [0]  # 序号和id相对应的列表，直接根据序号值作为索引取id
            self.id_li.clear()
            self.id_li.append(0)
            for i, item in enumerate(src_li):
                item = json.dumps(item)
                # 输出歌曲名
                print(str(i + 1) + ".", end=' ')
                print('歌单名:', json.loads(str(item))['name'], end='      ')
                print('创建者:', json.loads(str(item))['creator']['nickname'], end='      ')
                # 歌单id，代码测试完毕后不对用户进行展示
                id = self.get_id(item, random_param)
                self.id_li.append(id)


# id = SearchID()
# id.search_id()