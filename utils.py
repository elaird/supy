from multiprocessing import Process,JoinableQueue
import os,collections,array,math
import ROOT as r
#####################################
hyphens="-"*95
#####################################
def operateOnListUsingQueue(nCores,workerFunc,inList) :
    q = JoinableQueue()
    listOfProcesses=[]
    for i in range(nCores):
        p = Process(target = workerFunc, args = (q,))
        p.daemon = True
        p.start()
        listOfProcesses.append(p)
    map(q.put,inList)
    q.join()# block until all tasks are done
    #clean up
    for process in listOfProcesses :
        process.terminate()
#####################################
def goWorker(q):
    while True:
        item = q.get()
        item.go()
        q.task_done()
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
def mergeRunLsDicts(runLsDict,outFileName,printHyphens=False) :
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
            lsList.sort()
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
        print "File duplications, unresolved(%d), resolved(%d)" % (abandoned,resolved)
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
class rBin(object) :
    def __init__(self,num,den,i, minRelUnc=0.5) :
        self.lowEdge = num.GetBinLowEdge(i)
        self.num = num.GetBinContent(i)
        self.enum = num.GetBinError(i)
        self.den = den.GetBinContent(i)
        self.eden = den.GetBinError(i)
        self.next = None
        self.minRelUnc = minRelUnc
        return
        
    def ratio(self) :
        return self.num / self.den if self.den else 0
    
    def error(self) :
        return math.sqrt(self.enum**2 + self.ratio()**2 * self.eden**2) / self.den if self.den else 0
    
    def eatNext(self) :
        if not self.next: return 
        self.num += self.next.num
        self.den += self.next.den
        self.enum = math.sqrt(self.enum**2+self.next.enum**2)
        self.eden = math.sqrt(self.eden**2+self.next.eden**2)
        self.next = self.next.next
        return
        
    def ok(self) :
        return self.empty() or ( self.num!=0 and self.enum/self.num < self.minRelUnc and \
                                 self.den!=0 and self.eden/self.den < self.minRelUnc)
    
    def empty(self) :
        return self.num==0 and self.den==0
    
    def subsequentEmpty(self) :
        return  (not self.next) or self.next.empty() and self.next.subsequentEmpty()
    
    def eatMe(self,lastNonZeroOK=None) :
        if not lastNonZeroOK :
            while self.next and not self.ok():
                self.eatNext()
        if self.next and self.next.eatMe( self if self.ok() and not self.empty() else lastNonZeroOK ) :
            self.eatNext()
        if (not self.ok()) and \
           (not self.subsequentEmpty()) and \
           (self.nextNonZeroOKlowEdge() - self.lowEdge < \
            self.lowEdge - lastNonZeroOK.lowEdge ) :
            while not self.ok() :
                self.eatNext()
        return not self.ok()
    
    def nextNonZeroOKlowEdge(self) :
        if self.next.ok() and not self.next.empty() :
            return self.next.lowEdge
        return self.next.nextNonZeroOKlowEdge()
#####################################
def ratioHistogram(num,den) :
    bins = [ rBin(num,den,i+1) for i in range(num.GetNbinsX()) ]
    for i in range(len(bins)-1) : bins[i].next = bins[i+1]
    b = bins[0]
    b.eatMe()
    bins = [b]
    while(b.next) :
        bins.append(b.next)
        b=b.next
        
    lowEdges = [b.lowEdge for b in bins] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(lowEdges)-1, array.array('d',lowEdges))
    
    for i,bin in enumerate(bins) :
        ratio.SetBinContent(i+1,bin.ratio())
        ratio.SetBinError(i+1,bin.error())
        
    return ratio
#####################################
def roundString(val,err,width=None) :
    err_digit = int(math.floor(math.log(abs(err))/math.log(10))) if err else 0
    val_digit = int(math.floor(math.log(abs(val))/math.log(10))) if val else 0
    dsp_digit = max(err_digit,val_digit)
    sci = val_digit<-1 or err_digit>0

    precision = val_digit-err_digit if sci else -err_digit

    display_val = val/pow(10.,dsp_digit) if sci else val
    display_err = str(int(round(err/pow(10,err_digit))))

    while True:
        display_sci = ("e%+d"%dsp_digit) if sci else ""
        returnVal = "%.*f(%s)%s"%(precision,display_val,display_err,display_sci)
        if (not width) or len(returnVal) <= width or precision < 1: break
        else:
            display_err = "-"
            precision-=1
            if not precision :
                display_val*=10
                dsp_digit-=1
    return returnVal
########################
