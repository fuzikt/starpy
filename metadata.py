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
    'rlnComment': str,  # A metadata comment (This is treated in a special way)
    'rlnAreaId': int,  # ID (i.e. a unique number) of an area (i.e. field-of-view)
    'rlnAreaName': str,  # Name of an area (i.e. field-of-view)
    'rlnBodyMaskName': str,  # Name of an image that contains a [0
    'rlnBodyKeepFixed': int,  # Flag to indicate whether to keep a body fixed (value 1) or keep on refining it (0)
    'rlnBodyReferenceName': str,
    # Name of an image that contains the initial reference for one body of a multi-body refinement
    'rlnBodyRotateDirectionX': float,  # X-component of axis around which to rotate this body
    'rlnBodyRotateDirectionY': float,  # Y-component of axis around which to rotate this body
    'rlnBodyRotateDirectionZ': float,  # Z-component of axis around which to rotate this body
    'rlnBodyRotateRelativeTo': int,  # Number of the body relative to which this body rotates (if negative
    'rlnBodySigmaAngles': float,
    # Width of prior on all three Euler angles of a body in multibody refinement (in degrees)
    'rlnBodySigmaOffset': float,  # Width of prior on origin offsets of a body in multibody refinement (in pixels)
    'rlnBodySigmaOffsetAngst': float,
    # Width of prior on origin offsets of a body in multibody refinement (in Angstroms)
    'rlnBodySigmaRot': float,  # Width of prior on rot angles of a body in multibody refinement (in degrees)
    'rlnBodySigmaTilt': float,  # Width of prior on tilt angles of a body in multibody refinement (in degrees)
    'rlnBodySigmaPsi': float,  # Width of prior on psi angles of a body in multibody refinement (in degrees)
    'rlnBodyStarFile': str,  # Name of STAR file with body masks and metadata
    'rlnClassIndex': int,  # Class number of each class from the model STAR file of 2D classification
    'rlnParticleNr': float,  # Number of particles in this class
    'rlnIsSelected': int,  # Whether this class is selected
    'rlnCircleMaskedMean': float,
    # Average value for the pixels in the circularly masked area of this class average image
    'rlnCircleMaskedStddev': float,
    # Standard deviation for the pixel values in the circularly masked area of this class average image
    'rlnCircleMaskedSkew': float,
    # Skewness (3rd moment) for the pixel values in the circularly masked area of this class average image
    'rlnCircleMaskedKurt': float,
    # Kurtosis (4th moment) for the pixel values in the circularly masked area of this class average image
    'rlnRingMean': float,
    # Average value for the pixels in the area of this class average image specified by inner and outer radius
    'rlnRingStddev': float,
    # Standard deviation for the pixel values in the area of this class average image specified by inner and outer radius
    'rlnRingSkew': float,
    # Skewness (3rd moment) for the pixel values in the area of this class average image specified by inner and outer radius
    'rlnRingKurt': float,
    # Kurtosis (4th moment) for the pixel values in the area of this class average image specified by inner and outer radius
    'rlnInnerCircleMean': float,  # Average pixel value of the smaller circular area specified by inner / outer radius
    'rlnInnerCircleStddev': float,
    # Pixel value standard deviation of the smaller circular area specified by inner / outer radius
    'rlnInnerCircleSkew': float,
    # Pixel value skewness (3rd moment) of the smaller circular area specified by inner / outer radius
    'rlnInnerCircleKurt': float,
    # Pixel value kurtosis (4th moment) of the smaller circular area specified by inner / outer radius
    'rlnClassScore': float,  # Class score calculated based on estimated resolution and selection label
    'rlnJobScore': float,  # Overall score of this 2D classification job
    'rlnFftMean': float,  # Mean of Fourier components (amplitude only) up to resolution limit.
    'rlnFftStddev': float,  # Standard deviation of Fourier components (amplitude only) up to resolution limit.
    'rlnFftSkew': float,  # Skewness of Fourier components (amplitude only) up to resolution limit.
    'rlnFftKurt': float,  # Kurtosis of Fourier components (amplitude only) up to resolution limit.
    'rlnProteinArea': int,  # Whether protein area is non-zero.
    'rlnProteinSum': float,  # Sum of protein region.
    'rlnProteinMean': float,  # Mean of protein region.
    'rlnProteinStddev': float,  # Standard deviation of protein region.
    'rlnProteinSkew': float,  # Skewness of protein region.
    'rlnProteinKurt': float,  # Kurtosis of protein region.
    'rlnSolventArea': int,  # Whether solvent area is non-zero.
    'rlnSolventSum': float,  # Sum of solvent region.
    'rlnSolventMean': float,  # Mean of solvent region.
    'rlnSolventStddev': float,  # Standard deviation of solvent region.
    'rlnSolventSkew': float,  # Skewness of solvent region.
    'rlnSolventKurt': float,  # Kurtosis of solvent region.
    'rlnRelativeSignalIntensity': float,  # Sum of protein area's individual pixel values subtracting solvent area mean.
    'rlnScatteredSignal': float,  # Ratio of excluded white pixels when making the protein mask.
    'rlnEdgeSignal': float,  # Ratio of white pixels on the edge in the protein mask.
    'rlnProteinCAR': float,  # Circumference to area ratio of protein area (relative to a perfect circle).
    'rlnWeightedResolution': float,  # Estimated resolution weighted by the number of particles in the class.
    'rlnRelativeResolution': float,  # Estimated resolution weighted by the image dimension.
    'rlnLowpassFilteredImageMax': float,  # Maximum pixel value of the lowpass filtered image.
    'rlnLowpassFilteredImageMin': float,  # Minimum pixel value of the lowpass filtered image.
    'rlnLowpassFilteredImageMean': float,  # Mean pixel value of the lowpass filtered image.
    'rlnLowpassFilteredImageStddev': float,  # Standard deviation of pixel values of the lowpass filtered image.
    'rlnLBP': str,  # Histogram of the local binary pattern of the image.
    'rlnProteinLBP': str,  # Histogram of the local binary pattern of the protein area.
    'rlnSolventLBP': str,  # Histogram of the local binary pattern of the solvent area.
    'rlnTotalEntropy': float,  # Entropy of the entire image.
    'rlnProteinEntropy': float,  # Entropy of the protein area.
    'rlnSolventEntropy': float,  # Entropy of the solvent area.
    'rlnProteinHaralick': str,  # Haralick features of the protein area.
    'rlnSolventHaralick': str,  # Haralick features of the solvent area.
    'rlnZernikeMoments': str,  # Zernike moments of the image.
    'rlnGranulo': str,  # Granulo features of the image.
    'rlnNormalizedFeatureVector': str,  # Vector with normalized feature vector for neural network execution.
    'rlnSubImageStarFile': str,  # Name of a STAR file pointing to all subimages of this class average
    'rlnSubImageStack': str,  # Name of an MRC stack containing all subimages of this class average
    'rlnPredictedClassScore': float,  # 2D class merit scores predicted by RELION model.
    'rlnCtfAstigmatism': float,  # Absolute value of the difference between defocus in U- and V-direction (in A)
    'rlnCtfBfactor': float,  # B-factor (in A^2) that describes CTF power spectrum fall-off
    'rlnCtfMaxResolution': float,  # Estimated maximum resolution (in A) of significant CTF Thon rings
    'rlnCtfValidationScore': float,  # Gctf-based validation score for the quality of the CTF fit
    'rlnCtfScalefactor': float,  # Linear scale-factor on the CTF (values between 0 and 1)
    'rlnVoltage': float,  # Voltage of the microscope (in kV)
    'rlnDefocusU': float,  # Defocus in U-direction (in Angstroms
    'rlnDefocusV': float,  # Defocus in V-direction (in Angstroms
    'rlnDefocusAngle': float,  # Angle between X and defocus U direction (in degrees)
    'rlnSphericalAberration': float,  # Spherical aberration (in millimeters)
    'rlnChromaticAberration': float,  # Chromatic aberration (in millimeters)
    'rlnDetectorPixelSize': float,  # Pixel size of the detector (in micrometers)
    'rlnCtfPowerSpectrum': str,  # Power spectrum for CTF estimation
    'rlnEnergyLoss': float,  # Energy loss (in eV)
    'rlnCtfFigureOfMerit': float,  # Figure of merit for the fit of the CTF (not used inside relion_refine)
    'rlnCtfImage': str,  # Name of an image with all CTF values
    'rlnLensStability': float,  # Lens stability (in ppm)
    'rlnMagnification': float,  # Magnification at the detector (in times)
    'rlnPhaseShift': float,  # Phase-shift from a phase-plate (in degrees)
    'rlnConvergenceCone': float,  # Convergence cone (in mrad)
    'rlnLongitudinalDisplacement': float,  # Longitudinal displacement (in Angstroms)
    'rlnTransversalDisplacement': float,  # Transversal displacement (in Angstroms)
    'rlnAmplitudeContrast': float,  # Amplitude contrast (as a fraction
    'rlnCtfValue': float,  # Value of the Contrast Transfer Function
    'rlnImageName': str,  # Name of an image
    'rlnImageOriginalName': str,  # Original name of an image
    'rlnReconstructImageName': str,  # Name of an image to be used for reconstruction only
    'rlnImageId': int,  # ID (i.e. a unique number) of an image
    'rlnEnabled': bool,  # Not used in RELION
    'rlnDataType': int,  # Type of data stored in an image (e.g. int
    'rlnImageDimensionality': int,  # Dimensionality of data stored in an image (i.e. 2 or 3)
    'rlnBeamTiltX': float,  # Beam tilt in the X-direction (in mrad)
    'rlnBeamTiltY': float,  # Beam tilt in the Y-direction (in mrad)
    'rlnMtfFileName': str,  # The filename of a STAR file with the MTF for this optics group or image
    'rlnOpticsGroup': int,  # Group of particles with identical optical properties
    'rlnOpticsGroupName': str,  # The name of a group of particles with identical optical properties
    'rlnOddZernike': str,  # Coefficients for the antisymmetrical Zernike polynomials
    'rlnEvenZernike': str,  # Coefficients for the symmetrical Zernike polynomials
    'rlnImagePixelSize': float,  # Pixel size (in Angstrom)
    'rlnMagMat00': float,  # Anisotropic magnification matrix
    'rlnMagMat01': float,  # Anisotropic magnification matrix
    'rlnMagMat10': float,  # Anisotropic magnification matrix
    'rlnMagMat11': float,  # Anisotropic magnification matrix
    'rlnCoordinateX': float,  # X-Position of an image in a micrograph (in pixels)
    'rlnCoordinateY': float,  # Y-Position of an image in a micrograph (in pixels)
    'rlnCoordinateZ': float,  # Z-Position of an image in a 3D micrograph
    'rlnMovieFrameNumber': int,  # Number of a movie frame
    'rlnNormCorrection': float,  # Normalisation correction value for an image
    'rlnMagnificationCorrection': float,  # Magnification correction value for an image
    'rlnSamplingRate': float,  # Sampling rate of an image (in Angstrom/pixel)
    'rlnSamplingRateX': float,  # Sampling rate in X-direction of an image (in Angstrom/pixel)
    'rlnSamplingRateY': float,  # Sampling rate in Y-direction of an image (in Angstrom/pixel)
    'rlnSamplingRateZ': float,  # Sampling rate in Z-direction of an image (in Angstrom/pixel)
    'rlnImageSize': int,  # Size of an image (in pixels)
    'rlnImageSizeX': int,  # Size of an image in the X-direction (in pixels)
    'rlnImageSizeY': int,  # Size of an image in the Y-direction (in pixels)
    'rlnImageSizeZ': int,  # Size of an image in the Z-direction (in pixels)
    'rlnMinimumValue': float,  # Minimum value for the pixels in an image
    'rlnMaximumValue': float,  # Maximum value for the pixels in an image
    'rlnAverageValue': float,  # Average value for the pixels in an image
    'rlnStandardDeviationValue': float,  # Standard deviation for the pixel values in an image
    'rlnSkewnessValue': float,  # Skewness (3rd moment) for the pixel values in an image
    'rlnKurtosisExcessValue': float,  # Kurtosis excess (4th moment - 3) for the pixel values in an image
    'rlnImageWeight': float,  # Relative weight of an image
    'rlnMaskName': str,  # Name of an image that contains a [0
    'rlnJobIsContinue': bool,  # Is this a continuation job?
    'rlnJobIsTomo': bool,  # Is this a tomo job?
    'rlnJobType': int,  # Which type of job is this?
    'rlnJobTypeLabel': str,  # The name for this type of job (also name of main directory for output jobs)
    'rlnJoboptionType': int,  # Which type of joboption is this?
    'rlnJobOptionVariable': str,  # Name of the joboption variable
    'rlnJobOptionValue': str,  # Value of a joboption
    'rlnJobOptionGUILabel': str,  # GUI label of a joboption
    'rlnJobOptionDefaultValue': str,  # Default value of a joboption
    'rlnJobOptionSliderMin': float,  # Minimum value for slider of a joboption
    'rlnJobOptionSliderMax': float,  # Maximum value for slider of a joboption
    'rlnJobOptionSliderStep': float,  # Step value for slider of a joboption
    'rlnJobOptionHelpText': str,  # Extra helptext of a joboption
    'rlnJobOptionFilePattern': str,  # Pattern for file browser of a joboption
    'rlnJobOptionDirectoryDefault': str,  # Default directory for file browser of a joboption
    'rlnJobOptionMenuOptions': str,  # Options for pull-down menu
    'rlnMatrix_1_1': float,  # Matrix element (1
    'rlnMatrix_1_2': float,  # Matrix element (1
    'rlnMatrix_1_3': float,  # Matrix element (1
    'rlnMatrix_2_1': float,  # Matrix element (2
    'rlnMatrix_2_2': float,  # Matrix element (2
    'rlnMatrix_2_3': float,  # Matrix element (2
    'rlnMatrix_3_1': float,  # Matrix element (3
    'rlnMatrix_3_2': float,  # Matrix element (3
    'rlnMatrix_3_3': float,  # Matrix element (3
    'rlnAccumMotionTotal': float,  # 'Accumulated global motion during the entire movie (in A)
    'rlnAccumMotionEarly': float,  # 'Accumulated global motion during the first frames of the movie (in A)
    'rlnAccumMotionLate': float,  # 'Accumulated global motion during the last frames of the movie (in A)
    'rlnMicrographCoordinates': str,  # Filename of a file (in .star
    'rlnMicrographIceThickness': float,  # Ice thickness (in Angstrom) of a micrograph
    'rlnMicrographId': int,  # ID (i.e. a unique number) of a micrograph
    'rlnMicrographName': str,  # Name of a micrograph
    'rlnMicrographGainName': str,  # Name of a gain reference
    'rlnMicrographDefectFile': str,  # Name of a defect list file
    'rlnMicrographNameNoDW': str,  # Name of a micrograph without dose weighting
    'rlnMicrographMovieName': str,  # Name of a micrograph movie stack
    'rlnMicrographMetadata': str,  # Name of a micrograph metadata file
    'rlnMicrographTiltAngle': float,  # Tilt angle (in degrees) used to collect a micrograph
    'rlnMicrographTiltAxisDirection': float,  # Direction of the tilt-axis (in degrees) used to collect a micrograph
    'rlnMicrographTiltAxisOutOfPlane': float,
    # Out-of-plane angle (in degrees) of the tilt-axis used to collect a micrograph (90=in-plane)
    'rlnMicrographOriginalPixelSize': float,  # Pixel size of original movie before binning in Angstrom/pixel.
    'rlnMicrographPixelSize': float,  # Pixel size of (averaged) micrographs after binning in Angstrom/pixel.
    'rlnMicrographPreExposure': float,  # Pre-exposure dose in electrons per square Angstrom
    'rlnMicrographDoseRate': float,  # Dose rate in electrons per square Angstrom per frame
    'rlnMicrographBinning': float,  # Micrograph binning factor
    'rlnMicrographFrameNumber': int,  # Micrograph frame number
    'rlnMotionModelVersion': int,  # Version of micrograph motion model
    'rlnMicrographStartFrame': int,  # Start frame of a motion model
    'rlnMicrographEndFrame': int,  # End frame of a motion model
    'rlnMicrographShiftX': float,  # X shift of a (patch of) micrograph
    'rlnMicrographShiftY': float,  # Y shift of a (patch of) micrograph
    'rlnMotionModelCoeffsIdx': int,  # Index of a coefficient of a motion model
    'rlnMotionModelCoeff': float,  # A coefficient of a motion model
    'rlnEERUpsampling': int,  # EER upsampling ratio (1 = 4K
    'rlnEERGrouping': int,  # The number of hardware frames to group
    'rlnAccuracyRotations': float,  # Estimated accuracy (in degrees) with which rotations can be assigned
    'rlnAccuracyTranslations': float,  # Estimated accuracy (in pixels) with which translations can be assigned
    'rlnAccuracyTranslationsAngst': float,  # Estimated accuracy (in Angstroms) with which translations can be assigned
    'rlnAveragePmax': float,  # Average value (over all images) of the maxima of the probability distributions
    'rlnCurrentResolution': float,  # Current resolution where SSNR^MAP drops below 1 (in 1/Angstroms)
    'rlnCurrentImageSize': int,  # Current size of the images used in the refinement
    'rlnSsnrMap': float,  # Spectral signal-to-noise ratio as defined for MAP estimation (SSNR^MAP)
    'rlnReferenceDimensionality': int,  # Dimensionality of the references (2D/3D)
    'rlnDataDimensionality': int,  # Dimensionality of the data (2D/3D)
    'rlnDiff2RandomHalves': float,
    # Power of the differences between two independent reconstructions from random halves of the data
    'rlnEstimatedResolution': float,  # Estimated resolution (in A) for a reference
    'rlnFourierCompleteness': float,  # Fraction of Fourier components (per resolution shell) with SNR>1
    'rlnOverallFourierCompleteness': float,
    # Fraction of all Fourier components up to the current resolution with SNR>1
    'rlnGoldStandardFsc': float,
    # Fourier shell correlation between two independent reconstructions from random halves of the data
    'rlnGroupName': str,  # The name of a group of images (e.g. all images from a micrograph)
    'rlnGroupNumber': int,  # The number of a group of images
    'rlnGroupNrParticles': int,  # Number particles in a group of images
    'rlnGroupScaleCorrection': float,  # Intensity-scale correction for a group of images
    'rlnNrHelicalAsymUnits': int,  # How many new helical asymmetric units are there in each box
    'rlnHelicalTwist': float,  # The helical twist (rotation per subunit) in degrees
    'rlnHelicalTwistMin': float,  # Minimum helical twist (in degrees
    'rlnHelicalTwistMax': float,  # Maximum helical twist (in degrees
    'rlnHelicalTwistInitialStep': float,  # Initial step of helical twist search (in degrees)
    'rlnHelicalRise': float,  # The helical rise (translation per subunit) in Angstroms
    'rlnHelicalRiseMin': float,  # Minimum helical rise (in Angstroms)
    'rlnHelicalRiseMax': float,  # Maximum helical rise (in Angstroms)
    'rlnHelicalRiseInitialStep': float,  # Initial step of helical rise search (in Angstroms)
    'rlnIsHelix': bool,  # Flag to indicate that helical refinement should be performed
    'rlnFourierSpaceInterpolator': int,  # The kernel used for Fourier-space interpolation (NN=0
    'rlnLogLikelihood': float,  # Value of the log-likelihood target function
    'rlnMinRadiusNnInterpolation': int,  # 'Minimum radius for NN-interpolation (in Fourier pixels)
    'rlnNormCorrectionAverage': float,  # Average value (over all images) of the normalisation correction values
    'rlnNrClasses': int,  # The number of references (i.e. classes) to be used in refinement
    'rlnNrBodies': int,  # The number of independent rigid bodies to be refined in multi-body refinement
    'rlnNrGroups': int,  # The number of different groups of images (each group has its own intensity-scale correction)
    'rlnNrOpticsGroups': int,  # The number of different optics groups (each optics group has its own noise spectrum)
    'rlnOpticsGroupNumber': int,  # The number of an optics group
    'rlnOpticsGroupNrParticles': int,  # Number particles in an optics group
    'rlnSpectralOrientabilityContribution': float,
    # Spectral SNR contribution to the orientability of individual particles
    'rlnOriginalImageSize': int,  # Original size of the images (in pixels)
    'rlnPaddingFactor': float,  # Oversampling factor for Fourier transforms of the references
    'rlnClassDistribution': float,
    # Probability Density Function of the different classes (i.e. fraction of images assigned to each class)
    'rlnClassPriorOffsetX': float,  # Prior in the X-offset for a class (in pixels)
    'rlnClassPriorOffsetY': float,  # Prior in the Y-offset for a class (in pixels)
    'rlnOrientationDistribution': float,
    # Probability Density Function of the orientations  (i.e. fraction of images assigned to each orient)
    'rlnPixelSize': float,  # Size of the pixels in the references and images (in Angstroms)
    'rlnReferenceSpectralPower': float,  # Spherical average of the power of the reference
    'rlnOrientationalPriorMode': int,  # Mode for prior distributions on the orientations (0=no prior; 1=(rot
    'rlnReferenceImage': str,  # Name of a reference image
    'rlnGradMoment1': str,  # Name of image containing the first moment of the gradient
    'rlnGradMoment2': str,  # Name of image containing the second moment of the gradient
    'rlnSigmaOffsets': float,  # 'Standard deviation in the origin offsets (in pixels)
    'rlnSigmaOffsetsAngst': float,  # 'Standard deviation in the origin offsets (in Angstroms)
    'rlnSigma2Noise': float,  # Spherical average of the standard deviation in the noise (sigma)
    'rlnReferenceSigma2': float,  # Spherical average of the estimated power in the noise of a reference
    'rlnSigmaPriorRotAngle': float,  # Standard deviation of the prior on the rot (i.e. first Euler) angle
    'rlnSigmaPriorTiltAngle': float,  # Standard deviation of the prior on the tilt (i.e. second Euler) angle
    'rlnSigmaPriorPsiAngle': float,  # Standard deviation of the prior on the psi (i.e. third Euler) angle
    'rlnSignalToNoiseRatio': float,  # Spectral signal-to-noise ratio for a reference
    'rlnTau2FudgeFactor': float,
    # Regularisation parameter with which estimates for the power in the references will be multiplied (T in original paper)
    'rlnReferenceTau2': float,  # Spherical average of the estimated power in the signal of a reference
    'rlnOverallAccuracyRotations': float,  # Overall accuracy of the rotational assignments (in degrees)
    'rlnOverallAccuracyTranslations': float,  # Overall accuracy of the translational assignments (in pixels)
    'rlnOverallAccuracyTranslationsAngst': float,  # Overall accuracy of the translational assignments (in Angstroms)
    'rlnAdaptiveOversampleFraction': float,
    # Fraction of the weights that will be oversampled in a second pass of the adaptive oversampling strategy
    'rlnAdaptiveOversampleOrder': int,  # Order of the adaptive oversampling (0=no oversampling
    'rlnAutoLocalSearchesHealpixOrder': int,
    # Healpix order (before oversampling) from which autosampling procedure will use local angular searches
    'rlnAvailableMemory': float,  # Available memory per computing node (i.e. per MPI-process)
    'rlnBestResolutionThusFar': float,  # The highest resolution that has been obtained in this optimization thus far
    'rlnCoarseImageSize': int,
    # Current size of the images to be used in the first pass of the adaptive oversampling strategy (may be smaller than the original image size)
    'rlnChangesOptimalOffsets': float,  # The average change in optimal translation in the last iteration (in pixels)
    'rlnChangesOptimalOrientations': float,
    # The average change in optimal orientation in the last iteration (in degrees)
    'rlnChangesOptimalClasses': float,
    # The number of particles that changed their optimal clsas assignment in the last iteration
    'rlnCtfDataArePhaseFlipped': bool,  # Flag to indicate that the input images have been phase-flipped
    'rlnCtfDataAreCtfPremultiplied': bool,
    # Flag to indicate that the input images have been premultiplied with their CTF
    'rlnExperimentalDataStarFile': str,  # STAR file with metadata for the experimental images
    'rlnDoCorrectCtf': bool,  # Flag to indicate that CTF-correction should be performed
    'rlnDoCorrectMagnification': bool,  # Flag to indicate that (per-group) magnification correction should be performed
    'rlnDoCorrectNorm': bool,  # Flag to indicate that (per-image) normalisation-error correction should be performed
    'rlnDoCorrectScale': bool,
    # Flag to indicate that internal (per-group) intensity-scale correction should be performed
    'rlnDoExternalReconstruct': bool,
    # Flag to indicate that the reconstruction will be performed outside relion_refine
    'rlnDoRealignMovies': bool,  # Flag to indicate that individual frames of movies are being re-aligned
    'rlnDoMapEstimation': bool,  # Flag to indicate that MAP estimation should be performed (otherwise ML estimation)
    'rlnDoGradientRefine': bool,  # Perform gradient refine.
    'rlnDoStochasticGradientDescent': bool,
    # Flag to indicate that gradient refinement should be performed (otherwise expectation maximisation)
    'rlnGradEmIters': int,  # Finish gradient optimization with this many iterations of Expectation-Maximization.
    'rlnGradHasConverged': bool,  # Has gradient refinement converged.
    'rlnGradCurrentStepsize': float,  # The current step size.
    'rlnGradSubsetOrder': int,  # The initial subset size multiplied with two (2) to the power of this number.
    'rlnGradSuspendFinerSamplingIter': int,  # Suspend finer sampling this many iterations
    'rlnGradSuspendLocalSamplingIter': int,  # Suspend local sampling this many iterations
    'rlnDoStochasticEM': bool,
    # Flag to indicate that stochastic EM-optimisation should be performed (an alternative to gradient refinement)
    'rlnExtReconsDataReal': str,
    # Name of the map with the real components of the input data array for the external reconstruction program
    'rlnExtReconsDataImag': str,
    # Name of the map with the imaginary components of the input data array for the external reconstruction program
    'rlnExtReconsWeight': str,  # Name of the map with the input weight array for the external reconstruction program
    'rlnExtReconsResult': str,  # Name of the output reconstruction from the external reconstruction program
    'rlnExtReconsResultStarfile': str,  # Name of the output STAR file with updated FSC or tau curves
    'rlnDoFastSubsetOptimisation': bool,  # Use subsets of the data in the earlier iterations to speed up convergence
    'rlnSgdInitialIterationsFraction': float,
    # Fraction of initial gradient iterations (at rlnSgdInitialResolution and with rlnSgdInitialSubsetSize)
    'rlnSgdFinalIterationsFraction': float,
    # fraction of final gradient iterations (at rlnSgdFinalResolution and with rlnSgdFinalSubsetSize)
    'rlnSgdMinimumResolution': float,
    # Adjust under-estimated signal power in gradient optimization to this resolution.
    'rlnSgdInitialResolution': float,  # Resolution (in A) to use during the initial gradient refinement iterations
    'rlnSgdFinalResolution': float,  # Resolution (in A) to use during the final gradient refinement iterations
    'rlnSgdInitialSubsetSize': int,
    # Number of particles in a mini-batch (subset) during the initial gradient refinement iterations
    'rlnSgdFinalSubsetSize': int,
    # Number of particles in a mini-batch (subset) during the final gradient refinement iteration
    'rlnSgdMuFactor': float,  # The mu-parameter that controls the momentum of the SGD gradients
    'rlnSgdSigma2FudgeInitial': float,
    # The variance of the noise will initially be multiplied with this value (larger than 1)
    'rlnSgdSigma2FudgeHalflife': int,
    # After processing this many particles the multiplicative factor for the noise variance will have halved
    'rlnSgdSkipAnneal': bool,  # Option to switch off annealing of multiple references in gradient refinement
    'rlnSgdClassInactivityThreshold': float,
    # Threshold for dropping classes with low activity during gradient optimisation.
    'rlnSgdSubsetSize': int,  # The number of particles in the random subsets for gradient refinement
    'rlnSgdWriteEverySubset': int,  # Every this many iterations the model is written to disk in gradient refinement
    'rlnSgdMaxSubsets': int,  # Stop SGD after doing this many subsets (possibly spanning more than 1 iteration)
    'rlnSgdStepsize': float,  # Stepsize in gradient refinement updates
    'rlnSgdStepsizeScheme': str,  # Stepsize scheme used in gradient refinement
    'rlnTau2FudgeScheme': str,  # Tau2 fudge scheme for updating the tau2 fudge
    'rlnTau2FudgeArg': float,  # Tau2 fudge chosen by user
    'rlnMaximumSignificantPoses': int,  # Maximum number of most significant poses & translations to consider
    'rlnDoAutoRefine': bool,  # Flag to indicate that 3D auto-refine procedure is being used
    'rlnDoAutoSampling': bool,  # Flag to indicate that auto-sampling is to be used (outside the auto-refine procedure)
    'rlnDoOnlyFlipCtfPhases': bool,  # Flag to indicate that CTF-correction should only comprise phase-flipping
    'rlnDoCenterClasses': bool,
    # Flag to indicate that the class averages or reconstructions should be centered based on their center-of-mass during every iteration.
    'rlnDoSolventFlattening': bool,
    # Flag to indicate that the references should be masked to set their solvent areas to a constant density
    'rlnDoSolventFscCorrection': bool,  # Flag to indicate that the FSCs should be solvent-corrected during refinement
    'rlnDoSkipAlign': bool,
    # Flag to indicate that orientational (i.e. rotational and translational) searches will be omitted from the refinement
    'rlnDoSkipRotate': bool,  # Flag to indicate that rotational searches will be omitted from the refinement
    'rlnDoSplitRandomHalves': bool,  # Flag to indicate that the data should be split into two completely separate
    'rlnDoZeroMask': bool,
    # Flag to indicate that the surrounding solvent area in the experimental particles will be masked to zeros (by default random noise will be used
    'rlnFixSigmaNoiseEstimates': bool,
    # Flag to indicate that the estimates for the power spectra of the noise should be kept constant
    'rlnFixSigmaOffsetEstimates': bool,
    # Flag to indicate that the estimates for the stddev in the origin offsets should be kept constant
    'rlnFixTauEstimates': bool,
    # Flag to indicate that the estimates for the power spectra of the signal (i.e. the references) should be kept constant
    'rlnHasConverged': bool,  # Flag to indicate that the optimization has converged
    'rlnHasHighFscAtResolLimit': bool,  # Flag to indicate that the FSC at the resolution limit is significant
    'rlnHasLargeSizeIncreaseIterationsAgo': int,
    # How many iterations have passed since the last large increase in image size
    'rlnDoHelicalRefine': bool,  # Flag to indicate that helical refinement should be performed
    'rlnIgnoreHelicalSymmetry': bool,  # Flag to indicate that helical symmetry is ignored in 3D reconstruction
    'rlnFourierMask': str,  # Name of an FFTW-centred Fourier mask to be applied to the Projector for refinement.
    'rlnHelicalTwistInitial': float,  # The intial helical twist (rotation per subunit) in degrees before refinement
    'rlnHelicalRiseInitial': float,  # The initial helical rise (translation per subunit) in Angstroms before refinement
    'rlnHelicalCentralProportion': float,
    # Only expand this central fraction of the Z axis when imposing real-space helical symmetry
    'rlnNrHelicalNStart': int,  # The N-number for an N-start helix
    'rlnHelicalMaskTubeInnerDiameter': float,
    # Inner diameter of helical tubes in Angstroms (for masks of helical references and particles)
    'rlnHelicalMaskTubeOuterDiameter': float,
    # Outer diameter of helical tubes in Angstroms (for masks of helical references and particles)
    'rlnHelicalSymmetryLocalRefinement': bool,
    # Flag to indicate that local refinement of helical parameters should be performed
    'rlnHelicalSigmaDistance': float,  # Sigma of distance along the helical tracks
    'rlnHelicalKeepTiltPriorFixed': bool,
    # Flag to indicate that helical tilt priors are kept fixed (at 90 degrees) in global angular searches
    'rlnLowresLimitExpectation': float,  # Low-resolution-limit (in Angstrom) for the expectation step
    'rlnHighresLimitExpectation': float,  # High-resolution-limit (in Angstrom) for the expectation step
    'rlnHighresLimitSGD': float,  # High-resolution-limit (in Angstrom) for Stochastic Gradient Descent
    'rlnDoIgnoreCtfUntilFirstPeak': bool,  # Flag to indicate that the CTFs should be ignored until their first peak
    'rlnIncrementImageSize': int,
    # Number of Fourier shells to be included beyond the resolution where SSNR^MAP drops below 1
    'rlnCurrentIteration': int,  # The number of the current iteration
    'rlnLocalSymmetryFile': str,  # Local symmetry description file containing list of masks and their operators
    'rlnJoinHalvesUntilThisResolution': float,
    # Resolution (in Angstrom) to join the two random half-reconstructions to prevent their diverging orientations (for C-symmetries)
    'rlnMagnificationSearchRange': float,  # Search range for magnification correction
    'rlnMagnificationSearchStep': float,  # Step size  for magnification correction
    'rlnMaximumCoarseImageSize': int,
    # Maximum size of the images to be used in the first pass of the adaptive oversampling strategy (may be smaller than the original image size)
    'rlnMaxNumberOfPooledParticles': int,
    # Maximum number particles that are processed together to speed up calculations
    'rlnModelStarFile': str,  # STAR file with metadata for the model that is being refined
    'rlnModelStarFile2': str,
    # STAR file with metadata for the second model that is being refined (from random halves of the data)
    'rlnNumberOfIterations': int,  # Maximum number of iterations to be performed
    'rlnNumberOfIterWithoutResolutionGain': int,  # Number of iterations that have passed without a gain in resolution
    'rlnNumberOfIterWithoutChangingAssignments': int,
    # Number of iterations that have passed without large changes in orientation and class assignments
    'rlnOpticsStarFile': str,  # STAR file with metadata for the optical groups (new as of version 3.1)
    'rlnOutputRootName': str,  # Rootname for all output files (this may include a directory structure
    'rlnParticleDiameter': float,
    # Diameter of the circular mask to be applied to all experimental images (in Angstroms)
    'rlnRadiusMaskMap': int,  # Radius of the spherical mask to be applied to all references (in Angstroms)
    'rlnRadiusMaskExpImages': int,
    # Radius of the circular mask to be applied to all experimental images (in Angstroms)
    'rlnRandomSeed': int,  # Seed (i.e. a number) for the random number generator
    'rlnRefsAreCtfCorrected': bool,  # Flag to indicate that the input references have been CTF-amplitude corrected
    'rlnSmallestChangesClasses': int,
    # Smallest changes thus far in the optimal class assignments (in numer of particles).
    'rlnSmallestChangesOffsets': float,  # Smallest changes thus far in the optimal offset assignments (in pixels).
    'rlnSmallestChangesOrientations': float,
    # Smallest changes thus far in the optimal orientation assignments (in degrees).
    'rlnOrientSamplingStarFile': str,  # STAR file with metadata for the orientational sampling
    'rlnSolventMaskName': str,
    # Name of an image that contains a (possibly soft) mask for the solvent area (values=0 for solvent
    'rlnSolventMask2Name': str,
    # Name of a secondary solvent mask (e.g. to flatten density inside an icosahedral virus)
    'rlnTauSpectrumName': str,  # Name of a STAR file that holds a tau2-spectrum
    'rlnUseTooCoarseSampling': bool,
    # Flag to indicate that the angular sampling on the sphere will be one step coarser than needed to speed up calculations
    'rlnWidthMaskEdge': int,
    # Width (in pixels) of the soft edge for spherical/circular masks to be used for solvent flattening
    'rlnIsFlip': bool,  # Flag to indicate that an image should be mirrored
    'rlnOrientationsID': int,  # ID (i.e. a unique number) for an orientation
    'rlnOriginX': float,  # X-coordinate (in pixels) for the origin of rotation
    'rlnOriginY': float,  # Y-coordinate (in pixels) for the origin of rotation
    'rlnOriginZ': float,  # Z-coordinate (in pixels) for the origin of rotation
    'rlnOriginXPrior': float,  # Center of the prior on the X-coordinate (in pixels) for the origin of rotation
    'rlnOriginYPrior': float,  # Center of the prior on the Y-coordinate (in pixels) for the origin of rotation
    'rlnOriginZPrior': float,  # Center of the prior on the Z-coordinate (in pixels) for the origin of rotation
    'rlnOriginXAngst': float,  # X-coordinate (in Angstrom) for the origin of rotation
    'rlnOriginYAngst': float,  # Y-coordinate (in Angstrom) for the origin of rotation
    'rlnOriginZAngst': float,  # Z-coordinate (in Angstrom) for the origin of rotation
    'rlnOriginXPriorAngst': float,  # Center of the prior on the X-coordinate (in Angstrom) for the origin of rotation
    'rlnOriginYPriorAngst': float,  # Center of the prior on the Y-coordinate (in Angstrom) for the origin of rotation
    'rlnOriginZPriorAngst': float,  # Center of the prior on the Z-coordinate (in Angstrom) for the origin of rotation
    'rlnAngleRot': float,  # First Euler angle (rot
    'rlnAngleRotPrior': float,  # Center of the prior (in degrees) on the first Euler angle (rot)
    'rlnAngleRotFlipRatio': float,  # Flip ratio of bimodal rot prior (0~0.5
    'rlnAngleTilt': float,  # Second Euler angle (tilt
    'rlnAngleTiltPrior': float,  # Center of the prior (in degrees) on the second Euler angle (tilt)
    'rlnAnglePsi': float,  # Third Euler
    'rlnAnglePsiPrior': float,  # Center of the prior (in degrees) on the third Euler angle (psi)
    'rlnAnglePsiFlipRatio': float,  # Flip ratio of bimodal psi prior (0~0.5
    'rlnAnglePsiFlip': bool,  # Flag to indicate that psi prior angle has been flipped  // KThurber
    'rlnAutopickFigureOfMerit': float,  # Autopicking FOM for a particle
    'rlnHelicalTubeID': int,  # Helical tube ID for a helical segment
    'rlnHelicalTubePitch': float,  # Cross-over distance for a helical segment (A)
    'rlnHelicalTrackLength': float,
    # Distance (in pix) from the position of this helical segment to the starting point of the tube
    'rlnHelicalTrackLengthAngst': float,
    # Distance (in A) from the position of this helical segment to the starting point of the tube
    'rlnClassNumber': int,  # Class number for which a particle has its highest probability
    'rlnLogLikeliContribution': float,  # Contribution of a particle to the log-likelihood target function
    'rlnParticleId': int,  # ID (i.e. a unique number) for a particle
    'rlnParticleFigureOfMerit': float,  # Developmental FOM for a particle
    'rlnKullbackLeiblerDivergence': float,  # Kullback-Leibler divergence for a particle
    'rlnRandomSubset': int,  # Random subset to which this particle belongs
    'rlnBeamTiltClass': int,  # Beam-tilt class of a particle
    'rlnParticleName': str,  # Name for a particle
    'rlnOriginalParticleName': str,  # Original name for a particles
    'rlnNrOfSignificantSamples': int,
    # Number of orientational/class assignments (for a particle) with sign.probabilities in the 1st pass of adaptive oversampling /**< particle
    'rlnNrOfFrames': int,  # Number of movie frames that were collected for this particle
    'rlnAverageNrOfFrames': int,  # Number of movie frames that one averages over upon extraction of movie-particles
    'rlnMovieFramesRunningAverage': int,
    # Number of movie frames inside the running average that will be used for movie-refinement
    'rlnMaxValueProbDistribution': float,
    # Maximum value of the (normalised) probability function for a particle /**< particle
    'rlnParticleNumber': int,  # Number of particles
    'rlnPipeLineJobCounter': int,  # Number of the last job in the pipeline
    'rlnPipeLineNodeName': str,  # Name of a Node in the pipeline
    'rlnPipeLineNodeType': int,  # Type of a Node in the pipeline
    'rlnPipeLineNodeTypeLabel': str,  # Name for the Node Type in the pipeline
    'rlnPipeLineProcessAlias': str,  # Alias of a Process in the pipeline
    'rlnPipeLineProcessName': str,  # Name of a Process in the pipeline
    'rlnPipeLineProcessType': int,  # Type of a Process in the pipeline
    'rlnPipeLineProcessTypeLabel': str,  # Name for the Process type in the pipeline
    'rlnPipeLineProcessStatus': int,  # Status of a Process in the pipeline (integer for running
    'rlnPipeLineProcessStatusLabel': str,  # Name for the status of a Process in the pipeline (running
    'rlnPipeLineEdgeFromNode': str,  # Name of the origin of an edge
    'rlnPipeLineEdgeToNode': str,  # Name of the to-Node in an edge
    'rlnPipeLineEdgeProcess': str,  # Name of the destination of an edge
    'rlnFinalResolution': float,  # Final estimated resolution after postprocessing (in Angstroms)
    'rlnBfactorUsedForSharpening': float,  # Applied B-factor in the sharpening of the map
    'rlnParticleBoxFractionMolecularWeight': float,  # Fraction of protein voxels in the box
    'rlnParticleBoxFractionSolventMask': float,  # Fraction of protein voxels in the box
    'rlnFourierShellCorrelation': float,  # FSC value (of unspecified type
    'rlnFourierShellCorrelationCorrected': float,
    # Final FSC value: i.e. after correction based on masking of randomized-phases maps
    'rlnFourierShellCorrelationParticleMolWeight': float,  # CisTEM-like correction of unmasked FSCs
    'rlnFourierShellCorrelationParticleMaskFraction': float,  # CisTEM-like correction of unmasked FSCs
    'rlnFourierShellCorrelationMaskedMaps': float,  # FSC value after masking of the original maps
    'rlnFourierShellCorrelationUnmaskedMaps': float,  # FSC value before masking of the original maps
    'rlnCorrectedFourierShellCorrelationPhaseRandomizedMaskedMaps': float,
    # FSC value after masking of the randomized-phases maps
    'rlnAmplitudeCorrelationMaskedMaps': float,
    # Correlation coefficient between amplitudes in Fourier shells of masked maps
    'rlnAmplitudeCorrelationUnmaskedMaps': float,
    # Correlation coefficient between amplitudes in Fourier shells of unmasked maps
    'rlnDifferentialPhaseResidualMaskedMaps': float,  # Differential Phase Residual in Fourier shells of masked maps
    'rlnDifferentialPhaseResidualUnmaskedMaps': float,  # Differential Phase Residual in Fourier shells of unmasked maps
    'rlnFittedInterceptGuinierPlot': float,  # The fitted intercept of the Guinier-plot
    'rlnFittedSlopeGuinierPlot': float,  # The fitted slope of the Guinier-plot
    'rlnCorrelationFitGuinierPlot': float,  # The correlation coefficient of the fitted line through the Guinier-plot
    'rlnLogAmplitudesOriginal': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes of the input map
    'rlnLogAmplitudesMTFCorrected': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after MTF correction
    'rlnLogAmplitudesWeighted': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after FSC-weighting
    'rlnLogAmplitudesSharpened': float,
    # Y-value for Guinier plot: the logarithm of the radially averaged amplitudes after sharpening
    'rlnLogAmplitudesIntercept': float,
    # Y-value for Guinier plot: the fitted plateau of the logarithm of the radially averaged amplitudes
    'rlnResolutionSquared': float,  # X-value for Guinier plot: squared resolution in 1/Angstrom^2
    'rlnMolecularWeight': float,
    # Molecular weight of the ordered mass inside the box for calculating cisTEM-like part.FSC (in kDa)
    'rlnMtfValue': float,  # Value of the detectors modulation transfer function (between 0 and 1)
    'rlnRandomiseFrom': float,  # Resolution (in A) from which the phases are randomised in the postprocessing step
    'rlnUnfilteredMapHalf1': str,  # Name of the unfiltered map from halfset 1
    'rlnUnfilteredMapHalf2': str,  # Name of the unfiltered map from halfset 2
    'rlnPostprocessedMap': str,  # Name of the postprocssed map
    'rlnPostprocessedMapMasked': str,  # Name of the masked postprocssed map
    'rlnIs3DSampling': bool,  # Flag to indicate this concerns a 3D sampling
    'rlnIs3DTranslationalSampling': bool,  # Flag to indicate this concerns a x
    'rlnHealpixOrder': int,  # Healpix order for the sampling of the first two Euler angles (rot
    'rlnHealpixOrderOriginal': int,  # Original healpix order for the sampling of the first two Euler angles (rot
    'rlnTiltAngleLimit': float,  # Values to which to limit the tilt angles (positive for keeping side views
    'rlnOffsetRange': float,  # Search range for the origin offsets (in Angstroms)
    'rlnOffsetStep': float,  # Step size for the searches in the origin offsets (in Angstroms)
    'rlnOffsetRangeOriginal': float,  # Original search range for the origin offsets (in Angstroms)
    'rlnOffsetStepOriginal': float,  # Original step size for the searches in the origin offsets (in Angstroms)
    'rlnHelicalOffsetStep': float,  # Step size for the searches of offsets along helical axis (in Angstroms)
    'rlnSamplingPerturbInstance': float,  # Random instance of the random perturbation on the orientational sampling
    'rlnSamplingPerturbFactor': float,
    # Factor for random perturbation on the orientational sampling (between 0 no perturbation and 1 very strong perturbation)
    'rlnPsiStep': float,  # Step size (in degrees) for the sampling of the in-plane rotation angle (psi)
    'rlnPsiStepOriginal': float,
    # Original step size (in degrees) for the sampling of the in-plane rotation angle (psi)
    'rlnSymmetryGroup': str,  # Symmetry group (e.g.
    'rlnSchemeEdgeNumber': int,  # Numbered index of an edge inside a Scheme
    'rlnSchemeEdgeInputNodeName': str,  # Name of the input Node for a schedule Edge
    'rlnSchemeEdgeOutputNodeName': str,  # Name of the output Node for a schedule Edge
    'rlnSchemeEdgeIsFork': bool,  # Flag to indicate that this Edge is a Fork
    'rlnSchemeEdgeOutputNodeNameIfTrue': str,
    # Name of the output Node for a schedule Fork if the associated Boolean is True
    'rlnSchemeEdgeBooleanVariable': str,  # Name of the associated Boolean variable if this Edge is a Fork
    'rlnSchemeCurrentNodeName': str,  # Name of the current Node for this Scheme
    'rlnSchemeOriginalStartNodeName': str,  # Name of the original starting Node for this Scheme
    'rlnSchemeEmailAddress': str,  # Email address to send message when Scheme finishes
    'rlnSchemeName': str,  # Name for this Scheme
    'rlnSchemeJobName': str,  # Name of a Job in a Scheme
    'rlnSchemeJobNameOriginal': str,  # Original name of a Job in a Scheme
    'rlnSchemeJobMode': str,  # Mode on how to execute a Job
    'rlnSchemeJobHasStarted': bool,  # Flag to indicate whether a Job has started already in the execution of the Scheme
    'rlnSchemeOperatorName': str,  # Name of a Boolean operator in the Scheme
    'rlnSchemeOperatorType': str,  # Type of an operator in the Scheme
    'rlnSchemeOperatorInput1': str,  # Name of the 1st input to the operator
    'rlnSchemeOperatorInput2': str,  # Name of the 2nd input to the operator
    'rlnSchemeOperatorOutput': str,  # Name of the output variable on which this operator acts
    'rlnSchemeBooleanVariableName': str,  # Name of a Boolean variable in the Scheme
    'rlnSchemeBooleanVariableValue': bool,  # Value of a Boolean variable in the Scheme
    'rlnSchemeBooleanVariableResetValue': bool,  # Value which a Boolean variable will take upon a reset
    'rlnSchemeFloatVariableName': str,  # Name of a Float variable in the Scheme
    'rlnSchemeFloatVariableValue': float,  # Value of a Float variable in the Scheme
    'rlnSchemeFloatVariableResetValue': float,  # Value which a Float variable will take upon a reset
    'rlnSchemeStringVariableName': str,  # Name of a String variable in the Scheme
    'rlnSchemeStringVariableValue': str,  # Value of a String variable in the Scheme
    'rlnSchemeStringVariableResetValue': str,  # Value which a String variable will take upon a reset
    'rlnSelected': int,  # Flag whether an entry in a metadatatable is selected (1) in the viewer or not (0)
    'rlnParticleSelectZScore': float,  # Sum of Z-scores from particle_select. High Z-scores are likely to be outliers.
    'rlnSortedIndex': int,  # Index of a metadata entry after sorting (first sorted index is 0).
    'rlnStarFileMovieParticles': str,  # Filename of a STAR file with movie-particles in it
    'rlnPerFrameCumulativeWeight': float,
    # Sum of the resolution-dependent relative weights from the first frame until the given frame
    'rlnPerFrameRelativeWeight': float,  # The resolution-dependent relative weights for a given frame
    'rlnResolution': float,  # Resolution (in 1/Angstroms)
    'rlnAngstromResolution': float,  # Resolution (in Angstroms)
    'rlnResolutionInversePixel': float,  # Resolution (in 1/pixel
    'rlnSpectralIndex': int,  # Spectral index (i.e. distance in pixels to the origin in Fourier space)
    'rlnTomoName': str,  # Arbitrary name for a tomogram
    'rlnTomoTiltSeriesName': str,  # Tilt series file name
    'rlnTomoFrameCount': int,  # Number of tilts in a tilt series
    'rlnTomoSizeX': int,  # Width of a bin-1 tomogram in pixels
    'rlnTomoSizeY': int,  # Height of a bin-1 tomogram in pixels
    'rlnTomoSizeZ': int,  # Depth of a bin-1 tomogram in pixels
    'rlnTomoProjX': str,  # First row of the projection matrix
    'rlnTomoProjY': str,  # Second row of the projection matrix
    'rlnTomoProjZ': str,  # Third row of the projection matrix
    'rlnTomoProjW': str,  # Fourth row of the projection matrix
    'rlnTomoHand': float,  # Handedness of a tomogram (i.e. slope of defocus over the image-space z coordinate)
    'rlnTomoFiducialsStarFile': str,  # STAR file containing the 3D locations of fiducial markers
    'rlnTomoTiltSeriesPixelSize': float,  # Pixel size of the original tilt series
    'rlnTomoSubtomogramRot': float,  # First Euler angle of a subtomogram (rot
    'rlnTomoSubtomogramTilt': float,  # Second Euler angle of a subtomogram (tilt
    'rlnTomoSubtomogramPsi': float,  # Third Euler angle of a subtomogram (psi
    'rlnTomoSubtomogramBinning': float,  # Binning level of a subtomogram
    'rlnTomoParticleName': str,  # Name of each individual particle
    'rlnTomoParticleId': int,  # Unique particle index
    'rlnTomoManifoldIndex': int,  # Index of a 2D manifold in a tomogram
    'rlnTomoManifoldType': str,  # Name of the manifold type
    'rlnTomoManifoldParams': str,  # Set of coefficients pertaining to a generic 2D manifold in a tomogram
    'rlnTomoDefocusSlope': float,  # Rate of change of defocus over depth
    'rlnTomoParticlesFile': str,  # Name of particles STAR file
    'rlnTomoTomogramsFile': str,  # Name of tomograms STAR file
    'rlnTomoManifoldsFile': str,  # Name of manifolds STAR file
    'rlnTomoTrajectoriesFile': str,  # Name of trajectories STAR file
    'rlnTomoReferenceMap1File': str,  # Name of first reference map file
    'rlnTomoReferenceMap2File': str,  # Name of second reference map file
    'rlnTomoReferenceMaskFile': str,  # Name of mask file corresponding to a pair of reference maps
    'rlnTomoReferenceFscFile': str,  # Name of FSC STAR file corresponding to a pair of reference maps
    'rlnTomoImportOffsetX': float,  # X offset of a tomogram
    'rlnTomoImportOffsetY': float,  # Y offset of a tomogram
    'rlnTomoImportOffsetZ': float,  # Z offset of a tomogram
    'rlnTomoImportImodDir': str,  # IMOD tilt-series directory
    'rlnTomoImportCtfFindFile': str,  # CTFFind output file
    'rlnTomoImportCtfPlotterFile': str,  # CTFPlotter output file
    'rlnTomoImportOrderList': str,  # Frame order list
    'rlnTomoImportFractionalDose': float,  # Fractional dose of a tilt series
    'rlnTomoImportCulledFile': str,  # File name of a tilt series with certain frames removed
    'rlnTomoImportParticleFile': str,  # File name of a STAR file containing 3D particle coordinates
    'rlnTomoRelativeIceThickness': float,  # Relative ice thickness times its extinction coefficient
    'rlnTomoRelativeLuminance': float,  # Relative beam luminance
    'rlnTomoIceNormalX': float,  # X component of the estimated ice normal
    'rlnTomoIceNormalY': float,  # Y component of the estimated ice normal
    'rlnTomoIceNormalZ': float,  # Z component of the estimated ice normal
    'rlnTomoDeformationGridSizeX': int,  # Width of the 2D-deformation grid
    'rlnTomoDeformationGridSizeY': int,  # Height of the 2D-deformation grid
    'rlnTomoDeformationType': str,  # Model used to express 2D deformations
    'rlnTomoDeformationCoefficients': str,  # Coefficients describing a 2D deformation of a micrograph
    'rlnTomoTempPredTimesObs': float,  # Sum over products of predicted and observed values
    'rlnTomoTempPredSquared': float,  # Sum over squares of predicted values
    'rlnTomoTiltMovieIndex': int,  # Chronological index of a tilt movie
    'rlnTomoTiltMovieFile': str,  # Movie containing the frames of a tilt
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

    def clone(self):
        return copy.deepcopy(self)

    def clear(self):
        for attribute in dir(self):
            if "data_" in attribute and "_labels" not in attribute:
                setattr(self, attribute + "_labels", OrderedDict())
                setattr(self, attribute, [])

    def addDataTable(self, dataTableName, loop=False):
        setattr(self, dataTableName + "_labels", OrderedDict())
        setattr(self, dataTableName + "_loop", loop)
        setattr(self, dataTableName, [])

    def removeDataTable(self, dataTableName):
        delattr(self, dataTableName)

    def _setItemValue(self, item, label, value):
        setattr(item, label.name, label.type(value))

    def _addLabel(self, dataTableName, labelName):
        getattr(self, dataTableName + "_labels")[labelName] = Label(labelName)

    def read(self, input_star):
        self.clear()
        found_label = False
        found_loop = False
        non_loop_values = []

        f = open(input_star)

        def setItemValues(currentTableRead, values):
            # Iterate in pairs (zipping) over labels and values in the row
            item = Item()
            # Dynamically set values, using label type (str by default)
            for label, value in izip(getattr(self, currentTableRead + "_labels").values(), values):
                self._setItemValue(item, label, value)
            getattr(self, currentTableRead).append(item)

        for line in f:
            values = line.strip().split()

            if not values and found_label and not found_loop:  # empty lines after non-loop labels
                setItemValues(currentTableRead, non_loop_values)
                found_label = False
                continue

            if not values:  # empty lines
                continue

            if "#" in values[0]:
                continue

            if "data_" in values[0]:
                if values[0] == "data_":
                    self.version = "3"
                else:
                    self.version = "3.1"
                self.addDataTable(values[0])
                currentTableRead = values[0]
                found_label = False
                found_loop = False
                non_loop_values = []
                continue

            if values[0].startswith('loop_'):  # Label line
                setattr(self, currentTableRead + "_loop", True)
                found_loop = True
                continue

            if values[0].startswith('_rln'):  # Label line
                # Skip leading underscore in label name
                self._addLabel(currentTableRead, labelName=values[0][1:])
                if not found_loop:
                    non_loop_values.append(values[1])
                found_label = True
            elif found_label:  # Read data lines after at least one label
                setItemValues(currentTableRead, values)

        f.close()

    def _write(self, output_file):
        # Write labels and prepare the line format for rows
        for attribute in dir(self):
            if "data_" in attribute and "_labels" not in attribute and "_loop" not in attribute:
                line_format = ""
                if self.version == "3.1":
                    if "_loop" not in attribute:
                        output_file.write("\n# version 30001\n\n%s\n\n" % attribute)
                    if getattr(self, attribute + "_loop"):
                        output_file.write("loop_\n")
                else:
                    output_file.write("\n%s\n\nloop_\n" % attribute)

                for i, l in enumerate(getattr(self, attribute + "_labels").values()):
                    # Retrieve the type of the label
                    t = l.type
                    if getattr(self, attribute + "_loop"):
                        output_file.write("_%s #%d \n" % (l.name, i + 1))
                        if t is float:
                            line_format += "%%(%s)f \t" % l.name
                        elif t is int:
                            line_format += "%%(%s)d \t" % l.name
                        else:
                            line_format += "%%(%s)s \t" % l.name
                    else:
                        if t is float:
                            line_format = "_%-35s%15f\n"
                        elif t is int:
                            line_format = "_%-35s%15d\n"
                        else:
                            line_format = "_%-35s%15s\n"
                        output_file.write(line_format % (l.name, getattr(getattr(self, attribute)[0], l.name)))

                if getattr(self, attribute + "_loop"):
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

    def isLoop(self, dataTableName="data_particles"):
        return getattr(self, dataTableName + "_loop")

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
