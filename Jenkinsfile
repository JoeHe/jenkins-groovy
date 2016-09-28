#!groovy

jobDisplayName = env.BUILD_NUMBER
//Ecsworker path \\10.35.237.85\c$\JenkinsFiles\automation-jenkins-scripts
envFolder = "/media/ecsworkershare/automation-jenkins-scripts/environment/"
projFolder = "/media/ecsworkershare/automation-jenkins-scripts/project/"
gitRepoPath = "C:\\JenkinsFiles\\automation-jenkins-scripts"
//Environment
envs = [:]

@NonCPS
def SetJobName(){
		def myvariables = env.getEnvironment()
		for(myvar in myvariables){
			if(myvar.key ==~ /.*BUILD_NUMBER/){
				jobDisplayName = myvar.value
			}
		}
		if(jobDisplayName != env.BUILD_NUMBER){
			currentBuild.setDisplayName("#" + jobDisplayName)
		}
		if(myvariables['PRODUCTTYPE'] == null || myvariables['ENVFILE'] == null || myvariables['PROJFILE'] == null){
			throw new Exception ("""\nERROR: Please make sure added below 3 string parameters for job:<br />
			********* 3 necessary parameters ****************<br />
			*************************************************<br />
			PRODUCTTYPE(eg: IWD, C3D or Plant...)<br />  
			ENVFILE(eg: IWD_Main_Win81.xml)<br />              
			PROJFILE(eg: IWD_Main_Win81.xml)<br />            
			*************************************************
			""")			
		}	
}

@NonCPS
def AddParemeterToEnvs(){
	def myvariables = env.getEnvironment()
    for (v in myvariables) {
	   if(!v.key.contains('JENKINS_')&& !v.key.contains('HUDSON_')&& !v.key.contains('JOB_')&& v.key!='CLASSPATH'&& v.key!='BUILD_URL'){
           envs.putAt(v.key, v.value)
       }
    }
}

@NonCPS
def GetEnvs(xml) {
  AddParemeterToEnvs()
  def env = new XmlParser().parse(xml)
  for(itr in env){
    def n = itr.name()
    def v = itr.text()
    if (n == "include") {
      GetEnvs(envFolder+ PRODUCTTYPE + "/" + v)
    }
    else {
      def matcher = (v =~ /\$\{.*?\}/)
      for(mt in matcher){
          if (envs[mt[2..-2]] != null) {
          v = v.replace(mt, envs[mt[2..-2]])
        }
      }
      envs[n] = v
    }
  }
}

@NonCPS
def printEnv(e) {
    String s = ""
    for(itr in e){
        s = s + itr.key + "=" + itr.value + "\n"
    }
	echo s
}

def SyncRepoFiles(){
	if(FORCESYNC == "true"|| FORCESYNC == "TRUE"){   
	node("lb_ecs_worker"){
			echo "sync specified env and project file from github on ecsworker!"
			checkOutCmd = """
				call cd /d ${gitRepoPath}\\environment\\${PRODUCTTYPE}
				call git checkout origin/master -- ${ENVFILE}
				call cd /d ${gitRepoPath}\\project\\${PRODUCTTYPE}
				call git checkout origin/master -- ${PROJFILE}
			"""
			try{
				bat checkOutCmd
			}catch(Exception e){				
				throw new Exception ("ERROR: failed to check out env file " + ENVFILE + " or project file " + PROJFILE + " from GitHub https://git.autodesk.com/ICP-HST/automation-jenkins-scripts on node ecsworker!!!", e)
			}		
	}	
   }
}

@NonCPS
def getNodeNames(String label) {
    def names = []
	for (node in hudson.model.Hudson.instance.getLabel(label).getNodes()) {
		names.add(node.getNodeName())
	}
	
	if(names.size() <= 0){
		currentBuild.result = "FAILURE"
		throw new Exception ("ERROR: can't find nodes with label [${label}], please make sure added to jenkins server!!!")		
	}
    return names
}

@NonCPS
def ReplaceEnv(str) {
    def matcher = (str =~ /\$\{.*?\}/)
    for(mt in matcher){
           if (envs[mt[2..-2]] != null) {
            str = str.replace(mt, envs[mt[2..-2]])
        }
      }
	return str
}

def GetRuntimeScript(script) {
	return ReplaceEnv(script)
}

def RunBAT(script, continueOnFail) {   
	s = GetRuntimeScript(script)
	if(continueOnFail == true){
		try{
			bat s
		}catch(Exception e){}
	}
	else{
		bat s
	}
	//echo s	
}

def RunNode(runOn, runScript, timeOutMinutes, continueOnFail){
	def to
	def continueFail	
	timeOutMinutes == null?(to = 65):(to = timeOutMinutes.toInteger())
	continueOnFail == null?(continueFail = false):(continueFail = true)	
	node(runOn){
	    try{
		timeout(to) {
			RunBAT(runScript, continueFail)
		}
	    }catch(Exception e){
            currentBuild.result = "FAILURE"
			throw new Exception ("ERROR: failed to execute below script on node [${runOn}]:<br />${runScript}", e)
	    }
    }
}


def AddParralleBroadMaps(branches, name, runOn, runScript, timeOutMinutes, continueOnFail){
	for (nodeName in getNodeNames(runOn)) {
		def temp = nodeName
		branches["${name}_on_${temp}"] = {
            RunNode(runOn, runScript, timeOutMinutes, continueOnFail)
	    }
	}      
}


def ParseProj(xml) {
    def proj = new XmlParser().parse(xml)
	def branches = [:]
	for(itr in proj){
	    def name = itr.name()
        def runMode = itr.attribute("runMode")
        def runOn = ReplaceEnv(itr.attribute("runOn"))
        def runScript = itr.attribute("runScript")
        def include = itr.attribute("include")
		def continueOnFail = itr.attribute("continueOnFail")
		def timeOutMinutes = ReplaceEnv(itr.attribute("timeOut"))
       
        if (name == "stage"){
			if(branches.size() > 0){
				parallel branches
                branches.clear()
			}
			stage itr.attribute("stageName")
			//return  //windows 
			continue  //ubuntu
		}
		
		if (runMode == null) {              								
			if(branches.size() > 0){
				parallel branches
                branches.clear()
			}
			if(getNodeNames(runOn)){
				RunNode(runOn,runScript,timeOutMinutes,continueOnFail)
			}
        } else if (runMode == "parallel_broadcast") {                           				
				AddParralleBroadMaps(branches, name, runOn, runScript, timeOutMinutes, continueOnFail)							
        } else if (runMode == "parallel") { 				               							
				branches["${name}_on_${runOn}"] = {
						RunNode(runOn, runScript, timeOutMinutes, continueOnFail)
					}
         } else if (runMode == "broadcast") {
				if (branches.size() > 0) {
                    parallel branches
                    branches.clear()
                }		
                for (nodeName in getNodeNames(runOn)) {
                    RunNode(runOn, runScript, timeOutMinutes, continueOnFail)
                }
            } else {
                throw new Exception ("Incorrect mode")
            }  
	}
	if (branches.size() > 0 ) {                   
		parallel branches
        branches.clear()
    }		
}

def NotifyFailed(errorInfo, failRecipient) {
  emailext (	
      subject: "BUILD FAILED: Job ${env.JOB_NAME} - Build # ${jobDisplayName}",
      body: """<p>FAILED: ${env.JOB_NAME} - Build # ${jobDisplayName}</p>
        <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} ${jobDisplayName}</a> for details.</p>
		<p>ERROR INFO:<br />${errorInfo}</p>
		<p><br />Thanks<br />ICP Automation QA</p>""",
	  to: "${failRecipient}"
    )
}

node{
    try{
	  timestamps {
		stage 'SyncRepoFiles'
		SetJobName()
		SyncRepoFiles()
		GetEnvs(envFolder + PRODUCTTYPE + "/" + ENVFILE)
		printEnv(envs)		
		ParseProj(projFolder + PRODUCTTYPE + "/" + PROJFILE)
	  }
	}catch(Exception e){
	    currentBuild.result = "FAILURE"
	    // If build failed, send a notifications
		failRecipient = envs.containsKey('FAILRECIPIENT')? envs['FAILRECIPIENT'] : "aec.team.cetus@autodesk.com,v1g6h4a8d4l7q5d8@autodesk.slack.com"
	    NotifyFailed(e, failRecipient)
        throw e
	}
}
