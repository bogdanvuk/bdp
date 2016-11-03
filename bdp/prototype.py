import inspect
import types

def _getattr(obj, name):
    try:
        return object.__getattribute__(obj, name)
    except AttributeError:
        return None

def _setattr(obj, name, val):
    object.__setattr__(obj, name, val)

def _proto_getattr(obj, name):
    val = _getattr(obj, name)
    if val is None:
        parent = _getattr(obj, '__proto__')
        try:
            val = getattr(parent, name)
        except AttributeError:
            return None
        # val = _getattr(parent, name)
    return val

class PrototypeMetaClass(type):
    def __repr__(cls):
        return "<constructor '%s'>" % cls.__name__

class Prototype:
    __metaclass__ = PrototypeMetaClass
    _prototype = None

    def __init__(self):
        self.__proto__ = self._prototype
        self._constructor = self.__class__

    def __getattribute__(self, name):
        val = _proto_getattr(self, name)
        if isinstance(val, property) and val.fget:
            get = types.MethodType(val.fget, self)
            return get()
        elif inspect.isfunction(val):
            func = types.MethodType(val, self)
            return func
        else:
            return val

    def __setattr__(self, name, val):
        # if not isinstance(val, property):
        #     _val = _proto_getattr(self, name)
        #     if isinstance(_val, property) and _val.fset:
        #         _val.fset(self, val)
        #         return
        _setattr(self, name, val)

    def __delattr__(self, name):
        val = _proto_getattr(self, name)
        if isinstance(val, property) and val.fdel:
            val.fdel(self)
        else:
            object.__delattr__(self, name)

Prototype._prototype = Prototype()

def constructor(func):
    ret = type(func.__name__, (Prototype,), dict())
    ret._prototype = ret()
    def init(self, *vargs, **kwargs):
        Prototype.__init__(self)
        func(self, *vargs, **kwargs)
    ret.__init__ = init
    return ret

class CallablePrototype(Prototype):
    def __init__(self, proto=None, **kwargs):
        super().__init__()
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
        if proto:
            self.__proto__ = proto

    def __call__(self, **kwargs):
        return self.__class__(proto=self, **kwargs)

