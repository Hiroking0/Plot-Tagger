import json

import h5py as h5
import pandas as pd
import numpy as np 
import sys, os 
from datetime import datetime
from importlib import reload  
from scipy.constants import Planck, elementary_charge 
import tkinter as tk 
from tkinter.filedialog import askopenfilename  
import matplotlib.pyplot as plt
import pandas as pd
import uuid
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from pathlib import Path
import time
import h5py
import _warnings as warnings

COLNAMEATTR = '_colnames'
COLTYPEATTR = '_coltypes'

def saveH5Table(f, path, dframe):
    """Save a DataFrame in an HDF5 file.

    Store column names and dtypes in special meta-attributes for loading with
    `loadH5Table()`.

    Inputs
    ------
    f : h5py.File
    path : str
      HDF5 path to dataset.
    dframe : pandas.DataFrame-like
      Table to be saved in HDF5 file.

    """
    f.create_dataset(
        path,
        data=np.asarray(dframe.values, dtype=np.bytes_),
        dtype=h5.special_dtype(vlen=str)
    )
    f[path].attrs[COLNAMEATTR] = json.dumps(dframe.columns.tolist())
    f[path].attrs[COLTYPEATTR] = json.dumps(
        [t.str for t in dframe.dtypes.tolist()]
    )

def loadH5Table(f, path):
    """Load a DataFrame from an HDF5 file.

    Loads DataFrame contents, column names, and data types according to
    format used by `saveH5Table()`. Raises an error if column names cannot be
    found, and warns if type coercion cannot be performed.

    Inputs
    ------
    f : Connection to HDF5 file.
    path : str
      HDF5 path to dataset.

    Returns
    -------
    pandas.DataFrame with contents, column names, and dtypes from `f[path]`.
    """
    if COLNAMEATTR not in f[path].attrs.keys():
        raise AttributeError(
            'Missing column name attribute `{}`. Was this dataset '
            'saved using `saveH5Table()`?'.format(COLNAMEATTR)
        )
    colnames = json.loads(f[path].attrs[COLNAMEATTR])
    dframe = pd.DataFrame(f[path][()], columns = colnames)

    # Convert types if possible.
    if COLTYPEATTR not in f[path].attrs.keys():
        warnings.warn(
            'Could not find column type attribute `{}`. '
            'Skipping type coercion.'.format(COLTYPEATTR)
        )
    else:
        coltypes = json.loads(f[path].attrs[COLTYPEATTR])
        try:
            dframe = dframe.astype(
                {cn: np.dtype(ct) for cn, ct in zip(colnames, coltypes)}
            )
        except:
            warnings.warn('Type coercion failed. Skipping.')

    return dframe


def generate_and_store_unique_id_in_hdf(original_file_path):
    """
    Generates a unique ID for a plot and stores it in an HDF5 file with metadata.

    The function creates a unique ID and stores it in an HDF5 file with metadata.
    If another figure is made with the same data, it updates the old entry's `Status` column to `Replaced`.
    
    Parameters:
    -----------
    original_file_path : str
        The full path to the original data file (e.g., HDF5 file).

    Returns:
    --------
    str
        The generated unique ID.
    """
    # Get the current date and time
    current_time = datetime.now()
    # Get the creation time (on most platforms; falls back to modification time on Unix-like systems)
    creation_time = os.path.getctime(original_file_path)

    # Convert the timestamps to readable formats    
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    creation_time_str = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
    
    # Get current path
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Define the HDF5 file path
    hdf5_file_path = os.path.join(current_path,'tag_data.h5')
    
    path = 'dataset'
    # Initialize new UUID
    if os.path.exists(hdf5_file_path):
        # Open existing HDF5 file
        with h5py.File(hdf5_file_path, 'r+') as f:

            # Load existing data
            df = loadH5Table(f,path).applymap(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
            if not df.empty:
                last_uuid_str = df.iloc[-1]["Unique ID"]
                last_uuid = uuid.UUID(last_uuid_str)
                unique_id = uuid.UUID(int=last_uuid.int + 1)
            else:
                unique_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
    else:
        unique_id = uuid.UUID('00000000-0000-0000-0000-000000000000')

    # Extract metadata
    original_filename = os.path.basename(original_file_path)
    if os.path.isdir(original_file_path):
        original_filename = "Folder"
    
    # Check if the HDF5 file exists and create a DataFrame with metadata
    if os.path.exists(hdf5_file_path):
        with h5py.File(hdf5_file_path, 'r') as f:
            # Read the existing dataset
            df = loadH5Table(f,path).applymap(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    else:
        # Create a new DataFrame if no HDF5 file exists
        df = pd.DataFrame(columns=["Status", "Unique ID", "Original File Path", "Filename", "Data Taken", "Date Plot"])

    # Check if the file path already exists
    existing_entry_indices = df[df["Original File Path"] == original_file_path].index.tolist()
    if existing_entry_indices:
        df.loc[existing_entry_indices, "Status"] = "Replaced"
        status = "New"
    else:
        status = "New"
    
    # Append the new entry
    new_entry = {
        "Status": status,
        "Unique ID": str(unique_id),
        "Original File Path": original_file_path,
        "Filename": original_filename,
        "Data Taken": creation_time_str,
        "Date Plot": current_time_str
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    

    # Save the DataFrame to the HDF5 file
    with h5py.File(hdf5_file_path, 'w') as f:
        # Store the DataFrame as a dataset in the HDF5 file
        saveH5Table(f, path = path, dframe = df)
    
    return str(unique_id)


