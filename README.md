# starpy
Python scripts for easy STAR file manipulation. Base library file metadata.py needed by all scripts.

## add_beamtiltclass_star.py
Add beamtilt class to the particles. Script adds rlnBeamTiltClass extracted from the micrograph name (in FoilHoleXXXX FEI format).
```
  --i       Input STAR filename.
  --o       Output STAR filename.
```

## extract_particles_coords_star.py
Remove other columns than particle coords from star file.
```
  --i       Input STAR filename with particles.
  --o       Output STAR filename. 
```

## heatmap_orient_star.py

Generates heatmap of particle orientations from star file. For symmetrical particles, first make symmetry expand of the star file (relion_particle_symmetry_expand).

Requires:
- Matplotlib
- Numpy

```
  --i      Input STAR filename with particles and orientations.
  --o      Output files prefix. Default: heatmap_orient
  --format Output format. Available formats: png, svg, jpg, tif. Default: png
  --vmin   Min values represented on color bar. Default: -1 (auto)
  --vmax   Max values represented on color bar. Default: -1 (auto)
```
## join_star.py

Join two star files. Joining options:UNION, INTERSECT, EXCEPT. \n 
```
  --i1      Input1 STAR filename with particles.
  --i2      Input2 STAR filename with particles.
  --o       Output STAR filename.
  --lb      Label used for intersect/except joining. e.g. rlnAngleTilt, rlnDefocusU...; Default: rlnMicrographName
  --op      Operator used for comparison. Allowed: "union", "intersect", "except"
```

Example 1: Include all line from Input1 and Input2 in the Output star file.
``` 
join_star.py --i1 input1.star --i2 input2.star --o output.star \n\n 
```
Example 2: Select all lines from Input1 where micrographs DO match micrographs in Input2.
```
join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"intersect\"\n\n 
```
Example 3: Select all lines from Input1 where micrographs DO NOT match micrographs in Input2.
```
join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"except\""
```
## math_star.py
Perform basic math operations on star file values.


```
  --i             Input STAR filename with particles.
  --o             Output STAR filename.
  --lb            Label used for math operation. e.g. rlnAngleTilt, rlnDefocusU...
  --op            Operator used for comparison. Allowed: "+", "-", "*", "/","^","abs","=","mod","remainder"
  --val           Value used for math operation.
  --sellb         Label used for selection. e.g. rlnAngleTilt, rlnDefocusU... Default: None
  --selop         Operator used for comparison. Allowed: "=", "!=", ">=", "<=", "<"
  --selval        Value used for comparison. Used together with --selop parameter.
  --rh            Selection range Hi (upper bound). Default: Disabled
  --rl            Selection range Lo (lower bound). Default: Disabled
```
Example 1: Add 15 deg to rlnAngleTilt.
```
math_star.py --i input.star --o output.star --lb rlnAngleTilt --op "+" --val 15 
```
Example 2: Multiply rlnOriginX by 2.
```
math_star.py --i input.star --o output.star --lb rlnOriginX --op "*" --val 2
```
Example 3: Compute remainder of rlnAngleRot where rlnGroupNumber is 2.
```
math_star.py --i input.star --o output.star --lb rlnAnlgeRot --op "remainder" --sellb rlnGroupNumber --selval 2 
```


## rename_foilhole_star.py
Deprecated

## select_orientations_star.py
Limit orientations of particles in STAR file. Select particles that are in the defined range of ROT, TILT, PSI angle.

```
  --i           Input STAR filename with particles.
  --o           Output STAR filename.
  --rot_min     Minimum rot angle.
  --rot_max     Minimum rot angle.
  --tilt_min    Minimum tilt angle.
  --tilt_max    Minimum tilt angle.
  --psi_min     Minimum psi angle.
  --psi_max     Minimum psi angle.
```

## select_values_star.py
Select particles complying with selection rule on specified label.
``` 
  --i        Input STAR filename with particles.
  --o        Output STAR filename. 
  --lb       Label used for selection. e.g. rlnAngleTilt, rlnDefocusU...## binning_correct_star.py
  --op       Operator used for comparison. Allowed: "=", "!=", ">=", "<=", "<"Correct the particles in star file by binning factor
  --val      Value used for comparison. Used together with --op parameter.
  --rh       Range Hi (upper bound). If defined --op and -val disabled.## filter_astigmatism_star.py
  --rl       Range Lo (lower bound). If defined --op and -val disabled.
```

Example 1: Select lines from input.star where source micrograph does not equals to mic123456789.mrc
```
 select_values_star.py --i input.star --o output.star --lb rlnMicrographName --op "!=" --val mic123456789.mrc 
```
Example 2: Select lines from input.star where tilt angles are less than 15 deg.
```
select_values_star.py --i input.star --o output.star --lb rlnAngleTilt --op "<" --val 15
```

## helix_correct_star.py
Modify star file to be compatible with helix refinement
```
  --i       Input STAR filename with particles.
  --o       Output STAR filename. 
```

## json2star.py
deprecated

## metadata.py
Base library required bay all scripts.

## rotate_particles_star.py
Perform rotation of particles according to given euler angles.
```
  --i      Input STAR filename with particles.
  --o      Output STAR filename.
  --rot    Rotattion Euler angle. Default 0
  --tilt   Tilt Euler angle. Default 0
  --psi    Psi Euler angle. Default 0
  --x      Shift along X axis. Default 0
  --y      Shift along Y axis. Default 0
  --z      Shift along Z axis. Default 0
```
Example:
```
rotate_particles_star.py --i input.star --o output.star --rot 15 --tilt 20 --psi 150
```

## select_rand_sym_copy_ptcls.py
Select random orientation from symmetry expanded star files. One orientation per particle.
```
  --i       Input STAR filename with particles.
  --o       Output STAR filename. 
```

## stats_star.py
Print basic statistics on numerical labels present in STAR file
```
  --i       Input STAR filename.
  --lb      Labels used for statistics (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. "rlnAngleTilt rlnAngleRot")
```
Example 1: Print out statistics on all labels:
```
./stats_star.py --i input.star
```
Example 2: Print out statistics on rlnAngleTilt:
```
./stats_star.py --i input.star --lb rlnAngleTilt
```
Example 3: Print out statistics on rlnAngleTilt, rlnAngleRot and rlnAnglePsi
```
./stats_star.py --i input.star --lb "rlnAngleTilt rlnAngleRot rlnAnglePsi"
```

## yflip_particles_star.py
Perform transformation of euler angles to produce Y-flipped reconstruction.
```
  --i       Input STAR filename with particles.
  --o       Output STAR filename. 
```
