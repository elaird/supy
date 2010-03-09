-----------
| License |
-----------
GPLv3

----------------
| Instructions |
----------------
0) Set up pyROOT:
- use a CMSSW area:  cd /somewhere/CMSSW_3_4_1/src && cmsenv
- or see note (A)

1) Check out the code:
cvs co -d supy UserCode/SusyCAFmacro/standalone/supy

2) Define some samples you would like to analyze:
- Edit samples.py (add a function and call it from buildSampleDictionary).

3) Define a "cut flow":
- Edit lists.py (add a function and call it from buildListDictionary).

4) Define an analysis:
- Edit analyses.py (add a function and call it from buildAnalysisDictionary).

5) Specify an analysis to run:
- Edit go.py to specify the function you defined in step 4.

6) Run it!
- There are two possible ways:
  (a) ./go.py (if this fails, type "chmod +x go.py")
  (b) python go.py

- There are four commonly used arguments: "loop", "plot", "prof", and "-b".
E.g.: "./go.py loop" will loop over the events in the samples and output histograms in root files.
      "./go.py loop plot" will do the above loop, and, when finished, plot the histograms and save the plots to a ps file.
      "./go.py loop plot -b" will do the above in batch mode (i.e., no graphics will be displayed).
      "./go.py plot -b" will make the ps file in batch mode (without looping over the events again).
      "./go.py prof -b" will profile the code in batch mode.  You can view the results by running "python viewTheProfile.py".

---------
| Notes |
---------
(A) ROOT and python are required; CMSSW is not.  These are useful pages for setting up and learning pyROOT:
http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter
http://wlav.web.cern.ch/wlav/pyroot/

(B) A std::vector<bool> stored in a TTree is not yet supported.

--------
| Bugs |
--------
Please send bug reports to edward.laird@cern.ch.
