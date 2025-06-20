#
# Actions at the startup for Python sub-system
#

# pre-load modules for C-Wizard

import numpy
import scipy.optimize
import Tk

# setup .encpyc folders
import os.path
import encpyc, IGGSystem

numeca_dir = IGGSystem.get_numeca_dir_()
encpyc.add_encrypted_folder(os.path.join(numeca_dir, "_python", "_cwizard", "src"))
