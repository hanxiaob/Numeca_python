#                                                                             #
#                          MARINE Module                                      #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	      : 23/05/2012
#______________________________________________________________________________
#
# Description: Marine module for CFView
#______________________________________________________________________________

#!/bin/python
# Imports
import os.path
import sys

# Detect the installation path
cfviewpath = os.path.dirname(sys.argv[0])

if sys.platform=='win32':
	numecaDir = os.path.dirname(cfviewpath)
else:
	numecaDirTemp = os.path.dirname(cfviewpath)
	numecaDir = os.path.dirname(numecaDirTemp)

# Append MarineModule_lib to the path 
sys.path.append( os.path.join( numecaDir, '_python', '_fine', '_marine', '_MarineModule_lib' ) )

# Import all plugins
from group import Group_patches_by_type
from represent_fs import Represent_free_surface
from compute_wetted_area import Compute_wetted_area
from represent_water_line import Represent_water_line
from plot_wave_elevation import Plot_wave_elevation_along_X
from streamlines_upright import Streamlines_to_upright_position
from wake_flow import Wake_flow_tool
from forces_by_section import Forces_by_section
from camera_rotation_for_animation import Camera_rotation_for_animation
from display_computation_info import Display_computation_info
from represent_towing_tank_lines import Represent_towing_tank_lines
from relative_wave_height import Relative_wave_height
from customized_planes import Customized_planes