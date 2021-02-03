from abc import abstractmethod, ABCMeta


# Stolen from cpython's _collection_abc.py
def _check_methods(C, *methods):
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


class Updateable(metaclass=ABCMeta):
    # A class is Updateable if it has an update() method.
    __slots__ = ()

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Updateable:
            return _check_methods(subclass, "update")
        return NotImplemented


class Drawable(metaclass=ABCMeta):
    # A class is Updateable if it has a draw() method.
    __slots__ = ()

    @abstractmethod
    def draw(self):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Drawable:
            return _check_methods(subclass, "draw")
        return NotImplemented


class Collidable(metaclass=ABCMeta):
    # A class is Updateable if it has a collision_box attribute.
    __slots__ = ()

    @property
    @abstractmethod
    def collision_box(self):
        return None

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Collidable:
            return hasattr(subclass, "collision_box")
        return NotImplemented
