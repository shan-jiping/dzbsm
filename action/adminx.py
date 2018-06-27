from .models import hosts,group,hosts_group,task,task_result,ys_uid
import xadmin


class hostsAdmin(object):
    list_display = ['ip','status','source']
    search_fields = ['ip','status','source']
class groupAdmin(object):
    list_display = ['name','add_time','create_user']
    search_fields = ['name']
class hosts_groupAdmin(object):
    list_display = ['host_id','group_id']
class taskAdmin(object):
    list_display = ['Type','create_user','create_time','status']
class task_resultAdmin(object):
    list_display = ['task_id','result']
class ys_uidAdmin(object):
    list_display = ['uid','host','status']
    search_fields = ['uid','status','host__ip']
xadmin.site.register(hosts, hostsAdmin)
xadmin.site.register(group, groupAdmin)
xadmin.site.register(hosts_group, hosts_groupAdmin)
xadmin.site.register(task,taskAdmin)
xadmin.site.register(task_result,task_resultAdmin)
xadmin.site.register(ys_uid,ys_uidAdmin)
