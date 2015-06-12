import fnmatch
class Group(object):
    def __init__(self, *args, **kwargs):
        self.clear()
        
        self.append(*args, **kwargs)
        
    def clear(self):
        self._child = {}
        self._child_keys = []
    
    def add(self, obj):
        try:
            key = obj.t
        except AttributeError:
            try:
                key = obj.text.t
            except AttributeError:
                key = str(hash(obj))
        
        i = ''
        while ((key + i) in self._child_keys):
            if not i:
                i = '1'
            else:
                i = str(int(i) + 1)
        
        key += i
                
        self.__setitem__(key, obj)
        
        return self

    
    def __iadd__(self, obj):
        return self.add(obj)

    def _get_key(self, val):
        if isinstance(val, int):
            try:
                return self._child_keys[val], val
            except IndexError:
                raise
        elif isinstance(val, str):
            for i, t in enumerate(self._child_keys):
                try:
                    if fnmatch.fnmatch(t, val):
                        return t, i
                except AttributeError:
                    pass
                
            raise KeyError
        else:
            for i, t in enumerate(self._child_keys):
                if t == val:
                    return t,i

    def __delitem__(self, val):
        key, i = self._get_key(val)
        
        del self._child_keys[i]
        del self._child[key]

    def __getitem__(self, val):
        return self._child[self._get_key(val)[0]]

    def __setitem__(self, key, val):
        if key not in self._child:
            self._child_keys.append(key)
            
        self._child[key] = val

    def remove(self, val):
        self.__delitem__(val)
        
    def append(self, *args, **kwargs):
        for a in args:
            self += a
            
        for k,v in kwargs.items():
            self[k] = v
            
        return self
            
    def __iter__(self):
        for k in self._child_keys:
            yield k
    