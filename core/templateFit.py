#!/usr/bin/env python
import math, bisect, numpy as np

class cached(object):
    def __init__(self, func): self.__func = func
    def __get__(self, obj, _=None):
        setattr(obj, self.__func.func_name, self.__func(obj))
        return getattr(obj, self.__func.func_name)

class templateFitter(object) :
    '''Measure a parameter by polynomial interpolation of templates likelihood to model observation.'''

    @classmethod
    def ensembleOf(cls, nToys, template, templates, pars) :
        pseudos = np.array([np.random.poisson(mu, nToys) for mu in template]).transpose()
        return [cls(pseudo, templates, pars, 0) for pseudo in pseudos]

    def __init__(self, observed = (), templates = [()], pars=[], ensembleSize = 1e4) :
        self.templates = np.maximum(1e-6,templates) # avoid log(0)
        self.templatesN2LL = -2 * np.sum( observed * np.log(self.templates) - self.templates , axis = 1)
        self.__coef = np.polyfit(pars, self.templatesN2LL, deg = 3)[::-1]

        _,c1,c2,c3 = self.__coef
        R = c2 / (3*c3)
        D = math.sqrt(R**2 - c1 / (3*c3) )
        curve,self.__value = max([ (2*c2+6*p*c3, p) for p in [-R+D, -R-D]])
        self.__error = ( 0.5*curve )**-0.5

        self.pars = pars
        self.__ensembleSize = ensembleSize
        self.observed = np.array(observed)
        self.n2LL = sum([self.value**i * self.__coef[i] for i in range(4)])

    @property
    def coefficients(self) : return self.__coef
    @property
    def value(self) : return self.__value
    @property
    def error(self) : return self.__error
    @property
    def bestMatch(self) : return list(self.pars).index(min(self.pars, key = lambda p: abs(p-self.value)))
    @cached
    def ensemble(self) : return self.ensembleOf(self.__ensembleSize, self.templates[self.bestMatch], self.templates, self.pars)
    @property
    def p_value(self) : return 1-bisect.bisect(sorted([toy.n2LL for toy in self.ensemble]), self.n2LL) / float(self.__ensembleSize+1)
    @property
    def residuals(self) : return np.array([toy.value - self.pars[self.bestMatch] for toy in self.ensemble])
    @property
    def relResiduals(self) : return np.array([(toy.value-self.pars[self.bestMatch])/toy.error for toy in self.ensemble ])
    @property
    def bias(self) : return np.mean( self.residuals )
    @property
    def pull(self) : return np.std(self.relResiduals)

class templateEnsembles(object) :
    def __init__(self, nToys, templates, pars) :
        pars, templates = zip(*sorted(zip(pars,templates)))
        self.pars,self.templates = pars,templates
        self.ensembles = [templateFitter.ensembleOf(nToys, templ, templates, pars) for templ in templates ]
        self.biases = [np.mean([toy.value for toy in ensemble]) - par for par,ensemble in zip(pars,self.ensembles)]
        relativeResiduals = [np.array([(toy.value-par)/toy.error for toy in ensemble]) for par,ensemble in zip(pars,self.ensembles)]
        self.pulls = [np.std(rr) for rr in relativeResiduals]
        self.meanError = self.pulls * np.array([np.mean([toy.error for toy in ensemble]) for ensemble in self.ensembles])
        self.sensitivity = np.mean(self.meanError[1:-1])

import utils, ROOT as r
def drawTemplateFitter(tf, canvas = None) :
    if not canvas : canvas = r.TCanvas()
    else: canvas.Clear()
    canvas.cd(0)
    canvas.Divide(2,2)

    #------1
    LL = r.TGraph(len(tf.pars), np.array(tf.pars), tf.templatesN2LL)
    fit = r.TF1("fit","pol3",min(tf.pars),max(tf.pars))
    for i,c in enumerate(tf.coefficients) : fit.SetParameter(i,c)
    xMaxLL = [r.TGraph(2,np.array([val,val]),np.array([min(tf.templatesN2LL),max(tf.templatesN2LL)])) for val in [tf.value,tf.value+tf.error,tf.value-tf.error]]
    for h in xMaxLL : h.SetLineColor(r.kBlue)
    xMaxLL[1].SetLineStyle(r.kDashed)
    xMaxLL[2].SetLineStyle(r.kDashed)
    LL.SetTitle("best fit: %s  | corrected: %s"%(utils.roundString(tf.value,tf.error, noSci=True), 
                                                 utils.roundString(tf.value-tf.bias, tf.error*tf.pull,noSci=True)))
    canvas.cd(1)
    LL.Draw('A*')
    for h in xMaxLL : h.Draw('')
    fit.Draw('same')

    #------2
    n2lls = utils.rHist("-2logLs", *np.histogram([toy.n2LL for toy in tf.ensemble], 100) )
    n2ll = n2lls.Clone('-2logL') ; n2ll.Reset(); n2ll.SetBinContent(n2ll.FindFixBin(tf.n2LL), n2lls.GetMaximum()); 
    n2ll.SetFillColor(r.kBlue); n2lls.SetTitle("p-value: %0.4f"%tf.p_value)
    canvas.cd(2)
    n2lls.Draw()
    n2ll.Draw('same')

    #------3
    edges = range(len(tf.observed)+1)
    observed = utils.rHist("observed", tf.observed, edges, True)
    spars,stemplates = zip(*sorted(zip(tf.pars,tf.templates)))
    templates = [utils.rHist("template%d"%i, templ, edges) for i,templ in enumerate(stemplates) if i in [0,len(spars)-1,len(spars)/2]]
    observed.SetTitle("observed")
    observed.SetMarkerStyle(20)
    for i,templ in enumerate(templates) : templ.SetLineColor([r.kRed,r.kGreen,r.kBlue][i])
    maxHeight = max(h.GetMaximum() for h in [observed]+templates)
    for h in [observed]+templates : h.SetMaximum(1.1*maxHeight)
    canvas.cd(3)
    observed.Draw()
    for t in templates : t.Draw("same")

    #------4
    relMean = np.mean(tf.relResiduals)
    pull = utils.rHist("relative residuals", *np.histogram(tf.relResiduals,100,(relMean-5,relMean+5)))
    canvas.cd(4)
    pull.Draw()

    canvas.Update()
    return canvas,observed,templates,LL,fit,xMaxLL,n2lls,n2ll,pull

import sys
if __name__=="__main__" :
    '''Test the template fitter.'''
    r.gStyle.SetPalette(1)
    r.gROOT.SetStyle("Plain")

    if len(sys.argv)<2 : print "Usage: templateFit [trueParValue=0] [ScaleFactor=100]"
    truePar = float(sys.argv[1]) if len(sys.argv)>1 else 0
    norm = int(sys.argv[2]) if len(sys.argv)>2 else 100

    def template(p) : return np.array([100+norm*math.exp(-0.5*(x-p)**2) for x in range(-5,5)])

    pars = np.arange(-1.0,1.1,0.1)
    templates = [template(p) for p in pars]
    observed = np.array([np.random.poisson(mu) for mu in template(truePar)])

    TF = templateFitter(observed, templates, pars)
    print "true value: ", truePar
    print "measured : ", utils.roundString(TF.value,TF.error)
    canvas = drawTemplateFitter(TF)
    
    print "p-value :", TF.p_value
    print "bias : ", TF.bias
    print "pull : ", TF.pull
    
    raw_input()



    def format(d) : return "[ %s ]"%', '.join("%.3f"%f for f in d)
            
    ensembles = templateEnsembles(500, templates, pars)
    print "pars : ".rjust(20), format(ensembles.pars)
    print "biases : ".rjust(20), format(ensembles.biases)
    print "pulls : ".rjust(20), format(ensembles.pulls)
    print "meanErrors : ".rjust(20), format(ensembles.meanError)
    print "sensitivity : ".rjust(20), ensembles.sensitivity
    
