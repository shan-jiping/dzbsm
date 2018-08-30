#!/usr/local/bin/python
# -*- coding:utf8 -*-
from __future__ import absolute_import

import os
import json
from collections import namedtuple
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleParserError
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager



class playbookcallback(CallbackBase):
    #这里是状态回调，各种成功失败的状态,里面的各种方法其实都是从写于CallbackBase父类里面的，其实还有很多，可以根据需要拿出来用
    def __init__(self,*args):
        super(playbookcallback,self).__init__(display=None)
        self.status_ok=json.dumps({})
        self.status_fail=json.dumps({})
        self.status_unreachable=json.dumps({})
        self.status_playbook=''
        self.status_no_hosts=False
        self.host_ok = {}
        self.host_failed={}
        self.host_unreachable={}
    def v2_runner_on_ok(self,result):
        host=result._host.get_name()
        self.runner_on_ok(host, result._result)
        #self.status_ok=json.dumps({host:result._result},indent=4)
        self.host_ok[host] = result
    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)
        #self.status_fail=json.dumps({host:result._result},indent=4)
        self.host_failed[host] = result
    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self.runner_on_unreachable(host, result._result)
        #self.status_unreachable=json.dumps({host:result._result},indent=4)
        self.host_unreachable[host] = result
    def v2_playbook_on_no_hosts_matched(self):
        self.playbook_on_no_hosts_matched()
        self.status_no_hosts=True
    def v2_playbook_on_play_start(self, play):
        self.playbook_on_play_start(play.name)
        self.playbook_path=play.name

class ansiblecallback(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ansiblecallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        self.host_ok[result._host.get_name()] = result
        #host = result._host
        #print json.dumps({host.name:result._result},indent=4)

    def v2_runner_on_failed(self, result,  *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


class my_ansible_play():
    #这里是ansible运行 
    #初始化各项参数，大部分都定义好，只有几个参数是必须要传入的
    def __init__(self, playbook, extra_vars={}, 
                        host_list=None, 
                        connection='ssh',
                        become=False,
                        become_user=None,
                        module_path=None,
                        fork=50,
                        ansible_cfg=None,   #os.environ["ANSIBLE_CONFIG"] = None
                        passwords={},
                        check=False):
        self.passwords=passwords
        self.extra_vars=extra_vars
        Options = namedtuple('Options',
                   ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path',
                   'forks', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                      'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
        self.options = Options(listtags=False, listtasks=False, 
                              listhosts=False, syntax=False, 
                              connection=connection, module_path=module_path, 
                              forks=fork, private_key_file=None, 
                              ssh_common_args=None, ssh_extra_args=None, 
                              sftp_extra_args=None, scp_extra_args=None, 
                              become=become, become_method=None, 
                              become_user=become_user, 
                              verbosity=None, check=check)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.playbook_path=os.path.join(BASE_DIR, "action/role/"+playbook)
        host_list= os.path.join(BASE_DIR, "action/hosts")
        self.host_list=host_list
        ansible_cfg = os.path.join(BASE_DIR, "action/ansible.cfg")
        if ansible_cfg != None:
            os.environ["ANSIBLE_CONFIG"] = ansible_cfg
        self.variable_manager=VariableManager()
        self.variable_manager.extra_vars=self.extra_vars
        self.loader=DataLoader()
        self.inventory=Inventory(loader=self.loader,variable_manager=self.variable_manager,host_list=host_list)
    #定义运行的方法和返回值
    def run(self):
        complex_msg={}
        if not os.path.exists(self.playbook_path):
            code=1000
            results={'playbook':self.playbook_path,'msg':self.playbook_path+' playbook is not exist','flag':False}
            #results=self.playbook_path+'playbook is not existed'
            #return code,complex_msg,results
        pbex= PlaybookExecutor(playbooks=[self.playbook_path],
                       inventory=self.inventory,
                       variable_manager=self.variable_manager,
                       loader=self.loader,
                       options=self.options,
                       passwords=self.passwords)
        self.results_callback=playbookcallback()
        pbex._tqm._stdout_callback=self.results_callback
        try:
            code=pbex.run()
        except AnsibleParserError:
            code=1001
            results={'playbook':self.playbook_path,'msg':self.playbook_path+' playbook have syntax error','flag':False}
            #results='syntax error in '+self.playbook_path #语法错误
            return code,results
        if self.results_callback.status_no_hosts:
            code=1002
            results={'playbook':self.playbook_path,'msg':self.results_callback.status_no_hosts,'flag':False,'executed':False}
            #results='no host match in '+self.playbook_path
            return code,results
    def get_result(self):
        self.result_all={'success':{},'fail':{},'unreachable':{}}
        #print result_all
        #print dir(self.results_callback)
        for host, result in self.results_callback.host_ok.items():
            self.result_all['success'][host] = result._result

        for host, result in self.results_callback.host_failed.items():
            self.result_all['fail'][host] = result._result['msg']

        for host, result in self.results_callback.host_unreachable.items():
            self.result_all['unreachable'][host]= result._result['msg']
        
        #for i in self.result_all['success'].keys():
        #    print i,self.result_all['success'][i]
        #print self.result_all['fail']
        #print self.result_all['unreachable']
        return self.result_all
        
class my_ansible():
    def __init__(self, tasks, groups,
                        host_list=None,
                        connection='ssh',
                        become=False,
                        become_user=None,
                        module_path=None,
                        fork=50,
                        ansible_cfg=None,
                        passwords={},
                        check=False):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        host_list= os.path.join(BASE_DIR, "action/hosts")
        ansible_cfg = os.path.join(BASE_DIR, "action/ansible.cfg")
        if ansible_cfg != None:
            os.environ["ANSIBLE_CONFIG"] = ansible_cfg
        #host_list = '/data/shanjiping/ans_d/ansible/hosts'
        #ansible_cfg='/data/shanjiping/ans_d/ansible/ansible.cfg'
        self.tasks=tasks
        self.passwords=passwords
        self.groups=groups
        self.host_list=host_list
        Options = namedtuple('Options', ['connection','module_path', 'forks', 'remote_user',
            'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
            'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
		
        self.options = Options(connection='smart', 
            module_path=None, 
            forks=100,
            remote_user='root', 
            private_key_file=None, 
            ssh_common_args=None, 
            ssh_extra_args=None,
            sftp_extra_args=None, 
            scp_extra_args=None, 
            become=None, 
            become_method=None,
            become_user=None, 
            verbosity=None, 
            check=False
            )
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.host_list)
        #print self.inventory.list_hosts(groups)
        self.variable_manager.set_inventory(self.inventory)
        play_source =  dict(
                name = "Ansible Play",
                hosts = self.groups,
                gather_facts = 'no',
                tasks = self.tasks
        )
        self.play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        #print 'host_list:',host_list
        #print 'ansible_cfg:',ansible_cfg
        #print 'tasks:',tasks
        #print 'groups:',groups
        
    def run(self):
        try:
            tqm = None
            self.callback = ansiblecallback()
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback = self.callback
		)
            result = tqm.run(self.play)
        finally:
            if tqm is not None:
                tqm.cleanup()
    def get_result(self):
        self.result_all={'success':{},'fail':{},'unreachable':{}}
        for host, result in self.callback.host_ok.items():
            self.result_all['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            self.result_all['fail'][host] = result._result['msg']

        for host, result in self.callback.host_unreachable.items():
            self.result_all['unreachable'][host]= result._result['msg']

        #for i in self.result_all['success'].keys():
        #    print i,self.result_all['success'][i]
        #print self.result_all['fail']
        #print self.result_all['unreachable']
        #print self.result_all
        return self.result_all

if __name__ =='__main__':
    play_book=my_ansible_play('test.yml',extra_vars={'hosts':'2101-sjp-test'})
    play_book.run()
    play_book.get_result()



    #tasks = [ dict(action=dict(module='shell', args=dict(cmd='/usr/bin/uptime')))]
    #group='2101-sjp-test'
    #ans=my_ansible(tasks,group)
    #ans.run()
    #print ans.get_result()
    #print os.environ
