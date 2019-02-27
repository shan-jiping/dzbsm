#coding:utf-8
from __future__ import absolute_import, unicode_literals
from djcelery.models import  WorkerState,PeriodicTask, IntervalSchedule, CrontabSchedule
import xadmin


class PeriodicTaskAdmin(object):
    list_display = ['name','enabled','interval','crontab','args','description']


xadmin.site.register(IntervalSchedule) # 存储循环任务设置的时间
xadmin.site.register(CrontabSchedule) # 存储定时任务设置的时间
xadmin.site.register(PeriodicTask,PeriodicTaskAdmin) # 存储任务
#xadmin.site.register(TaskState) # 存储任务执行状态
xadmin.site.register(WorkerState) # 存储执行任务的worker
