#coding:utf-8
from django.conf.urls import url
from action.views import Update_host,task_test,Mytask,Mytest,mytask_result,init2101


urlpatterns = [
    url('^Update_host$', Update_host.as_view(), name="Update_host"),
    url('^task_test$', task_test.as_view(), name="task_test"),
    url('^$', Mytask.as_view(), name="mytask"),
    url('^test/c$', Mytest.as_view(), name="mytest"),
    url('^result/(?P<active_code>.*)/$', mytask_result.as_view(), name="mytask_result"),
    url('^init/2101/$', init2101.as_view(), name="init2101"),
]
