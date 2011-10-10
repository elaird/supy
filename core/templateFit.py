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
        self.__ensembleSize = ensembleSize
        self.observed = np.array(observed)
        self.templates = np.array(templates)
        self.pars = pars
        self.templatesLL = np.sum( self.observed * np.log(self.templates) - self.templates , axis = 1)

        self.__coef = np.polyfit(pars, self.templatesLL, deg = 3)[::-1]
        c = self.__coef

        if abs(c[3]/c[2]) < 1e-6 : #epsilon
            self.__value = -0.5 * c[1]/c[2]
            self.__error = math.sqrt(abs(0.25/c[2]))
            print "using quadratic: abs(c_3/c_2) = ", abs(c[3]/c[2])
        else:
            R = c[2]/(3*c[3])
            D = math.sqrt(R**2 - c[1]/(3*c[3]))
            self.__value = sorted([ -R+D, -R-D],  key = lambda p : 2*c[2] + 6*p*c[3] )[0]
            curvature = - ( 2*c[2] + 6*c[3]*self.__value )
            self.__error = (2*curvature)**-0.5
        self.maxLL = sum([self.value**i * c[i] for i in range(4)])

    @property
    def coefficients(self) : return self.__coef
    @property
    def value(self) : return self.__value
    @property
    def error(self) : return self.__error
    @property
    def bestMatch(self) : return next(iter(sorted(enumerate(self.pars),key = lambda p : abs(p[1]-self.value))))[0]
    @cached
    def ensemble(self) : return self.ensembleOf(self.__ensembleSize, self.templates[self.bestMatch], self.templates, self.pars)
    @property
    def p_value(self) : return bisect.bisect(sorted([-toy.maxLL for toy in self.ensemble]), -self.maxLL) / float(self.__ensembleSize+1)
    @property
    def residuals(self) : return np.array([toy.value - self.pars[self.bestMatch] for toy in self.ensemble])
    @property
    def relResiduals(self) : return np.array([(toy.value-self.pars[self.bestMatch])/toy.error for toy in self.ensemble ])
    @property
    def bias(self) : return np.mean( self.residuals )
    @property
    def pull(self) : return np.std(self.relResiduals)

import utils, ROOT as r
def drawTemplateFitter(tf, canvas = None) :
    if not canvas : canvas = r.TCanvas()
    canvas.cd(0)
    canvas.Divide(2,2)

    def rHist(name,bins,edges,poissonErrors=False) :
        hist = r.TH1D(name,"",len(bins), np.array(edges,dtype='double'))
        for i,bin in enumerate(bins) : 
            hist.SetBinContent(i+1,bin)
            hist.SetBinError(i+1,math.sqrt(bin) if poissonErrors else 0)
        return hist

    #------1
    LL = r.TGraph(len(tf.pars), tf.pars, tf.templatesLL)
    fit = r.TF1("fit","pol3",min(tf.pars),max(tf.pars))
    for i,c in enumerate(tf.coefficients) : fit.SetParameter(i,c)
    xMaxLL = [r.TGraph(2,np.array([val,val]),np.array([min(tf.templatesLL),max(tf.templatesLL)])) for val in [tf.value,tf.value+tf.error,tf.value-tf.error]]
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
    nlls = rHist("-logLs", *np.histogram([-toy.maxLL for toy in tf.ensemble], 100) )
    nll = nlls.Clone('-logL') ; nll.Reset(); nll.SetBinContent(nll.FindFixBin(-tf.maxLL), nlls.GetMaximum()); 
    nll.SetFillColor(r.kBlue); nlls.SetTitle("p-value: %0.4f"%tf.p_value)
    canvas.cd(2)
    nlls.Draw()
    nll.Draw('same')

    #------3
    edges = range(len(tf.observed)+1)
    observed = rHist("observed", tf.observed, edges, True)
    templates = [rHist("template%d"%i, templ, edges) for i,templ in enumerate(tf.templates) if i in [0,len(tf.templates)-1,len(tf.templates)/2]]
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
    pull = rHist("relative residuals", *np.histogram(tf.relResiduals,100,(relMean-5,relMean+5)))
    canvas.cd(4)
    pull.Draw()

    canvas.Update()
    return canvas,observed,templates,LL,fit,xMaxLL,nlls,nll,pull

import sys
if __name__=="__main__" :
    '''Test the template fitter.'''
    r.gStyle.SetPalette(1)
    r.gROOT.SetStyle("Plain")

    if len(sys.argv)<2 : print "Usage: templateFit [trueParValue=0] [ScaleFactor=100]"
    truePar = float(sys.argv[1]) if len(sys.argv)>1 else 0
    norm = int(sys.argv[2]) if len(sys.argv)>2 else 100

    #def template(p) : return np.array([norm*math.exp(-0.5*(x-p)**2) for x in range(-10,10)])
    def template(p) : return np.array([100+norm*math.exp(-0.5*(x-p)**2) for x in range(-5,5)])

    #pars = np.arange(-1,1.2,0.2)
    pars = np.arange(-2.0,2.2,0.2)
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
