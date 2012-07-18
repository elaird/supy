#!/usr/bin/env python
import bisect
try:
    import numpy as np
except:
    pass

class cached(object):
    def __init__(self, func): self.__func = func
    def __get__(self, obj, _=None):
        setattr(obj, self.__func.func_name, self.__func(obj))
        return getattr(obj, self.__func.func_name)

class componentSolver(object) :
    '''Maximum likelihood estimators for the component fractions in an observed distribution.'''

    @classmethod
    def ensembleOf(cls, nToys, expected, components, base) :
        return [cls(toy, components, 0, base) for toy in np.array([np.random.poisson(L, nToys) for L in expected]).transpose()]
    
    def __init__(self, observed = (), components = [()], ensembleSize = 1e2, base = None) :
        zero = 1e-6
        self.observed = np.array(observed)
        self.base = np.array(base if base!=None else len(observed)*[0])
        self.__comps = np.array(components) * float(sum(observed)) / zip(np.add.reduce(components,axis=1))
        M = self.__comps.dot(self.__comps.transpose())
        b = (self.observed - self.base).dot(self.__comps.transpose())
        self.fractions = np.linalg.solve(M,b)
        self.expected = np.maximum(zero, self.base + self.fractions.dot(self.__comps))
        self.covariance = np.linalg.inv( (self.__comps * self.observed / self.expected**2).dot(self.__comps.transpose()))
        self.errors = np.sqrt(np.diagonal(self.covariance))
        self.__ensembleSize = ensembleSize

    def __repr__(self) : return "componentSolver( %s, %s, %d, %s)"%(repr(tuple(self.observed)),repr([tuple(c) for c in self.__comps]),self.__ensembleSize, tuple(self.base))
    def __str__(self) : return '''\
    ML fractions   :  %s
    uncertainties  :  %s
    p-value        :  %s
    bias           :  %s
    pull           :  %s
    correlation    :\n%s
    '''%tuple([str(np.round(item, 4)) for item in [self.fractions, self.errors, self.p_value, self.bias, self.pull, self.correlation]])
   
    @property
    def logL(self) : return sum( self.observed * np.log(self.expected) - self.expected ) # - sum(np.log(np.factorial(self.observed)))
    @property
    def components(self) : return zip(self.fractions) * self.__comps 
    @property
    def correlation(self) : return (self.covariance / self.errors) / zip(self.errors)
    @property
    def norm(self) : return sum(self.fractions)
    @cached
    def ensemble(self) : return self.ensembleOf(self.__ensembleSize, self.expected, self.__comps, self.base)
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



import sys, itertools, ROOT as r
import __init__ as utils
def drawComponentSolver(cs, canvas = None, distName = "", templateNames = [], ) :
    oldStyle = r.gStyle.GetOptStat()
    r.gStyle.SetOptStat(1101)
    if not canvas : canvas = r.TCanvas()
    canvas.Clear()
    canvas.cd(0)
    canvas.Divide(2,2)

    provisionalTitle = "ML fractions:   "+", ".join(utils.roundString(f,e,noSci=True) for f,e in zip(cs.fractions,cs.errors) )

    base = utils.rHist("base",cs.base,range(len(cs.base)+1)); base.SetFillColor(r.kGray)
    rTemplates = [utils.rHist("template%d"%i,d,range(len(d)+1)) for i,d in enumerate(cs.components)]
    rObs = utils.rHist("observed",cs.observed,range(len(d)+1),True)
    rObs.SetTitle("%s;bin # ;events"%(distName if distName else provisionalTitle))
    rObs.SetMarkerStyle(20)

    nlls = utils.rHist("-logLs", *np.histogram([-toy.logL for toy in cs.ensemble], 100) )
    nll = nlls.Clone('-logL') ; nll.Reset(); nll.SetBinContent(nll.FindFixBin(-cs.logL), nlls.GetMaximum()); 
    nll.SetFillColor(r.kBlue); nlls.SetTitle("p-value in ensemble: %0.4f;-logL of pseudo-experiment;pseudo-experiments"%cs.p_value)
    pulls = [ utils.rHist( templateNames[i] if templateNames else "relative residuals %d"%i, 
                           *np.histogram(pull,100,(-5,5))) for i,pull in enumerate(cs.relResiduals.transpose())]

    [dist.SetTitleSize(0.05,j) for dist in (rTemplates+pulls+[rObs,nll,nlls]) for j in ['X','Y'] ]

    stats = []
    for i,a,t in zip(range(len(cs.fractions)),pulls,rTemplates) : 
        t.SetFillColor(i+2)
        t.SetLineColor(i+2)
        a.SetLineColor(i+2)
        a.SetMaximum(1.1*max(h.GetMaximum() for h in pulls))
        a.SetTitle(";( f^{pseudo} - f ) / #sigma^{pseudo};pseudo-experiments")
        canvas.cd(4); a.Draw("sames" if i else "")
        canvas.Update()
        st = a.GetListOfFunctions().FindObject("stats")
        st.SetOptStat(1101)
        st.SetLineColor(i+2)
        st.SetY1NDC(0.85-0.16*i)
        st.SetY2NDC(1.0-0.16*i)
        stats.append( st.Clone("stats%d"%i) )
    for s in stats : s.Draw()

    canvas.Update()
    canvas.cd(2) ; 
    nlls.Draw(); 
    nll.Draw("histsame")

    canvas.cd(3)
    leg = r.TLegend(0.05,0.05,0.95,0.95)
    leg.SetTextFont(102)
    labels = ["sample"]+(templateNames+len(rTemplates)*[""])[:len(rTemplates)]+["fixed","observed"]
    countLabels = [label.replace("#bar{","").replace("}","") for label in labels]
    fractions = ["fraction"]+[utils.roundString(f,e,noSci=True) for f,e in zip(cs.fractions,cs.errors)] + ["%.3f"%(float(sum(cs.base))/sum(cs.observed)),"1.0"]
    events = ["events"] + [str(int(sum(comp))) for comp in cs.components] + [str(int(sum(cs.base))),str(int(sum(cs.observed)))]
    objects = [0]+rTemplates + [base,rObs]

    [ leg.AddEntry(obj,
                   label.ljust(2+max(len(it) for it in countLabels) - len(countLabel) + len(label)) + 
                   frac.ljust(2+max(len(it) for it in fractions)) + 
                   ev.rjust(max(len(it) for it in events)) + "   ", 
                   '' if label=='sample' else 'lpe' if label=='observed' else 'f') for label,countLabel,frac,ev,obj in zip(labels,countLabels,fractions,events,objects) ]
    leg.Draw()

    canvas.cd(1)
    rTemplates = sorted(rTemplates,key=lambda t: -t.Integral()) + [base]
    for t,h in reversed(zip(rTemplates[:-1],rTemplates[1:])) : t.Add(h)
    rObs.Draw("e")
    for t in rTemplates : t.Draw("histsame")
    rObs.Draw("esame")

    r.gStyle.SetOptStat(1000000)
    canvas.Update()
    r.gStyle.SetOptStat(oldStyle)
    return [canvas,rObs,rTemplates,stats,pulls,nlls,nll,leg]



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
    base = [100]*histpars['bins']
    ff = componentSolver(obs+base, templates, ensembleSize, base)

    print "true fractions : ", np.round(fracs,4)
    print ff
    print
    print eval(repr(ff))

    if True : 
        stuff = drawComponentSolver(ff, distName = "Constructed Distribution", templateNames = ['red','green','blue','yellow'][:len(templates)])
        canvas = stuff[0]
        canvas.Print('test.pdf')
        raw_input()
