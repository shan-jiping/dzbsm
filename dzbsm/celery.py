# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from celery import Celery,platforms
from django.conf import settings

# set the default Django settings module for the 'celery_demo' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dzbsm.settings')
app = Celery('dzbsm')

# Using a string here means the worker will not have to
# pickle the object when using Windows.

platforms.C_FORCE_ROOT = True
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
