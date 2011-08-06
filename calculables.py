from wrappedChain import *
from inspect import isclass,ismodule,getargspec
import configuration,operator
##############################
class weight(wrappedChain.calculable) :
    def __init__(self, weights) :
        self.calcNames = [w.name for w in weights]
        self.moreName = ".".join(["1"]+sorted(self.calcNames))
    def update(self, ignored) :
        weights = [self.source[n] for n in self.calcNames]
        self.value = reduce(operator.mul, weights, 1) if None not in weights else None
##############################
class indicesOther(wrappedChain.calculable) :
    @property
    def name(self) : return self.indicesOther
    
    def __init__(self, collection = None) :
        self.indices      = "%sIndices%s"%collection
        self.indicesOther = "%sIndicesOther%s"%collection

    def update(self,ignored) :
        self.value = []
        if not self.source.node(self.indices).updated :
            self.source[self.indices]
##############################
def zeroArgs() :
    """Returns a list of instances of all zero argument calculables."""

    zeroArg = []
    for mod in globals().values() :
        if not ismodule(mod) : continue
        for name,calc in mod.__dict__.iteritems() :
            if not isclass(calc) : continue
            if not issubclass(calc, wrappedChain.calculable) : continue
            try:
                args = len(getargspec(calc.__init__.im_func)[0])
                if args < 2 :
                    zeroArg.append(calc())
            except: zeroArg.append(calc())
    return zeroArg
##############################
def fromCollections(module,collections) :
    """Returns a list of instances of all calculables in module taking only the collection as arg."""

    calcs = []
    for name,calc in module.__dict__.iteritems() :
        if not isclass(calc) : continue
        if not issubclass(calc, wrappedChain.calculable) : continue
        if not hasattr(calc.__init__,"im_func") : continue
        args = getargspec(calc.__init__.im_func)[0]
        if "collection" in args and len(args) is 2:
            for col in collections : calcs.append(calc(col))
    return calcs
##############################

import random,string,os
from analysisStep import analysisStep

class secondary(wrappedChain.calculable,analysisStep) :
    
    defaultValue = None
    def organize(self,org) : pass
    
    '''
    Functions an inheritor may wish to redefine :
    * calculable.update(self,ignored)
    * analysisStep.setup()
    * analysisStep.endFunc()
    * analysisStep.mergeFunc()
    * analysisStep.varsToPickle()
    '''

    def cacheFileName(self,tag=None) :
        pieces = filter(None,self.inputFileName.split('/'))
        return '/'.join(['']+pieces[:-2] + [tag if tag!=None else pieces[-2], "cache_%s.root"%self.name])

    @staticmethod
    def allDeps(node,graph, depsSoFar = set()) :
        if node is None : return []
        depsSoFar|=graph[node].deps
        return reduce(lambda s,t: s|t, [secondary.allDeps(n,graph,depsSoFar) for n in graph[node].deps if n not in depsSoFar], graph[node].deps)
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
        deps = set((n,t) for n,t,_ in self.allDeps( next((key for key in org.calculablesGraphs[iSample] if key[0]==self.name),None),  org.calculablesGraphs[iSample] ))

        new = deps - deps.intersection(cachedDeps)
        old = deps.union(cachedDeps) - deps
        if new or old : return "{%s} <- dependencies <+ {%s}"%(','.join(str(o) for o in old),','.join(str(n) for n in new))

        more = filter(lambda k: hists[k].GetEntries()>cachedHists[k].GetEntries(), hists.keys())
        less = filter(lambda k: hists[k].GetEntries()<cachedHists[k].GetEntries(), hists.keys())
        if more or less : return "{%s} <- stats <+ {%s}"%(','.join(less),','.join(more))

        return

    def checkCache(self,org) :
        self.organize(org)
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
            deps = self.allDeps(next((key for key in org.calculablesGraphs[iSample] if key[0]==self.name), None), org.calculablesGraphs[iSample])
            for name,title,_ in deps : r.gDirectory.mkdir(name,title)
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
                     
##############################
for module in configuration.calculablesFiles() :
    exec("import calculables%s as %s"%(module, module))
##############################
