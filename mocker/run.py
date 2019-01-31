#coding=utf-8
import os
import uuid
import json
from pprint import pprint
import subprocess
import traceback
from pyroute2 import IPDB, NetNS, netns
from cgroups import Cgroup
from cgroups.user import create_user_cgroups

from mocker import _base_dir_, log
from .base import BaseDockerCommand
from .images import ImagesCommand

try:
    from pychroot import Chroot
except ImportError:
    print('warning: missing chroot options')


class RunCommand(BaseDockerCommand):
    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        # 获得所有镜像的列表
        images = ImagesCommand().list_images()
        # 获得镜像的名字
        image_name = kwargs['<name>']
        ip_last_octet = 103 # TODO : configurable

        #通过传入的镜像名字，从而获得镜像的json文件(里面存储有镜像的manifest)
        match = [i[3] for i in images if i[0] == image_name][0]
        #读取镜像的manifest文件
        target_file = os.path.join(_base_dir_, match)
        with open(target_file) as tf:
            image_details = json.loads(tf.read())

        # setup environment details
        # 从manifest文件中获得镜像的体系结构(arch)，配置(conifg),启动命令(Cmd)等信息
        # 默认获取history的第一层，也就是最新一层
        state = json.loads(image_details['history'][0]['v1Compatibility'])

        # Extract information about this container
        # 获得即将启动的容器内部的环境变量
        env_vars = state['config']['Env']
        # 获得启动容器时候运行的命令，并将其从列表转化为字符串
        # 比如['/hello','-a','-b'] -> "/hello -a -b"
        start_cmd = subprocess.list2cmdline(state['config']['Cmd'])
        # 获取容器的初始工作目录
        working_dir = state['config']['WorkingDir']
        # 获得一个唯一ID
        id = uuid.uuid1()

        # unique-ish name
        # 获取前uuid的第五部分的前4个字符
        name = 'c_' + str(id.fields[5])[:4]
        # 获取uuid的第五部分的前2个字符
        # unique-ish mac
        mac = str(id.fields[5])[:2]
        
        layer_dir = os.path.join(_base_dir_, match.replace('.json', ''), 'layers', 'contents')
        # IPDB比IPRoute对性能的消耗更少，因为它是异步的，并且会将系统返回的信息缓存起来，不会每次都加载所有信息
        with IPDB() as ipdb:
            veth0_name = 'veth0_'+name
            veth1_name = 'veth1_'+name
            netns_name = 'netns_'+name
            bridge_if_name = 'bridge0'

            # 列出系统存在的网络设备名字
            existing_interfaces = ipdb.interfaces.keys()

            # Create a new virtual interface
            # 创建一个双端的网络设备，一端与宿主机（也就是运行mocker的真实机器在一个网段），另一端与容器的网络在一个网段，这段先这样浅显的解释下
            # 可能不是很准确
            with ipdb.create(kind='veth', ifname=veth0_name, peer=veth1_name) as i1:
                # 将双端网络设备启动
                i1.up()
                # 查找网桥是否创建过，如果没有的话，创建一个名字为`bridge0`的网桥
                if bridge_if_name not in existing_interfaces:
                    ipdb.create(kind='bridge', ifname=bridge_if_name).commit()
                i1.set_target('master', bridge_if_name)

            # Create a network namespace
            # 创建一个新的名称空间
            netns.create(netns_name)

            # move the bridge interface into the new namespace
            with ipdb.interfaces[veth1_name] as veth1:
                veth1.net_ns_fd = netns_name

            # Use this network namespace as the database
            ns = IPDB(nl=NetNS(netns_name))
            with ns.interfaces.lo as lo:
                lo.up()
            with ns.interfaces[veth1_name] as veth1:
                veth1.address = "02:42:ac:11:00:{0}".format(mac)
                veth1.add_ip('10.0.0.{0}/24'.format(ip_last_octet))
                veth1.up()
            ns.routes.add({
                'dst': 'default',
                'gateway': '10.0.0.1'}).commit()

            try:
                # setup cgroup directory for this user
                # 获得当前的登陆用户
                user = os.getlogin()
                # 为登陆用户创建cgroup
                create_user_cgroups(user)

                # First we create the cgroup and we set it's cpu and memory limits
                # 根据容器的用户名去创建Cgroup
                cg = Cgroup(name)
                # 限制最多占用cpu使用率为50%
                cg.set_cpu_limit(50)  # TODO : get these as command line options
                # 限制内存最多使用500MB
                cg.set_memory_limit(500)

                # Then we a create a function to add a process in the cgroup
                def in_cgroup():
                    try:
                        # 获得当前的pid
                        pid = os.getpid()
                        # 创建当前用户的cgroup
                        cg = Cgroup(name)
                        # 将环境变量设置到容器环境里，bug，因为os.putenv并不会把环境变量加入当前环境
                        for env in env_vars:
                            log.info('Setting ENV %s' % env)
                            os.putenv(*env.split('=', 1))

                        # Set network namespace
                        # 设置当前环境的网络命名空间
                        netns.setns(netns_name)

                        # add process to cgroup
                        # 将当前的进程加载到cgroup里面
                        cg.add(pid)
                        log.info("Working directory : %s" %layer_dir)
                        # 将文件系统的根路径切换到layer目录
                        os.chroot(layer_dir)
                        if working_dir != '':
                            log.info("Setting working directory to %s" % working_dir)
                            os.chdir(working_dir)
                    except Exception as e:
                        traceback.print_exc()
                        log.error("Failed to preexecute function")
                        log.error(e)
                # 获得启动容器的时候将要运行的命令
                cmd = start_cmd
                
                env_dict = {}
                for env in env_vars:
                    key,value = env.split('=',1)
                    env_dict[key] = value
                log.info('container env: %s' str(env_dict)
                log.info('Running "%s"' % cmd)


                # 在执行cmd之前先执行in_cgroup函数，这是subprocess.Popen函数里preexec_fn参数的意思
                # 在这里找到了一个bug，应该把shell=True改成shell=False，因为在有些容器的环境内，可能并没有
                # /bin/sh，就会导致执行的时候出错，比如library/hello-world这个镜像就只有一个hello文件
                # 当shell=True的时候就一定会报错
                
                process = subprocess.Popen(cmd, preexec_fn=in_cgroup, shell=False,env=env_dict)
                process.wait()
                # 输出容器进程的标准输出
                print(process.stdout)
                log.error(process.stderr)
            except Exception as e:
                traceback.print_exc()
                log.error(e)
            finally:
                log.info('Finalizing')
                # 关闭网络命名空间
                NetNS(netns_name).close()
                netns.remove(netns_name)
                # 清除虚拟网络设备
                ipdb.interfaces[veth0_name].remove()
                log.info('done')
