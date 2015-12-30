#############################################################################
##
##  KLA parsing patterns and pattern-manager
##
## Copyright (C) 2015 Kollective Technology.  All rights reserved.
##
#############################################################################

__author__ = 'john'

import logging
log = logging.getLogger('parser.patternManager')

import re
from collections import defaultdict

from parser.namespace import NameSpace

class Pattern(object):
    "compiled KLA pattern spec"

    def __init__(self, parser, regexp, taskName, isStart=False, isEnd=False):
        self.regexp = regexp
        self.taskName = taskName
        self.isStart = isStart
        self.isEnd = isEnd
        self.compiledRexep = self.fields = self.watchFields = None
        self.compile(parser)

    def compile(self, parser):
        "(re)compile my regexp"
        # reset field tracking
        self.fields, self.watchFields = [], {}
        # record all variable sub-patterns
        for m in re.finditer(r'\{\{(?P<field>[a-zA-Z0-9_\.]+)\}\}', self.regexp):
            field = m.group('field')
            self.watchFields[field] = ''
            parser.watchField(self, field)
        # map dotted field names to __-separated to be valid IDs
        self.mappedRegexp = ''
        name = False
        for s in re.split('(\\(\\?P\\<)|(>)|(\\(\\?P\\=)|(\))', self.regexp):
            if s:
                if name:
                    self.fields.append(s)
                    s = s.replace('.', '__')
                    name = False
                elif s == '(?P<':
                    name = True
                self.mappedRegexp += s

    def fieldChanged(self, parseTree, field, val):
        "handle notification that a watched field value is changing"
        self.watchFields[field] = re.escape(str(val))

    def match(self, line):
        ""
        if not self.compiledRexep:
            # compile it on demand, first expand field vars
            expandedRegexp = self.mappedRegexp
            for field, val in self.watchFields.items():
                expandedRegexp = expandedRegexp.replace('{{%s}}' % field, val)
            self.compiledRexep = re.compile(expandedRegexp)
        #
        return self.compiledRexep.match(line)

class Task(object):
    "represents an extracted task instance, maintains parsing state-machine for the task"

    def __init__(self, name, ordinal, indexFields, patternSpec):
        print("creating task", name)
        self.name = baseName = name
        self.ordinal = ordinal
        self.indexFields = indexFields
        self.parent = None
        self.children = []
        # find & wire in parent task if any
        if '.' in name:
            path = name.split('.')
            parentName = '.'.join(path[:-1])
            baseName = path[-1]
            parent = patternSpec.tasks.get(parentName)
            if parent:
                print("  wire parent", parentName)
                self.parent = parent
                parent.addChild(self)
            else:
                baseName = name
        # make the parseTree path-prefix
        self.pathPrefix = self.parent.pathPrefix if self.parent else ""
        self.pathPrefix += "%s.%03d." % (baseName, ordinal)
        print("  pathPrefix", self.pathPrefix)

    def addChild(self, child):
        "add child task"
        self.children.append(child)

    def removeChild(self, child):
        "remove child task"
        if child in self.children:
            self.children.remove(child)


class PatternSpec(object):
    "holds a fully-compiled set of patterns for a particular parser instance"

    def __init__(self, parser, patternDef):
        self.parser = parser
        self.parseTree = parser.parseTree
        self.nodeMeta = parser.nodeMeta
        self.tasks = {}
        self.taskOrdinal = defaultdict(int)
        self.indexFields = {}
        self.patterns = []
        self.patternDef = patternDef
        self.compile()

    def compile(self):
        "compile a KLA pattern definition into internal parsing structures"

        # {
        #     "startup.init": {  # label names task (or dotted-pathname subtask), multiple tasks can have matching patterns
        #         "prefix": r'aaaa',  # common prefix for patterns in this task
        #         "start": [ r'xxxxxx', r'yyyyyy', ],   # alternate start patterns (optional, if not present all matching are in the singleton task)
        #         "end":  [ r'xxxxxx', r'yyyyyy', ],   # alternate end patterns (optional)
        #         "subtasks": {
        #         },
        #         "patterns": [ r'xxxxxx', r'yyyyyyy',
        #             r'...(?P<x.y.z>...)...',  # named subpatterns extracted to fields under task, '.' are structure levels in the extract
        #                                       # field namespace (they are converted internally to '__' to be valid re group names)
        #                                       # field names beginning with '.' are absolute, those without are relative to current task
        #             r'...{{x.y.z}}...' ],  # {{}} bounded subpatterns match contents of named field in parse namespace
        #         "indexFields": [ 'thread', moid' ],   # list of fields that index this task in presence of multiple task instances
        #     },
        #     ...
        # }

        commonPrefix = self.patternDef.get("prefix", r'')
        def compileTasks(taskDict, taskNamePrefix=""):
            for taskName, defn in taskDict.items():
                # grab & compile all patterns
                taskName = taskNamePrefix + taskName
                taskPrefix = commonPrefix + defn.get("prefix", r'')
                for k in ("start", "end", "patterns"):
                    for pat in defn.get(k, []):
                        self.patterns.append(Pattern(self.parser, taskPrefix + pat, taskName, isStart=(k == "start"), isEnd=(k == "end")))
                # record index spec
                self.indexFields[taskName] = defn.get("indexFields", [])
                # recurse into any subtasks
                subtasks = defn.get("subtasks")
                if subtasks:
                    compileTasks(subtasks, taskNamePrefix=taskName + ".")
        compileTasks(self.patternDef["tasks"])

    def match(self, line, lineNo):
        "match line against my patterns"
        # print("\n\n---------\n", line)
        endTask = None
        for p in self.patterns:  # hey, optimize this into a single or-compounded re
            m = p.match(line)
            if m:
                print("matched", p.taskName, line)
                # match, update task state & parse-tree
                # grab current task for this pattern, bump if task-start pattern
                taskName = p.taskName
                task = self.tasks.get(taskName)
                if task and p.isStart:
                    self.resetTaskTree(task)
                if not task or p.isStart:
                    self.tasks[taskName] = task = Task(taskName, self.taskOrdinal[taskName], self.indexFields[taskName], self)
                    self.nodeMeta[task.pathPrefix + 'startLineNo'] = lineNo
                    self.taskOrdinal[taskName] += 1
                #print("  match ", taskName, "ordinal", task.ordinal, p.isStart, p.isEnd)
                # insert fields into parse-tree
                for field, val in m.groupdict().items():
                    # figure fully-qualified parseTree pathname
                    pathname = field[1:] if field.startswith('.') else task.pathPrefix + field
                    if field in task.indexFields:
                        self.nodeMeta[task.pathPrefix + 'index'] = val
                    try:
                        v = float(val)  # try to convert to a number
                        val = v if '.' in val or 'e' in val else int(v)
                    except:
                        pass
                    self.parseTree[pathname] = val
                    #print("    setting", pathname, "to", val)
                # signal close out current task if task-end pattern found
                if p.isEnd:
                    endTask = task
        if endTask:
            self.nodeMeta[endTask.pathPrefix + 'endLineNo'] = lineNo
            self.resetTaskTree(endTask)

    def resetTaskTree(self, task):
        "reset the task tree under given task"
        print("  resetting task tree", task.name)
        # import pprint
        # pprint.pprint(self.tasks, width=160)
        def _reset(task):
            for c in task.children:
                if c.children:
                    _reset(c)
                del self.tasks[c.name]
            del self.tasks[task.name]
        _reset(task)
        if task.parent:
            task.parent.removeChild(task)

    def endParse(self, lastLineNo):
        "clean up at end of parse"
        # close out any still open tasks
        for t in self.tasks.values():
            self.parseTree[t.pathPrefix + 'endLineNo'] = lastLineNo


# class PatternManager(object):
#     """Manages the KLA pattern library"""
#
#     def __init__(self):
#         pass
#
#     def compileSpec(self, patternSpec):
#         "compile a KLA pattern spec into internal parsing structures"
#
#         # {
#         #     "startup.init": {  # label names task (or dotted-pathname subtask), multiple tasks can have matching patterns
#         #         "start": [ r'xxxxxx', r'yyyyyy', ],   # alternate start patterns (optional, if not present all matching are in the singleton task)
#         #         "end":  [ r'xxxxxx', r'yyyyyy', ],   # alternate end patterns (optional)
#         #         "patterns": [ r'xxxxxx', r'yyyyyyy',
#         #             r'...(?P<x.y.z>...)...',  # named subpatterns extracted to fields under task, '.' are structure levels in the extract
#         #                                       # field namespace (they are converted internally to '__' to be valid re group names)
#         #             r'...{{x.y.z}}...' ],  # {{}} bounded subpatterns match contents of named field in parse namespace
#         #         "indexFields": [ 'thread', moid' ],   # list of fields that index this task in presence of multiple task instances
#         #     },
#         #     ...
#         # }
#
#         for taskName, spec in patternSpec.items():
#
# # instantiate manager singleton
# patternManager = PatternManager()

# class PluginManager(object):
#
#     def plugins(self, type):
#         "iterator over available plugins of the given type, yields modules with selected type metadata global"
#         # 'type' for now names sub-directory in plugins directory to scan
#         for root, dirs, files in os.walk(join(self.pluginPath, type)):
#             for fn in files:
#                 if fn.endswith('.py'):
#                     try:
#                         pkg_path = '%s.%s.' % (self.packageNameForPath(root), fn[:-3])
#                         meta = import_python_pathname(pkg_path + 'PLUGIN_META')
#                         plugin_class = import_python_pathname(pkg_path + meta['class'])
#                         # yield plugin main class which should have bound the PLUGIN_META to it's 'meta' class var
#                         yield plugin_class
#                     except:
#                         #log.warn(sys.exc_info())
#                         # ignore modules without PLUGIN_META['type'] of the desired type
#                         pass
#
#     @property
#     def pluginPath(self):
#         "return path to plugins tl directory - for now the plugins package inside astro-cat/app"
#         return os.path.dirname(os.path.abspath(__file__))
#
#     def packageNameForPath(self, path):
#         "construct an importable dotted-pathname for the given path directory"
#         plugin_subpath = self.pluginPackage.replace('.', '/')
#         return path[path.find(plugin_subpath):].replace('/', '.')
#
#     @property
#     def pluginPackage(self):
#         "return package pathname of plugins package - for now this package app.plugins"
#         return __package__
#
# # module-global loading
# def import_python_pathname(pathname):
#     "import a python global from its import pathname"
#     mod, sep, globalname = pathname.rpartition('.')
#     modpath, sep, globalmod = mod.rpartition('.')
#     return getattr(getattr(__import__(modpath, fromlist=(str(globalmod),)), globalmod), globalname)
