import re
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from snownlp import SnowNLP
from collections import Counter
import jieba.analyse
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']

#词云及高频词部分

# 加载jieba的默认词典
jieba.setLogLevel(20)
jieba.initialize()

# 从CSV文件加载评论数据集
df = pd.read_csv("test.csv")

# 预处理评论内容
def preprocess_comments(comments):
    processed_comments = []
    for comment in comments:
        if isinstance(comment, str):
            # 去除数字和特殊符号
            processed_comment = re.sub(r"[^\u4e00-\u9fa5]", "", comment)
            # 分行以及空格处理
            processed_comment = re.sub(r"\s+", "", processed_comment)
            processed_comments.append(processed_comment)
    return processed_comments

# 中文分词和绘制词云图
def process_comments(df):
    comments = df["content"].tolist()

    # 预处理评论内容
    processed_comments = preprocess_comments(comments)

    # 中文分词
    word_list = []
    for comment in processed_comments:
        words = jieba.lcut(comment)
        word_list.extend(words)
    word_list = list(set(word_list))
    print("中文分词结果:", word_list)

    word_string = " ".join(word_list)
    print("转换后的字符串:", word_string)

    # 关键词提取
    keywords = jieba.analyse.extract_tags("".join(processed_comments), topK=10)
    print("关键词：", keywords)



    # 绘制词云图
    wordcloud = WordCloud(font_path="ziti.ttf",
                          background_color="white",  # 设置背景颜色为白色
                          width=800, height=400).generate(word_string)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("./wordcloud.jpg")
    plt.close()  # 关闭图像窗口
    print("词云图已保存为wordcloud.jpg")

    img_path =r"./wordcloud.jpg"
    img = plt.imread(img_path)
    fig = plt.figure('show picture')
    # ax = fig.add_subplot(111)
    plt.imshow(img)
    plt.show()

#点赞分布部分

def likes_distribution():

    # 加载CSV文件
    df = pd.read_csv('test.csv')

    # 获取点赞数列
    likes = df['likedCount']

    # 定义区间和对应的标签
    bins = [0, 9, 99, float('inf')]

    labels = ['0-9', '10-99', '>100']

    # 使用pd.cut函数将点赞数划分到对应的区间，并计算各区间的数量
    like_bins = pd.cut(likes, bins=bins, labels=labels, right=False)
    like_counts = like_bins.value_counts()

    # 绘制扇形图
    #plt.pie(like_counts, labels=like_counts.index, autopct='%1.1f%%')
    plt.pie(like_counts, labels=like_counts.index,autopct='%1.1f%%',pctdistance=0.9,explode=(0,0.2,0.8))

    plt.title('点赞数目分布')
    plt.show()

#情感分析部分

def weight_function(likes):
    # 根据点赞数计算权值，这里使用点赞数作为权值
    return (likes+1)
def multiply_lists(list1, list2):
    return [a*b for a,b in zip(list1, list2)]


def sentiment_analysis():

    # 加载CSV文件
    df = pd.read_csv('test.csv')

    # 获取点赞数和评论内容列
    likes = df['likedCount']
    comments = df['content']

    # 进行情感分析
    sentiments = []
    for comment in comments:
        s = SnowNLP(str(comment))
        sentiments.append(s.sentiments)

    # 计算权值
    weights = [weight_function(like) for like in likes]

    # 绘制散点图
    plt.scatter(sentiments, likes, s=weights, alpha=0.5)
    plt.xlabel('情感分数')
    plt.ylabel('点赞数')
    plt.title('情感分数与点赞数的散点图')
    plt.ylim(0, 100)  # 设置纵坐标范围
    plt.show()

    #绘制扇形图
    # 定义区间和对应的标签
    bins = [0, 0.5, float('inf')]
    labels = ['消极', '积极']

    #加权情感分布目前功能尚不稳定(无专家指导权值参数)
    #weighted_sentiment= multiply_lists(likes, sentiments)
    #使用pd.cut函数将点赞数划分到对应的区间，并计算各区间的数量
    #weighted_sentiment_bins = pd.cut(weighted_sentiment , bins=bins, labels=labels, right=False)
    #weighted_sentiment_counts = weighted_sentiment_bins.value_counts()

    # 绘制扇形图
    #pie(weighted_sentiment_counts, labels=weighted_sentiment_counts.index,autopct='%1.1f%%',pctdistance=0.9)
    #plt.title('加权情感分布')
    #plt.show()

    #以下为非加权的
    # 使用pd.cut函数将点赞数划分到对应的区间，并计算各区间的数量
    sentiment_bins = pd.cut(sentiments , bins=bins, labels=labels, right=False)
    sentiment_counts = sentiment_bins.value_counts()

    # 绘制扇形图
    plt.pie(sentiment_counts, labels=sentiment_counts.index,autopct='%1.1f%%',pctdistance=0.9)
    plt.title('情感分布')
    plt.show()



if __name__ == '__main__':
    result_df = process_comments(df)
    likes_distribution()
    sentiment_analysis()

