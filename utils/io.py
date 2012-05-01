import sys,os,subprocess,cPickle
#####################################
def mkdir(path) :
    try:
        os.makedirs(path)
    except OSError as e :
        if e.errno!=17 :
            raise e
#####################################        
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}
#####################################
def readPickle(fileName, errorMessage = "readPickle() failed", exitOnError = True) :
    try:
        with open(fileName) as pickleFile : return cPickle.load(pickleFile)
    except:
        print errorMessage, "   (cannot open %s)"%fileName
        if exitOnError: sys.exit(0)
def writePickle(fileName, payload, errorMessage = "writePickle() failed", exitOnError = True) :
    try:
        with open(fileName,'w') as pickleFile : cPickle.dump(payload,pickleFile)
    except:
        print errorMessage, "   (cannot open %s"%fileName
        if exitOnError: sys.exit(0)
#####################################        
def popPath(p, char = '/') : return char.join(p.split(char)[:-1])
#####################################
def pruneCrabDuplicates(inList, sizes, alwaysUseLastAttempt = False, location = "", numericallyIncrementingKeys = True ) :
    import re
    from collections import defaultdict
    # CRAB old : filepathWithName_JOB_ATTEMPT.root
    # CRAB new : filepathWithName_JOB_ATTEMPT_RANDOMSTRING.root
    pattern  =  r"(_\d+_)(\d+)(_?\w*)(\.root$)"
    recombine = "%s%s%d%s.root"

    versionDict = defaultdict(list)
    for inFile,size in zip(inList,sizes) :
        fields = re.split(pattern,inFile.strip('/'))
        versionDict[ (fields[0],fields[1]) ].append( (int(fields[2]), size, fields[3]) )

    resolved = 0
    abandoned = []
    outList = []
    for key,val in versionDict.iteritems() :
        front,job = key
        attempt,size,rnd = max(val)
        maxSize = max([v[1] for v in val])

        if size == maxSize or alwaysUseLastAttempt :
            fileName = recombine % (front,job,attempt,rnd)
            outList.append(fileName)
            if len(val) > 1 : resolved += 1
        else: abandoned.append((key,val))

    if abandoned or resolved :
        print "File duplications, unresolved(%d), resolved(%d) %s" % (len(abandoned), resolved, location)
        if abandoned : print "Rerun with 'alwaysUseLastAttempt = True' in order to recover the following:"
        for key,val in abandoned : print '\t', key[1], "{ %s }"%'|'.join(str((attempt,size)) for attempt,size,rnd in val)

    if numericallyIncrementingKeys :
        keys = set(int(key[1].replace("_","")) for key in versionDict)
        missing = set(range(1,max(keys)+1 if keys else 1)) - keys
        if missing : print "Possibly missing %d jobs {%s}"%(len(missing),','.join(str(i) for i in sorted(missing)))

    return outList
#####################################
def fileListFromSrmLs(dCachePrefix = None, dCacheTrim = None, location = None, itemsToSkip = [], sizeThreshold = -1, pruneList = True, alwaysUseLastAttempt = False) :
    fileList=[]
    sizes=[]
    offset = 0
    output = []
    #print cmd
    maxSrmls = 500
    while len(output) >= maxSrmls*offset :
        cmd="srmls --count %d --offset %d %s"% (maxSrmls,maxSrmls*offset,location)
        output += getCommandOutput(cmd)["stdout"].split('\n')
        offset += 1
    for line in output :
        if ".root" not in line : continue
        acceptFile = True
        fields = line.split()
        size = float(fields[0])
        fileName = fields[1]
        
        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile :
            fileList.append( (dCachePrefix+fileName) if not dCacheTrim else (dCachePrefix+fileName).replace(dCacheTrim, "") )
            sizes.append(size)

    if pruneList :   fileList=pruneCrabDuplicates(fileList, sizes, alwaysUseLastAttempt, location)
    return fileList
#####################################    
def fileListFromCastor(location, itemsToSkip = [], sizeThreshold = 0, pruneList = True, alwaysUseLastAttempt = False) :
    fileList=[]
    sizes = []
    cmd="nsls -l "+location
    #print cmd
    output = getCommandOutput(cmd)["stdout"]
    for line in output.split("\n") :
        if ".root" not in line : continue
        acceptFile=True
        fields=line.split()
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile :
            fileList.append("rfio:///"+location+"/"+fileName)
            sizes.append(size)
            
    if pruneList :   fileList=pruneCrabDuplicates(fileList, sizes, alwaysUseLastAttempt, location)
    return fileList
#####################################
def fileListFromEos(location, itemsToSkip = [], sizeThreshold=0, eos = "", xrootdRedirector = "") :
    fileList=[]
    sizes=[]

    cmd= eos+" ls -l "+location
    output = getCommandOutput(cmd)
    out = output["stdout"]
    err = output["stderr"]
    if output["returncode"] or 'command not found' in err :
        print '\n'.join([out, err])
        return fileList
    for line in out.split("\n") :
        if ".root" not in line : continue
        acceptFile=True
        fields=line.split()
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile :
            fileList.append(xrootdRedirector+location+"/"+fileName)
            sizes.append(size)
    print fileList
    return fileList
#####################################
def fileListFromDisk(location, isDirectory = True, itemsToSkip = [], sizeThreshold = 0) :
    fileList=[]
    cmd="ls -l "+location
    #print cmd
    output = getCommandOutput(cmd)["stdout"]
    for line in output.split("\n") :
        acceptFile=True
        fields=line.split()
        if len(fields)<6 : continue
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile : fileList.append(fileName if not isDirectory else location+"/"+fileName)

    return fileList
#####################################
def fileListFromTextFile(fileName = None) :
    f = open(fileName)
    out = [line.replace("\n","") for line in f]
    f.close()
    return out
#####################################
def printSkimResults(org) :
    for iSkimmer,skimmer in filter(lambda tup: tup[1].name=="skimmer", enumerate(org.steps) ) :
        print org.tag
        print "efficiencies for skimmer with index",iSkimmer
        print "-"*40
        names = tuple([sample["name"] for sample in org.samples])
        denom = tuple([failPass[1] for failPass in org.steps[0].rawFailPass])
        numer = tuple([failPass[1] for failPass in org.steps[iSkimmer].rawFailPass])
        effic = tuple([num/float(den) for num,den in zip(numer,denom)])
        lumis =  tuple([sample["lumi"] if "lumi" in sample else None for sample in org.samples])
        xss  =   tuple([sample["xs"] if "xs" in sample else None for sample in org.samples])

        assert all([lumi or xs for lumi,xs in zip(lumis,xss)]), "Failed to find either xs or lumi"

        nameStrings = ['foo.add("%s_skim", '%name for name in names]
        dirStrings = ['\'utils.fileListFromDisk(location = "%s/'+name+'_*_skim.root", isDirectory = False)\'%dir,' for name in names]
        effStrings = [(' lumi = %e)'%lumi if lumi else ' xs = %e * %e)'%(eff,xs)) for eff,lumi,xs in zip(effic,lumis,xss)]
        
        def maxLength(l) : return max([len(s) for s in l])
        nameLength = maxLength(nameStrings)
        dirLength  = maxLength(dirStrings)
        effLength  = maxLength(effStrings)
        for name,dir,eff in zip(nameStrings, dirStrings, effStrings) :
            print name.ljust(nameLength) + dir.ljust(dirLength) + eff.ljust(effLength)
        print
#####################################
