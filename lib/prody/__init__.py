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

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'
__version__ = '1.2.1'

release = [int(x) for x in __version__.split('.')]

import os
import sys
import os.path
import platform
import warnings

if not (2, 6) <= sys.version_info[:2] <= (2, 7):
    raise Exception("prody is compatible with Python 2.6 and 2.7, you are "
                      "using Python " + platform.python_version())

try:
    import numpy as np
except ImportError:
    raise ImportError('Numpy is a required package for ProDy')
else:
    if tuple(map(int, np.__version__.split('.')[:2])) < (1, 4):
        raise ImportError('Numpy v1.4 or later is required for ProDy')

from utilities import USERHOME, PackageLogger, PackageSettings
from utilities import getPackagePath, joinRepr, tabulate

DEPRECATION_WARNINGS = False

from datetime import date
today = date.today()

if today.year == 2012:
    warnings.filterwarnings('default', category=DeprecationWarning)


def deprecate(dep, alt, ver=None, sl=3):
    """Issue a deprecation warning for *dep* and recommend using *alt*."""

    if ver is None:
        ver = list(__version__.split('.')[:2])
        ver[1] = str(int(ver[1]) + 1)
        ver = '.'.join(ver)  

    warnings.warn('`{0:s}` is deprecated for removal in v{1:s}, use `{2:s}`.'
                  .format(dep, ver, alt), DeprecationWarning, stacklevel=sl)

def turnonDepracationWarnings(action='always'):
    """Turn on deprecation warnings for the current session.  By default
     (``action='always'``), deprecation warnings will be printed every time
     a function is called to help identification of multiple occurrence 
     of deprecated function and method names.  When ``action='default'``
     is passed, warning will be issued at the first call of a function.
     The latter behavior will automatically kick in when v0.9 is released.
     Until v0.9 is released, restarting the session will turn of warnings.
     This function must be called as ``prody.turnonDepracationWarnings``."""
    
    global DEPRECATION_WARNINGS
    DEPRECATION_WARNINGS = True
    warnings.filterwarnings(action, category=DeprecationWarning)

    
_PY3K = PY3K = sys.version_info[0] > 2
PY2K = not PY3K

PACKAGECONF =  os.path.join(USERHOME, '.prodyrc')
if not os.path.isfile(PACKAGECONF) and os.path.isfile(PACKAGECONF[:-2]):
    os.rename(PACKAGECONF[:-2], PACKAGECONF)

LOGGER = PackageLogger('.prody')

SETTINGS = PackageSettings('prody', logger=LOGGER) 
SETTINGS.load()

__all__ = ['checkUpdates', 'confProDy', 'getVerbosity', 'setVerbosity',
           'startLogfile', 'closeLogfile', 
           'plog']

from . import kdtree
from .kdtree import *
__all__.extend(kdtree.__all__)
__all__.append('kdtree')

from . import atomic 
from .atomic import *
__all__.extend(atomic.__all__)
__all__.append('atomic')

from .atomic import SELECT

from . import proteins
from .proteins import *  
__all__.extend(proteins.__all__)
__all__.append('proteins')

from . import measure
from .measure import *
__all__.extend(measure.__all__)
__all__.append('measure')

from . import dynamics
from .dynamics import *
__all__.extend(dynamics.__all__)
__all__.append('dynamics')

from . import ensemble
from .ensemble import *
__all__.extend(ensemble.__all__)
__all__.append('ensemble')

from . import trajectory
from .trajectory import *
__all__.extend(trajectory.__all__)
__all__.append('trajectory')

import prody
__all__.append('prody')

# default, acceptable values, setter
CONFIGURATION = {
    'backup': (False, None, None),
    'backup_ext': ('.BAK', None, None),
    'ligand_xml_save': (False, None, None),
    'typo_warnings': (True, None, None),
    'check_updates': (0, None, None),
    'auto_secondary': (False, None, None),
    'selection_warning': (True, None, None),
    'verbosity': ('debug', list(utilities.LOGGING_LEVELS), 
                  LOGGER._setverbosity),
    'pdb_mirror_path': ('', None, proteins.setPDBMirrorPath),
    'local_pdb_folder': ('', None, proteins.setPDBMirrorPath),
}


def confProDy(*args, **kwargs):
    """Configure ProDy."""

    settings = None
    if args:
        values = []
        for option in args:
            try:
                values.append(SETTINGS[option])
            except KeyError:
                raise KeyError('{0:s} is not a valid configuration option'
                               .format(repr(option)))
        if len(values) == 1:
            return values[0]
        else:
            return values

    for option, value in kwargs.items():    
        try:
            default, acceptable, setter = CONFIGURATION[option]
        except KeyError:
            raise KeyError('{0:s} is not a valid configuration option'
                           .format(repr(option)))
        else:
            try:
                value = type(default)(value)
            except ValueError:
                raise TypeError('{0:s} must be a {1:s}'
                                .format(option, type(default).__name__))
            if acceptable is not None and value not in acceptable:
                raise ValueError('{0:s} must be one of {1:s}'.format(option, 
                    joinRepr(acceptable, sort=True, last=', or ')))
                
            SETTINGS[option] = value
            SETTINGS.save()
            LOGGER.info('ProDy is configured: {0:s}={1:s}'
                        .format(option, repr(value)))
            if setter is not None:
                setter(value)

_keys = list(CONFIGURATION)
_keys.sort()
_vals = []
for _key in _keys:
    default, acceptable, setter = CONFIGURATION[_key]
    try:
        if not setter.func_name.startswith('_'): 
            seealso = ' See also :func:`.' + setter.func_name + '`.'
    except AttributeError:
        seealso = ''
        
    if acceptable is None:
        _vals.append(repr(default) + seealso)
    else:
        _vals.append(repr(default) + ' (' + 
                     joinRepr(acceptable, sort=True, last=', or ')  + ')' +
                     seealso)
    if _key not in SETTINGS:
        SETTINGS[_key] = default

confProDy.__doc__ += '\n\n' + tabulate(['Option'] + _keys, 
    ['Default (acceptable values)'] + _vals) + """

Usage example::
        
    confProDy('backup')
    confProDy('backup', 'backup_ext')
    confProDy(backup=True, backup_ext='.bak')
    confProDy(backup_ext='.BAK')"""


def plog(*text):
    """Log *text* using ProDy logger at log level info.  Multiple arguments 
    are accepted.  Each argument will be converted to string and joined using 
    a white space as delimiter."""
    
    LOGGER.info(' '.join([str(s) for s in text]))


def startLogfile(filename, **kwargs):
    
    LOGGER.start(filename, **kwargs)
    
startLogfile.__doc__ = LOGGER.start.__doc__
    
    
def closeLogfile(filename):
    """Close logfile with *filename*."""

    LOGGER.close(filename)


def setVerbosity(level):
    """Deprecated for removal in v1.3, use :func:`.confProDy` instead."""

    deprecate('setVerbosity', 'confProDy(verbosity=\'debug\')')
    confProDy(verbosity=level)



def getVerbosity():
    """Deprecated for removal in v1.3, use :func:`.confProDy` instead."""
    
    deprecate('getVerbosity', 'confProDy(\'verbosity\')')
    return confProDy('verbosity')


def checkUpdates():
    """Check PyPI to see if there is a newer ProDy version available.  Setting
    ProDy configuration parameter *check_updates* to a positive integer will 
    make ProDy automatically check updates, e.g.::
       
      confProDy(check_updates=7) # check at most once a week
      confProDy(check_updates=0) # do not auto check updates
      confProDy(check_updates=-1) # check at the start of every session"""
    
    if PY3K:
        import xmlrpc.client
        pypi = xmlrpc.client.Server('http://pypi.python.org/pypi')
    else:
        import xmlrpclib
        pypi = xmlrpclib.Server('http://pypi.python.org/pypi')
    releases = pypi.package_releases('ProDy')
    if releases[0] == __version__:
        LOGGER.info('You are using the latest ProDy release (v{0:s}).'
                    .format(__version__))
    else:
        LOGGER.info('ProDy v{0:s} is available, you are using {1:s}.'
                    .format(releases[0], __version__))
    if SETTINGS['check_updates']:
        import time
        SETTINGS['last_check'] = time.time()
        SETTINGS.save()

if SETTINGS['check_updates']: 
    
    if SETTINGS.get('last_check') is None:
        SETTINGS['last_check'] = 0
    import time
    if ((time.time() - SETTINGS.get('last_check')) / 3600 / 24 > 
        SETTINGS['check_updates']):
        LOGGER.info('Checking PyPI for ProDy updates:')
        checkUpdates()

def test(**kwargs):
    """Run ProDy tests, ``prody.test()``. See :mod:`prody.tests` 
    documentation for more details."""
    
    if sys.version_info[:2] > (2,6):
        try:
            import prody.tests
        except ImportError as err:
            LOGGER.warning('Could not import ProDy unit tests, '
                           'please check your installation.')
            raise type(err)(str(err))
        else:
            prody.tests.test(**kwargs)
    else:
        LOGGER.warning('ProDy tests are available for Python 2.7') 
