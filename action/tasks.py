import time
from celery import task as ct
from celery import shared_task
from .models import task,task_result,group,short_task,short_task_template
from users.models import UserProfile
from .Myansible import my_ansible,my_ansible_play
from .get_host import host_list
from users.email_send import send_task_result,send_task_faild
from ffmpy import FFmpeg
from action.ShortTask import ShortTask
import logging
import os




@shared_task
def play_book_crontab(hosts,play_book,email):
    user = UserProfile.objects.get(username='crontab')
    mytask=task()
    mytask.create_user=user
    mytask.status='init'
    mytask.Type='playbook'
    mytask.group=group.objects.get(name=hosts)
    mytask.model=play_book
    mytask.args=''
    mytask.save()
    mytask_result=task_result()
    mytask_result.task_id=mytask
    mytask_result.result=''
    mytask_result.save()
    try:
        mytask.status='running'
        mytask.save()
        play_book=my_ansible_play(mytask.model,extra_vars={'hosts':mytask.group.name})
        play_book.run()
        fs=play_book.get_result()
        mytask_result.result=str(fs)
        mytask_result.save()
        mytask.status='done'
        mytask.save()
        send_task_result(email,mytask.id)
        return fs
    except Exception, e:
        mytask.status='error'
        mytask.save()
        logging.error('+++++++++++++++++++++++++++++++++++')
        logging.error(e)
        logging.error(str(fs))
        send_task_faild('shanjiping@fastcdn.com',mytask.id)
        return e
    
    
    
    
@shared_task(bind=True) 
def ffmpy_test(self,task_info):
    logging.info(self.request.id)
    t=FFmpeg(
        executable=task_info['executable'],
        global_options=task_info['global_options'],
        inputs=task_info['inputs'],
        outputs=task_info['outputs'],
        logfile='task_log/'+str(self.request.id)
    )
    while True:
        logging.info(t.cmd)
        try:
            t.run()
        except Exception, e:
            logging.error('+++++++++++++++++++++++++++++++++++')
            logging.error(e)

@shared_task(bind=True)
def short_task_run(self,task_id):
    task=short_task.objects.get(id=task_id)
    task.celery_task_id=self.request.id
    task.log='task_log/'+str(self.request.id)
    task.save()
    tem=short_task_template.objects.get(id=task.template_id)
    template_type=tem.type
    ct=ShortTask(task_id)
    if template_type=='nokill':
        print 'nokill task'
        while True:
            task=short_task.objects.get(id=task_id)
            try:
                if task.status != 'done':
                    logging.info('short_task id:'+str(task_id)+' template_type '+str(template_type)+'  status '+str(task.status) )
                    ct.run()
            except Exception, e:
                logging.info('restart task '+str(task_id))
                print e
            time.sleep(2)
    elif template_type=='default':
        logging.info('short_task id:'+str(task_id)+' template_type '+str(template_type) )
        try:
            ct.run()
        except Exception, e:
            print e    
        task.status='done'
        task.save()




@shared_task()
def update_hosts():
    logger = logging.getLogger("django")
    logger.info('update host list')
    host_list()
    logger.info('update host list  done')

@shared_task
def task_run(id):
    logger = logging.getLogger("django")
    mytask=task.objects.get(id=id)
    logger.info(str(mytask.__dict__))
    mytask.status='running'
    mytask.save()
    try:
        tasks = [ dict(action=dict(module=mytask.model, args=dict(cmd=mytask.args)))]
        if mytask.group_id !=None:
            ans=my_ansible(tasks,mytask.group.name)
        else:
            ans=my_ansible(tasks,mytask.host.ip)
        ans.run()
        #logging.info(ans.__dict__)
        fs=ans.get_result()
        mytask_result=task_result.objects.get(task_id_id=mytask)
        mytask_result.result=fs
        mytask_result.save()
        if 'success' in fs and len(fs['success']) >0:
            mytask.status='done'
        else:
            mytask.status='error'
        mytask.save()
        #logging.info('------------------------------------')
        #logging.info(ans.__dict__)
        #logging.info(fs)
        #logging.info(os.environ)
        #logging.info(mytask.__dict__,mytask_result.__dict__)
        return ans.get_result()
    except Exception, e:
        mytask.status='error'
        mytask.save()
        logging.error('+++++++++++++++++++++++++++++++++++')
        logging.error(e)
        return e

@shared_task
def pb_run(id):
    logger = logging.getLogger("django")
    mytask=task.objects.get(id=id)
    logger.info(str(mytask.__dict__))
    mytask.status='running'
    mytask.save()
    try:
        if mytask.group_id !=None:
            play_book=my_ansible_play(mytask.model,extra_vars={'hosts':mytask.group.name})
        else:
            play_book=my_ansible_play(mytask.model,extra_vars={'hosts':mytask.host.ip})
        play_book.run() 
        fs=play_book.get_result()
        mytask_result=task_result.objects.get(task_id_id=mytask)
        mytask_result.result=fs
        mytask_result.save()
        mytask.status='done'
        mytask.save()
        return fs
    except Exception, e:
        mytask.status='error'
        mytask.save()
        logging.error('+++++++++++++++++++++++++++++++++++')
        logging.error(e)
        return e

