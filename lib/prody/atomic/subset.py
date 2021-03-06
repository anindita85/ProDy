# -*- coding: utf-8 -*-
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

import numpy as np

from . import flags
from .atom import Atom
from .fields import ATOMIC_FIELDS, READONLY
from .fields import wrapGetMethod, wrapSetMethod
from .pointer import AtomPointer
from prody import LOGGER

__all__ = ['AtomSubset']

class AtomSubsetMeta(type):

    def __init__(cls, name, bases, dict):

        for fname, field in ATOMIC_FIELDS.iteritems():
            
            if field.private:
                continue

            meth = field.meth_pl
            getMeth = 'get' + meth
            setMeth = 'set' + meth
            # Define public method for retrieving a copy of data array
            def getData(self, meth=field.meth_pl, call=field.call):
                data = getattr(self._ag, '_get' + meth)()
                if data is not None:
                    return data[self._indices]
            getData = wrapGetMethod(getData)
            getData.__name__ = getMeth
            getData.__doc__ = field.getDocstr('get')
            setattr(cls, getMeth, getData)
            setattr(cls, '_' + getMeth, getData)
            
            if field.readonly:
                continue
            
            # Define public method for setting values in data array
            def setData(self, value, var=fname, none=field.none):
                array = self._ag._data[var]
                if array is None:
                    raise AttributeError(var + ' data is not set')
                array[self._indices] = value
                if none: self._ag._none(none)
            setData = wrapSetMethod(setData)
            setData.__name__ = setMeth 
            setData.__doc__ = field.getDocstr('set')  
            setattr(cls, setMeth, setData)

                        
class AtomSubset(AtomPointer):
    
    """A class for manipulating subset of atoms in an :class:`.AtomGroup`.
    Derived classes are:
        
      * :class:`.Selection`
      * :class:`.Segment`
      * :class:`.Chain`
      * :class:`.Residue`
    
    This class stores a reference to an :class:`.AtomGroup` instance, a set of 
    atom indices, and active coordinate set index for the atom group.
    
    """
    
    __metaclass__ = AtomSubsetMeta    
    
    __slots__ = ['_ag', '_indices', '_acsi', '_selstr']
    
    def __init__(self, ag, indices, acsi, **kwargs):
        
        AtomPointer.__init__(self, ag, acsi)

        if not isinstance(indices, np.ndarray):
            indices = np.array(indices, int)
        elif not indices.dtype == int:
            indices = indices.astype(int)
        
        if kwargs.get('unique'):
            self._indices = indices
        else:
            self._indices = np.unique(indices)
        
        self._selstr = kwargs.get('selstr')

    def __len__(self):
        
        return len(self._indices)

    def getCoords(self):
        """Return a copy of coordinates from the active coordinate set."""
        
        if self._ag._coords is not None:
            # Since this is not slicing, a view is not returned
            return self._ag._coords[self.getACSIndex(), self._indices]
    
    _getCoords = getCoords
    
    def setCoords(self, coords):
        """Set coordinates in the active coordinate set."""
        
        if self._ag._coords is not None:
            self._ag._coords[self.getACSIndex(), self._indices] = coords
            self._ag._setTimeStamp(self.getACSIndex())
    
    def getCoordsets(self, indices=None):
        """Return coordinate set(s) at given *indices*, which may be an integer 
        or a list/array of integers."""
        
        if self._ag._coords is None:
            return None
        if indices is None:
            return self._ag._coords[:, self._indices]
        if isinstance(indices, (int, slice)):
            return self._ag._coords[indices, self._indices]
        if isinstance(indices, (list, np.ndarray)):
            return self._ag._coords[indices, self._indices]
        raise IndexError('indices must be an integer, a list/array of '
                         'integers, a slice, or None')
                         
    _getCoordsets = getCoordsets

    def iterCoordsets(self):
        """Yield copies of coordinate sets."""
        
        coords = self._ag._getCoordsets()
        if coords is not None:
            indices = self._indices
            for xyz in coords:
                yield xyz[indices]

    _iterCoordsets = iterCoordsets
    
    def getIndices(self):
        """Return a copy of the indices of atoms."""
        
        return self._indices.copy()
    
    def _getIndices(self):
        """Return indices of atoms."""
        
        return self._indices
    
    def numAtoms(self, flag=None):
        """Return number of atoms, or number of atoms with given *flag*."""
        
        return len(self._getSubset(flag)) if flag else len(self._indices)

    def iterAtoms(self):
        """Yield atoms."""

        ag = self._ag
        acsi = self.getACSIndex()
        for index in self._indices:
            yield Atom(ag=ag, index=index, acsi=acsi)

    __iter__ = iterAtoms
    
    def getData(self, label):
        """Return a copy of data associated with *label*, if it is present."""
        
        data = self._ag._getData(label)
        if data is not None:
            return data[self._indices]
    
    _getData = getData
    
    def setData(self, label, data):
        """Update *data* associated with *label*.
        
        :raise AttributeError: when *label* is not in use or read-only"""
        
        if label in READONLY:
            raise AttributeError('{0:s} is read-only'.format(repr(label)))
        if label in ATOMIC_FIELDS:
            getattr(self, 'set' + ATOMIC_FIELDS[label].meth_pl)(data)
        else:
            try:
                self._ag._data[label][self._index] = data 
            except KeyError:
                raise AttributeError('data with label {0:s} must be set for '
                                     'AtomGroup first'.format(repr(label)))

    def getFlags(self, label):
        """Return a copy of atom flags for given *label*, or **None** when 
        flags for *label* is not set."""   
             
        return self._ag._getFlags(label)[self._indices]
    
    def setFlags(self, label, value):
        """Update flag associated with *label*.
        
         :raise AttributeError: when *label* is not in use or read-only"""
        
        if label in flags.PLANTERS:
            raise AttributeError('flag {0:s} cannot be changed by user'
                                    .format(repr(label)))
        flags = self._ag._getFlags(label)
        if flags is None:
            raise AttributeError('flags with label {0:s} must be set for '
                                    'AtomGroup first'.format(repr(label)))
        flags[self._index] = value
            
    def getHeteros(self):
        """Deprecated for removal in v1.3, use ``getFlags('hetatm')`` instead.
        """
        
        from prody import deprecate
        deprecate('getHereros', "getFlags('hetatm')", '1.3')
        return self.getFlags('hetatm')
    
    def setHeteros(self, data):
        """Deprecated for removal in v1.3, use ``setFlags('hetatm', data)``
        instead."""
        
        from prody import deprecate
        deprecate('setHereros', "setFlags('hetatm', data)", '1.3')
        return self.setFlags('hetatm', data)
