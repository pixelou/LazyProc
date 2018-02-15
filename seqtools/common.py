import numbers
from typing import Sequence


def isint(x):
    return isinstance(x, numbers.Integral)


def basic_getitem(f):
    """decorator for a sane defaults implementation of __getitem__ that calls
    the actual implementation on integer keys in range 0 to len(self).
    """
    def getitem(self, key):
        if isinstance(key, slice):
            return SeqSlice(self, key)

        elif isint(key):
            if key < -len(self) or key >= len(self):
                raise IndexError(
                    self.__class__.__name__ + " index out of range")

            if key < 0:
                key = len(self) + key

            return f(self, key)

        else:
            raise TypeError(
                self.__class__.__name__ + " indices must be integers or "
                "slices, not " + key.__class__.__name__)

    return getitem


def basic_setitem(f):
    def setitem(self, key, value):
        if isinstance(key, slice):
            slice_view = SeqSlice(self, key)

            if len(slice_view) != len(value):
                raise ValueError(
                    self.__class__.__name__ +
                    " only supports one-to-one assignment")

            for i, v in enumerate(value):
                slice_view[i] = v

        elif isint(key):
            if key < -len(self) or key >= len(self):
                raise IndexError(
                    self.__class__.__name__ + " index out of range")

            if key < 0:
                key = len(self) + key

            f(self, key, value)

        else:
            raise TypeError(
                self.__class__.__name__ + " indices must be integers or "
                "slices, not " + key.__class__.__name__)

    return setitem


def normalize_slice(start, stop, step, n):
    start = 0 if start is None else start
    stop = n if stop is None else stop
    step = 1 if step is None else step

    if step == 0:
        raise ValueError("slice step cannot be 0")

    start = max(-n, min(start, n - 1))
    if start < 0:
        start += n
    stop = max(-n - 1, min(stop, n))
    if stop < 0:
        stop += n

    if (stop - start) * step <= 0:
        return 0, 0, 1

    if step > 0:
        stop += step - ((stop - start - 1) % step) - 1
    else:
        stop -= -step - ((start - stop - 1) % -step) - 1

    return start, stop, step


class SeqSlice(Sequence):
    def __init__(self, sequence, key):
        if isinstance(sequence, SeqSlice):
            oldkey_start = sequence.start
            oldkey_step = sequence.step
            key_start, key_stop, key_step = normalize_slice(
                key.start, key.stop, key.step, len(sequence))
            start = oldkey_start + key_start * oldkey_step
            stop = oldkey_start + key_stop * oldkey_step
            step = key_step * oldkey_step
            sequence = sequence.sequence

        else:
            start, stop, step = key.start, key.stop, key.step

        self.sequence = sequence
        start, stop, step = normalize_slice(start, stop, step, len(sequence))
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        return abs(self.stop - self.start) // abs(self.step)

    @basic_getitem
    def __getitem__(self, key):
        return self.sequence[self.start + key * self.step]

    @basic_setitem
    def __setitem__(self, key, value):
        self.sequence[self.start + key * self.step] = value