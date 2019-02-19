## 想修改学习这个项目需要的基础知识
- Docker的基本操作与其原理，比如pull一个镜像都要经过哪些过程
- Python基础与拓展库pyroute2、docopt、cgroups等
## 目前存在的问题
下面的异常都是在我的测试机器上发现的，目前的0.0.1版本已经全部解决了下面的问题
- 环境:CentOS Linux release 7.2.1511 (Core) 

- 通过python setup.py install无法正常安装mocker(已解决)
- python mocker.py run library/hello-world无法正常工作(已解决)

## 准备修改哪些
0.0.1版本已经完成，完成工作有代码的中文注释，基本运行问题的修复
0.0.2版本准备继续完善整个mocker的功能
- mocker ps功能
- mocker 端口映射功能
- mocker run的交互式运行与后台运行模式，并增加执行命令功能
