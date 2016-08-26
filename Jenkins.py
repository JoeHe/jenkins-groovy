import os
import subprocess
import time
import urllib2, base64
import re

class Jenkins:
    def __init__(self, server_name, server_port, username, password): 
        self.server_name = server_name
        self.server_port = server_port
        self.username = username
        self.password = password
        
    def login(self):
        cmd = 'java -jar jenkins-cli.jar -s http://{0}:{1}/ login --username {2} --password {3}'.format(self.server_name, self.server_port, self.username, self.password)
        return os.system(cmd)
        
    def logout(self):
        cmd = 'java -jar jenkins-cli.jar -s http://{0}:{1}/ logout'.format(self.server_name, self.server_port)
        return os.system(cmd)

    def add_node(self, node_config):
        cmd = 'type {0}|java -jar jenkins-cli.jar -s http://{1}:{2}/ create-node'.format(node_config, self.server_name, self.server_port)
        return os.system(cmd)
    
    def remove_node(self, node_name):
        cmd = 'java -jar jenkins-cli.jar -s http://{1}:{2}/ delete-node {0}'.format(node_name, self.server_name, self.server_port)
        return os.system(cmd)
        
    def generate_agent_bat(self, computer_name, jenkins_home, is_secret):
        secret_param = ''
        if is_secret:
            request = urllib2.Request('http://{0}:{1}/computer/{2}/slave-agent.jnlp'.format(self.server_name, self.server_port, computer_name))
            base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            response = urllib2.urlopen(request)
            regex = re.compile('<argument>.*?</argument>')
            secret = regex.search(response.read()).group()[10:-11]
            secret_param = ' -secret ' + secret
        cmd = 'echo java -jar {3}\slave.jar -jnlpUrl http://{1}:{2}/computer/{0}/slave-agent.jnlp{4}> launchagent.bat'.format(computer_name, self.server_name, self.server_port, jenkins_home, secret_param)
        return os.system(cmd)
        
    def wait_node_online(self, node_name):
        cmd = 'java -jar jenkins-cli.jar -s http://{1}:{2}/ wait-node-online {0}'.format(node_name, self.server_name, self.server_port)
        proc = subprocess.Popen(cmd)
        timout = 30
        while proc.poll() is None and timout > 0:
            time.sleep(2)
            timout = timout - 2
        if timout <= 0:
            proc.kill()
            return -1
        else:
            return proc.returncode
