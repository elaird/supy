import ROOT as r
from array import array

class minuit(object) :
    
    def __init__(self, func, **initialValues) :
        self.ierflg = r.Long(1982) # for accessing MINUIT return values

        self.fcn = self.functionize(func)
        self.argNames = func.__code__.co_varnames[:func.__code__.co_argcount]
        self.minuit = r.TMinuit(len(self.argNames))
        self.minuit.SetFCN( self.fcn )
        self.setInitialValues(self.argNames, initialValues)
        return
        
    @staticmethod
    def functionize(function) :
        def fcn(npar, gin, f, par, iflag) : 
            f[0] = function(*tuple(par[i] for i in range(function.__code__.co_argcount)))
        return fcn

    def setInitialValues(self, argNames, ivs ) :
        for i,name in enumerate(argNames) :
            start,step,lo,hi = 0.,0.1,0.,0. # defaults
            if name in ivs :
                iv = ivs[name]
                if type(iv) is tuple:
                    assert len(iv)==2 or len(iv)==4,'\n\nInitial value can be start, (start,step), or (start,step,lo,hi)'
                    if len(iv)==2 : start,step = iv
                    else : start,step,lo,hi = iv
                else: start = initalValues[name]
            self.minuit.mnparm(i,name, start, step, lo, hi, self.ierflg)
        return

    def mnexcm(self,command,*args) :
        arglist = array('d',args)
        self.minuit.mnexcm( command, arglist, len(args), self.ierflg)
        return self.ierflg

    def printStatus(self) :
        amin,edm,errdef = tuple(r.Double(i) for i in 3*[0.])
        nvpar, nparx, icstat = tuple(r.Long(i) for i in 3*[1984])
        self.minuit.mnstat( amin, edm, errdef, nvpar, nparx, icstat )
        self.minuit.mnprin(3, amin)

# Example Usage:
#
#  Error = 0;
#  z = array( 'f', ( 1., 0.96, 0.89, 0.85, 0.78 ) )
#  errorz = array( 'f', 5*[0.01] )
#  x = array( 'f', ( 1.5751, 1.5825,  1.6069,  1.6339,   1.6706  ) )
#  y = array( 'f', ( 1.0642, 0.97685, 1.13168, 1.128654, 1.44016 ) )
#  
#  def fnc(a1,a2,a3,a4) :
#      chisq = 0.
#      for i in range(len(x)) :
#          f = ((a1/x[i])**2-1) / (a2+a3*y[i]-a4*y[i]*y[i])
#          delta = (z[i]-f)/errorz[i]
#          chisq += delta*delta
#      return chisq
#  
#  m = minuit(fnc, a1=(3,0.1),
#                  a2=(1,0.1),
#                  a3=(0.1,0.01),
#                  a4=(0.01,0.001))
#  m.mnexcm("SET ERR", 1)
#  m.mnexcm("MIGRAD",500,1.)
#  m.printStatus()
