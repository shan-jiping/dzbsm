import errno
import shlex
import subprocess
from action.models import short_task,short_task_template
import re
import os
import time
import signal

def CloseTask(id):
    from celery.task.control import revoke
    task=short_task.objects.get(id=id)
    revoke(task.celery_task_id, terminate=True)
    time.sleep(2)
    for i in range(0,3):
        fpid=os.popen("lsof "+task.log+" | grep ffmpeg |awk '{print $2}'|sort|uniq|head -n 1").read().strip()
        if fpid != '':
           try:
               os.kill(int(fpid), signal.SIGKILL)
           except Exception, e:
               print e
        else:
           break
    task.status='done'
    task.save()


class ShortTask(object):
    def __init__(self,id,global_options=None):
        task=short_task.objects.get(id=id)
        tem=eval(short_task_template.objects.get(id=task.template_id).template)
        source=eval(task.source)
        self.executable = tem['executable']
        self._cmd = [self.executable]
        self.logfile=task.log

        global_options = global_options or []
        # add global_options  
        if _is_sequence(global_options): # global_options is a class
            normalized_global_options = []
            for opt in global_options:
                normalized_global_options += shlex.split(opt)
        else:
            normalized_global_options = shlex.split(global_options)
        self._cmd += normalized_global_options
        #self._cmd += _merge_args_opts(inputs, add_input_option=True)
        #self._cmd += _merge_args_opts(outputs)

        # add template and source info
        self._cmd += _merge_args_opts(tem,source)
        self.cmd = subprocess.list2cmdline(self._cmd)
        self.process = None
        task.command=self.cmd
        task.save()

    def __repr__(self):
        return '<{0!r} {1!r}>'.format(self.__class__.__name__, self.cmd)

    def run(self, input_data=None, stdout=None, stderr=None):
        try:
            f=open(self.logfile,'a')
            self.process = subprocess.Popen(
                self._cmd,
                stdin=subprocess.PIPE,
                stdout=f.fileno(),
                stderr=f.fileno()
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise STExecutableNotFoundError("Executable '{0}' not found".format(self.executable))
            else:
                raise

        out = self.process.communicate(input=input_data)
        if self.process.returncode != 0:
            raise STRuntimeError(self.cmd, self.process.returncode, out[0], out[1])

        return out

class STExecutableNotFoundError(Exception):
    """Raise when executable was not found."""


class STRuntimeError(Exception):
    def __init__(self, cmd, exit_code, stdout, stderr):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

        message = "`{0}` exited with status {1}\n\nSTDOUT:\n{2}\n\nSTDERR:\n{3}".format(
            self.cmd,
            exit_code,
            (stdout or b'').decode(),
            (stderr or b'').decode()
        )

        super(STRuntimeError, self).__init__(message)


def _is_sequence(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str)



def _merge_args_opts(template,source):
    merged = []
    for s in template['sequence']:
        if '{*' in s and '*}' in s:
            arg=s.split('*')[1].strip()
            d=arg.split('[')[0]
            seq=int(arg.split('[')[1].split(']')[0])
            pattern = re.compile(r'\{\* .+ \*\}')
            s=re.sub(pattern,source[template[d][seq]],s)
            merged.append(s)
        else:
            merged.append(s)
    return merged