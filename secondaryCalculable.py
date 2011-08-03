from wrappedChain import *
from analysisStep import analysisStep

class secondaryCalculable(wrappedChain.calculable,analysisStep) :
    
    '''
    Functions in inheritor may wish to (re)define :
    * calculable.update(self,ignored)

    * calculable.name()

    * analysisStep.setup()
    * analysisStep.endFunc()
    * analysisStep.mergeFunc()
    * analysisStep.varsToPickle()


    * __init__(self)
    * refreshPolicy(self)
    '''
    defaultValue = None

    def secondarySetup(self, inputChain, fileDirectory) : return
    def setup(self, inputChain, fileDirectory) :
        self.secondarySetup(inputChain, fileDirectory)
    
    def secondaryEndFunc(self, chains) : return
    def endFunc(self, chains) :
        if hasattr(self,"source") and hasattr(self.source,"tracedKeys") :
            self.source.tracedKeys |= self.priorFilters
        self.secondaryEndFunc(chains)

    def outputSuffix(self) : return "_%s.root"%self.name

    def fromCache(self,tag,sample,hist) : pass


    def checkCache(self,tag,sample,deps,hists) :

        def equalAxes(p,q) :
            return all( getattr(getattr(p,ax)(),item)() == getattr(getattr(q,ax)(),item)()
                        for ax in ["GetXaxis","GetYaxis"] for item in ["GetNbins","GetXmin","GetXmax"])

        def check(cache) :
            if sample not in [key.GetName() for key in cache.GetListOfKeys()] : return "No cache"
            cache.cd(sample)
            keys = [key.GetName() for key in r.gDirectory.GetListOfKeys()]
            if "Calculables" not in keys : return "Missing deps?"
            #checkDeps
            cachedHists = dict(filter(lambda x: issubclass(type(x[1]),r.TH1), [(name,r.gDirectory.Get(name)) for name in keys]))

            missing = set(hists.keys()) - set(cachedHists.keys())
            if missing : return "Missing hists {%s}"%','.join(missing)

            mismatched = filter(lambda k: not equalAxes(hists[k],cachedHists[k]), hists.keys())
            if mismatched : return "Updated definitions {%s}"%','.join(mismatched)

            moreStats = filter(lambda k: hists[k].GetEntries()>cachedHists[k].GetEntries(), hists.keys())
            if moreStats : return "More stats {%s}"%','.join(moreStats)

            return
            
        cache = r.TFile.Open(self.outputFileName,"UPDATE")
        msg = check(cache)
        if msg : print "%s, use: %s --sample %s --updates %s"%(msg,"--tag %s"%tag if tag else tag,sample,self.name)
        cache.Close()

        
    def recache(self,tag,sample,depGraph,hists) :
        cache = r.TFile.Open(self.outputFileName,"UPDATE")

        if sample not in [k.GetName() for k in cache.GetListOfKeys()] : cache.mkdir(sample)
        cache.cd(sample)
        for h in hists.values() : h.Write()

        if "Calculables" in [k.GetName() for k in r.gDirectory.GetListOfKeys()] : r.gDirectory.rmdir("Calculables")
        r.gDirectory.mkdir("Calculables").cd()
        def allDeps(node) : return sum([allDeps(n) for n in depGraph[node].deps],set(depGraph[node].deps))
        deps = allDeps(next(key for key in depGraph if key[0]==self.name))
        for name,title,_ in deps : r.gDirectory.mkdir(name,title)

        print "Updated cache: %s"%self.outputFileName
        cache.Close()
