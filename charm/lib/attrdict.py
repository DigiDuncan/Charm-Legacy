# AttrDict by nfearnley.


class ReservedAttributeError(AttributeError):
    def __init__(self, obj, key):
        super().__init__(f"{key!r} is a reserved attribute for {obj.__class__.__name__!r}")


class ReservedKeyError(KeyError):
    def __init__(self, obj, key):
        super().__init__(f"{key!r} is a reserved key for {obj.__class__.__name__!r}")


class AttrDict:
    """A convenient class for accessing a dictionary via attributes"""
    __slots__ = ["_values"]

    def __init__(self, data={}):
        # Ensure we're dealing with a plain dictionary
        data = {**data}

        # Check for reserved keys
        for k in data:
            if self._is_reserved(k):
                raise ReservedKeyError(self, k)

        # Set self._values while avoiding an infinite recursion issue with __setattr__ and __getattr__
        super().__setattr__("_values", data)

    def _is_reserved(self, key):
        """Check if a key is reserved"""
        return key.startswith("_")

    def __getattr__(self, key):
        """value = attrdict.key"""
        try:
            return self._values[key]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {key!r}")

    def __setattr__(self, key, value):
        """attrdict.key = value"""
        if self._is_reserved(key):
            raise ReservedAttributeError(self, key)
        self._values[key] = value

    def __delattr__(self, key):
        """del attrdict.key"""
        if self._is_reserved(key):
            raise ReservedAttributeError(self, key)
        del self._values[key]

    def __getitem__(self, key):
        """value = attrdict[key]"""
        return self._values[key]

    def __setitem__(self, key, value):
        """attrdict[key] = value"""
        if self._is_reserved(key):
            raise ReservedKeyError(self, key)
        self._values[key] = value

    def __delitem__(self, key, value):
        """del attrdict[key]"""
        if self._is_reserved(key):
            raise ReservedKeyError(self, key)
        del self._values[key]

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return repr(self._values)

    def __iter__(self):
        return iter(self._values)

    def __contains__(self, key):
        return key in self._values

    def __len__(self):
        return len(self._values)

    def __eq__(self, other):
        return other == self._values
