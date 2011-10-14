import ROOT as r
import copy,re
import configuration,utils

class organizer(object) :
    """Organize step and histograms.

    samples is a tuple of dicts, each of which describes a sample.
    steps is a tuple of named dicts, keyed with histogram names (see class 'step')
    histograms of each sample remain in independent TDirectory structures.
    """
    class step(dict) : 
        """Keys are histogram names, values are tuples of histograms, parallel to samples."""
        def __init__(self,samples,dirs = None,keys = []) :
            if not dirs : dirs = [s['dir'] for s in samples]
            self.N = len(dirs)
            for key in keys: self[key] = tuple( map(lambda d: d.Get(key), dirs) )
            self.nameTitle = (dirs[0].GetName(),dirs[0].GetTitle()) if dirs else ("","")
            self.name,self.title = self.nameTitle
            self.rawFailPass = tuple(map(lambda h: (h.GetBinContent(1),h.GetBinContent(2)) if h else None, self["counts"] if "counts" in self else self.N*[None]))

            for key in self :
                if key in ["nJobsHisto"] : continue
                elif key in ["lumiHisto","xsHisto","xsPostWeightsHisto"] :
                    [ hist.Scale(  1.0 / sample['nJobs'] ) for hist,sample in zip(self[key],samples) if hist ]
                else: [ hist.Scale(sample["xs"]/sample['nEvents']) for hist,sample in zip(self[key],samples)
                        if hist and sample['nEvents'] and "xs" in sample ]

        @property
        def yields(self) : return ( tuple([(h.GetBinContent(2),h.GetBinError(2)) if h else None for h in self["counts"] ]) \
                                    if "counts" in self else tuple(self.N*[None]) )
        @property
        def isSelector(self) : return "counts" in self

        @classmethod
        def melded(cls, nameTitle, sizes, steps = [] ) :
            blanks = [tuple(size*[None]) for size in sizes]
            instance = cls(sum(sizes)*[{"dir":r.gDirectory}])
            instance.clear()
            instance.nameTitle = nameTitle
            instance.name,instance.title = nameTitle
            instance.rawFailPass = sum([s.rawFailPass if s else blank for s,blank in zip(steps,blanks)],())
            for key in set(sum([s.keys() for s in filter(None,steps)],[])) :
                instance[key] = sum([s[key] if s and key in s else blank for s,blank in zip(steps,blanks)],())
            return instance
        
    def __init__(self, tag, sampleSpecs = [], verbose = False ) :
        r.gROOT.cd()
        self.verbose = verbose
        self.scaled = False
        self.lumi = 1.0
        self.tag = tag
        self.samples = tuple(copy.deepcopy(sampleSpecs)) # columns
        self.steps # rows
        self.calculablesGraphs

    def __deepcopy__(self, memo) :
        new = copy.copy(self)
        new.samples = copy.copy(self.samples)
        new.__steps = copy.deepcopy(self.__steps, memo)
        return new

    @classmethod
    def meld(cls, tagprefix = "melded", organizers = []) :
        ordering = utils.topologicalSort([tuple(org.tag.split("_")) for org in organizers])            
        subTags = filter(lambda st: all(org.tag.split('_').count(st)==1 for org in organizers), ordering)
        for org in organizers : org.tag = '_'.join(filter(lambda st: st not in subTags, org.tag.split('_')))
        tag = '_'.join([tagprefix]+sorted(subTags, key = lambda x:ordering.index(x)))

        if len(set(org.lumi for org in organizers if org.lumi))!=1 :
            print "Warning: melding organizers with distinct lumi values, using max."
            print [org.lumi for org in organizers if org.lumi]
        sizes = [len(org.samples) for org in organizers]
        
        instance = cls(tag)
        instance.scaled = any(org.scaled for org in organizers)
        instance.lumi = max(org.lumi for org in organizers)
        instance.samples = sum( tuple( tuple( dict(list(s.iteritems())+[("name",org.tag +'.'+ s["name"])]) for s in org.samples) for org in organizers),())
        
        shared = sorted( set.intersection(*tuple(set(s.nameTitle for s in org.steps if s.isSelector) for org in organizers)),
                         key = lambda s: next(next(iter(organizers)).indicesOfStep(*s)) )

        instance.__steps = [cls.step.melded((tagprefix,', '.join(org.tag for org in organizers)), sizes)]
        for start,stop in zip(shared,shared[1:]+[None]) :
            slices = [org.steps[next(org.indicesOfStep(*start)):
                                next(org.indicesOfStep(*stop)) if stop else None] for org in organizers]
            order = utils.topologicalSort([tuple(step.nameTitle for step in slice) for slice in slices])
            for step in order :
                steps = [next((s for s in slice if s.nameTitle==step),None) for slice in slices]
                instance.__steps.append( cls.step.melded(step, sizes, steps ) )
        instance.__steps.append( cls.step(instance.samples) )
        instance.__steps = tuple(instance.__steps)

        return instance
    
    @property
    def steps(self) :
        if hasattr(self,"_organizer__steps") : return self.__steps

        for sample in self.samples :
            sample['file'] = r.TFile(sample["outputFileName"])
            sample['dir'] = sample['file'].Get("Master")
            def extract(histName,bin=1) :
                hist = sample['dir'].Get(histName)
                return hist.GetBinContent(bin) if hist and hist.GetEntries() else 0
            lumiNjobs,xsPreNjobs,xsPostNjobs,sample['nJobs'] = map(extract, ["lumiHisto","xsHisto","xsPostWeightsHisto","nJobsHisto"])
            sample['nEvents'] = extract('counts',bin=2)
            nEventsTotal = sample['nEvents'] + extract('counts')
            xsNjobs = xsPostNjobs if xsPostNjobs else xsPreNjobs *( 1 if not nEventsTotal else sample['nEvents'] / nEventsTotal)

            if xsNjobs : sample["xs"] = xsNjobs / sample['nJobs']
            if lumiNjobs: sample["lumi"] = lumiNjobs / sample['nJobs']
            assert ("xs" in sample)^("lumi" in sample), "Error: Sample %s has both lumi and xs."% sample["name"]
            
        steps = []
        dirs = [ s['dir'] for s in self.samples]
        while any(dirs) :
            keysets = [ [key.GetName() for key in dir.GetListOfKeys() if key.GetName()!="Calculables"] for dir in dirs ]
            keys = set(sum(keysets,[]))
            subdirs = map(lambda d,keys: next((d.Get(k) for k in keys if type(d.Get(k)) is r.TDirectoryFile), None), dirs,keysets)
            if any(subdirs) : keys.remove(next(iter(subdirs)).GetName())
            steps.append( self.step(self.samples,dirs,keys) )
            dirs = subdirs
        self.__steps = tuple(steps + [self.step(self.samples)])
        return self.__steps

    def mergeSamples(self,sources = [], targetSpec = {}, keepSources = False, allWithPrefix = None) :
        assert not self.scaled, "Merge must be called before calling scale."

        if not sources and allWithPrefix: sources = [s["name"] for s in self.samples if re.match(allWithPrefix,s["name"])]
        sourceIndices = [i for i in range(len(self.samples)) if self.samples[i]["name"] in sources]
        sources = [s for s in self.samples if s["name"] in sources]
        if not len(sourceIndices) :
            if self.verbose : print "None of the samples you want merged are specified, no action taken : %s"%str(allWithPrefix)
            return
        elif self.verbose: print ''.join("You have requested to merge unspecified sample %s\n"%src["name"]
                                         for src in sources if src not in self.samples),

        target = copy.deepcopy(targetSpec)
        target['sources'] = [s["name"] for s in sources]
        target['nEvents'] = [s['nEvents'] for s in sources]
        if all(["xs" in s for s in sources]) : 
            target["xsOfSources"] = [s["xs"] for s in sources ]
            target["xs"] = sum(target["xsOfSources"])
        elif all(["lumi" in s for s in sources]):
            target["lumiOfSources"] = [s["lumi"] for s in sources ]
            target["lumi"] = sum(target['lumiOfSources'])
        else: raise Exception("Cannot merge data with sim")
        
        def tuplePopInsert(orig, item) :
            val = list(orig)
            if not keepSources : [val.pop(i) for i in reversed(sourceIndices) ]
            val.insert(sourceIndices[0],item)
            return tuple(val)

        r.gROOT.cd()
        r.gDirectory.mkdir(target["name"]).cd()
        target["dir"] = r.gDirectory
        for step in self.steps :
            r.gDirectory.mkdir(*step.nameTitle).cd()
            for key,val in step.iteritems():
                sources = filter(None, map(val.__getitem__,sourceIndices))
                hist = sources[0].Clone(key) if len(sources) else None
                for h in sources[1:]: hist.Add(h)
                step[key] = tuplePopInsert( val, hist )
            step.rawFailPass = tuplePopInsert( step.rawFailPass, None )
        self.samples = tuplePopInsert( self.samples, target )
        return

    def scale(self, lumiToUseInAbsenceOfData = None, toPdf = False) :
        dataIndices = [i for i,sample in enumerate(self.samples) if "lumi" in sample and not toPdf ]
        iData = next( iter(dataIndices), None)
        self.lumi = self.samples[iData]["lumi"] if iData!=None else 0.0 if toPdf else lumiToUseInAbsenceOfData
        if type(self.lumi) is list : self.lumi = sum(self.lumi)
        assert len(dataIndices)<2, "What should I do with more than one data sample?"
        assert self.lumi or toPdf, "You need to have a data sample or specify the lumi to use."

        for step in self.steps :
            for key,hists in step.iteritems() :
                if key in ["lumiHisto","xsHisto","xsPostWeightsHisto","nJobsHisto","nEventsHisto"] : continue
                for i,h in enumerate(hists):
                    if not h: continue
                    if toPdf :
                        integral = h.Integral(0,h.GetNbinsX()+1) if not issubclass(type(h),r.TH2) else h.Integral()
                        h.Scale(1./integral if integral else 1, "width")
                    elif i!=iData : h.Scale(self.lumi)
                    dim = int(h.ClassName()[2])
                    axis = h.GetYaxis() if dim==1 else h.GetZaxis() if dim==2 else None
                    if axis: axis.SetTitle("p.d.f." if toPdf else "%s / %s pb^{-1}"%(axis.GetTitle(),str(self.lumi)))
        self.scaled = True

    def drop(self,sampleName) :
        index = self.indexOfSampleWithName(sampleName)
        if index is None :
            if self.verbose : print "%s is not present: cannot drop"%sampleName
            return
        self.samples = self.samples[:index] + self.samples[index+1:]
        for step in self.steps:
            for key,val in list(step.iteritems()):
                step[key] = val[:index] + val[index+1:]
                if not any(step[key]) :
                    if self.verbose : print "%s is gone."%key
                    del step[key]

    def dropSteps(self, indices = [], allButIndices = []) :
        if not indices : indices = [i for i in range(len(self.steps)) if i not in allButIndices]
        self.__steps = tuple(s for i,s in enumerate(self.__steps) if i not in indices)

    def indexOfSampleWithName(self,name) :
        someList = [sample["name"] for sample in self.samples]
        return someList.index(name) if name in someList else None

    def indicesOfStepsWithKey(self,key) :
        for iStep,step in enumerate(self.steps) :
            if key in step : yield iStep

    def indicesOfStep(self,name,title=None) :
        for iStep,step in enumerate(self.steps) :
            if name==step.name and title in [step.title,None] : yield iStep

    def keysMatching(self,inKeys) :
        return filter(lambda k: any([i in k for i in inKeys]), set(sum([step.keys() for step in self.steps],[])))

    @property
    def calculables(self) :
        def nodes(file, dirName) :
            def category(title) :
                return ("sltr" if dirName=="Master" else
                        "leaf" if dirName=="Leaves" else 
                        "fake" if title.count(configuration.fakeString()) else 
                        "calc" )
            def parseCalc(cd) :
                if dirName=="Master" and not cd.Get("Calculables") : return None
                tkeys = (cd.Get("Calculables") if dirName=="Master" else cd).GetListOfKeys()
                deps = frozenset([ utils.justNameTitle(t) for t in tkeys])
                name,title = utils.justNameTitle(cd)
                return tuple([name, title, category(title), deps])

            def keyNames(path,descend=False) :
                dirs = [ k.GetName() for k in file.Get(path[:-1]).GetListOfKeys()
                         if type(file.Get(path+k.GetName())) is r.TDirectoryFile and k.GetName()!="Calculables" ]
                return [path+dir for dir in dirs] + sum([keyNames(path+dir+"/",descend) for dir in dirs if descend],[])

            return filter(None,[parseCalc(file.Get(name)) for name in keyNames(dirName+'/',descend=(dirName=="Master"))])
        
        def calcs(sample) :
            return ( nodes(sample['file'], "Calculables") +
                     nodes(sample['file'], "Leaves") +
                     nodes(sample['file'], "Master")
                     )
        
        if not hasattr(self,"_organizer__calculables") :
            self.__calculables = [dict([(c[:3],c[3]) for c in calcs(sample)]) for sample in self.samples]
            allCalcs = reduce( lambda x,y: x|y, [set(s.keys()) for s in self.__calculables],set())

            for calc in allCalcs :
                for scalcs in self.__calculables :
                    if calc not in scalcs :
                        scalcs[(calc[0],calc[1],"absent")] = frozenset()
        return self.__calculables

    @property
    def calculablesGraphs(self) :
        def graph(scalcs) :
            calcs = filter(lambda c: c[2]!="absent", scalcs)
            calcByNameT = dict([(c[:2],c) for c in calcs])
            calcByName = dict([(c[0],c) for c in calcs])
            nodes = {}
            def addNode(calc) :
                if calc in nodes : return
                nodes[calc] = utils.vessel()
                nodes[calc].deps = set([calcByNameT[depNameT] if depNameT in calcByNameT else calcByName[depNameT[0]] for depNameT in scalcs[calc]])
                nodes[calc].feeds = set()
                nodes[calc].depLevel = 0
                for dep in nodes[calc].deps :
                    addNode(dep)
                    nodes[dep].feeds.add(calc)
                nodes[calc].depLevel = 0 if not nodes[calc].deps else 1+max([nodes[dep].depLevel for dep in nodes[calc].deps])
            for calc in calcs : addNode(calc)
            return nodes
        if not hasattr(self,"_organizer__calculablesGraphs") :
            self.__calculablesGraphs = [graph(scalcs) for scalcs in self.calculables]
        return self.__calculablesGraphs

    @property
    def mergedGraph(self) :
        if not hasattr(self,"_organizer__mergedGraph") :
            nodes = {}
            for snodes in self.calculablesGraphs :
                for node in snodes:
                    if node not in nodes : nodes[node] = snodes[node]
                    else :
                        nodes[node].deps |= snodes[node].deps
                        nodes[node].feeds|= snodes[node].feeds
            self.__mergedGraph = nodes
        return self.__mergedGraph
        
    @property
    def calculablesDotFile(self) :
        def nodeName(key) : return filter(lambda c: c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", (''.join([key[0]] if key[2]=='leaf' else key[:2])))
        def nodeColor(key) : return ("green" if "muon" in key[0] else
                                     "blue" if "ak5Jet" in key[0] else
                                     "red" if "electron" in key[0] else
                                     "orange" if "photon" in key[0] else
                                     "brown" if "vertex" in key[0] else
                                     "purple" if "track" in key[0] else "black")
        def nodeFontSize(node) : return 10 + 2*(len(node.deps) + len(node.feeds))
        def nodeTexts(nodes) :
            return ['%s [label="%s" shape="%s" fontcolor="%s" color="%s" fontsize="%s"];'%(nodeName(node),node[0][:30],{"fltr":"box","calc":"ellipse","leaf":"plaintext"}[node[2]], nodeColor(node), nodeColor(node), nodeFontSize(nodes[node])) for node in nodes]
        def edgeTexts(nodes) :
            return sum([["%s -> %s;"%(nodeName(node),nodeName(feed)) for feed in nodes[node].feeds] for node in nodes], [])
        if not hasattr(self,"_organizer__calculablesDotFile") :
            lines = nodeTexts(self.mergedGraph) + edgeTexts(self.mergedGraph)
            text = "\n".join(['digraph calculables {',"\trankdir=LR","\trotate=90"]+['\t'+L for L in lines]+['}'])
            self.__calculablesDotFile = text
        return self.__calculablesDotFile

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

        
