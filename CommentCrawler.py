#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math

import SearchSongID
import requests
import random
import json
import time
import pandas as pd
from urllib import parse

from SearchSongID import SearchID

# 定义全局变量
commentId = []  # 评论id
nickname = []  # 用户昵称
userId = []  # 用户ID
content = []  # 评论内容
likedCount = []  # 点赞数
commentTimestamp = []  # 评论时间戳


# 根据记录总数计算要抓取的页数
def countPages(total, limit):
    """ Count pages
    @ param total: total num of records, int
    @ param limit: limit per page, int
    @ return page: num of pages, int
    """
    pageCount = math.ceil(total / limit)
    return pageCount


def get_one_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  # 页面正常响应
        return response.text  # 返回页面源代码
    return None


# 解析一页数据
def parse_one_page(html):
    data = json.loads(html)['comments']  # 评论以json形式存储,故以json形式截取
    for item in data:
        likedCount.append(item['likedCount'])  # 点赞数
        content.append(item['content']),  # 评论内容
        commentId.append(item['commentId']),  # 评论id
        nickname.append(item['user']['nickname']),  # 评论用户名
        userId.append(item['user']['userId']),  # 评论用户id
        timestamp = int(time.mktime(time.localtime(int(str(item['time'])[:10]))))  # 评论时间
        commentTimestamp.append(timestamp)
        # print('评论内容:', item['content'], '    评论用户名:', item['user']['nickname'], '    评论id:', item['commentId'], '    评论用户的id:', item['user']['userId'], '    点赞数:', item['likedCount'])


def get_user_info(user_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    url = 'https://music.163.com/api/v1/user/detail/' + str(user_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  # 页面正常响应
        return response.text  # 返回页面源代码
    return None


def parse_user_info(user_id):
    data = json.loads(get_user_info(user_id))['profile']
    birthday = data['birthday']
    gender_num = data['gender']
    province = data['province']
    if gender_num == 1:
        gender = '男'
    else:
        gender = '女'
    print('gender:', gender, 'birthday:', birthday, 'province:', province, )
    # return gender, birthday, province


# 保存数据到文本文档
def get_comment(search_type, id):
    url1 = 'http://music.163.com/api/v1/resource/comments/'
    url2 = ''
    if search_type == '1':
        url2 = 'R_SO_4_'
    elif search_type == '2':
        url2 = 'R_AL_3_'
    elif search_type == '3':
        url2 = 'A_PL_0_'
    url3 = url1 + url2 + id
    html = get_one_page(url3)
    TOTAL_NUM = json.loads(html)['total']
    print('评论总数目为:', TOTAL_NUM)

    for i in range(0, TOTAL_NUM, 20):
        try:
            new_url = url3 + '?limit=20&offset=' + str(i)  # str(20 * (i - 1))  # 歌曲

            page_seq = i // 20 + 1
            if TOTAL_NUM > 20000:
                if page_seq <= 500 or page_seq >= TOTAL_NUM // 20 - 498:  # 前500页和后500页
                    html = get_one_page(new_url)
                    parse_one_page(html)
                    if page_seq % 10 == 1:
                        print('第%d页~%d页评论已保存.' % (page_seq, page_seq + 9))
                        # time.sleep(5 + float(random.randint(1, 50)) / 20)
            elif TOTAL_NUM > 10000:  # 大于500页小于1000页
                if page_seq % 10 == 1:
                    html = get_one_page(new_url)
                    parse_one_page(html)
                    print('第%d页~%d页评论已保存.' % (page_seq, page_seq + 9))
                    # time.sleep(5 + float(random.randint(1, 50)) / 20)
            elif TOTAL_NUM > 200:  # 小于500页
                if page_seq % 10 == 1:
                    html = get_one_page(new_url)
                    parse_one_page(html)
                    print('第%d页~%d页评论已保存.' % (page_seq, page_seq + 9))
            else:
                print('第%d页评论已保存.' % page_seq)
        except:
            return


TOTAL_NUM = 0
if __name__ == '__main__':
    while True:
        c = SearchID()
        c.search_id()
        search_type = c.search_type
        seq = int(input('请输入待爬取评论的对象所对应的序号：'))
        id = c.id_li[seq]
        get_comment(search_type, id)
        song_comment = {'likedCount': likedCount, 'content': content, 'commentId': commentId, 'nickname': nickname,
                        'userId': userId, 'commentTimestamp': commentTimestamp}
        song_comment = pd.DataFrame(song_comment, columns=['likedCount', 'content', 'commentId', 'nickname', 'userId',
                                                           'commentTimestamp'])
        song_comment.to_csv("test.csv", encoding="utf_8_sig", index=False)
        # 可根据查询到的用户id进行用户信息的查询
        # while True:
        #     user_id = input('请输入用户id（退出按q/Q）：')
        #     if user_id == 'q' or user_id == 'Q':
        #         break
        #     parse_user_info(user_id)
