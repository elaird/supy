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
def pruneCrabDuplicates(inList, sizes, alwaysUseLastAttempt = False) :
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

        if size == maxSize or alwaysUseLastAttempt :
            fileName = recombine % (front,job,attempt,rnd)
            outList.append(fileName)
            if len(val) > 1 : resolved += 1
        else: abandoned += 1

    if abandoned>0 or resolved>0 :
        print "File duplications, unresolved(%d), resolved(%d)" % (abandoned,resolved)
    return outList
#####################################
def fileListFromSrmLs(location, itemsToSkip = [], sizeThreshold = 0, pruneList = True, alwaysUseLastAttempt = False) :
    srmPrefix="srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN="
    dCachePrefix="dcap://gfe02.grid.hep.ph.ic.ac.uk:22128"

    fileList=[]
    sizes=[]
    offset = 0
    output = []
    #print cmd
    while len(output) >= 1000*offset :
        cmd="srmls --count 1000 --offset %d %s/%s 2>&1 | grep -v JAVA_OPTIONS"% (1000*offset,srmPrefix,location)
        output += getCommandOutput2(cmd).split('\n')
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
            fileList.append(dCachePrefix+fileName)
            sizes.append(size)

    if pruneList :   fileList=pruneCrabDuplicates(fileList, sizes, alwaysUseLastAttempt)
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
def fileListFromDisk(location, isDirectory = True, itemsToSkip = [], sizeThreshold = 0) :
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
        if acceptFile : fileList.append(fileName if not isDirectory else location+"/"+fileName)

    return fileList
#####################################        
class rBin(object) :
    def __init__(self,num,den,i, minRelUnc=0.25) :
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
            while self.next and not self.ok() :
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
    den.GetDirectory().cd()
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
            if not precision :
                display_val*=10
                dsp_digit-=1
            precision-=1
    return returnVal
#####################################
def printSkimResults(org) :
    def indicesFromName(name) :
        out = []
        for i,selection in enumerate(org.selections) :
            if selection.name == name : out.append(i)
        return out

    def numDict(index) :
        out = {}
        for sample,failPass in zip(org.samples, org.selections[index].rawFailPass) :
            key = sample["name"]
            out[key] = {}
            if failPass!=None :
                out[key]["fail"] = failPass[0]
                out[key]["pass"] = failPass[1]
            else :
                out[key]["fail"] = 0.0
                out[key]["pass"] = 0.0
        return out

    def aDict(var) :
        out = {}
        for sample in org.samples :
            if var in sample : out[sample["name"]] = sample[var]
        return out
        
    def maxLength(l) : return max([len(s) for s in l])
    
    nEventsIn = numDict(0)
    nameStrings = []
    dirStrings  = []
    effStrings  = []
    for index in indicesFromName("skimmer") :
        print "efficiencies for skimmer with index",index
        print "-"*40
        d = numDict(index)
        for name in sorted(nEventsIn.keys()) :
            eff = 0.0
            denom = nEventsIn[name]["pass"]
            if denom > 0.0 : eff = d[name]["pass"] / denom

            #format output
            nameStrings.append( 'foo.add("%s_skim", '%name )
            dirStrings.append( '\'utils.fileListFromDisk(location = "%s/'+name+'_*_skim.root", isDirectory = False)\'%dir,')
            if name in aDict("xs") : 
                effStrings.append( 'xs = %e * %e)'%(eff,aDict("xs")[name]) )
            elif name in aDict("lumi") :
                effStrings.append( 'lumi = %e)'%aDict("lumi")[name] )
            else :
                assert False,"failed to find either xs or lumi"
        nameLength = maxLength(nameStrings)
        dirLength  = maxLength(dirStrings)
        effLength  = maxLength(effStrings)
        for name,dir,eff in zip(nameStrings, dirStrings, effStrings) :
            print name.ljust(nameLength) + dir.ljust(dirLength) + eff.ljust(effLength)
        print
#####################################
def phiOrder(p4s, indices) :
    if not indices : return indices
    mp4 = reduce(lambda x,i: x-p4s.at(i), indices, r.LorentzV())
    iPhi = collections.deque(sorted(indices, key = lambda i: p4s.at(i).phi()))
    dphi = [r.Math.VectorUtil.DeltaPhi(mp4,p4s.at(i)) for i in iPhi]
    dphiP = [dp if dp>0 else 2*math.pi + dp for dp in dphi]
    rotation = -dphiP.index(min(dphiP))
    iPhi.rotate(rotation)
    return iPhi
#####################################
def partialSumP4(p4s, indices) :
    partial = [r.LorentzV()]
    for i in indices:
        partial.append(partial[-1]+p4s[i])
    return partial
#####################################
# Area and Centroid of polygon
# http://en.wikipedia.org/wiki/Polygon
def partialSumP4Area(partials) :
    p = partials + partials[:1]
    return 0.5 * sum([ p[i].x()*p[i+1].y() - p[i+1].x()*p[i].y() for i in range(len(partials))])
def partialSumP4Centroid(partials) :
    A = partialSumP4Area(partials)
    p = partials + partials[:1]
    oneOverSixA = 1./(6*A)
    Cx = oneOverSixA * sum([ (p[i].x()+p[i+1].x())*(p[i].x()*p[i+1].y() - p[i+1].x()*p[i].y()) for i in range(len(partials))])
    Cy = oneOverSixA * sum([ (p[i].y()+p[i+1].y())*(p[i].x()*p[i+1].y() - p[i+1].x()*p[i].y()) for i in range(len(partials))])
    return r.LorentzV(Cx,Cy,0,0)
#####################################
def dependence(TH2, name="", minimum=1.0/4, maximum=4) :
    if not TH2: return None
    TH2.GetDirectory().cd()
    dep = TH2.Clone(name if name else TH2.GetName()+"_dependence")
    dep.GetZaxis().SetTitle("dependence")
    norm = TH2.Integral()
    projX = TH2.ProjectionX()
    projY = TH2.ProjectionY()
    for iX in range(1,TH2.GetNbinsX()+1) :
        for iY in range(1,TH2.GetNbinsY()+1) :
            X = projX.GetBinContent(iX)
            Y = projY.GetBinContent(iY)
            bin = TH2.GetBin(iX,iY)
            XY = TH2.GetBinContent(bin)
            dep.SetBinContent(bin, min(maximum,max(minimum,norm*XY/X/Y)) if XY else 0)
            dep.SetBinError(bin,0) 
    dep.SetMinimum(minimum)
    dep.SetMaximum(maximum)
    
    return dep
#####################################
