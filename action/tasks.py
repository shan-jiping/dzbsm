import time
from celery import task as ct
from celery import shared_task
from .models import task,task_result,group
from users.models import UserProfile
from .Myansible import my_ansible,my_ansible_play
from .get_host import host_list
from users.email_send import send_task_result
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
        mytask_result.result=fs
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
        send_task_result(email,mytask.id)
        return e
    
    
    
    
    


@shared_task
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

@shared_task
def test_run():
    logger = logging.getLogger("django")
    mytask=task.objects.get(id=103)
    tasks = [ dict(action=dict(module=mytask.model, args=dict(cmd=mytask.args)))]
    ans=my_ansible(tasks,'36.102.216.90')
    ans.run()
    fs=ans.get_result()
    print ans.__dict__
    logging.info(fs)
    
