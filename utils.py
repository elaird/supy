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
def pruneFileList(inList) :
    #make a dictionary of file versions
    splitString="_"
    stripString=".root"
    versionDict={}
    cruftDict={}
    for inFile in inList :
        fieldList=inFile.replace(stripString,"").split(splitString)

        #determine which field is the file version (newer versions of CRAB use also a random string)
        versionIndex=-1
        cruftString=""
        try:
            int(fieldList[-1])
        except:
            versionIndex=-2
            cruftString="_"+fieldList[-1]

        key=tuple(fieldList[:versionIndex])
        value=int(fieldList[versionIndex])

        if key not in versionDict :
            versionDict[key]=[value]
            cruftDict[key]=[cruftString]
        else :
            print "duplicate found and removed:",key
            versionDict[key].append(value)
            cruftDict[key].append(cruftString)

    #select the highest-numbered version of each file
    outList=[]
    for key in versionDict :
        #print key,versionDict[key]
        fileName=splitString.join(key)

        maxVersion=max(versionDict[key])
        index=versionDict[key].index(maxVersion)
        cruftString=cruftDict[key][index]

        fileName+=splitString+str(maxVersion)+cruftString+stripString
        outList.append(fileName)
    return outList
#####################################
def fileListFromSrmLs(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
    srmPrefix="srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN="
    dCachePrefix="dcap://gfe02.grid.hep.ph.ic.ac.uk:22128"

    fileList=[]
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
        if acceptFile : fileList.append(dCachePrefix+fileName)

    if pruneList :   fileList=pruneFileList(fileList)
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
            
    if pruneList :   fileList=pruneFileList(fileList)
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
            
    if pruneList :   fileList=pruneFileList(fileList)
    if nMaxFiles>0 : fileList=fileList[:nMaxFiles]
    return fileList
#####################################        
