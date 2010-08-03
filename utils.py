import os,collections
import ROOT as r
#####################################
def goFunc(x) :
    x.go()
#####################################
def makeCodes(iTry,nOps,nItems) :
    codes=[0]*nItems
    for iItem in range(nItems) :
        code=iTry-iTry%(nOps**iItem)
        code/=(nOps**iItem)
        code=code%nOps
        codes[iItem]=code
    return codes
#####################################
def makeCodeString(iTry,nOps,nItems) :
    codeList=makeCodes(iTry,nOps,nItems)
    outString=""
    for code in codeList : outString+=str(code)
    return outString
#####################################
def psFromRoot(listOfInFileNames,outFileName,beQuiet) :
    if len(listOfInFileNames)==0 : return
    
    dummyCanvas=r.TCanvas("display","display",500,500)
    dummyCanvas.Print(outFileName+"[")
    for inFileName in listOfInFileNames :
        inFile=r.TFile(inFileName)
        keys=inFile.GetListOfKeys()
        for key in keys :
            someObject=inFile.Get(key.GetName())
            if someObject.ClassName()!="TCanvas" : print "Warning: found an object which is not a TCanvas in the display root file"
            someObject.Print(outFileName)
    dummyCanvas.Print(outFileName+"]")
    pdfFileName=outFileName.replace(".ps",".pdf")
    os.system("ps2pdf "+outFileName+" "+pdfFileName)
    os.system("gzip -f "+outFileName)
    if not beQuiet : print "The display file \""+pdfFileName+"\" has been written."    
#####################################
def mergeRunLsDicts(runLsDict,outFileName,hyphens,printHyphens=False) :
    if len(runLsDict)==0 : return

    #merge results into one dictionary
    mergedDict=collections.defaultdict(list)
    for item in runLsDict.values():
        for someDict in item :
            for run,lsList in someDict.iteritems() :
                mergedDict[run].extend(lsList)

    #make a json
    outDict={}
    for run,lsList in mergedDict.iteritems() :
        #check for duplicates            
        trimmedList=list(set(lsList))
        nDuplicates=len(lsList)-len(trimmedList)
        if nDuplicates!=0 :
            for ls in trimmedList :
                lsList.remove(ls)
            print "In run",run,", these lumi sections appear multiple times in the lumiTree:",lsList
        trimmedList.sort()

        #make the json
        newList=[]
        lowerBound=trimmedList[0]
        for iLs in range(len(trimmedList)-1) :
            thisLs=trimmedList[iLs  ]
            nextLs=trimmedList[iLs+1]
            if nextLs!=thisLs+1 :
                newList.append([lowerBound,thisLs])
                lowerBound=nextLs
            if iLs==len(trimmedList)-2 :
                newList.append([lowerBound,nextLs])
        outDict[str(run)]=newList

    outFile=open(outFileName,"w")
    outFile.write(str(outDict).replace("'",'"'))
    outFile.close()
    print "The json file",outFileName,"has been written."
    if printHyphens : print hyphens
#####################################        
def getCommandOutput2(command):
    child = os.popen(command)
    data = child.read()
    err = child.close()
    #if err: raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data
#####################################
def pruneCrabDuplicates(inList,sizes) :
    import re
    from collections import defaultdict
    # CRAB old : filepathWithName_JOB_ATTEMPT.root
    # CRAB new : filepathWithName_JOB_ATTEMPT_RANDOMSTRING.root
    pattern  =  r"(_\d+_)(\d+)(_?\w*)(\.root$)"
    recombine = "%s%s%d%s.root"

    versionDict = defaultdict(list)
    for inFile,size in zip(inList,sizes) :
        fields = re.split(pattern,inFile)
        versionDict[ (fields[0],fields[1]) ].append( (int(fields[2]), size, fields[3]) )

    resolved = 0
    abandoned = 0
    outList = []
    for key,val in versionDict.iteritems() :
        front,job = key
        attempt,size,rnd = max(val)
        maxSize = max([v[1] for v in val])

        if size == maxSize :
            fileName = recombine % (front,job,attempt,rnd)
            outList.append(fileName)
            if len(val) > 1 : resolved += 1
        else: abandoned += 1

    if abandoned>0 or resolved>0 :
        print "Unresolved files duplications: %d" % abandoned
        print "Resolved file duplications (pruned): %d" % resolved
    return outList
#####################################
def fileListFromSrmLs(location,itemsToSkip=[],sizeThreshold=0,pruneList=True) :
    srmPrefix="srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN="
    dCachePrefix="dcap://gfe02.grid.hep.ph.ic.ac.uk:22128"

    fileList=[]
    sizes=[]
    cmd="srmls "+srmPrefix+"/"+location+" 2>&1 | grep -v JAVA_OPTIONS"
    #print cmd
    output=getCommandOutput2(cmd)
    for line in output.split("\n") :
        if ".root" not in line : continue
        acceptFile=True
        fields=line.split()
        size=float(fields[0])
        fileName=fields[1]
        
        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile :
            fileList.append(dCachePrefix+fileName)
            sizes.append(size)

    if pruneList :   fileList=pruneCrabDuplicates(fileList,sizes)
    return fileList
#####################################    
def fileListFromCastor(location,itemsToSkip=[],sizeThreshold=0,pruneList=True) :
    fileList=[]
    cmd="nsls -l "+location
    #print cmd
    output=getCommandOutput2(cmd)
    for line in output.split("\n") :
        if ".root" not in line : continue
        acceptFile=True
        fields=line.split()
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile : fileList.append("rfio:///"+location+"/"+fileName)
            
    if pruneList :   fileList=pruneCrabDuplicates(fileList,size)
    return fileList
#####################################
def fileListFromDisk(location,itemsToSkip=[],sizeThreshold=0) :
    fileList=[]
    cmd="ls -l "+location
    #print cmd
    output=getCommandOutput2(cmd)
    for line in output.split("\n") :
        acceptFile=True
        fields=line.split()
        if len(fields)<6 : continue
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile : fileList.append(location+"/"+fileName)
            
    return fileList
#####################################        
