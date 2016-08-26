#!groovy

def SetJobName(){
    def myvariables = getBinding().getVariables()
    def jobName
    for(myvar in myvariables){
       if(myvar.key ==~ /.*BUILD_NUMBER/){
          jobName = myvar.value
        }
    }
    if(jobName){
      currentBuild.setDisplayName("#" + jobName)
    }
}
SetJobName()

envFolder = "/media/windowssharesh02/environment/"
projFolder = "/media/windowssharesh02/project/"

//Environment
envs = [:]

def AddParemeterToEnvs(){
    def myvariables = getBinding().getVariables()
    for (v in myvariables) {
       if(v.key != 'steps'&& v.key != 'envs'){ 
           envs.putAt(v.key, v.value)
       }
    }
}

def GetEnvs(xml) {
  AddParemeterToEnvs()
  def env = new XmlParser().parse(xml)
  for(it in env){
    def n = it.name()
    def v = it.text()
    if (n == "include") {
      GetEnvs(envFolder+ ProductType + v)
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
    for(it in e){
        s = s + it.key + "=" + it.value + "\n"
    }
    echo s
}

GetEnvs(envFolder + ProductType + envFile)
printEnv(envs)

@NonCPS
def getNodeNames(String label) {
    def names = []
	for (node in hudson.model.Hudson.instance.getLabel(label).getNodes()) {
		names.add(node.getNodeName())
	}
	
	if(names.size() <= 0){
		throw new Exception ("ERROR: can't find nodes with label [${label}], please make sure added to jenkins server!!!")
		currentBuild.result = FAILURE  
	}
    return names
}

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
		timeout(to) {
			RunBAT(runScript, continueFail)
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
    def b4runbranches = [:]
	def runbranches = [:]
	def aftrunbranches = [:]
	for(it in proj){
	     def name = it.name()
        def runMode = it.attribute("runMode")
        def runOn = ReplaceEnv(it.attribute("runOn"))
        def runScript = it.attribute("runScript")
        def include = it.attribute("include")
		def continueOnFail = it.attribute("continueOnFail")
		def timeOutMinutes = ReplaceEnv(it.attribute("timeOut"))
       
        if (name == "stage"){
			if(branches.size() > 0){
				parallel branches
                branches.clear()
			}
			stage it.attribute("stageName")
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

ParseProj(projFolder + ProductType + projFile)
