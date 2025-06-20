#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         M.P.                                                           Fev 2004            #
#--------------------------------------------------------------------------------------------#

import sys,os,math,copy,re

import types
import fnmatch

from Geom      import *
from IGGSystem import *
from CADImport import *
from Parasolid import *
from UHexaCommands import *
from UHexaDrawingCommands import *
from UHexaProjectCommands import *
from UHexaMeshGenerationCommands import *
from UHexaMeshQualityAnalysisCommands import *
from HXPGeomCommands import *
from UHexaFNMB import *
from DomainManip import *
from UHexaMesh import *
from BodyManip import *
from STLCmdsForImport import *
from STLManip import *
from HXPDebugCommands import *
import PythonViewing

## import types
## from Geom      import *
## #from CADImport import *
## #from Parasolid import *
## from UHexaCommands import *
## from UHexaMesh import *
#from UHexaFNMB import *

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#               Global query functions                                                       #
#--------------------------------------------------------------------------------------------#

def is_marine_version():
    return is_marine_version_()

def open_project(filename, loadMeshFlag = 1, conversionMode = 0, newFilename = "", finestLevel = 0, coarsestLevel = 0, transformNMBtoFNMB = 0, mergeZR = 0):

    # We currently force meshloading by setting loadMeshFlag to 2
    if loadMeshFlag == 1: loadMeshFlag = 2

    if not is_batch():
        #eval_tcl_string( "Hexa:Project:OpenProject {" + filename + "} 2" )
        eval_tcl_string( "Hexa:Project:BeforeOpenProject" )

        if filename != "":
            rc = HXP_open_project_(filename, 2, transformNMBtoFNMB)

            if rc == 2:
                convert2Hexa(filename, conversionMode, newFilename, finestLevel, coarsestLevel, mergeZR)
                return

            eval_tcl_string("Hexa:Project:AfterOpenProject {" + filename + "} " + str(rc))
    else:
        rc = HXP_open_project_(filename,loadMeshFlag,transformNMBtoFNMB)

        if rc == 2:
            convert2Hexa(filename, conversionMode, newFilename, finestLevel, coarsestLevel, mergeZR)

#--------------------------------------------------------------------------------------------#

def close_project():
    HXP_close_project_()
    
#--------------------------------------------------------------------------------------------#

def import_project(filename, conversionMode = 0, newFilename = "", finestLevel = 0, coarsestLevel = 0, mergeZR = 0):
    if not is_batch():
        #eval_tcl_string( "Hexa:Project:importProject {" + filename + "}" )

        currentActiveBlock = HXP_get_active_block_()
        currentNbOfBlocks = len(hxp_get_blocks_())

        if currentActiveBlock == "":
            eval_tcl_string(" puts \"bad\" ")
            open_project(filename, 1, conversionMode, newFilename, finestLevel, coarsestLevel)
            return

        if filename != "":
            HXP_importMeshIfNeeded_()
            rc = HXP_import_project_(filename, 1)

            if rc == 2:
                convert2Hexa(filename, conversionMode, newFilename, finestLevel, coarsestLevel, mergeZR)

            eval_tcl_string("Hexa:Project:afterImportProject " + currentActiveBlock + " " + str(currentNbOfBlocks) + " " + str(rc))
    else:
        rc = HXP_import_project_(filename,1)

        if rc == 2:
            convert2Hexa(filename, conversionMode, newFilename, finestLevel, coarsestLevel, mergeZR)

#--------------------------------------------------------------------------------------------#

def convert2Hexa(filename, conversionMode = 0, newFilename = "", finestLevel = 0, coarsestLevel = 0, mergeZR = 0):
    if not is_batch():
        if is_silent_mode():
            if newFilename == "":
                return
            if conversionMode == 0:
                HXP_setConnectionsImportMode_(1)
            else:
                HXP_setConnectionsImportMode_(0)
            eval_tcl_string("global hexa; set hexa(newProjectName) \"" + newFilename + "\"" )
            HXP_setConverterParameters_(finestLevel, coarsestLevel, mergeZR)
            rc = HXP_igg2hexa_(filename, newFilename, 1)
            eval_tcl_string("Hexa:Project:AfterConversion " + str(rc))
        else:
            HXP_setConverterParameters_(finestLevel, coarsestLevel, mergeZR)
            eval_tcl_string("Hexa:Project:Convert2Hexa:dialogBox {" + filename + "}")
    else:
        if newFilename == "":
            return
        if conversionMode == 0:
            HXP_setConnectionsImportMode_(1)
        else:
            HXP_setConnectionsImportMode_(0)
        HXP_setConverterParameters_(finestLevel, coarsestLevel, mergeZR)
        HXP_igg2hexa_(filename, newFilename, 1)

#--------------------------------------------------------------------------------------------#

def save_project(filename = 0):
    if filename == 0:
        HXP_save_project_()
    else:
        if not is_batch():
            eval_tcl_string("Hexa:Project:SaveProjectAs {" + filename + "}")
        else:
            HXP_saveAs_project_(filename)

#--------------------------------------------------------------------------------------------#

def save_domain_state():
    HXP_save_domain_state_()

#--------------------------------------------------------------------------------------------#

def face_set_bc_type(block_name, face_id, itype):
    HXP_face_set_bc_type_(block_name, face_id, itype)

#--------------------------------------------------------------------------------------------#

def import_domain(filename):
    if not os.path.exists(filename):
        raise ValueError("Domain file does not exist",filename)

    HXP_delete_stl_triangulation_()
    if not is_batch():
        eval_tcl_string( "hexa_import_domain {" + filename + "}" )
    else:
        HXP_import_domain_(filename)
    #eval_tcl_string("hexa_activate_menus 0")
    #eval_tcl_string("hexa_init_mesh:update 0")

#--------------------------------------------------------------------------------------------#

def import_dat_file (filename):
    if not os.path.exists(filename):
        raise ValueError("Data file does not exist",filename)

    if not is_batch():
        eval_tcl_string( "hexa_import_dat \"" + filename + "\"" )
    else:
        HXP_import_dat_file_(filename)

#--------------------------------------------------------------------------------------------#

def create_2d_domain(filename, zSize, curve_tol, curve_ang, curve_max, curveList):
    HXP_delete_stl_triangulation_()
    if not is_batch():
        #eval_tcl_string( "Hexa:Project:create_2d_domain " + filename + " " + str(zSize) )
        curBlock = HXP_get_active_block_()
        errCode = HXP_create_2d_domain_(filename, zSize, curve_tol, curve_ang, curve_max, collect_curves_pointers_(curveList))
        eval_tcl_string( "hexa_handle_domain_error " + str(errCode) + " \"" + curBlock + "\" \"" + filename + "\" \"2D\"" )
        eval_tcl_string( "hexa_modify_cursor \"normal\"")
    else:
        HXP_create_2d_domain_(filename, zSize, curve_tol, curve_ang, curve_max, collect_curves_pointers_(curveList))

#--------------------------------------------------------------------------------------------#

def replace_domain(filename, tolerance, numComparisonIterations, succesfulReplaceDomain):
    if not os.path.exists(filename):
        raise ValueError("Parasolid file does not exist",filename)
    else:
        HXP_replace_domain_(filename, tolerance, numComparisonIterations, succesfulReplaceDomain)

#--------------------------------------------------------------------------------------------#

def replace_domain_block(blockNum, applyMap, edgeIDMap, faceIDMap):
    edgeIDMap_ = []
    if (type(edgeIDMap) is types.TupleType) or (type(edgeIDMap) is types.ListType):
        for eitem in edgeIDMap:
            edgeIDMap_.append( eitem )
    else:
        edgeIDMap_.append( edgeIDMap )

    faceIDMap_ = []
    if (type(faceIDMap) is types.TupleType) or (type(faceIDMap) is types.ListType):
        for fitem in faceIDMap:
            faceIDMap_.append( fitem )
    else:
        faceIDMap_.append( faceIDMap )

    HXP_replace_domain_block_(blockNum, applyMap, edgeIDMap_, faceIDMap_)

#--------------------------------------------------------------------------------------------#

def import_parasolid(filename):
    if not os.path.exists(filename):
        raise ValueError("Parasolid file does not exist",filename)

    if not is_batch():
        eval_tcl_string("doOpen_X_T {" + filename + "}")
    else:
        HXP_import_parasolid_(filename)

#--------------------------------------------------------------------------------------------#

def import_catia(filename):
    if not os.path.exists(filename):
        raise ValueError("CATIA v5 file does not exist",filename)

    import_catia_file(filename)

#--------------------------------------------------------------------------------------------#

def import_catia_v6(filename):
    if not os.path.exists(filename):
        raise ValueError("CATIA v6 file does not exist",filename)

    import_catia_v6_file(filename)

#--------------------------------------------------------------------------------------------#

def export_parasolid(filename, bodies = [] ):
    if len(bodies) > 0:
        b = []
        extract_bodies_(bodies,b)
        HXP_Para_exportBodies_(filename,b)
    else:
        HXP_Para_export_(filename)

#--------------------------------------------------------------------------------------------#

def import_CGNS(filename):
    if not os.path.exists(filename):
        raise ValueError("CGNS file does not exist",filename)

    if not is_batch():
        eval_tcl_string( "Hexa:Project:ImportCGNSMesh {" + filename + "}" )
    else:
        HXP_import_CGNS_(filename)
        name = HXP_save_mesh_step_("init")
        init_mesh_from_file(name)

#--------------------------------------------------------------------------------------------#

def clear_cache():
    return HXP_clear_cache_()

#--------------------------------------------------------------------------------------------#

def disable_cache_recording():
    return HXP_disableCacheRecording_()

#--------------------------------------------------------------------------------------------#

def activate_mesh_wizard_step(step_name):
    if not is_batch():
        tclCommand = "hexa_activate_mesh_wizard_step " + step_name;
        eval_tcl_string(tclCommand)

#--------------------------------------------------------------------------------------------#

def delete_domain(domain_name):
    set_active_domain(domain_name)
    HXP_delete_domain_(0)
    domains = get_all_domains()
    set_active_domain(domains[0])

#--------------------------------------------------------------------------------------------#

def create_fnmb(name, lpatchList, rpatchList, stype, max_proj_dist, min_proj_dist, nb_iter, is_periodic, periodicity_idx, nb_repet, is_reversed, tolerance1, tolerance2):
    nleft = len(lpatchList)
    nright = len(rpatchList)
    create_fnmb_(name, nleft, lpatchList, nright, rpatchList, stype, max_proj_dist, min_proj_dist, nb_iter, is_periodic, periodicity_idx, nb_repet, is_reversed, tolerance1, tolerance2)

#--------------------------------------------------------------------------------------------#

def new_periodicity(blockIdx):
    return HXP_new_periodicity_(blockIdx)

#--------------------------------------------------------------------------------------------#

def set_periodicity_param(blockIdx, perIdx, type, orig_x, orig_y, orig_z, axis_x, axis_y, axis_z, numRep):
    HXP_set_periodicity_param_(blockIdx, perIdx, type, orig_x, orig_y, orig_z, axis_x, axis_y, axis_z, numRep)

#--------------------------------------------------------------------------------------------#

def delete_periodicity(blockIdx, perIdx):
    HXP_delete_periodicity_(blockIdx, perIdx)

#--------------------------------------------------------------------------------------------#

#def exit():
#   HXP_exit_()

#--------------------------------------------------------------------------------------------#

def get_domain_file_name():
    files = HXP_getProjectFilenames_()

    #print type( files[0][0] )
    if files[0][0] != 'hexa_none' and files[0][0] != 'none':
        return files[0][0][:-3] + 'dom'
    else:
        return files[3][0]
    
#--------------------------------------------------------------------------------------------#
#--------------------------------------STL Commands -----------------------------------------#
#--------------------------------------------------------------------------------------------#

STL_IMPORT_GROUP_BY_PROP_FILE = 0
STL_IMPORT_GROUP_BY_FEATURE   = 1
STL_IMPORT_GROUP_BY_NAMES     = 2
STL_DEFAULT_FEATURE_TOLERANCE       = 1e-20;
STL_DEFAULT_FEATURE_DETECTION_ANGLE = 40.0;

def import_stl(filename, importMode = STL_IMPORT_GROUP_BY_PROP_FILE, fTolerance = STL_DEFAULT_FEATURE_TOLERANCE, fAngle = STL_DEFAULT_FEATURE_DETECTION_ANGLE):
    errCode = STL_import_domainSTL_(filename, importMode)
    if importMode == STL_IMPORT_GROUP_BY_PROP_FILE:
        # update gui
        if errCode == 0:
            # prop file is not found -> detect groups by names
            msg = "*.prop file is not found. Predefined names from the STL file were used for grouping"
            print "\n[STL import] WARNING: " + msg + ".\n"
            if not is_batch():
                eval_tcl_string("SysMessage:warning {WARNING: " + msg + ".}")
        else:
            if not is_batch():
                eval_tcl_string("STLViewer:distroySTLTreeVeiw")
                eval_tcl_string("STLViewer:createSTLTreeView")
    else:
        if importMode == STL_IMPORT_GROUP_BY_FEATURE:
            STL_feature_detection_(fTolerance, fAngle)
        else:
            HXP_reconstruct_stl_groups_()

#--------------------------------------------------------------------------------------------#

# Create a separate group for every solid section in the corresponding STL file
def stl_group_by_predefined_names():
    HXP_reconstruct_stl_groups_()

#--------------------------------------------------------------------------------------------#

def stl_create_domain(filename):
    STL_create_domain_(filename)

#--------------------------------------------------------------------------------------------#

def stl_group_by_feature(tolerance, featureAngle):
    STL_feature_detection_(tolerance, featureAngle, 0)

#--------------------------------------------------------------------------------------------#

def stl_group_by_predefined_names():
    HXP_reconstruct_stl_groups_()

#--------------------------------------------------------------------------------------------#

class StlGroup:
    def __init__(self,id):
        self._id = id

    def __cmp__(self, other):
        if self._id == other._id:
            return 0
        return 1

    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return self._id

    def get_id(self):
        return self._id

    def get_parent(self):
        return STL_get_group_parent_(self._id)

    def get_name(self):
        return STL_get_group_name_(self._id)

    def set_name(self, name):
        STL_rename_single_group_(self._id, name)

# Return list of all stl groups
def get_stl_groups():
    groups = []
    for groupID in STL_get_all_groups_():
        groups.append(StlGroup(groupID))
    return groups

# Return list of groups by names, using unix style regular expression
def get_stl_groups_by_name(expr):
    #print "stl_get_groups_by_name : ",expr
    name_regexp = fnmatch.translate( expr )
    pattern =  re.compile(name_regexp,re.IGNORECASE)
    groups = []
    for groupID in STL_get_all_groups_():
        name = STL_get_group_name_( groupID )
        match =  pattern.search( name )
        if match:
            groups.append(StlGroup(groupID))
    return groups

# Merge specified stl groups
# list item can be integer ID or StlGroup object
def merge_stl_groups(group_list):
    #print "stl_merge_groups: ", group_list
    id_list = []
    for item in group_list:
        if type(item) is types.IntType:
            id_list.append( item )
        else:
            if isinstance(item,StlGroup):
                id_list.append( item.get_id() )
            else:
                print "[STL] Warning: cannot merge groups - wrong group id ", item
    STL_merge_groups_py_(len(id_list), id_list)

#--------------------------------------------------------------------------------------------#

# Split the group
# group: integer ID or StlGroup object
def split_stl_group(group, x1, y1, z1, x2, y2, z2):
    #print "stl_split_group: ", group, " at ", x1, y1, z1, " and ", x2, y2, z2
    if isinstance(group, StlGroup):
        STL_split_group_(group.get_id(), x1, y1, z1, x2, y2, z2)
    else:
        if type(group) is types.IntType:
            STL_split_group_(group, x1, y1, z1, x2, y2, z2)
        else:
            print "[STL] Warning: cannot split the group - wrong group id ", group

#--------------------------------------------------------------------------------------------#

# Rename the group
# group: integer ID or StlGroup object
def rename_stl_group(group, new_name):
    if isinstance(group, StlGroup):
        STL_rename_single_group_(group.get_id(), new_name)
    else:
        if type(group) is types.IntType:
            STL_rename_single_group_(group, new_name)
        else:
            print "[STL] Warning: cannot rename the group - wrong group id ", group

# Rename groups
# groups: list of integer IDs or StlGroup objects
# names : list of new names
# lists must be the same size
def rename_stl_groups(groups, names):

    if len(groups) != len(names):
        print "[STL] Warning: cannot rename a set of group - number of groups differ from number of names"
        return

    id_list = []
    name_list = []
    idx = 0
    for group in groups:
        if isinstance(group, StlGroup):
            id_list.append(group.get_id())
            name_list.append(names[idx])
        else:
            if type(group) is types.IntType:
                id_list.append(group)
                name_list.append(names[idx])
            else:
                print "[STL] Warning: cannot rename the group - wrong group id ", group
        idx = idx + 1

    STL_rename_groups_(idx, id_list, name_list)

#--------------------------------------------------------------------------------------------#

def reverse_orient(strGroupFlags):
    _notsup("reverse_orient")
    STL_reverse_orient_(strGroupFlags)

#--------------------------------------------------------------------------------------------#

def delete_stl_triangulation():
    #_notsup("delete_stl_triangulation")
    HXP_delete_stl_triangulation_()

    if not is_batch():
        eval_tcl_string("STLViewer:distroySTLTreeVeiw")
        eval_tcl_string("STLViewer:createSTLTreeView")

#--------------------------------------------------------------------------------------------#

def delete_stl_groups(num_groups, group_list):
    groups = []
    for group in group_list:
        if isinstance(group, StlGroup):
            groups.append(group.get_id())
        else:
            if type(group) is types.IntType:
                groups.append(group)
            else:
                if type(group) is types.StringType:
                    subset = get_stl_groups_by_name(group)
                    for subgroup in subset:
                        groups.append(subgroup.get_id())
                else:
                    print "[STL] Warning: cannot delete the group - wrong group id ", group

    HXP_delete_stl_groups_(len(groups), groups)

    if not is_batch():
        eval_tcl_string("STLViewer:distroySTLTreeVeiw")
        eval_tcl_string("STLViewer:createSTLTreeView")

#--------------------------------------------------------------------------------------------#

def delete_stl_files(num_files, files):
    HXP_delete_stl_files_(num_files, files)

    if not is_batch():
        eval_tcl_string("STLViewer:distroySTLTreeVeiw")
        eval_tcl_string("STLViewer:createSTLTreeView")

#--------------------------------------------------------------------------------------------#
#---------------------------------End of STL Commands ---------------------------------------#
#--------------------------------------------------------------------------------------------#

def lofted_surface(curves,name = "emptyName"):
    surf = HXP_create_internal_loft_surf_(collect_curves_pointers_(curves),name)
    if surf == 0: raise "Could not create lofted surface"
    return DomainFace( get_active_domain(), surf )

def import_internal_surface(filename):
    HXP_import_internal_surface_(filename)
    
def export_domain_to_stl(filename, ascii_flag):
    HXP_export_domain_to_stl_(filename, ascii_flag)

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

#def HEXA_regenerate_mesh():
#   return HEXA_regenerate_mesh_()

#def mesh_quality_reporting():
#   return HEXA_mesh_quality_reporting_()

def translate_mesh( domain_name, vec, use_correction = 0 ):
    domainPtr = get_domain_ptr_(domain_name)
    HXP_translate_mesh_(domainPtr, (vec.x,vec.y,vec.z), use_correction)

def rotate_mesh( domain_name, orig,dir, angle_deg, use_correction = 0):
    domainPtr = get_domain_ptr_(domain_name)
    HXP_rotate_mesh_(domainPtr, (orig.x,orig.y,orig.z), (dir.x,dir.y,dir.z), angle_deg, use_correction)
    
def scale_mesh( domain_name, scale, use_correction = 0 ):
    if scale.x <= 0.0 or scale.y <= 0.0 or scale.z <= 0.0:
        print "[Mesh Transformation] warning: invalid parameters for scaling transformation"
        print "[Mesh Transformation]          scale factors cannot be null or negative"
        if not is_batch():
            display_warning("scale factors cannot be null or negative")
    else:
        domainPtr = get_domain_ptr_(domain_name)
        HXP_scale_mesh_( domainPtr,(scale.x,scale.y,scale.z), use_correction)

#def mirror_mesh( domain_name , orig,dir ):
#    domainPtr = get_domain_ptr_(domain_name)
#    HXP_mirror_mesh_( domainPtr,(orig.x,orig.y,orig.z),(dir.x,dir.y,dir.z) )

def mirror_and_copy_mesh(domain_name , plane, use_correction = 0 ):
    domainPtr = get_domain_ptr_(domain_name)
    HXP_mirror_and_copy_mesh_( domainPtr, plane, use_correction)

def axisymmetric_mesh(domain_name,shift,axis,orig,angle,nbLayersToInsert):
    domainPtr = get_domain_ptr_(domain_name)
    params = HXP_get_axisymmetric_parameters_(shift, (axis.x, axis.y, axis.z), (orig.x, orig.y, orig.z))

    if (params[0] == 0):
        return
    phi = params[1]
    dz = params[2]

    HXP_translate_mesh_(domainPtr,(shift*axis.x,shift*axis.y,dz))
    HXP_rotate_mesh_(domainPtr,(orig.x,orig.y,orig.z),(0.0,0.0,1.0),phi)
    HXP_rotate_mesh_(domainPtr,(orig.x,orig.y,orig.z),(1.0,0.0,0.0),90.0)
    HXP_translate_mesh_(domainPtr,(-orig.x,-orig.y,-orig.z))
    HXP_axisymetric_mesh_(domainPtr,(0.0,0.0,0.0),(0.0,0.0,1.0),angle,nbLayersToInsert)

# keep old name for backward compatibility
def axisymetric_mesh(domain_name,shift,axis,orig,angle,nbLayersToInsert):
    axisymmetric_mesh(domain_name,shift,axis,orig,angle,nbLayersToInsert)


def extrude_mesh(domain_name, faceID, distance, extrusionFactor):
    domainPtr = get_domain_ptr_(domain_name)
    faces = []
    if isinstance(faceID,int):
        faces.append(faceID)
    else:
        faces += faceID
    defaultMode = 0
    HXP_apply_extrusion( domainPtr, len(faces), faces, distance, defaultMode, extrusionFactor)

#--------------------------------------------------------------------------------------------#

def get_num_parts():
    return HXP_get_num_parts_()

def get_parts():
    num_parts,parts = HXP_get_parts_()
    return parts

# Translate parts of active domain
def translate_parts(part_ids,dir):

    parts = []
    if (type(part_ids) is types.TupleType) or (type(part_ids) is types.ListType):
        for sitem in part_ids:
            parts.append( sitem )
    else:
        parts.append( part_ids )
        
    HXP_translate_part_(parts, (dir.x, dir.y, dir.z) )

def rotate_parts(part_ids,orig,dir,angle_deg):
    parts = []
    if (type(part_ids) is types.TupleType) or (type(part_ids) is types.ListType):
        for sitem in part_ids:
            parts.append( sitem )
    else:
        parts.append( part_ids )
        
    HXP_rotate_part_(parts, (orig.x,orig.y,orig.z) , (dir.x,dir.y,dir.z) ,angle_deg)

def scale_parts(part_ids,scale_factor):
    
    parts = []
    if (type(part_ids) is types.TupleType) or (type(part_ids) is types.ListType):
        for sitem in part_ids:
            parts.append( sitem )
    else:
        parts.append( part_ids )
        
    HXP_scale_part_(parts, ( scale_factor.x, scale_factor.y, scale_factor.z ) )

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
        
class DomainVertex:
    def __init__(self,domain,id):
        self._domain = domain
        self._id     = id

    def __cmp__(self, other):
        if self._id == other._id:
            return 0
        return 1
    
    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return self._id

    def get_id(self):
        return self._id

    def get_position(self):
        x,y,z = get_vertex_position_(self._domain.get_index(), self._id)
        return Point(x,y,z)

    def get_edges(self):
        edges = []
        for edge in HXP_get_vertex_edges_(self._domain.get_index(), self._id):
            edges.append(DomainEdge(self._domain, edge))
        return edges
    
    def get_faces(self):
        faces = []
        for face in HXP_get_vertex_faces_(self._domain.get_index(), self._id):
            faces.append(DomainFace(self._domain, face))
        return faces


#--------------------------------------------------------------------------------------------#

class DomainEdge:
    def __init__(self,domain,id):
        self._domain = domain
        self._id     = id

    def __cmp__(self, other):
        if self._id == other._id:
            return 0
        return 1
    
    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return self._id

    def get_id(self):
        return self._id

    def get_curve_ptr(self):
        return HXP_edge_get_curve_( self._domain._pointer , self._id )

    def get_length(self):
        _notsup2("DomainEdge::get_length")
        return HXP_edge_get_length_( self._domain._pointer , self._id )

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_edge_get_box_(self._domain._pointer,self._id)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])

    def get_other_face(self,face):
        f1,f2 = HXP_edge_get_all_faces_( self._domain._pointer , self._id )
        if face._id == f1: return DomainFace(self._domain,f2)
        else:              return DomainFace(self._domain,f1)

    def get_faces(self):
        f1,f2 = HXP_edge_get_all_faces_( self._domain._pointer , self._id )
        return DomainFace(self._domain,f1),DomainFace(self._domain,f2)

    def get_vertices(self):
        v0,v1 =  HXP_edge_get_vertices_( self._domain._pointer , self._id)
        if v0 != -1 and v1 != -1:
            return DomainVertex(self._domain,v0),DomainVertex(self._domain,v1)
        else:
            return ()

    def set_buffer_insertion_type(self,value):
        HXP_set_edge_buffer_type_(self._id,value)

    def set_snap_mode(self,value):
        # 0 must be captured
        # 1 must be skipped
        # 2 Can be skipped
        HXP_set_edge_snap_mode_(self._id,value)

    def is_adaptation_enabled(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)
        return active

    def enable_adaptation(self,value):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,value,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ)

    def set_number_of_refinements(self,n):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,n,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ)

    def get_number_of_refinements(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)
        return maxRef

    def set_adaptation_criteria(self,dist,curvature,target):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,maxAR,dist,curvature,crf,target,sizeX,sizeY,sizeZ)
        
    def set_adaptation_criterias(self,dist,curvature,target):
        self.set_adaptation_criteria(dist,curvature,target)
        
    def get_adaptation_criteria(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        return distActive,curvatureActive,sizeActive
    
    def get_adaptation_criterias(self):
        return self.get_adaptation_criteria()
    
    def enable_distance_criteria(self):
        _notsup2("DomainEdge::enable_distance_criteria")
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,maxAR,1,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ)

    def enable_curvature_criteria(self):
        _notsup2("DomainEdge::enable_curvature_criteria")
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,maxAR,distActive,1,crf,sizeActive,sizeX,sizeY,sizeZ)

    def set_max_aspect_ratio(self,n):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,n,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ)

    def get_max_aspect_ratio(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)
        return maxAR

    def set_target_sizes(self,x,y,z):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,1,x,y,z)

    def get_target_sizes(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)
        return sizeX,sizeY,sizeZ

    def set_diffusion_depth(self,depth):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,depth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ)

    def get_diffusion_depth(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        return diffDepth

    def set_advanced_adaptation_criteria(self,maxAR_in,crf_in):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        HXP_set_edge_adapation_params_(self._id,active,maxRef,diffDepth,maxAR_in,distActive,curvatureActive,crf_in,sizeActive,sizeX,sizeY,sizeZ)

    def set_advanced_adaptation_criterias(self,maxAR_in,crf_in):
        self.set_advanced_adaptation_criteria(maxAR_in,crf_in)

    def get_advanced_adaptation_criteria(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        return maxAR,crf

    def get_advanced_adaptation_criterias(self):
        return self.get_advanced_adaptation_criteria()

    def get_max_aspect_ratio(self):
        active,maxRef,diffDepth,maxAR,distActive,curvatureActive,crf,sizeActive,sizeX,sizeY,sizeZ = HXP_get_edge_adapation_params_(self._id)

        return maxAR

    def get_min_angle_between_faces(self):
        (minA,maxA,aver) = HXP_edge_get_angles_between_faces_( self._domain._pointer , self._id )
        return minA

    def get_min_max_angles_between_faces(self):
        _notsup2("DomainEdge::get_min_max_angles_between_faces")
        (minA,maxA,aver) = HXP_edge_get_angles_between_faces_( self._domain._pointer , self._id )
        return [minA,maxA,aver]

    # "t" is a curvilinear coordinate between 0 and 1
    # a linear interpolation is used between two real points
    def get_point_at(self, t):
        errCode, x, y, z = HXP_point_location_(self._domain.get_index(), self._id, t)
        if errCode != 0:
            raise Exception("Could not find point on curve "+str(self._id))
        return Point(x,y,z)

    def get_number_of_points(self):
        return HXP_number_points_in_edge_(self._domain.get_index(), self._id)

    def get_point_at_index(self, idx):
        errCode, x, y, z = HXP_edge_get_point_at_(self._domain.get_index(), self._id, idx)
        if errCode != 0:
            raise Exception("Could not get point on curve with index "+str(idx))
        return Point(x, y, z)

#--------------------------------------------------------------------------------------------

class DomainFace:
    # Note _id is the faceID of the Face
    #
    def __init__(self,domain,id):
        self._domain = domain
        self._id     = id

    def __cmp__(self, other):
        if self._id == other._id:
            return 0
        return 1
    
    def __eq__(self, other):
        return self._id == other._id

    def get_id(self):
        return self._id

    def is_enabled(self):
        return HXP_face_is_enabled_(self._domain._pointer,self._id)

    def get_name(self):
        return HXP_face_get_name_(self._domain._pointer,self._id)

    def set_name(self,name):
        return HXP_set_face_name_(self._domain.get_index(),self._id,name)

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_face_get_box_(self._domain._pointer,self._id)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])
    
    def get_rtz_box(self,axis = "Z",orig=Point(0,0,0)):
        _notsup2("DomainFace::get_rtz_box")
        iaxis = 0
        if axis=="Y": iaxis = 1
        if axis=="Z": iaxis = 2
        
        rmin,tmin,zmin,rmax,tmax,zmax = HXP_face_get_rtz_box_(self._domain._pointer,self._id,iaxis,orig.x,orig.y,orig.z)
        return BoxRTZ([rmin,rmax,tmin,tmax,zmin,zmax])

    def get_vertices(self):
        vertexIds = []
        for edge in HXP_face_get_all_edges_( self._domain._pointer , self._id ):
            v0,v1 =  HXP_edge_get_vertices_( self._domain._pointer , edge)
            if v0 != -1 and (not v0 in vertexIds) :
                vertexIds.append(v0)
            if v1 != -1 and (not v1 in vertexIds) :
                vertexIds.append(v1)

        vertices = []
        for v in vertexIds:
            vertices.append(DomainVertex(self._domain,v))

        return vertices

    def contains_vertex(self,vertex):
        vertexID = -1;
        if isinstance(vertex,DomainVertex):
            vertexID = vertex._id
        else:
            vertexID = vertex

        if vertexID == -1:
            return 0

        for e in HXP_face_get_all_edges_(self._domain._pointer , self._id):
            v0, v1 = HXP_edge_get_vertices_(self._domain._pointer, e)
            if vertexID == v0 or vertexID == v1:
                return 1
        return 0

    def get_angle_between_edges_at_vertex(self,vertex):
        vertexID = -1;
        if isinstance(vertex,DomainVertex):
            vertexID = vertex._id
        else:
            vertexID = vertex
        errCode, angle = HXP_face_get_angle_at_corner_(self._domain.get_index(), self._id, vertexID)
        return angle

    def num_edges(self):
        return len( HXP_face_get_all_edges_( self._domain._pointer , self._id) )

    def get_edges(self):
        edges = []
        for edge in HXP_face_get_all_edges_( self._domain._pointer , self._id ):
            edges.append(DomainEdge(self._domain,edge))
        return edges

    def get_neightbor_edges(self,edge):
        _notsup("DomainFace::get_neightbor_edges")
        v0,v1 = HXP_edge_get_vertices_( self._domain._pointer , edge._id)
        if v0==v1: return DomainEdge(self._domain,-1),DomainEdge(self._domain,-1)
        
        left  = -1
        right = -1
        for e in HXP_face_get_all_edges_( self._domain._pointer , self._id ):
            if e==edge._id: continue
            
            ve0,ve1 = HXP_edge_get_vertices_( self._domain._pointer , e)
            if ve0==v0 or ve1==v0:
                left = DomainEdge(self._domain,e)
            elif ve0==v1 or ve1==v1:
                right = DomainEdge(self._domain,e)
                
        return left,right

    def get_loops(self):
        edges = HXP_face_get_all_edges_(self._domain._pointer , self._id)

        return  get_loops_from_list_of_edges( self , edges )

    def num_loops(self):
        loops = self.get_loops()
        count = 0
        for loop in loops:
            count = count + 1
            
        return count

    def get_common_edges(self, face ):
        edges = []

        for edge in self.get_edges():
            if face.contains_edge(edge):
                edges.append(edge)

        return edges
    
    def get_connected_faces(self):
        _notsup2("DomainFace::get_connected_faces")
        faces = []

        for edge in self.get_edges():
            other_face = edge.get_other_face(self)
            if not other_face in faces:
                faces.append(other_face)
        return faces

    def get_num_connected_faces(self):
        faces = []

        for edge in self.get_edges():
            other_face = edge.get_other_face(self)
            if not other_face in faces:
                faces.append(other_face)
        return len(faces)
            
    def get_neighbor_faces(self):
        faces = []

        for edge in self.get_edges():
            other_face = edge.get_other_face(self)
            if not other_face in faces:
                faces.append(other_face)
        return faces
            
    def num_triangles(self):
        return HXP_face_num_triangles_(self._domain._pointer,self._id)
        
    def contains_edge(self,edge):
        edgeID = -1;
        if isinstance(edge,DomainEdge):
            edgeID = edge._id
        else:
            edgeID = edge
        for e in HXP_face_get_all_edges_(self._domain._pointer , self._id):
            if e == edgeID: return 1
        return 0

    def is_adaptation_enabled(self):
        return get_face_adapation_flag_(self._id)

    def enable_adaptation(self,value):
        HXP_face_enable_adaptation_(self._id,value)

#   def set_adaptations_criteria(self,dist,curvature,target,nv,aniso_extent):
#       HXP_set_adaptation_criterias_(self._id,distance,curvature,target,nv,aniso_extent)

    def set_adaptation_criteria(self,dist,curvature,target):
        disto,curvo,targeto,nv,aniso_extent = get_face_adaptation_criteria_(self._id)
        HXP_set_adaptation_criterias_(self._id,dist,curvature,target,nv,aniso_extent)

    def set_adaptation_criterias(self,dist,curvature,target):
        self.set_adaptation_criteria(dist,curvature,target)

    def get_adaptation_criteria(self):
        disto,curvo,targeto,nv,aniso_extent = get_face_adaptation_criteria_(self._id)
        return disto,curvo,targeto

    def get_adaptation_criterias(self):
        return self.get_adaptation_criteria()

    def set_advanced_adaptation_criteria(self,curvatureFactor,aniso_extent):
        dist,curv,target,nv,a_e = get_face_adaptation_criteria_(self._id)
        HXP_set_adaptation_criterias_(self._id,dist,curv,target,curvatureFactor,aniso_extent)
        
    def set_advanced_adaptation_criterias(self,curvatureFactor,aniso_extent):
        self.set_advanced_adaptation_criteria(curvatureFactor,aniso_extent)

    def get_advanced_adaptation_criteria(self):
        dist,curv,target,nv,a_e = get_face_adaptation_criteria_(self._id)
        return nv,a_e
    
    def get_advanced_adaptation_criterias(self):
        return self.get_advanced_adaptation_criteria()

    def set_diffusion_depth(self,depth):
        HXP_set_face_adapt_diffusion_depth_(self._id,depth)

    def get_diffusion_depth(self):
        return HXP_get_face_diffusion_depth_(self._id)[0]

    def enable_distance_criteria(self):
        _notsup2("DomainFace::enable_distance_criteria")
        dist,curv,target,nv,aniso_extent = get_face_adaptation_criteria_(self._id)
        HXP_set_adaptation_criterias_(self._id,1,curv,target,nv,aniso_extent)

    def enable_curvature_criteria(self):
        _notsup2("DomainFace::enable_curvature_criteria")
        dist,curv,target,nv,aniso_extent = get_face_adaptation_criteria_(self._id)
        HXP_set_adaptation_criterias_(self._id,dist,1,target,nv,aniso_extent)

    def set_target_sizes(self,x,y,z):

        # enable target size
        disto,curvo,targeto,nv,aniso_extent = get_face_adaptation_criteria_(self._id)
        HXP_set_adaptation_criterias_(self._id,disto,curvo,1,nv,aniso_extent)

        xo,yo,zo,min,max =  get_face_cell_size_(self._id)

        HXP_set_face_cell_size_(self._id,x,y,z,min,max)

    def get_target_sizes(self):
        x,y,z,min,max =  get_face_cell_size_(self._id)
        return x,y,z

    def set_min_max_cell_size(self,minSize,maxSize):
        _notsup("DomainFace::set_min_max_cell_size")
        x,y,z,min,max =  get_face_cell_size_(self._id)

        HXP_set_face_cell_size_(self._id,x,y,z,minSize,maxSize)

    def set_number_of_refinements(self,n):
        max_ref,max_aspect_ratio = get_face_adapation_parameters_(self._id)
        HXP_set_face_adapation_params_(self._id,n,max_aspect_ratio)

    def get_number_of_refinements(self):
        max_ref,max_aspect_ratio = get_face_adapation_parameters_(self._id)
        return max_ref
    
    def set_max_aspect_ratio(self,n):
        max_ref,max_aspect_ratio = get_face_adapation_parameters_(self._id)
        HXP_set_face_adapation_params_(self._id,max_ref,n)

    def get_max_aspect_ratio(self):
        max_ref,max_aspect_ratio = get_face_adapation_parameters_(self._id)
        return max_aspect_ratio

    def enable_trimming(self,value):
        HXP_face_set_trimming_flag_(self._id,value)

    def enable_viscous_layers(self,value):
        HXP_face_enable_VL_(self._id,value)

    def set_viscous_layer_params(self,nbLayer,stretch,thickness,aspectRatio = 5.,expansion = 1.3 ):
        nbLayerO,stretchO,thicknessO,d4,d5,d6,d7,d8,d9,d10,d11,d12 = HXP_face_get_VL_params_(self._id)
        HXP_face_set_VL_params_(self._id,nbLayer,stretch,thickness,aspectRatio,expansion,d6,d7,d8,d9,d10,d11,d12)

    def is_viscous_layers_enabled(self):
        return HXP_face_is_VL_active_(self._id)

    def get_viscous_layer_params(self):
        nbLayer,stretch,thickness,d4,d5,d6,d7,d8,d9,d10,d11,d12 = HXP_face_get_VL_params_(self._id)
        return [nbLayer,stretch,thickness]

    def get_min_edge_length(self):
        _notsup("DomainFace::get_min_edge_length")
        min = 1.e30
        for edge in self.get_edges():
            edge_length = edge.get_length()
            if(edge_length<min): min = edge_length
        return min
    
    def get_max_edge_length(self):
        _notsup("DomainFace::get_max_edge_length")
        max = -1.e30
        for edge in face.get_edges():
            edge_length = edge.get_length()
            if(edge_length>max): max = edge_length
        return max

    def get_closest_dist(self):
        _notsup("DomainFace::get_closest_dist")
        # Return closest distance to "opposite" face
        #
        return HXP_face_get_closest_dist_(self._domain._pointer,self._id)

    def get_area(self):
        return HXP_face_get_area_(self._domain._pointer,self._id)

    def get_perimeter(self):
        #_notsup("DomainFace::get_perimeter")
        perim = 0.
        for edge in self.get_edges():
            perim = perim + edge.get_length()
        return perim

    def get_type(self):
        return HXP_face_get_bc_type_(self._domain.get_index(),self._id)

    def set_type(self,type,change_default_trimming = 0):
        itype = 0
        if   type=="UND": itype = 0
        elif type=="CON": itype = 1
        elif type=="SOL": itype = 2
        elif type=="EXT": itype = 3
        elif type=="PER": itype = 4
        elif type=="NMB": itype = 5
        elif type=="SNG": itype = 6
        elif type=="MIR": itype = 7
        elif type=="INL": itype = 8
        elif type=="OUT": itype = 9
        elif type=="PERNM": itype = 10 
        elif type=="ROT": itype = 12

        if is_silent_mode():
            HXP_face_set_bc_type_(self._domain.get_name(),self._id,itype, 1, change_default_trimming)
        else:
            HXP_face_set_bc_type_(self._domain.get_name(),self._id,itype, 0)

    def get_color(self):
        ''' Returns RGB color triplet. Values between [0,255]'''
        
        material =  HXP_get_face_material_( self._domain.get_index() , self._id )
        r = material[0][0]
        g = material[0][1]
        b = material[0][2]

        return [int(r*255) , int(g*255) , int(b*255) ]

    def set_color(self,color):
        ''' Set color as RGB triplet. Values between [0,255]'''

        rgb = color
        if type(color) is types.StringType:
            rgb = RGBColor.color( color )
            
        material  =  HXP_get_face_material_( self._domain.get_index() , self._id )
        tmaterial = list(material)
        tmaterial[0] = list( tmaterial[0] )

        tmaterial[0][0] = float(rgb[0]) / 255.
        tmaterial[0][1] = float(rgb[1]) / 255.
        tmaterial[0][2] = float(rgb[2]) / 255.

        HXP_set_face_material_( self._domain.get_index() , self._id , tmaterial )

    def show_shading(self):
        _notsup2("DomainFace::show_shading")
        shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._domain._pointer , self._id, 1 , tri , mesh )

    def hide_shading(self):
        _notsup2("DomainFace::hide_shading")
        shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._domain._pointer , self._id, 0 , tri , mesh )

    def show_triangulation(self):
        _notsup2("DomainFace::show_triangulation")
        shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._domain._pointer , self._id, shade , 1 , mesh )

    def show_mesh(self):
        _notsup2("DomainFace::show_mesh")
        shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._domain._pointer , self._id, shade , tri , 1 )

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
# Face helper functions

# This function checks whether two faces are tangent at their common edges
# For each common edge, the algorithm takes the max angle between the two faces
# and compares it with a threshold value specified as input

def are_faces_fully_tangent_at_common_edges(ref_face,other_face,delta_angle):
    
    # delta_angle represents a threshold angle that must be added or substracted to 180 degrees
    # i.e delta_angle = 20

    if ref_face == other_face:
        return 1

    # Loop over each edge of the ref_face and perform the check if the edge is common
    # to the other face
    for edge in ref_face.get_edges():
        tf = edge.get_other_face( ref_face )

        if tf == other_face:
            mina,maxa,aver = edge.get_min_max_angles_between_faces()

            if aver < 180. - delta_angle or aver > 180. + delta_angle:
                # tangancy condition not met, break
                return 0
    return 1

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class DomainFaceLoop:
    def __init__(self,face,edgeIds):
        self._face  = face
        self._edges = []
        for e in edgeIds:
            if isinstance(e,DomainEdge):
                self._edges.append( e )
            else:
                self._edges.append( DomainEdge( face._domain, e ) )

#        for e in edgeIds:
#            self._edges.append( DomainEdge( face._domain, e ) )

    def get_edges(self):
        return self._edges

    def get_xyz_box(self):
        loopBox = Box( [1e30,-1e30,1e30,-1e30,1e30,-1e30] )
        
        for e in self._edges:            
            box = e.get_xyz_box()
            loopBox = loopBox + box
            
        return loopBox

    def get_perimeter(self):

        perim = 0.
        for edge in self._edges:            
            perim = perim + edge.get_length()

        return perim


#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_loops_from_list_of_edges( face , edges ):

    all_loops       = []
    remaining_edges = []                        # convert tuple to list

    if isinstance(edges[0],DomainEdge):
        for e in edges: remaining_edges.append(e._id)
    else:
        for e in edges: remaining_edges.append(e)

    # Begin search for a new loop
    while len(remaining_edges) > 0:
        aloop = []
        all_loops.append( aloop )
        
        edge = remaining_edges.pop()
        aloop.append(edge)
        
        vStart,vEnd = HXP_edge_get_vertices_( face._domain._pointer , edge )
            
        # if vertices ==-1 or are equal => loop !!
        if vStart == vEnd:
            continue

        remaining_edges_for_current_loop = copy.deepcopy(remaining_edges)

        end_loop = 0

        while not end_loop:

            for cedge in remaining_edges_for_current_loop:
                v0,v1 = HXP_edge_get_vertices_( face._domain._pointer , cedge )

                if v0==vEnd:
                    vEnd = v1
                    aloop.append( cedge )
                    remaining_edges_for_current_loop.remove(cedge)
                    remaining_edges.remove(cedge)
                    break
                elif v1==vEnd:
                    vEnd = v0
                    aloop.append( cedge )
                    remaining_edges_for_current_loop.remove(cedge)
                    remaining_edges.remove(cedge)
                    break

            if vEnd==vStart:
                end_loop = 1

    return_loops = []
    for loop in all_loops:
        return_loops.append( DomainFaceLoop( face , loop ) )

    return return_loops

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class Domain:
    # !! pointer is actually pointer to hexaBlock
    #
    def __init__(self,pointer):
        self._pointer = pointer

    def __eq__(self, other):
        return self._pointer == other._pointer

    def get_name(self):
        return HXP_domain_get_name_(self._pointer)

    def set_name(self, new_name):
        rename_domain(HXP_domain_get_name_(self._pointer), new_name)

    def get_index(self):
        return HXP_domain_get_index_(self._pointer)

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_domain_get_box_(self._pointer)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])

    def get_rtz_box(self,axis = "Z",orig=Point(0,0,0)):
        iaxis = 0
        if axis=="Y": iaxis = 1
        if axis=="Z": iaxis = 2
        rmin,tmin,zmin,rmax,tmax,zmax = HXP_domain_get_rtz_box_(self._pointer,iaxis,orig.x,orig.y,orig.z)
        return BoxRTZ([rmin,rmax,tmin,tmax,zmin,zmax])

    def num_faces(self):
        l = HXP_domain_get_faces_(self._pointer)
        size = len(l)
        return size

    # Return list of faces by names, using unix style regular expression
    def get_faces_by_name(self,expr):
        faces = []

        name_regexp = fnmatch.translate( expr )
        
        pattern =  re.compile(name_regexp,re.IGNORECASE)

        for faceID in HXP_domain_get_faces_(self._pointer):
            name = HXP_face_get_name_(self._pointer, faceID )
            match =  pattern.search( name )
            if match:
                faces.append(DomainFace(self,faceID))
            
        return faces

    def get_faces(self,expr=""):
        faces = []
        if expr == "":
            for face in HXP_domain_get_faces_(self._pointer):
                faces.append(DomainFace(self,face))
        else:
            # face list using python regulation expression
            pattern =  re.compile(expr)

            for faceID in HXP_domain_get_faces_(self._pointer):
                name = HXP_face_get_name_(self._pointer, faceID )
                match =  pattern.search( name )
                if match:
                    faces.append(DomainFace(self,faceID))
            
        return faces

    def get_face(self,ID):
        if type(ID) is types.StringType:
            for faceID in HXP_domain_get_faces_(self._pointer):
                name = HXP_face_get_name_(self._pointer, faceID )
                if name == ID:
                    return  DomainFace(self,faceID)
            raise ValueError("Wrong face name",ID)
        else:
            return DomainFace(self,ID)

    def contains_face(self,face):
        if type(face) is types.StringType:
            for faceID in HXP_domain_get_faces_(self._pointer):
                name = HXP_face_get_name_(self._pointer, faceID )
                if name == face:
                    return 1
            return 0
        else:
            faceID = -1;
            if isinstance(face,DomainFace):
                faceID = face._id
            else:
                faceID = face
            blockId, faceIdx = HXP_get_block_face_topId_(self._pointer, faceID)
            if faceIdx == -1:
                return 0
            return 1

    def get_MIR_faces(self):
        _notsup("Domain::get_MIR_faces")
        faces = []
        for face in HXP_domain_get_faces_(self._pointer):
            type = HXP_face_get_bc_type_(0,face)
            if type == "MIR":
                faces.append(DomainFace(self,face))
        return faces

    def get_angle_between_edges_at_vertex(self, face, vertex):
        vertexID = -1;
        if isinstance(vertex,DomainVertex):
            vertexID = vertex._id
        else:
            vertexID = vertex
        faceID = -1;
        if isinstance(face,DomainFace):
            faceID = face._id
        else:
            faceID = face
        errCode, angle = HXP_face_get_angle_at_corner_(self.get_index(), faceID, vertexID)
        return angle

    def compute_number_of_divisions(self,baseH):
        _notsup("Domain::compute_number_of_divisions")
        box = self.get_xyz_box()
        return [ int(box.dx()/baseH) , int(box.dy()/baseH), int(box.dz()/baseH) ]

    def create_adaptation_group(self, name, faces ):
        idList = []
    
        for face in faces:
            if isinstance(face,DomainFace):
                idList.append( face._id )
            else:
                idList.append( face )
            
        HXP_create_adaptation_group_(self._pointer, name,len(idList),idList)
        
        return SurfaceAdaptationGroup( self , name )

    def delete_adaptation_group( self, name ):
        result = HXP_delete_adaptation_group_( self._pointer , name )
        return result

    def delete_all_adaptation_groups( self ):
        HXP_delete_all_adaptation_groups_( self._pointer )

    def get_adaptation_groups( self ):
        nameList = []
        all_groups = HXP_getAdaptPatchGroups_( self._pointer )
        for group in all_groups:
            nameList.append(group[0])
        return nameList

    def get_adaptation_group(self,name):
        return SurfaceAdaptationGroup( self , name )

    def num_adaptation_groups(self):
        return len( HXP_getAdaptPatchGroups_( self._pointer ) )

    def create_edge_adaptation_group(self, name, edges ):
        idList = []
    
        for edge in edges:
            if isinstance(edge,DomainEdge):
                idList.append( edge._id )
            else:
                idList.append( edge )
            
        HXP_create_edge_adaptation_group_(self._pointer, name,len(idList),idList)
        
        return EdgeAdaptationGroup( self , name )

    def get_edge_adaptation_group(self,name):
        return EdgeAdaptationGroup( self , name )

    def num_edge_adaptation_groups(self):
        return len( HXP_getEdgeAdaptGroups_( self._pointer ) )

    def get_size(self):
        _notsup("Domain::get_size")
        return HXP_domain_get_size_(self._pointer)

    def get_cartesian_mesh_params(self):
        _notsup2("Domain::get_cartesian_mesh_params")
        return HXP_get_cartesian_mesh_params_(self._pointer)

##  def init_cartesian_mesh(self,dx,dy,dz):
##      HXP_init_cartesian_mesh_(self._pointer,dx,dy,dz)

##  def init_cylindrical_mesh(self,nr,nt,nz,axis="Z",orig=Point(0,0,0),rmin = -1,rmax = -1,tmin = -1,tmax = -1):
##      iaxis = 0
##      if axis=="Y": iaxis = 1
##      if axis=="Z": iaxis = 2
##      HXP_init_cylindrical_mesh_(self._pointer,nr,nt,nz,iaxis,orig.x,orig.y,orig.z,rmin,rmax,tmin,tmax)
        
##  def init_mesh_from_file(self,filename):
##      HXP_init_mesh_from_file_(self._pointer,filename)

    def compute_ditances(self):
        _notsup("Domain::compute_ditances")
        HXP_domain_compute_distances_(self._pointer)

    def create_BC_group(self,name,typeName):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        typeI   = HXP_get_type_as_id_(typeName)

        HXP_create_BC_group_(blockId,name,typeI)

    def delete_BC_group(self,groupName):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        HXP_delete_BC_group_(blockId,groupId)

    # OBSOLETE: old implementation return face indices
    def get_BC_group_patches_idx(self,groupName):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        return HXP_set_BC_group_patches_(blockId,groupId)

    # return face objects in the specified BC group
    def get_BC_group_patches(self,groupName):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        grp_patch_ids = HXP_set_BC_group_patches_(blockId, groupId)
        domain_patches = self.get_faces()
        grp_patches = []
        for patch_id in grp_patch_ids:
            grp_patches.append(domain_patches[patch_id])
        return grp_patches

    def add_patch_to_BC_group(self,groupName,patchId):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        if groupId >= 0:
            HXP_add_patch_to_BC_group_(blockId,groupId,patchId)

    def remove_patch_from_BC_group(self,groupName,patchId):
        blockId, patch = HXP_get_block_face_topId_(self._pointer, patchId)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        if groupId >= 0:
            HXP_remove_patch_from_BC_group_(blockId,groupId,patch)

    def set_BC_group_name(self,groupName,name):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        HXP_set_BC_group_name_(blockId,groupId,name)

    def set_BC_group_type(self,groupName,typeName):
        blockId = HXP_get_domain_id_from_ptr_(self._pointer)
        groupId = HXP_get_BC_group_id_(blockId,groupName)
        typeI   = HXP_get_type_as_id_(typeName)
        
        HXP_set_BC_group_type_(blockId,groupId,typeI)

    def get_number_of_cells(self):
        return HXP_mesh_num_cells_( self._pointer )

    def get_mesh_bad_cells_count(self):
        return HXP_mesh_bad_cells_( self._pointer )

    def get_mesh_orthogonality(self):
        return HXP_mesh_orthogonality_( self._pointer )
    
    def get_mesh_aspect_ratio(self):
        return HXP_mesh_aspect_ratio_( self._pointer )
    
    def get_mesh_expansion_ratio(self):
        return HXP_mesh_expansion_ratio_( self._pointer )
    
    def get_mesh_skewness_range(self):
        return HXP_mesh_skewness_range_( self._pointer )
    
    def get_mesh_max_skewness(self):
        return HXP_mesh_max_skewness_( self._pointer )

    def get_mesh_volume_distribution(self):
        return HXP_mesh_volume_( self._pointer )

    def get_mesh_adjacent_volume_ratio(self):
        return HXP_mesh_adjacent_volume_ratio_( self._pointer )

    def get_mesh_equiangular_skewness(self):
        return HXP_mesh_equiangular_skewness_( self._pointer )

    def get_mesh_fluent_aspect_ratio(self):
        return HXP_mesh_fluent_aspect_ratio_( self._pointer )

    def get_mesh_fluent_orthogonality(self):
        return HXP_mesh_fluent_orthogonality_( self._pointer )

    def get_mesh_non_orthogonality(self):
        return HXP_mesh_marine_non_orthogonality_( self._pointer )

    def get_mesh_openfoam_non_orthogonality(self):
        return HXP_mesh_openfoam_non_orthogonality_( self._pointer )

    def split_face( self, face, x1, y1, z1, x2, y2, z2, smallEdgeLength, x3 = 1e37, y3 = 1e37, z3 = 1e37 ):
        id = get_face_id_( self._pointer , face )
        if id == -1:
            raise ValueError,face

        face1,face2 = HXP_split_face_( self._pointer , id, x1, y1, z1, x2, y2, z2, x3, y3, z3, smallEdgeLength )

        if face1 == -1 and face2 == -1:
            raise "Could not split face"

        return DomainFace( self , face1 ), DomainFace( self , face2 )

    def get_split_segment_length( self, face, corner):
        id = get_face_id_( self._pointer , face )
        if id == -1:
            raise ValueError,face

        lengthMax = 1e8
        errCode, x1, y1, z1, x2, y2, z2, optLength = HXP_get_split_points_( self.get_index(), id, corner, lengthMax )
        if errCode != 0 and errCode != 6:
            raise Exception("Could not detect split points for a face near corner")
        if optLength == lengthMax:
            raise Exception("Could not detect optimal value for the length parameter")
        return optLength

    def split_face_near_corner( self, face, corner, length ):
        id = get_face_id_( self._pointer , face )
        if id == -1:
            raise ValueError,face

        errCode, x1, y1, z1, x2, y2, z2, optLength = HXP_get_split_points_( self.get_index(), id, corner, length )
        #print "[split_face_near_corner] errcode: "+str(errCode)+" make cut "+str(x1)+" "+str(y1)+" "+str(z1)+" => "+str(x2)+" "+str(y2)+" "+str(z2)
        if errCode != 0:
            raise Exception("Could not detect split points for a face near corner")
        x3 = 1e37
        y3 = 1e37
        z3 = 1e37
        smallEdgeLength = 1e-10
        face1, face2 = HXP_split_face_( self._pointer , id, x1, y1, z1, x2, y2, z2, x3, y3, z3, smallEdgeLength )
        if face1 == -1 or face2 == -1:
            raise Exception("Could not split face near corner")
        domFace1 = DomainFace( self , face1 )
        domFace2 = DomainFace( self , face2 )
        if domFace1.contains_vertex(corner):
            return domFace1,domFace2
        else:
            return domFace2,domFace1

    def merge_faces(self,face1,face2,new_name = "",main_face = -1):
        id1 = get_face_id_( self._pointer , face1 )
        id2 = get_face_id_( self._pointer , face2 )

        if id1 == -1 or id2 == -1:
            return DomainFace( self , -1 )
        
        if main_face == 0 or main_face == 1:
            newFaceId = HXP_merge_faces_ext_( self._pointer, id1, id2, main_face )
        else:
            newFaceId = HXP_merge_faces_( self._pointer, id1, id2 )

        if new_name != "":
            HXP_set_face_name_( self.get_index(), newFaceId , new_name )

        return DomainFace( self , newFaceId )

    def merge_all_edges( self, featureAngle ):
        numSets = HXP_create_edge_merge_sets_( self._pointer , featureAngle )
        
        for i in range( numSets ):
            HXP_merge_edge_set_( self._pointer, i )

        HXP_clear_edge_merge_sets_( self._pointer )

    def create_VL_group(self,group_name,faces):
        idList = []
    
        for face in faces:
            if isinstance(face,DomainFace):
                idList.append( face._id )
            else:
                idList.append( face )
            
        HXP_create_VL_group_( self._pointer, group_name, len(idList), idList )

        return VLGroup( self , group_name )

    def get_VL_group(self,name):
        return VLGroup( self , name )

    def num_VL_groups(self):
        return len( HXP_getVLPatchGroups_( self._pointer ) )

    def get_failed_captured_edges(self):
        _notsup("get_failed_captured_edges")
        
        edges = []
        for iTopoEdge in get_failed_captured_edges_():
            edges.append( DomainEdge(self, HXP_edge_get_ID_( iTopoEdge ) ) )
        return edges

    def show_shading(self):
        _notsup("Domain::show_shading")
        #shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._pointer , -1 , 1 , 0 , 0 )

    def hide_shading(self):
        _notsup("Domain::hide_shading")
        #shade,tri,mesh = HXP_face_get_display_flags_( self._domain._pointer , self._id )
        HXP_face_set_display_flags_( self._pointer , -1 , 0 , 0 , 0 )

    def search_periodic_connections(self):
        block_name = self.get_name()
        if not is_batch() and is_faceViewer_opened():
            eval_tcl_string( "HexaPatchDialog:search_periodic_patches " + block_name )
        else:
            blockID = self.get_index()
            patches = HXP_get_periodic_patches_(block_name)
            tmpList = []
            for connection in patches:
                # HXP_get_block_face_topId_(self._pointer, connection[0])
                patchID1 = HXP_active_domain_get_faceId_(blockID, connection[0])
                patchID2 = HXP_active_domain_get_faceId_(blockID, connection[1])
                self.set_periodic_connection(patchID1, patchID2)
                # store internal indices for periodic patches
                tmpList.append(connection[0])
                tmpList.append(connection[1])
            # remove periodic patches from groups
            groupList = HXP_get_all_BC_groups_()
            toDeleteGrp = []
            for groupData in groupList:
                # groupData: { 0/1 groupID blockID }, first item value: 0 - patches, 1 - groups
                if groupData[0]==0 or groupData[2]!=blockID:
                    continue
                # process groups for self domain
                groupID = groupData[1]
                grp_patches = HXP_set_BC_group_patches_(blockID, groupID)
                grp_name = HXP_get_BC_group_name_(blockID, groupID)
                for patchID in grp_patches:
                    for periodicID in tmpList:
                        if patchID==periodicID:
                            HXP_remove_patch_from_BC_group_(blockID,groupID,patchID)
                            break
                grp_patches = HXP_set_BC_group_patches_(blockID, groupID)
                if len(grp_patches)==0:
                    toDeleteGrp.append(grp_name)
            # delete empty groups. 
            # empty groups should be deleted by name after processing to prevent renumbering
            for grpName in toDeleteGrp:
                self.delete_BC_group(grpName)

    def set_periodic_connection(self, patchID1, patchID2):
        block_name = self.get_name()
        HXP_set_periodic_connection_(block_name, patchID1, patchID2)
        self.get_face(patchID1).set_type("PER")
        self.get_face(patchID2).set_type("PER")

    # return number of edges in domain
    def num_edges(self):
        l = HXP_domain_get_edges_(self._pointer)
        size = len(l)
        return size

    # return list of edges in domain
    def get_edges(self,expr=""):
        edges = []
        for edge in HXP_domain_get_edges_(self._pointer):
            edges.append(DomainEdge(self,edge))
        return edges

    # return edge object with the specified ID
    def get_edge(self,ID):
        return DomainEdge(self,ID)

    # check if the domain has critical errors
    def has_critical_errors(self):
       return HXP_check_domain_errors_flag_(self) 

    # return 1 if domain contains specified edge object, 0 - otherwise
    def contains_edge(self, edge):
        edgeID = -1;
        if isinstance(edge,DomainEdge):
            edgeID = edge._id
        else:
            edgeID = edge

        idx = HXP_get_edge_index_by_id_(self.get_name(),edgeID)
        if idx == -1:
            return 0
        return 1

    # return edge object with the specified index [0..num_edges()]
    def get_edge_by_index(self,idx):
        id = HXP_get_edge_id_by_index_(self.get_name(), idx)
        if id == -1:
            raise Exception("Edge index is out of range [0.." + str(num_edges() - 1) + "]")
        else:
            return DomainEdge(self, id)

    # select edge (highlight in GUI)
    def select_edge(self, ID):
        HXP_select_edge_(self.get_index(), ID)

    def unselect_edge(self, ID):
        HXP_unselect_edge_(self.get_index(), ID)

    def get_number_of_edge_points(self, ID):
        return HXP_number_points_in_edge_(self.get_index(), ID)

#--------------------------------------------------------------------------------------------#

def get_domain_faces_with_holes():
    ids = HXP_getSurfacesWithHoles_()
    faces = []
    for id in ids:
        faces.append(DomainFace(get_active_domain() , id))
    return faces

def get_holes_bbox():
    return HXP_getHoleBbox_()

def get_face_bbox(faceID):
    return HXP_getFaceBbox_(faceID)

#--------------------------------------------------------------------------------------------#

def get_common_edges( refFace, otherFaces ):

    if not isinstance(refFace,DomainFace):
        raise ValueError("",refFace)

    faces = otherFaces
    if isinstance(otherFaces,DomainFace):
        faces = [otherFaces]
        
    all_edges = []

    for face in faces:
        edges = face.get_common_edges( refFace )
        for e in edges:
            all_edges.append( e )
        
    return all_edges

#--------------------------------------------------------------------------------------------#

def split_edge(edgeId,x,y,z,smallEdgeLength):
    return HXP_split_edge_(edgeId,x,y,z,smallEdgeLength)

def merge_edges(vertexId):
    return HXP_merge_edges_(vertexId)

def split_face(faceId,x1,y1,z1,x2,y2,z2,smallEdgeLength,x3 = 1e37,y3 = 1e37,z3 = 1e37):
    face1,face2 = HXP_split_face_(faceId,x1,y1,z1,x2,y2,z2,x3,y3,z3,smallEdgeLength)
    return DomainFace( get_active_domain() , face1), DomainFace( get_active_domain() , face2)

def merge_faces(face1,face2):
    id1 = get_face_id_( get_active_domain()._pointer , face1 )
    if id1 == -1:
        raise Exception("Cannot merge faces: the first face is wrong")

    id2 = get_face_id_( get_active_domain()._pointer , face2 )
    if id2 == -1:
        raise Exception("Cannot merge faces: the second face is wrong")

    return DomainFace( get_active_domain() , HXP_merge_faces_(id1,id2) )

#--------------------------------------------------------------------------------------------#

def merge_face_list( list_of_faces , name = "" ):

    if len(list_of_faces) == 0:
        return

    facesIds = []

    if type( list_of_faces[0] ) is types.IntType:
        facesIds = list_of_faces
        domain0  = get_active_domain()
    else:
        face0   = list_of_faces[0]
        domain0 = face0._domain
    
        facesIds = []

        for face in list_of_faces:

            if face._domain != domain0:
                raise "Cannot merge faces belonging to different domains"

            if not face._id in facesIds:            
                facesIds.append( face._id )

    HXP_merge_face_list_cmd_( domain0._pointer , len(facesIds) , facesIds , name )

#--------------------------------------------------------------------------------------------#

def merge_edge_list( list_of_edges , name = "" ):

    if len(list_of_edges) == 0:
        return

    edgesIds = []

    if type( list_of_edges[0] ) is types.IntType:
        edgesIds = list_of_edges
        domain0  = get_active_domain()
    else:
        edge0   = list_of_edges[0]
        domain0 = edge0._domain
    
        edgesIds = []

        for edge in list_of_edges:

            if edge._domain != domain0:
                raise "Cannot merge edges belonging to different domains"

            if not edge._id in edgesIds:            
                edgesIds.append( edge._id )

    HXP_merge_edge_list_cmd_( domain0._pointer , len(edgesIds) , edgesIds , name )

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
# private function

def get_domain_ptr_(inp):
    # inp can be either:
    #   the name of a the domain,   --> return its pointer
    #   the string "ALL"        --> return 0
    #   an object of type Domain    --> return its pointer
    
    if isinstance(inp,Domain):
        return self._pointer

    domainPtr = 0           # 0 means either n
    if inp != "ALL":
        domainPtr = HXP_get_domain_by_name_(inp)
    return domainPtr

#--------------------------------------------------------------------------------------------#

def domain(name):
    dom_ptr =  HXP_get_domain_by_name_(name)

    if dom_ptr == 0:
        raise "Wrong Domain name : " + name

    return Domain( dom_ptr )

#--------------------------------------------------------------------------------------------#

def get_active_domain():
    return Domain(HXP_get_active_domain_pointer_())

#--------------------------------------------------------------------------------------------#

def get_active_domain_name():
    d =  Domain(HXP_get_active_domain_pointer_())
    return d.get_name()

#--------------------------------------------------------------------------------------------#

def set_active_domain(domain):
    # domain can either a string (the name of the Domain) or an object of type Domain

    name = domain 
    if isinstance(domain,Domain):
        name = domain.get_name()
        
    if not is_batch():
        eval_tcl_string( "hexa_set_active_block " + name )

    else:
        HXP_set_active_domain_(name)

#--------------------------------------------------------------------------------------------#

def rename_domain(src_domain_name, new_domain_name):
    isOk = HXP_set_block_name_(src_domain_name, new_domain_name)
    if not is_batch() and isOk != 0 :
        eval_tcl_string( "hexa_rename_domain:update_gui {" + src_domain_name + "} {" + new_domain_name + "}" )

#--------------------------------------------------------------------------------------------#
# return Domain Face using its faceID , from active domain

def domain_face(faceID):
    return DomainFace(get_active_domain(),faceID)

#--------------------------------------------------------------------------------------------#

def delete_internal_surface(dom, faceID):
    blockID = 0
    if type(dom) is types.IntType:
        blockID = dom
    elif type(dom) is types.StringType:
        blockID = domain(dom).get_index()
    elif isinstance(dom,Domain):
        blockID = dom.get_index()

    HXP_delete_internal_surface_(blockID, faceID)

#--------------------------------------------------------------------------------------------#
# return DomainEdge using its Edge ID , from active domain

def domain_edge(edgeID):
    return DomainEdge(get_active_domain(),edgeID)

#--------------------------------------------------------------------------------------------#

def get_all_domains():
    domains = []

    all = HXP_get_all_domains_()    # pointers

    for dom in all:
        domains.append(Domain(dom))
    return domains

#--------------------------------------------------------------------------------------------#

def get_active_domain():
    ptr = HXP_get_active_domain_pointer_()

    if ptr == 0:
        raise Exception("No active Domain")
        
    return Domain( HXP_get_active_domain_pointer_() )

#--------------------------------------------------------------------------------------------#

def print_domain(d,file):
    file.write("Domain %s \n" % (d.get_name()))
    file.write(" Number of faces %d \n" % (d.num_faces()))
    i = 0
    for face in d.get_faces():
        file.write("\t Face %d \n" % (i))
        file.write("\t Nb Edges, Nb Loops, Nb Triangles =  %d, %d, %d \n" % (face.num_edges(),face.num_loops(),face.num_triangles()))
        i = i + 1

#--------------------------------------------------------------------------------------------#

def print_domain_all(d,file):
    file.write("Domain %s \n" % (d.get_name()))
    file.write(" Number of faces %d \n" % (d.num_faces()))
    i = 0
    for face in d.get_faces():
        file.write("\t Face %d %s \n" % (i, face.get_name() ) )
        file.write("\t Nb Edges, Nb Loops, Nb Triangles =  %d, %d, %d \n" % (face.num_edges(),face.num_loops(),face.num_triangles()))

        j = 0
        for edge in face.get_edges():
            file.write("\t\t Edge %d \n" % (j))
            file.write("\t\t     Length %f \n" % (edge.get_length() ))
            
            j = j + 1

        j = 0
        for loop in face.get_loops():
            file.write("\t\t Loop %d \n" % (j))
            file.write("\t\t     Number of edges %d \n" % ( len(loop) ) )
            
            j = j + 1
            
        i = i + 1

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def init_cartesian_mesh(nr,nt,nz):
    HXP_init_cartesian_mesh_(nr,nt,nz)

def init_cylindrical_mesh(nr,nt,nz,
              axis = "Z",
              orig = Point(0,0,0),
              rmin = -1,rmax = -1,tmin = -1,tmax = -1, mode = 0):
    iaxis = 0
    if axis == "Y": iaxis = 1
    if axis == "Z": iaxis = 2
    HXP_init_cylindrical_mesh_(nr,nt,nz,iaxis,orig.x,orig.y,orig.z,rmin,rmax,tmin,tmax,mode)

def init_mesh_from_file(filename):
    HXP_init_mesh_from_file_(filename)

#--------------------------------------------------------------------------------------------#

log10_05 = math.log10(0.5)

def compute_number_of_required_refinements(start_size,target_size):
    n =  (1 + int(math.log10(target_size/start_size)/log10_05) )
    if n<0: n = 0
    return n
    
    
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
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#

#def set_global_adaptation_params(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef):
#   
#   HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef)

#--------------------------------------------------------------------------------------------#

def set_global_number_of_refinements(num_refinement):
    
    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(num_refinement,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def get_global_number_of_refinements():
    
    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    return maxRef

#--------------------------------------------------------------------------------------------#

def set_advanced_global_parameters(diffusion,minSize,maxSize,maxAR,nbCellsInGap):
    
    maxRef,d,minS,maxS,mxAR,nbcg,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def set_num_refinement_diffusion(new_num_diffusion):
    
    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,new_num_diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def set_number_of_cells_in_gaps(nb_cell_gap):
    
    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nb_cell_gap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def set_prevent_exterior_cells_refinement(prevent_ext_refinement):

    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,prevent_ext_refinement,isoRefInCorners,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def set_isotropic_refinement_in_corners(isotropic_refinement):

    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isotropic_refinement,blankByDistance,dentCellCorrection)

#--------------------------------------------------------------------------------------------#

def set_trimming_by_distance(blank_by_distance):

    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blank_by_distance,dentCellCorrection)


#--------------------------------------------------------------------------------------------#

def set_iterative_dent_cell_correction(iterative_dent_cell_correction):

    maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,dentCellCorrection = HXP_get_global_adaptation_params_()
    
    HXP_set_global_adaptation_params_(maxRef,diffusion,minSize,maxSize,maxAR,nbCellsInGap,preventExtRef,isoRefInCorners,blankByDistance,iterative_dent_cell_correction)


#--------------------------------------------------------------------------------------------#
# enable or disable adaptation . value is boolean type

def enable_refinement(value):
    refinement,trimming = HXP_get_refinement_trim_flags_()
    HXP_set_refinement_trim_flags_(value,trimming)

#--------------------------------------------------------------------------------------------#
# enable or disable trimming . value is boolean type

def enable_trimming(value):
    refinement,trimming = HXP_get_refinement_trim_flags_()
    HXP_set_refinement_trim_flags_(refinement,value)

#--------------------------------------------------------------------------------------------#
# enable or disable refinement . value is boolean type

def enable_snapping(value):
    HXP_enable_snapping_(value)

def enable_buffer_on_faces_not_used_for_trimming(value):
    HXP_enable_buffer_on_faces_not_used_for_trimming_(value)

#----------------------------------------------------------------------------------------------

# enable or disable buffer insertion.
# bufferA - value is boolean type (0 or 1)
# bufferB - value is boolean type (0 or 1)
# nbSmoothingIterations - non negative integer value.
# Smoothing disabled if the parameter is 0
def set_buffer_insertion_parameters(bufferA, bufferB, nbSmoothingIterations = 25):
    useSmoothing = 1
    if nbSmoothingIterations <= 0:
        useSmoothing = 0
    HXP_setBufferInsertionParameters(bufferA, bufferB, useSmoothing, nbSmoothingIterations)

#----------------------------------------------------------------------------------------------

# 0 - insert buffer type I for all layer
# 1 - insert buffer type I for curves only
def set_buffer_insertion_mode(value):
    HXP_setBufferInsertionMode(value)

#--------------------------------------------------------------------------------------------#

def enable_optimization(value):
    HXP_enable_optimization_(value, value)

def set_optimization_params(relaxInvalidFlag, 
                nbExtIterMax, invalidCellsMax, nbFinalOptimizeIterations,
                finalOptimizePercent,nbUnflatIterations, minOrthogonality):
    
    HXP_set_optimization_params_(relaxInvalidFlag, 
                     nbExtIterMax, invalidCellsMax, nbFinalOptimizeIterations,
                     finalOptimizePercent,nbUnflatIterations, minOrthogonality)

#--------------------------------------------------------------------------------------------#
#                               Viscous layer functions
#--------------------------------------------------------------------------------------------#

def set_viscous_layers_global_params(inflateFlag,fixedNbLayer,minNbLayer,maxNbLayer,inflateFactor,
                                     fixedFirstLayerFlag = 1, nbFinalOptiIterations = 5,
                                     finalOptiPercent = 3.0, nbUnflatIterations = 0, minOrthogonality = 10.0, snapNewVertices = 0):

    d0,insertFlag,d1,d2,d3,d4,maxInc,maxDec,nL,d5,tol,fS,fV,sav,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14 = HXP_get_VL_global_params_()

    HXP_set_VL_global_params_(fixedFirstLayerFlag, insertFlag, inflateFlag,
                              fixedNbLayer,minNbLayer, maxNbLayer,
                              maxInc, maxDec,nL,inflateFactor, tol,fS, fV,sav,t1,t2,t3,t4,t5,t6,t7,t8,
                              nbFinalOptiIterations, finalOptiPercent, nbUnflatIterations, minOrthogonality, snapNewVertices)

def get_viscous_layers_global_params():

    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25,t26,t27,t28 = HXP_get_VL_global_params_()
    # t1  - fixedFirstLayerFlag
    # t3  - inflateFlag
    # t4  - fixedNbLayer
    # t5  - minNbLayer
    # t6  - maxNbLayer
    # t10 - inflateFactor
    # auxiliary predefined parameters
    # t23 - nbFinalOptiIterations ==    5
    # t24 - finalOptiPercent      ==  3.0
    # t25 - nbUnflatIterations    ==    0
    # t26 - minOrthogonality      == 10.0
    # t27 - snapNewVertices       ==    0
    return t3,t4,t5,t6,t10,t1,t23,t24,t25,t26,t27

#--------------------------------------------------------------------------------------------#

# 1 - use separate inflation ratio for every patch (advanced mode)
# 0 - use common ratio for inflation (regular mode)
def set_viscous_layers_inflation_mode(mode):

    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25,t26,t27,t28 = HXP_get_VL_global_params_()
    HXP_set_VL_global_params_(t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25,t26,t27,mode)

def get_viscous_layers_inflation_mode():
    t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25,t26,t27,t28 = HXP_get_VL_global_params_()
    return t28

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#               Mesh generation functions                                                    #
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def set_mesh_generation_mode(mode):
    imode = 0
    if   mode == "2D": imode = 1
    elif mode == "3D": imode = 0
    else:
        raise "Invalid mesh generation mode. MUST be \"2D\" or \"3D\""

    HXP_set_mesh_generation_mode_(imode)

    if not is_batch():
        eval_tcl_string( "hexa_configdimmode_buttons" )

#--------------------------------------------------------------------------------------------#

def get_mesh_generation_mode():
    mode = "3D"

    if HXP_get_mesh_generation_mode_() == 1:
        mode = "2D"

    return mode

#--------------------------------------------------------------------------------------------#

def delete_mesh():
    if not is_batch():
           eval_tcl_string("hexa_init_mesh:delete_silent")
           eval_tcl_string("hexa_mesh_wizard:initializeMarks")
    else:
        HXP_importMeshIfNeeded_()
    
        HXP_open_domain_step_("init")
        HXP_delete_mesh_()
    
        HXP_setGeneralStatus_(get_active_domain_name(),"INITIAL_MESH","UNCHECKED")
        HXP_setGeneralStatus_(get_active_domain_name(),"ADAPTATION","UNCHECKED")
        HXP_setGeneralStatus_(get_active_domain_name(),"SNAPPING","UNCHECKED")
        HXP_setGeneralStatus_(get_active_domain_name(),"SMOOTHING","UNCHECKED")
        HXP_setGeneralStatus_(get_active_domain_name(),"VISCOUS_LAYER_INSERTION","UNCHECKED")
        HXP_setGeneralStatus_(get_active_domain_name(),"PARTITION","UNCHECKED")


#--------------------------------------------------------------------------------------------#

def generate_initial_mesh():

    HXP_importMeshIfNeeded_()

    # Enable initial mesh generation before proceeding
    HXP_setGeneralStatus_(get_active_domain_name(),"INITIAL_MESH","CHECKED")

    # Initial mesh generation
    status = HXP_generate_initial_mesh_()

    # Status==0 means succeded. Otherwise failed
    if status=="0":
        eval_tcl_string("hexa_init_mesh:update 0")
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_green init")

        HXP_setGeneralStatus_(get_active_domain_name(),"INITIAL_MESH","COMPLETED")

        HXP_save_mesh_step_("init")
    else:
        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_red init")

        HXP_setGeneralStatus_(get_active_domain_name(),"INITIAL_MESH","FAILED")
        
    return status

#--------------------------------------------------------------------------------------------#

def adapt_mesh():       # works on active block

    HXP_importMeshIfNeeded_()

    # Enable adaptation mesh generation before proceeding
    HXP_setGeneralStatus_(get_active_domain_name(),"ADAPTATION","CHECKED")

    # Update size distributions before proceeding to adaptation
    updateSizeDistri_()

    # Perform adaptation
    status = HXP_adapt_mesh_()

    # Status==0 means succeded. Otherwise failed
    if status=="0":
        # Update 3D Graphics
        eval_tcl_string("hexa_adapt_mesh:update 0")

        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_green adapt")

        # Update internal generation status to COMPLETED
        HXP_setGeneralStatus_(get_active_domain_name(),"ADAPTATION","COMPLETED")

        HXP_save_mesh_step_("adapt")
    else:
        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_red adapt")

        HXP_setGeneralStatus_(get_active_domain_name(),"ADAPTATION","FAILED")

        #raise RuntimeError,"Adaptation failed "
        
    return status

#--------------------------------------------------------------------------------------------#

def snap_mesh():

    HXP_importMeshIfNeeded_()

    # Enable adaptation mesh generation before proceeding
    HXP_setGeneralStatus_(get_active_domain_name(),"SNAPPING","CHECKED")
        
    # Init tcl GUI part
    eval_tcl_string("hexa_snap_mesh:get_global_param")

    # Perform snapping
    status = HXP_snap_mesh_()

    if status=="0":
        # Update 3D Graphics
        eval_tcl_string("hexa_snap_mesh:update 0")

        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_green snap")

        # Update internal generation status to COMPLETED
        HXP_setGeneralStatus_(get_active_domain_name(),"SNAPPING","COMPLETED")
    
        HXP_save_mesh_step_("snap")
    else:
        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_red snap")

        # Update internal generation status to FAILED
        HXP_setGeneralStatus_(get_active_domain_name(),"SNAPPING","FAILED")

        #raise RuntimeError,"Snapping failed "
        
    return status

#--------------------------------------------------------------------------------------------#

def regularize_mesh():

    HXP_importMeshIfNeeded_()

    # Enable optimization mesh generation before proceeding
    HXP_setGeneralStatus_(get_active_domain_name(),"SMOOTHING","CHECKED")
    
    # Perform optimization
    status = HXP_regularize_mesh_()

    if status=="0":
        # Update 3D Graphics
        eval_tcl_string("hexa_regularize_mesh:update 0")

        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_green regularize")

        # Update internal generation status to COMPLETED
        HXP_setGeneralStatus_(get_active_domain_name(),"SMOOTHING","COMPLETED")
    
        HXP_save_mesh_step_("regularize")
    else:
        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_red regularize")

        # Update internal generation status to FAILED
        HXP_setGeneralStatus_(get_active_domain_name(),"SMOOTHING","FAILED")

        #raise RuntimeError,"Optimization failed "

    return status

#--------------------------------------------------------------------------------------------#

def insert_viscous_layers():

    HXP_importMeshIfNeeded_()

    # Enable VL mesh generation before proceeding
    HXP_setGeneralStatus_(get_active_domain_name(),"VISCOUS_LAYER_INSERTION","CHECKED")

    # Perform VL insertion
    status = HXP_insert_viscous_layer_()

    if status=="0":
        # Update 3D Graphics
        eval_tcl_string("hexa_snap_mesh:update 0")

        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_green viscous_layer")

        # Update internal generation status to COMPLETED
        HXP_setGeneralStatus_(get_active_domain_name(),"VISCOUS_LAYER_INSERTION","COMPLETED")
    
    else:
        # Update tcl GUI part
        eval_tcl_string("hexa_mesh_wizard:flag_action_as_red viscous_layer")

        # Update internal generation status to FAILED
        HXP_setGeneralStatus_(get_active_domain_name(),"VISCOUS_LAYER_INSERTION","FAILED")

        #raise RuntimeError,"Viscous layers insertion failed "
    
    return status

#--------------------------------------------------------------------------------------------#

# explicit loading the mesh
def load_mesh():

    if not is_batch():
        eval_tcl_string("hexa_importMeshIfNeeded")
    else:
        HXP_importMeshIfNeeded_()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_number_of_negative_cells():
    return len(get_negative_cells_center_())

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
#--------------------------------------------------------------------------------------------#
# Currently work on active block

def create_adaptation_group(group_name,faces):

    idList = []
    
    for face in faces:
        if isinstance(face,DomainFace):
            idList.append( face._id )
        else:
            idList.append( face )
            
    HXP_create_adaptation_group_(get_active_domain()._pointer, group_name,len(idList),idList)

#--------------------------------------------------------------------------------------------#

def delete_adaptation_group(group_name):
    HXP_delete_adaptation_group_(get_active_domain()._pointer, group_name)

#--------------------------------------------------------------------------------------------#

def delete_all_adaptation_groups():
    HXP_delete_all_adaptation_groups_(get_active_domain()._pointer)

#--------------------------------------------------------------------------------------------#

def get_all_adaptation_groups():
    _notsup("get_all_adaptation_groups")
    print HXP_getAdaptPatchGroups_( get_active_domain()._pointer )

#--------------------------------------------------------------------------------------------#

def create_edge_adaptation_group(group_name,curves):
    get_active_domain().create_edge_adaptation_group(group_name,curves)

def delete_all_edge_adaptation_groups():
    HXP_delete_all_edge_adaptation_groups_()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

# types of refinement boxes
BOX    = 0
SECTOR = 1

def get_normal_by_direction(dir_id):
    norm = [0,0,0]
    if dir_id > 2 :
        # Z - default axis
        dir_id = 2
    norm[dir_id] = 1
    return norm

class RefinementBox:
    def __init__(self,id):
        self._id = id

    def get_shape_type(self):
        return HXP_get_box_type_(self._id)

    def get_sector_parameters(self):
        axis,originX,originY,originZ,radiusMin,radiusMax,angleStart,angleEnd,height = HXP_get_sector_parameters_(self._id)
        norm   = get_normal_by_direction(axis)
        origin = [originX,originY,originZ]
        return norm,origin,radiusMin,radiusMax,angleStart,angleEnd,height

    def get_xyz_box(self):
        if HXP_get_box_type_(self._id) == BOX :
            xmin,ymin,zmin,xmax,ymax,zmax = HXP_get_cube_parameters_(self._id)
            return Box([xmin,xmax,ymin,ymax,zmin,zmax])
        else:
            axis,originX,originY,originZ,radiusMin,radiusMax,angleStart,angleEnd,height = HXP_get_sector_parameters_(self._id)
            # set default values: Z axis
            xmin = originX - radiusMax
            xmax = originX + radiusMax
            ymin = originY - radiusMax
            ymax = originY + radiusMax
            zmin = originZ
            zmax = originZ + height
            if axis == 0 :
                # X
                xmin = originX
                xmax = originX + height
                zmin = originZ - radiusMax
                zmax = originZ + radiusMax
            elif axis == 1 :
                # Y
                ymin = originY
                ymax = originY + height
                zmin = originZ - radiusMax
                zmax = originZ + radiusMax
            return Box([xmin,xmax,ymin,ymax,zmin,zmax])

    def get_cube_parameters(self):
        return HXP_get_cube_parameters_(self._id)

    def get_box_state(self):
        active,volumic = HXP_get_box_state_(self._id)
        return active

    def get_transformation(self):
        matrix = []
        # get transformation coefficients and return as transformation matrix
        coefs = HXP_get_ref_box_transformation_(self._id)
        matrix.append([coefs[0], coefs[1], coefs[2], coefs[3]]);
        matrix.append([coefs[4], coefs[5], coefs[6], coefs[7]]);
        matrix.append([coefs[8], coefs[9], coefs[10], coefs[11]]);
        #matrix.append([0, 0, 0, 1]);
        return matrix

    def disable(self):
        HXP_set_box_adapation_flag_(self._id,0,1)

    def set_adaptation_flags(self,active,volumic):
        HXP_set_box_adapation_flag_(self._id,active,volumic)

    def set_position(self,xmin,ymin,zmin,xmax,ymax,zmax):
        HXP_set_box_position_(self._id,xmin,ymin,zmin,xmax,ymax,zmax)

    def set_target_size(self,x,y,z):
        HXP_set_box_target_size_(self._id,x,y,z)

    def set_refinement_level(self,n):
        max_ref,max_aspect_ratio = get_box_adapation_parameters_(self._id)
        HXP_set_box_parameters_(self._id,n,max_aspect_ratio)

    def set_max_aspect_ratio(self,n):
        max_ref,max_aspect_ratio = get_box_adapation_parameters_(self._id)
        HXP_set_box_parameters_(self._id,max_ref,n)

    def set_diffusion_depth(self,depth):
        HXP_set_box_diffusion_depth_(self._id,depth)

    def set_transformation(self, matrix):
        coefs = matrix[0] + matrix[1] + matrix[2]
        HXP_set_ref_box_transformation_(self._id, coefs)

#--------------------------------------------------------------------------------------------#

def create_refinement_cube(xmin,ymin,zmin,xmax,ymax,zmax):
    id = HXP_create_refinement_cube_(xmin,ymin,zmin,xmax,ymax,zmax)
    return RefinementBox(id)
 
def create_refinement_sector(axis,originX,originY,originZ,radiusMin,radiusMax,angleStart,angleEnd,height):
    id = HXP_create_refinement_sector_(axis,originX,originY,originZ,radiusMin,radiusMax,angleStart,angleEnd,height)
    return RefinementBox(id)

#--------------------------------------------------------------------------------------------#

def get_number_of_refinement_boxes():
    return HXP_get_number_of_ref_boxes_()

#--------------------------------------------------------------------------------------------#

def delete_refinement_box(id):
    HXP_delete_refinement_box_(id)

#--------------------------------------------------------------------------------------------#

def delete_all_refinement_boxes():
    HXP_delete_all_refinement_boxes_()

#--------------------------------------------------------------------------------------------#

def refinement_box(id):
    return RefinementBox(id)

#--------------------------------------------------------------------------------------------#

def save_mesh_step(step):
    HXP_save_mesh_step_(step)
    
#--------------------------------------------------------------------------------------------#

def open_mesh_step(step):
        try:
                HXP_open_domain_step_(step)
                HXP_open_mesh_step_(step)
        except:
                pass
        if not is_batch():
                eval_tcl_string("Hexa:Project:GetMeshStatus [hexa_getActiveBlock]")
                eval_tcl_string("hexa_mesh_wizard:initializeMarks")
                eval_tcl_string("hexa_drawScene [hexa_getActiveBlock]")

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#                       Active Surface Manipulations (only in interactive mode)
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#

def is_surf_adaptation_opened():
    return eval_tcl_string( "hexa_targetSizeBySurface:is_opened") == "1"

#--------------------------------------------------------------------------------------------#

def is_faceViewer_opened():
    return eval_tcl_string( "HexaPatchDialog:is_opened") == "1"

#--------------------------------------------------------------------------------------------#

def cursor_wait():
    eval_tcl_string( "hexa_modify_cursor \"wait\" ")

#--------------------------------------------------------------------------------------------#

def cursor_normal():
    eval_tcl_string( "hexa_modify_cursor \"normal\" " )

#--------------------------------------------------------------------------------------------#

def get_selected_faces():

    if is_batch():
        raise "get_selected_faces cannot be used in batch mode"
    
    faces = []
    
    info = HXP_getActiveSurfaceList_()

    for d in info:
        domain = Domain(d[0])

        for f in d[1]:
            faces.append( DomainFace(domain,f) )

    return faces

#--------------------------------------------------------------------------------------------#
# Add the input faces to the current surface selection (used in the BC & Face Viewer dialogoe boxes)

def add_faces_to_selection( infaces ):

    if is_surf_adaptation_opened():
        add_faces_to_surf_adapt_selection( infaces )
    else:
        add_faces_to_faceViewer_selection( infaces )

#--------------------------------------------------------------------------------------------#

def clear_face_selection():

    if is_surf_adaptation_opened():
        clear_surf_adapt_selection()
    else:
        clear_faceViewer_selection()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def clear_faceViewer_selection():

    if is_batch():
        raise "HXP.clear_faceViewer_selection cannot be used in batch mode"

    HXP_clearActiveSurfaceList_()       # clear selected surfaces & update  graphics

    if is_faceViewer_opened():         # update dialogue box selection
        eval_tcl_string( "HexaPatchDialog:unselect_all_entries" )

#--------------------------------------------------------------------------------------------#

def add_faces_to_faceViewer_selection( infaces ):
    
    if is_batch():
        raise "HXP.add_faces_to_faceViewer_selection cannot be used in batch mode"

    if len( infaces ) == 0:
        return

    is_dialogue_open = is_faceViewer_opened()

    if is_dialogue_open:
        eval_tcl_string( "HexaPatchDialog:storeForUndo")

    faces  = []
    domain = infaces[0]._domain
    
    for face in infaces:
        #    face.set_color("yellow")
        #    face.set_name("lulu")
        #    face.show_shading()

        faces.append( face._id )

        bI,fI = HXP_get_block_face_topId_( domain._pointer , face._id )

        if is_dialogue_open and not is_batch():
            eval_tcl_string( "HexaPatchDialog:select_entry_python  " + str(bI) + " " + str(fI) )

    HXP_setActiveSurfaceList_( domain._pointer , len( faces ) , faces )

    if is_dialogue_open and not is_batch():
        eval_tcl_string( "hexa_bc:setSelectSurfacesFromHideFlag" )
        eval_tcl_string( "hexa_bc:redraw_all_selected_surfaces " )
        eval_tcl_string( "HexaPatchDialog:changeWidgetState " )

#--------------------------------------------------------------------------------------------#

def remove_face_from_faceViewer_selection( infaces ):

    _notsup2("remove_face_from_faceViewer_selection")
    
    if len( infaces ) == 0:
        return

    if is_batch():
        raise "HXP.remove_face_from_selection cannot be used in batch mode"

    is_dialogue_open = is_faceViewer_opened()

    faces  = get_selected_faces()
    domain = infaces[0]._domain
    
    for face in infaces:

        bI,fI = HXP_get_block_face_topId_( domain._pointer , face._id )

        eval_tcl_string( "HexaPatchDialog:unselect_entry_python  " + str(bI) + " " + str(fI) )

        faces.remove( face )

    HXP_setActiveSurfaceList_( domain._pointer , len( faces ) , faces )

    if is_dialogue_open and not is_batch():
        eval_tcl_string( "surface_tool:unselect_all_surfaces")
        eval_tcl_string( "hexa_bc:setSelectSurfacesFromHideFlag" )
        eval_tcl_string( "hexa_bc:redraw_all_selected_surfaces " )

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
# Add the input faces to the current surface selection (used in the BC & Face Viewer dialogoe boxes)

def add_faces_to_surf_adapt_selection( infaces ):

    if len( infaces ) == 0:
        return

    if is_batch():
        raise "HXP.add_faces_to_surf_adapt_selection cannot be used in batch mode"

    if not is_surf_adaptation_opened():
        raise "HXP.add_faces_to_selection cannot be used while dialogue box  is closed"
        
    # ... Update parameters for previously selected patches
    eval_tcl_string( "hexa_targetSizeBySurface:updateParameters" )
    
    eval_tcl_string( "hexa_targetSizeBySurface:buildPatch2HlistMap" )

    faces  = []
    domain = infaces[0]._domain
    
    for face in infaces:
        faces.append( face._id )

        bI,fI = HXP_get_block_face_topId_( domain._pointer , face._id )

        eval_tcl_string( "hexa_targetSizeBySurface:select_entry_python  " + str(bI) + " " + str(fI) )

    eval_tcl_string("hexa_targetSizeBySurface:displayParametersForCurrentSelection")

            #    HXP_setActiveSurfaceList_( domain._pointer , len( faces ) , faces )

    eval_tcl_string("hexa_targetSizeBySurface:update_after_selection")
    eval_tcl_string("hexa_targetSizeBySurface:highlightSelectedPatches")

#--------------------------------------------------------------------------------------------#

def clear_surf_adapt_selection():

    if is_batch():
        raise "HXP.clear_surf_adapt_selection cannot be used in batch mode"

    if is_surf_adaptation_opened():         # update dialogue box selection
        eval_tcl_string( "hexa_targetSizeBySurface:unselect_all_entries" )

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class FNMB:
    def __init__(self,iname):
        self.name = iname

    def get_name(self):
        return self.name

    def set_name(self,name):
        HXP_set_fnmb_name_( self.name , name )
        self.name = name
        
    def get_type(self):
        return HXP_get_fnmb_type_(self.name)

    def set_type(self,type):
        if type != "Rotor/stator" and type != "Full non matching":
            raise ValueError('Wrong fnmb type. Must be: "Rotor/stator" or "Full non matching"',type)
    
        HXP_set_fnmb_type_(self.name,type)

    def get_parameters(self):
        max_proj,min_proj,nb_iter,is_periodic,periodicity_idx,nb_repet,is_reversed,vertex_tol,tol2 = HXP_get_fnmb_parameters_(self.name);

        return max_proj,min_proj,nb_iter,is_periodic,periodicity_idx,nb_repet,is_reversed,vertex_tol
    
    def set_parameters(self,max_proj_dist,min_proj_dist,nb_iter,is_periodic,periodicity_idx,nb_repet,is_reversed,vertex_tol):
        
        HXP_set_fnmb_parameters_(self.name,max_proj_dist,min_proj_dist,nb_iter,is_periodic,periodicity_idx,nb_repet,is_reversed,vertex_tol)

    def get_left_patches(self):
        return get_fnmb_left_patches_(self.name)

    def get_right_patches(self):
        return get_fnmb_right_patches_(self.name)

    def is_same_as(self,fnmb):
        _notsup("FNMB::is_same_as")
        this_left  = self.get_left_patches()
        other_left = fnmb.get_left_patches()

        this_right  = self.get_right_patches()
        other_right = fnmb.get_right_patches()

        if(len(this_left)==len(other_left) and
           len(this_right)==len(other_right)):
            pass

    def enable_rs_correction(self,value):
        HXP_set_rs_correction_(self.name,value)


#--------------------------------------------------------------------------------------------#

def get_block_fnmbs(block_name):
    fnmbs = get_block_fnmbs_(block_name)
    
    fnmb_list = []

    for fnmb in fnmbs:
        name = get_fnmb_name_(fnmb)
        fnmb_list.append(name)

    return fnmb_list

#--------------------------------------------------------------------------------------------#

def search_all_fnmbs(search_rs = 0):
    HXP_search_all_fnmbs_adt_(search_rs)

#--------------------------------------------------------------------------------------------#

def compute_fnmb(fnmb):
    
    name = fnmb 
    if isinstance(fnmb,FNMB):
        name = fnmb.get_name()
        
    HXP_fnmb_compute_(name)

#--------------------------------------------------------------------------------------------#

def get_all_fnmbs():
    fnmbs = []
    for  fnmb in HXP_get_all_fnmbs_():
        fnmbs.append( FNMB(fnmb) )
    return fnmbs

#--------------------------------------------------------------------------------------------#

def get_fnmb_name(fnmb_index):
    return get_fnmb_name_(fnmb_index)

#--------------------------------------------------------------------------------------------#

def delete_fnmb(fnmb_name):
    return delete_fnmb_(fnmb_name)

#--------------------------------------------------------------------------------------------#

def store_all_fnmbs():
    all_fnmbs = []
    
    nb_fnmb = len( HXP_get_all_fnmbs_() )
    for i in range(nb_fnmb):
        name = get_fnmb_name(i)
        ll = get_fnmb_left_patches_(name)
        rr = get_fnmb_right_patches_(name)

        left = []
        for l in ll:
            left.append(l)
        right = []
        for r in rr:
            right.append(r)
        all_fnmbs.append([name,left,right])

    return all_fnmbs

#--------------------------------------------------------------------------------------------#

def compare_list(list1,list2):

    if len(list1) != len(list2):
        return 0

    for l1 in list1:
        found = 0
        for l2 in list2:
            if l1[0] == l2[0] and l1[1] == l2[1]:
                found = 1
                break
        if found==0:
#           print "NOT SMAE"
            return 0
#   print "SMAE!!!!" 
    return 1

#--------------------------------------------------------------------------------------------#
# check if list1 is contained in list2

def contained_in(list1,list2):

    for l1 in list1:
        found = 0
        for l2 in list2:
            # compare blkId and groupId
            if l1[0] == l2[0] and l1[1] == l2[1]:
                found = 1
                break
        if found==0:
            return 0
    return 1

#--------------------------------------------------------------------------------------------#

def compare_fnmb(fnmb1,fnmb2):

    left1 = fnmb1
    left2 = fnmb2

    right1 = fnmb1
    right2 = fnmb2
    if compare_list(left1,left2)==1 and compare_list(right1,right2)==1:
        return 1
    if compare_list(left1,right2)==1 and compare_list(right1,left2)==1:
        return 1
    return 0

#--------------------------------------------------------------------------------------------#

def compare_fnmbs(all_1,all_2):

    print "Number of OLD FNMB %d " % (len(all_1))
    print "Number of NEW FNMB %d " % (len(all_2))
    
    not_found    = []
    new_remining = all_2
    
    for fnmb1 in all_1:
        found = 0
        for fnmb2 in all_2:
            if compare_fnmb(fnmb1,fnmb2)==1:
                new_remining.remove(fnmb2)
                found = 1
                break
        if found==0:
            not_found.append(fnmb1)

    print "After cross check: "

    if len(not_found) == 0:
        print "    ALL Old FNMBs found an exact match with NEW FNMB"
    if len(not_found):
        print "    %d OLD FNMBs did not find an exact match with NEW FNMBs" % (len(not_found))

    if len(new_remining) != 0:
        print "    %d NEW FNMBs were found wihtout exact match to an OLD FNMBs" % (len(new_remining))
    
    if len(not_found)>0:
        print "The %d OLD FNMBs that were not found are: " %(len(not_found))
        for fnmb in not_found:
            print fnmb
            
    if len(new_remining)>0:
        print "The %d New FNMBs found that are not in the OLD FNMBs are: " %(len(new_remining))
        for fnmb in new_remining:
            print fnmb

    print " "
    print " START checking if remaining (not found) OLD FNMBs are partially containing in new FNMBs: "
    
    not_found_after_cross_check = []
    for fnmb in not_found:
        found = 0
        for fnmb_new in new_remining:
            if contained_in(fnmb[1],fnmb_new[1]) and contained_in(fnmb[2],fnmb_new[2]):
                print " OLD FNMB %s fully contained in %s L-L (%d,%d) / (%d,%d) " % (fnmb[0],fnmb_new[0],len(fnmb[1]),len(fnmb[2]),len(fnmb_new[1]),len(fnmb_new[2]))
                found = 1
                for f in fnmb[1]:
                    fnmb_new[1].remove(f)
                for f in fnmb[2]:
                    fnmb_new[2].remove(f)
#               break
            elif contained_in(fnmb[1],fnmb_new[2]) and contained_in(fnmb[2],fnmb_new[1]):
                print " OLD FNMB %s fully contained in %s L-R (%d,%d) / (%d,%d) " % (fnmb[0],fnmb_new[0],len(fnmb[1]),len(fnmb[2]),len(fnmb_new[1]),len(fnmb_new[2]))
                for f in fnmb[1]:
                    fnmb_new[2].remove(f)
                for f in fnmb[2]:
                    fnmb_new[1].remove(f)
                found = 1
#               break
        if found == 0:
            not_found_after_cross_check.append(fnmb)

    print "After check, %d OLD FNMBs remained not found (either completely or partially) " %(len(not_found_after_cross_check))
    for fnmb in not_found_after_cross_check:
        print fnmb

    print " After check %d NEW FNMB ramining " % (len(new_remining))
    for fnmb_new in new_remining:
        print   fnmb_new    

                
    for fnmb_new in new_remining:

        if len(fnmb_new[1])==0 or len(fnmb_new[2])==0:
            continue
        found = 0
        for fnmb in not_found_after_cross_check:
            if contained_in(fnmb_new[1],fnmb[1]) and contained_in(fnmb_new[2],fnmb[2]):
                found = 1
                pass
                #print " NEW FNMB %s fully contained in %s L-L (%d,%d) / (%d,%d) " % (fnmb_new[0],fnmb[0],len(fnmb_new[1]),len(fnmb_new[2]),len(fnmb[1]),len(fnmb[2]))
            elif contained_in(fnmb_new[1],fnmb[2]) and contained_in(fnmb_new[2],fnmb[1]):
                found = 1
                pass
                #print " NEW FNMB %s fully contained in %s L-R (%d,%d) / (%d,%d) " % (fnmb_new[0],fnmb[0],len(fnmb_new[1]),len(fnmb_new[2]),len(fnmb[1]),len(fnmb[2]))
        if found==0:    
            print " NEW FNMB %s NOT FOUND IN OLD FNMB " % (fnmb_new[0])

#--------------------------------------------------------------------------------------------#

def compare_fnmbs_old(all_1,all_2):

    not_found    = []
    new_remining = all_2
    
    for fnmb1 in all_1:
        found = 0
        for fnmb2 in all_2:
            if compare_fnmb(fnmb1,fnmb2)==1:
                new_remining.remove(fnmb2)
                found = 1
                break
        if found==0:
            not_found.append(fnmb1)

    if len(not_found)>0:
        print "%d OLD FNMBs not found " %(len(not_found))
        for fnmb in not_found:
            print fnmb
            
    if len(new_remining)>0:
        print "%d New FNMBs found " %(len(new_remining))
        for fnmb in new_remining:
            print fnmb

    not_found_after_cross_check = []
    for fnmb in not_found:
        found = 0
        for fnmb_new in new_remining:
            if contained_in(fnmb[1],fnmb_new[1]) and contained_in(fnmb[2],fnmb_new[2]):
                print " OLD FNMB %s fully contained in %s L-L (%d,%d) / (%d,%d) " % (fnmb[0],fnmb_new[0],len(fnmb[1]),len(fnmb[2]),len(fnmb_new[1]),len(fnmb_new[2]))
                found = 1
            elif contained_in(fnmb[1],fnmb_new[2]) and contained_in(fnmb[2],fnmb_new[1]):
                print " OLD FNMB %s fully contained in %s L-R (%d,%d) / (%d,%d) " % (fnmb[0],fnmb_new[0],len(fnmb[1]),len(fnmb[2]),len(fnmb_new[1]),len(fnmb_new[2]))
                found = 1
        if found == 0:
            not_found_after_cross_check.append(fnmb)

    print "%d OLD FNMBs not found after cross check " %(len(not_found_after_cross_check))
    for fnmb in not_found_after_cross_check:
        print fnmb
                
    for fnmb_new in new_remining:
        for fnmb in not_found_after_cross_check:
            if contained_in(fnmb_new[1],fnmb[1]) and contained_in(fnmb_new[2],fnmb[2]):
                print " NEW FNMB %s fully contained in %s L-L (%d,%d) / (%d,%d) " % (fnmb_new[0],fnmb[0],len(fnmb_new[1]),len(fnmb_new[2]),len(fnmb[1]),len(fnmb[2]))
            elif contained_in(fnmb_new[1],fnmb[2]) and contained_in(fnmb_new[2],fnmb[1]):
                print " NEW FNMB %s fully contained in %s L-R (%d,%d) / (%d,%d) " % (fnmb_new[0],fnmb[0],len(fnmb_new[1]),len(fnmb_new[2]),len(fnmb[1]),len(fnmb[2]))

#--------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------#
#               Parasolid query and manipulations                #
#--------------------------------------------------------------------------------------------#

class Partition:
    def __init__(self,id):
        self._id = id
        
    def get_bodies(self):
        bodies = []
        bs = Partition_get_bodies_(self._id)
        for b in bs:
            bodies.append(Body(b))
        return bodies

    def num_of_bodies(self):
        return len(Partition_get_bodies_(self._id))

#--------------------------------------------------------------------------------------------#

class Body:
    def __init__(self,id):
        self._id = id
        
    def delete(self):
        _notsup("Body::delete")
        Para_delete_bodies_(self._id)
        
    def get_name(self):
        return HXP_Pentity_get_name_(self._id)

    def set_name(self, name ):
        return HXP_Pentity_set_name_(self._id , name )

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_Pentity_get_box_(self._id)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])

    def num_faces(self):
        return len(HXP_body_get_faces_(self._id))

    def get_faces(self):
        faces = []
        fs =  HXP_body_get_faces_(self._id)
        for f in fs:
            faces.append(BodyFace(f))
        return faces
    
    def get_type(self):
        info = Body_get_info_(self._id)
        return info

    def check(self):
        num_faults = len ( Para_check_bodies_    ([self._id]) )
        num_edge_1 = len ( HXP_Para_get_edge_M_1 ([self._id]) )

        if num_faults !=0 or num_edge_1 != 0:
            return 0
        return 1

#--------------------------------------------------------------------------------------------#

class BodyFace:
    def __init__(self,id):
        self._id = id
        
    def get_name(self):
        return HXP_Pentity_get_name_(self._id)

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_Pentity_get_box_(self._id)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])

    def get_edges(self):
        faces = []
        fs =  HXP_bodyface_get_edges_(self._id)
        for f in fs:
            faces.append(BodyEdge(f))
        return faces
        
#--------------------------------------------------------------------------------------------#

class BodyEdge:
    def __init__(self,id):
        self._id = id
        
    def get_name(self):
        return HXP_Pentity_get_name_(self._id)

    def get_xyz_box(self):
        xmin,ymin,zmin,xmax,ymax,zmax = HXP_Pentity_get_box_(self._id)
        return Box([xmin,xmax,ymin,ymax,zmin,zmax])

        
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_all_partitions():
    #_notsup("get_all_partitions")
    
    partitions = []
    ps = Para_get_partitions_()
    for part in ps:
        partitions.append(Partition(part))
    return partitions

#--------------------------------------------------------------------------------------------#

def get_all_bodies():
    bodies = []
    partitions = get_all_partitions()

    for p in partitions:
        for b in p.get_bodies():
            bodies.append(b)
    return bodies

#--------------------------------------------------------------------------------------------#

def get_body_id(name):
    return HXP_get_id_(name)

#--------------------------------------------------------------------------------------------#
#               Creation of Bodies                       #
#--------------------------------------------------------------------------------------------#

from BodyManips import *

#--------------------------------------------------------------------------------------------#
# Private functions

# Return face id according to input type
# item can be one of:
#   DomainFace
#   String ( == face name)
#   Int  ( == the id itself )

def get_face_id_( domainPointer, item ):
    
    if type(item) is types.IntType:
        return item
    elif type(item) is types.StringType:
        for faceID in HXP_domain_get_faces_( domainPointer ):
            name = HXP_face_get_name_( domainPointer, faceID )
            if name == item:
                return  faceID
        return -1
    elif isinstance(item,DomainFace):
        return item._id
    return -1

#--------------------------------------------------------------------------------------------#

def get_face_object_( domainPointer, item ):
    
    if type(item) is types.IntType:
        return DomainFace( domainPointer, item )
    
    elif type(item) is types.StringType:
        for faceID in HXP_domain_get_faces_( domainPointer ):
            name = HXP_face_get_name_( domainPointer, faceID )
            if name == item:
                return  DomainFace( domainPointer, faceID )
    
    elif isinstance(item,DomainFace):
        return item
    
    return DomainFace( domainPointer, -1 )

#--------------------------------------------------------------------------------------------#

def extract_bodies_(item,bodies):
    
    if (type(item) is types.TupleType) | (type(item) is types.ListType):
        for sitem in item:
            extract_bodies_(sitem,bodies)
    elif isinstance(item,Body):
        bodies.append( item._id )
    else:
        bodies.append( HXP_get_id_(item) )

#--------------------------------------------------------------------------------------------#

def create_cube(name,p1,p2):

    # Check first if name already in use:
    if get_body_id(name) != -1:
        raise NameError,"Body name " + name + " already in use"

    # Create cuve and return Body object
    id = HXP_create_cube_(name,(p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z))

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )
    return Body(id)

#--------------------------------------------------------------------------------------------#

def create_plane(name,orig,norm,ref_dir,size):

    # Check first if name already in use:
    if get_body_id(name) != -1:
        raise NameError,"Body name " + name + " already in use"

    # We need to pass p1, p2 NOT p1,  normal see C++ impl.
    id = HXP_create_plane_(name,(orig.x,orig.y,orig.z),(norm.x,norm.y,norm.z),(ref_dir.x,ref_dir.y,ref_dir.z),size)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

    return Body(id)

#--------------------------------------------------------------------------------------------#

def create_cone(name,summit,normal,height,radius):

    # Check first if name already in use:
    if get_body_id(name) != -1:
        raise NameError,"Body name " + name + " already in use"

    id = HXP_create_cone_(name,(summit.x,summit.y,summit.z),(normal.x,normal.y,normal.z),height,radius)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

    return Body(id)

#--------------------------------------------------------------------------------------------#

def create_cylinder(name,orig,normal,height,radius):

    # Check first if name already in use:
    if get_body_id(name) != -1:
        raise NameError,"Body name " + name + " already in use"

    id = HXP_create_cylinder_(name,(orig.x,orig.y,orig.z),(normal.x,normal.y,normal.z),height,radius)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

    return Body(id)

#--------------------------------------------------------------------------------------------#

def create_sphere(name,orig,radius):

    # Check first if name already in use:
    if get_body_id(name) != -1:
        raise NameError,"Body name " + name + " already in use"

    id = HXP_create_sphere_(name,(orig.x,orig.y,orig.z),radius)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

    return Body(id)

#--------------------------------------------------------------------------------------------#

def delete_bodies(bodies):
    target = []
    extract_bodies_(bodies,target)

    HXP_delete_bodies_(target)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

#--------------------------------------------------------------------------------------------#

def subtract_bodies(itarget, itools, createCopies = 0):
    target = []
    extract_bodies_(itarget,target)

    tools = []
    extract_bodies_(itools,tools)

    HXP_substract_bodies_(target[0], tools, createCopies)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

# keep old name for backward compatibility
def substract_bodies(itarget,itools):
    subtract_bodies(itarget,itools)
    
#--------------------------------------------------------------------------------------------#

def unite_bodies(itarget, itools, createCopies = 0):
    target = []
    extract_bodies_(itarget,target)

    tools = []
    extract_bodies_(itools,tools)

    HXP_unite_bodies_(target[0], tools, createCopies)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

#--------------------------------------------------------------------------------------------#

def intersect_bodies(itarget, itools, createCopies = 0):
    target = []
    extract_bodies_(itarget,target)

    tools = []
    extract_bodies_(itools,tools)

    HXP_intersect_bodies_(target[0], tools, createCopies)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

#--------------------------------------------------------------------------------------------#

def sew_bodies(tol,ibodies):
    bodies = []
    extract_bodies_(ibodies,bodies)

    HXP_sew_bodies_(tol,bodies)

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

#--------------------------------------------------------------------------------------------#

def translate_bodies(bodies, vec, createCopies = 0):
    list = []
    extract_bodies_(bodies,list)

    HXP_translate_bodies_(list,(vec.x,vec.y,vec.z), createCopies)

#--------------------------------------------------------------------------------------------#

def scale_bodies(bodies, scale_factors, createCopies = 0):
    list = []
    extract_bodies_(bodies,list)

    HXP_scale_bodies_(list,(scale_factors.x,scale_factors.y,scale_factors.z), createCopies)

#--------------------------------------------------------------------------------------------#

def rotate_bodies(bodies, orig, axis, angle_deg, createCopies = 0):
    list = []
    extract_bodies_(bodies,list)

    HXP_rotate_bodies_(list,(orig.x,orig.y,orig.z),(axis.x,axis.y,axis.z),angle_deg, createCopies)

#--------------------------------------------------------------------------------------------#

def create_domain(filename,body,min_facet_size,max_facet_size,curve_chord_tol,curve_chord_angle,surf_plane_tol,surf_plane_angle):

    list = []
    extract_bodies_(body,list)

    HXP_delete_stl_triangulation_()
    HXP_create_domain_(filename,len(list),list,min_facet_size,max_facet_size,curve_chord_tol,curve_chord_angle,surf_plane_tol,surf_plane_angle)

#--------------------------------------------------------------------------------------------#

def set_silent_mode(mode):
    eval_tcl_string( "hexa_setSilentMode " + str(mode) )

#--------------------------------------------------------------------------------------------#

def is_silent_mode():
    if not is_batch():
        return eval_tcl_string( "hexa_getSilentMode" ) == "1"
    else:
        return 1

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#   Private functions
#--------------------------------------------------------------------------------------------#

def _notsup(n):
    print "Python function : " + n + " not supported"
    sys.exit()

#--------------------------------------------------------------------------------------------#

def _notsup2(n):
    pass
#   print "Python function : " + n + " not supported"
#   sys.exit()

#--------------------------------------------------------------------------------------------#

def _obsolete(n):
    print "Python function " + n + " is obsolete"

#--------------------------------------------------------------------------------------------#

def is_batch():
    return "-batch" in sys.argv;

#--------------------------------------------------------------------------------------------#

def undo2():
    import IGGSystem
    IGGSystem.undo_()

    if not is_batch():
        eval_tcl_string( "HexaParasolidBrowser:open_all_partitions" )

#--------------------------------------------------------------------------------------------#

def compute_first_layer_thickness( yRef, Lref, Vref, kinVisc ):
    return (6 * pow( Vref / kinVisc , -0.875 ) * pow (Lref / 2.0 , 0.125) * yRef )

#--------------------------------------------------------------------------------------------#

def compute_number_of_layers( face, first_layer_thickness, stretchRatio ):
    
    cellHeight = HXP_calc_average_normal_edge_length_(1,face._id )
    
    nbLayers     = 1
    totalHeight  = first_layer_thickness
    addValue     = totalHeight
    
    while totalHeight < cellHeight:
        addValue = addValue * stretchRatio
        totalHeight = totalHeight + addValue
        nbLayers = nbLayers + 1
        
    return nbLayers

#--------------------------------------------------------------------------------------------#

def compute_box_division( totalNumCell ):
    # Usage: nx,ny,nz = compute_box_division( 10000 )
    
    return HXP_compute_box_division_( totalNumCell )

#--------------------------------------------------------------------------------------------#

def export_fluent(filename):
    HXP_export_fluent_(filename)

#--------------------------------------------------------------------------------------------#

# mode == 0 - CGNS ADF  format
# mode == 1 - CGNS HDF5 format

def export_cgns(filename, mode = 0):
    HXP_export_cgns_(filename, mode)

#--------------------------------------------------------------------------------------------#

def export_nastran(filename, precision):
    HXP_export_nastran_(filename, precision)

#--------------------------------------------------------------------------------------------#

def export_foam(dirname):
    HXP_export_foam_(dirname)

#--------------------------------------------------------------------------------------------#

def export_starcd(filename):
    HXP_export_starcd_(filename)

#--------------------------------------------------------------------------------------------#

def export_cedre(filename):
    HXP_export_cedre_(filename)

def export_cedre_short_name(filename):
    HXP_export_cedre_shortName_(filename)

#--------------------------------------------------------------------------------------------#

def export_starccm(filename):
    if is_batch():
        HXP_export_starccm_(filename)
    else:
        eval_tcl_string("Hexa:Project:exportStarCCM {" + filename + "}")

#--------------------------------------------------------------------------------------------#

def export_sph(filename):
    if is_batch():
        HXP_export_sph_(filename)
    else:
        eval_tcl_string("Hexa:Project:exportSPH {" + filename + "}")

#--------------------------------------------------------------------------------------------#

def export_samcef(filename):
    HXP_export_samcef_(filename)

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class SurfaceAdaptationGroup:
    # !! pointer is actually pointer to hexaBlock
    #
    def __init__(self, domain , groupName ):

        found = 0

        all_groups = HXP_getAdaptPatchGroups_( domain._pointer )
        for group in all_groups:
            if group[0] == groupName:
                found = 1
                break

        self.get_faces_by_name = 0
        if found == 0:
            # No group exist in the project definition. We will use directly
            # faces of the domain having the "groupName"
            self.get_faces_by_name = 1
            #raise ValueError("Surface Adaptation Group does not exist",groupName)

        self._groupName = groupName
        self._domain    = domain

    def get_patches(self):
        patches = []

        if self.get_faces_by_name == 0:
            for faceID in HXP_getAdaptGroupPatchIDs_( self._domain._pointer , self._groupName ):
                patches.append( DomainFace(self._domain, faceID) )
        else:
            for face in self._domain.get_faces_by_name(self._groupName):
                patches.append( face )
            
        return patches

    def enable_adaptation(self,value):
        for patch in self.get_patches():
            patch.enable_adaptation( value )

    def set_adaptation_criteria(self,dist,curvature,target):
        for patch in self.get_patches():
            patch.set_adaptation_criteria( dist, curvature, target )
            
    def set_adaptation_criterias(self,dist,curvature,target):
        self.set_adaptation_criteria(dist,curvature,target)

    def get_adaptation_criteria(self):
        patches =  self.get_patches()
        return patches[0].get_adaptation_criteria()

    def get_adaptation_criterias(self):
        return self.get_adaptation_criteria()

    def set_advanced_adaptation_criteria(self,curvatureFactor,aniso_extent):
        for patch in self.get_patches():
            patch.set_advanced_adaptation_criteria( curvatureFactor, aniso_extent )
            
    def set_advanced_adaptation_criterias(self,curvatureFactor,aniso_extent):
        self.set_advanced_adaptation_criteria(curvatureFactor,aniso_extent)

    def get_advanced_adaptation_criteria(self):
        patches =  self.get_patches()
        return patches[0].get_advanced_adaptation_criteria()

    def get_advanced_adaptation_criterias(self):
        return self.get_advanced_adaptation_criteria()

    def set_diffusion_depth(self,depth):
        for patch in self.get_patches():
            patch.set_diffusion_depth( depth )

    def get_diffusion_depth(self):
        patches =  self.get_patches()
        return patches[0].get_diffusion_depth()

    def set_number_of_refinements( self, n ):
        for patch in self.get_patches():
            patch.set_number_of_refinements( n )

    def get_number_of_refinements(self):
        patches =  self.get_patches()
        return patches[0].get_number_of_refinements()
    
    def set_max_aspect_ratio(self,maxAspectRatio):
        for patch in self.get_patches():
            patch.set_max_aspect_ratio( maxAspectRatio )

    def get_max_aspect_ratio(self):
        patches =  self.get_patches()
        return patches[0].get_max_aspect_ratio()

    def set_target_sizes(self,x,y,z):
        # enable target size
        for patch in self.get_patches():
            patch.set_target_sizes( x,y,z )

    def get_target_sizes(self):
        patches =  self.get_patches()
        return patches[0].get_target_sizes()

#--------------------------------------------------------------------------------------------#

class EdgeAdaptationGroup:
    def __init__(self, domain , groupName ):

        found = 0

        all_groups = HXP_getEdgeAdaptGroups_( domain._pointer )
        for group in all_groups:
            if group[0] == groupName:
                found = 1
                break

        if found == 0:
            raise ValueError("Edge Adaptation Group does not exist",groupName)

        self._groupName = groupName
        self._domain    = domain

    def get_edges(self):
        patches = []
        for edgeID in HXP_getEdgeAdaptGroupIDs_( self._domain._pointer , self._groupName ):
            patches.append( DomainEdge(self._domain, edgeID) )
        return patches

    def enable_adaptation(self,value):
        for patch in self.get_edges():
            patch.enable_adaptation( value )

    def set_adaptation_criteria(self,dist,curvature,target):
        for patch in self.get_edges():
            patch.set_adaptation_criteria( dist, curvature, target )
            
    def set_adaptation_criterias(self,dist,curvature,target):
        self.set_adaptation_criteria(dist,curvature,target)

    def get_adaptation_criteria(self):
        patches =  self.get_edges()
        return patches[0].get_adaptation_criteria()

    def get_adaptation_criterias(self):
        return self.get_adaptation_criteria()

    def set_advanced_adaptation_criteria(self,curvatureFactor,aniso_extent):
        for patch in self.get_edges():
            patch.set_advanced_adaptation_criteria( curvatureFactor, aniso_extent )
            
    def set_advanced_adaptation_criterias(self,curvatureFactor,aniso_extent):
        self.set_advanced_adaptation_criteria(curvatureFactor,aniso_extent)

    def get_advanced_adaptation_criteria(self):
        patches =  self.get_edges()
        return patches[0].get_advanced_adaptation_criteria()

    def get_advanced_adaptation_criterias(self):
        return self.get_advanced_adaptation_criteria()

    def set_diffusion_depth(self,depth):
        for patch in self.get_edges():
            patch.set_diffusion_depth( depth )

    def get_diffusion_depth(self):
        patches =  self.get_edges()
        return patches[0].get_diffusion_depth()

    def set_number_of_refinements( self, n ):
        for patch in self.get_edges():
            patch.set_number_of_refinements( n )

    def get_number_of_refinements(self):
        patches =  self.get_edges()
        return patches[0].get_number_of_refinements()
    
    def set_max_aspect_ratio(self,maxAspectRatio):
        for patch in self.get_edges():
            patch.set_max_aspect_ratio( maxAspectRatio )

    def get_max_aspect_ratio(self):
        patches =  self.get_edges()
        return patches[0].get_max_aspect_ratio()

    def set_target_sizes(self,x,y,z):
        # enable target size
        for patch in self.get_edges():
            patch.set_target_sizes( x,y,z )

    def get_target_sizes(self):
        patches =  self.get_edges()
        return patches[0].get_target_sizes()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class VLGroup:
    # !! pointer is actually pointer to hexaBlock
    #
    def __init__(self, domain , groupName ):

        found = 0

        all_groups = HXP_getVLPatchGroups_( domain._pointer )
        for group in all_groups:
            if group[0] == groupName:
                found = 1
                break

        self.get_faces_by_name = 0
        if found == 0:
            # No group exist in the project definition. We will use directly
            # faces of the domain having the "groupName"
            self.get_faces_by_name = 1
            #raise ValueError("Viscous Layer Group does not exist",groupName)

        self._groupName = groupName
        self._domain    = domain

    def get_patches(self):
        patches = []

        if self.get_faces_by_name == 0:
            for faceID in HXP_getVLPatchIDs_( self._domain._pointer , self._groupName ):
                patches.append( DomainFace(self._domain, faceID) )
        else:
            for face in self._domain.get_faces_by_name(self._groupName):
                patches.append( face )
                
        return patches

    def enable_viscous_layers(self,value):
        for patch in self.get_patches():
            patch.enable_viscous_layers( value )
        
    def set_viscous_layer_params(self,nbLayer,stretch,thickness,aspectRatio = 5.,expansion = 1.3 ):
        for patch in self.get_patches():
            patch.set_viscous_layer_params( nbLayer,stretch,thickness,aspectRatio,expansion )
        
    def get_viscous_layer_params(self):
        patches =  self.get_patches()
        return patches[0].get_viscous_layer_params()

#--------------------------------------------------------------------------------------------#

class RGBColor:

    color_table = { 
    "alice blue"    :"#f0f8ff",
    "antique white" :"#faebd7",
    "aqua"      :"#00ffff",
    "aquamarine"    :"#7fffd4",
    "azure"     :"#f0ffff",
    "beige"     :"#f5f5dc",
    "bisque"    :"#ffe4c4",
    "black"     :"#000000",
    "blanched almond"   :"#ffebcd",
    "blue"      :"#0000ff",
    "blue-Violet"   :"#8a2be2",
    "brown"     :"#a52a2a",
    "burlywood" :"#deb887",
    "cadet blue"    :"#5f9ea0",
    "chartreuse"    :"#7fff00",
    "chocolate" :"#d2691e",
    "coral"     :"#ff7f50",
    "cornflower blue"   :"#6495ed",
    "cornsilk"  :"#fff8dc",
    "cyan"      :"#00ffff",
    "dark blue" :"#00008b",
    "dark cyan" :"#008b8b",
    "dark goldenrod":"#b8860b",
    "dark gray" :"#a9a9a9",
    "dark green"    :"#006400",
    "dark khaki"    :"#bdb76b",
    "dark magenta"  :"#8b008b",
    "dark olive green":"#556b2f",
    "dark orange"   :"#ff8c00",
    "dark orchid"   :"#9932cc",
    "dark red"  :"#8b0000",
    "dark salmon"   :"#e9967a",
    "dark sea green"    :"#8fbc8f",
    "dark slate blue"   :"#483d8b",
    "dark slate gray"   :"#2f4f4f",
    "dark turquoise"    :"#00ced1",
    "dark violet"   :"#9400d3",
    "deep pink" :"#ff1493",
    "deep sky blue" :"#00bfff",
    "dim gray"  :"#696969",
    "dodger blue"   :"#1e90ff",
    "firebrick" :"#b22222",
    "floral white"  :"#fffaf0",
    "forest green"  :"#228b22",
    "fuschia"   :"#ff00ff",
    "gainsboro" :"#dcdcdc",
    "ghost white"   :"#f8f8ff",
    "gold"      :"#ffd700",
    "goldenrod" :"#daa520",
    "gray"      :"#808080",
    "green"     :"#008000",
    "green yellow"  :"#adff2f",
    "honeydew"  :"#f0fff0",
    "hot pink"  :"#ff69b4",
    "indian red"    :"#cd5c5c",
    "ivory"     :"#fffff0",
    "khaki"     :"#f0e68c",
    "lavender"  :"#e6e6fa",
    "lavender blush":"#fff0f5",
    "lawn green"    :"#7cfc00",
    "lemon chiffon" :"#fffacd",
    "light blue"    :"#add8e6",
    "light coral"   :"#f08080",
    "light cyan"    :"#e0ffff",
    "light goldenrod":"#eedd82",
    "light goldenrod Yellow":"#fafad2",
    "light gray"    :"#d3d3d3",
    "light green"   :"#90ee90",
    "light pink"    :"#ffb6c1",
    "light salmon"  :"#ffa07a",
    "light sea green":"#20b2aa",
    "light sky blue":"#87cefa",
    "light slate blue":"#8470ff",
    "light slate gray":"#778899",
    "light steel blue":"#b0c4de",
    "light yellow"  :"#ffffe0",
    "lime"      :"#00ff00",
    "lime green"    :"#32cd32",
    "linen"     :"#faf0e6",
    "magenta"   :"#ff00ff",
    "maroon"    :"#800000",
    "medium aquamarine" :"#66cdaa",
    "medium blue"   :"#0000cd",
    "medium orchid" :"#ba55d3",
    "medium purple" :"#9370db",
    "medium sea green"  :"#3cb371",
    "medium slate blue" :"#7b68ee",
    "medium spring green"   :"#00fa9a",
    "medium turquoise"  :"#48d1cc",
    "medium violet red" :"#c71585",
    "midnight blue" :"#191970",
    "mint cream"    :"#f5fffa",
    "misty rose"    :"#e1e4e1",
    "moccasin"  :"#ffe4b5",
    "navajo white"  :"#ffdead",
    "navy"      :"#000080",
    "old lace"  :"#fdf5e6",
    "olive"     :"#808000",
    "olive drab"    :"#6b8e23",
    "orange"    :"#ffa500",
    "orange red"    :"#ff4500",
    "orchid"    :"#da70d6",
    "pale goldenrod":"#eee8aa",
    "pale green"    :"#98fb98",
    "pale turquoise":"#afeeee",
    "pale violet red":"#db7093",
    "papaya whip"   :"#ffefd5",
    "peach puff"    :"#ffdab9",
    "peru"      :"#cd853f",
    "pink"      :"#ffc0cb",
    "plum"      :"#dda0dd",
    "powder blue"   :"#b0e0e6",
    "purple"    :"#800080",
    "red"       :"#ff0000",
    "rosy brown"    :"#bc8f8f",
    "royal blue"    :"#4169e1",
    "saddle brown"  :"#8b4513",
    "salmon"    :"#fa8072",
    "sandy brown"   :"#f4a460",
    "sea green" :"#2e8b57",
    "seashell"  :"#fff5ee",
    "sienna"    :"#a0522d",
    "silver"    :"#c0c0c0",
    "sky blue"  :"#87ceeb",
    "slate blue"    :"#6a5acd",
    "slate gray"    :"#708090",
    "snow"      :"#fffafa",
    "spring green"  :"#00ff7f",
    "steel blue"    :"#4682b4",
    "tan"       :"#d2b48c",
    "teal"      :"#008080",
    "thistle"   :"#d8bfd8",
    "tomato"    :"#ff6347",
    "turquoise" :"#40e0d0",
    "violet"    :"#ee82ee",
    "violet red"    :"#d02090",
    "wheat"     :"#f5deb3",
    "white"     :"#ffffff",
    "white smoke"   :"#f5f5f5",
    "yellow"    :"#ffff00",
    "yellow green"  :"#9acd32",
        }

    cur_color = 0
    
    color_set1 = ["black",
                "white",
                "yellow",
                "red",
                "blue",
                "green",
                "magenta",
                "green yellow",
                "light blue",
                "cyan",
                "orange",
                "gray",
                "orange",
                "violet red",
                "maroon",
                "lavender",
                "light yellow",
                "violet",
                "pink",
                "navy"]

    @staticmethod
    def color(name):
        hexv =  RGBColor.color_table[name]
        
        return [ int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:], 16)]

    
    @staticmethod
    def colorSet1():
        return RGBColor.color_set1

    @staticmethod
    def get_next_color():
        RGBColor.cur_color = RGBColor.cur_color + 1
        if RGBColor.cur_color >= len(RGBColor.color_set1):
            RGBColor.cur_color = 0
            
        return RGBColor.color_set1[RGBColor.cur_color]

#--------------------------------------------------------------------------------------------#

# NEW !!!!!!!!!1
#
def get_disjointed_face_sets( in_facelist ):
    _notsup2("get_disjointed_face_sets")

    facelist = copy.deepcopy( in_facelist )

    face_sets = []
    
    while len( facelist ) != 0:
        
        face     = facelist.pop()
        to_treat = [ face ]
        new_set  = []
        treated  = []

        face_sets.append( new_set )
        
        while len( to_treat ) !=0:
            cur_face = to_treat.pop()
            new_set.append( cur_face )
            treated.append( cur_face )
            
            for edge in cur_face.get_edges():
                other_face = edge.get_other_face( cur_face )

                if not other_face in treated and other_face in facelist:
                    to_treat.append( other_face )
                    facelist.remove( other_face )

    return face_sets

#--------------------------------------------------------------------------

def find_edges_with_multiplicity_1(faces):
    _notsup2("find_edges_with_multiplicity_1")

    edge_multiplicity = {}
                
    for f in faces:
        for e in f.get_edges():
            if not edge_multiplicity.has_key( e._id ):
                edge_multiplicity[e._id] = 0
                
            edge_multiplicity[e._id] = edge_multiplicity[e._id] + 1

    edges_with_multiplicity_1 = []
    for key in edge_multiplicity.keys():
        if edge_multiplicity[key] == 1:
#            edges_with_multiplicity_1.append( key )
            edges_with_multiplicity_1.append( DomainEdge( f._domain , key ) )

    return edges_with_multiplicity_1
        
#--------------------------------------------------------------------------

def display_warning(mess):
    message =  'SysMessage:warning ' + "\"" + mess + "\""
    eval_tcl_string( message )

#--------------------------------------------------------------------------

def display_info(mess):
    message =  'SysMessage:message '  + "\"" + mess + "\""
    eval_tcl_string( message )

#--------------------------------------------------------------------------

def save_camera_position(pos,target,up,width,height):
    set_camera_position(pos,target,up,width,height)
    PythonViewing._save_camera_position()

#--------------------------------------------------------------------------

def set_camera_position(pos,target,up,width,height):
    PythonViewing._set_camera_position((pos.x,pos.y,pos.z),(target.x,target.y,target.z),(up.x,up.y,up.z),width,height)

#--------------------------------------------------------------------------

def get_camera_position():
    return PythonViewing._get_camera_position()

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

# ref_angle must be >=0 * < 180
# useAverageAngle must be 0 or 1

class MergeTangentFaces:
    def __init__(self, initial_set, ref_angle = 160., useAverageAngle = 1):

        self.faces_to_treat = []

        # create a copy of the input list
        for f in initial_set:
            if isinstance(f,DomainFace):
                self.faces_to_treat.append(f.get_id())
            else:
                # 'f' - faceID => create and add a face object to the list
                self.faces_to_treat.append(f)

        self.merge_sets = []             # all face sets to be merged

        self.compute_merge_sets(ref_angle, useAverageAngle)
        self.merge_faces()

    #-----------------------------------------------------------------------
    def compute_merge_sets(self, ref_angle, useAverageAngle ):

        if not is_batch():
            clear_face_selection()

        active_merge_set = []
        all_merge_sets   = []
        domain = get_active_domain()

        all_merge_sets = HXP_get_face_merge_set_(len(self.faces_to_treat), self.faces_to_treat, ref_angle, useAverageAngle)
        for active_merge_set in all_merge_sets:
            if len(active_merge_set) > 0:
                self.merge_sets.append( active_merge_set )

    #-----------------------------------------------------------------------
    def merge_faces(self):
        for set in self.merge_sets:
            #color = RGBColor.get_next_color()
            #for face in set:
            #    face.set_color( color )

            merge_face_list( set )

#----------------------------------------------------------------------------------------------
#Debug functions
DT_SHOW_VERTEX = 1
DT_SHOW_EDGE   = 2
DT_SHOW_FACE   = 4
DT_SHOW_CELL   = 8


def get_cell_vertices(cellId):
    return HXP_get_cell_vertices_(cellId)
    
#----------------------------------------------------------------------------------------------

def get_cell_edges(cellId):
    return HXP_get_cell_edges_(cellId)
    
#----------------------------------------------------------------------------------------------

def get_cell_faces(cellId):
    return HXP_get_cell_faces_(cellId)
    
#----------------------------------------------------------------------------------------------

def get_face_vertices(faceId):
    return HXP_get_face_vertices_(faceId)
    
#----------------------------------------------------------------------------------------------

def get_face_edges(faceId):
    return HXP_get_face_edges_(faceId)
    
#----------------------------------------------------------------------------------------------

def get_edge_vertices(edgeId):
    return HXP_get_edge_vertices_(edgeId)
    
#----------------------------------------------------------------------------------------------

def find_cells_by_face(faceId):
    return HXP_find_cells_by_face_(faceId)
    
#----------------------------------------------------------------------------------------------

def display_cell(cellId,showId=0):
    HXP_display_cell_(cellId,showId)
    
#----------------------------------------------------------------------------------------------

def display_face(faceId,showId=0):
    HXP_display_face_(faceId,showId)
    
#----------------------------------------------------------------------------------------------

def display_edge(edgeId,showId=0):
    HXP_display_edge_(edgeId,showId)
    
#----------------------------------------------------------------------------------------------

def display_vertex(vertexId,showId=0):
    HXP_display_vertex_(vertexId,showId)

#----------------------------------------------------------------------------------------------

def clear_debug_draw():
    HXP_clear_debug_draw_()

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
