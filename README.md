# mocker0.0.1
修改的第一个版本，添加了中文代码注释，修改了我直接从tonybaloney:master clone
过来遇到的问题

# 修复的bug
- run某些镜像会报`[Errno 2] No such file or directory`的问题
- 将python包发布工具从distutils迁移到了setuptools，并且修复了之前运行`python setup.py install`失败的问题
