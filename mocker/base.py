#coding=utf-8
class BaseDockerCommand(object):
    def run(*args):
        raise NotImplementedError()