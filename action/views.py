#coding:utf-8
from django import http
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .get_host import host_list
from .Myansible import my_ansible,my_ansible_play
from .models import task,task_result,group,hosts,ys_uid,hosts_group,short_task_template,short_task
from .tasks import task_run,pb_run,short_task_run
from action.ShortTask import CloseTask
import logging
import redis
import os
import urllib2
import urllib
import json
import time
import hashlib
import random
import datetime
import httplib
import re
from email.utils import formatdate
from users.models import UserProfile
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
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            r=host_list()
            return render(request,'test.html',{"info":r})



def get_tgt_online():
    url = 'https://apis.dnion.com:8243/cas/v1/tickets'
    data = {
        'username': 'shanjiping@dnion.com',
        'password': 'dnion1234' }
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.headers['Location'].split('/')[-1]
def update_tgt(cachefile):
    TGT = get_tgt_online()
    with open(cachefile, 'wb') as f:
        f.write(TGT)
    return TGT
def get_tgt(cachefile):
    if not os.path.exists(cachefile):
        TGT = update_tgt(cachefile)
    else:
        t0 = os.path.getctime(cachefile)
        t1 = time.time()
        if t1 - t0 > 25200:
            TGT = update_tgt(cachefile)
        else:
            f = open(cachefile, 'r')
            TGT = f.read()
            f.close()
    return TGT

def get_platform_list(platform):
    url='https://apis.dnion.com:8243/machine/platform/allmachines?plNameEn='+platform
    TGT = get_tgt('TGT')
    req=urllib2.Request(url)
    req.add_header('Authorization',TGT)
    req.add_header('username','shanjiping@dnion.com')
    res=json.loads(urllib2.urlopen(req).read())
    return res


def tomd5(str):
    m=hashlib.md5()
    m.update(str)
    return m.hexdigest()

def fdl(kuwo_stream):
    kuwo_key='kuwo2013rtmp'
    now=int(time.time())
    opstr='publish'
    uid='44754776'
    roomid='1000'
    k=tomd5(opstr+str(now)+uid+roomid+kuwo_key)
    url='rtmp://rtmp.kuwoact.fastcdn.com/kuwoact/'+kuwo_stream+'?opstr='+opstr+'&tm='+str(now)+'&uid='+uid+'&roomid='+roomid+'&Md5='+k
    return url

class get_kuwoact(View):
    def get(self,request):
        kuwo_stream=request.GET.get('stream')
        if kuwo_stream == None:
            return HttpResponse('请输入流名    like:  /action/kuwo?stream=xxx')
        else:
            url=fdl(kuwo_stream)
            return HttpResponse(url)

class create_act(View):
    def post(self,request):
        if request.POST['type']=='':
            return HttpResponse('参数错误')
        else:
            task=True
            body={}
            url=''
            post_port=80
            method="POST"
            kuwo_lb_domain='yilanpushserver.dnionzb.com'
            if request.POST['type']=='reboadcast' and request.POST['reboadcast_file']!='' and request.POST['stream']!='':
                url='/yilan/v1/reboardcast'
                body={
                    "domain":"huanan",
                    "flv_file":"/mesos/ceph/NNOP00705/A3CGUIHJUE5K3HQYH158_live-dl-84561/live-dl-record/sjp/"+request.POST['reboadcast_file'].strip(),
                    "push":"rtmp://121.32.254.160:1835/pub.kuwoact.dnionzb.com/kuwoact/"+request.POST['stream'].strip()
               }

            elif request.POST['type']=='act' and request.POST['stream']!='' and request.POST['pull']!='':
                url='/yilan/v1/live'
                body={
                    "domain":"huanan",
                    "pull":request.POST['pull'].strip(),
                    "push":"rtmp://121.32.254.160:1835/pub.kuwoact.dnionzb.com/kuwoact/"+request.POST['stream'].strip()
               }
            else:
                task=False

            if task:
                    http_client = httplib.HTTPConnection(kuwo_lb_domain, post_port, timeout=30)
                    try:
                        body_str = json.JSONEncoder().encode(body)
                        http_header = dict()
                        http_header['Content-Type'] = "application/json"
                        http_header['Content-Length'] = len(body_str)
                        http_header['Date'] = formatdate(timeval=None, localtime=False, usegmt=True)
                        http_client.request(method, url, body=body_str, headers=http_header)
                        response = http_client.getresponse()
                        content = json.loads(response.read())
                    except Exception, e:
                        content={}
                        content['code']=1
                        content['msg']=str(e)
                    http_client.close()
                    print body_str
                    print content
                    if content['code']==0:
                        return http.HttpResponseRedirect('/action/kuwo_act/')
                    else:
                        return HttpResponse(content['msg'])

            else:
                return HttpResponse('参数错误')

class del_kuwo_act(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            stream=request.GET.get('stream')
            t=request.GET.get('type')
            if stream == None or t == None:
                return HttpResponse('没有流名和类型  请确认')
            else:
                stream=request.GET.get('stream')
                t=request.GET.get('type')
                if stream == None or t == None:
                    return HttpResponse('没有流名和类型  请确认')
                else:
                    kuwo_lb_domain='yilanpushserver.dnionzb.com'
                    post_port=80
                    method="POST"
                    url='/yilan/v1/delete'
                    push_dir='rtmp://121.32.254.160:1835/pub.kuwoact.dnionzb.com/kuwoact/'+stream
                    body={
                       "domain":"huanan",
                       "push":push_dir,
                       "stream":t
                    }
                    http_client = httplib.HTTPConnection(kuwo_lb_domain, post_port, timeout=30)
                    try:
                        body_str = json.JSONEncoder().encode(body)
                        http_header = dict()
                        http_header['Content-Type'] = "application/json"
                        http_header['Content-Length'] = len(body_str)
                        http_header['Date'] = formatdate(timeval=None, localtime=False, usegmt=True)
                        http_client.request(method, url, body=body_str, headers=http_header)
                        response = http_client.getresponse()
                        content = json.loads(response.read())
                    except Exception, e:
                        content={}
                        content['code']=1
                        content['msg']=str(e)
                    http_client.close()
                    print body_str
                    print content
                    if content['code']==0:
                        return http.HttpResponseRedirect('/action/kuwo_act/')
                    else:
                        return HttpResponse(content['msg'])

class kuwo_act(View):
    def get(self,request):
        kuwo_lb_domain='yilanpushserver.dnionzb.com'
        post_port=80
        method="POST"
        url='/yilan/v1/query'
        body={
           "domain":"huanan",
        }
        result={}
        http_client = httplib.HTTPConnection(kuwo_lb_domain, post_port, timeout=30)
        try:
            body_str = json.JSONEncoder().encode(body)
            http_header = dict()
            http_header['Content-Type'] = "application/json"
            http_header['Content-Length'] = len(body_str)
            http_header['Date'] = formatdate(timeval=None, localtime=False, usegmt=True)
            http_client.request(method, url, body=body_str, headers=http_header)
            response = http_client.getresponse()
            result = json.loads(response.read())
        except Exception, e:
            print 'ERROR: ' + str(e)
        http_client.close()

        if result['code']==0:
            info={}
            kuwo_key='kuwo2013rtmp'
            opstr='listen'
            uid='44754776'
            roomid='1000'
            now=int(time.time())
            for i in result['tasks']['reboard_tasks']:
                stream=i['push'].split('kuwoact/')[1]
                info[stream]={
                                  'reboard_task':{
                                                     'push':i['push'],
                                                     'flv_file':i['flv_file'],
                                                     'begintime':i['begintime']
                                                 },
                                  'rtmp_fdl':'?opstr='+opstr+'&tm='+str(now)+'&uid='+uid+'&roomid='+roomid+'&Md5='+tomd5(opstr+str(now)+uid+roomid+kuwo_key),
                                  'live_task':{
                                              'push':'',
                                              'pull':'',
                                              'begintime':''
                                             }
                             }
            for j in result['tasks']['live_tasks']:
                stream=j['push'].split('kuwoact/')[1]
                if stream in info:
                    info[stream]['live_task']={    
                                              'push':j['push'],
                                              'pull':j['pull'],
                                              'begintime':i['begintime']
                                          }
                else:
                    info[stream]={
                                  'reboard_task':{
                                                     'push':'',
                                                     'flv_file':'',
                                                     'begintime':''
                                                 },
                                  'rtmp_fdl':'?opstr='+opstr+'&tm='+str(now)+'&uid='+uid+'&roomid='+roomid+'&Md5='+tomd5(opstr+str(now)+uid+roomid+kuwo_key),
                                  'live_task':{          
                                              'push':j['push'],
                                              'pull':j['pull'],
                                              'begintime':j['begintime']
                                             }
                             } 
            #return HttpResponse(str(info))
            return render(request,'kuwo_act.html',{"info":info})
        else:
            return HttpResponse(result['msg'])


class list_platform(View):
    def get(self,request):
        xianlu={
                                'dx':u'电信',
                                'lt':u'联通',
                                'yd':u'移动',
                                'ck':u'长宽',
                                'jy':u'教育',
                                'hs':u'华数',
                                #'bgp':u'BGP'
                                'tt':u'铁通'
                                }
        try:
            #args=self.request.arguments
            #if 'p' in args:
            #    isp=''
            #    if 'isp' in args:
            #        isp=self.get_argument('isp')
            isp=request.GET.get('isp')
            platform=request.GET.get('p')
            if isp == None or platform == None :
                return HttpResponse('Missing parameter')
            #    platform=self.get_argument('p')
            result=get_platform_list(platform)
            if 'error' in result:
                return HttpResponse(' get_platform_list error:'+str(result['error']))
            else:
                s=''
                for i in result:
                    for j in i['platformMachineIpList']:
                        if j['mcipStatus']==u'2' or j['mcipStatus']==u'1' or j['mcipStatus']==u'5' :
                            if isp in xianlu :
                                if xianlu[isp] in j['ipIsp']:
                                    s=s+str(j['mcipIp'])+'   '+str(j['ipIsp'])+'   '+str(j['ndName'])+'\n'
                            #else:
                            #    s=s+j['mcipIp']+'   '+j['ipIsp']+'   '+j['ndName']+'\n'
            #else:
            #   self.write('Missing parameter')
            return HttpResponse(s)
        except Exception,e:
            return HttpResponse('捕获异常  '+str(e)+str(result))
            #self.write(str(e))
            



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
            user=request.user
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
            mytask.create_user=request.user
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
            return http.HttpResponseRedirect('/action/')

class Cronttask(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            logger = logging.getLogger("django")
            user=UserProfile.objects.get(username='crontab')
            my_tasks=task.objects.filter(create_user=user).order_by("-create_time")
            logger.info(str(my_tasks.__dict__))
            groups_list=[]
            for i in group.objects.filter():
                groups_list.append(i.name)
            groups_list.sort()
            return render(request,'crontab_list.html',{"tasks":my_tasks,"groups":groups_list})

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



class show_short_task(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            logger = logging.getLogger("django")
            info={}
            kuwo_key='kuwo2013rtmp'
            opstr='listen'
            uid='44754776'
            roomid='1000'
            now=int(time.time())
            rtmp_fdl='?opstr='+opstr+'&tm='+str(now)+'&uid='+uid+'&roomid='+roomid+'&Md5='+tomd5(opstr+str(now)+uid+roomid+kuwo_key)
            sts=short_task.objects.filter(status='running')
            flv_list=os.listdir('media/dianpian')
            running_zhuanma=short_task.objects.filter(template=4,status='running')
            zhuanma_list=[]
            for zm in running_zhuanma:
                fn=eval(zm.source)['flvname'].split('/')[-1]
                zhuanma_list.append(fn)
                if fn in flv_list:
                    del flv_list[flv_list.index(fn)]
            
            for st in sts:
                kt={
                        'reboard_task':{
                            'command':'',
                            'flv_file':'',
                            'begintime':'',
                            'task_id':'',
                            'log':''
                         },
                        'rtmp_fdl':rtmp_fdl,
                        'live_task':{
                            'command':'',
                            'pull':'',
                            'begintime':'',
                            'task_id':'',
                            'log':''
                        }
                    }
                if st.template.name == 'kuwo-tuiliu':
                    if eval(st.source)['stream'] not in info:
                        info[eval(st.source)['stream']]=kt
                    info[eval(st.source)['stream']]['live_task']={
                        'command':st.command,
                        'pull':eval(st.source)['input'],
                        'begintime':st.start_time,
                        'task_id':st.id,
                        'log':st.log
                    }
                elif st.template.name == 'kuwo-lunbo':
                    if eval(st.source)['stream'] not in info:
                        info[eval(st.source)['stream']]=kt
                    info[eval(st.source)['stream']]['reboard_task']={
                        'command':st.command,
                        'flv_file':eval(st.source)['filename'],
                        'begintime':st.start_time,
                        'task_id':st.id,
                        'log':st.log
                    }
            #logging.info(info)
            return render(request,'short_task.html',{"info":info,"flv_list":flv_list,"zhuanma_list":zhuanma_list})



class create_short_task(View):
    def post(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            post_data={}
            for i in request.POST:
                post_data[i]=request.POST[i]
            del post_data['csrfmiddlewaretoken']
            logging.info(post_data)
            if short_task_template.objects.filter(name=post_data['template']).exists():
                tem=short_task_template.objects.get(name=post_data['template'])
                rule=eval(tem.template)
                para=True
                for i in rule['must_parameters']:
                    if i not in post_data:
                        para=False
                if para:
                    task=short_task()
                    user=request.user
                    task.source=post_data
                    task.template=tem
                    task.create_user=user
                    task.status='running'
                    task.save()
                    short_task_run.delay(task.id)
                    #return HttpResponse('任务短创建成功')
                    return http.HttpResponseRedirect('/action/short_task')
                else:
                    return HttpResponse('lost args')
            else:
                return HttpResponse('模版名错误，请确认')


class upload_dianpian(View):
    def post(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            if request.FILES.get('dianpan'):
                obj = request.FILES.get('dianpan')
                source_file=os.path.join( 'media', 'video', 'upfile-'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'-'+obj.name)
                flv_file=os.path.join( 'media', 'dianpian', time.strftime("%Y%m%d%H%M%S", time.localtime())+'-'+obj.name.split('.')[-2]+'.flv')
                f = open(source_file, 'wb')
                for chunk in obj.chunks():
                    f.write(chunk)
                f.close()
                tem=short_task_template.objects.get(name='kuwo-dianpian')
        post_data={}
        for i in request.POST:
            post_data[i]=request.POST[i]
        post_data['sourcename']=source_file
        post_data['flvname']=flv_file
        del post_data['csrfmiddlewaretoken']
        logging.info( post_data )
        if short_task_template.objects.filter(name=post_data['template']).exists():
            tem=short_task_template.objects.get(name=post_data['template'])
            rule=eval(tem.template)
            para=True
            for i in rule['must_parameters']:
                if i not in post_data:
                    logging.info('para:'+str(para)+'  must_parameters lost '+str(i))
                    para=False
            if para:
                task=short_task()
                user=request.user
                task.source={'sourcename': source_file, 'flvname': flv_file, 'template': 'kuwo-dianpian'}
                task.template=tem
                task.create_user=user
                task.status='running'
                logging.info(task.__dict__)
                task.save()
                short_task_run.delay(task.id)
            #return HttpResponse('ok')
            return http.HttpResponseRedirect('/action/short_task')


class show_shrot_task_log(View):
    def get(self,request,active_code):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            if os.path.exists('task_log/'+str(active_code)):
               f=open('task_log/'+str(active_code),'r')
               info=''
               for line in f.readlines():
                   info=info+line+'</br>'
               f.close()
               #info.replace('frame=','</br>frame=')
               info=re.compile('frame=').sub('</br>frame=',info) 
               return HttpResponse(info)
            else:
                return HttpResponse('日志不存在')

class stop_short_task(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            id=request.GET.get('id')
            if id == None:
                return HttpResponse('参数错误')
            else:
                CloseTask(id)
                task=short_task.objects.get(id=id)
                if task.status=='done':
                    return http.HttpResponseRedirect('/action/short_task/')
                else:
                    return HttpResponse('任务状态异常，请检查')


class init2101(View):
    def get(self,request):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/users/login')
        else:
            logger = logging.getLogger("django")
            user=request.user
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
                mytask.create_user=request.user
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
            return http.HttpResponseRedirect('/action/')
        else:
            s='任务添加成功：'
            for ic in info['add']:
                s=s+ic+' '
            s=s+'</br>任务添加失败：'
            for ie in info['err']:
                s=s+ie+' '
            
            return HttpResponse(s)
