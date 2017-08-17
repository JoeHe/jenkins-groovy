package harness
class Utilities implements Serializable {
    def steps
    def currentBuild
    def env
    def branches = [:]
    
    Utilities(steps, currentBuild, env) {
        this.steps = steps
        this.currentBuild = currentBuild
        this.env = env
    }

    def log(logTitle, logMsg) {
        def starLen = (60 - logTitle.length() - 2) / 2
        def starStr = ""
        def formatedLogMsg = ""
        for(def i=0; i<starLen; i++) {
            starStr += "*"
        }
        for(line in logMsg.split("\n")) {
            if(line.trim() != "") {
                formatedLogMsg += "    ${line.trim()}\n"
            }
        }
        def echoMsg = "    ${starStr} ${logTitle} ${starStr}\n${formatedLogMsg}    ${starStr}*${logTitle.replaceAll(/./, '*')}*${starStr}"
        steps.echo echoMsg
    }
    
    def logWarning(logMsg) {
        log("WARNING", logMsg)
    }

    def logInfo(logMsg) {
        log("INFO", logMsg)
    }

    def logError(logMsg) {
        log("ERROR", logMsg)
    }
    
    def runSerialBAT(label, commands, timeoutMin, continueOnFail) {
        def info = """
            Run batch on ${label}
            Timeout: ${timeoutMin} minutes
            Continue if fail: ${continueOnFail}
            Scripts:
            ${commands}
        """
        log("INFO", info)
        commands = commands.trim().replaceAll(/[\s]*[\n][\s]*/, "&&")
        try {
            steps.node(label) {
                steps.timeout(time:timeoutMin, unit:'MINUTES') {
                    steps.bat commands
                }
            }
        } catch(Exception ex) {
            if(continueOnFail) {
                currentBuild.result = "UNSTABLE"
                log("WARNING", "Failed to execute commands on node with label [${label}]:\n${commands}\n${ex.toString()}")
            } else {
                throw new Exception ("ERROR: Failed to execute commands on node with label [${label}]:<br />${commands}", ex)
            }
        }
    }
    
    def runBAT(label, commands, timeoutMin, continueOnFail, isBroadcast) {
        if (isBroadcast) {
            for (nodeName in getNodeNames(label)) {
                runSerialBAT(nodeName, commands, timeoutMin, continueOnFail)
            }
        } else {
            runSerialBAT(label, commands, timeoutMin, continueOnFail)
        }
    }
    
    def addParallelStep(stepName, closure) {
        branches["p${branches.size()}-${stepName}"] = closure
    }
    
    def addParallelStep(stepName, label, commands, timeoutMin, continueOnFail, isBroadcast) {
        if (isBroadcast) {
            for (nodeName in getNodeNames(label)) {
                def temp = nodeName
                addParallelStep(stepName, {
                    runSerialBAT(temp, commands, timeoutMin, continueOnFail)
                })
            }
        } else {
            addParallelStep(stepName, {
                runSerialBAT(label, commands, timeoutMin, continueOnFail)
            })
        }
    }
    
    def runParallelSteps() {
        steps.parallel branches
        branches.clear()
    }

    def getNodeNames(label) {
        def names = []
        for (node in hudson.model.Hudson.instance.getLabel(label).getNodes()) {
            if(!node.getComputer().isOffline()) {
                names.add(node.getNodeName())
            }
        }
        
        if(names.size() <= 0){
            currentBuild.result = "FAILURE"
            throw new Exception ("ERROR: can't find online nodes with label [${label}], please make sure added to jenkins server!!!")
        }
        return names
    }
    
    def sendFailureNotification(msg, recipient) {
        steps.emailext (
            subject: "BUILD FAILED: Job ${env.JOB_NAME} - Build # ${currentBuild.getDisplayName()}",
            body: """<p>FAILED: ${env.JOB_NAME} - Build # ${currentBuild.getDisplayName()}</p>
                <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} ${currentBuild.getDisplayName()}</a> for details.</p>
                <p>ERROR INFO:<br />${msg}</p>
                <p><br />Thanks<br />ICP Automation QA</p>""",
            to: "${recipient}"
        )
    }
    
    def setGlobalEnvVar(envMap) {
        def globalNodeProperties = hudson.model.Hudson.instance.getGlobalNodeProperties()
        def envVarsNodePropertyList = globalNodeProperties.getAll(hudson.slaves.EnvironmentVariablesNodeProperty.class)

        def newEnvVarsNodeProperty = null
        def envVars = null

        if ( envVarsNodePropertyList == null || envVarsNodePropertyList.size() == 0 ) {
          newEnvVarsNodeProperty = new hudson.slaves.EnvironmentVariablesNodeProperty();
          globalNodeProperties.add(newEnvVarsNodeProperty)
          envVars = newEnvVarsNodeProperty.getEnvVars()
        } else {
          envVars = envVarsNodePropertyList.get(0).getEnvVars()
        }
        for(kv in envMap.entrySet()) {
            envVars.put(kv.getKey(), kv.getValue())
        }
        hudson.model.Hudson.instance.save()
    }
}

return new Utilities(steps, currentBuild, env)
