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
def getNamesAndDimensions(plotFileNameDict) :
    ranks       = collections.defaultdict(list) #list of ranks in the files
    dimensions  = collections.defaultdict(int)  #plot dimension
    histoDicts  = collections.defaultdict(dict) #dict mapping sampleName to histo
    
    for sampleName,theDict in plotFileNameDict.iteritems() :
        f=r.TFile(theDict["outputPlotFileName"])
        keyLister(sampleName,f,ranks,dimensions,histoDicts)
            
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

    listOfPlotContainers=[]
    for plotTuple in listOfPlotTuples :
        container={}
        container["histoDict"]={}
        container["plotName"]=plotTuple[3]
        container["dimension"]=plotTuple[2]
        for sampleName,histo in histoDicts[container["plotName"]].iteritems() :
            container["histoDict"][sampleName]=histo
        listOfPlotContainers.append(container)
    return listOfPlotContainers
##############################
def getXsLumiNeventJobNumbers(plotFileNameDict) :
    xsDict={}
    lumiDict={}
    nEventsDict={}
    nJobsDict={}
    for sampleName,theDict in plotFileNameDict.iteritems() :
        f=r.TFile(theDict["outputPlotFileName"])
        nJobs=f.Get("nJobsHisto").GetBinContent(1)
        xsDict      [sampleName] = f.Get("xsHisto").GetBinContent(1) / nJobs
        lumiDict    [sampleName] = f.Get("lumiHisto").GetBinContent(1) /  nJobs
        nEventsDict [sampleName] = f.Get("nEventsHisto").GetBinContent(1)
        nJobsDict   [sampleName] = nJobs
    return [xsDict,lumiDict,nEventsDict,nJobsDict]
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
def setColorsAndMarkerStyles(plotFileNamesDict,listOfPlotContainers,targetColorDict,targetMarkerStyleDict) :
    for container in listOfPlotContainers :
        for sampleName,histo in container["histoDict"].iteritems() :
            if "color" in plotFileNamesDict[sampleName] :
                histo.SetLineColor(plotFileNamesDict[sampleName]["color"])
                histo.SetMarkerColor(plotFileNamesDict[sampleName]["color"])
            if "markerStyle" in plotFileNamesDict[sampleName] :
                histo.SetMarkerStyle(plotFileNamesDict[sampleName]["markerStyle"])
            else :
                histo.SetLineColor(  targetColorDict[sampleName])
                histo.SetMarkerColor(targetColorDict[sampleName])
                histo.SetMarkerStyle(targetMarkerStyleDict[sampleName])
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
def go(plotFileNamesDict={},
       scaleHistograms=True,
       scaleByAreaRatherThanByXs=False,
       multipleDisjointDataSamples=False,
       lumiToUseInAbsenceOfData=100,#/pb
       histogramMergeRequests=[],
       histogramMergeKeepSources=[],
       targetColorDict={},
       targetMarkerStyleDict={}
       ) :

    #collection information
    listOfPlotContainers=getNamesAndDimensions(plotFileNamesDict)

    #the keys for these dictionaries are sample names
    xsDict,lumiDict,nEventsDict,nJobsDict=getXsLumiNeventJobNumbers(plotFileNamesDict)

    #get lumi value
    nDataSamples=len(lumiDict.values())-lumiDict.values().count(0.0)
    lumiValue=lumiToUseInAbsenceOfData
    if not nDataSamples :
        lumiValue = lumiToUseInAbsenceOfData
    elif nDataSamples==1 :
        lumiValue = max(lumiDict.values())
    elif multipleDisjointDataSamples :
        lumiValue = sum(lumiDict.values())
    else :
        raise Exception("at the moment, absolute normalization using multiple non-disjoint data samples is not supported")

    #scale the histograms
    if scaleHistograms :
        scaleHistos(listOfPlotContainers,xsDict,nEventsDict,nJobsDict,scaleByAreaRatherThanByXs,lumiValue)

    #merge the histograms
    mergeHistograms(listOfPlotContainers,histogramMergeRequests,histogramMergeKeepSources)

    #set the histograms' colors and styles
    setColorsAndMarkerStyles(plotFileNamesDict,listOfPlotContainers,targetColorDict,targetMarkerStyleDict)
    
    return listOfPlotContainers
