import re,copy,configuration,utils
#####################################
for module in configuration.stepsFiles() :
    exec("import steps%s as %s"%(module,module))
#####################################
def adjustSteps(inSteps, dataOrMc = None) :
    outSteps = []
    blackList = getattr(configuration, "stepsToDisableFor%s"%dataOrMc)()
    histoBlackList = getattr(configuration, "histogramsToDisableFor%s"%dataOrMc)()
    for step in inSteps :
        disable = False
        if step.name() in blackList : disable = True
        if isinstance(step, Other.histogrammer) :
            for matchString in histoBlackList :
                vars = [step.var] if type(step.var) is str else step.var
                for var in vars :
                    if re.search(matchString, var) : disable = True
        outSteps.append(copy.deepcopy(step))
        if disable : outSteps[-1].disable()
    return outSteps
#####################################
def adjustStepsForData(inSteps) : return adjustSteps(inSteps, "Data")
def adjustStepsForMc(inSteps)   : return adjustSteps(inSteps, "Mc")
#####################################
