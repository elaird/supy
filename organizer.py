import ROOT as r
import copy

class organizer(object) :
    """Organize selection and histograms.

    samples is a tuple of dicts, each of which describes a sample.
    selections is a tuple of named dicts, keyed with histogram names (see class 'selection')
    histograms of each sample remain in independent TDirectory structures.
    """
    class selection(dict) : 
        """Keys are histogram names, values are tuples of histograms, parallel to samples."""
        def __init__(self,name,title) :
            self.name = name
            self.title = title

    def __init__(self, sampleSpecs = [] ) :
        self.samples = tuple([copy.deepcopy(spec) for spec in sampleSpecs]) # columns
        self.selections = tuple(self.__inititialSelectionsList())  # rows
        self.scaled = False

    def __inititialSelectionsList(self) :
        """Scan samples in parallel to ensure consistency and build list of selection dicts"""
        fileNameString = "outputPlotFileName"
        selections = []

        for s in self.samples :
            s['dir'] = r.TFile(s[fileNameString])
            def extract(histName) :
                hist = s['dir'].Get(histName)
                return hist.GetBinContent(1) if hist and hist.GetEntries() else None
            lumiNjobs,xsNjobs,s['nEvents'],s['nJobs'] = map(extract, ["lumiHisto","xsHisto","nEventsHisto","nJobsHisto"])
            if lumiNjobs: s["lumi"] = lumiNjobs/s['nJobs']
            if xsNjobs: s["xs"] = xsNjobs/s['nJobs']
            assert ("xs" in s)^("lumi" in s), "Sample should have one and only one of {xs,lumi}."
            
        dirs = [ s['dir'] for s in self.samples]
        while dirs[0] :
            keysets = [set([key.GetName() for key in dir.GetListOfKeys()]) for dir in dirs]
            keys = reduce( lambda x,y: x|y ,keysets,set())

            subdirNames = map(lambda d,keys: filter(lambda k: type(d.Get(k)) is r.TDirectoryFile, keys), dirs,keysets)
            subdirLens = map(len,subdirNames)
            if sum(subdirLens) :
                assert subdirLens == [1]*len(dirs), "Organizer can only interpret a single subdirectory in any given directory."
                subdirs = map(lambda d,names: d.Get(names[0]), dirs,subdirNames)
                nameTitles = map(lambda sd: (sd.GetName(),sd.GetTitle()), subdirs)
                for nT in nameTitles: assert nT == nameTitles[0], "Subdirectory names,titles must be identical."
                keys.remove(subdirNames[0][0])
            else: subdirs = [None]*len(dirs)

            nameTitle = ("","") if "/" in dirs[0].GetName() else (dirs[0].GetName(),dirs[0].GetTitle())
            selections.append( self.selection(*nameTitle) )
            for key in keys:
                selections[-1][key] = val = tuple( map(lambda d: d.Get(key), dirs) )
                if key in ["nEventsHisto","nJobsHisto"] : continue
                for s,h in zip(self.samples,val) :
                    if key in ["lumiHisto","xsHisto"] and h: h.Scale(1.0/s['nJobs'])
                    elif "xs" in s and h: h.Scale(s["xs"]/s["nEvents"])
            dirs = subdirs

        return selections

    def mergeSamples(self,sources = [], targetSpec = {}, keepSources = False) :
        assert not self.scaled, "Merge must be called before calling scale."
        for src in sources:
            assert src in map(lambda s: s["name"], self.samples), "You have requested to merge unknown sample %s"%source
        target = copy.deepcopy(targetSpec)
        sourceIndices = filter(lambda i: self.samples[i]["name"] in sources, range(len(self.samples)))
        iTarget = sourceIndices[0]
        sourceIndices.sort()
        sourceIndices.reverse()

        if reduce(lambda x,y: x & y, ["xs" in self.samples[i] for i in sourceIndices], True) :
            #target["xs"] = sum([self.samples[i]["xs"] for i in sourceIndices ])
            target["xs"] = None
        elif reduce(lambda x,y: x & y, ["lumi" in self.samples[i] for i in sourceIndices], True) :
            target["lumi"] = sum([self.samples[i]["lumi"] for i in sourceIndices ])
        else: raise Exception("Cannot merge data with sim")
        
        r.gROOT.cd()
        dir = target["dir"] = r.gDirectory.mkdir(target["name"])
        for sel in self.selections :
            if sel.name is not "":
                dir = dir.mkdir(sel.name,sel.title)
            for key,val in sel.iteritems():
                sources = filter(lambda x:x, map(lambda i:val[i],sourceIndices))
                if len(sources) :
                    hist = sources[0].Clone(key)
                    hist.SetDirectory(dir)
                    for s in sources[1:] : hist.Add(s)
                else: hist = None

                newVal = list(val)
                if not keepSources:
                    for i in sourceIndices: newVal.pop(i)
                newVal.insert(iTarget,hist)
                sel[key] = tuple( newVal )

        samples = list(self.samples)
        if not keepSources:
            for i in sourceIndices: samples.pop(i)
        samples.insert(iTarget,target)
        self.samples = tuple( samples )


    def scale(self, lumiToUseInAbsenceOfData = None) :
        dataIndices = filter(lambda i: "lumi" in self.samples[i], range(len(self.samples)))
        assert len(dataIndices)<2, "What should I do with more than one data sample?"
        iData = dataIndices[0] if len(dataIndices) else None
        lumi = self.samples[iData]["lumi"] if iData!=None else lumiToUseInAbsenceOfData
        assert lumi, "You need to have a data sample or specify the lumi to use."

        for sel in self.selections :
            for key,hists in sel.iteritems() :
                if key in ["lumiHisto","xsHisto","nJobsHisto","nEventsHisto"] : continue
                for h in hists:
                    if not h: continue
                    h.Scale(lumi)
                    dim = int(h.ClassName()[2])
                    axis = h.GetYaxis() if dim==1 else h.GetZaxis() if dim==2 else None
                    if axis: axis.SetTitle("%s / %s pb^{-1}"%(axis.GetTitle(),str(lumi)))
        self.scaled = True
