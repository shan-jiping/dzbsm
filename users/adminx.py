# coding:utf-8
from crispy_forms.layout import Fieldset
from django.contrib.auth.models import Group, Permission

import xadmin
from xadmin import views
from .models import UserProfile,EmailVerifyRecord
from xadmin.plugins.auth import UserAdmin
from django.utils.translation import ugettext as _
from xadmin.models import Log


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True
class GlobalSettings(object):
    site_title = 'zxjy管理后台'
    site_footer = 'zxjy管理后台'
    menu_style="accordion"


class UserProfileAdmin(UserAdmin):
    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                Main(
                    Fieldset('',
                             'username', 'password',
                             css_class='unsort no_title'
                             ),
                    Fieldset(_('Personal info'),
                             Row('first_name', 'last_name'),
                             'email'
                             ),
                    Fieldset(_('Permissions'),
                             'groups', 'user_permissions'
                             ),
                    Fieldset(_('Important dates'),
                             'last_login', 'date_joined'
                             ),
                ),
                Side(
                    Fieldset(_('Status'),
                             'is_active',  'is_superuser',
                             ),
                )
            )
        return super(UserAdmin, self).get_form_layout()

class EmailVerifyRecordAdmin(object):
    # 配置后台我们需要显示的列
    list_display=['code','email','send_type','send_time']
        # 配置搜索字段,不做时间搜索
    search_fields=['code','email','send_type']
        # 配置筛选字段
    list_filter=['code','email','send_type','send_time']
    model_icon = 'fa fa-envelope'





xadmin.site.register(EmailVerifyRecord,EmailVerifyRecordAdmin)
xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView,GlobalSettings)
