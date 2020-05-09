"""
I/O for SU2 format, cf.
<https://su2code.github.io/docs_v7/Mesh-File/>.
"""
import numpy

from ..__about__ import __version__ as version
from .._exceptions import ReadError, WriteError
from .._files import open_file
from .._helpers import register
from .._mesh import Mesh

meshio_to_su2_type = {
    "line": 3,
    "triangle": 5,
    "quad": 9,
    "tetra": 10,
    "pyramid": 14,
    "wedge": 13,
    "hexahedron": 12,
}
su2_to_meshio_type = {v: k for k, v in meshio_to_su2_type.items()}


def read(filename):
    with open_file(filename, "r") as f:
        out = read_buffer(f)
    return out


def read_buffer(f):
    points = []
    cells = []

    return Mesh(points, cells)


def write(filename):
    with open_file(filename, "w") as f:
        pass


register("su2", [".su2"], read, {"su2": write})
