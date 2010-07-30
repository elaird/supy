import ROOT as r

class autoBook(dict) :
    def __init__(self,title="") :
        self.title = title
        self.__directory = 0 if title=="" else r.TDirectory(title,title)
        
    def fill(self,x, name, N, low, up, w=1, title="") :
        if not name in self :
            self[name] = \
                r.TH1D(    name,title,N,low,up) if type(x)!=tuple else \
                r.TProfile(name,title,N,low,up) if type(N)!=tuple else \
                r.TH2D(name,title,
                       N[0],low[0],up[0],
                       N[1],low[1],up[1]) if len(N)==2 else \
                r.TH3D(name,title,
                       N[0],low[0],up[0],
                       N[1],low[1],up[1],
                       N[2],low[2],up[2])
            
            self[name].SetDirectory(self.__directory)
            if not self[name].GetSumw2N() : self[name].Sumw2()

        if    type(x)!=tuple : self[name].Fill(x,w)
        elif  type(N)!=tuple : self[name].Fill(x[0],x[1],w)
        elif  len(N)==2      : self[name].Fill(x[0],x[1],w)
        else                 : self[name].Fill(x[0],x[1],x[2],w)
        

