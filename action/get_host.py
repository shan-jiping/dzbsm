#!/usr/local/bin/python
# -*- coding:utf8 -*-
import json
import os
from .models import hosts_group,hosts,group
from users.models import UserProfile

def host_list():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ans_host_path=os.path.join(BASE_DIR, "action/hosts")
    an_groups={}
    if os.path.getsize('/etc/ansible/cache/hosts') <= 500 :
        return {'error':'/etc/ansible/cache/hosts filesize is to small'}
        exit()
    if os.path.exists(ans_host_path):
        os.remove(ans_host_path)
    with open('/etc/ansible/cache/hosts','r') as json_file:
        an_groups=json.load(json_file)
    del an_groups['_meta']
    f=open(ans_host_path,'a')
    for g in an_groups:
        #print "["+g+"]"
        f.write("["+g+"]\n")
        for h in an_groups[g]['hosts']:
            if '#' in h:
                h=h.split(' ')[0]
            #print "ansible_ssh_host="+h+" ansible_ssh_port="+str(an_groups[g]['vars']['ansible_ssh_port'])+" ansible_ssh_user="+an_groups[g]['vars']['ansible_ssh_user']+" ansible_ssh_pass='"+an_groups[g]['vars']['ansible_ssh_pass']+"'"
            f.write(h+":"+str(an_groups[g]['vars']['ansible_ssh_port'])+" ansible_ssh_user="+an_groups[g]['vars']['ansible_ssh_user']+" ansible_ssh_pass='"+an_groups[g]['vars']['ansible_ssh_pass']+"'\n")
    f.close()
    result={}
    #all_host=hosts.objects.filter()
    #all_group=group.objects.filter()



#group check
    #sjp
    sjp=UserProfile.objects.get(username="sjp")
    for g in an_groups:
        if len(group.objects.filter(name=g))==0:
            newgroup=group()
            newgroup.source="ansible"
            newgroup.name=g
            newgroup.create_user=sjp  
            newgroup.save() 
            #result[g]='need add'


#host check
    ans_host_list={}
    for g in an_groups:
        for h in an_groups[g]['hosts']:
            h=h.split(' ')[0]
            ans_host_list[h]={'psss':an_groups[g]['vars']['ansible_ssh_pass'],'port':an_groups[g]['vars']['ansible_ssh_port'],'user':an_groups[g]['vars']['ansible_ssh_user'],'group':g}

    for h in ans_host_list:
        if len(hosts.objects.filter(ip=h))==0 :

            newhost=hosts()
            newhost.ip=h
            newhost.port=ans_host_list[h]['port']
            newhost.user=ans_host_list[h]['user']
            newhost.pwd=ans_host_list[h]['psss']
            newhost.ips="none"
            newhost.source="ansible"
            newhost.status="on"
            newhost.save()
            #result[h]=ans_host_list[h]
#hosts_group
    for g in an_groups:
        if len(group.objects.filter(name=g)) ==0:
            continue
        db_g=group.objects.get(name=g)
        g_h=hosts_group.objects.filter(group_id=db_g)
        db_hlist=[]
        for dbh in g_h:
           db_hlist.append(dbh.host_id.ip)
        #print db_hlist
        for h in an_groups[g]['hosts']:
            h=h.split(' ')[0]
            if h not in db_hlist:
                g_g=group.objects.get(name=g)
                g_h=hosts_group.objects.filter(group_id=g_g.id)
                newhosts_group=hosts_group()
                thishost=hosts.objects.get(ip=h) 
                thisgroup=group.objects.get(name=g)
                newhosts_group.host_id=thishost
                newhosts_group.group_id=thisgroup
                newhosts_group.save()
                result[g]=h
            #else:
            #   result[h]='not in list'
            
    

    return result

   
    

if __name__=='__main__':
    print host_list()
