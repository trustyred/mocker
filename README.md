# mocker
一直希望能了解docker的运行机制，但总是阅读概念，使用docker没有意思，不如写一个docker，并且采用自己比较熟悉的Python，本项目是基于tonybaloney/mocker项目，感谢他的无私贡献

## 想修改学习这个项目需要的基础知识
- Docker的基本操作与其原理，比如pull一个镜像都要经过哪些过程
- Python基础与拓展库pyroute2、docopt、cgroups等
## 目前存在的问题
下面的异常都是在我的测试机器上发现的
环境:CentOS Linux release 7.2.1511 (Core) 

- 通过python setup.py install无法正常安装mocker
- python mocker.py run hello-world无法正常工作

## 准备修改哪些
目前的初期计划就是，先对原先的mocker做一个全面详尽的注释，然后针对上一条“目前存在的问题”，将其全部解决