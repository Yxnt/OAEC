#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# date: 2016/12/10

from os import mkdir, path, chdir, getcwd
from re import search,sub

import requests
from bs4 import BeautifulSoup

domain = 'http://cloud.oracleoaec.com'
login_url = "{domain}{uri}".format(domain=domain, uri='/user/login')

# 替换账号密码为你自己的
# username = '123123123123'
# password = '12312312323'
username = ''
password = ''

login_par = {
    'name': username,
    'pass': password,
    'form_build_id': 'form-lvU5iMJ-2wpUEqR2V9X4NzTEgNhvgB34iUCS9MVKV0g',
    'form_id': 'user_login',
    'op': '登陆'
}

session = requests.session()
response = session.post(login_url, data=login_par)
course_total_url = '{domain}{uri}'.format(domain=domain, uri='/user/mycourse')


def getdownloadurl(url):
    '''
    获取视频下载链接并追加用户名和密码
    '''
    video = BeautifulSoup(session.get(url).text,'html.parser')
    videourl = video.find('source')
    if videourl:
        videourl = search(r'http://.*flv',str(videourl)).group()
        downloadurl = sub('http://','http://{username}:{password}@'.format(
            username=username,
            password=password
        ),videourl)
        content = requests.get(downloadurl).content

        return content

def getcourseurl(func):
    def geturl():
        if path.exists('视频下载') is not True:
            mkdir('视频下载')
        chdir('视频下载')
        for k, v in func().items():
            if path.exists(k) is not True:
                mkdir(k)
            player = BeautifulSoup(session.get(v).text, 'html.parser')
            for i in player.find_all('div', attrs={'class': 'item-title'}):
                '''创建目录结构'''
                st = i.find(attrs={'class': 'st'}).get_text()
                name = i.find(attrs={'class': 'name'}).get_text()

                directoryname = "{st}{name}".format(st=st, name=name) # 获取章节目录名称
                dirpath = ('{basedir}/{parent}/{course}'.format( # 拼接课程名曾
                    basedir=path.dirname(__file__),
                    parent='视频下载',
                    course=k,
                ))

                if search(r'章', st):
                    '''获取第几章名称并且创建该目录'''
                    chdir(dirpath)
                    try:
                        mkdir(directoryname)
                    except:
                        pass
                    chdir(directoryname)
                    dirname = dirpath+'/'+directoryname # 拼接目录名称
                elif search(r'节', st):
                    '''获取上一章下面的所有课程目录并创建该目录'''
                    try:
                        mkdir(directoryname)
                    except:
                        pass
                    tagname = dirname + '/' + directoryname # 拼接课程目录名称
                else:
                    chdir(tagname) # 进入课程目录下载当前课程
                    print(tagname)
                    if i.find('a'):
                        videourl = domain + i.find('a').get('href')
                        filename = i.find('a').get_text()+'.flv'
                        if path.exists(filename):
                            pass
                        else:
                            with open(filename.replace('/',''), 'wb') as f:
                                if getdownloadurl(videourl) is not None:
                                    f.write(getdownloadurl(videourl))
                    chdir('..') # 下载完成后切换至上层目录
            # 切换到视频下载目录
            chdir(path.dirname(__file__) + '/视频下载')

    return geturl

@getcourseurl
def getcourseurllist():
    '''获取当前账号所拥有的课程'''
    soup = BeautifulSoup(session.get(course_total_url).text, 'html.parser')
    resultlist = dict()
    for i in soup.find_all('a'):
        if i.get_text():
            result = search(r'course/.*', i.get('href'))
            if result:
                title = i.get_text()
                url = "{domain}/{uri}".format(domain=domain, uri=result.group())
                resultlist[title] = url
    return resultlist

if __name__ == '__main__':

    getcourseurllist()
