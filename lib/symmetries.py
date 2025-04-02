import copy

import numpy as np
from math import pi, sin, cos, radians, degrees
from .matrix3 import matrix_from_euler_np
from .euler import euler_from_matrix_np

class Symmetry():
    def __init__(self, groupName):
        self.group = str.upper(groupName)
        self.sym_matrices = []
        self.rot_sym_ops = []

        # now, lets build our sym operations and sym matrices
        self._groupName_to_operations()
        self._rot_sym_ops_to_matrix()

    def print_symmetry_matrices(self):
        """ Print the symmetry matrices in a formatted way. """
        print(f"Symmetry group: {self.group}")
        print(f"Order: {self.order}")
        print("Symmetry matrices:")
        for i, matrix in enumerate(self.sym_matrices):
            print(f"R({i + 1})=")
            formatted_matrix = np.array(matrix).round(4)
            for row in formatted_matrix:
                print("  {:8.4f} {:8.4f} {:8.4f}".format(*row))
            print()  # Add empty line between matrices

    def sym_expand_particle(self, particle):
        """Apply symmetry operations to a particle and return the transformed particles."""
        particle_rot_matrix = matrix_from_euler_np(
                radians(particle.rlnAngleRot),
                radians(particle.rlnAngleTilt),
                radians(particle.rlnAnglePsi)
            )

        # Prepare memory for sym_particles with exact size to avoid resizing
        sym_particles = [None] * len(self.sym_matrices)

        # Use enumeration to avoid append operations
        for i, matrix in enumerate(self.sym_matrices):
            particle_sym_copy = copy.copy(particle)

            symcopy_matrix = np.matmul(particle_rot_matrix, matrix)

            rot, tilt, psi = euler_from_matrix_np(symcopy_matrix)

            particle_sym_copy.rlnAngleRot = degrees(rot)
            particle_sym_copy.rlnAngleTilt = degrees(tilt)
            particle_sym_copy.rlnAnglePsi = degrees(psi)

            sym_particles[i] = particle_sym_copy

        return sym_particles

    def sym_expand_particles(self, particles):
        """Apply symmetry operations to a list of particles and return the transformed particles."""
        sym_particles = []
        for particle in particles:
            transformed_particles = self.sym_expand_particle(particle)
            sym_particles.extend(transformed_particles)
        return sym_particles

    def _validate_groupName(self):
        # Check if the name is in the format C<number>, D<number>, I<number>, T, O
        if not (self.group.startswith(("C", "D", "I", "T", "O")) and len(self.group) > 0):
            raise ValueError(f"Invalid symmetry name: {self.group}. Expected format: C<number>, D<number>, I<number>, T, O")

        if self.group.startswith(("C", "D")) and not (len(self.group) > 1 and self.group[1:].isdigit()):
            raise ValueError(f"Invalid symmetry name: {self.group}. Expected format: C<number>, D<number>")

        if self.group.startswith(("I")) and not self.group[1:].isdigit() and int(self.group[1:]) not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid symmetry name: {self.group}. Expected format: I1, I2, I3, I4")


    def _groupName_to_operations(self):
        """" Convert symmetry group name to symmetry operations. """
        self._validate_groupName()

        if not(self.group.startswith("O") or self.group.startswith("T")):
            self.order = int(self.group[1:])
        else:
            self.order = 1

        if self.group.startswith("C"):
            self.group = "C"
            self.rot_sym_ops.append("rot_axis " + str(self.order) + " 0 0 1")
        elif self.group.startswith("D"):
            self.group = "D"
            self.rot_sym_ops.append("rot_axis " + str(self.order) + " 0 0 1")
            self.rot_sym_ops.append("rot_axis 2 1 0 0")
        elif self.group.startswith("T"):
            self.group = "T"
            self.rot_sym_ops.append("rot_axis 3  0. 0. 1.")
            self.rot_sym_ops.append("rot_axis 2 0. 0.816496 0.577350")
        elif self.group.startswith("O"):
            self.group = "O"
            self.rot_sym_ops.append("rot_axis 3  0.5773502 0.5773502 0.5773502")
            self.rot_sym_ops.append("rot_axis 4 0 0 1")
        elif self.group.startswith("I"):
            self.group = "I"
            if self.order == 1:
                self.rot_sym_ops.append("rot_axis 2  1 0 0")
                self.rot_sym_ops.append("rot_axis 5 0.85065080702670 0 -0.5257311142635")
                self.rot_sym_ops.append("rot_axis 3 0.9341723640 0.3568220765 0")
            elif self.order == 2:
                self.rot_sym_ops.append("rot_axis 2  0 0 1")
                self.rot_sym_ops.append("rot_axis 5  0.525731114  0 0.850650807")
                self.rot_sym_ops.append("rot_axis 3  0 0.356822076 0.934172364")
            elif self.order == 3:
                self.rot_sym_ops.append("rot_axis 2  -0.5257311143 0 0.8506508070")
                self.rot_sym_ops.append("rot_axis 5  0 0 1")
                self.rot_sym_ops.append("rot_axis 3  -0.4911234778630044 0.3568220764705179 0.7946544753759428")
            elif self.order == 4:
                self.rot_sym_ops.append("rot_axis 2  0.5257311143 0 0.8506508070")
                self.rot_sym_ops.append("rot_axis 5  0.8944271932547096 0 0.4472135909903704")
                self.rot_sym_ops.append("rot_axis 3  0.4911234778630044 0.3568220764705179 0.7946544753759428")
            else:
                raise ValueError(f"Invalid order for I symmetry: {self.order}. Expected 1, 2, 3, or 4.")
        else:
            raise ValueError(f"Invalid symmetry name: {self.group}. Expected format: C<number>, D<number>, I<number>, T, O")

    def _rot_sym_ops_to_matrix(self):
        """ Convert rotation symmetry operations to matrices. """
        def axis_angle_to_matrix(axis, angle):
            """Convert an axis and angle to a rotation matrix using Rodriguez formula."""
            x, y, z = axis
            # Cross-product matrix
            K = np.array([
                [0, -z, y],
                [z, 0, -x],
                [-y, x, 0]
            ])
            # Rodriguez rotation formula
            R = np.identity(3) + sin(angle) * K + (1 - cos(angle)) * np.matmul(K, K)
            return clean_small_values(R)

        def clean_small_values(matrix, threshold=1e-12):
            """Set values that are very close to zero to exactly zero."""
            matrix = matrix.copy()
            matrix[np.abs(matrix) < threshold] = 0.0
            return matrix

        def generate_sym_group_matrices(generators):
            """Generate all matrices in the symmetry group from its generators using robust comparison."""
            matrices = [np.identity(3)]  # Start with identity matrix
            queue = [np.identity(3)]

            # Use matrix hashing for more reliable comparison
            def matrix_key(matrix, precision=5):
                """Convert matrix to a hashable representation with fixed precision."""
                return tuple(tuple(np.round(row, precision)) for row in matrix)

            # Track matrices we've already seen using their hash keys
            seen_matrices = {matrix_key(np.identity(3))}

            while queue:
                current = queue.pop(0)
                for gen in generators:
                    # Multiply current matrix by generator
                    new_matrix = clean_small_values(np.matmul(current, gen))

                    # Get hashable key for the new matrix
                    key = matrix_key(new_matrix)

                    # Check if we've seen this matrix before
                    if key not in seen_matrices:
                        matrices.append(new_matrix)
                        queue.append(new_matrix)
                        seen_matrices.add(key)

            self.sym_matrices = matrices

        rotation_generators = []
        for op in self.rot_sym_ops:
            parts = op.split()
            if len(parts) == 5:
                axis = [float(parts[2]), float(parts[3]), float(parts[4])]
                order = int(parts[1])
                angle = 2 * pi / order
                rotation_generators.append(axis_angle_to_matrix(axis, angle))

        # To generate the full symmetry group matrices, you would need to compute all possible products of these generators
        generate_sym_group_matrices(rotation_generators)
