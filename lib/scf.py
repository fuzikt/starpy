''' Adapted from https://github.com/LyumkisLab/CommandLineSCF/tree/main'''

import numpy as np
from .symmetries import Symmetry

class SCFstar:
    def __init__(self, particles, fourierRadius=50, numberToUse=0, tiltAngle=0, sym="C1"):
        self.particles = particles

        self.FourierRadiusInt = fourierRadius
        self.NumberToUse = numberToUse # default 0 => all
        self.TiltAngle = tiltAngle
        self.Sym = sym

        self.selectedParticles = self.selectRandomParticles(particles, self.NumberToUse)

        if not(self.TiltAngle > 0 or self.Sym == "C1"):
            symmetry = Symmetry(self.Sym)
            self.selectedParticles = symmetry.sym_expand_particles(self.selectedParticles)

        self.AllProjPointsInitial, self.OutPutAngles = self.particles2nVec(self.particles)
        self.AllProjPoints, _ = self.particles2nVec(self.selectedParticles)

        self.AllProjPointsB4Sym = self.AllProjPoints.copy()

        self.NumberToUseInt = len(self.selectedParticles)

        self.SpiralVec, self.NumFib = self.CreateSpiral(self.FourierRadiusInt)

        self.InnerProdBooleanSum0, self.InnerProdBooleanSum1, self.AllProjAndTilts, \
            self.TiltedNVecs, self.AllProjPoints = self.get_InnerProdBooleanSum1(self.SpiralVec, self.OutPutAngles, \
                                                                                 self.FourierRadiusInt,
                                                                                 self.NumberToUseInt,
                                                                                 self.AllProjPoints, \
                                                                                 self.TiltAngle)

        self.scf, self.scfStar = self.calcSFCstar(self.InnerProdBooleanSum1)

    def particles2nVec(self, particles):
        eulerAngles = []
        for particle in particles:
            eulerAngles.append([particle.rlnAnglePsi,
                                particle.rlnAngleTilt,
                                particle.rlnAngleRot])
        # convert to numpy array
        OutPutAngles = np.array(eulerAngles)
        psiVec = np.radians(OutPutAngles[:, 0])
        tiltVec = np.radians(OutPutAngles[:, 1])
        rotVec = np.radians(OutPutAngles[:, 2])

        nVecx = np.sin(tiltVec) * np.cos(rotVec)
        nVecy = np.sin(tiltVec) * np.sin(rotVec)
        nVecz = np.cos(tiltVec)

        nVec = np.vstack((nVecx, nVecy, nVecz)).T

        return nVec, OutPutAngles

    def selectRandomParticles(self, particles, num_samples=0):
        self.AllProjPointsInitial = len(particles)

        if len(particles) > num_samples and not num_samples == 0:
            indices = np.random.choice(len(particles), num_samples, replace=False)
            selected_particles = [particles[i] for i in indices]
            return selected_particles
        else:
            return particles

    def CreateSpiral(self, FourierRadiusInt):

        forceNumberofRaystothisinteger = np.int64(2 * np.pi * FourierRadiusInt * FourierRadiusInt)
        forceNumberofRaystothisinteger = np.min([forceNumberofRaystothisinteger, 5000])
        SpiralVec = self.GetIFibDirections_Now(forceNumberofRaystothisinteger)

        NumFib = np.shape(SpiralVec)[0]

        return SpiralVec, NumFib

    # @autojit
    def GetIFibDirections_Now(self, forceNumberofRaystothisinteger):
        NumPoints = forceNumberofRaystothisinteger

        phi = (1.0 + np.sqrt(5.0)) / 2.0 - 1
        ga = phi * 2.0 * np.pi # The Golden Angle

        jLongitude = np.arange(NumPoints)

        longitude = ga * jLongitude
        latitude = np.arcsin(1.0 * jLongitude / NumPoints)  # for hemisphere
        nhatz = np.sin(latitude)
        nhatx = np.cos(latitude) * np.cos(longitude)
        nhaty = np.cos(latitude) * np.sin(longitude)

        nVec = np.concatenate([nhatx, nhaty, nhatz])
        nVec = np.reshape(nVec, [3, NumPoints])

        return nVec.T

    def get_InnerProdBooleanSum1(self, SpiralVec, OutPutAngles, FourierRadiusInt, \
                                 NumberForEachTilt, AllProjPoints, TiltInDegB):

        sVec = np.shape(AllProjPoints)[0]

        PsiVec = 360.0 * np.random.rand(sVec)
        ThetaVec = OutPutAngles[:, 1]
        PhiVec = OutPutAngles[:, 2]

        if TiltInDegB > 0:
            TiltedNVecs = np.zeros_like(AllProjPoints)

            CTilt = np.cos(TiltInDegB * np.pi / 180.0)
            STilt = np.sin(TiltInDegB * np.pi / 180.0)
            TiltMat = np.array([[CTilt, 0, -STilt], [0, 1, 0], [STilt, 0, CTilt]])

            CPsi = np.cos(PsiVec * np.pi / 180.0)
            SPsi = np.sin(PsiVec * np.pi / 180.0)

            CTheta = np.cos(ThetaVec * np.pi / 180.0)
            STheta = np.sin(ThetaVec * np.pi / 180.0)

            CPhi = np.cos(PhiVec * np.pi / 180.0)
            SPhi = np.sin(PhiVec * np.pi / 180.0)

            for jAngle in range(sVec):
                CNow = CPsi[jAngle]
                SNow = SPsi[jAngle]
                PsiMat = np.array([[CNow, SNow, 0], [-SNow, CNow, 0], [0, 0, 1]])

                CNow = CTheta[jAngle]
                SNow = STheta[jAngle]
                ThetaMat = np.array([[CNow, 0, -SNow], [0, 1, 0], [SNow, 0, CNow]])

                CNow = CPhi[jAngle]
                SNow = SPhi[jAngle]
                PhiMat = np.array([[CNow, SNow, 0], [-SNow, CNow, 0], [0, 0, 1]])

                TiltPsi = np.dot(TiltMat, PsiMat)
                ThetaPhi = np.dot(ThetaMat, PhiMat)

                All4 = np.dot(TiltPsi, ThetaPhi)

                TiltedNVecs[jAngle, :] = All4[2, :]

            InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts = \
                self.ReturnSamplingLoop(SpiralVec, TiltedNVecs, FourierRadiusInt, 0, NumberForEachTilt)

            return InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts, TiltedNVecs, AllProjPoints

        NVecs0 = AllProjPoints

        NVecs0 = np.asarray(NVecs0)
        TiltedNVecs = NVecs0.copy()

        AllProjPoints = NVecs0.copy()  # AllProjPoints gets redefined here to the symmetrized version

        # print('Examining sAllProjPoints=%g' % np.shape(AllProjPoints)[0])

        InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts = \
            self.ReturnSamplingLoop(SpiralVec, NVecs0, FourierRadiusInt, 0, NumberForEachTilt)

        return InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts, TiltedNVecs, AllProjPoints

    def ReturnSamplingLoop(self, SpiralVec, AllProjPoints, FourierRadius, TiltInDeg, NumberForEachTilt):

        sSpiralVec = len(SpiralVec)
        InnerProdBooleanSum1Sum = np.zeros(sSpiralVec)
        InnerProdBooleanSum0Sum = np.shape(AllProjPoints)[0]
        sAllProjPoints = len(AllProjPoints)

        ChunkSize = np.int64(10000 * 3000 / sSpiralVec)

        NumChunks = sAllProjPoints // ChunkSize
        # print('sAllProjPoints = %g; ' % (sAllProjPoints))
        # print('NumChunks = %g; ChunkSize=%g' % (NumChunks, ChunkSize))

        jChunk = 0

        for jChunk in range(NumChunks):
            AllProjPointsInner = AllProjPoints[jChunk * ChunkSize:(jChunk + 1) * ChunkSize]
            InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts = \
                self.ReturnSampling(SpiralVec, AllProjPointsInner, FourierRadius, TiltInDeg, NumberForEachTilt)
            InnerProdBooleanSum1Sum += InnerProdBooleanSum1

        AllProjPointsInner = AllProjPoints[jChunk * ChunkSize:]
        InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts = \
            self.ReturnSampling(SpiralVec, AllProjPointsInner, FourierRadius, TiltInDeg, NumberForEachTilt)
        InnerProdBooleanSum1Sum += InnerProdBooleanSum1

        return InnerProdBooleanSum0Sum, InnerProdBooleanSum1Sum, AllProjAndTilts

    # @autojit
    def ReturnSampling(self, SpiralVec, AllProjPoints, FourierRadius, TiltInDeg, NumberForEachTilt):

        tiltRad = TiltInDeg * np.pi / 180

        # AllProjPoints may be very large, so we need to chunk it
        InnerProductDirMatrix = np.dot(SpiralVec, AllProjPoints.T)

        vv = np.where(np.abs(InnerProductDirMatrix) * FourierRadius < 0.5)

        InnerProdBoolean = np.zeros_like(InnerProductDirMatrix)
        InnerProdBoolean[vv[0], vv[1]] = 1

        InnerProdBooleanSum0 = np.sum(InnerProdBoolean, axis=0)
        InnerProdBooleanSum1 = np.sum(InnerProdBoolean, axis=1)

        if TiltInDeg == 0:
            return InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjPoints

        AllPointsPerp = np.argmin(np.abs(AllProjPoints), axis=1)
        print('np.shape(AllProjPoints), np.shape(AllPointsPerp)')
        print(np.shape(AllProjPoints), np.shape(AllPointsPerp))

        PerpVector = np.zeros_like(AllProjPoints)
        PerpPerpVector = np.zeros_like(AllProjPoints)

        # Perp0
        Perp0 = np.where(AllPointsPerp == 0)[0]

        nx = AllProjPoints[Perp0, 0]
        nx = np.asarray(nx)
        ny = AllProjPoints[Perp0, 1]
        ny = np.asarray(ny)
        nz = AllProjPoints[Perp0, 2]
        nz = np.asarray(nz)

        normyz = np.sqrt(ny * ny + nz * nz)

        PerpVector[Perp0, 1] = -nz / normyz
        PerpVector[Perp0, 2] = ny / normyz

        PerpPerpVector[Perp0, 0] = nz * nz / normyz
        PerpPerpVector[Perp0, 0] += ny * ny / normyz
        PerpPerpVector[Perp0, 1] = -nx * ny / normyz
        PerpPerpVector[Perp0, 2] = -nx * nz / normyz

        # Perp1

        Perp1 = np.where(AllPointsPerp == 1)[0]

        nx = AllProjPoints[Perp1, 0]
        nx = np.asarray(nx)
        ny = AllProjPoints[Perp1, 1]
        ny = np.asarray(ny)
        nz = AllProjPoints[Perp1, 2];
        nz = np.asarray(nz)

        normxz = np.sqrt(nx * nx + nz * nz)
        PerpVector[Perp1, 2] = -nx / normxz
        PerpVector[Perp1, 0] = nz / normxz

        PerpPerpVector[Perp1, 0] = -nx * ny / normxz
        PerpPerpVector[Perp1, 1] = nx * nx / normxz
        PerpPerpVector[Perp1, 1] += nz * nz / normxz
        PerpPerpVector[Perp1, 2] = -ny * nz / normxz

        # Perp2

        Perp2 = np.where(AllPointsPerp == 2)[0]

        nx = AllProjPoints[Perp2, 0]
        nx = np.asarray(nx)
        ny = AllProjPoints[Perp2, 1]
        ny = np.asarray(ny)
        nz = AllProjPoints[Perp2, 2]
        nz = np.asarray(nz)

        normxy = np.sqrt(nx * nx + ny * ny)

        PerpVector[Perp2, 0] = -ny / normxy
        PerpVector[Perp2, 1] = nx / normxy

        PerpPerpVector[Perp2, 0] = -nx * nz / normxy
        PerpPerpVector[Perp2, 1] = -ny * nz / normxy
        PerpPerpVector[Perp2, 2] = nx * nx / normxy
        PerpPerpVector[Perp2, 2] += ny * ny / normxy

        NumPhi = int(90. * np.sin(tiltRad))
        NumAll = len(AllProjPoints)
        phi = np.linspace(0, 2 * np.pi, NumPhi)
        AllProjPointsAlong = np.cos(tiltRad) * AllProjPoints
        AllProjPointsPerp = np.sin(tiltRad) * PerpVector
        AllProjPointsPP = np.sin(tiltRad) * PerpPerpVector

        AllProjAndTilts = np.zeros([NumAll * NumPhi, 3])
        print(len(AllProjPoints))

        for jAll in range(NumAll):
            PerpNow = AllProjPointsPerp[jAll]
            PPNow = AllProjPointsPP[jAll]
            PerpAllNow = np.outer(np.cos(phi), PerpNow) + np.outer(np.sin(phi), PPNow)
            AllProjAndTilts[(jAll * NumPhi):((jAll + 1) * NumPhi), :] = AllProjPointsAlong[jAll, :] + PerpAllNow

        InnerProductDirMatrix = np.dot(SpiralVec, AllProjAndTilts.T)

        vv = np.where(np.abs(InnerProductDirMatrix) * FourierRadius < 0.5)

        InnerProdBoolean = np.zeros_like(InnerProductDirMatrix)
        InnerProdBoolean[vv[0], vv[1]] = 1

        InnerProdBooleanSum0 = np.sum(InnerProdBoolean, axis=0)
        InnerProdBooleanSum1 = np.sum(InnerProdBoolean, axis=1)

        return InnerProdBooleanSum0, InnerProdBooleanSum1, AllProjAndTilts

    def calcSFCstar(self, InnerProdBooleanSum1):

        GoodVoxels = np.where(InnerProdBooleanSum1 > 0)[0]
        RecipSamp = 1. / InnerProdBooleanSum1[GoodVoxels]
        NOver2k = np.mean(InnerProdBooleanSum1)
        NumberOfZeros = self.NumFib - len(GoodVoxels)
        FractionOfZeros = NumberOfZeros / self.NumFib
        FractionOfNonZeros = 1 - NumberOfZeros / self.NumFib
        QkoverPk = FractionOfZeros / FractionOfNonZeros

        SCF0 = 1 / (np.mean(RecipSamp) * NOver2k)

        SCFStar = SCF0 / (1 + QkoverPk * NOver2k * SCF0 / 2)

        #print('Number Of Zeros = ' + str(NumberOfZeros))
        #print('FractionOfZeros= %.3f' % FractionOfZeros)
        #print('SCF = %.3f' % SCF0)
        #print('SCF*= %.3f' % SCFStar)

        return SCF0, SCFStar

