#/usr/bin/env python
import math,numpy as np

class templateFitter(object) :
    '''Measure a parameter by polynomial interpolation of templates likelihood to model observation.'''

    def __init__(self, observed = (), templates = [()], pvals=[], ensembleSize = 0) :
        self.observed = np.array(observed)
        self.templates = np.array(templates)
        self.pvals = pvals
        templatesLL = np.sum( self.observed * np.log(self.templates) - self.templates , axis = 1)

        self.__coef = np.polyfit(pvals, templatesLL, deg = 3)
        c = self.__coef
        R = c[1]/c[0]
        D = 2*math.sqrt(R**2 - 3*c[2]/c[0])
        self.__value = sorted([ -R+D,
                                -R-D],  key = lambda p : 6*p*c[0] + 2*c[1] )[0]
        curvature = - ( 2*c[1] + 6*c[0]*self.__value )
        self.__error = (2*curvature)**-0.5
        
    @property
    def coefficients(self) : return self.__coeff
    @property
    def value(self) : return self.__value
    @property
    def error(self) : return self.__error
    

if __name__=="__main__" :
    '''Test the template fitter.'''
    pass
