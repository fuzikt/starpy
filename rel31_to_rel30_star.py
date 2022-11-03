#!/usr/bin/env python3

import os
import sys
from metadata import MetaData
import argparse


class Rel31ToRel30Star:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Converts particle star from RELION 3.1 format to RELION 3.0 format.")
        add = self.parser.add_argument
        add('--i', help="Input STAR filename (RELON 3.1 format).")
        add('--o', help="Output STAR filename.")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if len(sys.argv) == 1:
            self.error("No input file given.")

        if not os.path.exists(args.i):
            self.error("Input file '%s' not found."
                       % args.i)

    def get_particles(self, md):
        particles = []
        for particle in md:
            particles.append(particle)
        return particles

    def get_optic_groups(self, md):
        optic_groups = []
        for optic_group in md.data_optics:
            optic_groups.append(optic_group)
        return optic_groups

    def rel30format(self, particles, optic_groups):
        newParticles = []
        for particle in particles:
            particle.rlnVoltage=optic_groups[particle.rlnOpticsGroup-1].rlnVoltage
            particle.rlnSphericalAberration=optic_groups[particle.rlnOpticsGroup - 1].rlnSphericalAberration
            particle.rlnAmplitudeContrast=optic_groups[particle.rlnOpticsGroup - 1].rlnAmplitudeContrast
            particle.rlnMagnification=10000
            particle.rlnDetectorPixelSize=optic_groups[particle.rlnOpticsGroup - 1].rlnImagePixelSize
            particle.rlnOriginX = particle.rlnOriginXAngst / optic_groups[particle.rlnOpticsGroup - 1].rlnImagePixelSize
            particle.rlnOriginY = particle.rlnOriginYAngst / optic_groups[particle.rlnOpticsGroup - 1].rlnImagePixelSize
            particle.rlnBeamTiltClass = particle.rlnOpticsGroup
            newParticles.append(particle)
        return newParticles

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()

        self.validate(args)

        md = MetaData(args.i)
        if md.version != "3.1":
            self.error("Input file '%s' is not RELION 3.1 format."
                       % args.i)

        new_particles = []

        print("Reading in input star file.....")

        particles = self.get_particles(md)

        optic_groups = self.get_optic_groups(md)

        print("Total %s particles in input star file." % str(
            len(particles)))

        print("Total %s optic groups found in input star file." % str(
            len(optic_groups)))

        new_particles.extend(self.rel30format(particles, optic_groups))

        mdOut = MetaData()
        particleTableName = "data_"
        mdOut.addDataTable(particleTableName, True)
        mdOut.addLabels(particleTableName, md.getLabels("data_particles"))

        mdOut.addLabels(particleTableName,['rlnVoltage', 'rlnSphericalAberration', 'rlnAmplitudeContrast', 'rlnMagnification', 'rlnDetectorPixelSize', 'rlnOriginX', 'rlnOriginY', 'rlnBeamTiltClass'])
        mdOut.removeLabels("data_", ['rlnOpticsGroup', 'rlnOriginXAngst', 'rlnOriginYAngst'])

        mdOut.addData(particleTableName, new_particles)

        mdOut.write(args.o)

        print("New star file %s in RELION 3.0 format created. Have fun!" % args.o)


if __name__ == "__main__":
    Rel31ToRel30Star().main()
