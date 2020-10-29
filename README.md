# starpy
Python scripts for easy RELION STAR file manipulation. Base library file metadata.py needed by all scripts.

**!!! Scripts are now RELION 3.1 compatible !!!**

Backward compatible with RELION <=3.0 format star files! 

## add_beamtiltclass_star.py
! only Relion <=3.0 format star files !
Add beamtilt class to the particles. Script adds rlnBeamTiltClass extracted from the micrograph name (in FoilHoleXXXX.mrc FEI format).
```
  --i    Input STAR filename.
  --o    Output STAR filename.
```

## assign_column_star.py
Add label (col_lb) to Input1 and assigns values to it from Input2 where the label (comp_lb) of Input2 matches Input1
```        
--i1        Input1 STAR filename.
--i2        Input2 STAR filename.
--o         Output STAR filename.
--col_lb    Label of the new column assigned to Input1; Default: rlnDefocusU
--comp_lb   Compare label used for Input1 and Input2 for value assignment. Default:rlnMicrographName
```
Example 1: Assign values of DefocusU from input2.star as a column to input1.star where the value of column rlnMicrographName matches in both inputs. 
``` 
assign_column_star.py --i1 input1.star --i2 input2.star --o output.star --col_lb rlnDefocusU --comp_lb rlnMicrographName
```

## extract_particles_coords_star.py
Remove other columns than particle coords from star file.
```
  --i    Input STAR filename with particles.
  --o    Output STAR filename. 
```

## create_beamtiltclass_from_xml.py
! only Relion <=3.0 format star files !
Clusters beam-shifts extracted from xml files into beam-tilt classes.
```
--i         Input XML directory
--o         Output star file. If empty no file generated generated
--o_shifts  Output file with extracted beam-shifts and cluster numbers. If empty no file generated generated
--clusters  Number of clusters the beam-shifts should be divided in. (default: 1)
--elbow     Number of max clusters used in Elbow method optimal cluster number determination. (default: 0)
--max_iter  Expert option: Maximum number of iterations of the k-means algorithm for a single run. (default: 300)
--n_init    Expert option: Number of time the k-means algorithm will be run with different centroid seeds. (default: 10)
```
Requires specific conda environment. Install:
```
conda create -n beamtiltclass-env
conda activate beamtiltclass-env
conda install scikit-learn
conda install matplotlib
```

## create_beamtiltclass_from_mdoc.py
! only Relion <=3.0 format star files !
Clusters beam-shifts extracted from serialem mdoc files into beam-tilt classes.
```
--i         Input mdoc directory
--o         Output star file. If empty no file generated generated
--o_shifts  Output file with extracted beam-shifts and cluster numbers. If empty no file generated generated
--clusters  Number of clusters the beam-shifts should be divided in. (default: 1)
--elbow     Number of max clusters used in Elbow method optimal cluster number determination. (default: 0)
--max_iter  Expert option: Maximum number of iterations of the k-means algorithm for a single run. (default: 300)
--n_init    Expert option: Number of time the k-means algorithm will be run with different centroid seeds. (default: 10)
```
Requires specific conda environment. Install:
```
conda create -n beamtiltclass-env
conda activate beamtiltclass-env
conda install scikit-learn
conda install matplotlib
```

## create_opticgroups_from_xml.py
! only Relion >=3.1 format star files !
Clusters beam-shifts extracted from xml files into optic groups.
```
--i         Input XML directory
--istar     Input particles star file.
--o         Output star file. If empty no file generated generated
--o_shifts  Output file with extracted beam-shifts and cluster numbers. If empty no file generated generated
--clusters  Number of clusters the beam-shifts should be divided in. (default: 1)
--elbow     Number of max clusters used in Elbow method optimal cluster number determination. (default: 0)
--max_iter  Expert option: Maximum number of iterations of the k-means algorithm for a single run. (default: 300)
--n_init    Expert option: Number of time the k-means algorithm will be run with different centroid seeds. (default: 10)
```
Requires specific conda environment. Install:
```
conda create -n beamtiltclass-env
conda activate beamtiltclass-env
conda install scikit-learn
conda install matplotlib
```

## create_opticgroups_from_mdoc.py
! only Relion >=3.1 format star files !
Clusters beam-shifts extracted from serialem mdoc files into optic groups.
```
--i         Input mdoc directory
--istar     Input particles star file.
--o         Output star file. If empty no file generated generated
--o_shifts  Output file with extracted beam-shifts and cluster numbers. If empty no file generated generated
--clusters  Number of clusters the beam-shifts should be divided in. (default: 1)
--elbow     Number of max clusters used in Elbow method optimal cluster number determination. (default: 0)
--max_iter  Expert option: Maximum number of iterations of the k-means algorithm for a single run. (default: 300)
--n_init    Expert option: Number of time the k-means algorithm will be run with different centroid seeds. (default: 10)
```
Requires specific conda environment. Install:
```
conda create -n beamtiltclass-env
conda activate beamtiltclass-env
conda install scikit-learn
conda install matplotlib
```

## get_absolute_apix.py
Calculates the absolute apix for the optics groups according to https://www3.mrc-lmb.cam.ac.uk/relion/index.php/Pixel_size_issues
```
  --i         Input STAR filename 
```

## heatmap_orient_star.py
Generates heatmap of particle orientations from star file. Cartesian and mollweide representations are generated. For symmetrical particles, first make symmetry expand of the star file (relion_particle_symmetry_expand).

Requires:
- Matplotlib
- Numpy
```
  --i         Input STAR filename with particles and orientations.
  --o         Output files prefix. Default: heatmap_orient
  --show      Only shows the resulting heatmap. Does not store any output file.
  --white_bg  Set background of the heatmap to white. (i.e. zero values represented by white)
  --black_bg  Set background of the heatmap to black . (i.e. zero values represented by black)
  --format    Output format. Available formats: png, svg, jpg, tif. Default: png
  --vmin      Min values represented on color bar. Default: -1 (auto)
  --vmax      Max values represented on color bar. Default: -1 (auto)
```

## helix_correct_star.py
Modify star file to be compatible with helix refinement
```
  --i    Input STAR filename with particles.
  --o    Output STAR filename. 
```
## join_star.py
Join two star files. Joining options: UNION, INTERSECT, EXCEPT. 
```
  --i1    Input1 STAR filename with particles.
  --i2    Input2 STAR filename with particles.
  --o     Output STAR filename.
  --lb    Label used for intersect/except joining. e.g. rlnAngleTilt, rlnDefocusU...; Default: rlnMicrographName
  --op    Operator used for comparison. Allowed: "union", "intersect", "except"
```
Example 1: Include all line from Input1 and Input2 in the Output star file.
``` 
join_star.py --i1 input1.star --i2 input2.star --o output.star 
```
Example 2: Select all lines from Input1 where micrographs DO match micrographs in Input2.
```
join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"intersect\" 
```
Example 3: Select all lines from Input1 where micrographs DO NOT match micrographs in Input2.
```
join_star.py --i1 input1.star --i2 input2.star --o output.star --lb rlnMicrographName --op \"except\""
```
## json2star.py
Convert EMAN2 json type box files into RELION coordinate STAR file.
Coordinates might be corrected for binning, when the particles were picked on binned micrographs.
Boxes lying outside micrograph boundaries might be discarded.
```
  --i          Input directory with json files (EMAN2 info directory location.)
  --o          Output directory to store STAR files.
  --suffix     Star file suffix (e.g. "_box" will produce micname123_box.star). Default: "_box"
  --boxsize    Box size used to exclude boxes that violates micrograph boundaries). Default: 256
  --binning    Binning factor correction. Use when particles we picked on binned micrographs. Default: 1
  --maxX       Max size of the micrograph in pixels in X dimension (used to exclude boxes from micrograph edges). Default: 4096
  --maxY       Max size of the micrograph in pixels in Y dimension (used to exclude boxes from micrograph edges). Default: 4096
```
## math_star.py
Perform basic math operations on star file values.
```
  --i         Input STAR filename with particles.
  --o         Output STAR filename.
  --lb        Label used for math operation. e.g. rlnAngleTilt, rlnDefocusU...
  --op        Operator used for comparison. Allowed: "+", "-", "*", "/","^","abs","=","mod","remainder". Use double quotes!!!
  --val       Value used for math operation.
  --sellb     Label used for selection. e.g. rlnAngleTilt, rlnDefocusU... Default: None
  --selop     Operator used for comparison. Allowed: "=", "!=", ">=", "<=", "<". Use double quotes!!!
  --selval    Value used for comparison. Used together with --selop parameter.
  --rh        Selection range Hi (upper bound). Default: Disabled
  --rl        Selection range Lo (lower bound). Default: Disabled
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
## metadata.py
Base library required by all scripts.

## particles_star_to_box.py
Extracts coordinates from particles STAR file and saves as per micrograph box files.
```
--i         Input STAR filename with particles.
--o         Output directory where the box files will be stored.
--box_size  Box size. Default: 256
```

## remove_preferred_orient.py
Remove particles with overrepresented orientations. Average count of particles at each orientation is calculated. Then the count of particles that are n-times SD over the average is modified by retaining the particles with the highest rlnMaxValueProbDistribution.
```
  --i      Input STAR filename with particles and orientations.
  --o      Output star file. Default: output.star
  --sd     This many times SD above the average count will be representations kept. Default: 3
```
## rename_foilhole_star.py
Deprecated - need to be rewritten

## rotate_particles_star.py
Perform rotation of particles according to given euler angles.
```
  --i       Input STAR filename with particles.
  --o       Output STAR filename.
  --rot     Rotattion Euler angle. Default 0
  --tilt    Tilt Euler angle. Default 0
  --psi     Psi Euler angle. Default 0
  --x       Shift along X axis. Default 0
  --y       Shift along Y axis. Default 0
  --z       Shift along Z axis. Default 0
```
Example:
```
rotate_particles_star.py --i input.star --o output.star --rot 15 --tilt 20 --psi 150
```

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

## select_rand_sym_copy_ptcls.py
Select random orientation from symmetry expanded star files. One orientation per particle.
```
  --i    Input STAR filename with particles.
  --o    Output STAR filename. 
```

## select_values_star.py
Select particles complying with selection rule on specified label.
``` 
  --i        Input STAR filename with particles.
  --o        Output STAR filename. 
  --lb       Label used for selection. e.g. rlnAngleTilt, rlnDefocusU...
  --op       Operator used for comparison. Allowed: "=", "!=", ">=", "<=", "<". Use double quotes!!!
  --val      Value used for comparison. Used together with --op parameter.
  --rh       Range Hi (upper bound). If defined --op and -val disabled.
  --rl       Range Lo (lower bound). If defined --op and -val disabled.
  --prctl_h  Select particles above defined percentile of values (e.g. 25, 50, 75). Used together with --lb parameter
  --prctl_l  Select particles below defined percentile of values (e.g. 25, 50, 75). Used together with --lb parameter
```

Example 1: Select lines from input.star where source micrograph does not equals to mic123456789.mrc
```
 select_values_star.py --i input.star --o output.star --lb rlnMicrographName --op "!=" --val mic123456789.mrc 
```
Example 2: Select lines from input.star where tilt angles are less than 15 deg.
```
select_values_star.py --i input.star --o output.star --lb rlnAngleTilt --op "<" --val 15
```
Example 3: Select particles where rlnMaxValueProbDistribution values are above 75-th percentile.
```
select_values_star.py --i input.star --o output.star --lb rlnMaxValueProbDistribution --prctl_h 75
```
Example 4: Select particles where rlnMaxValueProbDistribution values are below 75-th percentile.
```
select_values_star.py --i input.star --o output.star --lb rlnMaxValueProbDistribution --prctl_l 75
```

## split_stacks.py
Split MRC stacks listed in STAR file into separate files, and writes a new STAR file with split files info.
```
  --i        Input STAR filename.
  --o_dir    Output folder.
  --o_pref   Output image prefix.
```

## stats_star.py
Print basic statistics on numerical labels present in STAR file
```
  --i     Input STAR filename.
  --lb    Labels used for statistics (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. "rlnAngleTilt rlnAngleRot")
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
  --i    Input STAR filename with particles.
  --o    Output STAR filename. 
```
