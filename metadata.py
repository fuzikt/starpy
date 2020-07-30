# **************************************************************************
# * Authors:  Tibor Fuzik (tibor.fuzik@ceitec.mnuni.cz)
# * Authors:  J. M. de la Rosa Trevin (delarosatrevin@gmail.com)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# **************************************************************************

import sys

try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip
from collections import OrderedDict
import copy

LABELS = {
    'rlnAccumMotionEarly': float,  # Accumulated global motion during the first frames of the movie': in A)
    'rlnAccumMotionLate': float,  # Accumulated global motion during the last frames of the movie': in A)
    'rlnAccumMotionTotal': float,  # Accumulated global motion during the entire movie': in A)
    'rlnAccuracyRotations': float,  # Estimated accuracy': in degrees) with which rotations can be assigned
    'rlnAccuracyTranslations': float,  # Estimated accuracy': in pixels) with which translations can be assigned
    'rlnAccuracyTranslationsAngst': float,  # Estimated accuracy': in Angstroms) with which translations can be assigned
    'rlnAdaptiveOversampleFraction': float,
    # Fraction of the weights that will be oversampled in a second pass of the adaptive oversampling strategy
    'rlnAdaptiveOversampleOrder': int,
    # Order of the adaptive oversampling': 0=no oversampling, 1= 2x oversampling; 2= 4x oversampling, etc)
    'rlnAmplitudeContrast': float,  # Amplitude contrast': as a fraction, i.e. 10% = 0.1)
    'rlnAmplitudeCorrelationMaskedMaps': float,
    # Correlation coefficient between amplitudes in Fourier shells of masked maps
    'rlnAmplitudeCorrelationUnmaskedMaps': float,
    # Correlation coefficient between amplitudes in Fourier shells of unmasked maps
    'rlnAnglePsi': float,  # Third Euler, or in-plane angle': psi, in degrees)
    'rlnAnglePsiFlip': bool,  # Flag to indicate that psi prior angle has been flipped
    'rlnAnglePsiFlipRatio': float,
    # Flip ratio of bimodal psi prior': 0~0.5, 0 means an ordinary prior, 0.5 means a perfect bimodal prior)
    'rlnAnglePsiPrior': float,  # Center of the prior': in degrees) on the third Euler angle': psi)
    'rlnAngleRot': float,  # First Euler angle': rot, in degrees)
    'rlnAngleRotFlipRatio': float,
    # Flip ratio of bimodal rot prior': 0~0.5, 0 means an ordinary prior, 0.5 means a perfect bimodal prior)
    'rlnAngleRotPrior': float,  # Center of the prior': in degrees) on the first Euler angle': rot)
    'rlnAngleTilt': float,  # Second Euler angle': tilt, in degrees)
    'rlnAngleTiltPrior': float,  # Center of the prior': in degrees) on the second Euler angle': tilt)
    'rlnAngstromResolution': float,  # Resolution': in Angstroms)
    'rlnAreaId': int,  # ID': i.e. a unique number) of an area': i.e. field-of-view)
    'rlnAreaName': str,  # Name of an area': i.e. field-of-view)
    'rlnAutoLocalSearchesHealpixOrder': int,
    # Healpix order': before oversampling) from which autosampling procedure will use local angular searches
    'rlnAutopickFigureOfMerit': float,  # Autopicking FOM for a particle
    'rlnAvailableMemory': float,  # Available memory per computing node': i.e. per MPI-process)
    'rlnAverageNrOfFrames': int,  # Number of movie frames that one averages over upon extraction of movie-particles
    'rlnAveragePmax': float,  # Average value': over all images) of the maxima of the probability distributions
    'rlnAverageValue': float,  # Average value for the pixels in an image
    'rlnBeamTiltClass': int,  # Beam-tilt class of a particle
    'rlnBeamTiltX': float,  # Beam tilt in the X-direction': in mrad)
    'rlnBeamTiltY': float,  # Beam tilt in the Y-direction': in mrad)
    'rlnBestResolutionThusFar': float,  # The highest resolution that has been obtained in this optimization thus far
    'rlnBfactorUsedForSharpening': float,  # Applied B-factor in the sharpening of the map
    'rlnBodyKeepFixed': int,  # Flag to indicate whether to keep a body fixed': value 1) or keep on refining it': 0)
    'rlnBodyMaskName': str,  # Name of an image that contains a [0,1] body mask for multi-body refinement
    'rlnBodyReferenceName': str,
    # Name of an image that contains the initial reference for one body of a multi-body refinement
    'rlnBodyRotateDirectionX': float,  # X-component of axis around which to rotate this body
    'rlnBodyRotateDirectionY': float,  # Y-component of axis around which to rotate this body
    'rlnBodyRotateDirectionZ': float,  # Z-component of axis around which to rotate this body
    'rlnBodyRotateRelativeTo': int,
    # Number of the body relative to which this body rotates': if negative, use 'rlnBodyRotateDirectionXYZ)
    'rlnBodySigmaAngles': float,
    # Width of prior on all three Euler angles of a body in multibody refinement': in degrees)
    'rlnBodySigmaOffset': float,  # Width of prior on origin offsets of a body in multibody refinement': in pixels)
    'rlnBodySigmaOffsetAngst': float,
    # Width of prior on origin offsets of a body in multibody refinement': in Angstroms)
    'rlnBodySigmaPsi': float,  # Width of prior on psi angles of a body in multibody refinement': in degrees)
    'rlnBodySigmaRot': float,  # Width of prior on rot angles of a body in multibody refinement': in degrees)
    'rlnBodySigmaTilt': float,  # Width of prior on tilt angles of a body in multibody refinement': in degrees)
    'rlnBodyStarFile': str,  # Name of STAR file with body masks and metadata
    'rlnChangesOptimalClasses': float,
    # The number of particles that changed their optimal clsas assignment in the last iteration
    'rlnChangesOptimalOffsets': float,  # The average change in optimal translation in the last iteration': in pixels)
    'rlnChangesOptimalOrientations': float,
    # The average change in optimal orientation in the last iteration': in degrees)
    'rlnChromaticAberration': float,  # Chromatic aberration': in millimeters)
    'rlnClassDistribution': float,
    # Probability Density Function of the different classes': i.e. fraction of images assigned to each class)
    'rlnClassNumber': int,  # Class number for which a particle has its highest probability
    'rlnClassPriorOffsetX': float,  # Prior in the X-offset for a class': in pixels)
    'rlnClassPriorOffsetY': float,  # Prior in the Y-offset for a class': in pixels)
    'rlnCoarseImageSize': int,
    # Current size of the images to be used in the first pass of the adaptive oversampling strategy': may be smaller than the original image size)
    'rlnComment': str,  # A metadata comment': This is treated in a special way)
    'rlnConvergenceCone': float,  # Convergence cone': in mrad)
    'rlnCoordinateX': float,  # X-Position of an image in a micrograph': in pixels)
    'rlnCoordinateY': float,  # Y-Position of an image in a micrograph': in pixels)
    'rlnCoordinateZ': float,  # Z-Position of an image in a 3D micrograph, i.e. tomogram': in pixels)
    'rlnCorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps': float,
    # FSC value after masking of the randomized-phases maps
    'rlnCorrelationFitGuinierPlot': float,  # The correlation coefficient of the fitted line through the Guinier-plot
    'rlnCtfAstigmatism': float,  # Absolute value of the difference between defocus in U- and V-direction': in A)
    'rlnCtfBfactor': float,  # B-factor': in A^2) that describes CTF power spectrum fall-off
    'rlnCtfDataAreCtfPremultiplied': bool,
    # Flag to indicate that the input images have been premultiplied with their CTF
    'rlnCtfDataArePhaseFlipped': bool,  # Flag to indicate that the input images have been phase-flipped
    'rlnCtfFigureOfMerit': float,  # Figure of merit for the fit of the CTF': not used inside relion_refine)
    'rlnCtfImage': str,  # Name of an image with all CTF values
    'rlnCtfMaxResolution': float,  # Estimated maximum resolution': in A) of significant CTF Thon rings
    'rlnCtfPowerSpectrum': str,  # Power spectrum for CTF estimation
    'rlnCtfScalefactor': float,  # Linear scale-factor on the CTF': values between 0 and 1)
    'rlnCtfValidationScore': float,  # Gctf-based validation score for the quality of the CTF fit
    'rlnCtfValue': float,  # Value of the Contrast Transfer Function
    'rlnCurrentImageSize': int,  # Current size of the images used in the refinement
    'rlnCurrentIteration': int,  # The number of the current iteration
    'rlnCurrentResolution': float,  # Current resolution where SSNR^MAP drops below 1': in 1/Angstroms)
    'rlnDataDimensionality': int,  # Dimensionality of the data': 2D/3D)
    'rlnDataType': int,  # Type of data stored in an image': e.g. int, RFLOAT etc)
    'rlnDefocusAngle': float,  # Angle between X and defocus U direction': in degrees)
    'rlnDefocusU': float,  # Defocus in U-direction': in Angstroms, positive values for underfocus)
    'rlnDefocusV': float,  # Defocus in V-direction': in Angstroms, positive values for underfocus)
    'rlnDetectorPixelSize': float,  # Pixel size of the detector': in micrometers)
    'rlnDiff2RandomHalves': float,
    # Power of the differences between two independent reconstructions from random halves of the data
    'rlnDifferentialPhaseResidualMaskedMaps': float,  # Differential Phase Residual in Fourier shells of masked maps
    'rlnDifferentialPhaseResidualUnmaskedMaps': float,  # Differential Phase Residual in Fourier shells of unmasked maps
    'rlnDoAutoRefine': bool,  # Flag to indicate that 3D auto-refine procedure is being used
    'rlnDoCorrectCtf': bool,  # Flag to indicate that CTF-correction should be performed
    'rlnDoCorrectMagnification': bool,
    # Flag to indicate that': per-group) magnification correction should be performed
    'rlnDoCorrectNorm': bool,  # Flag to indicate that': per-image) normalisation-error correction should be performed
    'rlnDoCorrectScale': bool,
    # Flag to indicate that internal': per-group) intensity-scale correction should be performed
    'rlnDoExternalReconstruct': bool,
    # Flag to indicate that the reconstruction will be performed outside relion_refine, e.g. for learned priors
    'rlnDoFastSubsetOptimisation': bool,  # Use subsets of the data in the earlier iterations to speed up convergence
    'rlnDoHelicalRefine': bool,  # Flag to indicate that helical refinement should be performed
    'rlnDoIgnoreCtfUntilFirstPeak': bool,  # Flag to indicate that the CTFs should be ignored until their first peak
    'rlnDoMapEstimation': bool,  # Flag to indicate that MAP estimation should be performed': otherwise ML estimation)
    'rlnDoOnlyFlipCtfPhases': bool,  # Flag to indicate that CTF-correction should only comprise phase-flipping
    'rlnDoRealignMovies': bool,  # Flag to indicate that individual frames of movies are being re-aligned
    'rlnDoSkipAlign': bool,
    # Flag to indicate that orientational': i.e. rotational and translational) searches will be omitted from the refinement, only marginalisation over classes will take place
    'rlnDoSkipRotate': bool,
    # Flag to indicate that rotational searches will be omitted from the refinement, only marginalisation over classes and translations will take place
    'rlnDoSolventFlattening': bool,
    # Flag to indicate that the references should be masked to set their solvent areas to a constant density
    'rlnDoSolventFscCorrection': bool,  # Flag to indicate that the FSCs should be solvent-corrected during refinement
    'rlnDoSplitRandomHalves': bool,
    # Flag to indicate that the data should be split into two completely separate, random halves
    'rlnDoStochasticEM': bool,
    # Flag to indicate that stochastic EM-optimisation should be performed': an alternative to SGD)
    'rlnDoStochasticGradientDescent': bool,
    # Flag to indicate that SGD-optimisation should be performed': otherwise expectation maximisation)
    'rlnDoZeroMask': bool,
    # Flag to indicate that the surrounding solvent area in the experimental particles will be masked to zeros': by default random noise will be used
    'rlnEnabled': bool,  # Not used in RELION, only included for backward compatibility with XMIPP selfiles
    'rlnEnergyLoss': float,  # Energy loss': in eV)
    'rlnEstimatedResolution': float,  # Estimated resolution': in A) for a reference
    'rlnEvenZernike': str,  # Coefficients for the symmetrical Zernike polynomials
    'rlnExperimentalDataStarFile': str,  # STAR file with metadata for the experimental images
    'rlnExtReconsDataImag': str,
    # Name of the map with the imaginary components of the input data array for the external reconstruction program
    'rlnExtReconsDataReal': str,
    # Name of the map with the real components of the input data array for the external reconstruction program
    'rlnExtReconsResult': str,  # Name of the output reconstruction from the external reconstruction program
    'rlnExtReconsResultStarfile': str,  # Name of the output STAR file with updated FSC or tau curves
    'rlnExtReconsWeight': str,  # Name of the map with the input weight array for the external reconstruction program
    'rlnFinalResolution': float,  # Final estimated resolution after postprocessing': in Angstroms)
    'rlnFittedInterceptGuinierPlot': float,  # The fitted intercept of the Guinier-plot
    'rlnFittedSlopeGuinierPlot': float,  # The fitted slope of the Guinier-plot
    'rlnFixSigmaNoiseEstimates': bool,
    # Flag to indicate that the estimates for the power spectra of the noise should be kept constant
    'rlnFixSigmaOffsetEstimates': bool,
    # Flag to indicate that the estimates for the stddev in the origin offsets should be kept constant
    'rlnFixTauEstimates': bool,
    # Flag to indicate that the estimates for the power spectra of the signal': i.e. the references) should be kept constant
    'rlnFourierCompleteness': float,  # Fraction of Fourier components': per resolution shell) with SNR>1
    'rlnFourierMask': str,  # Name of an FFTW-centred Fourier mask to be applied to the Projector for refinement.
    'rlnFourierShellCorrelation': float,  # FSC value': of unspecified type, e.g. masked or unmasked)
    'rlnFourierShellCorrelationCorrected': float,
    # Final FSC value: i.e. after correction based on masking of randomized-phases maps
    'rlnFourierShellCorrelationMaskedMaps': float,  # FSC value after masking of the original maps
    'rlnFourierShellCorrelationParticleMaskFraction': float,
    # CisTEM-like correction of unmasked FSCs, based on fraction of white pixels in solvent mask
    'rlnFourierShellCorrelationParticleMolWeight': float,
    # CisTEM-like correction of unmasked FSCs, based on ordered molecular weight estimate
    'rlnFourierShellCorrelationUnmaskedMaps': float,  # FSC value before masking of the original maps
    'rlnFourierSpaceInterpolator': int,  # The kernel used for Fourier-space interpolation': NN=0, linear=1)
    'rlnGoldStandardFsc': float,
    # Fourier shell correlation between two independent reconstructions from random halves of the data
    'rlnGroupName': str,  # The name of a group of images': e.g. all images from a micrograph)
    'rlnGroupNrParticles': int,  # Number particles in a group of images
    'rlnGroupNumber': int,  # The number of a group of images
    'rlnGroupScaleCorrection': float,  # Intensity-scale correction for a group of images
    'rlnHasConverged': bool,  # Flag to indicate that the optimization has converged
    'rlnHasHighFscAtResolLimit': bool,  # Flag to indicate that the FSC at the resolution limit is significant
    'rlnHasLargeSizeIncreaseIterationsAgo': int,
    # How many iterations have passed since the last large increase in image size
    'rlnHealpixOrder': int,
    # Healpix order for the sampling of the first two Euler angles': rot, tilt) on the 3D sphere
    'rlnHealpixOrderOriginal': int,
    # Original healpix order for the sampling of the first two Euler angles': rot, tilt) on the 3D sphere
    'rlnHelicalCentralProportion': float,
    # Only expand this central fraction of the Z axis when imposing real-space helical symmetry
    'rlnHelicalKeepTiltPriorFixed': bool,
    # Flag to indicate that helical tilt priors are kept fixed': at 90 degrees) in global angular searches
    'rlnHelicalMaskTubeInnerDiameter': float,
    # Inner diameter of helical tubes in Angstroms': for masks of helical references and particles)
    'rlnHelicalMaskTubeOuterDiameter': float,
    # Outer diameter of helical tubes in Angstroms': for masks of helical references and particles)
    'rlnHelicalOffsetStep': float,  # Step size for the searches of offsets along helical axis': in Angstroms)
    'rlnHelicalRise': float,  # The helical rise': translation per subunit) in Angstroms
    'rlnHelicalRiseInitial': float,
    # The initial helical rise': translation per subunit) in Angstroms before refinement
    'rlnHelicalRiseInitialStep': float,  # Initial step of helical rise search': in Angstroms)
    'rlnHelicalRiseMax': float,  # Maximum helical rise': in Angstroms)
    'rlnHelicalRiseMin': float,  # Minimum helical rise': in Angstroms)
    'rlnHelicalSigmaDistance': float,  # Sigma of distance along the helical tracks
    'rlnHelicalSymmetryLocalRefinement': bool,
    # Flag to indicate that local refinement of helical parameters should be performed
    'rlnHelicalTrackLength': float,
    # Distance': in pix) from the position of this helical segment to the starting point of the tube
    'rlnHelicalTrackLengthAngst': float,
    # Distance': in A) from the position of this helical segment to the starting point of the tube
    'rlnHelicalTubeID': int,  # Helical tube ID for a helical segment
    'rlnHelicalTubePitch': float,  # Cross-over distance for a helical segment': A)
    'rlnHelicalTwist': float,  # The helical twist': rotation per subunit) in degrees
    'rlnHelicalTwistInitial': float,  # The intial helical twist': rotation per subunit) in degrees before refinement
    'rlnHelicalTwistInitialStep': float,  # Initial step of helical twist search': in degrees)
    'rlnHelicalTwistMax': float,  # Maximum helical twist': in degrees, + for right-handedness)
    'rlnHelicalTwistMin': float,  # Minimum helical twist': in degrees, + for right-handedness)
    'rlnHighresLimitExpectation': float,  # High-resolution-limit': in Angstrom) for the expectation step
    'rlnHighresLimitSGD': float,  # High-resolution-limit': in Angstrom) for Stochastic Gradient Descent
    'rlnIgnoreHelicalSymmetry': bool,  # Flag to indicate that helical symmetry is ignored in 3D reconstruction
    'rlnImageDimensionality': int,  # Dimensionality of data stored in an image': i.e. 2 or 3)
    'rlnImageId': int,  # ID': i.e. a unique number) of an image
    'rlnImageName': str,  # Name of an image
    'rlnImageOriginalName': str,  # Original name of an image
    'rlnImagePixelSize': float,  # Pixel size': in Angstrom)
    'rlnImageSize': int,  # Size of an image': in pixels)
    'rlnImageSizeX': int,  # Size of an image in the X-direction': in pixels)
    'rlnImageSizeY': int,  # Size of an image in the Y-direction': in pixels)
    'rlnImageSizeZ': int,  # Size of an image in the Z-direction': in pixels)
    'rlnImageWeight': float,  # Relative weight of an image
    'rlnIncrementImageSize': int,
    # Number of Fourier shells to be included beyond the resolution where SSNR^MAP drops below 1
    'rlnIs3DSampling': bool,  # Flag to indicate this concerns a 3D sampling
    'rlnIs3DTranslationalSampling': bool,  # Flag to indicate this concerns a x,y,z-translational sampling
    'rlnIsFlip': bool,  # Flag to indicate that an image should be mirrored
    'rlnIsHelix': bool,  # Flag to indicate that helical refinement should be performed
    'rlnJobIsContinue': bool,  # Is tthis a continuation job?
    'rlnJobOptionDefaultValue': str,  # Default value of a joboption
    'rlnJobOptionDirectoryDefault': str,  # Default directory for file browser of a joboption
    'rlnJobOptionFilePattern': str,  # Pattern for file browser of a joboption
    'rlnJobOptionGUILabel': str,  # GUI label of a joboption
    'rlnJobOptionHelpText': str,  # Extra helptext of a joboption
    'rlnJobOptionMenuOptions': str,  # Options for pull-down menu
    'rlnJobOptionSliderMax': float,  # Maximum value for slider of a joboption
    'rlnJobOptionSliderMin': float,  # Minimum value for slider of a joboption
    'rlnJobOptionSliderStep': float,  # Step value for slider of a joboption
    'rlnJobOptionValue': str,  # Value of a joboption
    'rlnJobOptionVariable': str,  # Name of the joboption variable
    'rlnJobType': int,  # Which type of job is this?
    'rlnJobTypeName': str,  # The name for this type of job': also name of main directory for output jobs)
    'rlnJoboptionType': int,  # Which type of joboption is this?
    'rlnJoinHalvesUntilThisResolution': float,
    # Resolution': in Angstrom) to join the two random half-reconstructions to prevent their diverging orientations': for C-symmetries)
    'rlnKullbackLeiblerDivergence': float,  # Kullback-Leibler divergence for a particle
    'rlnKurtosisExcessValue': float,  # Kurtosis excess': 4th moment - 3) for the pixel values in an image
    'rlnLensStability': float,  # Lens stability': in ppm)
    'rlnLocalSymmetryFile': str,  # Local symmetry description file containing list of masks and their operators
    'rlnLogAmplitudesIntercept': float,
    # Y-value for Guinier plot: the fitted plateau of the logarithm of the radially averaged amplitudes
    'rlnLogAmplitudesMTFCorrected': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after MTF correction
    'rlnLogAmplitudesOriginal': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes of the input map
    'rlnLogAmplitudesSharpened': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after sharpening
    'rlnLogAmplitudesWeighted': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after FSC-weighting
    'rlnLogLikeliContribution': float,  # Contribution of a particle to the log-likelihood target function
    'rlnLogLikelihood': float,  # Value of the log-likelihood target function
    'rlnLongitudinalDisplacement': float,  # Longitudinal displacement': in Angstroms)
    'rlnLowresLimitExpectation': float,  # Low-resolution-limit': in Angstrom) for the expectation step
    'rlnMagMat00': float,  # Anisotropic magnification matrix, element 1,1
    'rlnMagMat01': float,  # Anisotropic magnification matrix, element 1,2
    'rlnMagMat10': float,  # Anisotropic magnification matrix, element 2,1
    'rlnMagMat11': float,  # Anisotropic magnification matrix, element 2,2
    'rlnMagnification': float,  # Magnification at the detector': in times)
    'rlnMagnificationCorrection': float,  # Magnification correction value for an image
    'rlnMagnificationSearchRange': float,  # Search range for magnification correction
    'rlnMagnificationSearchStep': float,  # Step sizefor magnification correction
    'rlnMaskName': str,  # Name of an image that contains a [0,1] mask
    'rlnMatrix_1_1': float,  # Matrix element': 1,1) of a 3x3 matrix
    'rlnMatrix_1_2': float,  # Matrix element': 1,2) of a 3x3 matrix
    'rlnMatrix_1_3': float,  # Matrix element': 1,3) of a 3x3 matrix
    'rlnMatrix_2_1': float,  # Matrix element': 2,1) of a 3x3 matrix
    'rlnMatrix_2_2': float,  # Matrix element': 2,1) of a 3x3 matrix
    'rlnMatrix_2_3': float,  # Matrix element': 2,1) of a 3x3 matrix
    'rlnMatrix_3_1': float,  # Matrix element': 3,1) of a 3x3 matrix
    'rlnMatrix_3_2': float,  # Matrix element': 3,1) of a 3x3 matrix
    'rlnMatrix_3_3': float,  # Matrix element': 3,1) of a 3x3 matrix
    'rlnMaxNumberOfPooledParticles': int,
    # Maximum number particles that are processed together to speed up calculations
    'rlnMaxValueProbDistribution': float,  # Maximum value of the': normalised) probability function for a particle
    'rlnMaximumCoarseImageSize': int,
    # Maximum size of the images to be used in the first pass of the adaptive oversampling strategy': may be smaller than the original image size)
    'rlnMaximumValue': float,  # Maximum value for the pixels in an image
    'rlnMicrographBinning': float,  # Micrograph binning factor
    'rlnMicrographDefectFile': str,  # Name of a defect list file
    'rlnMicrographDoseRate': float,  # Dose rate in electrons per square Angstrom per frame
    'rlnMicrographEndFrame': int,  # End frame of a motion model
    'rlnMicrographFrameNumber': int,  # Micrograph frame number
    'rlnMicrographGainName': str,  # Name of a gain reference
    'rlnMicrographId': int,  # ID': i.e. a unique number) of a micrograph
    'rlnMicrographMetadata': str,  # Name of a micrograph metadata file
    'rlnMicrographMovieName': str,  # Name of a micrograph movie stack
    'rlnMicrographName': str,  # Name of a micrograph
    'rlnMicrographNameNoDW': str,  # Name of a micrograph without dose weighting
    'rlnMicrographOriginalPixelSize': float,  # Pixel size of original movie before binning in Angstrom/pixel.
    'rlnMicrographPixelSize': float,  # Pixel size of': averaged) micrographs after binning in Angstrom/pixel.
    'rlnMicrographPreExposure': float,  # Pre-exposure dose in electrons per square Angstrom
    'rlnMicrographShiftX': float,  # X shift of a': patch of) micrograph
    'rlnMicrographShiftY': float,  # Y shift of a': patch of) micrograph
    'rlnMicrographStartFrame': int,  # Start frame of a motion model
    'rlnMicrographTiltAngle': float,  # Tilt angle': in degrees) used to collect a micrograph
    'rlnMicrographTiltAxisDirection': float,  # Direction of the tilt-axis': in degrees) used to collect a micrograph
    'rlnMicrographTiltAxisOutOfPlane': float,
    # Out-of-plane angle': in degrees) of the tilt-axis used to collect a micrograph': 90=in-plane)
    'rlnMinRadiusNnInterpolation': int,
    # Minimum radius for NN-interpolation': in Fourier pixels), for smaller radii linear int. is used
    'rlnMinimumValue': float,  # Minimum value for the pixels in an image
    'rlnModelStarFile': str,  # STAR file with metadata for the model that is being refined
    'rlnModelStarFile2': str,
    # STAR file with metadata for the second model that is being refined': from random halves of the data)
    'rlnMolecularWeight': float,
    # Molecular weight of the ordered mass inside the box for calculating cisTEM-like part.FSC': in kDa)
    'rlnMotionModelCoeff': float,  # A coefficient of a motion model
    'rlnMotionModelCoeffsIdx': int,  # Index of a coefficient of a motion model
    'rlnMotionModelVersion': int,  # Version of micrograph motion model
    'rlnMovieFrameNumber': int,  # Number of a movie frame
    'rlnMovieFramesRunningAverage': int,
    # Number of movie frames inside the running average that will be used for movie-refinement
    'rlnMtfFileName': str,  # The filename of a STAR file with the MTF for this optics group or image
    'rlnMtfValue': float,  # Value of the detectors modulation transfer function': between 0 and 1)
    'rlnNormCorrection': float,  # Normalisation correction value for an image
    'rlnNormCorrectionAverage': float,  # Average value': over all images) of the normalisation correction values
    'rlnNrBodies': int,  # The number of independent rigid bodies to be refined in multi-body refinement
    'rlnNrClasses': int,  # The number of references': i.e. classes) to be used in refinement
    'rlnNrGroups': int,
    # The number of different groups of images': each group has its own noise spectrum, and intensity-scale correction)
    'rlnNrHelicalAsymUnits': int,  # How many new helical asymmetric units are there in each box
    'rlnNrHelicalNStart': int,  # The N-number for an N-start helix
    'rlnNrOfFrames': int,  # Number of movie frames that were collected for this particle
    'rlnNrOfSignificantSamples': int,
    # Number of orientational/class assignments': for a particle) with sign.probabilities in the 1st pass of adaptive oversampling
    'rlnNumberOfIterWithoutChangingAssignments': int,
    # Number of iterations that have passed without large changes in orientation and class assignments
    'rlnNumberOfIterWithoutResolutionGain': int,  # Number of iterations that have passed without a gain in resolution
    'rlnNumberOfIterations': int,  # Maximum number of iterations to be performed
    'rlnOddZernike': str,  # Coefficients for the antisymmetrical Zernike polynomials
    'rlnOffsetRange': float,  # Search range for the origin offsets': in Angstroms)
    'rlnOffsetRangeOriginal': float,  # Original search range for the origin offsets': in Angstroms)
    'rlnOffsetStep': float,  # Step size for the searches in the origin offsets': in Angstroms)
    'rlnOffsetStepOriginal': float,  # Original step size for the searches in the origin offsets': in Angstroms)
    'rlnOpticsGroup': int,  # Group of particles with identical optical properties
    'rlnOpticsGroupName': str,  # The name of a group of particles with identical optical properties
    'rlnOpticsStarFile': str,  # STAR file with metadata for the optical groups': new as of version 3.1)
    'rlnOrientSamplingStarFile': str,  # STAR file with metadata for the orientational sampling
    'rlnOrientationDistribution': float,
    # Probability Density Function of the orientations(i.e. fraction of images assigned to each orient)
    'rlnOrientationalPriorMode': int,
    # Mode for prior distributions on the orientations': 0=no prior; 1=(rot,tilt,psi); 2=(rot,tilt); 3=rot; 4=tilt; 5=psi)
    'rlnOrientationsID': int,  # ID': i.e. a unique number) for an orientation
    'rlnOriginX': float,  # X-coordinate': in pixels) for the origin of rotation
    'rlnOriginXAngst': float,  # X-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginXPrior': float,  # Center of the prior on the X-coordinate': in pixels) for the origin of rotation
    'rlnOriginXPriorAngst': float,  # Center of the prior on the X-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginY': float,  # Y-coordinate': in pixels) for the origin of rotation
    'rlnOriginYAngst': float,  # Y-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginYPrior': float,  # Center of the prior on the Y-coordinate': in pixels) for the origin of rotation
    'rlnOriginYPriorAngst': float,  # Center of the prior on the Y-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginZ': float,  # Z-coordinate': in pixels) for the origin of rotation
    'rlnOriginZAngst': float,  # Z-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginZPrior': float,  # Center of the prior on the Z-coordinate': in pixels) for the origin of rotation
    'rlnOriginZPriorAngst': float,  # Center of the prior on the Z-coordinate': in Angstrom) for the origin of rotation
    'rlnOriginalImageSize': int,  # Original size of the images': in pixels)
    'rlnOriginalParticleName': str,  # Original name for a particles
    'rlnOutputRootName': str,
    # Rootname for all output files': this may include a directory structure, which should then exist)
    'rlnOverallAccuracyRotations': float,  # Overall accuracy of the rotational assignments': in degrees)
    'rlnOverallAccuracyTranslations': float,  # Overall accuracy of the translational assignments': in pixels)
    'rlnOverallAccuracyTranslationsAngst': float,  # Overall accuracy of the translational assignments': in Angstroms)
    'rlnOverallFourierCompleteness': float,
    # Fraction of all Fourier components up to the current resolution with SNR>1
    'rlnPaddingFactor': float,  # Oversampling factor for Fourier transforms of the references
    'rlnParticleBoxFractionMolecularWeight': float,
    # Fraction of protein voxels in the box, based on ordered molecular weight estimate, for calculating cisTEM-like part_FSC
    'rlnParticleBoxFractionSolventMask': float,
    # Fraction of protein voxels in the box, based on the solvent mask, for calculating cisTEM-like part_FSC
    'rlnParticleDiameter': float,
    # Diameter of the circular mask to be applied to all experimental images': in Angstroms)
    'rlnParticleFigureOfMerit': float,  # Developmental FOM for a particle
    'rlnParticleId': int,  # ID': i.e. a unique number) for a particle
    'rlnParticleName': str,  # Name for a particle
    'rlnParticleNumber': int,  # Number of particles
    'rlnParticleSelectZScore': float,  # Sum of Z-scores from particle_select. High Z-scores are likely to be outliers.
    'rlnPerFrameCumulativeWeight': float,
    # Sum of the resolution-dependent relative weights from the first frame until the given frame
    'rlnPerFrameRelativeWeight': float,  # The resolution-dependent relative weights for a given frame
    'rlnPhaseShift': float,  # Phase-shift from a phase-plate': in degrees)
    'rlnPipeLineEdgeFromNode': str,  # Name of the origin of an edge
    'rlnPipeLineEdgeProcess': str,  # Name of the destination of an edge
    'rlnPipeLineEdgeToNode': str,  # Name of the to-Node in an edge
    'rlnPipeLineJobCounter': int,  # Number of the last job in the pipeline
    'rlnPipeLineNodeName': str,  # Name of a Node in the pipeline
    'rlnPipeLineNodeType': int,  # Type of a Node in the pipeline
    'rlnPipeLineProcessAlias': str,  # Alias of a Process in the pipeline
    'rlnPipeLineProcessName': str,  # Name of a Process in the pipeline
    'rlnPipeLineProcessStatus': int,  # Status of a Process in the pipeline': running, scheduled, finished or cancelled)
    'rlnPipeLineProcessType': int,  # Type of a Process in the pipeline
    'rlnPixelSize': float,  # Size of the pixels in the references and images': in Angstroms)
    'rlnPsiStep': float,  # Step size': in degrees) for the sampling of the in-plane rotation angle': psi)
    'rlnPsiStepOriginal': float,
    # Original step size': in degrees) for the sampling of the in-plane rotation angle': psi)
    'rlnRadiusMaskExpImages': int,
    # Radius of the circular mask to be applied to all experimental images': in Angstroms)
    'rlnRadiusMaskMap': int,  # Radius of the spherical mask to be applied to all references': in Angstroms)
    'rlnRandomSeed': int,  # Seed': i.e. a number) for the random number generator
    'rlnRandomSubset': int,  # Random subset to which this particle belongs
    'rlnRandomiseFrom': float,  # Resolution': in A) from which the phases are randomised in the postprocessing step
    'rlnReconstructImageName': str,  # Name of an image to be used for reconstruction only
    'rlnReferenceDimensionality': int,  # Dimensionality of the references': 2D/3D)
    'rlnReferenceImage': str,  # Name of a reference image
    'rlnReferenceSigma2': float,  # Spherical average of the estimated power in the noise of a reference
    'rlnReferenceSpectralPower': float,  # Spherical average of the power of the reference
    'rlnReferenceTau2': float,  # Spherical average of the estimated power in the signal of a reference
    'rlnRefsAreCtfCorrected': bool,  # Flag to indicate that the input references have been CTF-amplitude corrected
    'rlnResolution': float,  # Resolution': in 1/Angstroms)
    'rlnResolutionInversePixel': float,  # Resolution': in 1/pixel, Nyquist = 0.5)
    'rlnResolutionSquared': float,  # X-value for Guinier plot: squared resolution in 1/Angstrom^2
    'rlnSGDGradientImage': str,  # Name of image containing the SGD gradient
    'rlnSamplingPerturbFactor': float,
    # Factor for random perturbation on the orientational sampling': between 0 no perturbation and 1 very strong perturbation)
    'rlnSamplingPerturbInstance': float,  # Random instance of the random perturbation on the orientational sampling
    'rlnSamplingRate': float,  # Sampling rate of an image': in Angstrom/pixel)
    'rlnSamplingRateX': float,  # Sampling rate in X-direction of an image': in Angstrom/pixel)
    'rlnSamplingRateY': float,  # Sampling rate in Y-direction of an image': in Angstrom/pixel)
    'rlnSamplingRateZ': float,  # Sampling rate in Z-direction of an image': in Angstrom/pixel)
    'rlnScheduleBooleanVariableName': str,  # Name of a Boolean variable in the Schedule
    'rlnScheduleBooleanVariableResetValue': bool,  # Value which a Boolean variable will take upon a reset
    'rlnScheduleBooleanVariableValue': bool,  # Value of a Boolean variable in the Schedule
    'rlnScheduleCurrentNodeName': str,  # Name of the current Node for this Schedule
    'rlnScheduleEdgeBooleanVariable': str,  # Name of the associated Boolean variable if this Edge is a Fork
    'rlnScheduleEdgeInputNodeName': str,  # Name of the input Node for a schedule Edge
    'rlnScheduleEdgeIsFork': bool,
    # Flag to indicate that this Edge is a Fork, dependent on a Boolean Schedule variable
    'rlnScheduleEdgeNumber': int,  # Numbered index of an edge inside a Schedule
    'rlnScheduleEdgeOutputNodeName': str,  # Name of the output Node for a schedule Edge
    'rlnScheduleEdgeOutputNodeNameIfTrue': str,
    # Name of the output Node for a schedule Fork if the associated Boolean is True
    'rlnScheduleEmailAddress': str,  # Email address to send message when Schedule finishes
    'rlnScheduleFloatVariableName': str,  # Name of a Float variable in the Schedule
    'rlnScheduleFloatVariableResetValue': float,  # Value which a Float variable will take upon a reset
    'rlnScheduleFloatVariableValue': float,  # Value of a Float variable in the Schedule
    'rlnScheduleJobHasStarted': bool,
    # Flag to indicate whether a Job has started already in the execution of the Schedule
    'rlnScheduleJobMode': str,  # Mode on how to execute a Job
    'rlnScheduleJobName': str,  # Name of a Job in a Schedule
    'rlnScheduleJobNameOriginal': str,  # Original name of a Job in a Schedule
    'rlnScheduleName': str,  # Name for this Schedule
    'rlnScheduleOperatorInput1': str,  # Name of the 1st input to the operator
    'rlnScheduleOperatorInput2': str,  # Name of the 2nd input to the operator
    'rlnScheduleOperatorName': str,  # Name of a Boolean operator in the Schedule
    'rlnScheduleOperatorOutput': str,  # Name of the output variable on which this operator acts
    'rlnScheduleOperatorType': str,  # Type of an operator in the Schedule
    'rlnScheduleOriginalStartNodeName': str,  # Name of the original starting Node for this Schedule
    'rlnSchedulestrVariableName': str,  # Name of a str variable in the Schedule
    'rlnSchedulestrVariableResetValue': str,  # Value which a str variable will take upon a reset
    'rlnSchedulestrVariableValue': str,  # Value of a str variable in the Schedule
    'rlnSelected': int,  # Flag whether an entry in a metadatatable is selected': 1) in the viewer or not': 0)
    'rlnSgdFinalIterations': int,
    # Number of final SGD iterations': at 'rlnSgdFinalResolution and with 'rlnSgdFinalSubsetSize)
    'rlnSgdFinalResolution': float,  # Resolution': in A) to use during the final SGD iterations
    'rlnSgdFinalSubsetSize': int,  # Number of particles in a mini-batch': subset) during the final SGD iteration
    'rlnSgdInBetweenIterations': int,
    # Number of SGD iteration in between the initial ones to the final ones': with linear interpolation of resolution and subset size)
    'rlnSgdInitialIterations': int,
    # Number of initial SGD iterations': at 'rlnSgdInitialResolution and with 'rlnSgdInitialSubsetSize)
    'rlnSgdInitialResolution': float,  # Resolution': in A) to use during the initial SGD iterations
    'rlnSgdInitialSubsetSize': int,  # Number of particles in a mini-batch': subset) during the initial SGD iterations
    'rlnSgdMaxSubsets': int,  # Stop SGD after doing this many subsets': possibly spanning more than 1 iteration)
    'rlnSgdMuFactor': float,  # The mu-parameter that controls the momentum of the SGD gradients
    'rlnSgdSigma2FudgeHalflife': int,
    # After processing this many particles the multiplicative factor for the noise variance will have halved
    'rlnSgdSigma2FudgeInitial': float,
    # The variance of the noise will initially be multiplied with this value': larger than 1)
    'rlnSgdSkipAnneal': bool,  # Option to switch off annealing of multiple references in SGD
    'rlnSgdStepsize': float,  # Stepsize in SGD updates)
    'rlnSgdSubsetSize': int,  # The number of particles in the random subsets for SGD
    'rlnSgdWriteEverySubset': int,  # Every this many iterations the model is written to disk in SGD
    'rlnSigma2Noise': float,  # Spherical average of the standard deviation in the noise': sigma)
    'rlnSigmaOffsets': float,  # Standard deviation in the origin offsets': in pixels)
    'rlnSigmaOffsetsAngst': float,  # Standard deviation in the origin offsets': in Angstroms)
    'rlnSigmaPriorPsiAngle': float,  # Standard deviation of the prior on the psi': i.e. third Euler) angle
    'rlnSigmaPriorRotAngle': float,  # Standard deviation of the prior on the rot': i.e. first Euler) angle
    'rlnSigmaPriorTiltAngle': float,  # Standard deviation of the prior on the tilt': i.e. second Euler) angle
    'rlnSignalToNoiseRatio': float,  # Spectral signal-to-noise ratio for a reference
    'rlnSkewnessValue': float,  # Skewness': 3rd moment) for the pixel values in an image
    'rlnSmallestChangesClasses': int,
    # Smallest changes thus far in the optimal class assignments': in numer of particles).
    'rlnSmallestChangesOffsets': float,  # Smallest changes thus far in the optimal offset assignments': in pixels).
    'rlnSmallestChangesOrientations': float,
    # Smallest changes thus far in the optimal orientation assignments': in degrees).
    'rlnSolventMask2Name': str,
    # Name of a secondary solvent mask': e.g. to flatten density inside an icosahedral virus)
    'rlnSolventMaskName': str,
    # Name of an image that contains a': possibly soft) mask for the solvent area': values=0 for solvent, values =1 for protein)
    'rlnSortedIndex': int,  # Index of a metadata entry after sorting': first sorted index is 0).
    'rlnSpectralIndex': int,  # Spectral index': i.e. distance in pixels to the origin in Fourier space)
    'rlnSpectralOrientabilityContribution': float,
    # Spectral SNR contribution to the orientability of individual particles
    'rlnSphericalAberration': float,  # Spherical aberration': in millimeters)
    'rlnSsnrMap': float,  # Spectral signal-to-noise ratio as defined for MAP estimation': SSNR^MAP)
    'rlnStandardDeviationValue': float,  # Standard deviation for the pixel values in an image
    'rlnStarFileMovieParticles': str,  # Filename of a STAR file with movie-particles in it
    'rlnSymmetryGroup': str,  # Symmetry group': e.g., C1, D7, I2, I5, etc.)
    'rlnTau2FudgeFactor': float,
    # Regularisation parameter with which estimates for the power in the references will be multiplied': T in original paper)
    'rlnTauSpectrumName': str,  # Name of a STAR file that holds a tau2-spectrum
    'rlnTiltAngleLimit': float,
    # Values to which to limit the tilt angles': positive for keeping side views, negative for keeping top views)
    'rlnTransversalDisplacement': float,  # Transversal displacement': in Angstroms)
    'rlnUnfilteredMapHalf1': str,  # Name of the unfiltered map from halfset 1
    'rlnUnfilteredMapHalf2': str,  # Name of the unfiltered map from halfset 2
    'rlnUnknownLabel': str,  # NON-RELION label: values will be ignored, yet maintained in the STAR file.
    'rlnUseTooCoarseSampling': bool,
    # Flag to indicate that the angular sampling on the sphere will be one step coarser than needed to speed up calculations
    'rlnVoltage': float,  # Voltage of the microscope': in kV)
    'rlnWidthMaskEdge': int,
    # Width': in pixels) of the soft edge for spherical/circular masks to be used for solvent flattening
}


class Label:
    def __init__(self, labelName):
        self.name = labelName
        # Get the type from the LABELS dict, assume str by default
        self.type = LABELS.get(labelName, str)

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        return self.name == str(other)


class Item:
    """
    General class to store data from a row. (e.g. Particle, Micrograph, etc)
    """

    def copyValues(self, other, *labels):
        """
        Copy the values form other object.
        """
        for l in labels:
            setattr(self, l, getattr(other, l))

    def clone(self):
        return copy.deepcopy(self)


class MetaData:
    """ Class to parse Relion star files
    """

    def __init__(self, input_star=None):
        self.version = "3"
        if input_star:
            self.read(input_star)
        else:
            self.clear()

    def clear(self):
        for attribute in dir(self):
            if "data_" in attribute and "_labels" not in attribute:
                setattr(self, attribute + "_labels", OrderedDict())
                setattr(self, attribute, [])

    def addDataTable(self, dataTableName):
        setattr(self, dataTableName + "_labels", OrderedDict())
        setattr(self, dataTableName, [])

    def _setItemValue(self, item, label, value):
        setattr(item, label.name, label.type(value))

    def _addLabel(self, dataTableName, labelName):
        getattr(self, dataTableName + "_labels")[labelName] = Label(labelName)

    def read(self, input_star):
        self.clear()
        found_label = False
        f = open(input_star)

        for line in f:
            values = line.strip().split()

            if not values:  # empty lines
                continue
            if "#" in values[0]:
                continue

            if "data_" in values[0]:
                if values[0] == "data_optics":
                    self.version = "3.1"
                self.addDataTable(values[0])
                currentTableRead = values[0]
                found_label = False
                continue

            if values[0].startswith('_rln'):  # Label line
                # Skip leading underscore in label name
                self._addLabel(currentTableRead, labelName=values[0][1:])
                found_label = True

            elif found_label:  # Read data lines after at least one label
                # Iterate in pairs (zipping) over labels and values in the row
                item = Item()
                # Dynamically set values, using label type (str by default)

                for label, value in izip(getattr(self, currentTableRead + "_labels").values(), values):
                    self._setItemValue(item, label, value)
                getattr(self, currentTableRead).append(item)

        f.close()

    def _write(self, output_file):
        # Write labels and prepare the line format for rows
        for attribute in dir(self):
            if "data_" in attribute and "_labels" not in attribute:
                line_format = ""
                if self.version == "3.1":
                    output_file.write("\n# version 30001\n\n%s\n\nloop_\n" % attribute)
                else:
                    output_file.write("\n%s\n\nloop_\n" % attribute)

                for i, l in enumerate(getattr(self, attribute + "_labels").values()):
                    output_file.write("_%s #%d \n" % (l.name, i + 1))
                    # Retrieve the type of the label
                    t = l.type
                    if t is float:
                        line_format += "%%(%s)f \t" % l.name
                    elif t is int:
                        line_format += "%%(%s)d \t" % l.name
                    else:
                        line_format += "%%(%s)s \t" % l.name

                line_format += '\n'

                for item in getattr(self, attribute):
                    output_file.write(line_format % item.__dict__)

    def write(self, output_star):
        output_file = open(output_star, 'w')
        self._write(output_file)
        output_file.close()

    def printStar(self):
        self._write(sys.stdout)

    def size(self, dataTableName):
        return len(getattr(self, dataTableName))

    def __len__(self):
        if hasattr(self, "data_particles"):
            return self.size("data_particles")
        elif hasattr(self, "data_"):
            return self.size("data_")
        else:
            return 0

    def __iter__(self):
        if hasattr(self, "data_particles"):
            for item in self.data_particles:
                yield item
        else:
            for item in self.data_:
                yield item

    def getLabels(self, dataTableName="data_particles"):
        return [l.name for l in getattr(self, dataTableName + "_labels").values()]

    def setLabels(self, dataTableName, **kwargs):
        """ Add (or set) labels with a given value. """
        for key, value in kwargs.items():
            if key not in getattr(self, dataTableName + "_labels").keys():
                self._addLabel(dataTableName, key)

        for item in getattr(self, dataTableName):
            for key, value in kwargs.items():
                self._setItemValue(item, getattr(self, dataTableName + "_labels")[key], value)

    def _iterLabels(self, labels):
        """ Just a small trick to accept normal lists or *args
        """
        for l1 in labels:
            if isinstance(l1, list):
                for l2 in l1:
                    yield l2
            else:
                yield l1

    def addLabels(self, dataTableName, *labels):
        """
        Register labes in the metadata, but not add the values to the rows
        """
        for l in self._iterLabels(labels):
            if l not in getattr(self, dataTableName + "_labels").keys():
                self._addLabel(dataTableName, l)

    def removeLabels(self, dataTableName, *labels):
        for l in self._iterLabels(labels):
            if l in getattr(self, dataTableName + "_labels"):
                del getattr(self, dataTableName + "_labels")[l]

    def addItem(self, dataTableName, item):
        """ Add a new item to the MetaData. """
        getattr(self, dataTableName).append(item)

    def setData(self, dataTableName, data):
        """ Set internal data with new items. """
        setattr(self, dataTableName, data)

    def addData(self, dataTableName, data):
        """ Add new items to internal data. """
        for item in data:
            self.addItem(dataTableName, item)
