#coding:utf-8
from django.conf.urls import url
from action.views import Update_host,task_test,Mytask,mytask_result,init2101,get_kuwoact,kuwo_act,del_kuwo_act,create_act,Cronttask,create_short_task,show_short_task,stop_short_task,upload_dianpian,show_shrot_task_log


urlpatterns = [
    url('^Update_host$', Update_host.as_view(), name="Update_host"),
    url('^task_test$', task_test.as_view(), name="task_test"),
    url('^$', Mytask.as_view(), name="mytask"),
    url('^result/(?P<active_code>.*)/$', mytask_result.as_view(), name="mytask_result"),
    url('^init/2101/$', init2101.as_view(), name="init2101"),
    url('^del_kuwo',del_kuwo_act.as_view(),name="del_kuwo_act"),
    url('^kuwo_act',kuwo_act.as_view(),name="kuwo_act"),
    url('^kuwo',get_kuwoact.as_view(),name="kuwo_act_fdl"),
    url('^create_act',create_act.as_view(),name="create_act"),
    url('^crontab',Cronttask.as_view(),name="cront_task"),
    url('^create_short_task',create_short_task.as_view(),name="short_task"),
    url('^short_task',show_short_task.as_view(),name="short_task_list"),
    url('^upload_dianpian',upload_dianpian.as_view(),name="upload_dianpian"),
    url('^task_log/(?P<active_code>.*)/$',show_shrot_task_log.as_view(),name="show_shrot_task_log"),
    url('^stop_short_task',stop_short_task.as_view(),name="stop_short_task"),
    url('^short_task',create_short_task.as_view(),name="short_task"),
    url('^kuwo',get_kuwoact.as_view(),name="kuwo_act_fdl")
]
