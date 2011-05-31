import ROOT as r
import copy,re
import configuration,utils

class organizer(object) :
    """Organize selection and histograms.

    samples is a tuple of dicts, each of which describes a sample.
    selections is a tuple of named dicts, keyed with histogram names (see class 'selection')
    histograms of each sample remain in independent TDirectory structures.
    """
    class selection(dict) : 
        """Keys are histogram names, values are tuples of histograms, parallel to samples."""
        def __init__(self,samples,dirs,keys) :
            for key in keys: self[key] = tuple( map(lambda d: d.Get(key), dirs) )
            self.nameTitle  = ("","") if "/" in dirs[0].GetName() else (dirs[0].GetName(),dirs[0].GetTitle())
            self.name,self.title = self.nameTitle
            if "counts" not in self: self["counts"] = tuple([None]*len(dirs))
            self.rawFailPass = tuple(map(lambda h: (h.GetBinContent(1),h.GetBinContent(2)) if h else None, self["counts"]))

            for key in self :
                if key in ["nJobsHisto"] : continue
                elif key in ["lumiHisto","xsHisto"] :
                    map(  lambda hs: hs[0].Scale(  1.0  /hs[1]['nJobs']),       filter(lambda hs: hs[0],                   zip(self[key],samples)) )
                else: map(lambda hs: hs[0].Scale(hs[1]["xs"]/hs[1]['nEvents']), filter(lambda hs: hs[0] and hs[1]["nEvents"] and "xs" in hs[1], zip(self[key],samples)) )

        def yields(self) : return tuple(map(lambda h: (h.GetBinContent(2),h.GetBinError(2)) if h else None, self["counts"]))


    def __init__(self, sampleSpecs = [] , configurationId = 0 ) :
        self.configurationId = configurationId
        r.gROOT.cd()
        r.gDirectory.mkdir("config%d"%self.configurationId)
        self.samples = tuple([copy.deepcopy(spec) for spec in sampleSpecs]) # columns
        self.selections = tuple(self.__inititialSelectionsList())  # rows
        self.scaled = False
        self.lumi = 1.0
        self.alternateConfigurations = [] if configurationId else \
                                       [organizer(sampleSpecs,i) for i in range(1,len(sampleSpecs[0]["outputFileNames"]))]
        self.calculablesGraphs
            
    def __inititialSelectionsList(self) :
        """Scan samples in parallel to ensure consistency and build list of selection dicts"""
        selections = []

        for sample in self.samples :
            assert len(sample["outputFileNames"]) > self.configurationId, \
                   "You cannot request a configurationId >= than the number of outputFileNames in the sample."
            sample['file'] = r.TFile(sample["outputFileNames"][self.configurationId])
            sample['dir'] = sample['file'].Get("Master")
            def extract(histName,bin=1) :
                hist = sample['dir'].Get(histName)
                return hist.GetBinContent(bin) if hist and hist.GetEntries() else 0
            lumiNjobs,xsNjobs,sample['nJobs'] = map(extract, ["lumiHisto","xsHisto","nJobsHisto"])
            sample['nEvents'] = extract('counts',bin=2)
            nEventsRejected = extract('counts')

            if lumiNjobs: sample["lumi"] = lumiNjobs/sample['nJobs']
            if xsNjobs:
                sample["xs"] = (xsNjobs/sample['nJobs'])
                if (sample['nEvents']+nEventsRejected) : sample["xs"] *= (sample['nEvents']/(sample['nEvents']+nEventsRejected))
            assert ("xs" in sample)^("lumi" in sample), \
                   "Sample %s should have one and only one of {xs,lumi}."% sample["name"]
            
        dirs = [ s['dir'] for s in self.samples]
        while dirs[0] :
            keysets = [set(filter(lambda name: name!="Calculables",[key.GetName() for key in dir.GetListOfKeys()])) for dir in dirs]
            keys = reduce( lambda x,y: x|y ,keysets,set())

            subdirNames = map(lambda d,keys:  filter(lambda k: ( type(d.Get(k)) is r.TDirectoryFile), keys),  dirs,keysets)
            subdirLens = map(len,subdirNames)
            if sum(subdirLens) :
                keys.remove(subdirNames[0][0])
                subdirs = map(lambda d,names: d.Get(names[0]), dirs,subdirNames)
                assert subdirLens == [1]*len(dirs), \
                       "Organizer can only interpret a single subdirectory in any given directory.\n%s"%str(subdirNames)
                nameTitles = set(map(lambda sd: (sd.GetName(),sd.GetTitle()), subdirs))
                assert len(nameTitles)==1,"Subdirectory names,titles must be identical. %s"%str(nameTitles)
            else: subdirs = [None]*len(dirs)
            
            selections.append( self.selection(self.samples,dirs,keys) )
            dirs = subdirs

        return selections

    def indexOfSampleWithName(self,name) :
        someList = [sample["name"] for sample in self.samples]
        #assert name in someList,"organizer: sample %s not found"%name
        return someList.index(name) if name in someList else None

    def drop(self,sampleName) :
        index = self.indexOfSampleWithName(sampleName)
        if index is None :
            print "%s is not present: cannot drop"%sampleName
            return
        self.samples = self.samples[:index] + self.samples[index+1:]
        for selection in self.selections:
            for key,val in selection.iteritems():
                selection[key] = val[:index] + val[index+1:]

    def mergeSamples(self,sources = [], targetSpec = {}, keepSources = False, allWithPrefix = None) :
        for org in self.alternateConfigurations :
            org.mergeSamples(sources,targetSpec,keepSources,allWithPrefix)

        assert not self.scaled, "Merge must be called before calling scale."

        if not sources and allWithPrefix:
            sources = filter(lambda n: re.match(allWithPrefix,n), [s["name"] for s in self.samples])

        for src in sources:
            if not src in map(lambda s: s["name"], self.samples): print "You have requested to merge unspecified sample %s"%src
        sourceIndices = filter(lambda i: self.samples[i]["name"] in sources, range(len(self.samples)))
        if not len(sourceIndices) : print "None of the samples you want merged are specified, no action taken." ;return
        target = copy.deepcopy(targetSpec)
        target['sources'] = map(lambda i: self.samples[i]["name"], sourceIndices)
        target['nEvents'] = map(lambda i: self.samples[i]['nEvents'], sourceIndices)
        if all(["xs" in self.samples[i] for i in sourceIndices]) : 
            target["xsOfSources"] = [self.samples[i]["xs"] for i in sourceIndices ]
            target["xs"] = sum(target["xsOfSources"])
        elif all(["lumi" in self.samples[i] for i in sourceIndices]):
            target["lumiOfSources"] = [self.samples[i]["lumi"] for i in sourceIndices ]
            target["lumi"] = sum(target['lumiOfSources'])
        else: raise Exception("Cannot merge data with sim")
        
        def tuplePopInsert(orig, item) :
            val = list(orig)
            if not keepSources : [val.pop(i) for i in reversed(sourceIndices) ]
            val.insert(sourceIndices[0],item)
            return tuple(val)

        r.gROOT.cd()
        r.gDirectory.cd("config%d"%self.configurationId)
        dir = target["dir"] = r.gDirectory.mkdir(target["name"])
        for selection in self.selections :
            if selection.name is not "": dir = dir.mkdir(*selection.nameTitle)
            dir.cd()
            for key,val in selection.iteritems():
                sources = filter(None, map(val.__getitem__,sourceIndices))
                hist = sources[0].Clone(key) if len(sources) else None
                for h in sources[1:]: hist.Add(h)
                selection[key] = tuplePopInsert( val, hist )
            selection.rawFailPass = tuplePopInsert( selection.rawFailPass, None )
        self.samples = tuplePopInsert( self.samples, target )
        return

    def scale(self, lumiToUseInAbsenceOfData = None, toPdf = False) :
        for org in self.alternateConfigurations :
            org.scale(lumiToUseInAbsenceOfData, toPdf)

        dataIndices = filter(lambda i: "lumi" in self.samples[i], range(len(self.samples))) if not toPdf else []
        assert len(dataIndices)<2, \
               "What should I do with more than one data sample?"
        iData = dataIndices[0] if len(dataIndices) else None
        self.lumi = self.samples[iData]["lumi"] if iData!=None else 0.0 if toPdf else lumiToUseInAbsenceOfData
        assert self.lumi or toPdf, \
               "You need to have a data sample or specify the lumi to use."
        if type(self.lumi) is list : self.lumi = sum(self.lumi)

        for sel in self.selections :
            for key,hists in sel.iteritems() :
                if key in ["lumiHisto","xsHisto","nJobsHisto","nEventsHisto"] : continue
                for i,h in enumerate(hists):
                    if not h: continue
                    if toPdf : h.Scale(1/h.Integral("width") if h.Integral() else 1.0)
                    elif i!=iData : h.Scale(self.lumi)
                    dim = int(h.ClassName()[2])
                    axis = h.GetYaxis() if dim==1 else h.GetZaxis() if dim==2 else None
                    if axis: axis.SetTitle("p.d.f." if toPdf else "%s / %s pb^{-1}"%(axis.GetTitle(),str(self.lumi)))
        self.scaled = True

    def indicesOfSelectionsWithKey(self,key) :
        return filter( lambda i: key in self.selections[i], range(len(self.selections)))

    def keysMatching(self,inKeys) :
        return filter(lambda k: any([i in k for i in inKeys]), set(sum([sel.keys() for sel in self.selections],[])))

    @property
    def calculables(self) :
        if not hasattr(self,"__calculables") :
            def nodes(file, dirName) :
                dir = file.Get(dirName)
                def category(title) :
                    return ("fltr" if dirName=="Master" else
                            "leaf" if dirName=="Leaves" else 
                            "fake" if title.count(configuration.fakeString()) else 
                            "calc" )
                def keyNames(path,descend=False) :
                    dirs = filter(lambda name: type(file.Get(path+name)) is r.TDirectoryFile and name!="Calculables", [k.GetName() for k in file.Get(path[:-1]).GetListOfKeys()])
                    return [path+dir for dir in dirs] + (sum([keyNames(path+dir+"/",descend) for dir in dirs],[]) if dirs and descend else [])

                calcDirs = [file.Get(name) for name in keyNames(dirName+'/',descend=(dirName=="Master"))]
                return [(calcDir.GetName(),
                         calcDir.GetTitle().replace(calcDir.GetName(),""),
                         category(calcDir.GetTitle()),
                         frozenset([tkey.GetName() for tkey in (
                    (calcDir.GetListOfKeys() if dirName!="Master" else calcDir.Get("Calculables").GetListOfKeys() if calcDir.Get("Calculables") else []))])
                         )  for calcDir in calcDirs]
            
            def calcs(sample) :
                return ( nodes(sample['file'], "Calculables") +
                         nodes(sample['file'], "Leaves") +
                         filter(lambda c: c[3], nodes(sample['file'], "Master"))
                         )
            
            samplesCalcs = [dict([(c[:3],c[3]) for c in calcs(sample)]) for sample in self.samples]
            allCalcs = reduce( lambda x,y: x|y, [set(s.keys()) for s in samplesCalcs])

            for calc in allCalcs :
                for scalcs in samplesCalcs :
                    if calc not in scalcs :
                        scalcs[(calc[0],calc[1],"absent")] = frozenset()
            setattr(self,"__calculables", samplesCalcs)
        return getattr(self,"__calculables")

    @property
    def calculablesGraphs(self) :
        if not hasattr(self,"__calculablesGraphs") :
            def graph(scalcs) :
                calcs = filter(lambda c: c[2]!="absent", scalcs)
                calcByName = dict([(c[0],c) for c in calcs])
                nodes = {}
                def addNode(calc) :
                    if calc in nodes : return
                    nodes[calc] = utils.vessel()
                    nodes[calc].deps = set([calcByName[depName] for depName in scalcs[calc]])
                    nodes[calc].feeds = set()
                    for dep in nodes[calc].deps :
                        addNode(dep)
                        nodes[dep].feeds.add(calc)
                    nodes[calc].depLevel = 0 if not nodes[calc].deps else 1+max([nodes[dep].depLevel for dep in nodes[calc].deps])
                for calc in calcs : addNode(calc)
                return nodes
            setattr(self,"__calculablesGraphs",[graph(scalcs) for scalcs in self.calculables])
        return getattr(self,"__calculablesGraphs")

    @property
    def mergedGraph(self) :
        if not hasattr(self,"__mergedGraph") :
            nodes = {}
            for snodes in self.calculablesGraphs :
                for node in snodes:
                    if node not in nodes : nodes[node] = snodes[node]
                    else :
                        nodes[node].deps |= snodes[node].deps
                        nodes[node].feeds|= snodes[node].feeds
            setattr(self,"__mergedGraph",nodes)
        return getattr(self,"__mergedGraph")
        
    def formattedCalculablesGraph(self) :

        def leafStrip(moreName) :
            for rep in [("ROOT",""),("::Math::",""),("<PtEtaPhiM4D<float> >",""),(r",.*allocator<.*> >",">"),("unsigned int","unsigned")] :
                moreName = re.sub(rep[0],rep[1],moreName)
            return moreName.lstrip(".")

        def writeNow(dep) : return len(nodes[dep].feeds)==1 or not nodes[dep].deps

        def write(calc,indent="", filterWritten = True) :
            if filterWritten and calc in written : return
            written.add(calc)
            if not indent : lines.append(("","","") )
            lines.append( (indent, "(%s) %s"%(calc[2].upper()[0], calc[0]), leafStrip(calc[1])) )
            for dep in sorted(nodes[calc].deps, key = lambda dep: (dep[2]!='leaf', writeNow(dep), nodes[dep].depLevel,len(dep[0]),dep)) :
                if writeNow(dep) : write(dep,indent+tab, filterWritten=False)
                else : lines.append( (indent+tab, "|%d| %s"%(nodes[dep].depLevel,dep[0]), dep[1] ) )
            return
 
        nodes = self.mergedGraph
        written = set()
        lines = []
        tab = 3*" "
        ordered = (filter(lambda calc: len(nodes[calc].feeds)>1 and nodes[calc].depLevel, sorted(nodes.keys(), key = lambda calc: (nodes[calc].depLevel,len(nodes[calc].feeds),calc))) +
                   filter(lambda calc: len(nodes[calc].feeds)<1 and nodes[calc].depLevel, sorted(nodes.keys(), key = lambda calc: (-nodes[calc].depLevel,len(nodes[calc].deps),calc))) +
                   filter(lambda calc: len(nodes[calc].feeds)==1 or not nodes[calc].depLevel, nodes.keys())
                   )
        for calc in ordered : write(calc)
        return lines

    def printFormattedCalculablesGraph(self) :
        for block in filter(None,utils.splitList(self.formattedCalculablesGraph(), ("","","") )) :
            print
            maxLenName = max([len(line[1]) for line in block])
            for line in block : print "%s%s  %s"%(line[0],line[1].ljust(maxLenName),line[2])
