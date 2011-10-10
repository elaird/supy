#!/usr/bin/env python
import math, numpy as np

class templateFitter(object) :
    '''Measure a parameter by polynomial interpolation of templates likelihood to model observation.'''

    def __init__(self, observed = (), templates = [()], pvals=[], ensembleSize = 0, cubic = False) :
        self.observed = np.array(observed)
        self.templates = np.array(templates)
        self.pvals = pvals
        templatesLL = np.sum( self.observed * np.log(self.templates) - self.templates , axis = 1)

        self.__coef = np.polyfit(pvals, templatesLL, deg = 2)[::-1]
        c = self.__coef

        print "val2 : ", -0.5 * c[1]/c[2]
        print "err2 : ", math.sqrt(abs(0.25/c[2]))
        print

        self.__coef = np.polyfit(pvals, templatesLL, deg = 3)[::-1]
        c = self.__coef

        print c[3]/c[2]
        print

        R = c[2]/(3*c[3])
        D = math.sqrt(R**2 - c[1]/(3*c[3]))
        self.__value = sorted([ -R+D,
                                -R-D],  key = lambda p : 2*c[2] + 6*p*c[3] )[0]
        curvature = - ( 2*c[2] + 6*c[3]*self.__value )
        self.__error = (2*curvature)**-0.5

        print "val3 : ", self.__value
        print "err3 : ", self.__error
        
        self.templatesLL = templatesLL
        
    @property
    def coefficients(self) : return self.__coef
    @property
    def value(self) : return self.__value
    @property
    def error(self) : return self.__error
    

import ROOT as r
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

    edges = range(len(tf.observed)+1)
    observed = rHist("observed", tf.observed, edges, True)
    templates = [rHist("template%d"%i, templ, edges) for i,templ in enumerate(tf.templates)]
    observed.SetTitle("observed")
    observed.SetMarkerStyle(20)
    for i,templ in enumerate(templates) : templ.SetLineColor(i)


    LL = r.TGraph(len(tf.pvals), tf.pvals, tf.templatesLL)
    fit = r.TF1("fit","pol3",min(tf.pvals),max(tf.pvals))
    for i,c in enumerate(tf.coefficients) : fit.SetParameter(i,c)

    canvas.cd(0)
    observed.Draw()
    for t in templates : t.Draw("same")

    canvas.cd(1)
    LL.Draw('A*')
    fit.Draw('same')

    return canvas,observed,templates,LL,fit

import sys
if __name__=="__main__" :
    '''Test the template fitter.'''
    if len(sys.argv)<2 : print "Usage: templateFit [trueParValue=0] [ScaleFactor=100]"
    truePar = float(sys.argv[1]) if len(sys.argv)>1 else 0
    norm = int(sys.argv[2]) if len(sys.argv)>2 else 100

    def template(p) : return norm *abs(p)**0.05* np.array([math.exp(-0.5*(x-p)**2) for x in range(-10,10)])

    pars = np.arange(-1,1.2,0.2)
    templates = [template(p) for p in pars]
    observed = np.array([np.random.poisson(mu) for mu in template(truePar)])

    TF = templateFitter(observed, templates, pars)
    print "true value: ", truePar
    canvas = drawTemplateFitter(TF)
    raw_input()
