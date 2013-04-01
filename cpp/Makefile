
HEADERS      = SusyNt.h
SOURCES      = SusyNt.cxx
ROOTCINT     = rootcint
ROOTCONFIG   = root-config
ROOTCXXFLAGS = $(shell $(ROOTCONFIG) --cflags)
ROOTLIBS     = $(shell $(ROOTCONFIG) --libs) -lTreePlayer
ROOTINC      = $(shell $(ROOTCONFIG) --incdir)
ROOTLDFLAGS  = $(shell $(ROOTCONFIG) --ldflags)

CXXFLAGS = -O2 -Wall -fPIC $(INC_EXTRA) $(ROOTCXXFLAGS)

ROOTCONFIG   = root-config

all: libSusy.so

SusyDict.cxx: $(HEADERS) Linkdef.h
	rootcint -f $@ -c $(CXXFLAGS) -p $^

libSusy.so: SusyDict.cxx $(SOURCES)
	g++ -shared -o$@ $(ROOTLDFLAGS) $(CXXFLAGS) -I$(ROOTINC) $^

clean:
	rm -f *.o
	rm -f SusyDict.*
	rm -f libSusy.so
