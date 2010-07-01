import os
import ROOT as r
#####################################
def psFromRoot(listOfInFileNames,outFileName,beQuiet) :
    if len(listOfInFileNames)==0 : return
    
    dummyCanvas=r.TCanvas("display","display",500,500)
    dummyCanvas.Print(outFileName+"[")
    for inFileName in listOfInFileNames :
        inFile=r.TFile(inFileName)
        keys=inFile.GetListOfKeys()
        for key in keys :
            someObject=inFile.Get(key.GetName())
            if someObject.ClassName()!="TCanvas" : print "Warning: found an object which is not a TCanvas in the display root file"
            someObject.Print(outFileName)
    dummyCanvas.Print(outFileName+"]")
    os.system("ps2pdf "+outFileName+" "+outFileName.replace(".ps",".pdf"))
    os.system("gzip -f "+outFileName)
    if not beQuiet : print "The display file \""+outFileName+".gz\" has been written."    
#####################################
def getCommandOutput2(command):
    child = os.popen(command)
    data = child.read()
    err = child.close()
    #if err: raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data
#####################################
def pruneFileList(inList) :
    #make a dictionary of file versions
    splitString="_"
    stripString=".root"
    d={}
    for inFile in inList :
        fieldList=inFile.replace(stripString,"").split(splitString)
        key=tuple(fieldList[:-1])
        value=int(fieldList[-1])
        if key not in d :
            d[key]=[value]
        else :
            d[key].append(value)

    #select the highest-numbered version of each file
    outList=[]
    for key in d :
        #print key,d[key]
        fileName=splitString.join(key)
        fileName+=splitString+str(max(d[key]))+stripString
        outList.append(fileName)
    return outList
#####################################
