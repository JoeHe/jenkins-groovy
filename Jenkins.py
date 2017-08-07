import os
import subprocess
import time
import urllib2, base64
import re
import urllib
import filecmp
import datetime
import sys

class Jenkins:
    def __init__(self, server_name, username, password): 
        self.server_name = server_name
        self.username = username
        self.password = password
        
    def login(self):
        cmd = 'java -jar jenkins-cli.jar -s {0} login --username {1} --password {2}'.format(self.server_name, self.username, self.password)
        return os.system(cmd)
        
    def logout(self):
        cmd = 'java -jar jenkins-cli.jar -s {0} logout'.format(self.server_name)
        return os.system(cmd)

    def add_node(self, node_config):
        cmd = 'type {0}|java -jar jenkins-cli.jar -s {1} create-node'.format(node_config, self.server_name)
        return os.system(cmd)
    
    def remove_node(self, node_name):
        cmd = 'java -jar jenkins-cli.jar -s {0} delete-node {1}'.format(self.server_name, node_name)
        return os.system(cmd)
        
    def generate_agent_bat(self, computer_name, jenkins_home, is_secret):
        secret_param = ''
        if is_secret:
            request = urllib2.Request('{0}computer/{1}/slave-agent.jnlp'.format(self.server_name, computer_name))
            base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            response = urllib2.urlopen(request)
            regex = re.compile('<argument>.*?</argument>')
            secret = regex.search(response.read()).group()[10:-11]
            secret_param = ' -secret ' + secret
        cmd = 'echo start /min java -jar {0}\slave.jar -jnlpUrl {1}computer/{2}/slave-agent.jnlp{3}> launchagent.bat'.format(jenkins_home, self.server_name, computer_name, secret_param)
        return os.system(cmd)
        
    def wait_node_online(self, node_name, timeout_sec = 300):
        orig_timeout = timeout_sec
        cmd = 'java -jar jenkins-cli.jar -s {0} wait-node-online {1}'.format(self.server_name, node_name)
        proc = subprocess.Popen(cmd, close_fds=True)
        while timeout_sec > 0:
            if not proc.poll() is None:
                if proc.returncode != 0:
                    print 'wait-node-online returns {0}'.format(proc.returncode)
                    proc = subprocess.Popen(cmd, close_fds=True)
                else:
                    return 0
            else:
                time.sleep(1)
                timeout_sec = timeout_sec - 1
        if timeout_sec <= 0:
            print 'Timeout of {0} seconds excceeded to connect to {1}'.format(orig_timeout, node_name)
            sys.stdout.flush()
            proc.kill()
            return -1
        else:
            return proc.returncode
        
    def update_jar(self, jar_name):
        if os.path.isfile(jar_name):
            temp_jar = 'temp-' + datetime.datetime.now().time().isoformat().replace(':', '-').replace('.', '-') + jar_name
            urllib.urlretrieve ("{jenkins_server}jnlpJars/{name}".format(jenkins_server=self.server_name, name=jar_name), temp_jar)
            if not filecmp.cmp(jar_name, temp_jar):
                os.system('copy {0} {1}'.format(temp_jar, jar_name))
            os.remove(temp_jar)
        else:
            urllib.urlretrieve ("{jenkins_server}jnlpJars/{name}".format(jenkins_server=self.server_name, name=jar_name), jar_name)

    def get_job(self, job_name):
        cmd = 'java -jar jenkins-cli.jar -s {0} get-job {1} >{1}'.format(self.server_name, job_name)
        return os.system(cmd)

    def update_job(self, job_name):
        cmd = 'java -jar jenkins-cli.jar -s {0} update-job {1} <{1}'.format(self.server_name, job_name)
        return os.system(cmd)
