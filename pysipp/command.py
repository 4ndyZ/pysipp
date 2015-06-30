'''
Command string rendering
'''
import string
from distutils import spawn
from copy import copy


def iter_format(item):
    return string.Formatter().parse(item)


class CmdStr(object):
    '''Build a command string from an iterable of format string tokens
    '''
    def __init__(self, program, template):
        self.prog = program
        self.template = tuple(template)  # list of tokens
        self._params = set()
        for item in self.template:
            for _, name, fspec, conversion in iter_format(item):
                self._params.add(name)
                self.__dict__[name] = None
        self._init = True  # lock attribute creation

    def render(self):
        # build a content map of format string 'fields' to values
        content = {}
        for key in self._params:
            value = self.__dict__[key]
            if value is not None:
                content[key] = value

        # filter to tokens with assigned values
        tokens = []
        for item in self.template:
            fields = set()
            for _, name, fspec, conversion in iter_format(item):
                if name:
                    fields.add(name)
                else:
                    tokens.append(item)

            # print("fields '{}'".format(fields))
            # print("content '{}'".format(content))
            if all(field in content for field in fields):
                # only accept tokens for which we have all field values
                tokens.append(item)

        return ' '.join([self.prog] + tokens).format(**content)

    def __setattr__(self, key, value):
        # immutable after instantiation
        if getattr(self, '_init', False) and key not in self.__dict__:
            raise AttributeError(key)
        object.__setattr__(self, key, value)

    def copy(self):
        return copy(self)


def SippCmd(spec, fields=None):
    '''A command string renderer for `sipp`.

    Given the provided `spec` create a renderer type.
    '''
    sipp = spawn.find_executable('sipp')
    return CmdStr(sipp, spec)  # + tuple(fields) if fields else ())