# -*- coding: utf-8 -*-

from workflow import Workflow3, ICON_WEB, web

import sys,json
reload(sys)
sys.setdefaultencoding('utf8')

ICON_DEFAULT = 'icon.png'
ICON_ERROR = 'icon_error.png'

def set_baidutranslate_url(query):
    import os
    import random
    import urllib
    import hashlib

    appid = os.getenv('baidu_appid', '')
    secretKey = os.getenv('baidu_secretkey', '')

    if not appid or not secretKey:
        appid='20151113000005349'
        secretKey='osubCEzlGjzvw8qdQc41'

    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    fromLang = 'auto'
    toLang = 'auto'
    salt = random.randint(32768, 65536)

    sign = appid+query+str(salt)+secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    query = urllib.quote(str(query))
    url = url+'?appid='+appid+'&q='+query+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

    return url

def get_web_data(query):
    # 获取翻译数据
    url = set_baidutranslate_url(query)
    try:
        rt = web.get(url).json()
        return rt
    except:
        rt = {}
        rt['error_code'] = 500
        rt['error_msg'] = "Network Error"
        return rt

def check_English(query):
    # 检查英文翻译中午
    import re

    if re.search(ur"[\u4e00-\u9fa5]+", query):
        return False
    return True


def get_translation(query, isEnglish, rt):
    # 翻译结果
    subtitle = '翻译结果'
    translations = rt.get("trans_result")

    title = ''
    if translations is not None and len(translations) > 0:
        for i in translations:
            title = title + i.get('dst') + "\n"

    arg = [query, title, query, '', ''] if isEnglish else [
        query, title, title, '', '']
    arg = '$%'.join(arg)
    # print arg
    wf.add_item(
        title=title, subtitle=subtitle, arg=arg,
        valid=True, icon=ICON_DEFAULT)

def main(wf):
    query = wf.args[0].strip().replace("\\", "")
    if not isinstance(query, unicode):
        query = query.decode('utf8')

    rt = get_web_data(query)

    if rt.get("error_code") is not None:
        arg = ['', '', '', '', 'error']
        arg = '$%'.join(arg)
        wf.add_item(
            title=rt.get('error_msg'), subtitle='', arg=arg,
            valid=True, icon=ICON_ERROR)

    elif rt.get("error_code") is None:
        isEnglish = check_English(query)
        get_translation(query, isEnglish, rt)

    else:
        title = '百度也翻译不出来了'
        subtitle = '尝试一下去网站搜索'
        arg = [query, ' ', ' ', ' ']
        arg = '$%'.join(arg)
        wf.add_item(
            title=title, subtitle=subtitle, arg=arg,
            valid=True, icon=ICON_DEFAULT)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
