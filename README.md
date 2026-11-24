# STENVI-toolkit
A Python toolkit for visualizing and processing STENVI particle environments, with tools for flux queries, directional selection, particle sampling, angular rebinning, and reference-frame conversion.

## Purpose

Provide a reusable Python interface for working with STENVI environment files. The planned toolkit will evaluate flux over user-defined particle-property ranges and arrival directions, generate representative particle samples, and convert distributions between angular grids and reference frames.

The aim is to make different applications use the same documented interpretation of the environment data. ATHENA micropore and detector studies are one intended application. The current tools are written for and tested on IMEM2 `.sei` files.

## STENVI file format

The STENVI (Standard Environment Interface) `.sei` file format is defined in the IADC document included in this repository: [IADC-23-03 Standard Environment Interface (STENVI), Rev. 1.0](<IADC-23-03_Standard_Environment_Interface(STENVI)_Rev.1.0.pdf>). It explains what a STENVI file is, the header cards, bin definitions, `DISTSET` flux rows and their conventions. Refer to it when reading or writing `.sei` files with this toolkit.

## Current tools

Requires Python >= 3.9, NumPy and Matplotlib:

```
python -m pip install numpy matplotlib
```

Each module runs as a script from inside `stenvi_toolkit/`, or as `python -m stenvi_toolkit.<module>` from the repository root. Run any of them with `-h` for the full option list.

### `sei_formatfix.py`: fix the format of `.sei` files

Corrects the layout of a STENVI file and fixes common formatting errors that stop `.sei` files from being read correctly. Each line is rewritten in the fixed-column layout that the STENVI reading software expects:

- Header cards (`MODNAME`, `MISSBEGIN`/`MISSEND`, orbit, spectrum, `DIST*` intervals) and `DISTSET` flux rows are realigned to fixed columns.
- Numbers are written in Fortran-style `0.dddE+xx` notation.
- Line endings are set to CRLF.
- Uncommented separator or end-of-file lines (starting with `-`) are commented out.
- A model name written without its `MODNAME` card is given the card again.
- Missing minutes/seconds in mission dates are padded with `00`.
- Column-header comments are realigned, and two known flux-note comments that break the reader (`# Flux is the total flux in each bin.` and `# CAUTION! Non-standard units [1/m^2/year]`) are removed.

Flux values and units are not converted; only the formatting changes. The input file is left unchanged.

```
python sei_formatfix.py --sei IN.sei            # writes IN_fmt.sei
python sei_formatfix.py --sei IN.sei -o OUT.sei
```

The module also provides helpers for writing `.sei` files from other code: `normalize_header()` for header lines and `write_distset()` for flux rows.

### `zero_mass.py`: remove small-mass and zero-flux rows

Drops `DISTSET` rows whose diameter/density bin gives a spherical particle mass (m = ρ·π/6·d³) below a threshold, together with rows of zero flux. The output is written in the `sei_formatfix` layout. Large files are processed one line at a time.

```
python zero_mass.py --sei IN.sei                         # threshold 1e-6 g -> IN_mgt1e-06.sei
python zero_mass.py --sei IN.sei -m 1e-5 --mode lower -o OUT.sei
```

`--mode` chooses which value of each diameter/density bin is compared to the threshold: `center` (default), `lower` or `upper`.

### `plotting.py`: Aitoff sky maps

Plots the flux-weighted mean velocity and density (and diameter, with `--show-diameter`) in each azimuth/elevation bin on Aitoff maps, one figure per latitude bin. `--density-cuts` adds flux and mean-velocity maps per density class. `--confront OTHER.sei` compares the flux with a second file, re-binned onto the same angular grid.

```
python plotting.py IN.sei
python plotting.py path/to/folder --recursive -o plots
python plotting.py IN.sei --confront OTHER.sei
```

## Repository organization

| Path | Responsibility |
| --- | --- |
| `README.md` | Purpose, current capabilities, examples, and roadmap |
| `IADC-23-03_Standard_Environment_Interface(STENVI)_Rev.1.0.pdf` | IADC specification of the STENVI `.sei` file format |
| `stenvi_toolkit/sei_formatfix.py` | Corrects `.sei` formatting and fixes common format/read errors (existing) |
| `stenvi_toolkit/plotting.py` | Existing plots and future visualization helpers |
| `stenvi_toolkit/zero_mass.py` | Existing zero-mass functionality; rename if a more precise term is appropriate |
| `pyproject.toml` | Package metadata and dependencies (planned) |
| `stenvi_toolkit/io.py` | STENVI reading, validation, and writing (planned) |
| `stenvi_toolkit/environment.py` | Shared data model, dimensions, units, and metadata (planned) |
| `stenvi_toolkit/flux.py` | Differential representation, interpolation, and integration (planned) |
| `stenvi_toolkit/selection.py` | Particle-property limits and directional masks (planned) |
| `stenvi_toolkit/sampling.py` | Weighted particle and aperture sampling (planned) |
| `stenvi_toolkit/grids.py` | Angular geometry, solid angles, and rebinning (planned) |
| `stenvi_toolkit/frames.py` | Matrix-based direction transformations and rotated rebinning (planned) |
| `stenvi_toolkit/spice.py` | Optional later SPICE integration (planned) |
| `examples/` | Small reproducible workflows, including a future ATHENA interface example (planned) |
| `tests/` | Numerical checks and small synthetic fixtures (planned) |
| `docs/conventions.md` | File semantics, units, directions, frames, and numerical assumptions (planned) |
