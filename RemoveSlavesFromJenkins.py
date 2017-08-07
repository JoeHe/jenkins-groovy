#
#  Python modules
#
import os
import sys
import exceptions
import json
from optparse import OptionParser

import Jenkins
    
def main():
    parser = OptionParser()
    parser.add_option("-n", "--JenkinsServerName", dest="jenkins_server_name",help="JenkinsServerName")
    parser.add_option("-s", "--JenkinsUsername", dest="jenkins_username",help="JenkinsUsername")
    parser.add_option("-r", "--JenkinsPassword", dest="jenkins_password",help="JenkinsPassword")
    parser.add_option("-j", "--JSONFileName", dest="json_filename",help="JSONFile")
    (options, args) = parser.parse_args()
    jenkins = Jenkins.Jenkins(options.jenkins_server_name, options.jenkins_username, options.jenkins_password)
    json_filename = options.json_filename
    
    json_obj = json.load(file(json_filename))
    jenkins.login()
    for vm_info in json_obj:
        vm_name = vm_info['Name']
        vm_ip = vm_info['IpAddress']
        # remove node(if exists)
        jenkins.remove_node(vm_name)
    jenkins.logout()

if __name__ == "__main__":
    main()
