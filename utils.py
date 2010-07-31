import os
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

    print "Unresolved files duplications: %d" % abandoned
    print "Resolved file duplications (pruned): %d" % resolved
    return outList
#####################################
def fileListFromSrmLs(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
    srmPrefix="srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN="
    dCachePrefix="dcap://gfe02.grid.hep.ph.ic.ac.uk:22128"

    fileList=[]
    sizes=[]
    cmd="srmls "+srmPrefix+"/"+location
    #print cmd
    output=getCommandOutput2(cmd)
    for line in output.split("\n") :
        if "SusyCAF_Tree" not in line : continue
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
    if nMaxFiles>0 : fileList=fileList[:nMaxFiles]
    return fileList
#####################################    
def fileListFromCastor(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
    fileList=[]
    cmd="nsls -l "+location
    #print cmd
    output=getCommandOutput2(cmd)
    for line in output.split("\n") :
        if "SusyCAF_Tree" not in line : continue
        acceptFile=True
        fields=line.split()
        size=float(fields[-5])
        fileName=fields[-1]

        if size<=sizeThreshold : acceptFile=False
        for item in itemsToSkip :
            if item in fileName : acceptFile=False
        if acceptFile : fileList.append("rfio:///"+location+"/"+fileName)
            
    if pruneList :   fileList=pruneCrabDuplicates(fileList,size)
    if nMaxFiles>0 : fileList=fileList[:nMaxFiles]
    return fileList
#####################################
def fileListFromDisk(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
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
            
    if pruneList :   fileList=pruneCrabDuplicates(fileList,size)
    if nMaxFiles>0 : fileList=fileList[:nMaxFiles]
    return fileList
#####################################        
