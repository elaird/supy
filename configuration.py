def sourceFiles() :
    return ["pragmas.h","helpers.C"]

def batchScripts(hostName) :
    d = {"lx05.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
         "lx06.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
         }
    assert hostName in d,"hostname %s not recognized"%hostName
    return d[hostName]
