# starpy
Python scripts for easy RELION STAR file manipulation. Base library file metadata.py needed by all scripts.

**!!! Scripts are now RELION 3.1+ compatible !!!**

**Now many of the scripts supports STDIN/STDOUT for input/output.**

Backward compatible with RELION <=3.0 format star files! 

## Table of Contents
- [General usage](#general-usage)
- [add_beamtiltclass_star.py](#add_beamtiltclass_starpy)
- [add_remove_label.py](#add_remove_labelpy)
- [analyze_orientation_distances_star.py](#analyze_orientation_distances_starpy)
- [assign_column_star.py](#assign_column_starpy)
- [binning_correct_star.py](#binning_correct_starpy)
- [create_beamtiltclass_from_mdoc.py](#create_beamtiltclass_from_mdocpy)
- [create_beamtiltclass_from_xml.py](#create_beamtiltclass_from_xmlpy)
- [create_opticgroups_from_filename.py](#create_opticgroups_from_filenamepy)
- [create_opticgroups_from_xml.py](#create_opticgroups_from_xmlpy)
- [create_opticgroups_from_mdoc.py](#create_opticgroups_from_mdocpy)
- [extract_particles_coords_star.py](#extract_particles_coords_starpy)
- [filter_astigmatism_star.py](#filter_astigmatism_starpy)
- [flip_particles_coordinates.py](#flip_particles_coordinatespy)
- [get_absolute_apix.py](#get_absolute_apixpy)
- [heatmap_orient_star.py](#heatmap_orient_starpy)
- [helix_correct_star.py](#helix_correct_starpy)
- [join_star.py](#join_starpy)
- [json2star.py](#json2starpy)
- [math_star.py](#math_starpy)
- [math_exp_star.py](#math_exp_starpy)
- [metadata.py](#metadatapyy)
- [micrograph_star_from_particles_star.py](#micrograph_star_from_particles_starpy)
- [particles_star_to_box.py](#particles_star_to_boxpy)
- [particles_star_to_coords_star.py](#particles_star_to_coords_starpy)
- [plot_star.py](#plot_starpy)
- [print_symmetry_matrices.py](#print_symmetry_matricespy)
- [regular_box_pattern_around_center_coordinate.py](#regular_box_pattern_around_center_coordinatepy)
- [rel31_to_rel30_star.py](#rel31_to_rel30_starpy)
- [remove_preferred_orient.py](#remove_preferred_orientpy)
- [remove_preferred_orient_hlpx.py](#remove_preferred_orient_hlpxpy)
- [rename_foilhole_star.py](#rename_foilhole_starpy)
- [rotate_particles_star.py](#rotate_particles_starpy)
- [scf_star.py](#scf_starpy)
- [select_maxprob_sym_copy_ptcls.py](#select_maxprob_sym_copy_ptclspy)
- [select_orientations_star.py](#select_orientations_starpy)
- [select_rand_sym_copy_ptcls.py](#select_rand_sym_copy_ptclspy)
- [select_values_star.py](#select_values_starpy)
- [split_particles_to_micrographs.py](#split_particles_to_micrographspy)
- [split_stacks.py](#split_stackspy)
- [stats_star.py](#stats_starpy)
- [unbin_coordinates.py](#unbin_coordinatespy)
- [xflip_particles_star.py](#xflip_particles_starpy)
- [yflip_particles_star.py](#yflip_particles_starpy)

## Install
To install the scripts, clone the repository and add the path to the scripts to your PATH variable.

Some of the script need external libraries listed in requirements.txt. Install them ideally into separate virtual environment:
```
# Clone the repository
git clone https://github.com/fuzikt/starpy.git

# Change to the directory
cd starpy

# Create a virtual environment
python -m venv starpy_env

# Activate the virtual environment
source starpy_env/bin/activate

# Install requirements from the requirements.txt file
pip install -r requirements.txt
```

## General usage
All scripts are designed to be used in the command line. To show the help of the script use the **--h** parameter.

The input and output files are defined by the **--i** and **--o** parameters. 

In many scripts (see the description below) there is possibility to pass **STDIN** as input and **STDOUT** as output. This makes it possible to chain the result of one script to another using the pipe |.

If the --i parameter is not defined, the script will read from the standard input (STDIN).
If the --o parameter is not defined, the script will write to the standard output (STDOUT).

Example 1: Plot the astigmatism calculated by math_exp_star.py of particles from input.star using plot_star.py
```
math_exp_star.py --i input.star --exp "abs(rlnDefocusU-rlnDefocusV)" --res_lb rlnResult | plot_star.py --lby rlnResult --hist_bin 20 --show
```

Example 2: Y-flip the particle from class2, then rotate them by r:15, t:20, p:150, remove preferred orientations and plot the orientations.
```
yflip_particles_star.py --i input.star --cls_nr 2 | rotate_particles_star.py --rot 15 --tilt 20 --psi 150 | remove_preferred_orient_hlpx.py | heatmap_orient_star.py --show
```

Example 3: Select particles from input.star where the difference between rlnAngleRot and rlnAngleTilt is less than 5 and store it in output.star.
```
math_exp_star.py --i input.star --exp  "1" --sel_exp "abs(rlnAngleRot-rlnAngleTilt)<5" --res_lb rlnResult  --def_val 0 | select_values_star.py --o output.star --lb rlnResult --op ">" --val 0
```

## add_beamtiltclass_star.py
! only Relion <=3.0 format star files !
Add beamtilt class to the particles. Script adds rlnBeamTiltClass extracted from the micrograph name (in FoilHoleXXXX.mrc FEI format).
```
  --i    Input STAR filename (Default: STDIN).
  --o    Output STAR filename (Default: STDOUT).
```

## add_remove_label.py
Adds or removes labels from star file.
```
--i         Input STAR filename (Default: STDIN).
--o         Output STAR filename (Default: STDOUT).
--add       Add new label to the star file.
--rm        Remove label from the star file.
--lb        Label to be added or removed. Use comma separated label values to add or remove multiple labels. Default: None
--val       Value filled for added labels. Use comma separated values if adding multiple labels. Default: 0
--data      Data table from star file to be used (Default: data_particles).
```

Example 1: Remove rlnCoordinateY from input.star 
``` 
add_remove_label.py --i input.star --o output.star --lb rlnCoordinateY --rm
```

Example 2: Remove rlnCoordinateX,rlnCoordinateY from input.star 
``` 
add_remove_label.py --i input.star --o output.star --lb rlnCoordinateX,rlnCoordinateY --rm
```

Example 3: Add rlnCoordinateX,rlnCoordinateY with default values 10,20 respectively
``` 
add_remove_label.py --i input.star --o output.star --lb rlnCoordinateX,rlnCoordinateY --add --val 10,20
```

## analyze_orientation_distances_star.py
Calculates the spatial distance and angular distance between corresponding particles in --i1 and --i2. Output contains the particles from --i1 with additional columns for the spatial (rlnSpatDist), angular distances (rlnAngDist), rlnOriginXAngstDiff, rlnOriginYAngstDiff, rlnAngleRotDiff , rlnAngleTiltDiff, and rlnAnglePsiDiff.
```
  --i1    Input1 STAR filename (Default: STDIN).
  --i2    Input2 STAR filename (Default: STDIN).e
  --o     Output STAR filename (Default: STDOUT).
```

## assign_column_star.py
Add label (col_lb) to Input1 and assigns values to it from Input2 where the label (comp_lb) of Input2 matches Input1
```        
  --i1        Input1 STAR filename (Default: STDIN).
  --i2        Input2 STAR filename (Default: STDIN)..
  --o         Output STAR filename (Default: STDOUT).
  --data  Data table from star file to be used, Default: data_particles
  --col_lb    Label of the new column assigned to Input1; Default: rlnDefocusU
  --comp_lb   Compare label used for Input1 and Input2 for value assignment. Default:rlnMicrographName
```
Example 1: Assign values of DefocusU from input2.star as a column to input1.star where the value of column rlnMicrographName matches in both inputs. 
``` 
assign_column_star.py --i1 input1.star --i2 input2.star --o output.star --col_lb rlnDefocusU --comp_lb rlnMicrographName
```

## binnig_correct_star.py
Binning correct original star file according to the binning factor. Correcting rlnOriginX, rlnOriginY, pixel size, and particle suffix.
```
  --i             Input STAR filename with particles.
  --o             Output STAR filename.
  --bin_factor    Binning factor.
  --suf_orig      Original suffix to replace (e.g. _512.mrcs)
  --suf_new       New suffix to use for replacement (e.g. _256.mrcs)
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

## create_opticgroups_from_filename.py
! only Relion >=3.1 format star files !

Creates optic groups according to acquisition position identifier (number) in the FoilHole_XXX_Data_YYY_ZZZ_AAA_BBB-CCC.mrc filename of the micrograph.
```
  --i           Input STAR filename.
  --o,          Output STAR filename.
  --word_count  Position of the acquisition position identifier in the FoilHole_XXX_Data_YYY_ZZZ.mrc filename. Default: 4 (th word).")
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

## extract_particles_coords_star.py
Remove other columns than particle coords from star file.
```
  --i    Input STAR filename (Default: STDIN).
  --o    Output STAR filename (Default: STDOUT). 
```

## filter_astigmatism_star.py
Limit astigmatism of particles or micrographs in star file.
```
  --i      Input STAR filename (Default: STDIN).
  --o      Output STAR filename (Default: STDOUT).
  --astg   Max astigmatism in Angstroms. Default: 1000
  --res    Minimum resolution in Angstroms. Default: 0 (off)
  --data   Data table from star file to be used (Default: data_particles).
```

## flip_particles_coordinates.py
Flip (mirror) X/Y coordinates of particles in particles star file or coordinates star files in a directory.
```
  --i           Input particles STAR file.
  --o           Output particles STAR file.
  --i_dir       Input directory with coordinates STAR files.
  --o_dir       Output directory.
  --flipX       Flip coordinates along X-axis
  --flipY       Flip coordinates along Y-axis
  --axis_size   Size of micrograph in pixels along the flipping axis.
```

## get_absolute_apix.py
Calculates the absolute apix for the optics groups according to https://www3.mrc-lmb.cam.ac.uk/relion/index.php/Pixel_size_issues
```
  --i         Input STAR filename (Default: STDIN). 
```

## heatmap_orient_star.py
Generates heatmap of particle orientations from star file. Cartesian (hexbin, healpix, legacy) and mollweide (healpix, legacy) representations are generated. For symmetrical particles, first make symmetry expand of the star file (relion_particle_symmetry_expand).

Requires:
- Matplotlib
- Numpy
- healpy
```
  --i               Input STAR filename with particles and orientations (Default: STDIN).
  --o               Output files prefix. Default: heatmap_orient
  --sym             Symmetry used form symmetry expansion of the input star file. Default: C1
  --show            Only shows the resulting heatmap. Does not store any output file.
  --format          Output format. Available formats: png, svg, jpg, tif. Default: png
  --cmap            Color map used for the heatmap. Matplotlib colormap names accepted. Recommended: jet, inferno, viridis, turbo. (Default: turbo)")
  --mask_zero       Mask zero values not to be represented by color. (i.e. zero values represented by white)")
  --grid_size       Grid size of the hexbin grid. The higher number the finer sampling. Default: 50")
  --hlpx            Create HealPix style maps
  --hlpx_order      HealPix sampling order used for plotting (2->15deg,3->7.5deg, 4->3.75). Default: 4 (3.75deg)
  --no_graticule    Do not plot graticule on HealPix maps.
  --vmin            Min values represented on color bar. Default: -1 (auto)
  --vmax            Max values represented on color bar. Default: -1 (auto)
  --legacy          Creates old (original) style heatmaps
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
  --i1    Input1 STAR filename (Default: STDIN).
  --i2    Input2 STAR filename (Default: STDIN).
  --o     Output STAR filename (Default: STDOUT).
  --data  Data table from star file to be used, Default: data_particles
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
  --i         Input STAR filename (Default: STDIN).
  --o         Output STAR filename (Default: STDOUT).
  --data  Data table from star file to be used, Default: data_particles
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

## math_exp_star.py
Performs complex math operations on star file values defined by user provided expression.

Requires:
- cexprtk

All the supported math expressions can be found at: http://www.partow.net/programming/exprtk/index.html

```
  --i        Input STAR filename (Default: STDIN).
  --o        Output STAR filename (Default: STDOUT).
  --data     Data table from star file to be used (Default: data_particles).
  --res_lb   Label used for storing the result (e.g. rlnAngleTilt, rlnDefocusU...). If the label is not present in input file, it will be created. Default: rlnResult
  --exp      Expression to be evaluated. Enclose in double quotes!!! (e.g. "(rlnDefocusU - rlnDefocusV)/2")
  --sel_exp  Expression used for selection of particles on which the --exp will be evaluated. Enclose in double quotes!!!  (e.g. "(rlnDefocusU-1500)<20000"), Default empty => all particles
  --def_val  Default value of non-calculated results when --rel_lb is not present in --i. Default: 0.0"
```
Example 1: Add 15 deg to rlnAngleTilt.
```
math_exp_star.py --i input.star --o output.star --lb_res rlnAngleTilt --exp "rlnAngleTilt+15"
```
Example 2: Calculate the astigmatism and store it under label rlnAstigmatism.
```
math_exp_star.py --i input.star --o output.star --lb_res rlnAstigmatism --exp "abs(rlnDefocusU-rlnDefocusV)"
```
Example 3: Multiply rlnOriginX by 2 if (rlnOriginX+rlnOriginY) is less than 50.
```
math_exp_star.py --i input.star --o output.star --lb_res rlnOriginX --exp "rlnOriginX*2" --sel_exp "(rlnOriginX+rlnOriginY)<50"
```
Example 4: Compute cosine of rlnAngleRot and store it under label rlnCosAngleRot.
```
math_exp_star.py --i input.star --o output.star --lb_res rlnCosAngleRot --exp "cos(deg2rad(rlnAngleRot))"
```
Example 5: Set rlnResult to 150 if (rlnOriginX-rlnOriginY)<rlnOriginZ. If the condition is not fulfilled the default value of rlnResult is 20.
```
math_exp_star.py --i input.star --o output.star --lb_res rlnResult --exp "150" --sel_exp "(rlnOriginX-rlnOriginY)<rlnOriginZ" --def_val 20
```


## metadata.py
Base library required by all scripts.

## micrograph_star_from_particles_star.py
Create a micrographs star containing unique micrograph names file form input particles star file.
```
  --i    Input STAR filename (Default: STDIN).
  --o    Output STAR filename (Default: STDOUT).
```

## particles_star_to_box.py
Extracts coordinates from particles STAR file and saves as per micrograph box files.
```
  --i         Input STAR filename with particles.
  --o         Output directory where the box files will be stored.
  --box_size  Box size. Default: 256
```

## particles_star_to_coords_star.py 
Extracts coordinates from particles STAR file and saves as per micrograph
coords star files.
```
  --i         Input STAR filename with particles.
  --o         Output directory where the coords files will be stored.
```

## plot_star.py
Plots values of defined label(s) from STAR file.
```        
  --i              Input STAR filename. Multiple files allowed separated by comma or by space (then all must be enclosed in double quotes) (Default: STDIN).
  --data           Data table from star file to be used (Default: data_particles).
  --lbx            Label used for X axis (Default: None). If not defined, X axis is per record in the data table (e.g. per particle)
  --lby            Labels used for plot (Y-axis values). Accepts multiple labels to plot (separated by comma, or by space (then all must be enclosed in double quotes)).
  --hist_bins      Number of bins for plotting a histogram. If set to >0 then histogram is plotted.
  --scatter        Sets scatter type of plot.")
  --threshold      Draw a threshold line at the defined y value. Multiple values accepted, separated by comma (e.g. 0.5,0.143). (Default: none)
  --thresholdx     Draw a threshold line at the defined x value. Multiple values accepted, separated by comma (e.g. 0.5,0.143). (Default: none)"
  --multiplotY     Create separate plot for each --lby in a grid (Default: 1,1 = single plot). Define in parameter number of rows and columns  (e.g. --multiplotY \"2,3\")
  --multiplotFile  Create separate plot for each file in --i in a grid (Default: 1,1 = single plot). Define in parameter number of rows and columns  (e.g. --multiplotFile \"2,3\")
```
Example 1: Creates a scatter plot of DefocusU values per particle
```
plot_star.py --i input.star --lby rlnDefocusU --scatter 
```

Example 2: Creates a histogram (in 50 bins) of DefocusU values per particle
```
plot_star.py --i input.star --lby rlnDefocusU --hist_bins 50 
```

Example 3: Creates a scatter plot of DefocusU and DefocusV values in single plot
```
plot_star.py --i input.star --lby rlnDefocusU,rlnDefocusV --scatter
```

Example 4: Creates a scatter plot of DefocusU dependent on DefocusV values in single plot
```
plot_star.py --i input.star --lby rlnDefocusU --lbx rlnDefocusV --scatter
```

Example 5: Plot rlnDefocusU,rlnDefocusU values in 2 separate plots (1 row 2 plots)
```
plot_star.py --i micrographs_all_gctf_og.star --lby rlnDefocusU,rlnDefocusV --data data_micrographs --hist_bins 50 --multiplotY "1,2"
```
Note: If grid is < than the number of --lby => it iterates over the tiles from beginning.

Example 6: Plot rlnDefocusU, rlnDefocusV values of 2 datasets in a 2 plots (histogram)
```
plot_star.py --i micrographs_all_gctf_og.star,micrographs_all_gctf_og_200.star --lby rlnDefocusU,rlnDefocusV --data data_micrographs --hist_bins 50 --multiplotFile 1,2
```

Example 7: Plot out FSC from PostProcess
```
plot_star.py --i PostpProcess/job001/post.star --lby rlnFourierShellCorrelationCorrected,rlnFourierShellCorrelationUnmaskedMaps,rlnCorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps --lbx rlnResolution --data data_fsc --threshold 0.143
```

Example 8: Plot (compare) FSC curves from 2 separate postprocess with multiple thresholds set
```
plot_star.py --i "PostpProcess/job001/post.star PostpProcess/job002/post.star" --lby rlnFourierShellCorrelationCorrected --lbx rlnResolution --data data_fsc --threshold 0.143,0.3,0.5
```

Example 9: Plot FSC from all iterations of an auto-refine run
```
plot_star.py --i "$(ls Refine3D/job003/run_it*_half1_model.star)" --lby rlnGoldStandardFsc --lbx rlnResolution --data data_model_class_1
```

## print_symmetry_matrices.py
Prints out symmetry matrices in desired format.
```
    --sym       Symmetry type (Default: C1).")
    --o         Output filename (Default: STDOUT - print to screen).
    --biomt     Print symmetry matrices in REMARK 350 BIOMT format.
    --mtrix     Print symmetry matrices in PDB MTRIX format.
    --text      Print symmetry matrices in pure text format.
    --x         X coordinate for symmetry center in Angstroms (Default: 0.0).
    --y         Y coordinate for symmetry center in Angstroms (Default: 0.0).
    --z         Z coordinate for symmetry center in Angstroms (Default: 0.0).
```

## regular_box_pattern_around_center_coordinate.py
Creates a regular pattern of small boxes around the center coordinate of the particle.
```
--i             Input STAR filename with particles.
--o             Output directory where the coords files will be stored.
--orig_box      Size of the box in pixels around the center coordinate of the original particles. (Default: 512)
--pattern_box   Size of the box in the regular pattern. (Default: 128)
--overlap       Overlap in percents between the neighboring boxes in pattern. (Default: 30)
--sph_mask      If set then only boxes inside a circular mask touching the orig_box are included.
```

## rel31_to_rel30_star.py
Converts particle star from RELION 3.1 format to RELION 3.0 format.
```
  --i    Input STAR filename (RELON 3.1 format).
  --o    Output STAR filename. 
```

## remove_preferred_orient.py
!!! DEPRECATED USE: remove_preferred_orient_hlpx.py, which gives better results !!!
Remove particles with overrepresented orientations. Average count of particles at each orientation is calculated. Then the count of particles that are n-times SD over the average is modified by retaining the particles with the highest rlnMaxValueProbDistribution.
```
  --i      Input STAR filename (Default: STDIN).
  --o      Output STAR filename (Default: STDOUT).
  --sd     This many times SD above the average count will be representations kept. Default: 3
```

## remove_preferred_orient_hlpx.py
Remove particles with overrepresented orientations by sorting them into HealPix based orientation bins. Average count of particles per orientation bin is calculated. Then the count of particles that are n-times SD over the average is modified by retaining the particles with the highest rlnMaxValueProbDistribution.
```
  --i           Input STAR filename (Default: STDIN).
  --o           Output STAR filename (Default: STDOUT).
  --hlpx_order  HealPix sampling order used for sorting particles into orientation bins (2->15deg,3->7.5deg, 4->3.75). Default: 4 (3.75deg)
  --sd          This many times SD above the average count will be representations kept. Default: 3
```

## rename_foilhole_star.py
Deprecated - need to be rewritten

## rotate_particles_star.py
Performs rotation of particles according to given Euler angles.
```
  --i       Input STAR filename with particles. (Default: STDIN).
  --o       Output STAR filename. (Default: STDOUT).
  --rot     Rotation Euler angle. Default 0
  --tilt    Tilt Euler angle. Default 0
  --psi     Psi Euler angle. Default 0
  --x       Shift along X axis. Default 0
  --y       Shift along Y axis. Default 0
  --z       Shift along Z axis. Default 0
  --cls_nr  Comma-separated list of class numbers to be flipped.. (Default: -1 => off)
```
Example:
```
rotate_particles_star.py --i input.star --o output.star --rot 15 --tilt 20 --psi 150
```

## scf_star.py
Calculates the SCF* (Sampling Compensation Factor) for particle orientation distribution in STAR file.

Described in: Baldwin, P.R. and D. Lyumkis, Non-uniformity of projection distributions attenuates resolution in Cryo-EM.Prog Biophys Mol Biol, 2020. 150: p. 160-183.
```
  --i                 Input STAR filename (Default: STDIN).
  --o                 Output STAR filename (Default: STDOUT).
  --sym               Symmetry applied to the input particles (Default: C1).
  --tilt_angle        Tilt angle (cannot be used together with --sym).
  --samples           The number of random particle orientations from input to use (Default 0 => all particles).
```

## select_maxprob_sym_copy_ptcls.py
Select one orientation per particle from 3D classified symmetry expanded star files according to the greatest value of rlnMaxValueProbDistribution.

```
  --i    Input STAR filename (Default: STDIN).
  --o    Output STAR filename (Default: STDOUT). 
```
Example: You created a C5 symmetry expanded star file that was 3D classified into 5 classes. You select the best looking class, which should in theory contain 1/5 of the particles from the symmetry expanded star. Because the classification is not perfect there are multiple redundant (symmetry) copies of some of the particles present in the selected class. To filter out only a single copy (unique) of every particle you can use this script, which will chose the particle with the greatest value of rlnMaxValueProbDistribution.
```
select_maxprob_sym_copy_ptcls.py --i selected_class.star --o selected_class_unique.star
```

## select_orientations_star.py
Limit orientations of particles in STAR file. Select particles that are in the defined range of ROT, TILT, PSI angle.

```
  --i           Input STAR filename (Default: STDIN).
  --o           Output STAR filename (Default: STDOUT).
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
  --i    Input STAR filename (Default: STDIN).
  --o    Output STAR filename (Default: STDOUT). 
```

## select_values_star.py
Select particles complying with selection rule on specified label.
``` 
  --i        Input STAR filename (Default: STDIN).
  --o        Output STAR filename (Default: STDOUT).
  --data  Data table from star file to be used, Default: data_particles 
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

## split_particles_to_micrographs.py
Converts particle MRC stacks into separate MRC files and generate micrograph star file for them. In comparison to split_stacks.py, it is easier to keep track of the original particle in the resulting star file.
```
  --i        Input STAR filename.
  --o        Output prefix.
```

Example:
```
# Let's assume you have following input.star file:
_rlnImageName
_rlnMicrographName
1@particles/mic123682.mrcs Micrographs/mic123682.mrc
6@particles/mic123682.mrcs Micrographs/mic123682.mrc
2@particles/mic777772.mrcs Micrographs/mic777772.mrc

# running the following command
split_particles_to_micrographs.py --i input.star --o splitParticles

# will create a directory named splitParticles and a file splitParticles.star which will look like this:
_rlnMicrographName
splitParticles/mic123682_1.mrc
splitParticles/mic123682_6.mrc
splitParticles/mic777772_2.mrc

# Note: All other labels except rlnImageName remains in the output file preserved
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
  --i     Input STAR filename (Default: STDIN).
  --lb    Labels used for statistics (Default: ALL). Multiple labels can be used enclosed in double quotes. (e.g. "rlnAngleTilt rlnAngleRot")
  --data  Data table from star file to be used, Default: data_particles
```
Example 1: Print out statistics on particles - all labels:
```
stats_star.py --i input.star
```
Example 2: Print out statistics on data_model_class_1 - all labels
```
stats_star.py --i run_model.star --data data_model_class_1
```
Example 3: Print out statistics on rlnAngleTilt:
```
stats_star.py --i input.star --lb rlnAngleTilt
```
Example 4: Print out statistics on rlnAngleTilt, rlnAngleRot and rlnAnglePsi
```
stats_star.py --i input.star --lb "rlnAngleTilt rlnAngleRot rlnAnglePsi"
```

## unbin_coordinates.py
Unbin particle coordinate star files.
```
  --i    Input directory with coordinates STAR files.
  --o    Output directory.
  --bin  Binning factor used (--bin 10 will multiply input coordinates by 10.)
```

## xflip_particles_star.py
Performs transformation of euler angles to produce X-flipped reconstruction. The resulting map is the same as if "--invert_hand" is applied on the map in relion_image_handler.
```
  --i       Input STAR filename (Default: STDIN).
  --o       Output STAR filename (Default: STDOUT).
  --cls_nr  Comma-separated list of class numbers to be flipped.. (Default: -1 => off) 
```

## yflip_particles_star.py
Performs transformation of euler angles to produce Y-flipped reconstruction.
```
  --i       Input STAR filename (Default: STDIN).
  --o       Output STAR filename (Default: STDOUT).
  --cls_nr  Comma-separated list of class numbers to be flipped.. (Default: -1 => off)
```
