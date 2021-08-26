"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

# def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
#    """
#    called in lockstring with myfalse().
#    A simple logger that always returns false. Prints to stdout
#    for simplicity, should use utils.logger for real operation.
#    """
#    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
#    return False

def discovered(accessing_obj, accessed_obj, *args, **kwargs):
    try:
        knownBy = accessed_obj.db.knownBy
        if accessing_obj in knownBy:
            return True
        else:
            return False
    except:
        return False


def canBeSeen(accessing_obj, accessed_obj, *args, **kwargs):
    if accessed_obj.access(accessing_obj, "view"):
        return True
    else:
        return False

def callableWhenHidden(accessing_obj, accessed_obj, *args, **kwargs):
    try:
        val = accessed_obj.db.callableWhenHidden
        if val:
            return True
        else:
            return False
    except:
        return False
    return False
