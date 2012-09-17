#!/usr/bin/env pypy-cint
import sys,ROOT as r
print sys.executable
print sys.version
print r.module.__file__
r.gROOT.SetStyle("Plain")
print r.kBlack
