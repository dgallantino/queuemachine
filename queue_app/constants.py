def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)

class _IDX(object):
    @constant
    def ORG():
        return 'Organization'
    @constant
    def BOOTH():
        return 'CounterBooth'

class _TEMPLATE(object):
    @constant
    def QUEUES():
        return 'Queues'
    @constant
    def QUEUE():
        return 'Queue'
    @constant
    def SERVICES():
        return 'Services'
    @constant
    def SERVICE():
        return 'Service'
    @constant
    def ORGS():
        return 'Organizations'
    @constant
    def BOOTHS():
        return 'CounterBooths'
    @constant
    def BOOTH():
        return 'CounterBooth'

class _LANG(object):
    @constant
    def ID():
        return 'id'
    @constant
    def EN():
        return 'en'

LANG = _LANG()
IDX = _IDX()
TEMPLATE = _TEMPLATE()
