#coding:utf-8
'''
Created on 2017年4月7日

@author: shanjiping
'''
import time
import os
import json
import urllib2
import urllib


def get_tgt_online():
    try:
        url = 'https://apis.dnion.com:8243/cas/v1/tickets'
        data = {
            'username': 'shanjiping@dnion.com',
            'password': 'dnion1234' }
        request = urllib2.Request(url)
        response=urllib2.urlopen(request,urllib.urlencode(data))
        return response.headers['Location'].split('/')[-1]
    except Exception,e:
        print e
def update_tgt(cachefile):
    TGT = get_tgt_online()
    f=open(cachefile,'a')
    f.write(TGT)
    f.close
    return TGT
def get_tgt(cachefile):
    if not os.path.exists(cachefile):
        TGT = update_tgt(cachefile)
    else:
        t0 = os.path.getctime(cachefile)
        t1 = time.time()
        if t1 - t0 > 25200:
            TGT = update_tgt(cachefile)
        else:
            f = open(cachefile, 'r')
            TGT = f.read()
            f.close()
    return TGT

def get_platform_list(platform):
    url='https://apis.dnion.com:8243/machine/platform/allmachines?plNameEn='+platform
    my_TGT='TGT'
    TGT = get_tgt(my_TGT)
    req=urllib2.Request(url)
    req.add_header('Authorization',TGT)
    req.add_header('username','shanjiping@dnion.com')
    res=json.loads(urllib2.urlopen(req).read())
    return res


if __name__=='__main__':
    res=get_platform_list('NNOP015')
    for i in res:
        for j in range(len(i['platformMachineIpList'])):
            print i['currentPlatform'],i['platformMachineIpList'][j]['ndName'],i['platformMachineIpList'][j]['ndName'],i['platformMachineIpList'][j]['mcipIp'],i['cliName']
