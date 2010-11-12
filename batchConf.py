d = {"lx05.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
     "lx06.hep.ph.ic.ac.uk":("icSub.sh","icJob.sh"),
     }

def scripts(hostName) :
    assert hostName in d,"hostname %s not recognized"%hostName
    return d[hostName]
