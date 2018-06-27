#coding:utf-8
from django import http
from django.shortcuts import render
from django.views.generic.base import View
from .get_host import host_list
from .Myansible import my_ansible,my_ansible_play
from .models import task,task_result,group,hosts,ys_uid,hosts_group
from django.http import HttpResponse
from .tasks import task_run,test_run,pb_run
import logging
import redis
# Create your views here.


def getad(IP):
    r=redis.Redis(host='localhost',port=6379,db=6)
    ad=r.get(IP)
    if ad is None:
        return 'Unknown'
    else:
        return ad


class Update_host(View):
    def get(self, request):
        r=host_list()
        return render(request,'test.html',{"info":r})

class task_test(View):
    def get(self,request):
        tasks = [ dict(action=dict(module='shell', args=dict(cmd='/usr/bin/uptime')))]
        group='00705-cz-ceph'
        ans=my_ansible(tasks,group)
        ans.run()
        #print ans.get_result()
        return render(request,'task_test.html',{"info":ans.get_result()})

class Mytask(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            logger = logging.getLogger("django")
            user=user=request.user
            my_tasks=task.objects.filter(create_user=request.user).order_by("-create_time")
            logger.info(str(my_tasks.__dict__))
            groups_list=[]
            for i in group.objects.filter():
                groups_list.append(i.name)
            groups_list.sort()
            return render(request,'task_list.html',{"tasks":my_tasks,"groups":groups_list})

    def post(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            mytask=task()
            mytask.create_user=user=request.user
            mytask.status='init'
            mytask.Type=request.POST['Type']
            mytask.group=group.objects.get(name=request.POST['group'])
            mytask.model=request.POST['model']
            mytask.args=request.POST['args']
            mytask.save()
            mytask_result=task_result()
            mytask_result.task_id=mytask
            mytask_result.result=''
            mytask_result.save()
 

            #celery
            logging.info('type:'+mytask.Type)
            if mytask.Type == 'ansible':
                r=task_run.delay(mytask.id)
                my_tasks=task.objects.filter(id=request.user.id)
            elif mytask.Type == 'playbook':
                r=pb_run.delay(mytask.id)
                my_tasks=task.objects.filter(id=request.user.id)
            return http.HttpResponseRedirect('http://192.168.240.13:18072/action/')

class Mytest(View):
    def get(self,request):
        test_run.delay()
        my_tasks=task.objects.filter(id=103)
        return HttpResponse(my_tasks)
class mytask_result(View):
    def get(self,request,active_code):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            result=task_result.objects.get(task_id_id=active_code)
            if len(result.result) <4:
                return HttpResponse('结果未出来，请稍后再看，如很久没有结果请检查服务')
            else:
                return render(request,'result.html',{"info":eval(result.result)})
class init2101(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            logger = logging.getLogger("django")
            user=user=request.user
            my_tasks=task.objects.filter(create_user=request.user)
            logger.info(str(my_tasks.__dict__))
            groups_list=[]
            g=group.objects.get(name="NNOP2101")
            for h in hosts_group.objects.filter(group_id=g):
                groups_list.append(h.host_id.ip)
            groups_list.sort()
            free_uid=len(ys_uid.objects.filter(status='free'))
            return render(request,'init_2101.html',{"tasks":my_tasks,"groups":groups_list,'free_uid':free_uid})

    def post(self,request):
        groups_list=[]   #2101 ip列表
        info={'add':[],'err':[]}
        g=group.objects.get(name="NNOP2101")
        for h in hosts_group.objects.filter(group_id=g):
            groups_list.append(h.host_id.ip)
        for ip in request.POST['ip'].split(','):
            if ip in groups_list:
                mytask=task()
                mytask.create_user=user=request.user
                mytask.status='init'
                mytask.Type='ansible'
                mytask.model='shell'
                mytask.host=hosts.objects.get(ip=ip)
                info['add'].append(ip)
                uid=ys_uid.objects.filter(status='free')[0]
                uid.host=mytask.host
                uid.status='using'
                uid.save()
        
                qy=getad('.'.join(ip.split('.')[0:3]))
                qyxl='bf-ct'
                bf=['shandong','henan','shanxi','shaanxi','gansu','qinghai','xinjiang','hebei','tianjin','beijing','neimenggu','liaoning','jilin','heilongjiang','ningxia']
                if len(qy.split('-'))==2:
                    if qy.split('-')[1]=='yidong':
                        qyxl='qg-cmc'
                    else:
                        if qy.split('-')[0] in bf:
                            qyxl='bf-'
                        else:
                            qyxl='nf-'
                        if qy.split('-')[1]=='dianxin':
                            qyxl=qyxl+'ct'
                        else:
                            qyxl=qyxl+'cnc'
            
                mytask.args='rm -f init_2101.py;wget http://123.125.212.207/zbx/init_2101.py -q ; python init_2101.py --uid '+uid.uid + ' --region  '+qyxl
                mytask.save()
                mytask_result=task_result()
                mytask_result.task_id=mytask
                mytask_result.result=''
                mytask_result.save()

        #celery
                logging.info('type:'+mytask.Type)
                if mytask.Type == 'ansible':
                    r=task_run.delay(mytask.id)
                    my_tasks=task.objects.filter(id=request.user.id)
                elif mytask.Type == 'playbook':
                    r=pb_run.delay(mytask.id)
                    my_tasks=task.objects.filter(id=request.user.id)
            else:
                info['err'].append(ip)
        if len(info['err'])==0:
            return http.HttpResponseRedirect('http://192.168.240.13:18072/action/')
        else:
            s='任务添加成功：'
            for ic in info['add']:
                s=s+ic+' '
            s=s+'</br>任务添加失败：'
            for ie in info['err']:
                s=s+ie+' '
            
            return HttpResponse(s)
