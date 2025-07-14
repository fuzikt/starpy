#!/usr/bin/env python3

import sys
import argparse
from lib.symmetries import *


class printSymMatrices:
    def define_parser(self):
        self.parser = argparse.ArgumentParser(
            description="Prints out symmetry matrices in desired format.")
        add = self.parser.add_argument
        add('--sym', type=str, default="C1", help="Symmetry type (Default: C1).")
        add('--o', default="STDOUT", help="Output filename (Default: STDOUT - print to screen).")
        add('--biomt', action='store_true', help="Print symmetry matrices in REMARK 350 BIOMT format.")
        add('--mtrix', action='store_true', help="Print symmetry matrices in PDB MTRIX format.")
        add('--text', action='store_true', help="Print symmetry matrices in pure text format.")
        add('--x', type=float, default=0.0, help="X coordinate for symmetry center in Angstroms (Default: 0.0).")
        add('--y', type=float, default=0.0, help="Y coordinate for symmetry center in Angstroms (Default: 0.0).")
        add('--z', type=float, default=0.0, help="Z coordinate for symmetry center in Angstroms (Default: 0.0).")

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if args.sym == "":
            self.error("Please specify the symmetry type (--sym).")

        self.args = args

    def mprint(self, message):
        # muted print if the output is STDOUT
        if self.args.o != "STDOUT":
            print(message)

    def matrixToBiomt(self, matrix, serial):
        # serial is the matrix number (1-based)
        lines = []
        for i in range(3):
            line = (
                f"REMARK 350   BIOMT{i + 1} "
                f"{serial:>3} "
                f"{matrix[i][0]:9.6f}{matrix[i][1]:10.6f}{matrix[i][2]:10.6f}"
                f"{matrix[i][3]:15.5f}"
            )
            lines.append(line)
        return "\n".join(lines)

    def matricesToBiomt(self, matrices):
        return "\n".join(self.matrixToBiomt(matrix, idx + 1) for idx, matrix in enumerate(matrices))

    def matrixToMtrix(self, matrix, serial):
        # serial is the matrix number (1-based)
        lines = []
        for i in range(3):
            line = (
                f"MTRIX{i + 1:<1}  {serial:2d} "
                f"{matrix[i][0]:9.6f}{matrix[i][1]:10.6f}{matrix[i][2]:10.6f}"
                f"{matrix[i][3]:15.5f}"
            )
            lines.append(line)
        return "\n".join(lines)

    def matricesToMtrix(self, matrices):
        return "\n".join(self.matrixToMtrix(matrix, idx + 1) for idx, matrix in enumerate(matrices))

    def matrixToText(self, matrix, serial):
        return f"Matrix: {serial}\n" \
               f"{matrix[0][0]:10.6f} {matrix[0][1]:10.6f} {matrix[0][2]:10.6f} {matrix[0][3]:12.6f}\n" \
               f"{matrix[1][0]:10.6f} {matrix[1][1]:10.6f} {matrix[1][2]:10.6f} {matrix[1][3]:12.6f}\n" \
               f"{matrix[2][0]:10.6f} {matrix[2][1]:10.6f} {matrix[2][2]:10.6f} {matrix[2][3]:12.6f}"

    def matricesToText(self, matrices):
        return "\n".join(self.matrixToText(matrix, idx + 1) for idx, matrix in enumerate(matrices))

    def apply_translation(self, matrices, x, y, z):
        center = np.array([x, y, z])
        translated = []
        for m in matrices:
            R = np.array([row[:3] for row in m])
            I = np.identity(3)
            t = (I - R) @ center
            new_matrix = [
                [m[0][0], m[0][1], m[0][2], t[0]],
                [m[1][0], m[1][1], m[1][2], t[1]],
                [m[2][0], m[2][1], m[2][2], t[2]],
            ]
            translated.append(new_matrix)
        return translated

    def main(self):
        self.define_parser()
        args = self.parser.parse_args()
        self.validate(args)

        sym = Symmetry(args.sym)
        sym_matrices = self.apply_translation(sym.sym_matrices, args.x, args.y, args.z)

        if args.o == "STDOUT":
            if args.biomt:
                print(self.matricesToBiomt(sym_matrices))
            elif args.mtrix:
                print(self.matricesToMtrix(sym_matrices))
            elif args.text:
                print(self.matricesToText(sym_matrices))
        else:
            with open(args.o, 'w') as f:
                if args.biomt:
                    f.write(self.matricesToBiomt(sym_matrices))
                elif args.mtrix:
                    f.write(self.matricesToMtrix(sym_matrices))
                elif args.text:
                    f.write(self.matricesToText(sym_matrices))


if __name__ == "__main__":
    printSymMatrices().main()
