.. _eda:

*******************************************************************************
EDA of MD Trajectories
*******************************************************************************

Synopsis
===============================================================================

This example shows how to perform essential dynamics analysis of molecular
dynamics (MD) trajectories.  A :class:`.EDA` instance that stores covariance 
matrix and principal modes that describes the essential dynamics of the system
observed in the simulation will be built.  :class:`.EDA` and principal modes 
(:class:`.Mode`) can be used as input to functions in :mod:`.dynamics` module
for further analysis.


User needs to provide trajectory in DCD file format and PDB file of the system.

Example input: 

* :download:`MDM2 structure and dcd files </doctest/mdm2.tar.gz>`

Notes
-------------------------------------------------------------------------------

Analysis of trajectories in some other formats can be performed with the help
of MDAnalysis Python package. Interested user should consult |mdanalysis| for 
more information.


Parse reference structure
===============================================================================

We start by importing everything from ProDy:
  
>>> from prody import *

The PDB file provided with this example contains and X-ray structure which will 
be useful in a number of places, so let's start with parsing this file first:

.. plot::
   :nofigs:
   :context:
   :include-source:

   >>> structure = parsePDB('mdm2.pdb')
   >>> structure
   <AtomGroup: mdm2 (1449 atoms)>

This function returned a :class:`.AtomGroup` instance that
stores all atomic data parsed from the PDB file.

EDA calculations
===============================================================================

Essential dynamics analysis (EDA or PCA) of a trajectory can be performed in 
two ways. 

**Small trajectory files**

If you are analyzing a small trajectory, you can use an :class:`.Ensemble` 
instance obtained by parsing the trajectory at once using :func:`.parseDCD`:

>>> ensemble = parseDCD('mdm2.dcd')
>>> ensemble.setCoords(structure)
>>> ensemble.setAtoms(structure.calpha)
>>> ensemble
<Ensemble: mdm2 (0:500:1) (500 conformations; selected 85 of 1449 atoms)>
>>> ensemble.superpose()
>>> eda_ensemble = EDA('MDM2 Ensemble')
>>> eda_ensemble.buildCovariance( ensemble )
>>> eda_ensemble.calcModes()
>>> eda_ensemble
<EDA: MDM2 Ensemble (20 modes; 85 atoms)>

**Large trajectory files**

If you are analyzing a large trajectory, you can pass the trajectory instance
to the :meth:`.PCA.buildCovariance` method as follows:

>>> dcd = DCDFile('mdm2.dcd')
>>> dcd.link(structure)
>>> dcd.setAtoms(structure.calpha)
>>> dcd
<DCDFile: mdm2 (linked to AtomGroup mdm2; next 0 of 500 frames; selected 85 of 1449 atoms)>
>>> eda_trajectory = EDA('MDM2 Trajectory')
>>> eda_trajectory.buildCovariance( dcd )
>>> eda_trajectory.calcModes()
>>> eda_trajectory
<EDA: MDM2 Trajectory (20 modes; 85 atoms)>

**Compare two methods**

>>> printOverlapTable(eda_ensemble[:3], eda_trajectory[:3])
Overlap Table
                       EDA MDM2 Trajectory
                         #1     #2     #3
EDA MDM2 Ensemble #1   +1.00   0.00   0.00
EDA MDM2 Ensemble #2    0.00  +1.00   0.00
EDA MDM2 Ensemble #3    0.00   0.00  +1.00
<BLANKLINE>

Overlap values of +1 along the diagonal of the table shows that top ranking
3 essential (principal) modes are the same.

Multiple files
===============================================================================

It is also possible to analyze multiple trajectory files without concatenating
them. In this case we will use data from two independent simulations 

.. plot::
   :nofigs:
   :context:
   :include-source:

   >>> trajectory = Trajectory('mdm2.dcd')
   >>> trajectory.addFile('mdm2sim2.dcd')
   >>> trajectory
   <Trajectory: mdm2 (2 files; next 0 of 1000 frames; 1449 atoms)>
   >>> trajectory.link(structure)
   >>> trajectory.setCoords(structure)
   >>> trajectory.setAtoms(structure.calpha)
   >>> trajectory
   <Trajectory: mdm2 (linked to AtomGroup mdm2; 2 files; next 0 of 1000 frames; selected 85 of 1449 atoms)>
   >>> eda = EDA('mdm2')
   >>> eda.buildCovariance( trajectory )
   >>> eda.calcModes()
   >>> eda
   <EDA: mdm2 (20 modes; 85 atoms)>

**Save your work**

You can save your work using ProDy function :func:`.saveModel`. This will 
allow you to avoid repeating calculations when you return to your work later:

>>> saveModel(eda)
'mdm2.eda.npz'

:func:`.loadModel` function can be used to load this object without any loss.

Print data
===============================================================================

Let's print fraction of variance for top raking 4 essential modes:

>>> for mode in eda_trajectory[:4]:
...     print calcFractVariance(mode).round(2)
0.26
0.11
0.08
0.06

Plot data
===============================================================================

Now, let's project the trajectories onto top three essential modes:

.. plot::
   :context:
   :include-source:
  
   >>> mdm2ca_sim1 = trajectory[:500] # doctest: +SKIP
   >>> mdm2ca_sim1.superpose() # doctest: +SKIP
   >>> mdm2ca_sim2 = trajectory[500:] # doctest: +SKIP
   >>> mdm2ca_sim2.superpose() # doctest: +SKIP
   >>> # Let's import plotting library and make an empty figure
   >>> import matplotlib.pyplot as plt # doctest: +SKIP
   >>> # We project independent trajectories in different color   
   >>> showProjection(mdm2ca_sim1, eda[:3], color='red', marker='.') # doctest: +SKIP
   >>> showProjection(mdm2ca_sim2, eda[:3], color='blue', marker='.') # doctest: +SKIP
   >>> # Now let's mark the beginning of the trajectory with a circle
   >>> showProjection(mdm2ca_sim1[0], eda[:3], color='red', marker='o', ms=12) # doctest: +SKIP
   >>> showProjection(mdm2ca_sim2[0], eda[:3], color='blue', marker='o', ms=12) # doctest: +SKIP
   >>> # Now let's mark the end of the trajectory with a square
   >>> showProjection(mdm2ca_sim1[-1], eda[:3], color='red', marker='s', ms=12) # doctest: +SKIP
   >>> showProjection(mdm2ca_sim2[-1], eda[:3], color='blue', marker='s', ms=12) # doctest: +SKIP



Write NMD file
===============================================================================

The above projection is shown for illustration. Interpreting the essential 
modes and projection of snapshots onto them is case dependent. One should know
what kind of motion the top essential modes describe. You can use :ref:`nmwiz`
for visualizing essential mode shapes and fluctuations along these modes. 

We can write essential modes into an :term:`NMD` file for NMWiz as follows:

>>> writeNMD('mdm2_eda.nmd', eda[:3], structure.select('calpha'))
'mdm2_eda.nmd'

See Also
===============================================================================
   
See other examples in :ref:`pca-xray` for illustration of 
comparative analysis of theoretical and computational data.

See also :ref:`trajectory` for more analysis examples. 

|questions|

|suggestions|
