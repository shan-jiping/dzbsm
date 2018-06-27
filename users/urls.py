#coding:utf-8
from django.conf.urls import url
from users.views import RegisterView,LoginView,ActiveUserView,LogoutView,ForgetPwdView,ResetView,UpdatePwdView,ModifyPwdView,SendEmailCodeView,UserInfoView


urlpatterns = [
    url('^info$', UserInfoView.as_view(), name="user_info"),
    url('^register', RegisterView.as_view(), name="register"),
    url('^login',LoginView.as_view(), name="login"),
    url('^logout$', LogoutView.as_view(), name="logout"),
    url('^forget_pwd$', ForgetPwdView.as_view(), name="forget_pwd"),
    url('^active/(?P<active_code>.*)/$',ActiveUserView.as_view(), name= "user_active"),
    url('^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url('^modify_pwd$', ModifyPwdView.as_view(), name="modify_pwd"),
    url('^update/pwd$', UpdatePwdView.as_view(), name="update_pwd"),
    url(r'^sendemail_code/$',SendEmailCodeView.as_view(),name="sendemail_code"),


]
