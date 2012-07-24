import supy,configuration,array,ROOT as r

def filePath() :
    return "%s/%s/typetree.root"%(supy.whereami(),configuration.localpath())

def writeTree() :
    file = r.TFile.Open(filePath(), "RECREATE")
    dir,name = configuration.mainTree()
    file.cd('/')
    file.mkdir(dir.strip('/'))
    file.cd(dir)


    # Note : ROOT and array.array use opposite conventions for upper/lowercase (un)signed
    #         name  array  ROOT
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

    mal = configuration.maxArrayLength()
    line = "typedef struct {Int_t len;%s} arrays_t;"%(' '.join('  %s a_%s[%d];'%(t,name,mal) for name,(ar,ro,t) in types.items() 
                                                               if name not in ["bool","char","uchar","uint","ushort","ulong"]))
    r.gROOT.ProcessLine(line)
    arrays = r.arrays_t()

    addresses = {}
    tree = r.TTree(name,name)
    tree.Branch("len", r.AddressOf(arrays,"len"), "len/I")
    for name,(ar,ro,t) in types.items() :
        addresses[name] = array.array(ar,[0])
        tree.Branch(name, addresses[name], "%s/%s"%(name,ro))

        vname = "v_"+name
        addresses[vname] = r.std.vector(t)()
        tree.Branch(vname, addresses[vname])

        aname = "a_"+name
        if hasattr(arrays,aname) :
            tree.Branch(aname, r.AddressOf(arrays,aname), "%s[len]/%s"%(aname,ro))

    upper = {"char": 2**7-1, "short": 2**15-1, "int": 2**31-1, "long":2**63-1}

    for iEntry in range(10) :
        arrays.len = iEntry
        for var in ["char","short","int","long"] :
            addresses[var][0]     = iEntry if iEntry<5 else -iEntry
            addresses["u"+var][0] = iEntry if iEntry<5 else upper[var] + iEntry

            vvar = "v_"+var
            addresses[vvar].clear()
            for i in range(iEntry) : addresses[vvar].push_back(-i if i<5 else upper[var]-i )

            for avar in ["a_"+var,"a_u"+var] :
                if hasattr(arrays,avar) and arrays.len :
                    setattr(arrays,avar,array.array(types[var][0], range(arrays.len)))

            if var!="long" : # c++ crashes on ULong_t
                vvar = "v_u"+var
                addresses[vvar].clear()
                for i in range(iEntry) : addresses[vvar].push_back(i if i<5 else upper[var]+i )

        for var in ["float","double"] :
            addresses[var][0] = iEntry + 0.5

            vvar = "v_"+var
            addresses[vvar].clear()
            for i in range(iEntry) : addresses[vvar].push_back(i)

            avar = "a_"+var
            if hasattr(arrays,avar) and arrays.len : setattr(arrays,avar,array.array(types[var][0], range(arrays.len)))

        addresses["bool"][0] = bool(iEntry%2)
        addresses["v_bool"].clear()
        for i in range(iEntry+3) : addresses["v_bool"].push_back(bool(i%2))

        tree.Fill()
    
    tree.Write()
    file.Close()


if __name__ == "__main__" :
    writeTree()
