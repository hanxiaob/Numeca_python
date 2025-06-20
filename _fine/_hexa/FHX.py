#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#--------------------------------------------------------------------------------------------#

import sys,os,math,copy,string

import fnmatch, re ; # regular expressions

###import types
from Geom      import *
from IGGSystem import *

from HexaModuleCommands import *
from HexaModuleBcsCommands import *
from HexaModuleInitsolCommands import *
from HexaModuleOutputsCommands import *
from HexaModuleNLHCommands import *
from HexaModuleANSYSCommands import *
from HexaModuleCouplingCommands import *
from HexaModuleComputationsCommands import *

#--------------------------------------------------------------------------------------------#
#				Global query functions					     #
#--------------------------------------------------------------------------------------------#

def get_version():
    majorVer = 0;
    minorVer = 0;
    patchVer = 0;

    # -------------------------------
    # Get current version
    # Assume format is one of following:
    # x.y[-z[-z1]]
    #   x: major version
    #   y: minor version
    #   z: patch version (optional)
    #
    # x.yrc (rc version)
    #   x: major version
    #   y: minor version
    #
    # 10*x+ydevXXX (dev version)
    #   x: major version
    #   y: minor version
    #
    # 10*x+yaXXX (alpha version)
    #   x: major version
    #   y: minor version
    #
    # 10*x+ybXXX (beta version)
    #   x: major version
    #   y: minor version
    #
    # -------------------------------
    versionStr = FHX_get_version_()

    # Get major version (number before first '.')
    if (len(string.split(versionStr,'.')) > 1):
        majorVer = int(string.split(versionStr,'.')[0])            
    elif (len(string.split(versionStr,'dev')) > 1):
        versionStr2 = string.split(versionStr,'dev')[0]
        majorVer = int(versionStr2)/10
        minorVer = int(versionStr2)-10*majorVer
    elif (len(string.split(versionStr,'a')) > 1):
        versionStr2 = string.split(versionStr,'a')[0]
        majorVer = int(versionStr2)/10
        minorVer = int(versionStr2)-10*majorVer
    elif (len(string.split(versionStr,'b')) > 1):
        versionStr2 = string.split(versionStr,'b')[0]
        majorVer = int(versionStr2)/10
        minorVer = int(versionStr2)-10*majorVer
        
    # Get minor version (number after first '.', and before first '-')
    if (len(string.split(versionStr,'.'))>1):
        s = string.split(versionStr,'.')[1]
        s1 = string.split(s,'-')[0]
        # ... Trim first letter (alpha version for example)
        pattern = re.compile('[a-z]')
        if (pattern.search(s1)):
            index1 = pattern.search(s).start()
            minorVer = int(s[0:index1])
        else:
            minorVer = int(s1)

    # Get patch version (number after first '-', and before second '-')
    if (len(string.split(versionStr,'.'))>1 and len(string.split(s,'-'))>1): 
        s2 = string.split(s,'-')[1]
        # ... Trim first letter (alpha version for example)
        pattern = re.compile('[a-z]')
        if (pattern.search(s2)):
            index1 = pattern.search(s2).start()
            patchVer = int(s2[0:index1])
        else:
            patchVer = int(s2)

    #print 'versionStr: '+str(versionStr)
    #print 'Major version: '+str(majorVer)
    #print 'Minor version: '+str(minorVer)
    #print 'Patch version: '+str(patchVer)
    return majorVer, minorVer, patchVer

#--------------------------------------------------------------------------------------------#
def is_batch():
    for arg in sys.argv:
        if arg == "-batch":
            return 1
    return 0

#--------------------------------------------------------------------------------------------#
def switch_to_HEXPRESS():
    FHX_switch_to_HEXPRESS_()
    
#--------------------------------------------------------------------------------------------#
def close_HEXPRESS():
    FHX_restore_an_HEXPRESS_license_()
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( "changeProduct hexa" )

#--------------------------------------------------------------------------------------------#
def create_project(projectname):
    dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
    basename = os.path.basename(projectname)

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( "ith_project:_do_create_new_project \"" + projectname + "\"" )
    else:
        ## BATCH MODE
        FHX_create_project_(basename,dirname)
        FHX_init_computations_position_()
        
#--------------------------------------------------------------------------------------------#
def new_project():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( "ith_project:new_project" )
    else:
        ## BATCH MODE
        FHX_new_project_()

#--------------------------------------------------------------------------------------------#
def open_project(projectname):

    if not is_batch():
        ## INTERACTIVE MODE
        s = projectname
        escape_dict = {'\a':r'\a', '\b':r'\b', '\n':r'\n', '\r':r'\r', '\t':r'\t'}
        for c in escape_dict .keys() :
            s = s.replace(c,escape_dict[c])
        s = s.replace('\\','\\\\')
        eval_tcl_string( "itf_do_open_project \"" + s + "\"")

    else:
        ## BATCH MODE
        dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
        basename = os.path.basename(projectname)
        escape_dict = {'\a':r'\a', '\b':r'\b', '\n':r'\n', '\r':r'\r', '\t':r'\t'}
        for c in escape_dict .keys() :
            dirname   = dirname.replace(c,escape_dict[c])
            basename  = basename.replace(c,escape_dict[c])
        dirname  = dirname.replace('\\','\\\\')
        basename = basename.replace('\\','\\\\')
        
        FHX_open_project_(basename,dirname)
        FHX_init_computations_position_()
        
#--------------------------------------------------------------------------------------------#
def save_project():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( "topToolBar:itf_save_all_project" )
    else:
        ## BATCH MODE
        FHX_save_project_()
        
#--------------------------------------------------------------------------------------------#
def duplicate_project(newProjectname, duplicateResults):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string("global itf_save_as(duplicateComputation); set itf_save_as(duplicateComputation) "+duplicateResults)
        eval_tcl_string( "itf_do_save_as_new_project2 " + newProjectname )
    else:
        ## BATCH MODE
        ## ... TO DO
        return

#--------------------------------------------------------------------------------------------#
def link_mesh_file(meshfile):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string("ith_project:import_mesh \"" + meshfile + "\"" )
    else:
        ## BATCH MODE
        FHX_link_mesh_file_(meshfile)
        nb_def_bc = FHX_get_nb_def_bc_()
        for idx in range( nb_def_bc ):
            bc_name = FHX_get_def_bc_name_(idx)[0]
            FHX_auto_group_patches_(bc_name)


#--------------------------------------------------------------------------------------------#
METER      = 1.0
CENTIMETER = 0.01
MILLIMETER = 0.001
INCH       = 0.0254
#--------------------------------------------------------------------------------------------#
def get_unit_ratio():
    return FHX_get_unit_ratio_()

#--------------------------------------------------------------------------------------------#
def set_unit_ratio(ratio):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string("HEXA:set_mesh_unit_ratio " + str(ratio) )
    else:
        ## BATCH MODE
        FHX_set_unit_ratio_(ratio)




#--------------------------------------------------------------------------------------------#
#----				Computation management					 ----#
#--------------------------------------------------------------------------------------------#
def get_nb_computations():
    nc = FHX_get_nb_computations_()
    return nc

#--------------------------------------------------------------------------------------------#
def set_active_computations(indexList):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" ith_computations:clear_active_computation_list ")
        for idx in indexList:
            print 'idx: '+str(idx)
            eval_tcl_string(" ith_computations:activate_computation " + str(idx) )
        eval_tcl_string(" ith_computations:get_computations_names" )
    else:
        ## BATCH MODE
        FHX_clear_active_computations_()
        for idx in indexList:
            FHX_set_active_computation_(idx)

#--------------------------------------------------------------------------------------------#
def get_computation_name(index):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    rc = FHX_get_computation_name_(index)
    return rc[0]

#--------------------------------------------------------------------------------------------#
def set_computation_name(index,name):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    # Check if name already exists
    nc = get_nb_computations()
    for i in range( nc ):
        if (FHX_get_computation_name_(i) == name):
            raise ValueError, "Computation : " + name + ' already exists.'

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_rename_selected_computation " + str(index) + " " + name + " " + str(1) )
        eval_tcl_string(" ith_computations:get_computations_names ")
        FHX_save_project_()
    else:
        ## BATCH MODE
        FHX_set_computation_name_(index,name,1)
        FHX_save_project_()

#--------------------------------------------------------------------------------------------#
def save_selected_computations():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" topToolBar:itf_save_run_file ")
    else:
        ## BATCH MODE
        FHX_save_active_computations_()

#--------------------------------------------------------------------------------------------#
def new_computation(name):
    # Check if name already exists
    nc = get_nb_computations()
    for i in range( nc ):
        if (FHX_get_computation_name_(i) == name):
            raise ValueError, "Computation : " + name + ' already exists.'
        
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" ith_computations:new ")
        set_active_computations([nc])
        eval_tcl_string(" itf_rename_selected_computation " + str(nc) + " " + name + " " + str(1) )
        eval_tcl_string(" ith_computations:get_computations_names ")
        ##FHX_save_project_()
    else:
        ## BATCH MODE
        FHX_set_nb_computations_(nc+1)
        set_active_computations([nc])
        FHX_set_computation_name_(nc,name,0)
        FHX_init_computations_position_()
        ##FHX_save_project_()

#--------------------------------------------------------------------------------------------#
def remove_selected_computations( deleteFiles ):
    nc = get_nb_computations()
    if (nc<2):
        print 'Only one computation is defined. This cannot be removed.'
        return
    
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" ith_computations:do_remove_selected_computations "+str(deleteFiles) )
    else:
        ## BATCH MODE
        FHX_remove_active_computations_( deleteFiles )

#--------------------------------------------------------------------------------------------#
def clean_selected_computations( deepDelete ):
    result = FHX_clean_active_computations_( deepDelete )
    isOk = result[0]
    if (isOk==0):
        errMess = result[2]
        print 'Warning:'
        print errMess

#--------------------------------------------------------------------------------------------#
def move_down_selected_computations():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" ith_computations:move_down_selection ")
    else:
        ## BATCH MODE
        FHX_move_down_active_computations_()

#--------------------------------------------------------------------------------------------#
def move_up_selected_computations():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" ith_computations:move_up_selection ")
    else:
        ## BATCH MODE
        FHX_move_up_active_computations_()


#--------------------------------------------------------------------------------------------#
#----				Solver precision					 ----#
#--------------------------------------------------------------------------------------------#

def get_precision_mode():
    return FHX_get_precision_mode_() # values are "single", "hybrid" or "double"

def set_precision_mode(mode):
    FHX_set_precision_mode_(mode)


#--------------------------------------------------------------------------------------------#
#----				Batch file					         ----#
#--------------------------------------------------------------------------------------------#
def save_batch_file():
    return FHX_save_batch_file_()


#--------------------------------------------------------------------------------------------#
#----				Mesh properties					         ----#
#--------------------------------------------------------------------------------------------#
def get_nb_domains():
    return FHX_get_nb_domains_()
#--------------------------------------------------------------------------------------------#
def get_domain_name(idx):
    # ... Check domain index validity
    if (idx<0 or idx>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(idx)
    name = FHX_get_domain_name_(idx)
    return name
#--------------------------------------------------------------------------------------------#
def get_domain_index(name):
    idx = FHX_get_domain_index_(name)
    if idx == -1:
        raise ValueError,"Wrong domain name : " + name
    return idx
#--------------------------------------------------------------------------------------------#
def get_all_domains():
    domList = []
    for idx in range( get_nb_domains() ):
        domList.append(idx)
    return domList
#--------------------------------------------------------------------------------------------#
def get_domains_list(pattern):
    block_list = []
    regexp = fnmatch.translate(pattern) ; # convert pattern to regular expression
    reobj = re.compile(regexp)
    for b in range( get_nb_domains() ):
        block_name = FHX_get_domain_name_(b)
        if (reobj.match(block_name)):
            block_list.append(b)
    return block_list
#--------------------------------------------------------------------------------------------#
def get_nb_domain_patches(idx):
    # ... Check domain index validity
    if (idx<0 or idx>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(idx)
    # ... Get nb of patches for domain idx
    return FHX_get_nb_domain_patches_(idx)



#--------------------------------------------------------------------------------------------#
#------------------------------ Characteristic Parameters -----------------------------------#
#--------------------------------------------------------------------------------------------#
def get_characteristic_length():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return L
#--------------------------------------------------------------------------------------------#
def set_characteristic_length(length):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(V,length,D,A,P,T)
    
#--------------------------------------------------------------------------------------------#
def get_characteristic_velocity():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return V
#--------------------------------------------------------------------------------------------#
def set_characteristic_velocity(velocity):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(velocity,L,D,A,P,T)

#--------------------------------------------------------------------------------------------#
def get_characteristic_density():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return D
#--------------------------------------------------------------------------------------------#
def set_characteristic_density(density):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(V,L,density,A,P,T)

#--------------------------------------------------------------------------------------------#
def get_characteristic_area():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return A
#--------------------------------------------------------------------------------------------#
def set_characteristic_area(area):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(V,L,D,area,P,T)

#--------------------------------------------------------------------------------------------#
def get_characteristic_pressure():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return P
#--------------------------------------------------------------------------------------------#
def set_characteristic_pressure(pressure):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(V,L,D,A,pressure,T)

#--------------------------------------------------------------------------------------------#
def get_characteristic_temperature():
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    return T
#--------------------------------------------------------------------------------------------#
def set_characteristic_temperature(temperature):
    V,L,D,A,P,T = FHX_get_characteristic_values_()
    FHX_set_characteristic_values_(V,L,D,A,P,temperature)



#--------------------------------------------------------------------------------------------#
#------------------------------ Fluid Model -------------------------------------------------#
#--------------------------------------------------------------------------------------------#
def select_fluid_from_database(blocks,fluid_name):
    rc=0
    if (type(blocks) is types.TupleType) or (type(blocks) is types.ListType):
        for index in blocks:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            rc=FHX_select_fluid_from_DB_(index,fluid_name)
    else:
        index=blocks
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        rc=FHX_select_fluid_from_DB_(index,fluid_name)

    if (rc == -1):
        raise ValueError,"Could not find fluid name : " + str(fluid_name)

#--------------------------------------------------------------------------------------------#
def get_fluid_name(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    fluid_name = FHX_get_fluid_model_name_(iBlock)
    return fluid_name

#--------------------------------------------------------------------------------------------#
#def set_fluid_name(iBlock,fluidName):
#    if (iBlock<0 or iBlock>=get_nb_domains()):
#        raise IndexError,"Domain index out of bounds : " + str(iBlock)
#    FHX_set_fluid_model_name_(iBlock,fluidName)

#--------------------------------------------------------------------------------------------#
def get_fluid_type(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    fluid_type = FHX_get_fluid_model_type_(iBlock)
    return fluid_type

#--------------------------------------------------------------------------------------------#
#def set_fluid_type(iBlock,fluidName):
#    if (iBlock<0 or iBlock>=get_nb_domains()):
#        raise IndexError,"Domain index out of bounds : " + str(iBlock)
#    FHX_set_fluid_model_type_(iBlock,fluidName)


#--------------------------------------------------------------------------------------------#
#------------------------------ CHT parameters ----------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
def get_block_type(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    block_type = FHX_get_block_type_(iBlock)
    return block_type

#--------------------------------------------------------------------------------------------#
def set_block_type(iBlock,blockType):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    FHX_set_block_type_(iBlock,blockType)

#--------------------------------------------------------------------------------------------#
def get_solid_conductivity_type(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    return results[0]

#--------------------------------------------------------------------------------------------#
def get_solid_conductivity_value(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    return results[1]

#--------------------------------------------------------------------------------------------#
def get_solid_conductivity_profile(iBlock):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    return results[2]

#--------------------------------------------------------------------------------------------#
def set_solid_conductivity_type(iBlock,lawFlag):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    nb = len(results[2])
    FHX_set_CHT_parameters_(iBlock,lawFlag,results[1],nb,results[2])

#--------------------------------------------------------------------------------------------#
def set_solid_conductivity_value(iBlock,value):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    nb = len(results[2])
    FHX_set_CHT_parameters_(iBlock,results[0],value,nb,results[2])

#--------------------------------------------------------------------------------------------#
def set_solid_conductivity_profile(iBlock,dataList):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "SOLID":
        raise IndexError,"Domain #" + str(iBlock) + " is not solid!"
    results = FHX_get_CHT_parameters_(iBlock)
    nb = len(dataList)
    FHX_set_CHT_parameters_(iBlock,results[0],results[1],nb,dataList)


#--------------------------------------------------------------------------------------------#
#------------------------------ Flow Model parameters ---------------------------------------#
#--------------------------------------------------------------------------------------------#

# =================================
# Get/Set time configuration:
# steady/unsteady  <==> iTimeAccurate_ = 0/1
# harmonic         <==> iNLH_ = 0/1
# =================================
STEADY   = 0
UNSTEADY = 1
HARMONIC = 2
#--------------------------------------------------------------------------------------------#
def get_time_configuration():
    # Global parameter => get value of first block.
    iBlock = 0
    iNLH          = get_parameter_value_('iNLH_',iBlock)
    iTimeAccurate = get_parameter_value_('iTimeAccurate_',iBlock)
    if (iNLH==1):
        return 2
    else:
        return iTimeAccurate

#--------------------------------------------------------------------------------------------#
def set_time_configuration(value):
    if (value==2):
        iTimeAccurate = 0
        iNLH          = 1
    else:
        if (value==0 or value==1):
            iTimeAccurate = value
            iNLH          = 0
        else:
            raise ValueError,"Wrong value for argument : should be 0 (=STEADY), 1 (=UNSTEADY) or 2 (=HARMONIC)"

    # Global parameter => set value for all blocks
    ##set_parameter_value_('iTimeAccurate_', get_all_domains(), iTimeAccurate)
    ##set_parameter_value_('iNLH_', get_all_domains(), iNLH)
    for iblock in range( get_nb_domains() ):
        print 'FHX_set_flow_model_time_configuration_( '+str(iblock)+', '+str(iTimeAccurate)+', '+str(iNLH)+')'
        FHX_set_flow_model_time_configuration_( iblock, iTimeAccurate, iNLH)

# =================================
# Get/Set mathematical model
#   Euler                                       <==> model_ = 1
#   Laminar                                     <==> model_ = 2
#
#   Turbulent                                   <==> model_ = 4
#        Spalart-Allmaras                       <==> turbModel_ = 1
#        SARC                                   <==> turbModel_ = 2
#        Spalart-Allmaras (Wall function)       <==> turbModel_ = 3
#        SARC (Wall function)                   <==> turbModel_ = 4
#        Spalart-Allmaras DDES                  <==> turbModel_ = 7
#        Spalart-Allmaras DDES (Wall function)  <==> turbModel_ = 8
#        Spalart-Allmaras IDDES                 <==> turbModel_ = 9
#        Spalart-Allmaras IDDES (Wall function) <==> turbModel_ = 10
#
#   Turbulent K-E                               <==> model_ = 5
#        extended wall function                 <==> turbModel_ = 1
#        low Re Yang-Shih (classic)             <==> turbModel_ = 3
#        low Re Yang-Shih (distance free)       <==> turbModel_ = 4
#        standard                               <==> turbModel_ = 9
#
#   Turbulent K-W                               <==> model_ = 5
#        M-SST                                  <==> turbModel_ = 5
#        Wilcox                                 <==> turbModel_ = 6
#        low-Re                                 <==> turbModel_ = 7
#        low Re with compressibility correction <==> turbModel_ = 8
#        M-SST (wall function)                  <==> turbModel_ = 11
#        M-SST (generalized transition)         <==> turbModel_ = 12
#
#   Turbulent LES                               <==> model_ = 8
#        Smagorinsky-Lilly LES                  <==> turbModel_ = 2
#        WALE LES                               <==> turbModel_ = 3
#
#   Turbulent EARSM                             <==> model_ = 9
#        BSL-EARSM                              <==> turbModel_ = 1
#        BSL-EARSM (Wall function)              <==> turbModel_ = 3
# =================================
EULER                                    = 100
LAMINAR                                  = 200
SPALART_ALLMARAS                         = 401
SARC                                     = 402
SPALART_ALLMARAS_EXT_WALL_FUNCTION       = 403
SARC_EXT_WALL_FUNCTION                   = 404
SPALART_ALLMARAS_DDES                    = 407
SPALART_ALLMARAS_DDES_EXT_WALL_FUNCTION  = 408
SPALART_ALLMARAS_IDDES                   = 409
SPALART_ALLMARAS_IDDES_EXT_WALL_FUNCTION = 410
K_EPSILON_EXT_WALL_FUNCTION              = 501
K_EPSILON_LOW_RE_YANG_SHIH_CLASSIC       = 503
K_EPSILON_LOW_RE_YANG_SHIH_DIST_FREE     = 504
K_OMEGA_M_SST                            = 505
K_OMEGA_WILCOX                           = 506
K_OMEGA_LOW_RE                           = 507
K_OMEGA_LOW_RE_WITH_COMPRESSIBILITY_CORR = 508
K_OMEGA_M_SST_EXT_WALL_FUNCTION          = 511
K_OMEGA_M_SST_GENERALIZED_TRANSITION     = 512
SMAW_LES                                 = 802
WALE_LES                                 = 803
S_BSL_EARSM                              = 901
S_BSL_EARSM_EXT_WALL_FUNCTION            = 903
#--------------------------------------------------------------------------------------------#
def get_mathematical_model(iBlock):
    model     = get_parameter_value_('model_',iBlock)
    turbModel = 0
    if (model>=4):
        turbModel = get_parameter_value_('turbModel_',iBlock)
    return (100*model+turbModel)
#--------------------------------------------------------------------------------------------#
def set_mathematical_model(iBlock,model_code):
    # Extract model and turb model from code
    model,turbModel = divmod(model_code,100)
    # Set mathematical model
    set_parameter_value_('model_',iBlock,model)
    set_parameter_value_('turbModel_',iBlock,turbModel)

# =================================
# Get/Set gravity activation flag
#   Gravity flag  <==>  iGravity_
# =================================
def get_gravity_flag(iBlock):
    return get_parameter_value_('iGravity_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_gravity_flag(iBlock,flag):
    set_parameter_value_('iGravity_',iBlock,flag)

# =================================
# Get/Set gravity h0
#   Gravity h0 <==>  gravity_coord_
# =================================
def get_gravity_h0(iBlock):
    h0 = get_parameter_value_('gravity_coord_',iBlock)
    return Point(h0[0], h0[1], h0[2])
#--------------------------------------------------------------------------------------------#
def set_gravity_h0(iBlock,point):
    h0 = [point.x, point.y, point.z]
    set_parameter_value_('gravity_coord_',iBlock,h0)

# =================================
# Get/Set gravity vector
#   Gravity vector <==>  gravity_vector_
# =================================
def get_gravity_vector(iBlock):
    g = get_parameter_value_('gravity_vector_',iBlock)
    return Vector(g[0], g[1], g[2])
#--------------------------------------------------------------------------------------------#
def set_gravity_vector(iBlock,vector):
    g = [vector.x, vector.y, vector.z]
    set_parameter_value_('gravity_vector_',iBlock,g)

# =================================
# Get/Set preconditioning
# preconditioning activated  <==> iPreconditioning_ = 1
# =================================
def get_preconditioning(iBlock):
    return get_parameter_value_('iPreconditioning_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning(iBlock,iPreconditioning):
    set_parameter_value_('iPreconditioning_',iBlock,iPreconditioning)

# =================================
# Get/Set reference parameters
#   Reference length     <==>  LRef_
#   Reference velocity   <==>  velRef_
# =================================
def get_reference_length(iBlock):
    return get_parameter_value_('LRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_reference_length(iBlock,LRef):
    set_parameter_value_('LRef_',iBlock,LRef)
# =================================
def get_reference_velocity(iBlock):
    return get_parameter_value_('velRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_reference_velocity(iBlock,VRef):
    set_parameter_value_('velRef_',iBlock,VRef)
    # Update output reference velocity
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        for index in iBlock:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            flag = get_parameter_value_('out_userDefinedRef_',index)
            if (flag==0):
                set_parameter_value_('out_velRef_',index,VRef)
    else:
        index=iBlock
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        FHX_set_parameter_value_('out_velRef_',index,VRef)



#--------------------------------------------------------------------------------------------#
#------------------------------ Rotating machinery  -----------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_rotating_machinery_flag(iBlock):
    isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(iBlock)
    return isRotating
#--------------------------------------------------------------------------------------------#
def get_rotating_machinery_rotation_speed(iBlock):
    isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(iBlock)
    return rotSpeed
#--------------------------------------------------------------------------------------------#
def get_rotating_machinery_rotation_axis(iBlock):
    isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(iBlock)
    return Vector(dirX,dirY,dirZ)
#--------------------------------------------------------------------------------------------#
def get_rotating_machinery_rotation_center(iBlock):
    isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(iBlock)
    return Point(cX,cY,cZ)

#--------------------------------------------------------------------------------------------#
def set_rotating_machinery_flag(iBlock,flag):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        for index in iBlock:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
            FHX_set_rotating_machinery_parameters_(index,
                                                   flag,
                                                   rotSpeed,
                                                   dirX,dirY,dirZ,
                                                   cX,cY,cZ)
    else:
        index=iBlock
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
        FHX_set_rotating_machinery_parameters_(index,
                                               flag,
                                               rotSpeed,
                                               dirX,dirY,dirZ,
                                               cX,cY,cZ)

#--------------------------------------------------------------------------------------------#
def set_rotating_machinery_rotation_speed(iBlock,speed):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        for index in iBlock:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
            FHX_set_rotating_machinery_parameters_(index,
                                                   isRotating,
                                                   speed,
                                                   dirX,dirY,dirZ,
                                                   cX,cY,cZ)
    else:
        index=iBlock
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
        FHX_set_rotating_machinery_parameters_(index,
                                               isRotating,
                                               speed,
                                               dirX,dirY,dirZ,
                                               cX,cY,cZ)
#--------------------------------------------------------------------------------------------#
def set_rotating_machinery_rotation_axis(iBlock,rotAxis):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        for index in iBlock:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
            FHX_set_rotating_machinery_parameters_(index,
                                                   isRotating,
                                                   rotSpeed,
                                                   rotAxis.x,rotAxis.y,rotAxis.z,
                                                   cX,cY,cZ)
    else:
        index=iBlock
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
        FHX_set_rotating_machinery_parameters_(index,
                                               isRotating,
                                               rotSpeed,
                                               rotAxis.x,rotAxis.y,rotAxis.z,
                                               cX,cY,cZ)
            
#--------------------------------------------------------------------------------------------#
def set_rotating_machinery_rotation_center(iBlock,rotCenter):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        for index in iBlock:
            if (index<0 or index>=get_nb_domains()):
                raise IndexError,"Domain index out of bounds : " + str(index)
            isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
            FHX_set_rotating_machinery_parameters_(index,
                                                   isRotating,
                                                   rotSpeed,
                                                   dirX,dirY,dirZ,
                                                   rotCenter.x,rotCenter.y,rotCenter.z)
    else:
        index=iBlock
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        isRotating,rotSpeed,dummy,dirX,dirY,dirZ,cX,cY,cZ = FHX_get_rotating_machinery_parameters_(index)
        FHX_set_rotating_machinery_parameters_(index,
                                               isRotating,
                                               rotSpeed,
                                               dirX,dirY,dirZ,
                                               rotCenter.x,rotCenter.y,rotCenter.z)




#--------------------------------------------------------------------------------------------#
#------------------------------ Numerical Model parameters ----------------------------------#
#--------------------------------------------------------------------------------------------#

# =================================
# Get/Set CPU booster activation flag
#   CPU booster flag  <==>  iCPUBooster_
# =================================
def get_CPU_booster_flag():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('iCPUBooster_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_CPU_booster_flag(flag):
    # Global parameters => set value for all blocks
    # set_parameter_value_('iCPUBooster_',get_all_domains(),flag)
    numBlocks = get_nb_domains()
    for i in range( numBlocks ):
        FHX_set_num_model_cpu_booster_(i,flag)

# =================================
# Get/Set CFL number:
#   CFL  <==> tm_cflV_    (classical)
#   CFL  <==> tm_cflVCPB_ (CPU booster switch on)
# =================================
def get_CFL_number(iBlock):
    return FHX_get_num_model_cfl_number_(iBlock)
#--------------------------------------------------------------------------------------------#
def set_CFL_number(iBlock,CFL):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        FHX_set_num_model_cfl_number_(index,CFL)

# =================================
# Get/Set nb of multigrid levels:
#   Nb of multigrid levels <==> mg_nbGrid_
# =================================
def get_MG_level_number():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('mg_nbGrid_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_level_number(nb):
    # Global parameter => set value for all blocks
    set_parameter_value_('mg_nbGrid_',get_all_domains(),nb)

# =================================
# Get/Set multigrid activation:
#   Multigrid activation  <==> tm_iFMG_
# =================================
def get_MG_flag():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('tm_iFMG_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_flag(iFMG):
    # Global parameters => set value for all blocks
    set_parameter_value_('tm_iFMG_',get_all_domains(),iFMG)

# =================================
# Get/Set sweeps on each MG level:
#   Sweeps <==> mg_nbSweepfc_
# =================================
def get_MG_number_of_sweeps():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('mg_nbSweepfc_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_number_of_sweeps(sweeps):
    # Global parameters => set value for all blocks
    set_parameter_value_('mg_nbSweepfc_',get_all_domains(),sweeps)

# =================================
# Get/Set multigrid correction damping:
#   Correction damping <==> mg_iCoorSmoo_
# =================================
def get_MG_correction_damping():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('mg_iCorrSmoo_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_correction_damping(iCoorSmoo):
    # Global parameters => set value for all blocks
    set_parameter_value_('mg_iCorrSmoo_',get_all_domains(),iCoorSmoo)

# =================================
# Get/Set multigrid number of cycles per grid level
#   Number of cycle <==> tm_fmg_nbIter_    (FMG CPU booster switched off)
#   Number of cycle <==> tm_fmg_nbIterCPB_ (FMG CPU booster switched on)
# =================================
def get_MG_number_of_cycles():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
        return get_parameter_value_('tm_fmg_nbIterCPB_',iBlock)
    else:
        return get_parameter_value_('tm_fmg_nbIter_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_number_of_cycles(n):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
        set_parameter_value_('tm_fmg_nbIterCPB_',get_all_domains(),n)
    else:
        set_parameter_value_('tm_fmg_nbIter_',get_all_domains(),n)
        
# =================================
# Get/Set convergence criteria on each grid level
#   Number of cycle <==> tm_fmg_resCri_    (FMG CPU booster switch off)
#   Number of cycle <==> tm_fmg_resCriCPB_ (FMG CPU booster switch on)
# =================================
def get_MG_convergence_criteria():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
        return get_parameter_value_('tm_fmg_resCriCPB_',iBlock)
    else:
        return get_parameter_value_('tm_fmg_resCri_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_convergence_criteria(resMax):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
        set_parameter_value_('tm_fmg_resCriCPB_',get_all_domains(),resMax)
    else:
        set_parameter_value_('tm_fmg_resCri_',get_all_domains(),resMax)
        
# =================================
# Get/Set dual time step convergence criteria
#   Convergence criteria <==> ta_tm_resRed_    (CPU booster switched off)
#   Convergence criteria <==> ta_tm_resRedCPB_ (CPU booster switched on)
# =================================
def get_MG_dual_convergence_criteria():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1:
        return get_parameter_value_('ta_tm_resRedCPB_',iBlock)
    else:
        return get_parameter_value_('ta_tm_resRed_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_dual_convergence_criteria(resMax):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1:
        set_parameter_value_('ta_tm_resRedCPB_',get_all_domains(),resMax)
    else:
        set_parameter_value_('ta_tm_resRed_',get_all_domains(),resMax)
        
# =================================
# Get/Set dual time step max number of inner iterations
#   Maximum iterations <==> ta_tm_itMax_    (CPU booster switched off)
#   Maximum iterations <==> ta_tm_itMaxCPB_ (CPU booster switched on)
# =================================
def get_MG_dual_number_of_iterations():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1:
        return get_parameter_value_('ta_tm_itMaxCPB_',iBlock)
    else:
        return get_parameter_value_('ta_tm_itMax_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_dual_number_of_iterations(itMax):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1:
        set_parameter_value_('ta_tm_itMaxCPB_',get_all_domains(),itMax)
    else:
        set_parameter_value_('ta_tm_itMax_',get_all_domains(),itMax)
        
# =================================
# Get/Set CPU booster activation flag on each grid level
#   Number of cycle <==> fmg_iCPUBooster_
# =================================
def get_MG_CPU_booster_flag():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('fmg_iCPUBooster_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_CPU_booster_flag(flag):
    # Global parameters => set value for all blocks
    set_parameter_value_('fmg_iCPUBooster_',get_all_domains(),flag)

# =================================
# Get/Set CFL on each grid level
#   CFL number <==> tm_fmg_cflV_    (FMG CPU booster switch off)
#   CFL number <==> tm_fmg_cflVCPB_ (FMG CPU booster switch on)
# =================================
def get_MG_CFL_number(*args):
    if len(args)==0:
        # Global parameter => get value of first block (backward compatibility)
        iBlock = 0
    else:
        # Local parameter => get value of specified block
        iBlock = args[0]
    if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
        return get_parameter_value_('tm_fmg_cflVCPB_',iBlock)
    else:
        return get_parameter_value_('tm_fmg_cflV_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_MG_CFL_number(*args):
    if len(args)==1:
        # Global parameter => set value for all blocks (backward compatibility)
        cfl=args[0]
        if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
            set_parameter_value_('tm_fmg_cflVCPB_',get_all_domains(),cfl)
        else:
            set_parameter_value_('tm_fmg_cflV_',get_all_domains(),cfl)
    else:
        # Local parameter => set value for specified block
        iBlock = args[0]
        cfl    = args[1]
        if get_CPU_booster_flag()==1 and get_MG_CPU_booster_flag()==1:
            set_parameter_value_('tm_fmg_cflVCPB_',iBlock,cfl)
        else:
            set_parameter_value_('tm_fmg_cflV_',iBlock,cfl)

# =================================
# Get/Set multigrid parameters:
#   Nb of grids max                         <==> UHexaBlock->nbOfLevelMax
#   Multigrid type			    <==> mg_type_
#   Smoothing				    <==> tm_iResSmoo_
#   CFL smoothing multipl. factor	    <==> tm_smooCfl_
#   Multigrid activation                    <==> tm_iFMG_
#   Max nb of cycles per grid level         <==> tm_fmg_nbIter_
#   Convergence criteria on each grid level <==> tm_fmg_resCri_
#   CFL on each grid level                  <==> tm_fmg_cfl_
# =================================
def get_multigrid_parameters():
    # Global parameters => get value of first block.
    iBlock = 0
    nbGrid,nbGridMax,iCoorSmoo,iFMG = FHX_get_num_model_multigrid_parameters_(iBlock)
    return nbGrid,nbGridMax,iCoorSmoo,iFMG
#--------------------------------------------------------------------------------------------#
def set_multigrid_parameters(nbGrid,iCoorSmoo,iFMG):
    # Global parameters => set value for all blocks
    numBlocks = get_nb_domains()
    for i in range( numBlocks ):
        FHX_set_num_model_multigrid_parameters_(i,nbGrid,iCoorSmoo,iFMG)

# =================================
# Get/Set time stepping technique (unsteady)
#   Dual time stepping     <==> ta_iGlobTimeStepping_ = 0
#   Explicit time stepping <==> ta_iGlobTimeStepping_ = 1
# =================================
DUAL_TIME_STEPPING     = 0
EXPLICIT_TIME_STEPPING = 1
#--------------------------------------------------------------------------------------------#
def get_time_stepping_method():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('ta_iGlobTimeStepping_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_time_stepping_method(method):
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_iGlobTimeStepping_',get_all_domains(),method)

# =================================
# Get/Set numerical scheme:
#   "Central"        <==> spaceScheme_ = 1
#   "Central matrix" <==> spaceScheme_ = 2
#   "Roe upwind"     <==> spaceScheme_ = 4
#   "LDFSS upwind"   <==> spaceScheme_ = 7
# =================================
CENTRAL_SCHEME        = 1
CENTRAL_MATRIX_SCHEME = 2
ROE_UPWIND_SCHEME     = 4
LDFSS_UPWIND_SCHEME   = 7
#--------------------------------------------------------------------------------------------#
def get_numerical_scheme(iBlock):
    return get_parameter_value_('spaceScheme_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_numerical_scheme(iBlock,scheme):
    set_parameter_value_('spaceScheme_',iBlock,scheme)

# =================================
# Get/Set numerical scheme accuracy:
#   "1st order" <==> spc_accuracy_ = 1
#   "2nd order" <==> spc_accuracy_ = 2
# =================================
FIRST_ORDER  = 1
SECOND_ORDER = 2
MIXED_ORDER  = 3
#--------------------------------------------------------------------------------------------#
def get_numerical_scheme_accuracy(iBlock):
    return get_parameter_value_('spc_accuracy_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_numerical_scheme_accuracy(iBlock,accuracy):
    set_parameter_value_('spc_accuracy_',iBlock,accuracy)

# =================================
# Get/Set mixed-order (to be used with LDFSS upwind)
#   "order" <==> rAllMachMixedOrderValue_
# =================================
def get_numerical_scheme_mixed_order(iBlock):
    return get_parameter_value_('rAllMachMixedOrderValue_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_numerical_scheme_mixed_order(iBlock,orderValue):
    set_parameter_value_('rAllMachMixedOrderValue_',iBlock,orderValue)

    # =================================
# Get/Set preconditioning method:
#   Hakimi <==> iMerklePreconditioning_ = 0
#   Merkle <==> iMerklePreconditioning_ = 1
# =================================
HAKIMI = 0
MERKLE = 1
#--------------------------------------------------------------------------------------------#
def get_preconditioning_method(iBlock):
    return get_parameter_value_('iMerklePreconditioning_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning_method(iBlock,method):
    set_parameter_value_('iMerklePreconditioning_',iBlock,method)

# =================================
# Get/Set preconditioning Beta:
#   beta <==> preco_beta_
# =================================
def get_preconditioning_beta(iBlock):
    return get_parameter_value_('preco_beta_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning_beta(iBlock,beta):
    set_parameter_value_('preco_beta_',iBlock,beta)

# =================================
# Get/Set preconditioning characteristic velocity + local scaling:
#   charact. velocity <==> preco_qRef_
# =================================
def get_preconditioning_characteristic_velocity(iBlock):
    velocity = get_parameter_value_('preco_qRef_',iBlock)
    if velocity<0 :
        return abs(velocity),1
    else:
        return abs(velocity),0

#--------------------------------------------------------------------------------------------#
def set_preconditioning_characteristic_velocity(*args):
    iBlock  =args[0]
    velocity=args[1]

    if len(args)==2:
        # ... NEW arguments: iblock, velocity
        if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
            blockList = iBlock
        else:
            blockList = [iBlock]
        for index in blockList:
            localScaling = get_preconditioning_local_scaling(index)
            if localScaling==1:
                set_parameter_value_('preco_qRef_',index,(-1)*(abs(velocity)))
            else:
                set_parameter_value_('preco_qRef_',index,abs(velocity))

    elif len(args)==3:
        # ... OLD arguments: iblock, velocity, local scaling
        localScaling=args[2]
        if localScaling==1:
            set_parameter_value_('preco_qRef_',iBlock,(-1)*(abs(velocity)))
        else:
            set_parameter_value_('preco_qRef_',iBlock,abs(velocity))
        
# =================================
# Get/Set preconditioning local scaling:
#   local scaling <==> sign(preco_qRef_) ('+': OFF,  '-':ON)
# =================================
def get_preconditioning_local_scaling(iBlock):
    velocity = get_parameter_value_('preco_qRef_',iBlock)
    if velocity<0 :
        return 1
    else:
        return 0
#--------------------------------------------------------------------------------------------#
def set_preconditioning_local_scaling(iBlock,localScaling):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        velocity = get_parameter_value_('preco_qRef_',index)
        if localScaling==1:
            set_parameter_value_('preco_qRef_',index,(-1)*(abs(velocity)))
        else:
            set_parameter_value_('preco_qRef_',index,abs(velocity))
        
# =================================
# Get/Set preconditioning gauge parameters activation
#   gauge flag <==> igauge_p_T_
# =================================
def get_preconditioning_gauge_parameters_activation(iBlock):
    return get_parameter_value_('igauge_p_T_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning_gauge_parameters_activation(iBlock,flag):
    set_parameter_value_('igauge_p_T_',iBlock,flag)

# =================================
# Get/Set preconditioning gauge pressure
#   gauge pressure <==> preco_pRef_
# =================================
def get_preconditioning_gauge_pressure(iBlock):
    return get_parameter_value_('preco_pRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning_gauge_pressure(iBlock,p):
    set_parameter_value_('preco_pRef_',iBlock,p)

# =================================
# Get/Set preconditioning gauge temperature
#   gauge temperature <==> preco_TRef_
# =================================
def get_preconditioning_gauge_temperature(iBlock):
    return get_parameter_value_('preco_TRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_preconditioning_gauge_temperature(iBlock,T):
    set_parameter_value_('preco_TRef_',iBlock,T)



#--------------------------------------------------------------------------------------------#
#------------------------------ Output parameters -------------------------------------------#
#--------------------------------------------------------------------------------------------#
EXTERNAL_FLOW  = 0
INTERNAL_FLOW  = 1
TURBOMACHINERY = 2
#--------------------------------------------------------------------------------------------#
def get_outputs_flow_configuration(iBlock):
    return FHX_get_outputs_flow_configuration_(iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_flow_configuration(iBlock,flag):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        FHX_set_outputs_flow_configuration_(index,flag)
#--------------------------------------------------------------------------------------------#
def get_outputs_external_lift(iBlock):
    momentCenter,liftDir,dragDir,momentDir = FHX_get_outputs_external_parameters_(iBlock)
    return Vector(liftDir[0],liftDir[1],liftDir[2])
#--------------------------------------------------------------------------------------------#
def set_outputs_external_lift(iBlock,liftDir):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        _momentCenter,_liftDir,_dragDir,_momentDir = FHX_get_outputs_external_parameters_(index)
        FHX_set_outputs_external_parameters_(index,
                                             [_momentCenter[0],_momentCenter[1],_momentCenter[2]],
                                             [liftDir.x,liftDir.y,liftDir.z],
                                             [_dragDir[0],_dragDir[1],_dragDir[2]],
                                             [_momentDir[0],_momentDir[1],_momentDir[2]])
#--------------------------------------------------------------------------------------------#
def get_outputs_external_drag(iBlock):
    momentCenter,liftDir,dragDir,momentDir = FHX_get_outputs_external_parameters_(iBlock)
    return Vector(dragDir[0],dragDir[1],dragDir[2])
#--------------------------------------------------------------------------------------------#
def set_outputs_external_drag(iBlock,dragDir):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        _momentCenter,_liftDir,_dragDir,_momentDir = FHX_get_outputs_external_parameters_(index)
        FHX_set_outputs_external_parameters_(index,
                                             [_momentCenter[0],_momentCenter[1],_momentCenter[2]],
                                             [_liftDir[0],_liftDir[1],_liftDir[2]],
                                             [ dragDir.x,  dragDir.y, dragDir.z],
                                             [_momentDir[0],_momentDir[1],_momentDir[2]])
#--------------------------------------------------------------------------------------------#
def get_outputs_external_moment(iBlock):
    momentOri,liftDir,dragDir,momentDir = FHX_get_outputs_external_parameters_(iBlock)
    return Point( momentOri[0], momentOri[1], momentOri[2]), Vector( momentDir[0], momentDir[1], momentDir[2])
#--------------------------------------------------------------------------------------------#
def set_outputs_external_moment(iBlock,momentCenter,momentDir):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        _momentCenter,_liftDir,_dragDir,_momentDir = FHX_get_outputs_external_parameters_(index)
        FHX_set_outputs_external_parameters_(index,
                                             [momentCenter.x,momentCenter.y,momentCenter.z],
                                             [_liftDir[0],_liftDir[1],_liftDir[2]],
                                             [_dragDir[0],_dragDir[1],_dragDir[2]],
                                             [momentDir.x,momentDir.y,momentDir.z])
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_flag(iBlock):
    return get_parameter_value_('out_userDefinedRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_flag(iBlock,flag):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_userDefinedRef_',iBlock,flag)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_density(iBlock):
    return get_parameter_value_('out_massVolRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_density(iBlock,densRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_massVolRef_',iBlock,densRef)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_velocity(iBlock):
    return get_parameter_value_('out_velRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_velocity(iBlock,velRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_velRef_',iBlock,velRef)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_length(iBlock):
    return get_parameter_value_('out_lengthRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_length(iBlock,lengthRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_lengthRef_',iBlock,lengthRef)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_area(iBlock):
    return get_parameter_value_('out_areaRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_area(iBlock,areaRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_areaRef_',iBlock,areaRef)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_pressure(iBlock):
    return get_parameter_value_('out_pRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_pressure(iBlock,pRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_pRef_',iBlock,pRef)
#--------------------------------------------------------------------------------------------#
def get_outputs_reference_temperature(iBlock):
    return get_parameter_value_('out_TRef_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_outputs_reference_temperature(iBlock,TRef):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_('out_TRef_', iBlock, TRef)





#--------------------------------------------------------------------------------------------#
#------------------------------ Output format -----------------------------------------------#
#--------------------------------------------------------------------------------------------#
def enable_output_format( format_type ):
    # Global parameters => set value for all blocks
    if (format_type == "CFVIEW"):
        set_parameter_value_('out_cfview_',get_all_domains(),1)
    elif (format_type == "ENSIGHT"):
        set_parameter_value_('out_ensight_',get_all_domains(),1)
    elif (format_type == "CGNS"):
        set_parameter_value_('out_cgns_',get_all_domains(),1)
    else :
        raise ValueError,"Wrong value for 'format_type' : should be 'CFVIEW', 'ENSIGHT' or 'SMOOTH'"
#--------------------------------------------------------------------------------------------#
def disable_output_format( format_type ):
    # Global parameters => set value for all blocks
    if (format_type == "CFVIEW"):
        set_parameter_value_('out_cfview_',get_all_domains(),0)
    elif (format_type == "ENSIGHT"):
        set_parameter_value_('out_ensight_',get_all_domains(),0)
    elif (format_type == "CGNS"):
        set_parameter_value_('out_cgns_',get_all_domains(),0)
    else :
        raise ValueError,"Wrong value for 'format_type' : should be 'CFVIEW', 'ENSIGHT' or 'SMOOTH'"



#--------------------------------------------------------------------------------------------#
#------------------------------ Outputs selection -------------------------------------------#
#--------------------------------------------------------------------------------------------#
def select_output( key_name ):
    # Global parameters => set value for all blocks
    for index in get_all_domains():
        FHX_select_quantity_(index,key_name)
    FHX_update_outputs_()
    FHX_delete_copy_outputs_()
#--------------------------------------------------------------------------------------------#
def unselect_output( key_name ):
    # Global parameters => set value for all blocks
    for index in get_all_domains():
        FHX_unselect_quantity_(index,key_name)
    FHX_update_outputs_()
    FHX_delete_copy_outputs_()




#--------------------------------------------------------------------------------------------#
#------------------------------ Launching mode ----------------------------------------------#
#--------------------------------------------------------------------------------------------#
SERIAL   = 0
PARALLEL = 1
#--------------------------------------------------------------------------------------------#
def get_launching_mode():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('iParallel_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_launching_mode(mode):
    # Global parameters => set value for all blocks
    set_parameter_value_('iParallel_',get_all_domains(),mode)

# =================================
# Get/Set load balancing method
#   1: forbid multiple domains on a single proc
#   2: allow  multiple domains on a single proc 
# =================================
def get_load_balancing_method():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('loadBalancingMode_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_load_balancing_method(method):
    # Global parameters => set value for all blocks
    set_parameter_value_('loadBalancingMode_',get_all_domains(),method)

#--------------------------------------------------------------------------------------------#
def get_number_of_processes():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('nbProcs_',iBlock)

# ---
# For backward:
# ---
def get_number_of_processors():
    return get_number_of_processes()

#--------------------------------------------------------------------------------------------#
def set_number_of_processes(*args):

    # ------------------------------------------------
    # OLD IMPLEMENTATION
    # ------------------------------------------------
##    parts = FHX_compute_default_partitioning_(nproc)
##    print 'parts: ' + str(parts)
##    weightedFlags = []
##    weights       = []
##    for i in range( get_nb_domains() ):
##        weightedFlags.append(0)
##        for j in range( parts[i] ):
##            weights.append( round(1000.0/parts[i])/10.0 )
##    FHX_set_partition_parameters_(parts,weights,weightedFlags)

    # ------------------------------------------------
    # NEW IMPLEMENTATION
    # ------------------------------------------------
    # ... Get automatic partitioning parameters
    nproc = args[0]
    loadBalancingMethod = get_load_balancing_method()
    if len(args)==2 :
        loadBalancingMethod = args[1]
        set_parameter_value_('loadBalancingMode_',get_all_domains(),loadBalancingMethod)

    # ... Compute automatic partitioning
    partsNEW = FHX_compute_default_partitioningNEW_(loadBalancingMethod,nproc)
    print 'partsNEW: '+str(partsNEW)
    nbPartitions  = []
    weights       = []
    weightedFlags = []
    procList      = []
    nbProcs       = 0
    grpIdx        = 1
    for i in range(len(partsNEW)):
        blocks = partsNEW[i][0]
        procs  = partsNEW[i][1]

        groupName = "none"
        if (len(blocks) > 1):
            groupName = "Group_"+str(grpIdx)
            grpIdx = grpIdx+1

        procList.append([groupName,len(blocks),partsNEW[i][0],len(procs),procs])

        if (len(blocks) == 1):
            nbPartitions.insert(blocks[0],len(procs))
        else:
            for bid in blocks:
                nbPartitions.insert(bid,1)
                
        if (len(blocks)>1):
            nbProcs = nbProcs + 1
        else:
            nbProcs = nbProcs + len(procs)

    for i in range( get_nb_domains() ):
        weightedFlags.append(0)
        for j in range( nbPartitions[i] ):
            weights.append( round(1000.0/nbPartitions[i])/10.0 )

    print 'nbPartitions: ' + str(nbPartitions)
    print 'procList: ' + str(procList)
    print 'nbProcs:  ' + str(nbProcs)
    print 'nproc: '    + str(nproc)
    ##FHX_set_partition_parameters_(nbPartitions,weights,weightedFlags)
    ##FHX_set_partition_parametersNEW_(nbProcs,len(procList),procList)

    FHX_set_load_balancing_(loadBalancingMethod,
                            nbProcs,len(procList),procList,nbPartitions,weightedFlags,weights)

# ---
# For backward:
# ---
def set_number_of_processors(*args):
    set_number_of_processes(*args)

#--------------------------------------------------------------------------------------------#
def get_load_balancing():
     result = FHX_get_load_balancing_()
     print 'result: '+str(result)

     # ---
     # Distribution
     # ---
     distribution = result[1]
     print '   distribution: '+str(distribution)

     # ---
     # Partitions and Weights
     # ---
     # Number of partitions for each domain
     partitions   = result[0][0]

     # Weight flag for each domain
     iPartWeights = result[0][1]
     print '   iPartWeights: '+str(iPartWeights)

     # Weights for each partition
     partWeights  = result[0][2]
     print '   partWeights : '+str(partWeights)

     # Create 'weights' list: Weight flags + Weights
     weights = []
     weights.append(iPartWeights)
     weights.append(partWeights)
     print '   weights : '+str(weights)
     
     return distribution, partitions, weights

     
#--------------------------------------------------------------------------------------------#
def set_load_balancing(distribution,weights):

    # Get load balancing method
    loadBalancingMethod = get_load_balancing_method()

    # Extract information from distribution
    nbItems = len(distribution)

    nbProcs       = 0
    procsOfBlock  = []
    nbPart        = 0
    nbPartitions  = []
    for i in range(nbItems):
        item = distribution[i]
        groupName = item[0] ; print 'groupName: '+groupName
        blocks    = item[1] ; print 'blocks: '   +str(blocks)
        procIDs   = item[2] ; print 'procIDs: '  +str(procIDs)

        procsOfBlock.append([groupName,len(blocks),blocks,len(procIDs),procIDs])
        
        if (len(blocks)>1):
            # This is a group
            nbProcs = nbProcs + len(blocks)
            # Check: load balancing method should be 2
            if (loadBalancingMethod==1):
                raise ValueError, "Load balancing method is 1, not compatible with multiple domains on a same processor."
        else:
            nbProcs = nbProcs + 1

        if (len(blocks) == 1):
            nbPart = nbPart + len(procIDs)
            nbPartitions.insert(blocks[0],len(procIDs))
        else:
            for bid in blocks:
                print '   bid: '+str(bid)
                nbPart = nbPart + 1
                nbPartitions.insert(bid,1)
                

    iPartWeights = weights[0]
    partWeights  = weights[1]
    print '   iPartWeights: '+str(iPartWeights)
    print '   partWeights : '+str(partWeights)
    FHX_set_load_balancing_(loadBalancingMethod,
                            nbProcs,nbItems,procsOfBlock,nbPartitions,iPartWeights,partWeights)

#--------------------------------------------------------------------------------------------#
#------------------------------ Control variables -------------------------------------------#
#--------------------------------------------------------------------------------------------#

# =================================
# Get/Set maximum number of iteration (steady)
#   Maximum iterations <==> tm_itMax_    (CPU booster switched off)
#   Maximum iterations <==> tm_itMaxCPB_ (CPU booster switched on)
# =================================
def get_nb_iter_max():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1:
        return get_parameter_value_('tm_itMaxCPB_',iBlock)
    else:
        return get_parameter_value_('tm_itMax_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_nb_iter_max(itMax):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1:
        set_parameter_value_('tm_itMaxCPB_',get_all_domains(),itMax)
    else:
        set_parameter_value_('tm_itMax_',get_all_domains(),itMax)
        
# =================================
# Get/Set convergence criteria (steady)
#   Maximum iterations <==> tm_resRed_    (CPU booster switched off)
#   Maximum iterations <==> tm_resRedCPB_ (CPU booster switched on)
# =================================
def get_convergence_criteria():
    # Global parameters => get value of first block.
    iBlock = 0
    if get_CPU_booster_flag()==1:
        return get_parameter_value_('tm_resRedCPB_',iBlock)
    else:
        return get_parameter_value_('tm_resRed_',iBlock)
    
#--------------------------------------------------------------------------------------------#
def set_convergence_criteria(resRed):
    # Global parameters => set value for all blocks
    if get_CPU_booster_flag()==1:
        set_parameter_value_('tm_resRedCPB_',get_all_domains(),resRed)
    else:
        set_parameter_value_('tm_resRed_',get_all_domains(),resRed)
        
# =================================
# Get/Set physical time step (unsteady)
# =================================
def get_physical_time_step():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('ta_physTimeStep_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_physical_time_step(physTimeStep):
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_physTimeStep_',get_all_domains(),physTimeStep)

# =================================
# Get/Set number of time steps (unsteady)
# =================================
def get_nb_of_time_steps():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('ta_nbIter_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_nb_of_time_steps(nbTimeStep):
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_nbIter_',get_all_domains(),nbTimeStep)

# =================================
# Get/Set CFL number (unsteady + 'Explicit time stepping')
# =================================
def get_time_step_CFL():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('ta_physCFL_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_time_step_CFL(CFL):
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_physCFL_',get_all_domains(),CFL)

# =================================
# Get/Set maximum duration (unsteady + 'Explicit time stepping')
# =================================
def get_maximum_duration():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('ta_physGlobTimeComp_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_maximum_duration(maxDuration):
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_physGlobTimeComp_',get_all_domains(),maxDuration)

# =================================
# Enable/Disable solution averaging output (unsteady)
# =================================
def enable_time_averaged_solution(afterNbIter):
    if (afterNbIter < 0):
        raise ValueError, 'unexpected negative value ' +str(afterNbIter)+ ' for number of time steps.'
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_avg_iter_',get_all_domains(),afterNbIter)
#--------------------------------------------------------------------------------------------#
def disable_time_averaged_solution():
    # Global parameters => set value for all blocks
    set_parameter_value_('ta_avg_iter_',get_all_domains(),-1)
#--------------------------------------------------------------------------------------------#
def get_beginning_time_step_for_averaged_solution():
    # Global parameters => get value of first block.
    iBlock = 0
    value = get_parameter_value_('ta_avg_iter_',iBlock)
    return value


# =================================
# Get/Set output writing frequency (steady/unsteady)
# =================================
def get_output_writing_frequency():
    # Global parameters => get value of first block.
    iBlock = 0
    is_unsteady = get_time_configuration()
    if not is_unsteady :
        return get_parameter_value_('out_writeInterval_',iBlock)
    else :
        return get_parameter_value_('out_writeInterval_ta_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_output_writing_frequency(freq):
    # Global parameters => set value for all blocks
    is_unsteady = get_time_configuration()
    if not is_unsteady :
        set_parameter_value_('out_writeInterval_',get_all_domains(),freq)
    else :
        set_parameter_value_('out_writeInterval_ta_',get_all_domains(),freq)


# =================================
# Get/Set expert_parameter
# =================================
def get_expert_parameter(iBlock,param_name):
    return get_parameter_value_(param_name,iBlock)
#--------------------------------------------------------------------------------------------#
def set_expert_parameter(iBlock,param_name,value):
    if (type(iBlock) is types.TupleType) or (type(iBlock) is types.ListType):
        blockList = iBlock
    else:
        blockList = [iBlock]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        set_parameter_value_(param_name,iBlock,value)



#--------------------------------------------------------------------------------------------#
#------------------------------ Porous Media Module parameters ------------------------------#
#--------------------------------------------------------------------------------------------#
DARCY_LAW    = 1
ERGUN_LAW    = 2
INTEGRAL_LAW = 3

CARMAN_KOZENY_FORMULA        = 0
USER_DEFINED_HOMOGENEOUS     = 1
USER_DEFINED_NON_HOMOGENEOUS = 2

# =================================
# Enable/Disable POROUS MEDIA module
# =================================
#--------------------------------------------------------------------------------------------#
def enable_porous_media_computing(iBlock):
    set_parameter_value_('iPorMed_',iBlock,1)
#--------------------------------------------------------------------------------------------#
def disable_porous_media_computing(iBlock):
    set_parameter_value_('iPorMed_',iBlock,0)

# =================================
# Get/Set POROUS MEDIA model
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_model(iBlock):
    return get_parameter_value_('iPorMedModel_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_porous_media_model(iBlock,model):
    set_parameter_value_('iPorMedModel_',iBlock,model)

# =================================
# Get/Set DARCY law options
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_darcy_option(iBlock):
    return get_parameter_value_('iPorMed_Darcy_Opt_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_porous_media_darcy_option(iBlock,option):
    set_parameter_value_('iPorMed_Darcy_Opt_',iBlock,option)

# =================================
# Get/Set DARCY Carman-Kozeny parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_darcy_carman_kozeny_parameters(iBlock):
    porosity         = get_parameter_value_('darcy_Porosity_',iBlock)
    specificSurfArea = get_parameter_value_('darcy_specificSurfArea_',iBlock)
    return porosity , specificSurfArea
#--------------------------------------------------------------------------------------------#
def set_porous_media_darcy_carman_kozeny_parameters(iBlock,porosity,specificSurfArea):
    set_parameter_value_('darcy_Porosity_',iBlock,porosity)
    set_parameter_value_('darcy_specificSurfArea_',iBlock,specificSurfArea)

# =================================
# Get/Set DARCY homogeneous parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_darcy_homogeneous_parameters(iBlock):
    return get_parameter_value_('darcy_kPrim_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_porous_media_darcy_homogeneous_parameters(iBlock,kPrim):
    set_parameter_value_('darcy_kPrim_',iBlock,kPrim)

# =================================
# Get/Set DARCY non-homogeneous parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_darcy_nonhomogeneous_parameters(iBlock):
    kPrim  = get_parameter_value_('darcy_aniso_kPrim_' ,iBlock)
    ksiDir = get_parameter_value_('darcy_aniso_ksiDir_',iBlock)
    etaDir = get_parameter_value_('darcy_aniso_etaDir_',iBlock)
    return kPrim,ksiDir,etaDir
#--------------------------------------------------------------------------------------------#
def set_porous_media_darcy_nonhomogeneous_parameters(iBlock,kPrim,ksiDir,etaDir):
    set_parameter_value_('darcy_aniso_kPrim_' ,iBlock,kPrim)
    set_parameter_value_('darcy_aniso_ksiDir_',iBlock,ksiDir)
    set_parameter_value_('darcy_aniso_etaDir_',iBlock,etaDir)

# =================================
# Get/Set ERGUN law options
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_ergun_option(iBlock):
    return get_parameter_value_('iPorMed_Ergun_Opt_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_porous_media_ergun_option(iBlock,option):
    set_parameter_value_('iPorMed_Ergun_Opt_',iBlock,option)

# =================================
# Get/Set ERGUN Carman-Kozeny parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_ergun_carman_kozeny_parameters(iBlock):
    porosity         = get_parameter_value_('ergun_Porosity_',iBlock)
    specificSurfArea = get_parameter_value_('ergun_specificSurfArea_',iBlock)
    constant         = get_parameter_value_('constInErgunModel_',iBlock)
    if (constant < 1.81):
        surface_type = "SMOOTH"
    else:
        surface_type = "ROUGH"
    return porosity,specificSurfArea,surface_type
#--------------------------------------------------------------------------------------------#
def set_porous_media_ergun_carman_kozeny_parameters(iBlock,porosity,specificSurfArea,surface_type):
    set_parameter_value_('ergun_Porosity_',iBlock,porosity)
    set_parameter_value_('ergun_specificSurfArea_',iBlock,specificSurfArea)
    if (surface_type == "SMOOTH"):
        set_parameter_value_('constInErgunModel_',iBlock,1.8)
    elif (surface_type == "ROUGH"):
        set_parameter_value_('constInErgunModel_',iBlock,4.0)
    else :
        raise ValueError,"Wrong value for 'surface_type' : should be 'ROUGH' or 'SMOOTH'"
    
# =================================
# Get/Set ERGUN homogeneous parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_ergun_homogeneous_parameters(iBlock):
    kPrim   = get_parameter_value_('ergun_kPrim_',iBlock)
    kSecond = get_parameter_value_('kSec_',iBlock)
    return kPrim , kSecond
#--------------------------------------------------------------------------------------------#
def set_porous_media_ergun_homogeneous_parameters(iBlock,kPrim,kSecond):
    set_parameter_value_('ergun_kPrim_',iBlock,kPrim)
    set_parameter_value_('kSec_',iBlock,kSecond)

# =================================
# Get/Set ERGUN non-homogeneous parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_ergun_nonhomogeneous_parameters(iBlock):
    kPrim   = get_parameter_value_('ergun_aniso_kPrim_' ,iBlock)
    kSecond = get_parameter_value_('ergun_aniso_kSec_'  ,iBlock)
    ksiDir  = get_parameter_value_('ergun_aniso_ksiDir_',iBlock)
    etaDir  = get_parameter_value_('ergun_aniso_etaDir_',iBlock)
    return kPrim,kSecond,ksiDir,etaDir
#--------------------------------------------------------------------------------------------#
def set_porous_media_ergun_nonhomogeneous_parameters(iBlock,kPrim,kSec,ksiDir,etaDir):
    set_parameter_value_('ergun_aniso_kPrim_' ,iBlock,kPrim)
    set_parameter_value_('ergun_aniso_kSec_'  ,iBlock,kSec)
    set_parameter_value_('ergun_aniso_ksiDir_',iBlock,ksiDir)
    set_parameter_value_('ergun_aniso_etaDir_',iBlock,etaDir)

# =================================
# Get/Set INTEGRAL law parameters
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_integral_law_parameters(iBlock):
    propor_cst = get_parameter_value_('constInIntegralLaw_',iBlock)
    thickness  = get_parameter_value_('thickPorMed_',iBlock)
    area_ratio = get_parameter_value_('areaRatio_',iBlock)
    exponent   = get_parameter_value_('exponentIntegralLaw_',iBlock)
    return propor_cst,thickness,area_ratio,exponent
#--------------------------------------------------------------------------------------------#
def set_porous_media_integral_law_parameters(iBlock,propor_cst,thickness,area_ratio,exponent):
    set_parameter_value_('constInIntegralLaw_',iBlock,propor_cst)
    set_parameter_value_('thickPorMed_',iBlock,thickness)
    set_parameter_value_('areaRatio_',iBlock,area_ratio)
    set_parameter_value_('exponentIntegralLaw_',iBlock,exponent)

# =================================
# Get/Set flow direction
# =================================
#--------------------------------------------------------------------------------------------#
def get_porous_media_flow_direction(iBlock):
    is_imposed = get_parameter_value_('iImposedFlowDirPorMed_',iBlock)
    direction  = get_parameter_value_('flowDirPorMed_vector_',iBlock)
    return is_imposed,direction
#--------------------------------------------------------------------------------------------#
def set_porous_media_flow_direction(iBlock,is_imposed,direction):
    set_parameter_value_('iImposedFlowDirPorMed_',iBlock,is_imposed)
    set_parameter_value_('flowDirPorMed_vector_',iBlock,direction)




#--------------------------------------------------------------------------------------------#
#------------------------------ Harmonic Model ----------------------------------------------#
#--------------------------------------------------------------------------------------------#

# =================================
# Get/Set maximum rank
# =================================
#--------------------------------------------------------------------------------------------#
def get_harmo_maximum_rank():
    return FHX_get_maximum_rank_()
#--------------------------------------------------------------------------------------------#
def set_harmo_maximum_rank(n):
    if (n<0 or n>2):
        raise ValueError,"Value out of bounds : " + str(n) + ". Must be 1 or 2"
    FHX_set_maximum_rank_(n)

# ===================================
# Get/Set number of harmonics of rank
# ===================================
#--------------------------------------------------------------------------------------------#
def get_harmo_number_of_rank_harmonics():
    # Identical for all ranks --> return value for 1st rank
    return FHX_get_nb_harmonics_per_rank_(0)
#--------------------------------------------------------------------------------------------#
def set_harmo_number_of_rank_harmonics(n):
    # Identical for all ranks --> set value for all ranks
    for idx in range( get_harmo_maximum_rank() ):
        FHX_set_nb_harmonics_per_rank_(n,idx)

# ==============================
# Get/Set multi-rank interaction
# ==============================
#--------------------------------------------------------------------------------------------#
def get_harmo_multi_rank_interaction():
    return FHX_get_multi_rank_interaction_()
#--------------------------------------------------------------------------------------------#
def set_harmo_multi_rank_interaction(flag):
    if (flag!=0 and flag!=1):
        raise ValueError,"Wrong value : " + str(flag) + ". Must be 0 or 1"
    FHX_set_multi_rank_interaction_(flag)

# =================================
# Get/Set maximum interaction order
# =================================
#--------------------------------------------------------------------------------------------#
def get_harmo_maximum_interaction_order():
    return FHX_get_max_order_interaction_()
#--------------------------------------------------------------------------------------------#
def set_harmo_maximum_interaction_order(n):
    FHX_set_max_order_interaction_(n)

# ========================
# Get/Set clocking effects
# ========================
TIME_AVERAGE_AND_TIME_HARMONICS = 0
TIME_AVERAGE_ONLY = 1
#--------------------------------------------------------------------------------------------#
def get_harmo_clocking_effects_choice():
    return FHX_get_multirk_partial_()
#--------------------------------------------------------------------------------------------#
def set_harmo_clocking_effects_choice(value):
    if (value!=0 and value!=1):
        raise ValueError,"Wrong value : " + str(value) + ". Must be 0 (Time average and time harmonics) or 1 (Time average only)"
    FHX_set_multirk_partial_(value)

# ================
# Get/Set clocking
# ================
#--------------------------------------------------------------------------------------------#
def get_harmo_clocking():
    # Global parameter => get value of first block.
    iBlock = 0
    return FHX_get_clocking_position_(iBlock)
#--------------------------------------------------------------------------------------------#
def set_harmo_clocking(flag):
    if (flag!=0 and flag!=1):
        raise ValueError,"Wrong value : " + str(flag) + ". Must be 0 (variable) or 1 (fixed)"
    # Global parameter => set value for all blocks
    set_parameter_value_('iNLHMerge_', get_all_domains(), flag)

# ===================================
# Get/Set number of harmonics per disturber
# ===================================
def get_harmo_number_of_disturber_per_group(grpIdx):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    nb = FHX_get_nb_disturbers_per_block_(grpIdx)

    # ---
    # if no disturber found: recompute harmonics
    # Necessary because disturber were not stored before NLH flexibility interfacing
    # ---
    if nb==0:
        rc = compute_harmo_distribution()
        if (rc==0 or rc==9):
            nb = FHX_get_nb_disturbers_per_block_(grpIdx)
            if rc==9:
                print 'Warning ! More than 40 harmonics detected for some groups.'
        else:
            raise ValueError,"Harmonics computation failed."

    return nb
#--------------------------------------------------------------------------------------------#
def get_harmo_number_of_harmonics_per_disturber(grpIdx,disturbIdx):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    if (disturbIdx<0 or disturbIdx>=get_harmo_number_of_disturber_per_group(grpIdx)):
        raise IndexError,"Disturber index out of bounds : " + str(disturbIdx)

    results=FHX_get_disturber_data_(grpIdx,disturbIdx)
    return results[1]
#--------------------------------------------------------------------------------------------#
def set_harmo_number_of_harmonics_per_disturber(grpIdx,disturbIdx,nhar):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    if (disturbIdx<0 or disturbIdx>=get_harmo_number_of_disturber_per_group(grpIdx)):
        raise IndexError,"Disturber index out of bounds : " + str(disturbIdx)

    FHX_set_nb_harmo_per_disturber_(grpIdx,disturbIdx,nhar)


# ===================================
# Select / Deselect an harmonic
# ===================================
#--------------------------------------------------------------------------------------------#
def get_harmo_selection_flag(grpIdx,harmIdx):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    if (harmIdx<0 or harmIdx>=FHX_get_nb_harmonics_per_group_(grpIdx)):
        raise IndexError,"Disturber index out of bounds : " + str(disturbIdx)

    results=FHX_get_harmonics_data_(grpIdx,harmIdx)
    return results[4]
#--------------------------------------------------------------------------------------------#
def set_harmo_selection_flag(grpIdx,harmIdx,flag):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    if (harmIdx<0 or harmIdx>=FHX_get_nb_harmonics_per_group_(grpIdx)):
        raise IndexError,"Disturber index out of bounds : " + str(disturbIdx)

    FHX_set_harmo_selection_flag_(grpIdx,harmIdx,flag)


# ==============================
# Compute harmonics distribution
# ==============================
#--------------------------------------------------------------------------------------------#
def compute_harmo_distribution():
    result = FHX_compute_harmo_distribution_()
    if type(result) is int:
        rc = result
    else:
        rc = result[0]

    if (rc!=0):
        last_log =  FHX_harmo_last_error_message_()
        print '------------------------------------'
        print 'WARNING! problem in harmonic module:'
        print last_log
        print '------------------------------------'
    return rc
#--------------------------------------------------------------------------------------------#
def get_harmo_info_nb_harmonics_per_group(grpIdx):
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    return FHX_get_nb_harmonics_per_group_(grpIdx)
#--------------------------------------------------------------------------------------------#
def get_harmo_info_harmonics_data(grpIdx,harmIdx):
    # to be implemented
    if (grpIdx<0 or grpIdx>=get_nb_domains()):
        raise IndexError,"Group index out of bounds : " + str(grpIdx)

    if (harmIdx<0 or harmIdx>=get_harmo_info_nb_harmonics_per_group(grpIdx)):
        raise IndexError,"Harmonic index out of bounds : " + str(harmIdx)

    results=FHX_get_harmonics_data_(grpIdx,harmIdx)
    # name        = results[0]
    # frequency   = results[1]
    # phase_angle = results[2]
    # nb aliases  = results[3]
    # active      = results[4]
    # base        = results[5]
    return results


#--------------------------------------------------------------------------------------------#
# private functions
#--------------------------------------------------------------------------------------------#
def get_parameter_value_(parameter_name,iblock):
    # ... Check domain index validity
    if (iblock<0 or iblock>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(iblock)

    # ... Get parameter value
    value = FHX_get_parameter_value_(parameter_name,iblock)
    if value!=None:
        if len(value)==1:
            return value[0]
        else:
            valueList = []
            for i in range( len(value) ):
                valueList.append(value[i])
            return valueList
    else:
        raise ValueError,"Could not access parameter : " + parameter_name
#--------------------------------------------------------------------------------------------#
def set_parameter_value_(parameter_name,blocks,value):
    if (type(blocks) is types.TupleType) or (type(blocks) is types.ListType):
        blockList = blocks
    else:
        blockList = [blocks]

    for index in blockList:
        if (index<0 or index>=get_nb_domains()):
            raise IndexError,"Domain index out of bounds : " + str(index)
        FHX_set_parameter_value_(parameter_name,index,value)
#--------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------#
#------------------------------ ANSYS Module ------------------------------------------------#
#--------------------------------------------------------------------------------------------#

# =================================
# Get/Set ANSYS coupling activation flag
#   ANSYS coupling flag  <==>  iAnsys_
# =================================
def get_ANSYS_coupling_flag():
    # Global parameters => get value of first block.
    iBlock = 0
    return get_parameter_value_('iAnsys_',iBlock)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_coupling_flag(flag):
    # Global parameters => set value for all blocks
    set_parameter_value_('iAnsys_',get_all_domains(),flag)

# =================================
# Get/Set ANSYS global parameters :
#   'Pressure' code
#   'Pressure' unit
#   'Temperature' code
#   'Temperature' unit
#   'Heat Transfer Coefficient' code
#   'Heat Transfer Coefficient' unit
#   'Heat Flux' code
#   'Heat Flux' unit
#   'Temperature bulk' flag
#   'Input' filename
#   'Output' filename
#   'Grid units'
#   'Scale factor'
# =================================
def get_ANSYS_pressure_code():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return P
#--------------------------------------------------------------------------------------------#
def set_ANSYS_pressure_code(pressureCode):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(pressureCode,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_pressure_unit():
    res = FHX_get_ansys_units_params_()
    unitSystem = res[0]
    factor     = res[4]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_pressure_unit(unitSystem):
    FHX_set_ansys_units_params_(0,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_temperature_code():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return T
#--------------------------------------------------------------------------------------------#
def set_ANSYS_temperature_code(temperatureCode):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,temperatureCode,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_temperature_unit():
    res = FHX_get_ansys_units_params_()
    unitSystem = res[1]
    factor     = res[5]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_temperature_unit(unitSystem):
    FHX_set_ansys_units_params_(1,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_transfer_coefficient_code():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return HTC
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_transfer_coefficient_code(htcCode):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,htcCode,HF,Tbulk,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_transfer_coefficient_unit():
    res = FHX_get_ansys_units_params_()
    unitSystem = res[3]
    factor     = res[7]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_transfer_coefficient_unit(unitSystem):
    FHX_set_ansys_units_params_(3,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_flux_code():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return HF
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_flux_code(heatfluxCode):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,HTC,heatfluxCode,Tbulk,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_flux_unit():
    res = FHX_get_ansys_units_params_()
    unitSystem = res[2]
    factor     = res[6]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_flux_unit(unitSystem):
    FHX_set_ansys_units_params_(2,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_temperature_bulk_flag():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return Tbulk
#--------------------------------------------------------------------------------------------#
def set_ANSYS_temperature_bulk_flag(TbulkFlag):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,HTC,HF,TbulkFlag,inputFile,gridUnits,scale,outputFile)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_input_filename():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return inputFile
#--------------------------------------------------------------------------------------------#
def set_ANSYS_input_filename(inputFilename):
    # Check filename existence
    if (os.path.isfile(inputFilename) == False):
        raise ValueError, "Cannot open '"+inputFilename+"' : file does not exist."

    # Set and read 'inputFilename'
    id1 = get_ANSYS_pressure_code()
    id2 = get_ANSYS_temperature_code()
    id3 = get_ANSYS_heat_transfer_coefficient_code()
    id4 = get_ANSYS_heat_flux_code()
    for compIdxStr in FHX_get_active_computations_():
        compIdx = int(string.split(compIdxStr,'.')[0])
        FHX_read_ansys_input_file_(inputFilename,compIdx,id1,id2,id3,id4)
    
#--------------------------------------------------------------------------------------------#
def get_ANSYS_output_filename():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return outputFile
#--------------------------------------------------------------------------------------------#
def set_ANSYS_output_filename(outputFilename):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFilename)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_grid_units():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return gridUnits
#--------------------------------------------------------------------------------------------#
def set_ANSYS_grid_units(gridunit):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,HTC,HF,Tbulk,inputFile,gridunit,scale,outputFile)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_scale_factor():
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    return scale
#--------------------------------------------------------------------------------------------#
def set_ANSYS_scale_factor(scaleFactor):
    P,T,HTC,HF,Tbulk,inputFile,gridUnits,scale,outputFile = FHX_get_ansys_params_()
    FHX_set_ansys_params_(P,T,HTC,HF,Tbulk,inputFile,gridUnits,scaleFactor,outputFile)

# =============================
# Get/Set reference systems :
#   Origin, point1, point2, point3 for FLUID mesh
#   Origin, point1, point2, point3 for ANSYS mesh
# =============================
def get_ANSYS_solid_mesh_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    return Point(F_ORIx, F_ORIy, F_ORIz), Point(F_PT1x, F_PT1y, F_PT1z), Point(F_PT2x, F_PT2y, F_PT2z), Point(F_PT3x, F_PT3y, F_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_mesh_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    FHX_set_ansys_reference_systems_(S_ORIx, S_ORIy, S_ORIz,
                                     orig.x, orig.y, orig.z,
                                     S_PT1x, S_PT1y, S_PT1z,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     S_PT2x, S_PT2y, S_PT2z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     S_PT3x, S_PT3y, S_PT3z,
                                     pnt3.x, pnt3.y, pnt3.z)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_fluid_mesh_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z = FHX_get_ansys_reference_systems_()
    return Point(S_ORIx, S_ORIy, S_ORIz), Point(S_PT1x, S_PT1y, S_PT1z), Point(S_PT2x, S_PT2y, S_PT2z), Point(S_PT3x, S_PT3y, S_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_fluid_mesh_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    FHX_set_ansys_reference_systems_(orig.x, orig.y, orig.z,
                                     F_ORIx, F_ORIy, F_ORIz,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     F_PT1x, F_PT1y, F_PT1z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     F_PT2x, F_PT2y, F_PT2z,
                                     pnt3.x, pnt3.y, pnt3.z,
                                     F_PT3x, F_PT3y, F_PT3z)

# =============================
# Get/Set reference systems :
#   Origin, point1, point2, point3 for FLUID mesh
#   Origin, point1, point2, point3 for ANSYS mesh
# NOTE: following commands are obsolete, kept for backward compatibility (see defect #24475)
# =============================
def get_ANSYS_fluid_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    return Point(F_ORIx, F_ORIy, F_ORIz), Point(F_PT1x, F_PT1y, F_PT1z), Point(F_PT2x, F_PT2y, F_PT2z), Point(F_PT3x, F_PT3y, F_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_fluid_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    FHX_set_ansys_reference_systems_(S_ORIx, S_ORIy, S_ORIz,
                                     orig.x, orig.y, orig.z,
                                     S_PT1x, S_PT1y, S_PT1z,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     S_PT2x, S_PT2y, S_PT2z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     S_PT3x, S_PT3y, S_PT3z,
                                     pnt3.x, pnt3.y, pnt3.z)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_solid_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z = FHX_get_ansys_reference_systems_()
    return Point(S_ORIx, S_ORIy, S_ORIz), Point(S_PT1x, S_PT1y, S_PT1z), Point(S_PT2x, S_PT2y, S_PT2z), Point(S_PT3x, S_PT3y, S_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FHX_get_ansys_reference_systems_()
    FHX_set_ansys_reference_systems_(orig.x, orig.y, orig.z,
                                     F_ORIx, F_ORIy, F_ORIz,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     F_PT1x, F_PT1y, F_PT1z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     F_PT2x, F_PT2y, F_PT2z,
                                     pnt3.x, pnt3.y, pnt3.z,
                                     F_PT3x, F_PT3y, F_PT3z)


# =============================
# Initialize ANSYS datastructure
# with default values
# =============================
def initialize_ansys_surfaces():
    # Obsolete
    #FHX_initialize_ansys_surfaces_()
    pass

    
# =============================
# Remove all connected patches
# to ANSYS face
# =============================
def clear_ansys_surfaces( sID ):
    FHX_clear_ansys_surfaces_( sID )

# =============================
# Connect patch(es) to a ANSYS face
# =============================
def connect_ansys_solid_face_to_patch( *args ):
    if len(args)==4:
        # ----
        # Old implementation:
        #   Patch (b,f,p) is connected to specified ANSYS surface (idx)
        #    /!\ This patch is added to previous connected patches
        # ----
        idx = args[0]
        b   = args[1]
        f   = args[2]
        p   = args[3]
        FHX_add_patch_to_code_ansys_( idx, b, f , p )

    else:
        # ----
        # New implementation:
        #   Patches list [[b1,p1], [b2,p2], ...] are connected to specified ANSYS surface (idx)
        #   /!\ This list replaces previous connected patches
        # ----
        idx = args[0]
        patchList = args[1]
        FHX_set_ansys_patches_( idx, len(patchList), patchList )
    
# =============================
# Get/Set connected fluid patch parameters :
#   Periodic flag
#   Rotation angle (around Z)
#   Translation vector ????
#   Number of repetitions
#   Partial flag
# =============================
def get_ANSYS_connected_fluid_patch_periodic_flag(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    return periodic_flag
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_periodic_flag(surfID, patchID, flag):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    FHX_set_ansys_fluid_patch_parameters_(surfID, patchID, partial_flag, flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_rotation_angle(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    return rot_angle
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_rotation_angle(surfID, patchID, angle):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    FHX_set_ansys_fluid_patch_parameters_(surfID, patchID, partial_flag, periodic_flag, angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_translation_vector(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    return Vector(trans_x, trans_y, trans_z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_translation_vector(surfID, patchID, translation):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    FHX_set_ansys_fluid_patch_parameters_(surfID, patchID, partial_flag, periodic_flag, rot_angle, trans_flag, translation.x, translation.y, translation.z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_nb_repetitions(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    return nb_repet
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_nb_repetitions(surfID, patchID, nbRepet):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    FHX_set_ansys_fluid_patch_parameters_(surfID, patchID, partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nbRepet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_partial_flag(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    return partial_flag
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_partial_flag(surfID, patchID, flag):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FHX_get_ansys_fluid_patch_parameters_(surfID, patchID)
    FHX_set_ansys_fluid_patch_parameters_(surfID, patchID, flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)



# =============================
# Get/Set surface parameters :
#   Interpolation type (0: non-conservative  /  1: conservative)
#   Maxi distance
# =============================
def get_ANSYS_solid_surface_list():
    surfaces = []
    surfacestmp = FHX_get_ansys_solid_surfaces_()
    for surf in surfacestmp:
        sid = int(surf[0])
        surfaces.append(sid)
    return surfaces

#--------------------------------------------------------------------------------------------#
def get_ANSYS_solid_surface_interpolation_type( sID ):
    interp,max_dist = FHX_get_ansys_solid_surface_params_(sID)
    return interp
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_surface_interpolation_type( sID, interp_type ):
    interp,max_dist = FHX_get_ansys_solid_surface_params_(sID)
    FHX_set_ansys_solid_surface_params_(sID, interp_type, max_dist)
    
#--------------------------------------------------------------------------------------------#
def get_ANSYS_solid_surface_maximum_distance( sID ):
    interp,max_dist = FHX_get_ansys_solid_surface_params_(sID)
    return max_dist
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_surface_maximum_distance( sID, max_distance):
    interp,max_dist = FHX_get_ansys_solid_surface_params_(sID)
    FHX_set_ansys_solid_surface_params_(sID, interp, max_distance)


#--------------------------------------------------------------------------------------------#
#------------------------------ Boundary Conditions -----------------------------------------#
#--------------------------------------------------------------------------------------------#

class BCPatch:
    def __init__(self,blockID,patchID):
        self._blockID    = blockID
        self._patchID    = patchID

    def get_name(self):
        return FHX_get_patch_name_(self._blockID,1,self._patchID)

    def get_group_name(self):
        return FHX_get_group_name_(self._blockID,1,self._patchID)

    def get_block_patch(self):
        return self._blockID,self._patchID

    def get_bc_name(self):
        return FHX_get_bc_name_(self._blockID,1,self._patchID)

    def get_bc_type(self):
        bc_id,bc_opsel = FHX_get_bc_values_(self._blockID,1,self._patchID)
        return [bc_id,bc_opsel]
    
    def set_bc_type(self,value):
        bc_id    = value[0]
        bc_opsel = value[1]
        FHX_set_bc_values_(self._blockID,1,self._patchID,bc_id,bc_opsel)

    def get_parameter_value(self,name):
        value = FHX_get_bc_parameter_value_(self._blockID,1,self._patchID,name)
        if value!=None:
            return value
        else:
            raise ValueError, "Could not find parameter : " + name + " for patch " + str(get_name())

    def set_parameter_value(self,name,value):
        # ...
        # Set value according to its type.
        # Following formats are supported for value:
        #  -> INTEGER
        #  -> REAL
        #  -> PROFILE: [interpolationType, [x1,y1,z1] , [x2,y2,z2] , ... , [xn,yn,zn]]
        #  -> LIST: [v1,v2,v3]
        #  -> Vector type
        #  -> Point type
        
        value_type=""
        if (type(value) is types.IntType):
            FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"INTEGER",value)
        elif (type(value) is types.FloatType):
            FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"REAL",value)
        elif (type(value) is types.TupleType) or (type(value) is types.ListType):
            if (type(value[0]) is types.TupleType) or (type(value[0]) is types.ListType):
                # Backward : set dummy interpolation type that will be ignored
                FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"PROFILE",-1,len(value),value)
            else:
                if (len(value)==2 and (type(value[1]) is types.TupleType or type(value[1]) is types.ListType)):
                    FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"PROFILE",value[0],len(value[1]),value[1])
                else:   
                    FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"VECTOR",value)
        elif (type(value) is types.InstanceType) and isinstance(value,Vector):
                FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"VECTOR",[value.x,value.y,value.z])
        elif (type(value) is types.InstanceType) and isinstance(value,Point):
                FHX_set_bc_parameter_value_(self._blockID,1,self._patchID,name,"VECTOR",[value.x,value.y,value.z])
        else:
            # WRONG TYPE FOR 'value'
            raise ValueError, "Wrong type : " + str(type(value)) + " for parameter name " + name

    def get_nb_integer_entries(self):
        return FHX_get_nb_integer_entries_(self._blockID,1,self._patchID)
    def get_integer_parameter_index(self,name):
        return FHX_get_integer_parameter_index_(self._blockID,1,self._patchID,name)
    def get_integer_parameter_name(self,idx):
        return FHX_get_integer_parameter_name_(self._blockID,1,self._patchID,idx)
    def get_integer_parameter_value(self,idx):
        return FHX_get_integer_parameter_value_(self._blockID,1,self._patchID,idx)
    def set_integer_parameter_value(self,idx,val):
        FHX_set_integer_parameter_value_(self._blockID,1,self._patchID,idx,val)
    def set_integer_parameter_value(self,name,val):
        idx=self.get_integer_parameter_index(name)
        FHX_set_integer_parameter_value_(self._blockID,1,self._patchID,idx,val)

    def get_nb_real_entries(self):
        return FHX_get_nb_real_entries_(self._blockID,1,self._patchID)
    def get_real_parameter_index(self,name):
        return FHX_get_real_parameter_index_(self._blockID,1,self._patchID,name)
    def get_real_parameter_name(self,idx):
        return FHX_get_real_parameter_name_(self._blockID,1,self._patchID,idx)
    def get_real_parameter_value(self,idx):
        return FHX_get_real_parameter_value_(self._blockID,1,self._patchID,idx)
    def set_real_parameter_value(self,idx,val):
        FHX_set_real_parameter_value_(self._blockID,1,self._patchID,idx,val)
    def set_real_parameter_value(self,name,val):
        idx=self.get_real_parameter_index(name)
        FHX_set_real_parameter_value_(self._blockID,1,self._patchID,idx,val)

    def get_nb_choice_entries(self):
        return FHX_get_nb_choice_entries_(self._blockID,1,self._patchID)
    def get_choice_parameter_index(self,name):
        return FHX_get_choice_parameter_index_(self._blockID,1,self._patchID,name)
    def get_choice_parameter_name(self,idx):
        return FHX_get_choice_parameter_name_(self._blockID,1,self._patchID,idx)
    def get_choice_parameter_value(self,idx):
        return FHX_get_choice_parameter_value_(self._blockID,1,self._patchID,idx)
    def set_choice_parameter_value(self,idx,val):
        FHX_set_choice_parameter_value_(self._blockID,1,self._patchID,idx,val)
    def set_choice_parameter_value(self,name,val):
        idx=self.get_choice_parameter_index(name)
        FHX_set_choice_parameter_value_(self._blockID,1,self._patchID,idx,val)

    def get_nb_vector_entries(self):
        return FHX_get_nb_vector_entries_(self._blockID,1,self._patchID)
    def get_vector_parameter_index(self,name):
        return FHX_get_vector_parameter_index_(self._blockID,1,self._patchID,name)
    def get_vector_parameter_name(self,idx):
        return FHX_get_vector_parameter_name_(self._blockID,1,self._patchID,idx)
    def get_vector_parameter_value(self,idx):
        return FHX_get_vector_parameter_value_(self._blockID,1,self._patchID,idx)
    def set_vector_parameter_value(self,name,vect):
        idx=self.get_vector_parameter_index(name)
        FHX_set_vector_parameter_value_(self._blockID,1,self._patchID,idx,vect)

    def get_nb_physical_entries(self):
        return FHX_get_nb_physical_entries_(self._blockID,1,self._patchID)
    def get_physical_parameter_index(self,name):
        return FHX_get_physical_parameter_index_(self._blockID,1,self._patchID,name)
    def get_physical_parameter_name(self,idx):
        return FHX_get_physical_parameter_name_(self._blockID,1,self._patchID,idx)
    def get_physical_parameter_value(self,idx):
        return FHX_get_physical_parameter_value_(self._blockID,1,self._patchID,idx)
    def set_physical_parameter_value(self,idx,val):
        FHX_set_physical_parameter_value_(self._blockID,1,self._patchID,idx,val)
    def set_physical_parameter_value(self,name,val):
        idx=self.get_physical_parameter_index(name)
        FHX_set_physical_parameter_value_(self._blockID,1,self._patchID,idx,val)
    def get_physical_parameter_type(self,idx):
        return FHX_get_physical_parameter_type_(self._blockID,1,self._patchID,idx)
    def set_physical_parameter_type(self,idx,type):
        FHX_set_physical_parameter_type_(self._blockID,1,self._patchID,idx,type)
    def get_physical_parameter_profile(self,idx):
        return FHX_get_physical_parameter_profile_(self._blockID,1,self._patchID,idx)
    def set_physical_parameter_profile(self,idx,nbpts,profile):
        FHX_set_physical_parameter_profile_(self._blockID,1,self._patchID,idx,nbpts,profile)

    def get_compute_force_and_torque_flag(self):
        if (self.get_bc_name() != 'SOL'):
            raise ValueError,"Not applicable for boundary condition : " + self.get_bc_name()
        res = FHX_get_force_and_torque_(self._blockID,1,self._patchID)
        if res[0]=='No_Force_and_Torque':
            return 0
        else:
            return 1        
    def set_compute_force_and_torque_flag(self,flag):
        if (self.get_bc_name() != 'SOL'):
            raise ValueError,"Not applicable for boundary condition : " + self.get_bc_name()
        res = FHX_get_force_and_torque_(self._blockID,1,self._patchID)
        FHX_set_force_and_torque_(self._blockID,1,self._patchID,flag,res[1],res[2],res[3],res[4],res[5])

## ........................................................................................
##                                          B.C Types
## ........................................................................................
## BC_NAME                                                                         [id,opsel]
## ........................................................................................

## ... INLETs
SUPERSONIC_CARTESIAN_VELOCITY_COMPONENTS_IMPOSED                                  = [ 23,0]
SUPERSONIC_CYLINDRICAL_VELOCITY_COMPONENTS_IMPOSED                                = [ 23,1]
SUBSONIC_CYLINDRICAL_VELOCITY_COMPONENTS_IMPOSED                                  = [ 23,2]
SUPERSONIC_CARTESIAN_MACH_NUMBER_AND_VELOCITY_ANGLE_IMPOSED                       = [ 23,3]
SUBSONIC_CARTESIAN_STATIC_PRESSURE_EXTRAPOLATED                                   = [ 24,1]
SUBSONIC_CARTESIAN_MACH_NUMBER_EXTRAPOLATED                                       = [ 24,2]
SUBSONIC_CARTESIAN_MAGNITUDE_OF_ABSOLUTE_VELOCITY_EXTRAPOLATED                    = [ 24,3]
SUBSONIC_CARTESIAN_MACH_NUMBER_AND_VELOCITY_ANGLE_IMPOSED                         = [ 24,4]
SUBSONIC_CARTESIAN_VELOCITY_NORMAL_TO_INLET                                       = [ 24,5]
SUBSONIC_CARTESIAN_VELOCITY_DIRECTION                                             = [ 28,3]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION                                   = [124,1]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION_V_EXTRAPOLATED                    = [124,2]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION_VZ_EXTRAPOLATED                   = [124,3]
SUBSONIC_CYLINDRICAL_VELOCITY_DIRECTION_V_EXTRAPOLATED                            = [124,4]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_MERIDIONAL_DIRECTION_STATIC_PRESSURE_EXTRAPOLATED = [124,5]
SUBSONIC_CYLINDRICAL_TANGENTIAL_VELOCITY_AND_MERIDIONAL_ANGLE_VM_EXTRAPOLATED     = [124,6]
SUBSONIC_CYLINDRICAL_VELOCITY_COMPONENTS_STATIC_PRESSURE_EXTRAPOLATED             = [124,7]
SUBSONIC_CYLINDRICAL_RELATIVE_ANGLE_FROM_AXIAL_DIRECTION_VZ_EXTRAPOLATED          = [124,8]
SUBSONIC_CYLINDRICAL_RELATIVE_VELOCITY_DIRECTION_W_EXTRAPOLATED                   = [124,9]
SUBSONIC_CYLINDRICAL_MERIDIONAL_FLOW_ANGLE_AND_TANGENTIAL_VELOCITY                = [ 28,1]
SUBSONIC_CYLINDRICAL_VELOCITY_DIRECTION                                           = [ 28,2]

## ... OUTLETs
SUBSONIC_CARTESIAN_STATIC_PRESSURE_IMPOSED                                        = [ 25, 10]
SUBSONIC_CARTESIAN_RADIAL_EQUILIBRIUM                                             = [125, 10]
SUPERSONIC_EXTRAPOLATION                                                          = [ 22,  0]
SUBSONIC_CARTESIAN_VELOCITY_SCALING                                               = [ 27, 21]
SUBSONIC_CARTESIAN_PRESSURE_ADAPTATION                                            = [ 27, 30]
SUBSONIC_CYLINDRICAL_STATIC_PRESSURE_IMPOSED                                      = [ 25,110]
SUBSONIC_CYLINDRICAL_RADIAL_EQUILIBRIUM                                           = [125,110]
SUBSONIC_CYLINDRICAL_VELOCITY_SCALING                                             = [ 27,121]
SUBSONIC_CYLINDRICAL_PRESSURE_ADAPTATION                                          = [ 27,130]

## ... SOLIDs
NS_CARTESIAN_ADIABATIC                                                            = [ 13,0]
NS_CARTESIAN_HEAT_FLUX_IMPOSED                                                    = [ 10,0]
NS_CARTESIAN_HEAT_TRANSFER_COEFFICIENT_IMPOSED                                    = [ 11,0]
NS_CARTESIAN_TEMPERATURE_IMPOSED                                                  = [ 14,0]
EULER_EULER_SOLID_WALL                                                            = [ 16,0]
NS_CYLINDRICAL_ADIABATIC_CONSTANT_ROTATION_SPEED                                  = [113,0]
NS_CYLINDRICAL_ADIABATIC_AREA_DEFINED_ROTATION_SPEED                              = [113,1]
NS_CYLINDRICAL_HEAT_FLUX_IMPOSED_CONSTANT_ROTATION_SPEED                          = [110,0]
NS_CYLINDRICAL_HEAT_FLUX_IMPOSED_AREA_DEFINED_ROTATION_SPEED                      = [110,1]
NS_CYLINDRICAL_TEMPERATURE_IMPOSED_CONSTANT_ROTATION_SPEED                        = [114,0]
NS_CYLINDRICAL_TEMPERATURE_IMPOSED_AREA_DEFINED_ROTATION_SPEED                    = [114,1]

## ... EXTERNALs
STATIC_QUANTITIES                                                                 = [21,1]
MACH_NUMBER_AND_VELOCITY_ANGLE                                                    = [21,2]

#--------------------------------------------------------------------------------------------#
# WALL TYPES
#--------------------------------------------------------------------------------------------#
SMOOTH = 1
ROUGH  = 2

#--------------------------------------------------------------------------------------------#
# PROFILE: INTERPOLATION TYPES
#--------------------------------------------------------------------------------------------#
## ... 1D
INTERPOLATION_1D_ALONG_X             =  1
INTERPOLATION_1D_ALONG_Y             =  2
INTERPOLATION_1D_ALONG_Z             =  3
INTERPOLATION_1D_ALONG_R             =  4
INTERPOLATION_1D_ALONG_THETA         =  5
INTERPOLATION_1D_ALONG_ROTATION_AXIS =  6
## ... 2D
INTERPOLATION_2D_ALONG_X_Y           = 51
INTERPOLATION_2D_ALONG_X_Z           = 52
INTERPOLATION_2D_ALONG_Y_Z           = 53
INTERPOLATION_2D_ALONG_R_THETA       = 54
INTERPOLATION_2D_ALONG_R_Z           = 55
INTERPOLATION_2D_ALONG_THETA_Z       = 56

#--------------------------------------------------------------------------------------------#
def get_bc_patch(blockID,patchID):
    return BCPatch(blockID+1,patchID+1)

#--------------------------------------------------------------------------------------------#
def get_bc_patch_by_name(name):
    for b in range( get_nb_domains() ):
        for p in range( get_nb_domain_patches(b) ):
            patch = get_bc_patch(b,p)
            if (patch.get_name() == name):
                return patch
    raise ValueError,"Wrong patch name : " + name
    return None

#--------------------------------------------------------------------------------------------#
def get_bc_patch_list(pattern):
    patch_list = []
    regexp = fnmatch.translate(pattern) ; # convert pattern to regular expression
    reobj = re.compile(regexp)
    for b in range( get_nb_domains() ):
        for p in range( get_nb_domain_patches(b) ):
            patch = get_bc_patch(b,p)
            if (reobj.match(patch.get_name())):
                patch_list.append(patch)
    return patch_list

#--------------------------------------------------------------------------------------------#
#--- BC patch grouping
#--------------------------------------------------------------------------------------------#
def create_group(name,value):

    if ( type(value) is types.ListType ):
        # Exhaustive list of patches to group
        bc_patch_list = value
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        bc_patch_list = get_bc_patch_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    patchList=[]
    for bc_patch in bc_patch_list:
        b,p = bc_patch.get_block_patch()
        patchList.append([b,1,p])
    FHX_group_patches_(name,len(patchList),patchList)
#--------------------------------------------------------------------------------------------#
def ungroup(name):
    FHX_ungroup_patches_(name)
#--------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------#
#------------------------------ Initial solution --------------------------------------------#
#--------------------------------------------------------------------------------------------#
CONSTANT_VALUES            = 'const'
FROM_FILE                  = 'file'
CARTESIAN_COORDS           = 'abs'
CYLINDRICAL_COORDS         = 'rel'
ABSOLUTE_VELOCITY          = 'abs'
RELATIVE_VELOCITY          = 'rel'
RESET_CONVERGENCE_HISTORY  = 1
IMPORT_CONVERGENCE_HISTORY = 2
CONSTANT_PRESSURE          = 0
RADIAL_EQUILIBRIUM         = 1
class InitialSolution:
    def __init__(self,blockID):
        self._blockID = blockID
        
    def get_mode(self):
        return FHX_get_initial_solution_mode_(self._blockID)
    def set_mode(self,mode):
        FHX_set_initial_solution_mode_(self._blockID,mode)

    def get_coord_system(self):
        return FHX_get_initial_coord_system_(self._blockID)
    def set_coord_system(self,cs):
        FHX_set_initial_coord_system_(self._blockID,cs)

    def get_pressure(self):
        return FHX_get_initial_pressure_(self._blockID)
    def set_pressure(self,P):
        FHX_set_initial_pressure_(self._blockID,P)

    def get_temperature(self):
        return FHX_get_initial_temperature_(self._blockID)
    def set_temperature(self,T):
        FHX_set_initial_temperature_(self._blockID,T)

    def get_velocity_type(self):
        return FHX_get_initial_velocity_type_(self._blockID)
    def set_velocity_type(self,velType):
        FHX_set_initial_velocity_type_(self._blockID,velType)

    def get_velocity(self):
        v = FHX_get_initial_velocity_(self._blockID)
        return Vector(v[0],v[1],v[2])
    def set_velocity(self,vel):
        FHX_set_initial_velocity_(self._blockID,[vel.x,vel.y,vel.z])

    def get_turbulent_viscosity(self):
        return FHX_get_initial_turb_visc_(self._blockID)
    def set_turbulent_viscosity(self,turb_visc):
        FHX_set_initial_turb_visc_(self._blockID,turb_visc)

    def get_k_epsilon(self):
        return FHX_get_initial_k_epsilon_(self._blockID)
    def set_k_epsilon(self,k,epsilon):
        FHX_set_initial_k_epsilon_(self._blockID,k,epsilon)

    def get_restart_filename(self):
        return FHX_get_initial_filename_(self._blockID)
    def set_restart_filename(self,filename):
        FHX_set_initial_filename_(self._blockID,filename)

    def get_restart_mode(self):
        return FHX_get_initial_restart_mode_(self._blockID)
    def set_restart_mode(self,mode):
        FHX_set_initial_restart_mode_(self._blockID,mode)

    def get_grid_to_grid_solution_transfer_flag(self):
        return FHX_get_initial_grid_to_grid_flag_(self._blockID)
    def set_grid_to_grid_solution_transfer_flag(self,mode):
        FHX_set_initial_grid_to_grid_flag_(self._blockID,mode)

#--------------------------------------------------------------------------------------------#
# In case of Initial Solution "turbo" mode
#--------------------------------------------------------------------------------------------#
# Channel selected patches
#--------------------------------------------------------------------------------------------#
    # ---
    # Get/Set main entrance patch
    # ---
    def get_turbo_entrance_patch(self):
        result = FHX_get_channel_selected_patches_(self._blockID)
        lstIdx = result[0][0]
        grpIdx = result[0][1]
        if (lstIdx==-1 and grpIdx==-1):
            print 'get_turbo_entrance_patch() : no main entrance patch found.'
            return None
        else:
            b,f,p  = FHX_get_bfp_idx_(lstIdx,grpIdx)
            if (b!=-1 and f!=-1 and p!=-1):
                return get_bc_patch(b,p)

        return None

    def set_turbo_entrance_patch(self,bcpatch):
        # Convert bfp -> list+group idx
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        # Set new entrance patch
        result =  FHX_get_channel_selected_patches_(self._blockID)
        patches = []
        patches.append([lstIdx,grpIdx])
        patches.append([ result[1][0] , result[1][1] ])
        patches.append([ result[2][0] , result[2][1] ])
        FHX_set_channel_selected_patches_(self._blockID, patches)


    # ---
    # Get/Set main exit patch
    # ---
    def get_turbo_exit_patch(self):
        result = FHX_get_channel_selected_patches_(self._blockID)
        lstIdx = result[1][0]
        grpIdx = result[1][1]
        if (lstIdx==-1 and grpIdx==-1):
            print 'get_turbo_exit_patch() : no main exit patch found.'
            return None
        else:
            b,f,p  = FHX_get_bfp_idx_(lstIdx,grpIdx)
            if (b!=-1 and f!=-1 and p!=-1):
                return get_bc_patch(b,p)

        return None

    def set_turbo_exit_patch(self,bcpatch):
        # Convert bfp -> list+group idx
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        # Set new exit patch
        result =  FHX_get_channel_selected_patches_(self._blockID)
        patches = []
        patches.append([ result[0][0] , result[0][1] ])
        patches.append([lstIdx,grpIdx])
        patches.append([ result[2][0] , result[2][1] ])
        FHX_set_channel_selected_patches_(self._blockID, patches)


    # ---
    # Get/Set exit up patch
    # ---
    def get_turbo_exitup_patch(self):
        result = FHX_get_channel_selected_patches_(self._blockID)
        lstIdx = result[2][0]
        grpIdx = result[2][1]
        if (lstIdx==-1 and grpIdx==-1):
            print 'get_turbo_exitup_patch() : no exit up patch found.'
            return None
        else:
            b,f,p  = FHX_get_bfp_idx_(lstIdx,grpIdx)
            if (b!=-1 and f!=-1 and p!=-1):
                return get_bc_patch(b,p)

        return None
        
    def set_turbo_exitup_patch(self,bcpatch):
        # Convert bfp -> list+group idx
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        # Set new exit patch
        result =  FHX_get_channel_selected_patches_(self._blockID)
        patches = []
        patches.append([ result[0][0] , result[0][1] ])
        patches.append([ result[1][0] , result[1][1] ])
        patches.append([lstIdx,grpIdx])
        FHX_set_channel_selected_patches_(self._blockID, patches)

#--------------------------------------------------------------------------------------------#
# Pressure type (CONSTANT=0 / RADIALEQUILIBRIUM=1)
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_pressure_type(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[0]
    def set_turbo_patch_pressure_type(self,bcpatch,pressureType):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,pressureType,result[1],result[2],result[3],result[4],result[5],result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Pressure value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_pressure(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[1]
    def set_turbo_patch_pressure(self,bcpatch,pressure):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],pressure,result[2],result[3],result[4],result[5],result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Radius (for radial equilibrium)
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_radius(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[2]
    def set_turbo_patch_radius(self,bcpatch,radius):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],radius,result[3],result[4],result[5],result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Temperature value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_temperature(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[3]
    def set_turbo_patch_temperature(self,bcpatch,temperature):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],result[2],temperature,result[4],result[5],result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Velocity type
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_velocity_type(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[4]
    def set_turbo_patch_velocity_type(self,bcpatch,velocityType):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],result[2],result[3],velocityType,result[5],result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Vr value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vr(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[5]
    def set_turbo_patch_vr(self,bcpatch,vr):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],result[2],result[3],result[4],vr,result[6],result[7])
#--------------------------------------------------------------------------------------------#
# Vt value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vt(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[6]
    def set_turbo_patch_vt(self,bcpatch,vt):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],result[2],result[3],result[4],result[5],vt,result[7])
#--------------------------------------------------------------------------------------------#
# Vz value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vz(self,bcpatch):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        return result[7]
    def set_turbo_patch_vz(self,bcpatch,vz):
        b,p = bcpatch.get_block_patch()
        lstIdx,grpIdx = FHX_get_list_and_group_idx_(b-1, 0, p-1)
        result = FHX_get_turbo_patch_params_(lstIdx,grpIdx)
        FHX_set_turbo_patch_params_(lstIdx,grpIdx,result[0],result[1],result[2],result[3],result[4],result[5],result[6],vz)

#--------------------------------------------------------------------------------------------#
# TURBOMACHINERY initial solution: get channel information
#--------------------------------------------------------------------------------------------#
def get_turbo_channel_nb_entrance_patches():
    result = FHX_get_channel_entrance_patches_()
    return len(result)
def get_turbo_channel_nb_internal_patches():
    result = FHX_get_channel_internal_patches_()
    return len(result)
def get_turbo_channel_nb_exit_patches():
    result = FHX_get_channel_exit_patches_()
    return len(result)
def get_turbo_channel_nb_exit_up_patches():
    result = FHX_get_channel_exit_up_patches_()
    return len(result)

def get_turbo_channel_entrance_patches():
    result = FHX_get_channel_entrance_patches_()
    bc_patch_list = []
    for i in range(len(result)):
        lstIdx = result[i][2]
        grpIdx = result[i][3]
        b,f,p = FHX_get_bfp_idx_(lstIdx,grpIdx)
        bc_patch_list.append(get_bc_patch(b,p))
    return bc_patch_list

def get_turbo_channel_internal_patches():
    result = FHX_get_channel_internal_patches_()
    bc_patch_list = []
    for i in range(len(result)):
        lstIdx = result[i][2]
        grpIdx = result[i][3]
        b,f,p = FHX_get_bfp_idx_(lstIdx,grpIdx)
        bc_patch_list.append(get_bc_patch(b,p))
    return bc_patch_list

def get_turbo_channel_exit_patches():
    result = FHX_get_channel_exit_patches_()
    bc_patch_list = []
    for i in range(len(result)):
        lstIdx = result[i][2]
        grpIdx = result[i][3]
        b,f,p = FHX_get_bfp_idx_(lstIdx,grpIdx)
        bc_patch_list.append(get_bc_patch(b,p))
    return bc_patch_list

def get_turbo_channel_exit_up_patches():
    result = FHX_get_channel_exit_up_patches_()
    bc_patch_list = []
    for i in range(len(result)):
        lstIdx = result[i][2]
        grpIdx = result[i][3]
        b,f,p = FHX_get_bfp_idx_(lstIdx,grpIdx)
        bc_patch_list.append(get_bc_patch(b,p))
    return bc_patch_list

#--------------------------------------------------------------------------------------------#
# Initial Solution blocks grouping/ungrouping
#--------------------------------------------------------------------------------------------#
def create_initial_solution_block_group(name,value):
    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to group
        blocks_list = []
        for block in value:
            if ( type(block) is types.IntType ) :
                idx  = block
                blocks_list.append(idx)
            elif ( type(block) is types.StringType ):
                name = block
                idx  = FHX_get_domain_index_(name)
                blocks_list.append(idx)
        
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        blocks_list = get_domains_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    FHX_group_initial_solution_blocks_(name,len(blocks_list),blocks_list)
    FHX_update_initial_solution_blocks_groups_()

def initial_solution_ungroup_block(value):
    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to ungroup
        blocks_list = []
        for block in value:
            if ( type(block) is types.IntType ) :
                idx  = block
                name = get_domain_name(idx)
                FHX_group_initial_solution_blocks_(name,1,[idx])
            elif ( type(block) is types.StringType ):
                name = block
                idx  = FHX_get_domain_index_(name)
                FHX_group_initial_solution_blocks_(name,1,[idx])

    elif ( type(value) is types.StringType ):
        # Get list of blocks from pattern
        pattern = value
        blocks_list = get_domains_list(pattern)
        for idx in blocks_list:
            name = get_domain_name(idx)
            FHX_group_initial_solution_blocks_(name,1,[idx])

    elif ( type(value) is types.IntType ):
        # Single block index specified
        name = get_domain_name(value)
        FHX_group_initial_solution_blocks_(name,1,[value])

    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    # Update grouping
    FHX_update_initial_solution_blocks_groups_()

#--------------------------------------------------------------------------------------------#
def get_initial_solution(blockID):
    return InitialSolution(blockID)
#--------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------#
#------------------------------ Coupling Module ---------------------------------------------#
#--------------------------------------------------------------------------------------------#
NO_COUPLING             = 0
MODAL_APPROACH_COUPLING = 1
MPCCI_COUPLING          = 2
OOFELIE_COUPLING        = 3
RIGID_MOTION            = 4
# =================================
# Get/Set coupling activation mode
# (global parameter)
# =================================
def get_coupling_mode():
    # Global parameters => get value of first block.
    iBlock = 0
    result = FHX_get_coupling_global_params_(iBlock)
    iMpCCi         = result[0]
    iModalApproach = result[1]
    iOofelie       = result[2]
    pRef           = result[3]
    FS_pRef        = result[4]
    iRigidMotion   = result[5]
    
    if   (iModalApproach == 1): return MODAL_APPROACH_COUPLING
    elif (iMpCCi         == 1): return MPCCI_COUPLING
    elif (iOofelie       == 1): return OOFELIE_COUPLING
    elif (iRigidMotion   == 1): return RIGID_MOTION
    else:                       return NO_COUPLING
    
#--------------------------------------------------------------------------------------------#
def set_coupling_mode(mode):
    # Global parameters => get value of first block.
    iBlock = 0
    result = FHX_get_coupling_global_params_(iBlock)
    iMpCCi         = result[0]
    iModalApproach = result[1]
    iOofelie       = result[2]
    pRef           = result[3]
    FS_pRef        = result[4]
    iRigidMotion   = result[5]
    
    iMpCCi         = 0
    iOofelie       = 0
    iModalApproach = 0
    iRigidMotion   = 0
    if   (mode==MODAL_APPROACH_COUPLING): iModalApproach = 1
    elif (mode==MPCCI_COUPLING         ): iMpCCi = 1
    elif (mode==OOFELIE_COUPLING       ): iOofelie = 1
    elif (mode==RIGID_MOTION           ): iRigidMotion = 1

    # Global parameters => set value for all blocks
    for iBlock in get_all_domains():
        FHX_set_coupling_global_params_(iBlock,iMpCCi,iModalApproach,iOofelie,
                                        pRef,FS_pRef,iRigidMotion)

# =================================
# Get/Set reference pressure
# (global parameter)
# =================================
def get_coupling_reference_pressure():
    # Global parameters => get value of first block.
    iBlock = 0
    result = FHX_get_coupling_global_params_(iBlock)
    pRef   = result[3]

    return pRef
#--------------------------------------------------------------------------------------------#
def set_coupling_reference_pressure(pRef):
    # Global parameters => get value of first block.
    iBlock = 0
    result = FHX_get_coupling_global_params_(iBlock)
    iMpCCi         = result[0]
    iModalApproach = result[1]
    iOofelie       = result[2]
    FS_pRef        = result[4]
    iRigidMotion   = result[5]

    # Global parameters => set value for all blocks
    for iBlock in get_all_domains():
        FHX_set_coupling_global_params_(iBlock,iMpCCi,iModalApproach,iOofelie,
                                        pRef,FS_pRef,iRigidMotion)


# =================================
# Get/Set coupling patch groups
# =================================
def get_coupling_total_nb_groups():
    # Get total number of coupling groups (including groups that cannot be coupled))
    result = FHX_get_coupling_all_groups_()
    return len(result)

#--------------------------------------------------------------------------------------------#
def get_coupling_nb_groups():
    # Get number of coupling groups
    # Warning: depending the coupling type, some patches cannot be coupled.
    # ==> the returned number may be lower than the total number of groups used internally.
    result = FHX_get_coupling_all_groups_()
    n=0
    for i in range(len(result)):
        if (result[i][0] != "__NOT_COUPLED__"):
            n=n+1
    return n

#--------------------------------------------------------------------------------------------#
def get_coupling_group_index(name):
    # Get coupling group index from name.
    result = FHX_get_coupling_all_groups_()
    idx=0
    for group in result:
        groupname = group[0]
        if (name==groupname):
            return idx
        idx=idx+1
    # Specified group name could not be found !
    return -1

#--------------------------------------------------------------------------------------------#
def add_coupling_patch_to_group(bcpatch, groupName):
    # Add patch to specified group.
    # If group does not exist, it will be created.
    if (get_coupling_mode()==MODAL_APPROACH_COUPLING):
        b,p = bcpatch.get_block_patch()
        FHX_set_coupling_patch_of_group_(groupName,[b-1,0,p-1])
        FHX_update_coupling_patch_data_()
    else:
        print 'WARNING: this patch cannot be modified.'
        print 'Patch can be grouped only when Modal Approach Coupling mode is activated.'
#--------------------------------------------------------------------------------------------#
def remove_coupling_patch_from_group(bcpatch):
    # Remove patch from a group.
    if (get_coupling_mode()==MODAL_APPROACH_COUPLING):
        b,p = bcpatch.get_block_patch()
        FHX_set_coupling_patch_of_group_("Undefined",[b-1,0,p-1])
        FHX_update_coupling_patch_data_()
    else:
        print 'WARNING: this patch cannot be modified.'
        print 'A patch can be ungrouped only when Modal Approach Coupling mode is activated.'

# =================================
# Get/Set patch properties
# =================================
def get_coupling_patch_modal_structure_ID(grpItem):
    if (type(grpItem) is types.IntType):
        # Group/patch is specified from its index
        result = FHX_get_coupling_all_groups_()
        nbGroups = len(result)
        if (grpItem<0 or grpItem>=nbGroups):
            raise IndexError,"Group index out of bounds : " + str(grpItem)
        result=FHX_get_coupling_patch_modal_structure_index_(grpItem)
        return result

    elif (type(grpItem) is types.StringType):
        # Group/patch is specified from its name
        idx = get_coupling_group_index(grpItem)
        if (idx!=-1):
            result=FHX_get_coupling_patch_modal_structure_index_(idx)
            return result
        else:
            # Specified group name could not be found !
            raise ValueError,"Group or patch with name '"+str(grpItem)+"' could not be found !"
                
#--------------------------------------------------------------------------------------------#
def set_coupling_patch_modal_structure_ID(grpItem, structID):
    # ---
    # Check 'grpItem' validity
    # ---
    if (type(grpItem) is types.IntType):
        result = FHX_get_coupling_all_groups_()
        nbGroups = len(result)
        if (grpItem<0 or grpItem>=nbGroups):
            raise IndexError,"Group index out of bounds : " + str(grpItem)
        grpIdx=grpItem
    elif (type(grpItem) is types.StringType):
        # Group/patch is specified from its name
        grpIdx = get_coupling_group_index(grpItem)
        if (grpIdx==-1):
           # Specified group name could not be found !
            raise ValueError,"Group or patch with name '"+str(grpItem)+"' could not be found !"

    # ---
    # Check 'structID' validity
    # ---
    if (structID != -1):
        # ... Check modal structure ID validity
        nb = get_coupling_nb_modal_structures()
        index = -1
        for idx in range(nb):
            IDloc = get_coupling_modal_structure_ID(idx)
            if (IDloc==structID):
                index=idx
                break
        if (index == -1):
            raise ValueError,"Modal structure with ID="+str(structID)+" could not be found."

    # ---
    # Check 'grpIdx' can be modified
    # ---
    result = FHX_get_coupling_all_groups_()
    groupName = result[grpIdx][0]
    if (groupName=="__NOT_COUPLED__" and structID!=-1):
        raise ValueError,"This group "+str(grpItem)+" cannot be coupled."

    # ---
    # Update coupling parameters
    # ---
    if (structID==-1):
        # This group is not coupled, default deformation type = "Fixed"
        not_coupled=0
        fixed_grid=0
        FHX_set_coupling_patch_parameters_(grpIdx,not_coupled,fixed_grid)
    elif (structID>=1):
        # This group is coupled (mechanic + moving grid == only choice)
        mechanic_coupling=2
        moving_grid=1
        FHX_set_coupling_patch_parameters_(grpIdx,mechanic_coupling,moving_grid)

    # ---
    # Attach patch to this modal structure index
    # ---
    FHX_set_coupling_patch_modal_structure_index_(grpIdx, structID)


# =================================
# Get/Set modal structure properties
# =================================
def get_coupling_nb_modal_structures():
    nb = FHX_get_coupling_nb_modal_structure_()
    return nb

#--------------------------------------------------------------------------------------------#
def create_coupling_modal_structure( ID, name, filename, dampingCoefficients ):
    FHX_set_coupling_modal_structure_params_( ID, name, filename, len(dampingCoefficients), dampingCoefficients )

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_ID( idx ):
    # ... Check modal structure index validity
    if (idx<0 or idx>=get_coupling_nb_modal_structures()):
        raise IndexError,"Modal structure index out of bounds : " + str(idx)

    result = FHX_get_coupling_modal_structure_params_( idx )
    return result[0]

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_index( ID ):
    # ... Return modal structure index from its ID
    nb = get_coupling_nb_modal_structures()
    index = -1
    for idx in range(nb):
        IDloc = get_coupling_modal_structure_ID(idx)
        if (IDloc==ID):
            index=idx
            break

    return index

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_name( ID ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    # ... Return structure ID name
    result = FHX_get_coupling_modal_structure_params_( index )
    return result[1]
#--------------------------------------------------------------------------------------------#
def set_coupling_modal_structure_name( ID , name ):
    # ... Check modal structure index validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    result = FHX_get_coupling_modal_structure_params_( index )
    ID = result[0]
    FHX_set_coupling_modal_structure_params_( ID, name, result[2], result[3], result[4] )

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_filename( ID ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    result = FHX_get_coupling_modal_structure_params_( index )
    return result[2]
#--------------------------------------------------------------------------------------------#
def set_coupling_modal_structure_filename( ID , filename ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    result = FHX_get_coupling_modal_structure_params_( index )
    ID = result[0]
    FHX_set_coupling_modal_structure_params_( ID, result[1], filename, result[3], result[4] )

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_nb_modes( ID ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    result = FHX_get_coupling_modal_structure_params_( index )
    return result[3]

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_damping_coefficients( ID ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    # ... Return all damping coefficients
    result = FHX_get_coupling_modal_structure_params_( index )
    coeffs = []
    for imode in range( len(result[4]) ):
        coeffs.append(result[4][imode])
    return coeffs
#--------------------------------------------------------------------------------------------#
def set_coupling_modal_structure_damping_coefficients( ID , coeffs):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    # ... Check damping coefficients validity
    if (len(coeffs)<1):
        raise ValueError,"Minimum "+str(1)+" coefficient expected."
    nbModesMax = get_coupling_modal_structure_max_nb_nodes(ID)
    if (len(coeffs)>nbModesMax):
        raise ValueError,"Maximum "+str(nbModesMax)+" coefficient(s) expected."

    # ... Set all damping coefficients
    result = FHX_get_coupling_modal_structure_params_( index )
    ID = result[0]
    FHX_set_coupling_modal_structure_params_( ID, result[1], result[2], len(coeffs), coeffs )

#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_max_nb_nodes( ID ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    # ... Check structure filename
    structFilename = get_coupling_modal_structure_filename( ID )
    if (structFilename == "unknown"):
        raise ValueError,"Structure filename for modal structure with ID="+str(ID)+" is not defined."

    # ... Extract maximum number of modes from structure file
    nbModes = 0
    inputfile = open(structFilename,"r")
    found = 0
    for line in inputfile:
        for word in line.split():
            if ("mode" in word.lower()):
                found=1
            if (found and word.isdigit()):
                nbModes=int(word)
                found=2;
                break
        if (found==2):
            break
    inputfile.close()

    return nbModes


#--------------------------------------------------------------------------------------------#
def get_coupling_modal_structure_damping_coefficient( ID , imode ):
    # ... Check modal structure ID validity
    index = get_coupling_modal_structure_index(ID)
    if (index == -1):
        raise ValueError,"Modal structure with ID="+str(ID)+" could not be found."

    # ... Check modal structure mode index validity
    if (imode<0 or imode>=get_coupling_modal_structure_nb_modes(ID)):
        raise IndexError,"Modal structure mode index out of bounds : " + str(imode)

    result = FHX_get_coupling_modal_structure_params_( index )
    return result[4][imode]


# =================================
# Get/Set patch deformation type
# =================================
DEFORM_FIXED     = 0 ; # Fixed grid points
DEFORM_MOVING    = 1 ; # Moving grid points
DEFORM_FLOATING  = 2 ; # Floating grid points
DEFORM_FREE      = 3 ; # Free grid points
def get_coupling_patch_deformation_type(grpItem):
    if (type(grpItem) is types.IntType):
        # Group/patch is specified from its index
        result = FHX_get_coupling_all_groups_()
        nbGroups = len(result)
        if (grpItem<0 or grpItem>=nbGroups):
            raise IndexError,"Group index out of bounds : " + str(grpItem)
        couplingType,deformType,structIdx = FHX_get_coupling_patch_parameters_(grpItem)
        return deformType

    elif (type(grpItem) is types.StringType):
        # Group/patch is specified from its name
        idx = get_coupling_group_index(grpItem)
        if (idx!=-1):
            couplingType,deformType,structIdx = FHX_get_coupling_patch_parameters_(idx)
            return deformType
        else:
            # Specified group name could not be found !
            raise ValueError,"Group or patch with name '"+str(grpItem)+"' could not be found !"
                
#--------------------------------------------------------------------------------------------#
def set_coupling_patch_deformation_type(grpItem, deformType):
    # ---
    # Check 'grpItem' validity
    # ---
    if (type(grpItem) is types.IntType):
        result = FHX_get_coupling_all_groups_()
        nbGroups = len(result)
        if (grpItem<0 or grpItem>=nbGroups):
            raise IndexError,"Group index out of bounds : " + str(grpItem)
        grpIdx=grpItem
    elif (type(grpItem) is types.StringType):
        # Group/patch is specified from its name
        grpIdx = get_coupling_group_index(grpItem)
        if (grpIdx==-1):
           # Specified group name could not be found !
            raise ValueError,"Group or patch with name '"+str(grpItem)+"' could not be found !"

    # ---
    # Check 'grpIdx' can be modified
    # ---
    result = FHX_get_coupling_all_groups_()
    groupName = result[grpIdx][0]
    if (groupName=="__NOT_COUPLED__" and structID!=-1):
        raise ValueError,"This group "+str(grpItem)+" cannot be coupled."

    # ---
    # Update coupling parameters
    # ---
    couplingType,dummy,structIdx = FHX_get_coupling_patch_parameters_(grpIdx)
    if (structIdx==-1 and deformType!=DEFORM_MOVING):
        # This group is not coupled, deformation type not "Moving"
        FHX_set_coupling_patch_parameters_(grpIdx,couplingType,deformType)
    elif (structIdx!=-1):
        # This group is coupled (moving grid == only choice)
        print 'WARNING: this patch is coupled.'
        print 'The deformation type cannot be modified.'
        moving_grid=1
        FHX_set_coupling_patch_parameters_(grpIdx,couplingType,DEFORM_MOVING)
