#
#  Python modules
#
import os
import sys
import re

from optparse import OptionParser
import Jenkins
    
def main():
    parser = OptionParser()
    parser.add_option("-n", "--JenkinsServerName", dest="jenkins_server_name",help="JenkinsServerName")
    parser.add_option("-s", "--JenkinsUsername", dest="jenkins_username",help="JenkinsUsername")
    parser.add_option("-r", "--JenkinsPassword", dest="jenkins_password",help="JenkinsPassword")
    parser.add_option("-j", "--JobName", dest="job_name",help="JobName")
    parser.add_option("-b", "--PipelineScript", dest="pipeline_script",help="PipelineScript")
    (options, args) = parser.parse_args()
    jenkins = Jenkins.Jenkins(options.jenkins_server_name, options.jenkins_username, options.jenkins_password)
    job_name = options.job_name
    pipeline_script = options.pipeline_script
    
    jenkins.update_jar('slave.jar')
    jenkins.update_jar('jenkins-cli.jar')
    
    jenkins.login()
    jenkins.get_job(job_name)
    with open(job_name, 'r+') as f:
        new_script = re.sub('<script>[\\s\\S]*?</script>', '<script>' + pipeline_script + '</script>', f.read())
        f.seek(0)
        f.truncate()
        f.write(new_script)
    jenkins.update_job(job_name)
    jenkins.logout()
    os.remove(job_name)

if __name__ == "__main__":
    main()
