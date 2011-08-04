import random,string
from wrappedChain import *
from analysisStep import analysisStep

class secondaryCalculable(wrappedChain.calculable,analysisStep) :
    
    defaultValue = None
    def organize(self,org) : pass
    
    '''
    Functions in inheritor may wish to (re)define :
    * calculable.update(self,ignored)
    * analysisStep.setup()
    * analysisStep.endFunc()
    * analysisStep.mergeFunc()
    * analysisStep.varsToPickle()
    '''

    def cacheFileName(self,tag=None) :
        pieces = self.inputFileName.split('/')
        return '/'.join(pieces[:-2] + [tag if tag!=None else pieces[-2], "cache_%s.root"%self.name])

    @staticmethod
    def allDeps(node,graph) :
        return reduce(lambda s,t: s|t, [secondaryCalculable.allDeps(n,graph) for n in graph[node].deps], graph[node].deps)
    @staticmethod
    def equalAxes(p,q) :
        return all( getattr(getattr(p,ax)(),item)() == getattr(getattr(q,ax)(),item)()
                    for ax in ["GetXaxis","GetYaxis"] for item in ["GetNbins","GetXmin","GetXmax"])

    def checkOne(self,cache,org,iSample) :
        sample = org.samples[iSample]['name']

        if sample not in [key.GetName() for key in cache.GetListOfKeys()] : return "no cache"
        cache.cd(sample)
        keys = [key.GetName() for key in r.gDirectory.GetListOfKeys()]

        hists = dict((key,val[iSample]) for key,val in org.steps[0].iteritems())
        cachedHists = dict(filter(lambda x: issubclass(type(x[1]),r.TH1), [(name,r.gDirectory.Get(name)) for name in keys]))

        missing = set(hists.keys()) - set(cachedHists.keys())
        if missing : return "missing {%s}"%','.join(missing)

        mismatched = [k for k in hists.keys() if not self.equalAxes(hists[k],cachedHists[k])]
        if mismatched : return "new definitions {%s}"%','.join(mismatched)

        if "Calculables" not in keys : return "Missing deps"
        r.gDirectory.cd("Calculables")
        cachedDeps = [(key.GetName(),key.GetTitle() if key.GetTitle()!=key.GetName() else '') for key in r.gDirectory.GetListOfKeys()]
        deps = set((n,t) for n,t,_ in self.allDeps( next(key for key in org.calculablesGraphs[iSample] if key[0]==self.name),  org.calculablesGraphs[iSample] ))

        new = deps - deps.intersection(cachedDeps)
        old = deps.union(cachedDeps) - deps
        if new or old : return "{%s} <- dependencies <+ {%s}"%(','.join(str(o) for o in old),','.join(str(n) for n in new))

        more = filter(lambda k: hists[k].GetEntries()>cachedHists[k].GetEntries(), hists.keys())
        less = filter(lambda k: hists[k].GetEntries()<cachedHists[k].GetEntries(), hists.keys())
        if more or less : return "{%s} <- stats <+ {%s}"%(','.join(less),','.join(more))

        return

    def checkCache(self,org) :
        self.organize(org)
        cache = r.TFile.Open(self.cacheFileName(),"UPDATE")
        msgs = filter(lambda x: x[1], [(sample['name'],self.checkOne(cache, org, iSample)) for iSample,sample in enumerate(org.samples)])
        cache.Close()
        if msgs :
            print "Not up to date: %s"%self.cacheFileName()
            print '\n'.join("\t%s : %s"%(m,s) for s,m in msgs)
        
    def doCache(self,org) :
        self.organize(org)
        cache = r.TFile.Open(self.cacheFileName(),"UPDATE")
        print "Updating " + self.cacheFileName()

        for iSample,sample in enumerate(org.samples) :
            if sample['name'] in [k.GetName() for k in cache.GetListOfKeys()] : cache.rmdir(sample['name'])
            cache.mkdir(sample['name']).cd()
            for hists in org.steps[0].values() :
                if hists[iSample] : hists[iSample].Write()

            if "Calculables" in [k.GetName() for k in r.gDirectory.GetListOfKeys()] : r.gDirectory.rmdir("Calculables")
            r.gDirectory.mkdir("Calculables").cd()
            deps = self.allDeps(next(key for key in org.calculablesGraphs[iSample] if key[0]==self.name), org.calculablesGraphs[iSample])
            for name,title,_ in deps : r.gDirectory.mkdir(name,title)
            cache.cd()
            print "\t%s"%sample['name']
        cache.Close()


    def fromCache(self,samples,keys, tag = None) :
        cache = r.TFile.Open(self.cacheFileName(tag),"READ")
        if not cache : return cache,dict()
        sampleHists = dict([(sample,dict((k,None) for k in keys)) for sample in samples])

        pad = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
        for sample,hists in sampleHists.iteritems() :
            if sample not in [k.GetName() for k in cache.GetListOfKeys()] : continue
            for key in keys :
                if key in [k.GetName() for k in cache.GetDirectory(sample).GetListOfKeys()] :
                    obj = cache.GetDirectory(sample).Get(key)
                    if issubclass(type(obj),r.TH1) :
                        hists[key] = obj.Clone(obj.GetName()+sample+pad)
                        hists[key].SetDirectory(0)
        return cache,sampleHists
                     
