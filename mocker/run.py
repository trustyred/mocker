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

        with IPDB() as ipdb:
            veth0_name = 'veth0_'+name
            veth1_name = 'veth1_'+name
            netns_name = 'netns_'+name
            bridge_if_name = 'bridge0'

            existing_interfaces = ipdb.interfaces.keys()

            # Create a new virtual interface
            with ipdb.create(kind='veth', ifname=veth0_name, peer=veth1_name) as i1:
                i1.up()
                if bridge_if_name not in existing_interfaces:
                    ipdb.create(kind='bridge', ifname=bridge_if_name).commit()
                i1.set_target('master', bridge_if_name)

            # Create a network namespace
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
                user = os.getlogin()
                create_user_cgroups(user)

                # First we create the cgroup and we set it's cpu and memory limits
                cg = Cgroup(name)
                cg.set_cpu_limit(50)  # TODO : get these as command line options
                cg.set_memory_limit(500)

                # Then we a create a function to add a process in the cgroup
                def in_cgroup():
                    try:
                        pid = os.getpid()
                        cg = Cgroup(name)
                        for env in env_vars:
                            log.info('Setting ENV %s' % env)
                            os.putenv(*env.split('=', 1))

                        # Set network namespace
                        netns.setns(netns_name)

                        # add process to cgroup
                        cg.add(pid)

                        os.chroot(layer_dir)
                        if working_dir != '':
                            log.info("Setting working directory to %s" % working_dir)
                            os.chdir(working_dir)
                    except Exception as e:
                        traceback.print_exc()
                        log.error("Failed to preexecute function")
                        log.error(e)
                cmd = start_cmd
                log.info('Running "%s"' % cmd)
                process = subprocess.Popen(cmd, preexec_fn=in_cgroup, shell=True)
                process.wait()
                print(process.stdout)
                log.error(process.stderr)
            except Exception as e:
                traceback.print_exc()
                log.error(e)
            finally:
                log.info('Finalizing')
                NetNS(netns_name).close()
                netns.remove(netns_name)
                ipdb.interfaces[veth0_name].remove()
                log.info('done')
