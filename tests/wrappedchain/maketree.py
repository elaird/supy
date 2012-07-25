import supy,configuration,array,ROOT as r

def filePath() :
    return "%s/%s/typetree.root"%(supy.whereami(),configuration.localpath())

# Note : ROOT and array.array use opposite conventions for upper/lowercase (un)signed
#         name     array  ROOT  ROOT_typedef
types = {"int"    : ("i", "I", "Int_t"),
         "uint"   : ("I", "i", "UInt_t"),
         "long"   : ("l", "L", "Long_t"),
         "ulong"  : ("L", "l", "ULong_t"),
         "float"  : ("f", "F", "Float_t"),
         "double" : ("d", "D", "Double_t"),
         "char"   : ("b", "B", "Char_t"),
         "uchar"  : ("B", "b", "UChar_t"),
         "bool"   : ("B", "O", "Bool_t"),
         "short"  : ("h", "S", "Short_t"),
         "ushort" : ("H", "s", "UShort_t"),
         }

class writeTree(object) :
    upper = {"char": 2**7-1, "short": 2**15-1, "int": 2**31-1, "long":2**63-1}

    def __init__(self) :
        tree,treeFile = self.makeTree()
        addresses = self.branch(tree)
        for iEntry in range(10) : 
            self.fillAddresses(iEntry, addresses)
            tree.Fill()
        tree.Write()
        treeFile.Close()

    def makeTree(self) :
        drt,name = configuration.mainTree()
        treeFile = r.TFile.Open(filePath(), "RECREATE")
        if drt.strip('/') : treeFile.mkdir(drt.strip('/')).cd()
        tree = r.TTree(name,name)
        return tree,treeFile

    def branch(self,tree) :
        mal = configuration.maxArrayLength()
        line = "typedef struct {Int_t len;%s} arrays_t;"%(' '.join('  %s a_%s[%d];'%(t,name,mal) for name,(ar,ro,t) in types.items() 
                                                                   if name not in ["bool","char","uchar","ushort","ulong"]))
        r.gROOT.ProcessLine(line)
        arrayAddress = r.arrays_t()
        address = {}

        tree.Branch("len", r.AddressOf(arrayAddress,"len"), "len/I")
        for name,(ar,ro,t) in types.items() :
            address[name] = array.array(ar,[0])
            tree.Branch(name, address[name], "%s/%s"%(name,ro))

            vname = "v_"+name
            address[vname] = r.std.vector(t)()
            tree.Branch(vname, address[vname])

            aname = "a_"+name
            if hasattr(arrayAddress,aname) :
                tree.Branch(aname, r.AddressOf(arrayAddress,aname), "%s[len]/%s"%(aname,ro))

        return address,arrayAddress

    def fillAddresses(self,iEntry,(address,arrayAddress)) :
        address["bool"][0] = bool(iEntry%2)
        self.vfill(address["v_bool"], [bool(i%2) for i in range(iEntry+1)])

        arrayAddress.len = iEntry+1
        for var in ["char","short","int","long","float","double"] :
            uvar,vvar,vuvar,avar,auvar = [s+var for s in ["u","v_","v_u","a_","a_u"]]

            signed = [0.5+i if var in ["float","double"] else i for i in range(iEntry+1)]
            unsigned = [] if var not in self.upper else range(self.upper[var]-5,self.upper[var]-5+iEntry+1)

            if var in address : address[var][0] = signed[-1]
            if uvar in address : address[uvar][0] = unsigned[-1]
            if vvar in address : self.vfill( address[vvar], signed )
            if vuvar in address : self.vfill( address[vuvar], unsigned ) if var!="long" else None
            if hasattr(arrayAddress, avar) and arrayAddress.len :
                setattr(arrayAddress, avar, array.array(types[var][0], signed ) )
            if hasattr(arrayAddress, auvar) and arrayAddress.len :
                setattr(arrayAddress, auvar, array.array(types[uvar][0], unsigned ) )

    @staticmethod
    def vfill(vector, items) :
        vector.clear()
        for i in items : vector.push_back(i)

if __name__ == "__main__" :
    writeTree()
