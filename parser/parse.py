#############################################################################
##
##  KLA parser
##
## Copyright (C) 2015 Kollective Technology.  All rights reserved.
##
#############################################################################

__author__ = 'john'

import logging, os, re
log = logging.getLogger('parser.parse')

from parser.patternManager import PatternSpec
from parser.namespace import NameSpace

class ParseTree(NameSpace):
    "initial result of a parse, a structured namespace of all tasks containing extracted log field entries"

    def __init__(self, **kwargs):
        super(NameSpace, self).__setattr__('_watchedFields',  {})
        super(ParseTree, self).__init__(auto_add_levels=True)

    def watch(self, name, callback):
        "watch for assignments to named field in tree"
        super(NameSpace, self).__getattribute__('_watchedFields')[name] = callback

    def unwatch(self, name):
        "stop watching for changes on named field"
        del super(NameSpace, self).__getattribute__('_watchedFields')[name]

    def __setitem__(self, key, val):
        "override root namespace assigner to check for watched fields"
        callback = super(NameSpace, self).__getattribute__('_watchedFields').get(key)
        if callback:
            callback(self, key, val)
        super(ParseTree, self).__setitem__(key, val)

class Parser(object):
    "client log parser, instances maintain parsing state & parse tree for a given log file"

    def __init__(self, logfileName, patternDef):
        self.logfileName = logfileName
        self.parseTree = ParseTree()
        self.nodeMeta = {} # holds parseTree node metadata keyed by full node pathname
        self.log = None
        # each parser has it's own "compiled" pattern struct as it may contain logfile-specific
        #  {{var}} variable expansions
        self.patternSpec = PatternSpec(self, patternDef)

    def watchField(self, pattern, field):
        "sets a watchpoint on the given parseTree field for the given pattern"
        self.parseTree.watch(field, self._curryWatch(pattern))

    def _curryWatch(self, pattern):
        "generates a curried watchField callback function applied to the given pattern"
        def fieldChanged(parseTree, key, val):
            pattern.fieldChanged(parseTree, key, val)
        return fieldChanged

    def parse(self):
        "perform a parse on my logfile"
        # grab log copy
        with open(self.logfileName) as logfile:
            self.log = logfile.read()
        # read logfile line-by-line, match against pattern-spec
        with open(self.logfileName) as logfile:
            lineNo = 0
            line = logfile.readline()
            while line:
                line = line.strip()
                self.patternSpec.match(line, lineNo)
                line = logfile.readline()
                lineNo += 1
        # clean up
        self.patternSpec.endParse(lineNo)
        self.optimizeParseTree()

    ordinalRE = re.compile(r'\d\d\d')

    def optimizeParseTree(self):
        "optimize parse-tree - remove unneeded ordinal levels, turn ordinal-indexes into lists"
        def optimize(subtree):
            keys = subtree.keys()
            # look for keys that are 3-digit ordinals
            if keys:
                if all(self.ordinalRE.match(k) for k in keys):
                    if False and len(keys) == 1:
                        # single entry, elide level
                        return optimize(subtree[list(keys)[0]])
                    else:
                        # turn multi-entry into  list
                        return [optimize(subtree[k]) for k in sorted(keys)]
                else:
                    # non-ordinal index level, iterate keys & optimize subtrees
                    for k, v in subtree.items():
                        if isinstance(v, NameSpace):
                            subtree[k] = optimize(v)
                    return subtree
        self.parseTree = optimize(self.parseTree)

if __name__ == "__main__":

    from parser.patterns.clientLog import patternDef
    import pprint, json
    #
    p = Parser(os.path.expanduser("~/Dropbox/Documents/Kontiki 2014/debugging/Lloyds/pDPTu3_AT2k1-20151125-204429/error2.log"), patternDef)
    p.parse()
    #
    #pprint.pprint(p.parseTree, width=160)
    print(json.dumps(p.parseTree, indent=2, sort_keys=True))


