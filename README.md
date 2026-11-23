# STENVI-toolkit
A Python toolkit for visualizing and processing STENVI particle environments, with tools for flux queries, directional selection, particle sampling, angular rebinning, and reference-frame conversion.

## Purpose

Provide a reusable Python interface for working with STENVI environment files. The planned toolkit will evaluate flux over user-defined particle-property ranges and arrival directions, generate representative particle samples, and convert distributions between angular grids and reference frames.

The aim is to make different applications use the same documented interpretation of the environment data. ATHENA micropore and detector studies are one intended application.

| Path | Responsibility |
| --- | --- |
| `README.md` | Purpose, current capabilities, examples, and roadmap |
| `pyproject.toml` | Package metadata and dependencies |
| `src/stenvi_toolkit/io.py` | STENVI reading, validation, and writing |
| `src/stenvi_toolkit/environment.py` | Shared data model, dimensions, units, and metadata |
| `src/stenvi_toolkit/plotting.py` | Existing plots and future visualization helpers |
| `src/stenvi_toolkit/zero_mass.py` | Existing zero-mass functionality; rename if a more precise term is appropriate |
| `src/stenvi_toolkit/flux.py` | Differential representation, interpolation, and integration |
| `src/stenvi_toolkit/selection.py` | Particle-property limits and directional masks |
| `src/stenvi_toolkit/sampling.py` | Weighted particle and aperture sampling |
| `src/stenvi_toolkit/grids.py` | Angular geometry, solid angles, and rebinning |
| `src/stenvi_toolkit/frames.py` | Matrix-based direction transformations and rotated rebinning |
| `src/stenvi_toolkit/spice.py` | Optional later SPICE integration |
| `examples/` | Small reproducible workflows, including a future ATHENA interface example |
| `tests/` | Numerical checks and small synthetic fixtures |
| `docs/conventions.md` | File semantics, units, directions, frames, and numerical assumptions |
