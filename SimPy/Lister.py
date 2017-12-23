# coding=utf-8
"""
Pretty-printer for SimPy class objects

"""
from builtins import object
class Lister(object):

    indent = 0

    def __str__(self):
        Lister.indent += 1
        if Lister.indent > 3:
            # In case of recursion, avoid infinite loop
            result = ' ... '
        else:
            result = '< Instance of %s, id %s:\n%s%s>' % (
                self.__class__.__name__,
                id(self),
                self.attrnames(),
                '\t' * (Lister.indent - 1),
            )
        Lister.indent -= 1
        return result

    def attrnames(self):
        result = ''
        for attr in self.__dict__:
            # Ignore built-in and private attributes
            if not (attr[:2] == '__' or attr[0] == '_'):
                result += '\t' * Lister.indent + '.%s=%s\n' % (attr,
                        self.__dict__[attr])
        return result

    def __repr__(self):
        return self.__str__()
