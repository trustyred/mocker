#!/usr/bin/python
from docopt import docopt
import mocker
from mocker.base import BaseDockerCommand
from mocker.pull import PullCommand
from mocker.images import ImagesCommand
from mocker.run import RunCommand
import sys

def init_mocker_lib(path):
    #因为直接在机器上执行python setup.py无法进行mocker的安装，现在通过手动方式将mocker依赖的库路径导入python的库加载路径中
    #path根据你机器上的`mocker`路径去传入即可
    sys.path.append(path)

if __name__ == '__main__':
    init_mocker_lib("path_to_mocker_Lib")
    # 通过docopt库将mocker库中的__doc__变量解析成命令行参数
    arguments = docopt(mocker.__doc__, version=mocker.__version__)
    command = BaseDockerCommand
    if arguments['pull']:
        command = PullCommand
    elif arguments['images']:
        command = ImagesCommand
    elif arguments['run']:
        command = RunCommand

    cls = command(**arguments)
    cls.run(**arguments)
