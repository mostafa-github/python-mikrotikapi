#!/usr/bin/python
import paramiko
import logging

console = logging.StreamHandler()
logging.getLogger('paramiko.transport').addHandler(console)




class SSHClient(object):
    """SSH warapper around the paramiko library that can run commands and return the results in string."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def run(self, cmd):
        """Run command cmd and return its output."""
        t = paramiko.SSHClient()
        t.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        t.connect(self.hostname, port = self.port, username = self.username, password = self.password)
        outs = t.exec_command(cmd)
        if outs:
            res = outs[1].read()
            t.close()
            return res
        else:
            t.close()
            raise Exception('ssh output is None')
