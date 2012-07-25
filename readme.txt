-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

---------------
| Quick Start |
---------------
1) Set up pyROOT:
- use a CMSSW area: cd /somewhere/CMSSW_4_2_8/src && cmsenv

2) Clone the repository:
git clone git://github.com/elaird/supy.git
#  or, if you have forked it,
git clone git://github.com/your_username/supy.git
cd supy

3) Add the directory containing supy/ to your PYTHONPATH; optionally
# add the supy/bin directory to your PATH:
PYTHONPATH=$PYTHONPATH:`pwd`/..
PATH=$PATH:`pwd`/bin

4) Run the tests and/or example :
./bin/supy-test
./bin/supy examples/one.py --loop 1

5) Write your own configuration.py and analysis.

---------------------
| Brief Description |
---------------------
To be written.

----------------
| Dependencies |
----------------
ROOT (>=5.27.06) and python (2.x, x>=6) are required; CMSSW is not required.  
These are useful pages for setting up and learning pyROOT:
http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter
http://wlav.web.cern.ch/wlav/pyroot/

- If afs is mounted on your machine, you could use something like
this: https://github.com/elaird/ra1stats/blob/master/env.sh

-----------
| Gotchas |
-----------
- TTrees with multiple leaves per branch are not yet supported.

- pyROOT does not support leaves whose names collide with the names of
  TChain member functions

- Creating a Lorentz vector every event is slow.  As a workaround, use
  utils.LorentzV (see calculables.Jet.SumP4 for an example).

- Iterating through a std::map<string, bool> is slow.  Consider using
  a cache (see steps.Trigger.Counts for an example).

--------
| Bugs |
--------
Please report problems at https://github.com/elaird/supy/issues
