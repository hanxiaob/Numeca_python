#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         M.P.                                                           Fev 2004            #
#--------------------------------------------------------------------------------------------#

import types
from Geom      import *
#from CADImport import *
from Parasolid import *
#from UHexaCommands import *
from UHexaProjectCommands import *
from UHexaMeshGenerationCommands import *
from UHexaMeshQualityAnalysisCommands import *
from UHexaMesh import *
from BodyManip import *
from STLCmdsForImport import *
from STLManip import *
#--------------------------------------------------------------------------------------------#

def get_parasolid_precision():
	return Para_get_precision_()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------STL Commands -----------------------------------------#
#--------------------------------------------------------------------------------------------#

def STL_import_domainSTL(filename):
	STL_import_domainSTL_(filename)

#--------------------------------------------------------------------------------------------#
def STL_create_domain(filename):
	STL_create_domain_(filename)

#--------------------------------------------------------------------------------------------#
def STL_feature_detection(tolerance, featureAngle, preview):
	STL_feature_detection_(tolerance, featureAngle, preview)

#--------------------------------------------------------------------------------------------#
def STL_merge_groups(strGroupFlags):
	STL_merge_groups_(strGroupFlags)

#--------------------------------------------------------------------------------------------#
def STL_split_group(goupID, X1, Y1, Z1, X2, Y2, Z2):
	STL_split_group_(goupID, X1, Y1, Z1, X2, Y2, Z2)

#--------------------------------------------------------------------------------------------#
def STL_rename_group(nbGroups, oldNames, newNames):
	STL_rename_group_(nbGroups, oldNames, newNames)

#--------------------------------------------------------------------------------------------#
def STL_reverse_orient(strGroupFlags):
	STL_reverse_orient_(strGroupFlags)

#--------------------------------------------------------------------------------------------#
#---------------------------------End of STL Commands ---------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def HEXA_generate_mesh():
	return HEXA_generate_mesh_()

def HEXA_regenerate_mesh():
	return HEXA_regenerate_mesh_()

def HEXA_mesh_quality_reporting():
	return HEXA_mesh_quality_reporting_()

#--------------------------------------------------------------------------------------------#
#---------------------------------IMPORT/EXPORT CGNS MESH-------------------------------------------#

def HXP_import_CGNS(fileName):
	return HXP_import_CGNS_(fileName)

def HXP_export_CGNS(fileName):
	return HXP_export_CGNS_(fileName)

#--------------------------------------------------------------------------------------------#
#---------------------------------IMPORT/EXPORT CGNS MESH-------------------------------------------#

def HXP_import_ANSYS(fileName):
	return HXP_import_ANSYS_(fileName)

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#

def get_bodies():
	bodies = []
	partitions = get_partitions()
	for p in partitions:
		for b in p.get_bodies():
			bodies.append(b)
	return bodies

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def check_bodies(*body_list):
    bodies = []
    extract_bodies_(body_list,bodies)

    return Para_check_bodies_(bodies)

#--------------------------------------------------------------------------------------------#

def sew_bodies(tol,*body_list):
    bodies = []
    extract_bodies_(body_list,bodies)

    sew_bodies_(tol,bodies)

#--------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
# Private functions


#--------------------------------------------------------------------------------------------#

cur_body_list_ = []

def update_body_list_():
    global cur_body_list_
    cur_body_list_ = get_bodies()

def get_new_bodies_():
    global cur_body_list_
    bodies = []
    all_bodies = get_bodies()

    for b in all_bodies:
        found = 0
        for c in cur_body_list_:
            if b._id == c._id: found = 1
        if not found:
            bodies.append(b)
    return bodies

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def set_surface_trimming_flag():
	return set_surface_trimming_flag_(faceID, flag)

#--------------------------------------------------------------------------------------------#

def get_surface_trimming_flag():
	return get_surface_trimming_flag_(faceID)

#--------------------------------------------------------------------------------------------#

def set_buffer_insertion_param():
	return set_buffer_insertion_param_(edgeID, flag)

#--------------------------------------------------------------------------------------------#

def get_buffer_insertion_param():
	return get_buffer_insertion_param_(edgeID)

#--------------------------------------------------------------------------------------------#

def HEXA_get_block_list():
	return HEXA_get_block_list_()

#--------------------------------------------------------------------------------------------#

def HEXA_set_active_block(name):
	return HEXA_set_active_block_(name)

#--------------------------------------------------------------------------------------------#

def get_all_domain_vertices():
	vertices = []
	for vertex in domain_get_all_vertices_():
		vertices.append(DomainVertex(vertex))
	return vertices

#--------------------------------------------------------------------------------------------#

def get_failed_captured_vertices():
	vertices = []
	for vertex in get_failed_captured_vertices_():
		vertices.append(DomainVertex(vertex))
	return vertices
	
#--------------------------------------------------------------------------------------------#

def get_failed_captured_edges():
	edges = []
	for edge in get_failed_captured_edges_():
		edges.append(DomainEdge(edge))
	return edges
	
#--------------------------------------------------------------------------------------------#

def get_all_domain_faces():
	faces = []
	for face in domain_get_all_faces_():
		faces.append(DomainFace(face))
	return faces

#--------------------------------------------------------------------------------------------#

def num_dfaces():
	l = domain_get_all_faces_()
	size = l.length()
	return size

#--------------------------------------------------------------------------------------------#

def dface(index):
	return DomainFace(index)

#--------------------------------------------------------------------------------------------#

def sort_faces_by_perimeter(in_faces):
	faces      = []
	perimeters = []
	cur_size   = 0
	for face in in_faces:
		perim = face.get_perimeter()

		inserted = 0
		for i in range(cur_size):
			if perim<perimeters[i]:
				faces.insert(i,face)
				perimeters.insert(i,perim)
				inserted = 1
				break
		if not inserted:
			faces.append(face)
			perimeters.append(perim)
				
		cur_size = cur_size +1

	return faces

#--------------------------------------------------------------------------------------------#

def set_global_adaptation_params(num_refinement):
	
	maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap = get_global_adaptation_params_()
	
	set_global_adaptation_params_(num_refinement,diffusion,minSize,maxSize,maxAR,nbCellsInGap)

#--------------------------------------------------------------------------------------------#

def set_adapt_flags(refine_flag,blank_flag):
	
	set_adapt_flags_(refine_flag,blank_flag)

#--------------------------------------------------------------------------------------------#

def get_negative_cells_center():
	return get_negative_cells_center_()

#--------------------------------------------------------------------------------------------#

def get_concave_cells_center():
	return get_concave_cells_center_()

#--------------------------------------------------------------------------------------------#

def get_concave_cells_center_slow():
	return get_concave_cells_center24_()

#--------------------------------------------------------------------------------------------#
