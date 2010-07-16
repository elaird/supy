-----------
| License |
-----------
GPLv3

----------------
| Instructions |
----------------
0) Set up pyROOT:
- use a CMSSW area:  cd /somewhere/CMSSW_3_7_0_patch4/src && cmsenv
- or see note (A)

1) Check out the code:
cvs co -d supy -r V6-0 UserCode/elaird/supy

2) Define some samples you would like to analyze:
- Edit samples.py (add a function to sampleDictionaryHolder).

3) Define a "cut flow":
- Edit lists.py (add a function to listDictionaryHolder).

4) Define an analysis:
- See analyses/example.py for an example.

5) modify $PYTHONPATH so that supy modules can be imported:
- cd supy
- source supyenv.sh

6) Run it!
- python analyses/example.py

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
