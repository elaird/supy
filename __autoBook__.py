import ROOT as r

class autoBook(dict) :
    def __init__(self, arg = None) :
        self.__directory = r.TDirectory(arg,arg) if type(arg)==str else arg if arg else 0
        self.fillOrder = []
        self.weight = 1

    @property
    def title(self) : return self.__directory.GetName() if self.__directory else ""
    
    def fill(self, x, name, N, low, up, w = None, title = "", xAxisLabels = [], yAxisLabels = []) :
        if w is None : w = self.weight
        if type(name) in [tuple,list]: name = '_'.join(name)
        if not name in self :
            self.__directory.cd()
            self.fillOrder.append(name)
            self[name] = \
                       r.TH1D( name, title, N, low, up)                            if type(x)!=tuple or len(x)==1 else \
                       r.TProfile( name, title, N, low, up)                        if type(N)!=tuple else \
                       r.TH2D( name,title, N[0],low[0],up[0],  N[1],low[1],up[1])  if len(N)==2      else \
                       r.TH3D( name,title, N[0],low[0],up[0],  N[1],low[1],up[1],  N[2],low[2],up[2])
            if not self[name].GetSumw2N() : self[name].Sumw2()
            for i,label in enumerate(xAxisLabels) :
                self[name].GetXaxis().SetBinLabel(i+1, label)
            for i,label in enumerate(yAxisLabels) :
                self[name].GetYaxis().SetBinLabel(i+1, label)

        if    type(x)!=tuple : self[name].Fill(x,w)
        elif  len(x)==1      : self[name].Fill(x[0],w)
        elif  type(N)!=tuple : self[name].Fill(x[0],x[1],w)
        elif  len(N)==2      : self[name].Fill(x[0],x[1],w)
        else                 : self[name].Fill(x[0],x[1],x[2],w)

    def fillVarBin(self, x, name, B, w =  None, title = "") :
        if type(name) in [tuple,list]: name = '_'.join(name)
        if not name in self :
            import array
            self.__directory.cd()
            self.fillOrder.append(name)
            self[name] = \
                       r.TH1D( name, title, len(B) - 1, array.array('d', B) )  if type(x)!=tuple else \
                       r.TProfile( name, title, len(B) - 1, array.array('d', B) ) if type(B)!=tuple else \
                       r.TH2D( name, title, len(B[0]) - 1, array.array('d', B[0]), len(B[1]) - 1, array.array('d', B[1]) ) if len(B)==2 else \
                       r.TH3D( name, title, len(B[0]) - 1, array.array('d', B[0]), len(B[1]) - 1, array.array('d', B[1]), len(B[2]) - 1, array.array('d', B[2]) )
            if not self[name].GetSumw2N() : self[name].Sumw2()
        self.fill( x, name, B, None, None, w)
