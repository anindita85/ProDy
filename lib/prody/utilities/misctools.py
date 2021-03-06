# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2012 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module defines miscellaneous utility functions."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

from textwrap import wrap as textwrap

from numpy import unique

__all__ = ['Everything', 'rangeString', 'alnum', 'importLA', 'dictElement',]
        
class Everything(object):
    
    """Everything is here."""
    
    def __contains__(self, what):
        
        return True

def rangeString(lint, sep=' ', rng=' to ', exc=False, pos=True):
    """Return a structured string for a given list of integers.
    
    :arg lint: integer list or array
    :arg sep: range or number separator     
    :arg rng: range symbol
    :arg exc: set **True** if range symbol is exclusive
    :arg pos: only consider zero and positive integers 

    >>> from prody.utilities import rangeString
    >>> lint = [1, 2, 3, 4, 10, 15, 16, 17]
    >>> rangeString(lint) 
    '1 to 4 10 15 to 17'
    >>> rangeString(lint, sep=',', rng='-') 
    '1-4,10,15-17'
    >>> rangeString(lint, ',', ':', exc=True)
    '1:5,10,15:18'
    """
        
    ints = unique(lint)
    if pos and ints[0] < 0:
        ints = ints[ints > -1]

    prev = ints[0]
    lint = [[prev]]
    for i in ints[1:]:
        if i - prev > 1:
            lint.append([i])
        else:
            lint[-1].append(i)
        prev = i
    exc = int(exc)
    return sep.join([str(l[0]) if len(l) == 1 else 
                     str(l[0]) + rng + str(l[-1] + exc) for l in lint])

def alnum(string, alt='_', trim=False, single=False):
    """Replace non alpha numeric characters with *alt*.  If *trim* is **True**
    remove preceding and trailing *arg* characters.  If *single* is **True**,
    contain only a single joining *alt* character. """
    
    result = ''
    multi = not bool(single)
    prev = None
    for char in string:
        if char.isalnum():
            result += char
            prev = char
        else:
            if multi or prev != alt:
                result += alt
            prev = alt
    trim = int(bool(trim))
    result = result[trim * (result[0] == alt):
                    len(result) - trim * (result[-1] == alt)]
    return result


def importLA():
    """Return one of :mod:`scipy.linalg` or :mod:`numpy.linalg`."""
    
    try:
        import scipy.linalg as linalg
    except ImportError:
        try:
            import numpy.linalg as linalg
        except:
            raise ImportError('scipy.linalg or numpy.linalg is required for '
                              'NMA and structure alignment calculations')
    return linalg


def dictElement(element, prefix=None):
    """Returns a dictionary built from the children of *element*, which must be
    a :class:`xml.etree.ElementTree.Element` instance.  Keys of the dictionary
    are *tag* of children without the *prefix*, or namespace.  Values depend on
    the content of the child.  If a child does not have any children, its text 
    attribute is the value.  If a child has children, then the child is the 
    value."""
    
    dict_ = {}
    length = False
    if isinstance(prefix, str):
        length = len(prefix)
    for child in element:
        tag = child.tag
        if length and tag.startswith(prefix):
            tag = tag[length:]
        if len(child) == 0:
            dict_[tag] = child.text
        else:
            dict_[tag] = child
    return dict_


