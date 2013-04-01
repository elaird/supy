import supy,configuration,array
import ROOT as r
import sys

def filePath() :
    return "%s/%s/nonflat_typetree.root"%(supy.whereami(),configuration.localpath())
def libpath() :
    return "%s/cpp/libSusy.so"%supy.whereami()


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
        # for iEntry in range(10) : 
        #     self.fillAddresses(iEntry, addresses)
        #     tree.Fill()
        tree.Write()
        treeFile.Close()

    def makeTree(self) :
        drt,name = configuration.mainTree()
        treeFile = r.TFile.Open(filePath(), "RECREATE")
        if drt.strip('/') : treeFile.mkdir(drt.strip('/')).cd()
        tree = r.TTree(name,name)
        print treeFile.GetName()
        return tree,treeFile

    def branch(self,tree) :
        r.gSystem.Load('libPhysics.so') # brings in TLorentzVector
        r.gSystem.Load(libpath())
        part = r.Susy.Particle()
        partVec = r.std.vector('Susy::Particle')()
        tree.Branch('particle', part)
        tree.Branch('partVec', partVec)
        for i in range(10) :
            part.eta, part.phi = i+2.0, i*1.5
            partVec.clear()
            for j in range(3+i) :
                p = r.Susy.Particle()
                px, py, pz = r.gRandom.Gaus(0,10), r.gRandom.Gaus(0,10), r.gRandom.Gaus(0,10)
                p.SetPxPyPzE(px, py, pz, r.TMath.Sqrt(px*px + py*py + pz*pz))
                partVec.push_back(p)
            print 'partVec.size() :',partVec.size()
            tree.Fill()
        # tree.SetBranchAddress("TpcWaveform", ROOT.AddressOf(wf))
        # for name,(ar,ro,t) in types.items() :
        #     address[name] = array.array(ar,[0])
        #     tree.Branch(name, address[name], "%s/%s"%(name,ro))
        #     vname = "v_"+name
        #     address[vname] = r.std.vector(t)()
        #     tree.Branch(vname, address[vname])
        #     aname = "a_"+name
        #     if hasattr(arrayAddress,aname) :
        #         tree.Branch(aname, r.AddressOf(arrayAddress,aname), "%s[len]/%s"%(aname,ro))
        # return address,arrayAddress

if __name__ == "__main__" :
    wt = writeTree()

