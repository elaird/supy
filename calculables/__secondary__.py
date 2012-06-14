import random,string,os,operator, ROOT as r
from supy import analysisStep,wrappedChain,utils

class secondary(wrappedChain.calculable,analysisStep) :
    
    defaultValue = None
    def organize(self,org) : pass
    def onlySamples(self) : return [] # declaration of which samples _not_ to ignore, [] ignores none
    def baseSamples(self) : return [] # declaration of with which samples to build organizer, [] uses all
    def reportCache(self) : print "No report for " + self.name
    
    '''
    Functions an inheritor may wish to redefine :
    * calculable.update(self,_)
    * analysisStep.setup()
    * analysisStep.uponAcceptance()
    * analysisStep.endFunc()
    * analysisStep.mergeFunc()
    * analysisStep.varsToPickle()
    '''

    def cacheFileName(self,tag=None) :
        pieces = filter(None,self.inputFileName.split('/'))
        return '/'.join(['']+pieces[:-2] + [tag if tag!=None else pieces[-2], "cache_%s.root"%self.name])

    @staticmethod
    def allDeps(node,graph, depsSoFar = set()) :
        if node is None : return set()
        nodesToDo = graph[node].deps - depsSoFar
        return set(reduce(operator.__or__, [secondary.allDeps(n,graph,depsSoFar|graph[node].deps) for n in nodesToDo], graph[node].deps))
    @staticmethod
    def equalAxes(p,q) :
        return all( getattr(getattr(p,ax)(),item)() == getattr(getattr(q,ax)(),item)()
                    for ax in ["GetXaxis","GetYaxis"] for item in ["GetNbins","GetXmin","GetXmax"])

    def checkOne(self,cache,org,iSample) :
        sample = org.samples[iSample]['name']
        if self.onlySamples() and sample not in self.onlySamples() : return
        
        if sample not in [key.GetName() for key in cache.GetListOfKeys()] : return "no cache"
        cache.cd(sample)
        keys = [key.GetName() for key in r.gDirectory.GetListOfKeys()]

        hists = dict((key,val[iSample]) for key,val in next(iter(org.steps),dict()).iteritems())
        cachedHists = dict(filter(lambda x: issubclass(type(x[1]),r.TH1), [(name,r.gDirectory.Get(name)) for name in keys]))

        missing = set(hists.keys()) - set(cachedHists.keys())
        if missing : return "missing {%s}"%','.join(missing)

        lost = set(cachedHists.keys()) - set(hists.keys())
        if lost: return "lost {%s}"%','.join(lost)

        mismatched = [k for k in hists.keys() if not self.equalAxes(hists[k],cachedHists[k])]
        if mismatched : return "new definitions {%s}"%','.join(mismatched)

        if "Calculables" not in keys : return "Missing deps"
        r.gDirectory.cd("Calculables")
        cachedDeps = [utils.justNameTitle(key) for key in r.gDirectory.GetListOfKeys()]
        deps = set((n,t) for n,t,_ in self.allDeps( next((key for key in org.calculablesGraphs[iSample] if key[0]==self.name),None),  org.calculablesGraphs[iSample] ))

        new = deps - deps.intersection(cachedDeps)
        old = deps.union(cachedDeps) - deps
        if new or old :
            return ("dependencies changed :\n" +
                    '\n'.join(["                     +-> %s\t%s"%(c[0][:20].ljust(20),c[1][:40].ljust(40)) for c in new]+
                              ["                     <-- %s\t%s"%(c[0][:20].ljust(20),c[1][:40].ljust(40)) for c in old])+  '\t')

        more = filter(lambda k: hists[k].GetEntries()>cachedHists[k].GetEntries(), hists.keys())
        less = filter(lambda k: hists[k].GetEntries()<cachedHists[k].GetEntries(), hists.keys())
        if more or less : return "{%s} <- stats <+ {%s}"%(','.join(less),','.join(more))

        return

    def checkCache(self,org) :
        self.__organize(org)

        if not os.path.exists(self.cacheFileName()) :
            print
            print "!! No cache: %s"%self.cacheFileName()
            return
        cache = r.TFile.Open(self.cacheFileName(),"READ")

        msgs = filter(lambda x: x[1], [(sample['name'],self.checkOne(cache, org, iSample)) for iSample,sample in enumerate(org.samples)])
        cache.Close()
        if msgs :
            print
            print "!! Not up to date: %s"%self.cacheFileName()
            print '\n'.join("\t%s : %s"%(m,s) for s,m in msgs)
        
    def doCache(self,org) :
        self.__organize(org)
        cache = r.TFile.Open(self.cacheFileName(),"UPDATE")
        print "Updating " + self.cacheFileName()

        for iSample,sample in enumerate(org.samples) :
            if sample['name'] in [k.GetName() for k in cache.GetListOfKeys()] : cache.rmdir(sample['name'])
            cache.mkdir(sample['name']).cd()
            for hists in org.steps[0].values() :
                if hists[iSample] : hists[iSample].Write()

            r.gDirectory.mkdir("Calculables").cd()
            deps = self.allDeps(next((key for key in org.calculablesGraphs[iSample] if key[0]==self.name), None), org.calculablesGraphs[iSample])
            for name,title,_ in deps : r.gDirectory.mkdir(name+title.replace('/','-SLASH-').replace(';','-SEMI-').replace(':','-COLON-'),title)
            cache.cd()
            print "\t%s"%sample['name']
        cache.Close()


    def fromCache(self,samples,keys, tag = None) :
        assert type(samples) in [list,set], "fromeCache() takes a list or set of samples"
        sampleHists = dict([(sample,dict((k,None) for k in keys)) for sample in samples])

        cache = r.TFile.Open(self.cacheFileName(tag),"READ") if os.path.exists(self.cacheFileName(tag)) else None
        if not cache :
            print "!! No cache: " + self.cacheFileName(tag)
            return sampleHists

        pad = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
        for sample,hists in sampleHists.iteritems() :
            if sample not in [k.GetName() for k in cache.GetListOfKeys()] : continue
            for key in keys :
                if key in [k.GetName() for k in cache.GetDirectory(sample).GetListOfKeys()] :
                    obj = cache.GetDirectory(sample).Get(key)
                    if issubclass(type(obj),r.TH1) :
                        hists[key] = obj.Clone(obj.GetName()+sample+pad)
                        hists[key].SetDirectory(0)
        cache.Close()
        return sampleHists
                     
    def __organize(self,org) :
        self.organize(org)
        only = self.onlySamples()
        if only:
            for name in [s['name'] for s in org.samples if s['name'] not in only] :
                org.drop(name)

##############################
