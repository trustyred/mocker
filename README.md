## 想修改学习这个项目需要的基础知识
- Docker的基本操作与其原理，比如pull一个镜像都要经过哪些过程
- Python基础与拓展库pyroute2、docopt、cgroups等
## 使用手册(与Docker基本类似)
### 镜像拉取
```
[root@VM_145_23_centos ~]# mocker pull busybox
warning: missing chroot options
Starting new HTTPS connection (1): auth.docker.io
Fetching manifest for busybox:latest...
Starting new HTTPS connection (1): registry-1.docker.io
...
```
### 镜像列表显示
```
[root@VM_145_23_centos ~]# mocker images
warning: missing chroot options
+-----------------+---------+----------+----------------------+
| name            | version | size     | file                 |
+-----------------+---------+----------+----------------------+
| library/nginx   | latest  | 42.7MiB  | library_nginx.json   |
| library/busybox | latest  | 738.2KiB | library_busybox.json |
+-----------------+---------+----------+----------------------+
```
### 启动容器
- 执行镜像默认命令
```
[root@VM_145_23_centos ~]# mocker run busybox
warning: missing chroot options
library/busybox
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
container env: {u'PATH': u'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'}
Running "[u'sh']"
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
Layer directory : /root/mocker/library_busybox/layers/contents
/ # 
```
- 根据命令行指定执行的命令
```
[root@VM_145_23_centos ~]# mocker run busybox ifconfig
warning: missing chroot options
library/busybox
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
container env: {u'PATH': u'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'}
Running "['ifconfig']"
Creating cgroups sub-directories for user root
cgroups sub-directories created for user root
Layer directory : /root/mocker/library_busybox/layers/contents
ifconfig: /proc/net/dev: No such file or directory
lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          UP LOOPBACK RUNNING  MTU:65536  Metric:1

veth1_c_9052 Link encap:Ethernet  HWaddr 02:42:AC:11:00:90  
          inet addr:10.0.0.103  Bcast:0.0.0.0  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1

None
None
Finalizing
done
shutdown in progress
```
## 正在开发的0.0.2版本功能
重新规划0.0.2的版本开发工作，因为像`docker ps`这种功能是需要一个统一的管理端将容器的进程管理起来才能实现，目前没准备做那么复杂，所以去掉
0.0.2版本准备继续完善整个mocker的功能
- mocker 端口映射功能
- 通过命令行参数定义容器将执行的命令
- 增加对overlay2文件系统的支持，将镜像文件存储到overlay2中