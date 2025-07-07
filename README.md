# HDF5 Tag Manager

A lightweight utility for tracking data files and the figures generated from them.
It assigns every plot a **stable UUID**, stores rich metadata in an **HDF5** table, and lets you export the log to **Excel** with colour‑coded status markers.

---

## Table of contents

1. [Overview](#overview)
2. [Quick start](#quick-start)
3. [Project layout](#project-layout)
4. [API reference](#api-reference)
5. [Command‑line tools](#command-line-tools)
6. [Data schema](#data-schema)
7. [Installation](#installation)
8. [Contributing](#contributing)
9. [Licence](#licence)

---

## Overview <a name="overview"></a>

`hdf5_handle.py` keeps a single HDF5 file—`tag_data.h5`—containing a table called **/dataset**.
Each row records:

* a unique identifier (`Unique ID`)
* where the raw data live (`Original File Path` and `Filename`)
* when the data were taken
* when the figure was made
* a `Status` flag (`New` | `Replaced`)

When you re‑plot the *same* data the old entry is marked *Replaced* and a fresh UUID is issued.
`view_hdf.py` converts the log to an Excel workbook (`tag_data.xlsx`) and highlights rows so new or superseded items jump out at a glance.

## Quick start <a name="quick-start"></a>

```bash
# Activate your environment first…
python -m pip install -r requirements.txt

# In your analysis script:
from hdf5_handle import generate_and_store_unique_id_in_hdf
uid = generate_and_store_unique_id_in_hdf(r"C:\path\to\my_data.h5")
print(f"This figure carries ID {uid}")
```

```bash
# To inspect the full log in Excel:
python view_hdf.py  # creates tag_data.xlsx next to the scripts
```

## Project layout <a name="project-layout"></a>

```
.
├── hdf5_handle.py   # core library
├── view_hdf.py      # Excel export helper
├── tag_data.h5      # auto‑generated metadata log
└── README.md        # you are here
```

## API reference <a name="api-reference"></a>

### `saveH5Table(f, path, df)`

Save a `pandas.DataFrame` as an HDF5 dataset and stash column names / dtypes in attributes so they round‑trip cleanly with `loadH5Table()`.

### `loadH5Table(f, path)`

Inverse of `saveH5Table()`.  Reconstructs the DataFrame with original column names and types.

### `generate_and_store_unique_id_in_hdf(original_file_path)`

1. Opens (or creates) `tag_data.h5`.
2. Issues the next UUID (monotonic increment).
3. Writes/updates a row in **/dataset** with metadata inferred from the path.
4. Returns the UUID as a string so you can embed it in filenames, figure captions, etc.

## Command‑line tools <a name="command-line-tools"></a>

### `view_hdf.py`

* Loads **/dataset** from `tag_data.h5`.
* Saves the table to `tag_data.xlsx` with row shading:

  * **Green** → `New`
  * **Grey** → `Replaced`

Open the spreadsheet in Excel or LibreOffice to filter, sort, and search.

## Data schema <a name="data-schema"></a>

| Column               | Type | Notes                                      |
| -------------------- | ---- | ------------------------------------------ |
| `Status`             | str  | `New` or `Replaced`                        |
| `Unique ID`          | str  | UUID4‑compatible identifier                |
| `Original File Path` | str  | Absolute or relative path to raw data      |
| `Filename`           | str  | Convenience cache of `os.path.basename`    |
| `Data Taken`         | str  | Timestamp (YYYY‑MM‑DD HH\:MM\:SS) of input |
| `Date Plot`          | str  | Timestamp of figure generation             |

## Installation <a name="installation"></a>

Python ≥ 3.8 recommended.

```bash
# clone your repo … then
python -m pip install h5py pandas numpy openpyxl tabulate matplotlib scipy
```

> **Tip:** if you work in Jupyter or VS Code, install *tk* (`pip install tk`) to enable the file‑picker in `generate_and_store_unique_id_in_hdf()`.

Alternatively, copy the exact versions in your lab environment into `requirements.txt` and `pip install -r requirements.txt`.

## Contributing <a name="contributing"></a>

Pull requests are welcome!  Please:

1. Ensure your code passes `flake8`.
2. Add/update docstrings and in‑line comments.
3. Bump the `README.md` where behaviour or dependencies change.

## Licence <a name="licence"></a>

Apache-2.0 © 2025 Hiroki Fujisato
