#coding:utf-8
from __future__ import unicode_literals

from django.db import models
from users.models import UserProfile
from datetime import datetime
# Create your models here.

class hosts(models.Model):
    source_CHOICES=(
        ("ansible","系统"),
        ("custom","自定义")
    )
    ip=models.CharField(max_length=50, verbose_name=u"IP")
    port=models.IntegerField(default=55667, verbose_name=u"PORT")
    user=models.CharField(max_length=20, verbose_name=u"管理用户")
    pwd=models.CharField(max_length=50, verbose_name=u"管理用户密码")
    ips=models.CharField(max_length=200, verbose_name=u"IP")
    source=models.CharField(choices=source_CHOICES,max_length=20, verbose_name=u"来源",null=True, blank=True)
    status=models.CharField(max_length=50, verbose_name=u"状态")
    class Meta:
        verbose_name = u"主机"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.ip
class group(models.Model):
    source_CHOICES=(
        ("ansible","系统"),
        ("custom","自定义")
    )
    source=models.CharField(choices=source_CHOICES,max_length=50, verbose_name=u"主机来源",null=True, blank=True)
    name=models.CharField(max_length=50, verbose_name=u"主机组")
    add_time=models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    create_user=models.ForeignKey(UserProfile, verbose_name=u"创建用户", null=True, blank=True)
    class Meta:
        verbose_name = u"主机组"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.name
class hosts_group(models.Model):
    host_id = models.ForeignKey(hosts, verbose_name=u"主机", null=True, blank=True)
    group_id = models.ForeignKey(group, verbose_name=u"主机组", null=True, blank=True)
    class Meta:
        verbose_name = u"主机组关系"
        verbose_name_plural = verbose_name

class short_task_template(models.Model):
    name=models.CharField(max_length=50, verbose_name=u"短任务模版名",unique=True)
    type=models.CharField(max_length=10, verbose_name=u"短任务模版类型",null=True,default='default')
    template=models.TextField(null=True, blank=True,verbose_name="短任务模版")
    class Meta:
        verbose_name = u"短任务模版"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.name

class short_task(models.Model):
    status_CHOICES=(
        ("running","进行中"),
        ("done","已结束")
    )
    celery_task_id=models.CharField(max_length=50, verbose_name=u"celery_task_id",null=True, blank=True)
    source=models.TextField(null=True, blank=True,verbose_name="源数据")
    template=models.ForeignKey(short_task_template, verbose_name=u"模版", null=True, blank=True)
    create_user=models.ForeignKey(UserProfile, verbose_name=u"创建用户", null=True, blank=True)
    start_time=models.DateTimeField(default=datetime.now, verbose_name=u"开始时间")
    end_time=models.DateTimeField(default=datetime.now,verbose_name=u"结束时间",null=False)
    status=models.CharField(choices=status_CHOICES, max_length=15, verbose_name=u"状态")
    log=models.CharField(max_length=50, verbose_name=u"任务日志",null=True, blank=True)
    result=models.CharField(max_length=50, verbose_name=u"任务结果",null=True, blank=True)
    command=models.CharField(max_length=1000, verbose_name=u"运行命令",null=True, blank=True)
    class Meta:
        verbose_name = u"短任务任务"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.celery_task_id

class task(models.Model):
    action_CHOICES=(
        ("ansible","ansible"),
        ("playbook","动作组"),
        ("conn","链接主机")
    )
    status_CHOICES=(
        ("init","任务初始化"),
        ("start","开始"),
        ("running","进行中"),
        ("error","错误"),
        ("done","已结束")
    )
    Type=models.CharField(choices=action_CHOICES, max_length=10, verbose_name=u"动作")
    group=models.ForeignKey(group, verbose_name=u"主机组", null=True, blank=True)
    host=models.ForeignKey(hosts, verbose_name=u"主机", null=True, blank=True)
    create_user=models.ForeignKey(UserProfile, verbose_name=u"创建用户", null=True, blank=True)
    create_time=models.DateTimeField(default=datetime.now, verbose_name=u"创建时间")
    model=models.CharField(max_length=50, verbose_name=u"模块/playbook",null=True, blank=True)
    args=models.CharField(max_length=150, verbose_name=u"参数/command",null=True, blank=True)
    status=models.CharField(choices=status_CHOICES, max_length=15, verbose_name=u"状态")
    class Meta:
        verbose_name = u"任务"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.create_user.username

class task_result(models.Model):
    task_id=models.ForeignKey(task, verbose_name=u"任务", null=True, blank=True)
    result=models.TextField(null=True, blank=True,verbose_name="结果")
    class Meta:
        verbose_name = u"任务结果"
        verbose_name_plural = verbose_name


class ys_uid(models.Model):
    status_CHOICES=(
        ("using","正在使用"),
        ("free","未使用"),
        ("Disable","不可用")
    )
    uid=models.CharField(max_length=50, verbose_name=u"UID")
    host=models.ForeignKey(hosts, verbose_name=u"主机", null=True, blank=True)
    status=models.CharField(choices=status_CHOICES, max_length=15, verbose_name=u"状态")
    
    class Meta:
        verbose_name = u"央视UID"
        verbose_name_plural = verbose_name
