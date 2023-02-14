import shutil
from socket import socket

# import cfscrape
import requests
import socks


def sock5():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 7890)
    socket.socket = socks.socksocket
    res = requests.get('https://www.baidu.com')
    print(res.text)


if __name__ == '__main__':
    # shutil.copytree('D:\githubProjects\movie-bot-dev\mbot', 'D:\githubProjects\mr_plugins\mbot', symlinks=True)
    # shutil.copytree('D:\githubProjects\movie-bot-api\moviebotapi', 'D:\githubProjects\mr_plugins\movie-bot-api', symlinks=True)
    sock5()
