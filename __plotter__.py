import ROOT as r
import os,math,string,itertools,re
import utils,configuration as conf
from supy import whereami


def combineBinContentAndError(histo, binToContainCombo, binToBeKilled) :
    xflows     = histo.GetBinContent(binToBeKilled)
    xflowError = histo.GetBinError(binToBeKilled)

    if xflows==0.0 : return #ugly

    currentContent = histo.GetBinContent(binToContainCombo)
    currentError   = histo.GetBinError(binToContainCombo)
    
    histo.SetBinContent(binToBeKilled, 0.0)
    histo.SetBinContent(binToContainCombo, currentContent+xflows)
    
    histo.SetBinError(binToBeKilled, 0.0)
    histo.SetBinError(binToContainCombo, math.sqrt(xflowError**2+currentError**2))


def mcLumi(nEvents=None, w=None, xs=None):
    """see docs/mcLumi.txt"""
    if not w*xs:
        return 0.0
    return nEvents**2/(w*xs)


def sampleName(sample):
    if len(sample.get("sources", [])) == 1:
        return sample["sources"][0]["name"]
    else:
        return sample["name"]


def sampleInfo(samples, trim=""):
    out = []
    for sample in samples:
        if "xs" in sample:
            xs = sample["xs"]
            lumi = mcLumi(nEvents=sample["nEventsIn"],
                          w=sample["weightIn"],
                          xs=sample["xs"])
        elif "lumi" in sample:
            xs = None
            lumi = sample["lumi"]
        else:
            assert False, sample

        name = sampleName(sample)
        if trim:
            name = name.replace(trim, "")
        out.append((name,
                    "%d" % sample['nEventsIn'],
                    "%3.2e" % sample['weightIn'],
                    "%3.2e" % (lumi/1.0e3),
                    "%3.2e" % (xs*1.0e3) if xs is not None else "",
                    ))
    return out


def suffixes(samples=[]):
    out = [""]
    for sample in samples:
        name = sampleName(sample)
        iDot = name.find(".")
        if 0 <= iDot:
            out.append(name[iDot:])
    return set(out)


def sampleRows(samples=[]):
    out = []
    used = []
    for suffix in sorted(suffixes(samples), key=lambda x: -len(x)):
        remaining = filter(lambda x: x not in used, samples)
        #remaining.sort(key=lambda x: (x[0][:5], int(float(x[2])), -int(x[1]), x[0][5:]))

        subset = []
        for sample in remaining:
            if sampleName(sample).endswith(suffix):
                subset.append(sample)
        used += subset
        out += [tuple([suffix] + [""]*4)]
        out += sampleInfo(subset, trim=suffix)
    return out


class plotter(object) :
    ##############################
    @staticmethod
    def setupStyle(optStat=None) :
        r.gROOT.SetStyle("Plain")
        r.gStyle.SetPalette(1)
        if optStat:
            r.gStyle.SetOptStat(optStat)
    ##############################
    @staticmethod
    def setupTdrStyle() :
        r.gROOT.ProcessLine(".L %s/cpp/tdrstyle.C"%whereami())
        r.setTDRStyle()
        #tweaks
        r.tdrStyle.SetPadRightMargin(0.06)
        r.tdrStyle.SetErrorX(r.TStyle().GetErrorX())
        r.gStyle.SetPalette(1)
    ##############################
    @staticmethod
    def tcanvas(anMode = False) :
        return r.TCanvas("canvas", "canvas", 500, 500) if anMode else r.TCanvas()
    ##############################
    @staticmethod
    def doShiftUnderAndOverflows(dimension, histos, dontShiftList = []) :
        if dimension!=1 : return
        for histo in histos:
            if not histo : continue
            if histo.GetName() in dontShiftList : continue
            if type(histo) is r.TProfile : continue
            bins = histo.GetNbinsX()
            entries = histo.GetEntries()
            combineBinContentAndError(histo, binToContainCombo = 1   , binToBeKilled = 0     )
            combineBinContentAndError(histo, binToContainCombo = bins, binToBeKilled = bins+1)
            histo.SetEntries(entries)
    ##############################
    @staticmethod
    def dimensionOfHisto(histos) :
        def D(h) : return 3 if issubclass(type(h),r.TH3) else 2 if issubclass(type(h),r.TH2) else 1 if issubclass(type(h),r.TH1) else 0
        dimensions = set([D(h) for h in histos if h])
        assert len(dimensions)==1,"inconsistent histogram dimensions\n{%s}"%','.join(h.GetName() for h in histos if h)
        return next(iter(dimensions))
    ##############################        
    @staticmethod
    def metFit(histo) :
        if "met" not in histo.GetName() :
            return
        r.gStyle.SetOptFit(1111)
        funcName="func"
        func=r.TF1(funcName,"[0]*x*exp( -(x-[1])**2 / (2.0*[2])**2 )/[2]",0.5,30.0)
        func.SetParameters(1.0,5.0,3.0)
        histo.Fit(funcName,"lrq","sames")
        histo.GetFunction(funcName).SetLineWidth(1)
        histo.GetFunction(funcName).SetLineColor(histo.GetLineColor())
        return func
    ##############################
    @staticmethod
    def makeAlphaTFunc(alphaTValue) :
        alphaTFunc=r.TF1("alphaTCurve"+str(alphaTValue),
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(r.kBlack)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc
    ##############################
    @staticmethod
    def adjustPad(pad, anMode = False, pushLeft = False) :
        if not anMode :
            r.gPad.SetRightMargin(0.15)
            r.gPad.SetTicky()
            r.gPad.SetTickx()
            if pushLeft : r.gPad.SetLeftMargin(0.4)


    def __init__(self,
                 someOrganizer,
                 pdfFileName = "out.pdf",
                 samplesForRatios = ("",""),
                 sampleLabelsForRatios = ("",""),
                 printRatios = False,
                 foms = [],
                 printXs = True,
                 printImperfectCalcPageIfEmpty=False,
                 showStatBox = True,
                 doLog = True,
                 pegMinimum = None,
                 optStat = 1111111,
                 anMode = False,
                 drawYx = False,
                 fitFunc = None,
                 doColzFor2D = True,
                 compactOutput = False,
                 noSci = False,
                 showErrorsOnDataYields = False,
                 linYAfter = None,
                 nLinesMax = 22,
                 nColumnsMax = 75,
                 pageNumbers = True,
                 latexYieldTable = False,
                 detailedCalculables = False,
                 shiftUnderOverFlows = True,
                 rowColors = [r.kBlack],
                 rowCycle = 5,
                 omit2D = False,
                 dependence2D = False,
                 dontShiftList = ["lumiHisto","xsHisto","nJobsHisto"],
                 blackList = [],
                 whiteList = [],
                 pushLeft = False
                 ) :
        for item in ["someOrganizer","pdfFileName","samplesForRatios","sampleLabelsForRatios","doLog","linYAfter","latexYieldTable",
                     "pegMinimum", "anMode","drawYx","fitFunc","doColzFor2D","nLinesMax","nColumnsMax","compactOutput","pageNumbers",
                     "noSci", "showErrorsOnDataYields", "shiftUnderOverFlows","dontShiftList","whiteList","blackList","showStatBox",
                     "detailedCalculables", "rowColors","rowCycle","omit2D","dependence2D","foms","printXs","optStat",
                     "printImperfectCalcPageIfEmpty", "pushLeft"] :
            setattr(self,item,eval(item))

        self.nLinesMax -= nLinesMax/rowCycle
        if "counts" not in self.whiteList : self.blackList.append("counts")
        self.plotRatios = self.samplesForRatios!=("","")
        self.canvas = self.tcanvas(self.anMode)
        self.formerMaxAbsI = -1
        self.pageNumber = -1
        self.pdfOptions = ''
        if pdfFileName[-3:]==".ps" : self.pdfFileName = self.pdfFileName.replace('.ps','.pdf')

        # backward compatibility
        if printRatios and (not self.foms):
            self.foms = [{"value": lambda x, y: x/y,
                          "uncRel": lambda x, y, xUnc, yUnc: math.sqrt((xUnc/x)**2 + (yUnc/y)**2),
                          "label": lambda x, y:"%s/%s" % (x, y),
                          },
                         ]

        #used for making latex tables
        self.cutDict = {}
        self.yieldDict = {}
        self.sampleList = []

    def plotAll(self) :
        print utils.hyphens
        self.setupStyle(self.optStat)

        self.printCanvas("[")
        text1 = self.printTimeStamp()
        text2 = self.printNEventsIn()
        self.flushPage()

        if self.detailedCalculables :
            blocks = filter(None, utils.splitList( self.someOrganizer.formattedCalculablesGraph(), ('','','')))
            for page in utils.pages(blocks,50) :
                text3 = self.printCalculablesDetailed(page)
                self.flushPage()
        else :
            text3 = self.printCalculables(selectImperfect = False)
            self.flushPage()
            text4 = self.printCalculables(selectImperfect = True)
            if text4 or self.printImperfectCalcPageIfEmpty:
                self.flushPage()
            
        nSelectionsPrinted = 0
        selectionsSoFar=[]
        for step in self.someOrganizer.steps :
            if step.isSelector : selectionsSoFar.append(step)
            elif nSelectionsPrinted<len(selectionsSoFar) and not self.compactOutput :
                self.printSteps(selectionsSoFar, printAll = self.compactOutput)
                nSelectionsPrinted = len(selectionsSoFar)
            if (step.name, step.title)==self.linYAfter : self.doLog = False
            for plotName in sorted(step.keys()) :
                if self.compactOutput and plotName not in self.whiteList : continue
                if any( re.match(pattern+'$',plotName) for pattern in self.blackList ): continue
                self.onePlotFunction(step[plotName])

        self.printCanvas("]")
        print self.pdfFileName, 'has been written'
        if self.latexYieldTable : self.printLatexYieldTable()
        print utils.hyphens

    def oneTable(self, f, columnSpecs = "", header = "", rows = []) :
        f.write(r'''
\begin{table}
\begin{tabular}{''')
        f.write(columnSpecs)
        f.write(r'''}
\hline\hline
''')
        f.write(header)
        f.write(r''' \\ \hline
''')
        for row in rows : f.write("%s%s"%(row,"\n"))
        f.write(r'''\hline\hline
\end{tabular}
\end{table}
''')

    def printLatexYieldTable(self, blackList = ["passFilter"]) :
        texFile = self.pdfFileName.replace(".pdf",".tex")
        f = open(texFile, "w")
        f.write(r'''
\documentclass[landscape]{article}
\usepackage[landscape]{geometry}
\begin{document}
''')

        #table of letter <--> cut name,desc
        filtered = []
        descDict = {}
        rows = []
        for key in sorted(self.cutDict.keys(), key = string.ascii_letters.index) :
            name,desc = self.cutDict[key]
            if any( re.match(pattern+'$', name) for pattern in self.blackList ) :
                filtered.append(key)
                continue
            for item in [name, desc] :
                if item.count("@") : print "WARNING: @ replaced by ! in %s"%item
            name2 = name.replace("@","!")
            desc2 = desc.replace("@","!")
            descDict[key] = r'\verb@%s@'%desc2
            rows.append( r'%s & \verb@%s@ & %s \\'%(key, name2, descDict[key]) )

        self.oneTable(f, columnSpecs = "llr", header = "letter & name & description", rows = rows)


        #tables of cut letter <--> yields; cut desc <--> yields
        for i in range(len(self.sampleList)) :
            if self.sampleList[i].count("@") : print "WARNING: @ replaced by ! in %s"%self.sampleList[i]
            self.sampleList[i] = self.sampleList[i].replace("@","!").lstrip().rstrip()
        names = r"@ & \verb@".join(self.sampleList)
        names = names.join([r"\verb@", "@"])

        rowsLettered = []
        rowsDescribed = []
        for key in sorted(self.yieldDict.keys(), key = string.ascii_letters.index) :
            if key in filtered : continue
            yields = self.yieldDict[key]
            for i in range(len(yields)) :
                if yields[i].count("@") : print "WARNING: @ replaced by ! in %s"%yields[i]
                yields[i] = yields[i].replace("@","!").lstrip().rstrip()
                
            yields = r"@ & \verb@".join(yields)
            yields = yields.join([r"\verb@", "@"])
            rowsLettered.append( r'%s & %s \\'%(key, yields) )
            rowsDescribed.append( r'%s & %s \\'%(descDict[key], yields) )

        self.oneTable(f, columnSpecs = "l"+"c"*len(self.sampleList), header = "letter & "+names, rows = rowsLettered)
        self.oneTable(f, columnSpecs = "l"+"c"*len(self.sampleList), header = "description & "+names, rows = rowsDescribed)

        f.write('''\end{document}''')
        f.close()
        print "The output file \""+texFile+"\" has been written."
        
    def printOnePage(self, name = "", tight = False, padNumber = None, alsoC = False) :
        fileName = "%s_%s.eps"%(self.pdfFileName.replace(".pdf",""),name)
        pad = self.canvas if padNumber is None else self.canvas.cd(padNumber)
        pad.Print(fileName)
        message = "The output file \"%s\" has been written."%fileName
        if alsoC :
            pad.Print(fileName.replace(".eps",".C"))
            print message.replace(".eps",".C")
            
        if not tight : #make pdf
            os.system("epstopdf "+fileName)
            os.system("rm       "+fileName)
        else : #make pdf with tight bounding box
            epsiFile = fileName.replace(".eps",".epsi")
            os.system("ps2epsi "+fileName+" "+epsiFile)
            os.system("epstopdf "+epsiFile)
            os.system("rm       "+epsiFile)

        print message.replace(".eps",".pdf")

    def individualPlots(self, plotSpecs, newSampleNames = {}, cms = True, preliminary = True, tdrStyle = True) :
        def goods(spec) :
            for item in ["stepName", "stepDesc", "plotName"] :
                if item not in spec : return

            histoList = []
            nMasters = [step.name for step in self.someOrganizer.steps].count("master")
            if nMasters!=2 : print "I have %d master step(s)."%nMasters
            
            for step in self.someOrganizer.steps :
                if (spec["stepName"], spec["stepDesc"]) not in [(step.name, step.title), (step.name,None)] : continue
                if spec["plotName"] not in step : continue
                histoList.append(step[spec["plotName"]])

            assert histoList,"Failed %s"%str(spec)
            histos = histoList[spec["index"] if "index" in spec else 0]
            if "sampleWhiteList" not in spec :
                return histos,None
            else :
                return histos,[not (sample["name"] in spec["sampleWhiteList"]) for sample in self.someOrganizer.samples]

        def onlyDumpToFile(histos, spec) :
            if "onlyDumpToFile" in spec and spec["onlyDumpToFile"] :
                rootFileName = self.pdfFileName.replace(".pdf","_%s.root"%spec["plotName"])
                f = r.TFile(rootFileName, "RECREATE")
                for h in histos :
                    h.Write()
                f.Close()
                print "The output file \"%s\" has been written."%rootFileName
                return True
            return False

        def rebin(h, spec) :
            if "reBinFactor" in spec :
                for histo in h :
                    if histo!=None : histo.Rebin(spec["reBinFactor"])
                
        def setTitles(h, spec) :
            if "newTitle" in spec :
                for histo in h :
                    histo.SetTitle(spec["newTitle"])

        def stylize(h) :
            for histo in h :
                histo.UseCurrentStyle()

        def setRanges(h, spec) :
            for item in ["xRange", "yRange"] :
                if item not in spec : continue
                for histo in h :
                    method = "Get%saxis"%item[0].capitalize()
                    getattr(histo, method)().SetRangeUser(*spec[item])

        print utils.hyphens
        if tdrStyle : self.setupTdrStyle()

        for spec in plotSpecs :
            histos,ignoreHistos = goods(spec)
            if histos==None : continue

            if onlyDumpToFile(histos, spec) : continue
            rebin(histos, spec)
            setRanges(histos, spec)
            setTitles(histos, spec)
            stylize(histos)

            individual = {"legendCoords": (0.55, 0.55, 0.85, 0.85),
                          "reverseLegend": False,
                          "stampCoords": (0.75, 0.5),
                          "ignoreHistos": ignoreHistos,
                          "newSampleNames" : newSampleNames,
                          "legendTitle" : ""
                          }
            for key in spec :
                if key in individual.keys()+["order"] :
                    individual[key] = spec[key]

            stuff,pads = self.onePlotFunction(histos, individual = individual)
            if ("stamp" not in spec) or spec["stamp"] :
                utils.cmsStamp(lumi = self.someOrganizer.lumi, cms = cms, preliminary = preliminary, coords = individual["stampCoords"])

            args = {"name":spec["plotName"],
                    "tight":False,#self.anMode
                    "alsoC":spec["alsoC"] if "alsoC" in spec else False,
                    }
            if "sampleName" in spec :
                sampleName = spec["sampleName"]
                assert sampleName in pads,str(pads)
                args["name"] += "_%s"%sampleName.replace(" ","_")
                args["padNumber"] = pads[sampleName]
                setTitles(histos, spec) #to allow for overwriting global title
            self.printOnePage(**args)
        print utils.hyphens

    def printCalculablesDetailed(self, blocks) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.35*text.GetTextSize())

        maxLensB = [max(len(b) for a,b,c in block) for block in blocks]
        stringBlocks = [["%s%s  %s"%(a,b.ljust(maxLenB),c) for a,b,c in block] for block,maxLenB in zip(blocks,maxLensB)]
        for iLine,line in enumerate(sum(stringBlocks,[])) :
            y=0.98 - 0.35*(iLine+0.5)/self.nLinesMax
            text.DrawTextNDC(0,y, line)
        return text
            
    def printCalculables(self, selectImperfect) :
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.45*text.GetTextSize())

        allCalcs = sum([s.keys() for s in self.someOrganizer.calculables], [])
        genuine = ((name,more,"") for name,more,cat in sorted(set(allCalcs)) if more and cat is "calc")

        def third(c) : return c[2]
        groups = dict((cat,[name for name,more,_ in group]) for cat,group in itertools.groupby(sorted(allCalcs, key=third) , key=third))
        cats = groups.keys()
        fake = conf.fakeString()
        imperfect = ( ( name,  more.replace(fake,""), '  '.join("%4d"%groups[key].count(name) for key in cats))
                      for name,more,cat in set(allCalcs)
                      if cat is 'fake' or cat is "calc" and not ("leaf" in groups and (bool(groups["leaf"].count(name))^bool(groups["calc"].count(name)))) )

        calcs = (([("Calculables",'(imperfect)','  '.join(cats)), ('','','')] + max( list(imperfect), [('','NONE','')])) if selectImperfect else \
                 ([("Calculables",'',''),                         ('','','')] + max( list(genuine), [('','NONE','')])) )

        if selectImperfect and (not list(imperfect)) and (not self.printImperfectCalcPageIfEmpty):
            return
        maxName,maxMore = map(max, zip(*((len(name),len(more)) for name,more,cat in calcs)))
        [text.DrawTextNDC(0.02, 0.98 - 0.4*(iLine+0.5)/self.nLinesMax, line)
         for iLine,line in enumerate("%s   %s   %s"%(name.rjust(maxName+2), more.ljust(maxMore+2), cat)
                                     for name,more,cat in calcs) ]
        return text
        
    def printTimeStamp(self) :
        text=r.TText()
        text.SetNDC()
        dateString="file created at ";
        tdt=r.TDatime()
        text.DrawText(0.1,0.1,dateString+tdt.AsString())
        return text

    def printSampleList(self, x, rows=[], header="", sigma=None):
        text = r.TLatex()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.38*text.GetTextSize())
        defSize = text.GetTextSize()

        rows = [("name", "nEventsIn", "weightIn", "lumi(/fb)", "xs(fb)")] + rows
        realRows = filter(lambda x: len(x[1]), rows)
        if len(realRows) == 1:
            return

        lengths = []
        for iColumn in realRows[0]:
            lengths.append([])

        for row in realRows:
            for iColumn in range(len(lengths)):
                width = len(row[iColumn])
                lengths[iColumn].append(width)

        for i in range(len(lengths)):
            lengths[i] = max(lengths[i])

        total = 5 + sum(lengths[:-1]) + (lengths[-1] if self.printXs else 0)
        if self.nColumnsMax < total:
            text.SetTextSize(defSize * self.nColumnsMax/(total + 0.0))

        y = 0.9
        dy = 0.55 / self.nLinesMax
        text.DrawLatex(x, y+dy, header)
        for iRow, row in enumerate(rows):
            fields = []
            for iColumn in range(len(row) - (0 if self.printXs else 1)):
                s = getattr(row[iColumn], "rjust" if iColumn else "ljust")(lengths[iColumn])
                fields.append(s)

            c = "  %s" % ("#kern[0.3]{#Sigma}" if (sigma and not iRow) else " ")
            line = c.join(fields)

            if row not in realRows:
                y -= dy
            if line.strip():
                text.DrawLatex(x, y, line)
                y -= dy
        return text

    def printNEventsIn(self):
        before, merged = self.someOrganizer.individualAndMergedSamples()
        b = self.printSampleList(0.02,
                                 sampleRows(before),
                                 header="individual samples",
                                 )
        m = self.printSampleList(0.52,
                                 sampleRows(merged),
                                 header="samples merged from at least 2 sources",
                                 sigma=True)
        return [b, m]  # gcruft

    def flushPage(self) :
        self.printCanvas()
        self.canvas.Clear()

    def printCanvas(self, extra = "") :
        self.pageNumber += 1
        if self.pageNumber>1 :
            text = r.TText()
            text.SetNDC()
            text.SetTextFont(102)
            text.SetTextSize(0.45*text.GetTextSize())
            text.SetTextAlign(33)
            text.DrawText(0.95, 0.03, "page %3d"%self.pageNumber if self.pageNumbers else ".")
        self.canvas.Print(self.pdfFileName+extra,('pdf ' if extra=='[' else 'Title:')+self.pdfOptions)
        self.pdfOptions = ''

    def printSteps(self, steps, printAll=False) :
        if printAll and len(steps)>self.nLinesMax : self.printSteps(steps[:1-self.nLinesMax],printAll)
        self.canvas.cd(0)
        self.canvas.Clear()
        
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.40*text.GetTextSize())

        pageWidth = 120
        nSamples = len(self.someOrganizer.samples) + len(self.foms)
        colWidth = min(25, pageWidth/nSamples)
        space = 1

        nametitle = "{0}:  {1:<%d}   {2}" % (3+max([len(s.name) for s in steps]))
        for i,step in enumerate(steps[-self.nLinesMax:]) :
            absI = i + (0 if len(steps) <= self.nLinesMax else len(steps)-self.nLinesMax)

            text.SetTextColor(self.rowColors[absI%len(self.rowColors)])
            letter = string.ascii_letters[absI]
            x = 0.02
            y = 0.98 - 0.34*(i+0.5+(absI/self.rowCycle) - ((absI-i)/self.rowCycle) )/self.nLinesMax

            nums = []
            ratios = [None]*len(self.samplesForRatios)
            for k,sample in zip(step.yields,self.someOrganizer.samples) :
                special = "lumi" in sample and not self.showErrorsOnDataYields
                s = utils.roundString(*k, width=(colWidth-space), noSci = self.noSci or special, noErr = special) if k else "-    "
                if sample["name"] in self.samplesForRatios : ratios[self.samplesForRatios.index(sample["name"])] = k
                nums.append(s.rjust(colWidth))

            if len(ratios)==2 and ratios[0] and ratios[1]:
                num = float(ratios[0][0])
                den = float(ratios[1][0])
                numUnc = float(ratios[0][1])
                denUnc = float(ratios[1][1])

                for fom in self.foms:
                    s = "-    "
                    if num and den:
                        value = fom["value"](num, den)
                        error = value*fom["uncRel"](num, den, numUnc, denUnc)
                        s = utils.roundString(value, error, width=(colWidth-space))
                    nums.append(s.rjust(colWidth))

            if step.name in ['master','label']: self.pdfOptions = step.title
            if step.name=='label' :
                text.SetTextColor(r.kBlack)
                font = text.GetTextFont()
                text.SetTextFont(62)
                label = "[  %s  ]"%step.title
                text.DrawTextNDC(0.01, y, label)
                text.DrawTextNDC(0.01, y-0.51, label )
                text.SetTextFont(font)
            else:
                text.DrawTextNDC(x, y-0.00, nametitle.format(letter, step.name, step.title ))
                text.DrawTextNDC(x, y-0.51, "%s: %s"%(letter, "".join(nums)))
                self.cutDict[letter] = (step.name, step.title)
                self.yieldDict[letter] = nums

            if absI > self.formerMaxAbsI :
                text.SetTextColor(r.kBlack)
                text.DrawTextNDC(0.008,y-0.00,'|')
                text.DrawTextNDC(0.008,y-0.51,'|')

        self.formerMaxAbsI = absI
        self.sampleList = [s["name"][:(colWidth-space)].rjust(colWidth) for s in self.someOrganizer.samples]
        if len(self.samplesForRatios)==2:
            for fom in self.foms:
                self.sampleList += (fom["label"](*self.sampleLabelsForRatios))[:(colWidth-space)].rjust(colWidth)
        text.SetTextColor(r.kBlack)
        text.DrawTextNDC(x, 0.5, "   "+"".join(self.sampleList))
        text.SetTextAlign(13)
        if self.someOrganizer.lumi is None:
            lumi = "(MC @ 1/pb; data not scaled)"
        else:
            lumi = "events / %.0f fb^{-1}" % (self.someOrganizer.lumi/1.0e3)
        text.DrawTextNDC(0.05, 0.03, lumi)
        self.flushPage()

    def getExtremes(self, dimension, histos, ignoreHistos) :
        globalMax = -1.0
        globalMin = 1.0e9

        for histo,ignore in zip(histos,ignoreHistos) :
            if ignore or (not histo) : continue
            if dimension==1 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    content = histo.GetBinContent(iBinX)
                    error   = histo.GetBinError(iBinX)
                    valueUp   = content + error
                    if valueUp>0.0 and valueUp>globalMax : globalMax = valueUp
                    if self.doLog and content>0 : globalMin = min(globalMin,content)
                    if not self.doLog : globalMin = min(globalMin,content-error)
            if dimension==2 :
                for iBinX in range(histo.GetNbinsX()+2) :
                    for iBinY in range(histo.GetNbinsY()+2) :
                        value = histo.GetBinContent(iBinX,iBinY)
                        if value>0.0 :
                            if value<globalMin : globalMin = value
                            if value>globalMax : globalMax = value                            
        return globalMin,globalMax

    def setRanges(self, histos, globalMin, globalMax) :
        for histo in histos :
            if not histo : continue
            if self.doLog :
                histo.SetMinimum(0.5*globalMin) if self.pegMinimum==None else histo.SetMinimum(self.pegMinimum)
                histo.SetMaximum(2.0*globalMax)
            else :
                histo.SetMaximum(1.1*globalMax)
                histo.SetMinimum(1.1*globalMin if globalMin<0 else 0)

    def prepareCanvas(self,histos,dimension) :
        self.canvas.cd(0)
        self.canvas.Clear()
        if dimension==1 :
            if self.plotRatios :
                split = 0.2
                self.canvas.Divide(1,2)
                self.canvas.cd(1).SetPad(0.01,split+0.01,0.99,0.99)
                self.canvas.cd(2).SetPad(0.01,0.01,0.99,split)
                #self.canvas.cd(2).SetTopMargin(0.07)#default=0.05
                #self.canvas.cd(2).SetBottomMargin(0.45)
                self.canvas.cd(1)
            else :
                self.canvas.Divide(1,1)
                if self.anMode : self.canvas.UseCurrentStyle()
        else :
            mx=1
            my=1
            while mx*my<len(histos) :
                if mx==my : mx+=1
                else :      my+=1
            self.canvas.Divide(mx,my)

    def plotEachHisto(self, dimension, histos, opts) :
        stuffToKeep = []
        legend = r.TLegend(*opts["legendCoords"])
        if opts["legendTitle"]:
            legend.SetHeader(opts["legendTitle"])
        stuffToKeep.append(legend)
        legendEntries = []
        if self.anMode :
            legend.SetFillStyle(0)
            legend.SetBorderSize(0)

        count = 0
        pads = {}
        for sample,histo,ignore in sorted( zip(self.someOrganizer.samples, histos, opts["ignoreHistos"]), key = lambda x: opts["order"].index(x[0]["name"]) ) :
            if ignore or (not histo) or (not histo.GetEntries()) : continue

            if "color" in sample :
                for item in ["Line", "Marker"] :
                    getattr(histo,"Set%sColor"%item)(sample["color"])
            for item in ["lineColor", "lineStyle", "lineWidth",
                         "markerStyle", "markerColor", "fillStyle", "fillColor"] :
                if item in sample : getattr(histo, "Set"+item.capitalize()[0]+item[1:])(sample[item])

            sampleName = opts["newSampleNames"].get(sample["name"], sample["name"])
            legendEntries.append( (histo, sampleName, sample.get("legendOpt", "lpf")) )
            if dimension==1 :
                stuffToKeep += self.plot1D(histo, count,
                                           goptions = sample.get("goptions", ""),
                                           double = sample.get("double", ""))
            elif dimension==3 : continue
            elif dimension==2 and self.omit2D : continue
            elif dimension==2 :
                self.plot2D(histo, count, sampleName, stuffToKeep)
                pads[sampleName] = 1+count
            else :
                print "Skipping histo",histo.GetName(),"with dimension",dimension
                continue
            count+=1
        if dimension==1 :
            if opts["reverseLegend"] : legendEntries.reverse()
            for e in legendEntries : legend.AddEntry(*e)
            legend.Draw()
        return count,stuffToKeep,pads

    def plotRatio(self,histos,dimension) :
        numLabel,denomLabel = self.sampleLabelsForRatios
        numSampleName,denomSampleNames = self.samplesForRatios
        if type(denomSampleNames)!=list: denomSampleNames = [denomSampleNames]

        ratios = []
        try:
            numHisto = histos[self.someOrganizer.indexOfSampleWithName(numSampleName)]
            denomHistos = map(lambda name: histos[self.someOrganizer.indexOfSampleWithName(name)], denomSampleNames)
        except TypeError:
            return ratios

        if not numHisto : return ratios

        same = ""
        for denomHisto in denomHistos :
            ratio = None
            if numHisto and denomHisto and numHisto.GetEntries() and denomHisto.GetEntries() :
                ratio = utils.ratioHistogram(numHisto,denomHisto)
                ratio.SetMinimum(0.0)
                ratio.SetMaximum(2.0)
                ratio.GetYaxis().SetTitle(numLabel+"/"+denomLabel)
                self.canvas.cd(2)
                self.adjustPad(r.gPad, self.anMode)
                r.gPad.SetGridy()
                ratio.SetStats(False)
                ratio.GetXaxis().SetLabelSize(0.0)
                ratio.GetXaxis().SetTickLength(3.5*ratio.GetXaxis().GetTickLength())
                ratio.GetYaxis().SetLabelSize(0.2)
                ratio.GetYaxis().SetNdivisions(502,True)
                ratio.GetXaxis().SetTitleOffset(0.2)
                ratio.GetYaxis().SetTitleSize(0.2)
                ratio.GetYaxis().SetTitleOffset(0.2)
                if len(denomHistos)==1: ratio.SetMarkerStyle(numHisto.GetMarkerStyle())
                color = numHisto.GetLineColor() if len(denomHistos)==1 else denomHisto.GetLineColor()
                ratio.SetLineColor(color)
                ratio.SetMarkerColor(color)
                ratio.Draw(same)
                same = "same"
            else :
                self.canvas.cd(2)
            ratios.append(ratio)
        return ratios

    def onePlotFunction(self, histos, individual = {}) :
        dimension = self.dimensionOfHisto(histos)
        self.prepareCanvas(histos, dimension)

        options = {"newSampleNames": {},
                   "legendCoords": (0.86, 0.60, 1.00, 0.10),
                   "reverseLegend": False,
                   "ignoreHistos": [],
                   "order" : [ss["name"] for ss in self.someOrganizer.samples],
                   "legendTitle" : ""
                   }
        options.update(individual)
        if not options["ignoreHistos"] : options["ignoreHistos"] = [False]*len(histos)
        
        if self.shiftUnderOverFlows : self.doShiftUnderAndOverflows(dimension, histos, self.dontShiftList)
        self.setRanges(histos, *self.getExtremes(dimension, histos, options["ignoreHistos"]))

        count,stuffToKeep,pads = self.plotEachHisto(dimension, histos, options)
            
        if self.plotRatios and dimension==1 :
            ratios = self.plotRatio(histos,dimension)
        self.canvas.cd(0)
        if count>0 and not individual :
            self.printCanvas()
        if individual :
            return stuffToKeep,pads
        if dimension==2 and self.dependence2D :
            depHistos = tuple(utils.dependence(h) for h in histos)
            self.prepareCanvas(depHistos, dimension)
            count,stuffToKeep,pads = self.plotEachHisto(dimension, depHistos, options)
            self.canvas.cd(0)
            if count>0 : self.printCanvas()

    def plot1D(self, histo, count, goptions = "", double = False) :
        keep = []
        self.adjustPad(r.gPad, self.anMode)

        if count==0 :
            if not self.anMode : histo.GetYaxis().SetTitleOffset(1.25)
            if self.doLog : r.gPad.SetLogy()
        else :
            goptions += "same"

        histo.SetStats(self.showStatBox)
        histo.Draw(goptions)

        if double :
            histo2 = histo.Clone(histo.GetName()+"_cloneDouble")
            histo2.SetFillStyle(0)
            histo2.Draw("histsame")
            keep.append(histo2)

        r.gStyle.SetOptFit(0)
        if self.fitFunc:
            func = self.fitFunc(histo)
            keep.append(func)

        #move stat box
        r.gPad.Update()
        tps=histo.FindObject("stats")
        keep.append(tps)
        if tps :
            tps.SetTextColor(histo.GetLineColor())
            tps.SetX1NDC(0.86)
            tps.SetX2NDC(1.00)
            tps.SetY1NDC(0.70)
            tps.SetY2NDC(1.00)
        return keep

    def lineDraw(self, name, offset, slope, histo, color = r.kBlack, suffix = "") :
        if name not in histo.GetName() : return None
        axis = histo.GetXaxis()
        func = r.TF1(name+suffix,"(%g)+(%g)*x"%(offset,slope),axis.GetXmin(),axis.GetXmax())
        func.SetLineWidth(1)
        func.SetLineColor(color)
        func.Draw("same")
        return func
        
    def plot2D(self,histo,count,sampleName,stuffToKeep) :
    	yx=r.TF1("yx","x",histo.GetXaxis().GetXmin(),histo.GetXaxis().GetXmax())
    	yx.SetLineColor(r.kBlack)
    	yx.SetLineWidth(1)
    	yx.SetNpx(300)
    	
    	self.canvas.cd(count+1)
        self.adjustPad(r.gPad, pushLeft = self.pushLeft )
        
    	histo.GetYaxis().SetTitleOffset(1.2)
    	oldTitle=histo.GetTitle()
    	newTitle=sampleName if oldTitle=="" else sampleName+"_"+oldTitle
    	histo.SetTitle(newTitle)
    	histo.SetStats(False)
    	histo.GetZaxis().SetTitleOffset(1.3)
        if self.doLog : r.gPad.SetLogz()

        histo.Draw("colz" if self.doColzFor2D else "")

        #plot-specific stuff
        if "deltaHtOverHt_vs_mHtOverHt" in histo.GetName() \
               or "deltaHtOverHt_vs_metOverHt" in histo.GetName() :
            histo.GetYaxis().SetRangeUser(0.0,0.7)
            funcs=[
                self.makeAlphaTFunc(0.55),
                self.makeAlphaTFunc(0.50),
                self.makeAlphaTFunc(0.45)
                ]
            for func in funcs : func.Draw("same")
            stuffToKeep.extend(funcs)
        elif self.drawYx :
            yx.Draw("same")
            stuffToKeep.append(yx)

        stuffToKeep.append( self.lineDraw(name = "alphaTMet_vs_alphaT",      offset = 0.0,   slope = 1.0,   histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "alphaTMet_zoomvs_alphaT",  offset = 0.0,   slope = 1.0,   histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "mhtVsPhotonPt",            offset = 0.0,   slope = 1.0,   histo = histo) )

        #loose
        stuffToKeep.append( self.lineDraw(name = "jurassicEcalIsolation",    suffix = "loose", offset = 4.2,   slope = 0.006,  histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "towerBasedHcalIsolation",  suffix = "loose", offset = 2.2,   slope = 0.0025, histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "hadronicOverEm",           suffix = "loose", offset = 0.05,  slope = 0.0,    histo = histo) )
        stuffToKeep.append( self.lineDraw(name = "hollowConeTrackIsolation", suffix = "loose", offset = 3.5,   slope = 0.001,  histo = histo) )

        #tight
        stuffToKeep.append( self.lineDraw(name = "jurassicEcalIsolation",    suffix = "tight", offset = 4.2,   slope = 0.006,  histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "towerBasedHcalIsolation",  suffix = "tight", offset = 2.2,   slope = 0.0025, histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "hadronicOverEm",           suffix = "tight", offset = 0.05,  slope = 0.0,    histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "hollowConeTrackIsolation", suffix = "tight", offset = 2.0,   slope = 0.001,  histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "sigmaIetaIetaBarrel",      suffix = "tight", offset = 0.013, slope = 0.0,    histo = histo, color = r.kBlue) )
        stuffToKeep.append( self.lineDraw(name = "sigmaIetaIetaEndcap",      suffix = "tight", offset = 0.030, slope = 0.0,    histo = histo, color = r.kBlue) )
##############################
