import ROOT as r
import collections
##############################
def keyLister(sampleName,subDir,ranks,dimensions,histoDicts) :
    keys=subDir.GetListOfKeys()
    for iKey in range(len(keys)) :
        plotName=keys[iKey].GetName()
        obj=subDir.Get(plotName)
        className=obj.ClassName()

        if className[0:2]=="TH" :
            item=subDir.Get(plotName).Clone(plotName+"_"+sampleName)
            item.SetDirectory(0)
            ranks[plotName].append(iKey)
            dimensions[plotName]=int(className[2])
            histoDicts[plotName][sampleName]=item
        elif className=="TDirectoryFile" :
            keyLister(sampleName,obj,ranks,dimensions,histoDicts)
##############################
def scaleHistos(listOfPlotContainers,xsDict,nEventsDict,nJobsDict,scaleByAreaRatherThanByXs,lumiValue) :
    if scaleByAreaRatherThanByXs :
        raise Exception("scaling by area is not yet supported")
    
    for container in listOfPlotContainers :
        #special cases here
        if "xsHisto" in container["plotName"] or "lumiHisto" in container["plotName"] :
            for sampleName,histo in container["histoDict"].iteritems() :
                histo.Scale(1.0/nJobsDict[sampleName])
            continue
        if "nEventsHisto" in container["plotName"] : continue
        if "nJobsHisto"   in container["plotName"] : continue

        #"normal" cases here
        for sampleName,histo in container["histoDict"].iteritems() :
            xs=xsDict[sampleName]
            nEventsIn=nEventsDict[sampleName]
            if xs>0.0 and nEventsIn>0 :
                histo.Scale(lumiValue*xs/nEventsIn)
            if container["dimension"]==1 :
                newTitle=histo.GetYaxis().GetTitle()+" / "+str(lumiValue)+" pb^{-1}"
                histo.GetYaxis().SetTitle(newTitle)
            if container["dimension"]==2 :
                newTitle=histo.GetZaxis().GetTitle()+" / "+str(lumiValue)+" pb^{-1}"
                histo.GetZaxis().SetTitle(newTitle)
##############################
def mergeHistograms(listOfPlotContainers,histogramMergeRequests,histogramMergeKeepSources) :
    for container in listOfPlotContainers :
        listOfSourcesToBeRemoved=[]
        for mergeRequest,keepSources in zip(histogramMergeRequests,histogramMergeKeepSources) :

            #make a dict for the new histos, keyed by target
            newHistos={}
            for target in mergeRequest.values() : newHistos[target]=None

            #keep track of which sources we've merged (keyed by target)
            sourcesMerged=collections.defaultdict(list)

            #do this merge into the new histo(s)
            for source,target in mergeRequest.iteritems() :
                #don't clobber something that exists already
                if target in container["histoDict"].keys() : raise Exception("target",target,"is already in this container's histoDict")

                for sampleName,histo in container["histoDict"].iteritems() :
                    if source==sampleName :
                        if len(sourcesMerged[target])==0 :
                            newName=histo.GetName().replace(source,target)
                            newHistos[target]=histo.Clone(newName)
                            #print "NEW",container["plotName"],": merging",source,"into",target
                        else :
                            newHistos[target].Add(histo)
                            #print "   ",container["plotName"],": merging",source,"into",target                            
                        sourcesMerged[target].append(source)
                        #print sourcesMerged

            #mark for removal if requested
            if not keepSources :
                for sourceList in sourcesMerged.values() :
                    for source in sourceList :
                        listOfSourcesToBeRemoved.append(source)

            #transfer the merged histograms into the container
            for target in newHistos :
                if newHistos[target]==None : continue
                container["histoDict"][target]=newHistos[target]

        #remove sources if requested (after all mergeRequests)
        for source in set(listOfSourcesToBeRemoved) :
            del container["histoDict"][source]
##############################
class histogramOrganizer(object) :
    def __init__(self,
                 sampleSpecs = {},
                 scaleHistograms = False,
                 scaleByAreaRatherThanByXs = False,
                 multipleDisjointDataSamples = False,
                 lumiToUseInAbsenceOfData=100,#/pb
                 ) :

        for arg in ["sampleSpecs","scaleHistograms","scaleByAreaRatherThanByXs",
                    "multipleDisjointDataSamples","lumiToUseInAbsenceOfData" ] :
            setattr(self,arg,eval(arg))

        self.listOfMergeRequests=[]
        self.listOfMergeKeepSources=[]

        self.buildColorAndStyleDicts()

    def collectNamesAndDimensions(self) :
        ranks       = collections.defaultdict(list) #list of ranks in the files
        dimensions  = collections.defaultdict(int)  #plot dimension
        histoDicts  = collections.defaultdict(dict) #dict mapping sampleName to histo

        for theDict in self.sampleSpecs :
            f=r.TFile(theDict["outputPlotFileName"])
            keyLister(theDict["sampleName"],f,ranks,dimensions,histoDicts)
            
        listOfPlotTuples=[]
        for plotName in ranks.keys() :
            #compute the average rank
            avgRank=0.0
            nFiles=len(ranks[plotName])
            for rank in ranks[plotName] :
                avgRank+=rank
            if nFiles>0 : avgRank/=nFiles
            #add to the list
            listOfPlotTuples.append( (nFiles,-avgRank,dimensions[plotName],plotName) )

        #sort by display order
        listOfPlotTuples.sort()
        listOfPlotTuples.reverse()

        self.listOfPlotContainers=[]
        for plotTuple in listOfPlotTuples :
            container={}
            container["histoDict"]={}
            container["plotName"]=plotTuple[3]
            container["dimension"]=plotTuple[2]
            for sampleName,histo in histoDicts[container["plotName"]].iteritems() :
                container["histoDict"][sampleName]=histo
            self.listOfPlotContainers.append(container)

    def collectXsLumiEtc(self) :
        self.xsDict={}
        self.lumiDict={}
        self.nEventsDict={}
        self.nJobsDict={}
        for theDict in self.sampleSpecs :
            f=r.TFile(theDict["outputPlotFileName"])
            nJobs=f.Get("nJobsHisto").GetBinContent(1)
            self.xsDict      [theDict["sampleName"]] = f.Get("xsHisto").GetBinContent(1) / nJobs
            self.lumiDict    [theDict["sampleName"]] = f.Get("lumiHisto").GetBinContent(1) /  nJobs
            self.nEventsDict [theDict["sampleName"]] = f.Get("nEventsHisto").GetBinContent(1)
            self.nJobsDict   [theDict["sampleName"]] = nJobs

    def determineLumiValue(self) :
        nDataSamples=len(self.lumiDict.values())-self.lumiDict.values().count(0.0)
        self.lumiValue=self.lumiToUseInAbsenceOfData
        if not nDataSamples :
            self.lumiValue = self.lumiToUseInAbsenceOfData
        elif nDataSamples==1 :
            self.lumiValue = max(self.lumiDict.values())
        elif multipleDisjointDataSamples :
            self.lumiValue = sum(self.lumiDict.values())
        else :
            raise Exception("at the moment, absolute normalization using multiple non-disjoint data samples is not supported")

    def buildColorAndStyleDicts(self) :
        self.colorDict={}
        self.markerStyleDict={}
        for someDict in self.sampleSpecs :
            self.colorDict      [someDict["sampleName"]] = someDict["color"]
            self.markerStyleDict[someDict["sampleName"]] = someDict["markerStyle"]

    def setColorsAndMarkerStyles(self) :
        for container in self.listOfPlotContainers :
            for sampleName,histo in container["histoDict"].iteritems() :
                histo.SetLineColor(  self.colorDict[sampleName])
                histo.SetMarkerColor(self.colorDict[sampleName])
                histo.SetMarkerStyle(self.markerStyleDict[sampleName])

    def mergeSamples(self,source = [], target = "", targetColor = 1, targetMarkerStyle = 1, keepSourceSamples = False) :
        outDict={}
        for item in source :
            outDict[item]=target
        self.listOfMergeRequests.append(outDict)
        self.listOfMergeKeepSources.append(keepSourceSamples)
        self.colorDict[target]=targetColor
        self.markerStyleDict[target]=targetMarkerStyle

    def organize(self) :
        #collection information
        self.collectNamesAndDimensions()

        #the keys for these dictionaries are sample names
        self.collectXsLumiEtc()

        #determine lumi value
        self.determineLumiValue()

        #scale the histograms
        if self.scaleHistograms :
            scaleHistos(self.listOfPlotContainers,self.xsDict,self.nEventsDict,self.nJobsDict,self.scaleByAreaRatherThanByXs,self.lumiValue)

        #merge the histograms
        mergeHistograms(self.listOfPlotContainers,self.listOfMergeRequests,self.listOfMergeKeepSources)

        #set the histograms' colors and styles
        self.setColorsAndMarkerStyles()

    def blob(self) :
        self.organize()
        return self.listOfPlotContainers
