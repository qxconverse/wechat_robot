import os
import re

import PIL.Image as Image
import itchat
import jieba
import matplotlib.pyplot as plt
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Map, Pie
from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot
from wordcloud import WordCloud, ImageColorGenerator

friends_province_path = os.getcwd() + "/pic/%s-微信好友省份分布图.%s"
friends_gender_path = os.getcwd() + "/pic/%s-微信好友性别分布图.%s"

gender_dis = {
    1: "男",
    2: "女",
    0: "其它"
}


def get_friends():
    return itchat.get_friends(update=False)


def get_self_info():
    return itchat.search_friends()


def show_friend_info(friend):
    print("昵称：" + friend['NickName'])
    print("省份：" + friend['Province'])
    print("城市：" + friend['City'])
    print("性别：" + gender_dis[friend['Sex']])
    print("备注名：" + friend['RemarkName'])
    print("个人签名：" + friend['Signature'])


def search_friend(name):
    # 使用search_friends方法可以搜索用户，有四种搜索方式： 1. 仅获取自己的用户信息 2. 获取特定UserName的用户信息
    # 3. 获取备注、微信号、昵称中的任何一项等于name键值的用户 4. 获取备注、微信号、昵称分别等于相应键值的用户
    return itchat.search_friends(name=name)[0]


def gen_sex_distribution(save_pic=False):
    friends_list = get_friends()
    male = female = other = 0

    # 1表示男性，2女性
    for i in friends_list[1:]:
        sex = i["Sex"]
        if sex == 1:
            male += 1
        elif sex == 2:
            female += 1
        else:
            other += 1

    gender_type = ["男性", "女性", "其它"]
    gender_num = [male, female, other]

    c = (
        Pie()
            .add("", [list(z) for z in zip(gender_type, gender_num)])
            .set_global_opts(title_opts=opts.TitleOpts(title="微信好友性别分布"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    c.render(friends_gender_path % (get_self_info()["NickName"], 'html'))
    if save_pic:
        save_path = friends_gender_path % (get_self_info()["NickName"], 'png')
        make_snapshot(snapshot, c.render(), save_path)
        itchat.send('这是你微信好友的性别分布图', toUserName='filehelper')
        itchat.send_image(save_path, toUserName='filehelper')


def gen_province_distribution(save_pic=False):
    friends_list = get_friends()
    province_distribution = {}
    for i in friends_list[1:]:
        province = i['Province']
        if province not in province_distribution:
            province_distribution[province] = 1
        else:
            province_distribution[province] += 1

    province = list(province_distribution.keys())
    values = list(province_distribution.values())

    c = (
        Map()
            .add("省份人数", [list(z) for z in zip(province, values)], "china")
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title="微信好友省份分布图"),
            visualmap_opts=opts.VisualMapOpts(max_=max(values)),
        )
    )
    c.render(friends_province_path % (get_self_info()["NickName"], 'html'))
    if save_pic:
        save_path = friends_province_path % (get_self_info()["NickName"], 'png')
        make_snapshot(snapshot, c.render(), save_path)
        itchat.send('这是你微信好友的省份分布图', toUserName='filehelper')
        itchat.send_image(save_path, toUserName='filehelper')


def get_word_cloud():
    friends = get_friends()
    t = []
    for i in friends:
        signature = i["Signature"].replace(" ", "").replace("span", "").replace("class", "") \
            .replace("emoji", "").replace("<", "").replace(">", "").replace("\"", "").replace("/", "")
        rep = re.compile("1f\d.+")
        signature = rep.sub("", signature)
        print(signature)
        t.append(signature)

    # 拼接字符串
    text = "".join(t)

    # jieba分词
    wordlist_jieba = jieba.cut(text, cut_all=True)
    wl_space_split = " ".join(wordlist_jieba)

    alice_coloring = np.array(Image.open(os.path.join(os.getcwd(), "pic/wx_bg.jpg")))
    my_wordcloud = WordCloud(
        background_color="white",
        max_words=3000,
        mask=alice_coloring,
        font_path='xx',
        max_font_size=60,
        random_state=42
    ).generate(wl_space_split)

    image_colors = ImageColorGenerator(alice_coloring)
    plt.imshow(my_wordcloud.recolor(color_func=image_colors))
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()

    # 保存图片 并发送到手机
    save_path = os.path.join(os.getcwd(), "pic/wechat_cloud.png")
    my_wordcloud.to_file(save_path)
    itchat.send_image(save_path, toUserName="filehelper")
