"""
I/O for SU2 format, cf.
<https://su2code.github.io/docs_v7/Mesh-File/>.
"""
import numpy

from ..__about__ import __version__ as version
from .._common import num_nodes_per_cell
from .._exceptions import ReadError, WriteError
from .._files import open_file
from .._helpers import register
from .._mesh import CellBlock, Mesh

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
    cell_sets = {}

    while True:
        line = f.readline().strip()

        if line.startswith("NDIME"):
            num_dims = _read_param(line)
        elif line.startswith("NPOIN"):
            num_nodes = _read_param(line)
            points = _read_nodes(f, num_nodes, num_dims)
        elif line.startswith("NELEM"):
            num_cells = _read_param(line)
            cells = _read_cells(f, num_cells)
        elif line.startswith("NMARK"):
            num_sets = _read_param(line)
            cells_, cell_sets_ = _read_sets(f, num_sets)
            for k, v in cell_sets_.items():
                cell_sets[k] = [numpy.arange(0) for _ in range(len(cells))]
                cell_sets[k] += v
            cells += cells_
        elif not line:
            break

    return Mesh(
        points=numpy.array(points),
        cells=[(cell_type, numpy.array(data)) for cell_type, data in cells],
        cell_sets=cell_sets,
    )


def _read_param(line, dtype=int):
    return dtype(line.split("=")[1])


def _read_nodes(f, num_nodes, num_dims):
    points = []
    for _ in range(num_nodes):
        line = f.readline().strip().split()
        points.append([float(x) for x in line[:num_dims]])
    return points


def _read_cells(f, num_cells):
    cells = []
    for _ in range(num_cells):
        line = f.readline().strip().split()
        cell_type = su2_to_meshio_type[int(line[0])]
        cell = [int(x) for x in line[1:num_nodes_per_cell[cell_type] + 1]]
        if len(cells) > 0 and cells[-1].type == cell_type:
            cells[-1].data.append(cell)
        else:
            cells.append(CellBlock(cell_type, [cell]))
    return cells


def _read_sets(f, num_sets):
    cells, cell_sets = [], {}
    for i in range(num_sets):
        tag = _read_param(f.readline().strip(), str).strip()
        cell_sets[tag] = [numpy.arange(0) for _ in range(num_sets)]
        
        num_cells = _read_param(f.readline().strip())
        cells += _read_cells(f, num_cells)
        cell_sets[tag][i] = numpy.arange(num_cells)
    return cells, cell_sets


def write(filename):
    with open_file(filename, "w") as f:
        pass


register("su2", [".su2"], read, {"su2": write})
