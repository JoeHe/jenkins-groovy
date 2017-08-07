#
#  Python modules
#
import os
import sys
import exceptions
import json
from optparse import OptionParser
try: 
    import xml.etree.cElementTree as ET 
except ImportError: 
    import xml.etree.ElementTree as ET 

import Jenkins
    
def main():
    parser = OptionParser()
    parser.add_option("-n", "--JenkinsServerName", dest="jenkins_server_name",help="JenkinsServerName")
    parser.add_option("-s", "--JenkinsUsername", dest="jenkins_username",help="JenkinsUsername")
    parser.add_option("-r", "--JenkinsPassword", dest="jenkins_password",help="JenkinsPassword")
    parser.add_option("-v", "--SlaveName", dest="slave_name",help="SlaveName")
    parser.add_option("-i", "--SlaveIp", dest="slave_ip",help="SlaveIp")
    parser.add_option("-l", "--LabelName", dest="label_name",help="LabelName")
    parser.add_option("-t", "--NodeTemplateFileName", dest="node_templ_filename",help="NodeTemplateFileName")
    parser.add_option("-u", "--SlaveUsername", dest="slave_username",help="SlaveUsername")
    parser.add_option("-w", "--SlavePassword", dest="slave_password",help="SlavePassword")
    parser.add_option("-m", "--SlaveJenkinsHome", dest="slave_jenkins_home",help="SlaveJenkinsHome")
    (options, args) = parser.parse_args()
    jenkins = Jenkins.Jenkins(options.jenkins_server_name, options.jenkins_username, options.jenkins_password)
    slave_name = options.slave_name
    slave_ip = options.slave_ip
    label_name = options.label_name
    node_templ_filename = options.node_templ_filename
    slave_username = options.slave_username
    slave_password = options.slave_password
    slave_jenkins_home = options.slave_jenkins_home
    
    jenkins.update_jar('slave.jar')
    jenkins.update_jar('jenkins-cli.jar')

    # generate configuration for creating node
    tree = ET.parse(node_templ_filename)
    root = tree.getroot()
    root.find('./name').text = slave_name
    root.find('./description').text = slave_ip
    root.find('./remoteFS').text = slave_jenkins_home
    if label_name != slave_name:
        root.find('./label').text = '{0} {1}'.format(label_name, slave_name)
    else:
        root.find('./label').text = label_name
    temp_filename = slave_name + '.xml'
    tree.write(temp_filename)
    # remove node(if exists) and add node
    jenkins.login()
    jenkins.remove_node(slave_name)
    ret = jenkins.add_node(temp_filename)
    os.remove(temp_filename)
    if ret != 0:
        raise Exception('Failed to add node ' + slave_name)
    # copy bat and jar to slave
    jenkins.generate_agent_bat(slave_name, slave_jenkins_home, True)
    os.system('net use \\\\{0} /user:{1} {2}'.format(slave_ip, slave_username, slave_password))
    os.system('mkdir \\\\{0}\\{1}'.format(slave_ip, options.slave_jenkins_home.replace(':', '$')))
    os.system('copy launchagent.bat \\\\{0}\\{1}'.format(slave_ip, options.slave_jenkins_home.replace(':', '$')))
    os.system('copy launchagent.bat "\\\\{0}\\C$\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp"'.format(slave_ip))
    os.system('copy slave.jar \\\\{0}\\{1}'.format(slave_ip, options.slave_jenkins_home.replace(':', '$')))
    os.system('net use /delete \\\\{0}'.format(slave_ip))
    os.remove('launchagent.bat')
    # create task schedule to launch agent
    os.system('schtasks /create /S {0} /U {1} /P {2} /TN StartJenkinsAgent /TR "cmd /c {3}\\launchagent.bat" /SC MONTHLY /F'.format(slave_ip, slave_username, slave_password, slave_jenkins_home))
    os.system('schtasks /run /S {0} /U {1} /P {2} /TN StartJenkinsAgent'.format(slave_ip, slave_username, slave_password))
    ret = jenkins.wait_node_online(slave_name)
    if ret != 0:
        raise Exception('Failed to connect node {0}.  Return {1}'.format(slave_name, ret))
    jenkins.logout()

if __name__ == "__main__":
    main()
