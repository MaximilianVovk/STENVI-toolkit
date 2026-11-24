"""
Write STENVI (.sei) lines in the fixed-column layout of a MASTER-produced file
(e.g. master_mtbg.sei), which is what the reading software expects:

    MODNAME   IMEM2 v1.0
    MISSBEGIN  2027   01   01   12     00   00          Begin [yyyy mm dd hh  mm ss]
    INCLIN          51.6                    Orbit inclination [deg]
    AZIMUTH      72   -180.0     180.0     Azimuth   [deg]
    DISTAZI       1     -0.180E+03     -0.175E+03
    DISTSET       1    1    2    1    1    1    0.14404E+01

Fortran-style 0.dddE+xx numbers, CRLF line endings (open files with NEWLINE),
separator lines always commented. normalize_header() re-formats header lines
from any source; write_distset() writes the flux rows. The two known flux-note
comments are removed for reader compatibility. This does not convert flux units.

Run as a script to re-format an existing file:
    python sei_formatfix.py --sei IN.sei [-o OUT.sei]

The input is preserved; output defaults to IN_fmt.sei.
"""
import argparse
import math
import os

import numpy as np

NEWLINE = "\r\n"  # pass as open(path, "w", newline=NEWLINE)

SPECTRUM = {  # spectrum card: label
    "AZIMUTH": "Azimuth   [deg]",
    "ELEVATION": "Elevation [deg]",
    "VELOCITY": "Velocity  [km/s]",
    "DIAMETER": "Diameter  [m]",
    "LATITUDE": "Argument of True Latitude [deg]",
    "DENSITY": "Density   [g/cm^3]",
}
ORBIT = {  # orbit card: label
    "SEMIAXIS": "Semimajor axis [km]",
    "ECCENTRI": "Eccentricity of the orbit [-]",
    "INCLIN": "Orbit inclination [deg]",
    "RAAN": "Right ascension of ascending node [deg]",
    "ARGPERI": "Argument of perigee [deg]",
}
MISSION = {"MISSBEGIN": "Begin [yyyy mm dd hh  mm ss]", "MISSEND": "End [yyyy mm dd hh  mm ss]"}
DISTS = ("DISTAZI", "DISTELE", "DISTVEL", "DISTDIA", "DISTLAT", "DISTDEN")
COLUMN_COMMENTS = {  # whitespace-normalised comment -> aligned version
    "# Bin Min Max": "#           Bin       Min       Max",
    "# No Lower Border Upper Border": "#            No   Lower Border   Upper Border",
    "# Azi Ele Vel Dia Lat Den Flux": "#           Azi  Ele  Vel  Dia  Lat  Den           Flux",
    "# STANDARD ENVIRONMENT INTERFACE": "#                       STANDARD ENVIRONMENT INTERFACE",
}
REMOVED_COMMENTS = {
    "# Flux is the total flux in each bin.",
    "# CAUTION! Non-standard units [1/m^2/year]",
}


def fe(x, digits):
    """Fortran E format: 0.dddE+xx with `digits` significant digits."""
    if x == 0:
        return f"0.{'0' * digits}E+00"
    mant, exp = f"{abs(x):.{digits - 1}E}".split("E")
    return f"{'-' if x < 0 else ''}0.{mant.replace('.', '')}E{int(exp) + 1:+03d}"


def mission_line(card, nums):
    """MISSBEGIN / MISSEND from [yyyy, mm, dd, hh, mm, ss] or a datetime."""
    if not isinstance(nums, (list, tuple)):
        nums = [nums.year, nums.month, nums.day, nums.hour, nums.minute, nums.second]
    nums = list(nums) + [0] * (6 - len(nums))  # missing minutes/seconds -> 00
    y, mo, d, h, mi, s = (f"{x:02d}" for x in nums)
    return f"{card:<9}{y:>6}{mo:>5}{d:>5}{h:>5}{mi:>7}{s:>5}          {MISSION[card]}"


def orbit_line(card, value):
    if not math.isfinite(value):  # e.g. argument of perigee of a circular/equatorial orbit
        print(f"warning: {card} = {value}, written as 0.0")
        value = 0.0
    v = fe(value, 1) if card == "ECCENTRI" else f"{value:.1f}"
    return f"{card:<8}{v:>12}{'':20}{ORBIT[card]}"


def spectrum_line(card, n, lo, hi):
    f = (lambda x: fe(x, 1)) if card == "DIAMETER" else (lambda x: f"{x:.1f}")
    return f"{card:<9}{n:>6}{f(lo):>10}{f(hi):>10}     {SPECTRUM[card]}"


def interval_line(card, n, lo, hi):
    return f"{card:<7}{n:>8}{fe(lo, 3):>15}{fe(hi, 3):>15}"


def distset_line(idx, flux):
    return "DISTSET" + f"{idx[0]:>8}" + "".join(f"{i:>5}" for i in idx[1:]) + f"{fe(flux, 5):>15}"


def normalize_line(line, prev=""):
    """Format one line; return None for a known comment that must be omitted."""
    line = line.rstrip()
    tok = line.split()
    if not tok:
        return "#"
    if tok[0].startswith("#"):
        # Accept indentation, tabs, repeated spaces, and an omitted space after #.
        comment = "# " + " ".join(line.lstrip()[1:].split())
        if comment in REMOVED_COMMENTS:
            return None
        return COLUMN_COMMENTS.get(" ".join(tok), line)
    if tok[0].startswith("-"):  # uncommented separator / EOF marker
        return "#" + line.strip()
    key = tok[0].upper()
    if key == "DISTSET":
        return distset_line([int(t) for t in tok[1:7]], float(tok[7]))
    if key in DISTS:
        return interval_line(key, int(tok[1]), float(tok[2]), float(tok[3]))
    if key in SPECTRUM:
        return spectrum_line(key, int(tok[1]), float(tok[2]), float(tok[3]))
    if key in ORBIT:
        return orbit_line(key, float(tok[1]))
    if key in MISSION:
        return mission_line(key, [int(t) for t in tok[1:7] if t.isdigit()])
    if key == "STENVI":
        return f"STENVI      {tok[1]}"
    if key == "COMMENT":
        return f"COMMENT   {line.split(None, 1)[1] if len(tok) > 1 else ''}"
    if key == "MODNAME":
        return f"MODNAME   {line.split(None, 1)[1]}"
    if prev.startswith("# Environment Model"):  # model name written without its MODNAME card
        return f"MODNAME   {line.strip()}"
    raise ValueError(f"unknown .sei card: {line!r}")


def normalize_header(lines):
    """Normalize lines and omit known incompatible flux-note comments."""
    out = []
    for l in lines:
        normalized = normalize_line(l, out[-1] if out else "")
        if normalized is not None:
            out.append(normalized)
    return out


def write_distset(fh, idx, flux):
    """Write DISTSET rows: idx [n, 6] 1-based bin indices, flux [n] (>= 0)."""
    flux = np.asarray(flux, float)
    exp = np.where(flux > 0, np.floor(np.log10(np.where(flux > 0, flux, 1.0))) + 1, 0).astype(int)
    mant = np.rint(flux / 10.0 ** exp * 1e5).astype(np.int64)
    over = mant >= 100000  # rounded up to 1.0 -> 0.10000E(exp+1)
    mant[over] //= 10
    exp[over] += 1
    np.savetxt(fh, np.column_stack([np.asarray(idx, np.int64), mant, exp]),
               fmt="DISTSET%8d%5d%5d%5d%5d%5d    0.%05dE%+03d", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sei", required=True, help="input .sei file")
    ap.add_argument("-o", "--output", help="output file (default: <input>_fmt.sei)")
    a = ap.parse_args()
    out = a.output or f"{os.path.splitext(a.sei)[0]}_fmt.sei"
    if os.path.exists(out) and os.path.samefile(a.sei, out):
        raise SystemExit("Input and output must be different files.")
    prev = ""
    removed = 0
    with open(a.sei) as fin, open(out, "w", newline=NEWLINE) as fout:
        for line in fin:
            normalized = normalize_line(line, prev)
            if normalized is None:
                removed += 1
                continue
            prev = normalized
            fout.write(prev + "\n")
    print(f"Wrote {out}")
    if removed:
        print(f"Removed {removed} flux-note comment line(s); flux units are unchanged.")


if __name__ == "__main__":
    main()
