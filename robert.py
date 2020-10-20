import json
import os
import sys
import time

import itchat
import requests
from itchat.content import *

sys.path.append("..")

file_helper = 'filehelper'

beauty_mode = False


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    # 记录消息
    record(msg, True)

    # 下载聊天记录
    if msg.user['UserName'] == file_helper and '聊天记录' in msg.text:
        dl_record(msg.text.split('-')[1])

    get_response(msg)


def record(msg, r=False):
    if r:
        folder = 'record/{}/'.format(file_helper if msg.user['UserName'] == file_helper else msg.user['RemarkName'])
        if not os.path.exists(folder):
            os.mkdir(folder)
        record_file = folder + time.strftime("%Y%m", time.localtime()) + '.txt'
        with open(record_file, 'a', encoding='utf-8') as f:
            if msg.toUserName == msg.user.userName:
                f.write(time.strftime("%d %H:%M:%S", time.localtime()) + " your name：" + msg.text + '\n')
            else:
                f.write(
                    time.strftime("%d %H:%M:%S", time.localtime()) + " " + msg.user['NickName'] + "：" + msg.text + '\n')


def dl_record(remark_name):
    file_name = time.strftime("%Y%m", time.localtime()) + '.txt'
    file_path = os.path.join(os.getcwd(), 'record/{}/{}'.format(remark_name, file_name))
    itchat.send_file(file_path, toUserName=file_helper)


def get_response(msg):
    url = 'http://openapi.tuling123.com/openapi/api/v2'
    # apiKey need obtained
    payloads = {
        'reqType': 0,
        'perception': {
            'inputText': {
                'text': msg.text
            },
            'selfInfo': {
                'location': {
                    'city': '北京'
                }
            }
        },
        'userInfo': {
            'apiKey': 'xx',
            'userId': 'qx'
        }
    }

    r = requests.post(url, data=json.dumps(payloads)).json()
    if r['intent']['code'] in (4000, 5000, 6000):
        return
    result = r['results'][0]['values']['text']
    msg.user.send(result)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    folder = 'record/{}/'.format(file_helper if msg.user['UserName'] == file_helper else msg.user['RemarkName'])
    if not os.path.exists(folder):
        os.mkdir(folder)
    msg.download(folder + msg.fileName)


itchat.auto_login(True, enableCmdQR=2)
itchat.run(True)
