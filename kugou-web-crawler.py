# kugou-web-crawler
# 1:05PM, Feb 7th, 2018 @ CE, 9/-3, very cold
# 爬取酷狗 top 500 排行榜的音乐信息
# 爬取的信息：歌手、歌曲名称、歌曲时长
# http://www.kugou.com/yy/rank/home/1-8888.html?from=rank
# http://www.kugou.com/yy/rank/home/2-8888.html?from=rank
# ...
# http://www.kugou.com/yy/rank/home/23-8888.html?from=rank
# 共23个页面，498条信息，酷狗TOP500 2018-2-1 更新

from bs4 import BeautifulSoup
import requests
import time
import re
import json

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

def get_info(url):
    global count, file
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    # 歌手、歌曲名称、歌曲链接在同一段 html 代码中
    # 歌曲时长在另一段 html 代码中
    infomations = soup.select('#rankWrap > div.pc_temp_songlist > ul > li > a')
    songTimes = soup.select('#rankWrap > div.pc_temp_songlist > ul > li > span.pc_temp_tips_r > span')
    for infomation, songTime in zip(infomations, songTimes):
        href = infomation.get('href')
        singer = infomation.get('title')
        songTime = songTime.getText().strip()
        count += 1
        print('歌曲{count}：\n'.format(count=count)+'链接：' + href + '\n' + '歌曲：' + singer + '\n' + '时长：' + songTime + '\n')
        file.write('歌曲{count}：\n'.format(count=count) + '链接：' + href + '\n' + '歌曲：' + singer + '\n' + '时长：' + songTime + '\n')
        get_hash(href)

def get_hash(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    hash_pattern = re.compile(r"\"hash\"\:\"(.*?)\"", re.MULTILINE | re.DOTALL)
    script = soup.find("script")
    hash = hash_pattern.search(script.text).group(1)
    get_music(hash)

def get_music(hash):
    global count, file
    res = requests.get('http://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery19106946809784755619_1540004931600&hash=' + hash + '&album_id=0')
    music = json.loads(res.text.replace('jQuery19106946809784755619_1540004931600(','').replace(');',''))
    print('hash：' + hash + '\n' + '下载地址：' + music['data']['play_url'] + '\n' + '封面：' + music['data']['img'] + '\n')
    file.write('hash：' + hash + '\n' + '下载地址：' + music['data']['play_url'] + '\n' + '封面：' + music['data']['img'] + '\n' + '\n')
    if music['data']['play_url']:
        r = requests.get(music['data']['play_url']) 
        with open(r"music/" + music['data']['audio_name'] + ".mp3", "wb") as code:
            code.write(r.content)    

def main():
    global count, file
    count = 0
    # UnicodeEncodeError 坑了半小时，最后使用 open() 函数时加上 encoding='utf-8' 这个参数解决了问题
    file = open(r'results-kugou-top500.txt', 'w', encoding='utf-8')
    # 原先的写法：
    # file = open(r'E:\AllPrj\PyCharmPrj\py-crawler\results-kugou-top500.txt', 'w')
    # 运行报错如下：
    # UnicodeEncodeError: 'gbk' codec can't encode character '\ubc45' in position 26: illegal multibyte sequence
    # 遇到网页上 title 名为 'BIGBANG - BANG BANG BANG (뱅뱅뱅) (Korean Ver.)' 中的 '뱅뱅뱅' 出现 UnicodeEncodeError
    # 我们来分析一下
    # open 函数的原型是：
    # open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
    # help(open) 返回的注释:
    # In text mode, if encoding is not specified the encoding used is platform dependent:
    # locale.getpreferredencoding(False) is called to get the current locale encoding.
    # 从官方描述中发现，open() 函数默认的 encoding 参数取决于平台环境，我这边默认是 'gbk'
    # 但是 'gbk' 不支持 '뱅뱅뱅' 这种字符，加上 encoding='utf-8' 这个参数就解决了
    urls = ['http://www.kugou.com/yy/rank/home/{page}-8888.html?from=rank'.format(page=page) for page in range(1, 24)]
    print('酷狗TOP500 2018-2-1 更新')
    file.write('酷狗TOP500 2018-2-1 更新\n\n')
    for url in urls:
        print('on page:'+url+'\n')
        file.write('on page:'+url+'\n')
        get_info(url)
        time.sleep(20)

if __name__ == '__main__':
    main()
