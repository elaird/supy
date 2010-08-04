-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

----------------
| Instructions |
----------------
0) Set up pyROOT:
- use a CMSSW area:  cd /somewhere/CMSSW_3_7_0_patch4/src && cmsenv
- or see note (A)

1) Check out the code:
cvs co -d supy -r V8-3 UserCode/elaird/supy

2) modify $PYTHONPATH so that supy modules can be imported:
- cd supy
- source supyenv.sh

3) Run it!
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
