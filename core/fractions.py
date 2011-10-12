#!/usr/bin/env python
import math, bisect, numpy as np

class cached(object):
    def __init__(self, func): self.__func = func
    def __get__(self, obj, _=None):
        setattr(obj, self.__func.func_name, self.__func(obj))
        return getattr(obj, self.__func.func_name)

class componentSolver(object) :
    '''Maximum likelihood estimators for the component fractions in an observed distribution.'''

    @classmethod
    def ensembleOf(cls, nToys, expected, components) :
        return [cls(toy, components, 0) for toy in np.array([np.random.poisson(L, nToys) for L in expected]).transpose()]
    
    def __init__(self, observed = (), components = [()], ensembleSize = 1e2) :
        zero = 1e-6
        self.observed = np.array(observed)
        self.__comps = np.array(components) * float(sum(observed)) / zip(np.add.reduce(components,axis=1))
        M = self.__comps.dot(self.__comps.transpose())
        b = self.observed.dot(self.__comps.transpose())
        self.fractions = np.linalg.solve(M,b)
        self.expected = np.maximum(zero, self.fractions.dot(self.__comps))
        self.covariance = np.linalg.inv( (self.__comps * self.observed / self.expected**2).dot(self.__comps.transpose()))
        self.errors = np.sqrt(np.diagonal(self.covariance))
        self.__ensembleSize = ensembleSize

    def __repr__(self) : return "componentSolver( %s, %s, %d)"%(repr(tuple(self.observed)),repr([tuple(c) for c in self.__comps]),self.__ensembleSize)
    def __str__(self) : return '''\
    ML fractions   :  %s
    uncertainties  :  %s
    p-value        :  %s
    bias           :  %s
    pull           :  %s
    correlation    :\n%s
    '''%tuple([str(np.round(item, 4)) for item in [self.fractions, self.errors, self.p_value, self.bias, self.pull, self.correlation]])
   
    @property
    def logL(self) : return sum( self.observed * np.log(self.expected) - self.expected ) # - np.log(np.factorial(self.observed))
    @property
    def components(self) : return zip(self.fractions) * self.__comps 
    @property
    def correlation(self) : return (self.covariance / self.errors) / zip(self.errors)
    @property
    def norm(self) : return sum(self.fractions)
    @cached
    def ensemble(self) : return self.ensembleOf(self.__ensembleSize, self.expected, self.__comps)
    @property
    def p_value(self) : return 1-bisect.bisect(sorted([-toy.logL for toy in self.ensemble]), -self.logL) / float(self.__ensembleSize+1)
    @property
    def residuals(self) : return np.array([toy.fractions - self.fractions for toy in self.ensemble])
    @property
    def relResiduals(self) : return np.array([(toy.fractions-self.fractions)/toy.errors for toy in self.ensemble ])
    @property
    def bias(self) : return np.mean( self.residuals, axis=0)
    @property
    def pull(self) :
        rels = self.relResiduals
        return np.std( np.sign(rels) * np.minimum(10, np.fabs(rels)), axis=0)



import sys, utils, itertools, ROOT as r
def drawComponentSolver(cs, canvas = None) :
    if not canvas : canvas = r.TCanvas()
    canvas.cd(0)
    canvas.Divide(2,2)

    rTemplates = [utils.rHist("template%d"%i,d,range(len(d)+1)) for i,d in enumerate(cs.components)]
    rObs = utils.rHist("observed",cs.observed,range(len(d)+1),True)
    rObs.SetTitle("ML fractions:   "+", ".join(utils.roundString(f,e,noSci=True) for f,e in zip(cs.fractions,cs.errors) ))

    nlls = utils.rHist("-logLs", *np.histogram([-toy.logL for toy in cs.ensemble], 100) )
    nll = nlls.Clone('-logL') ; nll.Reset(); nll.SetBinContent(nll.FindFixBin(-cs.logL), nlls.GetMaximum()); 
    nll.SetFillColor(r.kBlue); nll.SetTitle("p-value: %0.4f"%cs.p_value)
    pulls = [ utils.rHist("relative residuals %d"%i, *np.histogram(pull,100,(-5,5))) for i,pull in enumerate(cs.relResiduals.transpose())]

    corr = cs.correlation
    corrH = r.TH2D("correlations","correlations", len(corr), -0.5, len(corr)-0.5, len(corr), -0.5, len(corr)-0.5)
    for i,j in itertools.product(range(len(corr)), repeat = 2) : corrH.SetBinContent(i+1,j+1,round(corr[i][j],3))
    corrH.SetMaximum(1)
    corrH.SetMinimum(-1)
    canvas.cd(3)
    corrH.Draw("colztext")

    stats = []
    for i,a,t in zip(range(len(cs.fractions)),pulls,rTemplates) : 
        t.SetFillColor(i+2)
        t.SetLineColor(i+2)
        a.SetLineColor(i+2)
        a.SetMaximum(1.1*max(h.GetMaximum() for h in pulls))
        canvas.cd(4); a.Draw("sames" if i else "")
        canvas.Update()
        st = a.GetListOfFunctions().FindObject("stats")
        st.SetOptStat(1101)
        st.SetLineColor(i+2)
        st.SetY1NDC(0.85-0.16*i)
        st.SetY2NDC(1.0-0.16*i)
        stats.append( st.Clone("stats%d"%i) )
    for s in stats : s.Draw()

    canvas.cd(2) ; nll.Draw(); nlls.Draw("histsame")
    rObs.SetMarkerStyle(20)

    def draw(i,logY = False) :
        canvas.cd(i).SetLogy(logY)
        rObs.Draw("e")
        for t in rTemplates : t.Draw("histsame")
        rObs.Draw("esame")

    rTemplates = sorted(rTemplates,key=lambda t: -t.Integral())
    for t,h in reversed(zip(rTemplates[:-1],rTemplates[1:])) : t.Add(h)
    draw(1, logY = False)    
    #draw(3, logY = True)
    canvas.Update()
    return [canvas,rObs,rTemplates,stats,pulls,nlls,nll,corrH]

if __name__=="__main__" :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.gStyle.SetOptStat(1101)
    fracs = [eval(b) for b in sys.argv[1:]] ; fracs.append(1-sum(fracs))
    if not ( 2 <= len(fracs) <= 4 ) : print "Pass between 1 and 3 composition fractions."; sys.exit(0)
    if not sum(fracs) <= 1: print "Sum of fractions cannot exceeed 1!"; sys.exit(0)

    histpars = {"bins":50,"range":(-5,5)}
    throws = 1e6
    ensembleSize = 1e4
    attenuation = 100

    gauss = [[(-1,1),(1,1),(2,0.5),(-3,3),(5,1)] , # mirrored
             [(0,1),(2,0.5),(-3,3),(5,1)] ,        # heterogeneous
             [(0,1),(0,1.1),(0.1,1),(5,1)] ,       # highly correlated
             ][1][:len(fracs)]

    def values(mu,sig,N=0) : return list(np.minimum(histpars['range'][1],(np.maximum(histpars["range"][0],np.random.normal(mu,sig,N)))))
    templates = [np.histogram(values(*pars, N=throws), **histpars)[0] for pars in gauss]
    obs,edges = np.histogram( sum([values(*pars,N=frac*throws/attenuation) for pars,frac in zip(gauss,fracs)],[]), **histpars)
    ff = componentSolver(obs, templates, ensembleSize)

    print "true fractions : ", np.round(fracs,4)
    print ff
    print
    print eval(repr(ff))

    if True : 
        stuff = drawComponentSolver(ff)
        canvas = stuff[0]
        canvas.Print('test.eps')
        raw_input()
