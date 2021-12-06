# this is the seed of the python sonification library pyson
# (c) 2015++ Thomas Hermann, .... Ambient Intelligence group,
#B ielefeld University

import numpy


def linlin(x, smi, sma, dmi, dma):
    return (x - smi) / (sma - smi) * (dma - dmi) + dmi


def midicps(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def cpsmidi(c):
    return 69 + 12 * numpy.log2(c / 440.0)


def dbamp(db):
    return 10 ** (db / 20.0)


def ampdb(amp):
    return 20 * numpy.log10(amp)