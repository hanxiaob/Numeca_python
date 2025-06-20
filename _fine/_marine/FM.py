#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#--------------------------------------------------------------------------------------------#

import startup
import sys,os,math,copy, os.path

import fnmatch, re, random

from Geom      import *
from IGGSystem import *
import HXP

from MarineModuleCommands import *
from MarineModuleBodyCommands import *
from MarineModuleBcsCommands import *
from MarineModuleAnchorageCommands import *
from MarineModuleActuatorDisksCommands import *
from MarineModuleUQCommands import *
from TurboModuleCommands import *
from TaskModuleCommands import *
from MarineModuleResultsCommands import *
from MarineModuleFSICommands import *
from MarineModuleOversetCommands import *
from MarineModuleAddModelsCommands import *
from MarineModuleJetCommands import *

#
# Deprecated and now meaningless stuff (some kind of backward compatibility)
#

# this functionality was never available in FINE/Marine, it was in F/O/F/T
METER      = 1.0
CENTIMETER = 0.01
MILLIMETER = 0.001
INCH       = 0.0254

def set_mesh_unit_ratio(ratio):
    print 'You can remove set_mesh_unit_ratio function call, it is obsolete'

# these functions were never documented and they had no meaning from user's POV
def set_rw_sw_body_param(flag):
    print 'You can remove set_rw_sw_body_param function call, it is obsolete'

def set_rw_sw_body_param_velrel(flag):
    print 'You can remove set_rw_sw_body_param_velrel function call, it is obsolete'

# not documented and is more like detail of solver's implementation
def get_RW_mode():
    print 'You can remove get_RW_mode function call, it is obsolete'
    return 0

def set_RW_mode(mode_num):
    print 'You can remove set_RW_mode function call, it is obsolete'

#--------------------------------------------------------------------------------------------#
#                                Global query functions                                      #
#--------------------------------------------------------------------------------------------#

def is_batch():
    return ("-batch" in sys.argv)

#--------------------------------------------------------------------------------------------#
DEFAULT_WELCOME=0
SUPPRESS_WELCOME=1
SHOW_WELCOME=2
def switch_to_HEXPRESS(suppress_welcome=DEFAULT_WELCOME):
    if not is_batch():
        FM_switch_to_HEXPRESS(suppress_welcome)

#--------------------------------------------------------------------------------------------#
def switch_HEXPRESS_to_FM(mode = 6):
    # 6 = 4 + 2, Not save mesh and Yes, use new .igg from HEXPRESS if changed
    if is_batch():
        # for now, it works only in batch
        FM_switch_from_HEXPRESS
    else:
        eval_tcl_string( " changeProductFromHexpressToMarine " + str(mode))

#--------------------------------------------------------------------------------------------#
def close_HEXPRESS():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( " changeProductFromHexpressToMarine 6" )

#--------------------------------------------------------------------------------------------#

def switch_to_Task_Manager():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( " changeProduct \"Task Manager\"" )

#--------------------------------------------------------------------------------------------#

def close_Task_Manager():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( " changeProductFromTaskManagerToFineMarine" )

#--------------------------------------------------------------------------------------------#
#----                             Parameters management                                  ----#
#--------------------------------------------------------------------------------------------#

NO  = 0
YES = 1

OFF = 0
ON  = 1

INTEGER  = "INTEGER"
REAL     = "REAL"
STRING   = "STRING"

# param_num - value index for array parameters
# use 0 for single values

def set_parameter(name,param_type,param_num,value):
    FM_set_parameter(name,param_type,param_num,value)

def get_parameter(name,param_num):
    res = FM_get_parameter(name,param_num)
    if int(res[0]) == 1:
        return res[1]
    else:
        raise ValueError, "Parameter " + name + ' not found.'

# returns pair {code {result}}
# code - 0 or 1 - specifies result state (0 - parameter not found)
# result - list of complex parameter values
def get_complete_parameter(name):
    res = FM_get_complete_parameter(name)
    if int(res[0]) == 1:
        return res[1]
    else:
        raise ValueError, "Parameter " + name + ' not found.'

def set_simple_int_parameter(name,value):
    FM_set_parameter(name,INTEGER,0,value)

def set_simple_real_parameter(name,value):
    FM_set_parameter(name,REAL,0,value)

def set_simple_string_parameter(name,value):
    FM_set_parameter(name,STRING,0,value)

def set_custom_parameter(paramName,paramTypeName,isisString,paramPrint,paramExpert,paramSize,param):
    FM_set_custom_parameter(paramName,paramTypeName,isisString,paramPrint,paramExpert,paramSize,param)

def get_mean_parameter(number):
    return FM_get_mean_para(number)

def set_mean_parameter(number,flag):
    FM_set_mean_para(number,flag)

def get_optional_parameter(number):
    return FM_get_optional_parameter(number)

def set_optional_parameter(number,flag):
    FM_set_optional_parameter(number,flag)

def get_expert_integer_parameters(name):
    return FM_get_expert_integer_parameters(name)

def set_expert_integer_parameters(name,length,num,intval):
    FM_set_expert_integer_parameters(name,length,num,intval)

def get_expert_real_parameters(name):
    return FM_get_expert_real_parameters(name)

def set_expert_real_parameters(name,length,num,realnum):
    FM_set_expert_real_parameters(name,length,num,realnum)

def get_expert_string_parameters(name):
    return FM_get_expert_string_parameters(name)

def set_expert_string_parameters(name,length,num,realnum):
    FM_set_expert_string_parameters(name,length,num,realnum)

#--------------------------------------------------------------------------------------------#
#----                              Project management                                    ----#
#--------------------------------------------------------------------------------------------#

def get_project_file_name():
    path = FM_get_project_path()
    name = FM_get_project_name()
    return path,name

def create_project(projectname):
    dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
    basename = os.path.basename(projectname)
    FM_create_new_project(basename, dirname)
    eval_tcl_string("itm_project:update_titlebar")
    HXP.close_project()

def get_mesh_location():
    return FM_get_mesh_location()

def get_mesh_file_igg():
    return FM_get_mesh_location() + FM_get_mesh_file()

def get_mesh_file_dom():
    igg_name = FM_get_mesh_file()
    name,ext = os.path.splitext(igg_name)
    name = FM_get_mesh_location() + name + '.dom'
    if not os.path.exists(name):
        raise ValueError("Domain file does not exist",name)
    return name

def get_mesh_file_bcs():
    igg_name = FM_get_mesh_file()
    name,ext = os.path.splitext(igg_name)
    name = FM_get_mesh_location() + name + '.bcs'
    if not os.path.exists(name):
        raise ValueError("BC file does not exist",name)
    return name

def get_mesh_file_hex():
    igg_name = FM_get_mesh_file()
    name,ext = os.path.splitext(igg_name)
    name = FM_get_mesh_location() + name + '.hex'
    if not os.path.exists(name):
        raise ValueError("hex mesh file does not exist",name)
    return name

#--------------------------------------------------------------------------------------------#

def close_project():

    # itm_project:new_project displays Create new project dialog,
    # but it isn't what the user wants to do when calls FM.close_project() sure.
    # bug 17558 + bug 18187

    if is_batch():
        FM_new_project()
        HXP.close_project()
    else:
        # do not save the project implicitly
        eval_tcl_string("itm_project:new_project_wo_startup_dialog NO")

#--------------------------------------------------------------------------------------------#

def open_project(projectname):
    projectname = os.path.abspath(projectname) # for ones using ..
    dirname  = os.path.dirname(projectname)+os.sep
    basename = os.path.basename(projectname)

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( " itf_do_open_project {"+projectname+"}" )
    else:
        ## BATCH MODE
        FM_open_project(basename,dirname)

#--------------------------------------------------------------------------------------------#

def save_project():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string("topToolBar:itf_save_all_project")
    else:
        ## BATCH MODE
        FM_save_project()

def duplicate_project(newProjectLocation, newProjectName, duplicateResults):
    if is_batch():
        FM_duplicate_project(newProjectName, newProjectLocation, duplicateResults)
    else:
        full_path = os.path.join(newProjectLocation, newProjectName)
        command = \
            "global itf_save_as app; " + \
            "set itf_save_as(duplicateComputation) " + str(duplicateResults) + "; " + \
            "set app(forbid_GUI_messages) 1; " + \
            "itf_do_save_as_new_project2 {" + full_path + "}; " + \
            "set app(forbid_GUI_messages) 0"
        eval_tcl_string(command)

def create_backup(folder_name, compress=0):
    FM_create_backup(folder_name, compress)

def reset_computation():
    return FM_reset_computation()

def move_computation_up():
    FM_move_computation_up()

def move_computation_down():
    FM_move_computation_down()

def link_mesh_file(meshfile, move_files=False):
    # 21025 expand relative paths
    meshfile = os.path.abspath(meshfile)

    if is_batch():
        if move_files:
            project_dir = FM_get_project_path()
            mesh_dir = os.path.join(project_dir, '_mesh')
            proper_name = os.path.basename(meshfile)
            FM_move_mesh_files(meshfile, mesh_dir)
            meshfile = os.path.join(mesh_dir, proper_name)

        FT_set_project_igg_file_name(meshfile)
    else:
        eval_tcl_string("itm_project:import_mesh {" + meshfile + "} NO " + str(move_files))

    update_body_list()

#--------------------------------------------------------------------------------------------#
#----                            Computation management                                   ---#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#

def get_nb_computations():
    nc = FT_get_nb_computations()
    return nc


def set_active_computation(idx):
    return set_active_computations([idx])

def set_active_computations(idx_list):
    dotted = []

    for idx in idx_list:
        if isinstance(idx, list) or isinstance(idx, tuple):
            cur = str(idx[0]) + "." + str(idx[1])
        else:
            cur = str(idx)

        dotted.append(cur)

    stat = FM_set_active_computations(*dotted)

    if not is_batch():
        eval_tcl_string("itm_computations:get_computations_names")

    return stat

def get_active_computations():
    return FM_get_active_computations()

def get_active_computation():
    result = FM_get_active_computation()
    return result

#--------------------------------------------------------------------------------------------#

def get_computation_name(index):
    if isinstance(index, list) or isinstance(index, tuple):
        rc = FT_get_computation_name(*index)
    else:
        rc = FT_get_computation_name(index)

    return rc[0]

#--------------------------------------------------------------------------------------------#

def set_computation_name(index,name):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    old_name = get_computation_name(index)

    if (name != old_name):
        if __comp_name_exists(name):
            print 'Error! set_computation_name: computation with name "' + name + '" already exists.'
        else:
            FM_set_computation_name_real(index, name)
            FM_save_project()

            if not is_batch():
                eval_tcl_string(" itm_computations:get_computations_names ")

def _strip_suffix(str, suffix):
    res = str
    n = len(suffix)

    if str[-n:] == suffix:
        res = str[:-n]

    return res

def _strip_prefix(str, prefix):
    res = str
    n = len(prefix)

    if str[:n] == prefix:
        res = str[n:]

    return res

def restart_from_previous_computation(name,import_history = 1):
    if name == "":
        set_initial_solution_type(0)
    else:
        set_initial_solution_type(1) # restart
        # extract only the proper file name w/o extension
        t = os.path.basename(name)
        t = _strip_suffix(t, '.sim')
        p = FM_get_project_name()
        p = _strip_suffix(p, '.iec')
        t = _strip_prefix(t, p + '_')
        set_initial_solution_computation(t) # restart from this computation

    if import_history:
        arg = "YES"
    else:
        arg = "NO"

    set_convergence_accu(arg)
    # set interface position as in the initial computation
    ctx = get_active_computations()
    n = get_nb_computations()
    i = 0
    found = False

    while (i < n) and not found:
        cur_name = get_computation_name(i)

        if cur_name == name:
            found = True
            set_active_computation(i)
        else:
            m = get_nb_of_subcomputations(i)
            j = 0

            while j < m and not found:
                cur_name = get_computation_name([i, j])

                if cur_name == name:
                    fount = True
                    set_active_computation([i, j])

                j += 1

        i += 1

    if found:
        z = get_initial_interface_position()
        set_active_computations(ctx)
        set_initial_interface_position(z)

def get_initial_solution_type():
    return FM_get_initial_solution_type()

def set_initial_solution_type(restart):
	FM_set_initial_solution_type(restart)

def get_initial_solution_computation():
	return FM_get_initial_computation()

def set_initial_solution_computation(name):
	FM_set_initial_computation(name)

#--------------------------------------------------------------------------------------------#

def save_active_computation():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" topToolBar:itm_save_simulation_file yes ")
    else:
        ## BATCH MODE
        FM_save_active_computation()

def save_1st_active_computation():
    if is_batch():
        FM_save_1st_active_computation()
    else:
        eval_tcl_string("topToolBar:save_1st_active_computation yes")

def __comp_name_exists(name):
    n = get_nb_computations()
    i = 0
    found = False

    while (i < n) and not found:
        cur_name = get_computation_name(i)

        if cur_name == name:
            found = True
        else:
            m = get_nb_of_subcomputations(i)
            j = 0

            while j < m and not found:
                cur_name = get_computation_name([i, j])
                found = (cur_name == name)
                j += 1

        i += 1

    return found

#--------------------------------------------------------------------------------------------#
def new_computation(name):
    nc = get_nb_computations()

	# bug 17622
    # Ensure unique computation name
    while __comp_name_exists(name):
        name = "new_" + name

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string("itm_computations:new")
        set_active_computation(nc)
        FM_set_computation_name_internal(nc, name, 0)
        eval_tcl_string("itm_computations:get_computations_names")
    else:
        ## BATCH MODE
        # ideally internal part of itm_computaion:new
        # which doesn't deal with GUI should be called there
        FT_set_nb_computations(nc + 1)
        set_active_computation(nc)
        oldname = get_computation_name(nc)
        # bug 17222
        FM_set_computation_name_internal(nc, name, 0)
        FT_update_marine_params(oldname, nc)
    FM_save_project()

def delete_computation(index):
    nc = get_nb_computations()
    if (index<0 or index>=nc):
        raise IndexError,"Computation index out of bounds : " + str(index)
    elif nc == 1:
        raise IndexError,"Cannot delete last computation in the system"
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" global itf_adm")
        eval_tcl_string(" set itf_adm(removefile) 1")
        eval_tcl_string(" itm_computations:remove_selected_ " + str(index))
        eval_tcl_string(" itm_computations:set_new_name")
    else:
        ## BATCH MODE
        FM_delete_computation(index, 1)
        FT_set_nb_computations(nc - 1)
        set_active_computation(nc - 2)
        FM_save_project()

# absolute path to the sim-file of the first selected computation
def get_computation_path():
    no = get_active_computation()

    if (isinstance(no, list) or isinstance(no, tuple)) and len(no) == 2:
        res = FM_get_computation_path(no[0], no[1])
    else:
        res = FM_get_computation_path(no)

    return res

def get_sim_file():
    return FM_get_sim_file()

def get_comments():
    return FM_get_comments()

def set_comments(comments):
    FM_set_comments(comments)

#--------------------------------------------------------------------------------------------#
#----                                 Batch file                                         ----#
#--------------------------------------------------------------------------------------------#

def save_batch_file(task):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_taskmgr_tasks:saveScriptAsBatch "+str(task))
    else:
        print 'save batch for the task: '+str(task)

#--------------------------------------------------------------------------------------------#
#----                              Mesh properties                                       ----#
#--------------------------------------------------------------------------------------------#

def get_nb_domains():
    return FM_get_nb_domains()

def get_nb_domain_patches(idx):
    # ... Check domain index validity
    if (idx<0 or idx>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(idx)
    # ... Get nb of patches for domain idx
    return FM_get_nb_domain_patches(idx)

#--------------------------------------------------------------------------------------------#

def get_domain_name(idx):
    # ... Check domain index validity
    if (idx<0 or idx>=get_nb_domains()):
        raise IndexError,"Domain index out of bounds : " + str(idx)
    name = FM_get_domain_name(idx)
    return name
#--------------------------------------------------------------------------------------------#

def get_domain_list():
    domList = []
    for idx in range(0,get_nb_domains()):
        domList.append([idx,FM_get_domain_name(idx)])
    return domList

def get_all_domains():
    names = []

    for i in range(0, get_nb_domains()):
        names.append(FM_get_domain_name(i))

    return names

#--------------------------------------------------------------------------------------------#
class BCParameter:
    def __init__(self):
        self._type = "constant"
        self._value = 0.0
        self._out_filename = ""
        self._in_filename = ""
        self._profile_points = []

    def get_type(self):
        return self._type

    def set_type(self, type):
        self._type = type

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def get_in_filename(self):
        return self._in_filename

    def set_in_filename(self, filename):
        self._in_filename = filename

    def get_out_filename(self):
        return self._out_filename

    def set_out_filename(self, filename):
        self._out_filename = filename

    def get_profile_points(self):
        return self._profile_points

    def set_profile_points(self, points):
        self._profile_points = points

class BCPatch:
    def __init__(self,blockID,patchID):
        self._blockID    = blockID
        self._patchID    = patchID

    def get_name(self):
        return FM_get_patch_name(self._blockID,1,self._patchID)

    def set_name(self,name):
        FM_set_patch_name(self._blockID,1,self._patchID,name)

    def get_block_patch(self):
        return self._blockID,self._patchID

    def get_bc_name(self):
        return FM_get_bc_name(self._blockID,1,self._patchID)

    def get_bc_type(self):
        bc_id,bc_opsel = FM_get_bc_values(self._blockID,1,self._patchID)
        return [bc_id,bc_opsel]

    def set_bc_type(self,value):
		# bug 17410 opsel isn't used in FINE/Marine
        if isinstance(value, list):
            bc_id    = value[0]
            bc_opsel = value[1]
        else:
            bc_id = value
            bc_opsel = -1
        FM_set_bc_values(self._blockID,1,self._patchID,bc_id,bc_opsel)

    def get_parameter_type(self, parameter_name):
        return FM_get_BC_parameter_type(self._blockID, self._patchID, parameter_name)

    def get_parameter_value(self, parameter_name):
        parameter_type = self.get_parameter_type(parameter_name)
        result = None

        if parameter_type == 0:
            print 'Error in BCPatch.get_parameter_type! '\
                  'The parameter "{}" is not found in block #{}, patch #{}.'.format(parameter_name,
                                                                                    self._blockID,
                                                                                    self._patchID)
        elif parameter_type == 1:
            result = FM_get_integer_BC_parameter(self._blockID, self._patchID, parameter_name)
        elif parameter_type == 2:
            result = FM_get_real_BC_parameter(self._blockID, self._patchID, parameter_name)
        elif parameter_type == 3:
            type, value, out_filename, in_filename, points = \
                FM_get_bc_physical_entry(self._blockID, self._patchID, parameter_name)
            p = BCParameter()
            p.set_type(type)
            p.set_value(value)
            p.set_out_filename(out_filename)
            p.set_in_filename(in_filename)
            p.set_profile_points(list(points))
            result = p
        else:
            print 'Error in BCPatch.get_parameter_type! '\
                  'Parameter "{}" in block #{}, patch #{}, has unknown type {}'.format(parameter_name,
                                                                                    self._blockID,
                                                                                    self._patchID,
                                                                                    parameter_type)

        return result

    def set_parameter_value(self, parameter_name, parameter):
        parameter_type = self.get_parameter_type(parameter_name)

        if parameter_type == 0:
            print 'Error in BCPatch.set_parameter_type! '\
                  'The parameter "{}" is not found in block #{}, patch #{}.'.format(parameter_name,
                                                                                    self._blockID,
                                                                                    self._patchID)
        elif parameter_type == 1:
            FM_set_integer_BC_parameter(self._blockID, self._patchID, parameter_name, parameter)
        elif parameter_type == 2:
            FM_set_real_BC_parameter(self._blockID, self._patchID, parameter_name, parameter)
        elif parameter_type == 3:
            flat_coords = []
            points = parameter.get_profile_points()
            n = len(points)

            for p in points:
                flat_coords.append(p[0])
                flat_coords.append(p[1])
                flat_coords.append(p[2])

            FM_set_bc_physical_entry(self._blockID, self._patchID, parameter_name,
                parameter.get_type(), parameter.get_value(),
                parameter.get_out_filename(), parameter.get_in_filename(),
                n, *flat_coords)
        else:
            print 'Error in BCPatch.set_parameter_type! '\
                  'Parameter "{}" in block #{}, patch #{}, has unknown type {}'.format(parameter_name,
                                                                                    self._blockID,
                                                                                    self._patchID,
                                                                                    parameter_type)
    def set_passive_scalar(self, on, value):
        FM_set_passive_scalar_bc_value(self._blockID, self._patchID, on, value)

    def get_passive_scalar(self):
        return FM_get_passive_scalar_bc_value(self._blockID, self._patchID)

    def get_jet(self):
        jet_name = FM_get_patch_jet(self._blockID, self._patchID)
        return Jet(jet_name)

    def set_jet(self, jet):
        FM_set_patch_jet(self._blockID, self._patchID, jet._name)

    def get_sand_grain_height(self):
        return FM_get_patch_sand_grain_height(self._blockID, self._patchID)

    def set_sand_grain_height(self, height):
        FM_set_patch_sand_grain_height(self._blockID, self._patchID, height)

#--------------------------------------------------------------------------------------------#
#------------------------------ Fluid Model -------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def set_fluid_model_number(nFluids):
    FM_set_multifluid_model_number(nFluids)

def get_fluid_model_number():
    return FM_get_multifluid_model_number()

def get_fluid_name(model):
    if model == 1:
        return FM_get_fluid_model_name(0)
    elif model == 2:
        return FM_get_multifluid_model_name()
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."

def set_fluid_name(model,name):
    if model == 1:
        #FM_set_fluid_model_name(name) - encoding problem
        set_simple_string_parameter("nameFluid1_",name)
        set_simple_string_parameter("nameFluid_",name)
    elif model == 2:
        #FM_set_multifluid_name(name)
        set_simple_string_parameter("nameFluid2_",name)
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."

def get_fluid_viscosity(model):
    if model == 1:
        return FM_get_fluid_model_viscosity(0)
    elif model == 2:
        viscosity,density = FM_get_multifluid_model_viscosity_density()
        return viscosity
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."

def set_fluid_viscosity(model,viscosity):
    if model == 1:
        FM_set_fluid_model_viscosity(0,viscosity)
    elif model == 2:
        tmp,density = FM_get_multifluid_model_viscosity_density()
        FM_set_multifluid_model_viscosity_density(viscosity,density)
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."

def get_fluid_density(model):
    if model == 1:
        return FM_get_fluid_model_density(0)
    elif model == 2:
        viscosity,density = FM_get_multifluid_model_viscosity_density()
        return density
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."

def set_fluid_density(model,density):
    if model == 1:
        FM_set_fluid_model_density(0,density)
    elif model == 2:
        viscosity,tmp = FM_get_multifluid_model_viscosity_density()
        FM_set_multifluid_model_viscosity_density(viscosity,density)
    else:
        raise ValueError, "Fluid model " + str(model) + " does not exists."



# =================================
# Get/Set time configuration:
# steady/unsteady  <==> iTimeAccurate_ = 0/1
# =================================
STEADY   = 0
UNSTEADY = 1
#--------------------------------------------------------------------------------------------#
def get_time_configuration():
    return FM_get_time_configuration()
#    flag = FM_get_time_configuration()
#    if flag == 0:
#        return "STEADY"
#    else:
#        return "UNSTEADY"

def set_time_configuration(mode):
    FM_set_time_configuration(mode)
#    flag = 0
#    if mode == "UNSTEADY":
#        flag = 1
#    FM_set_time_configuration(flag)

#--------------------------------------------------------------------------------------------#
#------------------------------ Flow Model parameters ---------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_flow_model_turb_model(block=0):
    return FM_get_flow_model_math_model()

def set_flow_model_turb_model(model):
    FM_set_flow_model_math_model(0,model)

def get_flow_model_gravity_parameters():
#    return FM_get_flow_model_gravity_parameters(block)
    x = get_parameter("gVector_",0)
    y = get_parameter("gVector_",1)
    z = get_parameter("gVector_",2)
    return x,y,z

def set_flow_model_gravity_parameters(x,y,z):
#    FM_set_flow_model_gravity_parameters(block,x,y,z)
    if get_fluid_model_number() == 1:
        print 'FM.set_flow_model_gravity_parameters: ignored in mono-fluid'

    set_parameter("gVector_",REAL,0,x)
    set_parameter("gVector_",REAL,1,y)
    set_parameter("gVector_",REAL,2,z)

def get_flow_model_reference_parameters():
    length = get_parameter("refLength_",0)
    velocity = get_parameter("refVelocity_",0)
    return length,velocity

def set_flow_model_reference_parameters(LRef,velRef):
    FM_set_flow_model_reference_parameters(LRef,velRef)

def get_control_variables():
    return FM_get_control_variables()

def set_control_variables(max_iterations,order,time_step,freq_saving):
    FM_set_control_variables(max_iterations,order,time_step,freq_saving)

def get_timelaw():
    return FM_get_timelaw()

def set_timelaw(tlaw,a,b,c,d):
    FM_set_timelaw(tlaw,a,b,c,d)
    FM_set_ctr_page_open(1) # pretend that Control variables page has been visited

def get_timesplit_active():
    return get_parameter("splitActivation_",0)

def set_timesplit_active(ans):
    FM_set_timesplit_active(ans)

def get_travelling_shot_parameters():
    Tx = get_parameter("TravellingShot_",0)
    Ty = get_parameter("TravellingShot_",1)
    Tz = get_parameter("TravellingShot_",2)
    Rx = get_parameter("TravellingShot_",3)
    Ry = get_parameter("TravellingShot_",4)
    Rz = get_parameter("TravellingShot_",5)
    bodyID = get_parameter("TravellingShotBody_",0)
    return bodyID,Tx,Ty,Tz,Rx,Ry,Rz

def get_traveling_shot_parameters():
    return get_travelling_shot_parameters()

def set_travelling_shot_parameters(bodyID,Tx,Ty,Tz,Rx,Ry,Rz):
    FM_set_travelling_shot_parameters(Tx,Ty,Tz,Rx,Ry,Rz,bodyID)

def set_traveling_shot_parameters(bodyID,Tx,Ty,Tz,Rx,Ry,Rz):
    set_travelling_shot_parameters(bodyID,Tx,Ty,Tz,Rx,Ry,Rz)

# Four functions below are not used any more and kept for backward compatibility with 3.0-1.
# To manage probes, use functions below, sec. output management.

def get_probe_para(iQuant,iProbe):
    return get_volume_probe(iQuant)

def set_probe_para(para_num,num,val1,val2,type,saveToSim):
    if type == 'seconds':
        interv = val2
    else:
        interv = val1

    enable = (interv > 0 and saveToSim)
    set_volume_probe(para_num, enable)
    set_volume_probe_interval(interv, type)

def get_probe_parameter(para_num):
    return get_volume_probe(para_num)

def set_probe_parameter(para_num,num,saveToSim):
    set_volume_probe(para_num, num and saveToSim)

#--------------------------------------------------------------------------------------------#
#-------------------------- Boundary Conditions parameters ----------------------------------#
#--------------------------------------------------------------------------------------------#

def set_real_bc_value(block,face,patch,index,val):
    FM_set_real_bc_value(block,face,patch,index,val)

def get_bc_value(block,face,patch):
    return FM_get_bc_value(block,face,patch)

def set_bc_value(block,face,patch,bc_no):
    FM_set_bc_value(block,face,patch,bc_no)

def get_grid_bc(block,face,patch):
    return FM_get_grid_bc(block,patch)

def set_grid_bc(block,face,patch,grid_bc_no):
    FM_set_grid_bc(block,patch,grid_bc_no)

def get_far_velocity():
    return FM_get_far_velocity()

def set_far_velocity(x,y,z):
    FM_set_far_velocity(x,y,z)

def get_FF_profile_type(block,face,patch):
    return FM_get_FF_profile_type(block,face,patch)

def set_FF_profile_type(block,face,patch,t):
    FM_set_FF_profile_type(block,face,patch,t)

def get_FF_velocity(block,face,patch):
    return FM_get_FF_velocity(block,face,patch)

def set_FF_velocity(block,face,patch,*data):
    FM_set_FF_velocity(block,face,patch,*data)

def get_FF_turb_kenergy(block,face,patch):
    return FM_get_FF_turb_kenergy(block,face,patch)

def set_FF_turb_kenergy(block,face,patch,*data):
    FM_set_FF_turb_kenergy(block,face,patch,*data)

def get_FF_turb_dissip(block,face,patch):
    return FM_get_FF_turb_dissip(block,face,patch)

def set_FF_turb_dissip(block,face,patch,*data):
    FM_set_FF_turb_dissip(block,face,patch,*data)

def get_FF_turb_viscosity(block,face,patch):
    return FM_get_FF_turb_viscosity(block,face,patch)

def set_FF_turb_viscosity(block,face,patch,*data):
    FM_set_FF_turb_viscosity(block,face,patch,*data)

def get_FF_mass_fraction(block,face,patch):
    return FM_get_FF_mass_fraction(block,face,patch)

def set_FF_mass_fraction(block,face,patch,value):
    FM_set_FF_mass_fraction(block,face,patch,value)

def get_FF_turb_length_scale(block,face,patch):
    return FM_get_FF_turb_length_scale(block,face,patch)

def set_FF_turb_length_scale(block,face,patch,value):
    FM_set_FF_turb_length_scale(block,face,patch,value)

def get_wave_parameters():
    print "get_wave_parameters is deprecated. Use get_WaVe_params instead"
    speed,order,dp,propX,propY,refX,refY,height,period,spectrum_id = FM_get_wave_params()
    spectrum = "REGULAR"
    if spectrum_id == 1:
        spectrum = "ITTC"
    elif spectrum_id == 2:
        spectrum = "JONSWAP"
    elif spectrum_id == 3:
        spectrum = "PIERSON-MOSKOWITZ"
    return speed,order,dp,propX,propY,refX,refY,height,period,spectrum

def get_wave_params():
    print "get_wave_params is deprecated. Use get_WaVe_params instead"
    speed,order,dp,propX,propY,refX,refY,height,period,spectrum_id = FM_get_wave_params()
    return speed,order,dp,propX,propY,refX,refY,height,period

def set_wave_parameters(flag,speed,order,dp,propX,propY,refX,refY,amp0,amp1,spectrum="REGULAR"):
    print "set_wave_parameters is deprecated. Use set_WaVe_params instead"
    spectrum_id = 0
    if spectrum == "ITTC":
        spectrum_id = 1
    elif spectrum == "JONSWAP":
        spectrum_id = 2
    elif spectrum == "PIERSON-MOSKOWITZ":
        spectrum_id = 3
    FM_set_wave_params(flag,speed,order,dp,propX,propY,refX,refY,amp0,amp1,spectrum_id)

def set_wave_params(flag,speed,order,dp,propX,propY,refX,refY,amp0,amp1):
    print "set_wave_params is deprecated. Use set_WaVe_params instead"
    FM_set_wave_params(flag,speed,order,dp,propX,propY,refX,refY,amp0,amp1)

# the most relevant version
def get_WaVe_params():
    s, order, depth, dirx, diry, refx, refy, h, p, gamma = FM_get_WaVe_params()
    return [s, order, depth, dirx, diry, refx, refy, h, p, gamma]

# unused quantities may be arbitrary
def set_WaVe_params(spectrum, wave_order, depth, propdirx, propdixy, refx, refy, height, period, gamma):
    FM_set_WaVe_params(spectrum, wave_order, depth, propdirx, propdixy, refx, refy, height, period, gamma)

def get_irr_waves_file():
    return FM_get_irr_waves_file()

def get_irregular_waves_file():
    sim = get_computation_path()
    dir = os.path.dirname(sim)
    file = get_irr_waves_file()
    file = os.path.join(dir, file)
    return file

def set_irregular_waves_file(name):
    FM_set_irr_waves_file(name)

def bcs_status_change(i):
    FM_bcs_status_change(i)

def get_bc_patch_by_patch(patch):
    return BCPatch(1,patch+1)

def get_bc_patch(block,patch):
    return BCPatch(block+1,patch+1)

def get_bc_patch_by_name(name):
    for b in range( get_nb_domains() ):
        for p in range( get_nb_domain_patches(b) ):
            patch = get_bc_patch(b,p)
            if (patch.get_name() == name):
                return patch
    raise ValueError,"Wrong patch name : " + name
    return None

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
#--------------------------------- Body commands --------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_body_list():
    return FM_get_body_list()

def get_nb_bodies():
    return FM_get_nb_bodies()

def set_body(bodyId,bodyName,nPatches,*patches):
    FM_set_body(bodyId, bodyName, nPatches, patches)

def remove_patch_from_body(block, face, patch):
    FM_set_body(0, "", 1, [[block, face, patch]])

def set_body_by_patch_name(bodyName,value):
    if ( type(value) is types.ListType ):
        # Exhaustive list of patches to group
        bc_patch_list = value
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        bc_patch_list = get_bc_patch_list(pattern)
    else:
        raise ValueError, "Wrong type : " + str(type(value))

    patchList=[]

    for bc_patch in bc_patch_list:
        b, p = bc_patch.get_block_patch()
        patchList.append([b - 1, 0, p - 1])

    new_id = 0

    for body_entry in get_body_list():
        bodyID = body_entry[0]

        if bodyID > new_id:
            new_id = bodyID

    new_id += 1

    FM_set_body(new_id, bodyName, len(patchList), patchList)
    return new_id


def get_subBody_list():
    return FM_get_subBody_list()

def set_subBody(subBodyId,subBodyName,nPatches,*patches):
    i = 0
    while i < nPatches:
        # Every patch[i] composes [block, face, patch]
        block = patches[i][0]
        face = patches[i][1]
        patch = patches[i][2]
        i = i + 1
        FM_set_subBody(block,face,patch,subBodyId,subBodyName)

def remove_patch_from_subBody(block,face,patch):
    FM_set_subBody(block,face,patch,0,"")

def get_body_domain(bodyId):
    return FM_get_body_domain(bodyId)

def set_body_domain(bodyId,domainId):
    set_domain_motion_source(domainId, bodyId)

def get_domain_motion_source(domainId):
    return FM_get_domain_motion_source(domainId)

def set_domain_motion_source(domainId, bodyId):
    FM_set_domain_motion_source(domainId, bodyId)

def update_body_list():
    FM_update_body_list()

def get_body_motion_outputs():
    Tx = get_parameter("BodyOutputDofTrans_",0)
    Ty = get_parameter("BodyOutputDofTrans_",1)
    Tz = get_parameter("BodyOutputDofTrans_",2)
    R0 = get_parameter("BodyOutputDofRot_",0)
    R1 = get_parameter("BodyOutputDofRot_",1)
    R2 = get_parameter("BodyOutputDofRot_",2)
    R3 = get_parameter("BodyOutputDofRot_",3)
    Vx = get_parameter("BodyOutputDofVel_",0)
    Vy = get_parameter("BodyOutputDofVel_",1)
    Vz = get_parameter("BodyOutputDofVel_",2)
    dRx = get_parameter("BodyOutputDofAngVel_",0)
    dRy = get_parameter("BodyOutputDofAngVel_",1)
    dRz = get_parameter("BodyOutputDofAngVel_",2)
    Ax = get_parameter("BodyOutputDofAccel_",0)
    Ay = get_parameter("BodyOutputDofAccel_",1)
    Az = get_parameter("BodyOutputDofAccel_",2)
    d2Rx = get_parameter("BodyOutputDofAngAccel_",0)
    d2Ry = get_parameter("BodyOutputDofAngAccel_",1)
    d2Rz = get_parameter("BodyOutputDofAngAccel_",2)
    return Tx,Ty,Tz,R0,R1,R2,R3,Vx,Vy,Vz,dRx,dRy,dRz,Ax,Ay,Az,d2Rx,d2Ry,d2Rz

def set_body_motion_outputs(Tx,Ty,Tz,R0,R1,R2,R3,Vx,Vy,Vz,dRx,dRy,dRz,Ax,Ay,Az,d2Rx,d2Ry,d2Rz):
    FM_set_body_motion_outputs(Tx,Ty,Tz,R0,R1,R2,R3,Vx,Vy,Vz,dRx,dRy,dRz,Ax,Ay,Az,d2Rx,d2Ry,d2Rz)

def get_body_motion_type(bodyId):
    return FM_get_body_motion_type(bodyId)

def set_body_motion_type(body,Tx,Ty,Tz,Rx,Ry,Rz):
    FM_set_body_motion_type(body,Tx,Ty,Tz,Rx,Ry,Rz)

def get_body_motion_law(bodyId):
    #14766 Make law 'None' if it is attached to the fixed or solved DOF
    lawList = list(FM_get_body_motion_law(bodyId))
    Tx,Ty,Tz,Rx,Ry,Rz = FM_get_body_motion_type(bodyId)
    if Tx in ['Fixed', 'Solved']:
        lawList[0] = 'None'
    if Ty in ['Fixed', 'Solved']:
        lawList[1] = 'None'
    if Tz in ['Fixed', 'Solved']:
        lawList[2] = 'None'
    if Rx in ['Fixed', 'Solved']:
        lawList[3] = 'None'
    if Ry in ['Fixed', 'Solved']:
        lawList[4] = 'None'
    if Rz in ['Fixed', 'Solved']:
        lawList[5] = 'None'
    return lawList

def set_body_motion_law(bodyId,lawStrTx,lawStrTy,lawStrTz,lawStrRx,lawStrRy,lawStrRz):
    FM_set_body_motion_law(bodyId,lawStrTx,lawStrTy,lawStrTz,lawStrRx,lawStrRy,lawStrRz)

def get_body_motion_params(dobyId,dof):
    return FM_get_body_motion_params(dobyId,dof)

def get_body_motion_parameters(dobyId,dof):
    return FM_get_body_motion_params(dobyId,dof)

def set_body_motion_params(bodyId,paramsTx,paramsTy,paramsTz,paramsRx,paramsRy,paramsRz):
    paramList = []

    for v in paramsTx:
        paramList.append(v)

    for v in paramsTy:
        paramList.append(v)

    for v in paramsTz:
        paramList.append(v)

    for v in paramsRx:
        paramList.append(v)

    for v in paramsRy:
        paramList.append(v)

    for v in paramsRz:
        paramList.append(v)

    FM_set_body_motion_params(bodyId, *paramList)

def set_body_motion_parameters(bodyId,paramsTx,paramsTy,paramsTz,paramsRx,paramsRy,paramsRz):
    set_body_motion_params(bodyId, paramsTx, paramsTy, paramsTz, paramsRx, paramsRy, paramsRz)

def get_body_motion_refPoint(bodyId):
    return FM_get_body_motion_refPoint(bodyId)

def set_body_motion_relative_time(bodyId, relTx, relTy, relTz, relRx, relRy, relRz):
    FM_set_body_motion_relative_time(bodyId, relTx, relTy, relTz, relRx, relRy, relRz)

def get_body_motion_relative_time(bodyId):
    return FM_get_body_motion_relative_time(bodyId)

def get_body_motion_reference_point(bodyId):
    return FM_get_body_motion_refPoint(bodyId)

def set_body_motion_refPoint(bodyId,x,y,z):
    FM_set_body_motion_refPoint(bodyId,x,y,z)

def set_body_motion_reference_point(bodyId,x,y,z):
    FM_set_body_motion_refPoint(bodyId,x,y,z)

def get_domain_grid_motion(domain):
    return FM_get_domain_grid_motion(domain)

def get_domain_grid_motion2(domain):
    flags = FM_get_domain_grid_motion(domain)
    new_flags = []

    for deform in flags:
        new_deform = deform

        if deform == 'Weighted_deform':
            new_deform = 'Weighted_deformation'

        new_flags.append(new_deform)

    return tuple(new_flags)

def set_domain_grid_motion(domain, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_domain_grid_motion(domain, Tx, Ty, Tz, Rx, Ry, Rz)

def get_body_inertia_spec(bodyId):
    return FM_get_body_inertia_spec(bodyId)

def set_body_inertia_spec(bodyId, consider):
    FM_set_body_inertia_spec(bodyId, consider)

def get_solvedMotion_geometry(bodyId):
    return FM_get_solvedMotion_fullGeometry(bodyId)

def get_solved_motion_geometry(bodyId):
    return FM_get_solvedMotion_fullGeometry(bodyId)

def set_solvedMotion_geometry(bodyId,geometry):
    FM_set_solvedMotion_fullGeometry(bodyId,geometry)

def set_solved_motion_geometry(bodyId,geometry):
    FM_set_solvedMotion_fullGeometry(bodyId,geometry)

def get_solvedMotion_gravityCenter(bodyId):
    return FM_get_solvedMotion_gravityCenter(bodyId)

def get_solved_motion_gravity_center(bodyId):
    return FM_get_solvedMotion_gravityCenter(bodyId)

def set_solvedMotion_gravityCenter(bodyId,x,y,z):
    FM_set_solvedMotion_gravityCenter(bodyId,x,y,z)

def set_solved_motion_gravity_center(bodyId,x,y,z):
    FM_set_solvedMotion_gravityCenter(bodyId,x,y,z)

# Cardan angles

def get_solved_motion_cardan_angle(bodyId):
    roll, pitch, yaw = FM_get_body_cardan_angles(bodyId)
    flag = FM_get_cardan_angles_activation()
    return flag, yaw, pitch, roll

def set_solved_motion_cardan_angle(flag, body, yaw_Rz0, pitch_Ry1, roll_Rx2):
    FM_set_body_cardan_angles(body, roll_Rx2, pitch_Ry1, yaw_Rz0)
    FM_set_cardan_angles_activation(flag)

def _get_effective_body_cardan_angles():
    return FM_get_effective_body_cardan_angles()

# These two are kept for backward compatibility

def get_solvedMotion_cardanAngle(bodyId):
    flag, yaw, pitch, roll = get_solved_motion_cardan_angle(bodyId)

    if flag:
        value = 'YES'
    else:
        value = 'NO'

    return value, yaw, pitch, roll

def set_solvedMotion_cardanAngle(ans, body, yaw_Rz0, pitch_Ry1, roll_Rx2):
    flag = (ans == 'YES')
    set_solved_motion_cardan_angle(flag, body, yaw_Rz0, pitch_Ry1, roll_Rx2)

def get_solvedMotion_mass(bodyId):
    return FM_get_solvedMotion_mass(bodyId)

def get_solved_motion_mass(bodyId):
    return FM_get_solvedMotion_mass(bodyId)

def set_solvedMotion_mass(bodyId,m):
    FM_set_solvedMotion_mass(bodyId,m)

def set_solved_motion_mass(bodyId,m):
    FM_set_solvedMotion_mass(bodyId,m)

def get_solvedMotion_inertiaMatrix(bodyId):
    return FM_get_solvedMotion_inertiaMatrix(bodyId)

def get_solved_motion_inertia_matrix(bodyId):
    return FM_get_solvedMotion_inertiaMatrix(bodyId)

def set_solvedMotion_inertiaMatrix(bodyId,im0,im1,im2,im3,im4,im5):
    FM_set_solvedMotion_inertiaMatrix(bodyId,im0,im1,im2,im3,im4,im5)

def set_solved_motion_inertia_matrix(bodyId,im0,im1,im2,im3,im4,im5):
    FM_set_solvedMotion_inertiaMatrix(bodyId,im0,im1,im2,im3,im4,im5)

def get_solvedMotion_addedMassCoef(bodyId):
    return FM_get_added_mass_coeff_value(bodyId)

def get_solved_motion_added_mass_coefficient(bodyId):
    return FM_get_added_mass_coeff_value(bodyId)

def set_solvedMotion_addedMassCoef(bodyId,amc0,amc1,amc2,amc3,amc4,amc5):
    FM_set_added_mass_coeff_value(bodyId,amc0,amc1,amc2,amc3,amc4,amc5)

def set_solved_motion_added_mass_coefficient(bodyId,amc0,amc1,amc2,amc3,amc4,amc5):
    FM_set_added_mass_coeff_value(bodyId,amc0,amc1,amc2,amc3,amc4,amc5)

def get_solvedMotion_dampingCoef(bodyId):
    return FM_get_solvedMotion_dampingCoef(bodyId)

def get_solved_motion_damping_coefficient(bodyId):
    return FM_get_solvedMotion_dampingCoef(bodyId)

def set_solvedMotion_dampingCoef(bodyId,coef):
    FM_set_solvedMotion_dampingCoef(bodyId,coef)

def set_solved_motion_damping_coefficient(bodyId,coef):
    FM_set_solvedMotion_dampingCoef(bodyId,coef)

def get_solvedMotion_initialVelocity(bodyId):
    return FM_get_solvedMotion_initialVelocity(bodyId)

def get_solved_motion_initial_velocity(bodyId):
    return FM_get_solvedMotion_initialVelocity(bodyId)

def set_solvedMotion_initialVelocity(bodyId,velX,velY,velZ,rotVelX,rotVelY,rotVelZ):
    FM_set_solvedMotion_initialVelocity(bodyId,velX,velY,velZ,rotVelX,rotVelY,rotVelZ)

def set_solved_motion_initial_velocity(bodyId,velX,velY,velZ,rotVelX,rotVelY,rotVelZ):
    FM_set_solvedMotion_initialVelocity(bodyId,velX,velY,velZ,rotVelX,rotVelY,rotVelZ)

def get_solvedMotion_initialDisp(bodyId):
    return FM_get_solvedMotion_initialDisp(bodyId)

def get_solved_motion_initial_displacement(bodyId):
    return FM_get_solvedMotion_initialDisp(bodyId)

def set_solvedMotion_initialDisp(bodyId,transX,transY,transZ,rotationX,rotationY,rotationZ):
    FM_set_solvedMotion_initialDisp(bodyId,transX,transY,transZ,rotationX,rotationY,rotationZ)

def set_solved_motion_initial_displacement(bodyId,transX,transY,transZ,rotationX,rotationY,rotationZ):
    FM_set_solvedMotion_initialDisp(bodyId,transX,transY,transZ,rotationX,rotationY,rotationZ)

def get_solvedMotion_wrenchParams(bodyId):
    return FM_get_solvedMotion_wrenchParams(bodyId)

def get_solved_motion_wrench_parameters(bodyId):
    return FM_get_solvedMotion_wrenchParams(bodyId)

def set_solvedMotion_wrenchParams(bodyId,toggle,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,pointX,pointY,pointZ):
    FM_set_solvedMotion_wrenchParams(bodyId,toggle,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,pointX,pointY,pointZ)

def set_solved_motion_wrench_parameters(bodyId,toggle,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,pointX,pointY,pointZ):
    FM_set_solvedMotion_wrenchParams(bodyId,toggle,forceX,forceY,forceZ,torqueX,torqueY,torqueZ,pointX,pointY,pointZ)

def get_solved_motion_wrench_follower_force(bodyId):
    return FM_get_solved_motion_wrench_follower_force(bodyId)

def set_solved_motion_wrench_follower_force(bodyId, follow):
    FM_set_solved_motion_wrench_follower_force(bodyId, follow)

def get_solvedMotion_propellerParams(bodyId):
    return FM_get_solvedMotion_propellerParams(bodyId)

def get_solved_motion_propeller_parameters(bodyId):
    return FM_get_solvedMotion_propellerParams(bodyId)

def set_solvedMotion_propellerParams(bodyId,toggle,dirX,dirY,dirZ,pointX,pointY,pointZ):
    FM_set_solvedMotion_propellerParams(bodyId,toggle,dirX,dirY,dirZ,pointX,pointY,pointZ)

def set_solved_motion_propeller_parameters(bodyId,toggle,dirX,dirY,dirZ,pointX,pointY,pointZ):
    FM_set_solvedMotion_propellerParams(bodyId,toggle,dirX,dirY,dirZ,pointX,pointY,pointZ)

def get_solved_motion_propeller_follower_force(bodyId):
    return FM_get_solved_motion_propeller_follower_force(bodyId)

def set_solved_motion_propeller_follower_force(bodyId, follow):
    FM_set_solved_motion_propeller_follower_force(bodyId, follow)

def get_solved_motion_spring_wrench(bodyID):
    return FM_get_solved_motion_spring_wrench(bodyID)

def set_solved_motion_spring_wrench(bodyID, enable, x, y, z, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_solved_motion_spring_wrench(bodyID, enable, x, y, z, Tx, Ty, Tz, Rx, Ry, Rz)

def get_solved_motion_damping_wrench(bodyID):
    return FM_get_solved_motion_damping_wrench(bodyID)

def set_solved_motion_damping_wrench(bodyID, enable, x, y, z, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_solved_motion_damping_wrench(bodyID, enable, x, y, z, Tx, Ty, Tz, Rx, Ry, Rz)

def get_solved_motion_link_wrench(bodyID):
    return FM_get_solved_motion_link_wrench(bodyID)

def set_solved_motion_link_wrench(bodyID, enable, torque, spring_stiff, damping):
    FM_set_solved_motion_link_wrench(bodyID, enable, torque, spring_stiff, damping)

def get_body_connection(bodyId):
    return FM_get_body_connection(bodyId)

def get_body_connection2(bodyId):
    connId, connType, p, d = FM_get_body_connection(bodyId)
    return connId, connType, p[0], p[1], p[2], d[0], d[1], d[2]

def set_body_connection(bodyId,connectionId,connectionType,pointX,pointY,pointZ,normalX,normalY,normalZ):
    FM_set_body_connection(bodyId,connectionId,connectionType,pointX,pointY,pointZ,normalX,normalY,normalZ)

def get_body_kinematics(body):
    return FM_get_body_kinematics(body)

def set_body_kinematics(body,type):
    FM_set_body_kinematics(body,type)

def domain_motion_enabled(domain, check_imposed_motion=1):
    return FM_domain_motion_enabled(domain, check_imposed_motion)

def enable_domain_motion(domain):
    print 'FM.enable_domain_motion is deprecated. Use FM.update_body_list to automatically create virtual bodies.'
    return 0, -1 - domain

def disable_domain_motion(domain):
    print 'FM.disable_domain_motion is deprecated. Use FM.update_body_list to automatically create virtual bodies.'

#
# Evaluation of added mass coefficient
#

def get_added_mass_coeff_type(bodyID):
    return FM_get_added_mass_coeff_type(bodyID)

def get_added_mass_coeff_value(bodyID):
    return FM_get_added_mass_coeff_value(bodyID)

def get_added_mass_coeff_period(bodyID):
    return FM_get_added_mass_coeff_period(bodyID)

def set_added_mass_coeff_type(bodyID, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_added_mass_coeff_type(bodyID, Tx, Ty, Tz, Rx, Ry, Rz)

def set_added_mass_coeff_value(bodyID, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_added_mass_coeff_value(bodyID, Tx, Ty, Tz, Rx, Ry, Rz)

def set_added_mass_coeff_period(bodyID, Tx, Ty, Tz, Rx, Ry, Rz):
    FM_set_added_mass_coeff_period(bodyID, Tx, Ty, Tz, Rx, Ry, Rz)

def get_added_mass_coeff_linking(bodyID):
    return FM_get_added_mass_coeff_linking(bodyID)

# account body links when computing AMC
def set_added_mass_coeff_linking(bodyID, account):
    FM_set_added_mass_coeff_linking(bodyID, account)

#--------------------------------------------------------------------------------------------#
#------------------------------ Initial solution commands -----------------------------------#
#--------------------------------------------------------------------------------------------#

def get_initial_solution_turb_parameters():
    return FM_get_initial_solution_isis_parameters()

def set_initial_solution_turb_parameters(turb_level,turb_val,turb_length):
    FM_set_initial_solution_isis_parameters(turb_level,turb_val,turb_length)

def get_initial_turbulence():
    turbLevel = get_parameter("initialTurbLevel_",0)
    turbFreq = get_parameter("initialTurbFreq_",0)
    return turbLevel,turbFreq

def set_initial_turbulence(turbLevel,turbFreq):
    FM_set_initial_turbulence(turbLevel,turbFreq)

def get_initial_interface_position():
    return get_parameter("multiPointInter_",0)

def set_initial_interface_position(mulpos):
    FM_set_initial_mulpos(mulpos)

def get_initial_velocity():
    vel0 = get_parameter("initVelocity_",0)
    vel1 = get_parameter("initVelocity_",1)
    vel2 = get_parameter("initVelocity_",2)
    return vel0,vel1,vel2

def set_initial_velocity(vel0,vel1,vel2):
    FM_set_initial_velocity(vel0,vel1,vel2)

def get_convergence_accu():
    ans = "NO"

    if FM_get_convergence_accu():
        ans = "YES"

    return ans

def set_convergence_accu(ans):
    import_hist = (ans == "YES")
    FM_set_convergence_accu(import_hist)

def classic_turbulence_init():
    return FM_classic_turbulence_init()

def turbulence_level_init(Ls, Tu):
    return FM_turbulence_level_init(Ls, Tu)

#--------------------------------------------------------------------------------------------#
#----------------------------- Computational control ----------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_probe_on_walls_para():
#    FM_get_probe_on_walls_para()
    flag = get_parameter("ProbeOnWallsForces_",0)
    freq = get_parameter("ProbeOnWallsForcesFreq_",0)
    start = get_parameter("ProbeOnWallsForcesStart_",0)
    end = get_parameter("ProbeOnWallsForcesEnd_",0)
    flowQuantOnly = get_parameter("ProbeOnWallsForcesFlowQuantOnly_",0)
    return flag,freq,start,end,flowQuantOnly

def set_probe_on_walls_para(flag,freq,start,end,flowQuantOnly):
#    FM_set_probe_on_walls_para(flag,freq,start,end,flowQuantOnly)
    set_simple_string_parameter("ProbeOnWallsForces_",flag)
    set_simple_int_parameter("ProbeOnWallsForcesFreq_",freq)
    set_simple_real_parameter("ProbeOnWallsForcesStart_",start)
    set_simple_real_parameter("ProbeOnWallsForcesEnd_",end)
    set_simple_string_parameter("ProbeOnWallsForcesFlowQuantOnly_",flowQuantOnly)

def get_timesplit_maxstep():
    return FM_get_timesplit_maxstep()

def set_timesplit_maxstep(steps):
    FM_set_timesplit_maxstep(steps)

def get_timesplit_minstep():
    return FM_get_timesplit_minstep()

def set_timesplit_minstep(steps):
    FM_set_timesplit_minstep(steps)

def get_timesplit_courant_number():
    return get_parameter("splitTargetValue_",0)

def set_timesplit_courant_number(ans):
    FM_set_timesplit_courant_number(ans)

def get_expert_cv():
    return FM_get_expert_cv()

def set_expert_cv(iTurbscheme):
    FM_set_expert_cv(iTurbscheme)

#--------------------------------------------------------------------------------------------#
#------------------------------ Numerical model parameters ----------------------------------#
#--------------------------------------------------------------------------------------------#

def get_turb_scheme():
    return FM_get_turb_scheme()

def set_turb_scheme(iTurbscheme,upc_turb):
    FM_set_turb_scheme(iTurbscheme,upc_turb)

def get_momt_scheme():
    return FM_get_momt_scheme()

def set_momt_scheme(iTurbscheme,upc_momt):
    FM_set_momt_scheme(iTurbscheme,upc_momt)

def get_transition_scheme():
    return FM_get_trans_scheme()

def set_transition_scheme(scheme, upwindc):
    FM_set_trans_scheme(scheme, upwindc)

def get_multi_scheme():
    return FM_get_multi_scheme()

def set_multi_scheme(iTurbscheme):
    FM_set_multi_scheme(iTurbscheme)

def get_cavitation_scheme():
    return FM_get_cavitation_scheme()

def set_cavitation_scheme(iTurbscheme):
    FM_set_cavitation_scheme(iTurbscheme)

def get_urex_velocity():
    return FM_get_urex_velocity()

def set_urex_velocity(x,y,z):
    FM_set_urex_velocity(x,y,z)

def get_urex_params():
    return FM_get_urex_params()

def set_urex_params(pressure,velocity,correction):
    FM_set_urex_params(pressure,velocity,correction)

def get_urex_pressure():
    return get_parameter("underPres_",0)

def get_urex_velocity_flux():
    return get_parameter("underVelFlux_",0)

def get_urex_correction():
    return get_parameter("underCorrect_",0)

def set_urex_pressure(pressure):
    dummy,velocity,correction = FM_get_urex_params()
    FM_set_urex_params(pressure,velocity,correction)

def set_urex_velocity_flux(velocity):
    pressure,dummy,correction = FM_get_urex_params()
    FM_set_urex_params(pressure,velocity,correction)

def set_urex_correction(correction):
    pressure,velocity,dummy = FM_get_urex_params()
    FM_set_urex_params(pressure,velocity,correction)

def get_urex_turb_params():
    return FM_get_urex_turb_params()

def set_urex_turb_params(kinetic_energy,frequency,diss,viscosity,mass_fraction):
    FM_set_urex_turb_params(kinetic_energy,frequency,diss,viscosity,mass_fraction)

def get_urex_cavitation():
    return FM_get_urex_cavitation()

def set_urex_cavitation(value):
    FM_set_urex_cavitation(value)

def get_urex_intermittency():
    return FM_get_urex_intermittency()

def set_urex_intermittency(urex):
    FM_set_urex_intermittency(urex)

def get_projection_method():
    value = get_parameter("UseProjectionOnSurface_",0)
    flag = 0
    if value == "YES":
        flag = 1
    return flag,get_parameter("ProjectionFile_",0)

def set_projection_method(flag,file):
    value = "NO"
    if flag == 1:
        value = "YES"
    set_simple_string_parameter("UseProjectionOnSurface_",value)
    set_simple_string_parameter("UseCustomProjectionFile_",value)
    if value == "NO" and file != "-":
        print "Warning: reset projection file " + str(file)
        file = "-"
    set_simple_string_parameter("ProjectionFile_",file)

#--------------------------------------------------------------------------------------------#
#------------------------------ Output parameters -------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_volume_probe(number):
    return FM_get_volume_probe(number)

def set_volume_probe(number, enable):
    FM_set_volume_probe(number, enable)
    _switch_probes_mode('volume')

def get_probe_interval():
    it, sec, units = FM_get_probing_interval()
    value = 0

    if units == "timesteps":
        value = it
    elif units == "seconds":
        value = sec

    return value, units

def _set_probing_interval(value, units):
    it, sec, uts = FM_get_probing_interval()

    if units == "seconds":
        sec = value
    elif units == "timesteps":
        it = value

    FM_set_probing_interval(it, sec, units)

def set_probe_interval(value,units):
    # _set_probing_interval(value, units) # is already inside set_volume.../set_surface...
    set_volume_probe_interval(value,units)
    set_surface_probe_interval(value,units)

def get_volume_probe_interval():
    return get_probe_interval()


def set_volume_probe_interval(value,units):
    _set_probing_interval(value, units)

def get_surface_probe_interval():
    return get_probe_interval()

def set_surface_probe_interval(value,units):
    _set_probing_interval(value, units)
    if units == "seconds":
        val1 = 0
        val2 = value
    else:
        val1 = value
        val2 = 0
    freq1 = get_parameter("ProbeWallForcesFreq_",0)
    freq2 = get_parameter("ProbeWallForcesFreq_",1)
    if (freq1 != 0 or freq2 != 0):
        FM_set_custom_parameter("ProbeWallForcesFreq_","REAL","*** PROBE WALL FORCES: FREQUENCY",1,0,2,val1,val2)
    if (int(FM_get_parameter("ProbeFreeSurfaceFile_",0)[0]) == 1 and FM_get_parameter("ProbeFreeSurfaceFile_",0)[1] != '-'):
        FM_set_custom_parameter("ProbeFreeSurface_","REAL","*** PROBE WATER SURFACE: FREQUENCY",1,0,2,val1,val2)
    if (int(FM_get_parameter("ProbeWallFile_",0)[0]) == 1 and FM_get_parameter("ProbeWallFile_",0)[1] != '-'):
        FM_set_custom_parameter("ProbeWallFreq_","REAL","*** PROBE WALL: FREQUENCY",1,0,2,val1,val2)
    n_max = 99
    i = 0
    while i < n_max:
        file = 'ProbeIsoSurfaceFile_' + str(i+1)
        freq = 'ProbeIsoSurfaceFreq_' + str(i+1)
        res = FM_get_parameter(file,0)
        if int(res[0]) == 1 and res[1] != '-':
            FM_set_custom_parameter(freq,"REAL","*** PROBE ISOSURFACE " + str(i+1) + ": FREQUENCY",1,0,2,val1,val2)
        else:
            break
        i = i + 1

def update_surface_probe_mode(mode):
    param = FM_get_parameter("ProbeFreeSurfaceFile_",0)
    if (param[0] == 1 and param[1] != '-'):
        FM_set_custom_parameter("ProbeFreeSurfaceFile_","STRING","*** PROBE WATER SURFACE: FILE",mode,0,1,param[1])
        param1 = FM_get_parameter("ProbeFreeSurface_",0)
        param2 = FM_get_parameter("ProbeFreeSurface_",1)
        if param1[0] == 1 and param2[0] == 1:
            FM_set_custom_parameter("ProbeFreeSurface_","REAL","*** PROBE WATER SURFACE: FREQUENCY",mode,0,2,param1[1],param2[1])
    param = FM_get_parameter("ProbeWallFile_",0)
    if (param[0] == 1 and param[1] != '-'):
        FM_set_custom_parameter("ProbeWallFile_","STRING","*** PROBE WALL: FILE",mode,0,1,param[1])
        n_max = 9
        i = 0
        while i < n_max:
            quantity_name = 'ProbeWallQuantity_' + str(i+1)
            quantity = get_parameter(quantity_name,0)
            if quantity == '-':
                break
            else:
                isis = '*** PROBE WALL ' + str(i+1) + ': PROBE VARIABLE'
                FM_set_custom_parameter(quantity_name,"STRING",isis,mode,0,1,quantity)
            i = i + 1
        param1 = FM_get_parameter("ProbeWallFreq_",0)
        param2 = FM_get_parameter("ProbeWallFreq_",1)
        if param1[0] == 1 and param2[0] == 1:
            FM_set_custom_parameter("ProbeWallFreq_","REAL","*** PROBE WALL: FREQUENCY",mode,0,2,param1[1],param2[1])
    n_max = 99
    i = 0
    while i < n_max:
        file = 'ProbeIsoSurfaceFile_' + str(i+1)
        param = FM_get_parameter(file,0)
        if param[0] == 1 and param[1] != '-':
            isis = '*** PROBE ISOSURFACE ' + str(i+1) + ': FILE'
            FM_set_custom_parameter(file,"STRING",isis,mode,0,1,param[1])
            variable = 'ProbeIsoSurfaceVariable_' + str(i+1)
            isis = '*** PROBE ISOSURFACE ' + str(i+1) + ': ISO VARIABLE'
            iso_variable = get_parameter(variable,0)
            FM_set_custom_parameter(variable,"STRING",isis,mode,0,1,iso_variable)
            value = 'ProbeIsoSurfaceValue_' + str(i+1)
            isis = '*** PROBE ISOSURFACE ' + str(i+1) + ': ISO VALUE'
            iso_value = get_parameter(value,0)
            FM_set_custom_parameter(value,"REAL",isis,mode,0,1,iso_value)
            quantity = 'ProbeIsoSurfaceQuantity_' + str(i+1)
            isis = '*** PROBE ISOSURFACE ' + str(i+1) + ': PROBE VARIABLE'
            probe_variable = get_parameter(quantity,0)
            FM_set_custom_parameter(quantity,"STRING",isis,mode,0,1,probe_variable)
            isis = '*** PROBE ISOSURFACE ' + str(i+1) + ': FREQUENCY'
            var = "ProbeIsoSurfaceFreq_" + str(i+1)
            param1 = FM_get_parameter(var,0)
            param2 = FM_get_parameter(var,1)
            if param1[0] == 1 and param2[0] == 1:
                FM_set_custom_parameter(var,"REAL",isis,mode,0,2,param1[1],param2[1])
        i = i + 1

def get_probe_wall_forces_file():
    freq1 = get_parameter("ProbeWallForcesFreq_",0)
    freq2 = get_parameter("ProbeWallForcesFreq_",1)
    if (freq1 != 0 or freq2 != 0):
        return get_parameter("ProbeWallForcesFile_",0)
    else:
        return '-'

def set_probe_wall_forces_file(name):
    FM_set_custom_parameter("ProbeWallForcesFile_","STRING","*** PROBE WALL FORCES: FILE",1,0,1,name)

def get_surface_probe_wall_forces():
    freq1 = get_parameter("ProbeWallForcesFreq_",0)
    freq2 = get_parameter("ProbeWallForcesFreq_",1)
    if (freq1 != 0 or freq2 != 0):
        return get_parameter("ProbeWallForcesFile_",0)
    else:
        return '-'

def set_surface_probe_wall_forces(name):
    # Wall surface probe has always a definite file name. Actual state is defined by frequencies.
    #ext = '.cpr'
    #if int(FM_get_parameter("nodesFile_",0)[0]) == 1:
    #    dummy, ext = os.path.splitext(FM_get_parameter("nodesFile_",0)[1])
    #name_forever = 'wall_data' + str(ext)
    FM_set_custom_parameter("ProbeWallForcesFile_","STRING","*** PROBE WALL FORCES: FILE",1,0,1,name)
    if name == '-':
        FM_set_custom_parameter("ProbeWallForcesFreq_","REAL","*** PROBE WALL FORCES: FREQUENCY",1,0,2,0,0)
    else:
        value,units = get_probe_interval()
        if units == "seconds":
            val1 = 0
            val2 = value
        else:
            val1 = value
            val2 = 0
        FM_set_custom_parameter("ProbeWallForcesFreq_","REAL","*** PROBE WALL FORCES: FREQUENCY",1,0,2,val1,val2)
    _switch_probes_mode('surface')


def get_surface_probe_free():
    return get_parameter("ProbeFreeSurfaceFile_",0)

def set_surface_probe_free(name):
    if name == '-':
        FM_set_custom_parameter("ProbeFreeSurfaceFile_","STRING","*** PROBE WATER SURFACE: FILE",0,0,1,name)
        FM_set_custom_parameter("ProbeFreeSurface_","REAL","*** PROBE WATER SURFACE: FREQUENCY",0,0,2,0,0)
    else:
        FM_set_custom_parameter("ProbeFreeSurfaceFile_","STRING","*** PROBE WATER SURFACE: FILE",1,0,1,name)
        value,units = get_probe_interval()
        val1 = val2 = 0
        if units == "seconds":
            val1 = 0
            val2 = value
        else:
            val1 = value
            val2 = 0
        FM_set_custom_parameter("ProbeFreeSurface_","REAL","*** PROBE WATER SURFACE: FREQUENCY",1,0,2,val1,val2)
    _switch_probes_mode('surface')


def get_surface_probe_wall():
    n_max = 9
    i = 0
    quantities = []
    while i < n_max:
        quantity_name = 'ProbeWallQuantity_' + str(i+1)
        quantity = get_parameter(quantity_name,0)
        if quantity == '-':
            break
        else:
            quantities.append(quantity)
        i = i + 1
    name = get_parameter("ProbeWallFile_",0)
    return name, i, quantities

def set_surface_probe_wall(name, nQuantities, *quantities):
    i = 0
    n_max = 9
    while i < n_max:
        quantity_name = 'ProbeWallQuantity_' + str(i+1)
        isis = '*** PROBE WALL ' + str(i+1) + ': PROBE VARIABLE'
        if i < nQuantities:
            quantity = str(quantities[i]).strip().upper()
            FM_set_custom_parameter(quantity_name,"STRING",isis,1,0,1,quantity)
        else:
            FM_set_custom_parameter(quantity_name,"STRING",isis,0,0,1,'-')
        i = i + 1
    if name == '-':
        FM_set_custom_parameter("ProbeWallFile_","STRING","*** PROBE WALL: FILE",0,0,1,name)
        FM_set_custom_parameter("ProbeWallFreq_","REAL","*** PROBE WALL: FREQUENCY",0,0,2,0,0)
    else:
        FM_set_custom_parameter("ProbeWallFile_","STRING","*** PROBE WALL: FILE",1,0,1,name)
        val1 = val2 = 0
        value,units = get_probe_interval()
        if units == "seconds":
            val1 = 0
            val2 = value
        else:
            val1 = value
            val2 = 0
        FM_set_custom_parameter("ProbeWallFreq_","REAL","*** PROBE WALL: FREQUENCY",1,0,2,val1,val2)
    _switch_probes_mode('surface')

def _switch_probes_mode(mode):
    if mode == 'surface':
        FM_set_custom_parameter("ProbeType_","STRING","*** PROBE TYPE",0,0,1,"SURFACE")
        update_surface_probe_mode(1)
    elif mode == 'volume':
        FM_set_custom_parameter("ProbeType_","STRING","*** PROBE TYPE",0,0,1,"VOLUME")
        update_surface_probe_mode(0)
    else:
        print 'WARNING: unknown mode "' + str(mode) + '" for _switch_probes_mode'

def get_surface_probe_iso(id):
    file = 'ProbeIsoSurfaceFile_' + str(id)
    variable = 'ProbeIsoSurfaceVariable_' + str(id)
    value = 'ProbeIsoSurfaceValue_' + str(id)
    quantity = 'ProbeIsoSurfaceQuantity_' + str(id)
    return get_parameter(file,0), get_parameter(variable,0), get_parameter(value,0), get_parameter(quantity,0)

def set_surface_probe_iso(id, file_name, iso_variable, iso_value, probe_variable):
    mode = 1
    if file_name == '-':
        mode = 0
    probe_file = 'ProbeIsoSurfaceFile_' + str(id)
    isis = '*** PROBE ISOSURFACE ' + str(id) + ': FILE'
    FM_set_custom_parameter(probe_file,"STRING",isis,mode,0,1,file_name)
    variable = 'ProbeIsoSurfaceVariable_' + str(id)
    isis = '*** PROBE ISOSURFACE ' + str(id) + ': ISO VARIABLE'
    FM_set_custom_parameter(variable,"STRING",isis,mode,0,1,str(iso_variable).strip().upper())
    value = 'ProbeIsoSurfaceValue_' + str(id)
    isis = '*** PROBE ISOSURFACE ' + str(id) + ': ISO VALUE'
    FM_set_custom_parameter(value,"REAL",isis,mode,0,1,iso_value)
    quantity = 'ProbeIsoSurfaceQuantity_' + str(id)
    isis = '*** PROBE ISOSURFACE ' + str(id) + ': PROBE VARIABLE'
    FM_set_custom_parameter(quantity,"STRING",isis,mode,0,1,str(probe_variable).strip().upper())
    isis = '*** PROBE ISOSURFACE ' + str(id) + ': FREQUENCY'
    if file_name == '-':
        FM_set_custom_parameter("ProbeIsoSurfaceFreq_" + str(id),"REAL",isis,0,0,2,0,0)
    else:
        val1 = val2 = 0
        value,units = get_probe_interval()
        if units == "seconds":
            val1 = 0
            val2 = value
        else:
            val1 = value
            val2 = 0
        FM_set_custom_parameter("ProbeIsoSurfaceFreq_" + str(id),"REAL",isis,1,0,2,val1,val2)
    _switch_probes_mode('surface')

def get_surface_probe_cut(id):
    return FM_get_surface_probe_cut(id)

def get_surface_probe_cut_plane(id):
    full = get_surface_probe_cut(id)
    file = full[0]
    variable = full[1]
    body = full[2]
    x = full[3]
    y = full[4]
    z = full[5]
    nx = full[6]
    ny = full[7]
    nz = full[8]
    return file, variable, body, x, y, z, nx, ny, nz

def set_surface_probe_cut(id, file_name, quantity, body_id, origin_x, origin_y, origin_z, normal_x, normal_y, normal_z, type, dim1, dim2):
    FM_set_surface_probe_cut(id, file_name, quantity, body_id, origin_x, origin_y, origin_z, normal_x, normal_y, normal_z, type, dim1, dim2)
    _switch_probes_mode('surface')

def set_surface_probe_cut_plane(id, file_name, quantity, body_id, origin_x, origin_y, origin_z, normal_x, normal_y, normal_z):
    set_surface_probe_cut(id, file_name, quantity, body_id, origin_x, origin_y, origin_z, normal_x, normal_y, normal_z, "PLANE", 1.0, 1.0)

def get_point_probe(id):
    var_desc = FM_get_parameter('ProbePointVar_' + str(id), 0)
    var = '-'

    if var_desc[0] != 0:
        var = var_desc[1]

    body_desc = FM_get_parameter('ProbePointBody_' + str(id), 0)
    body = 0

    if body_desc[0] != 0:
        body = body_desc[1]

    origin_var = 'ProbePointOrigin_' + str(id)
    p = [0.0, 0.0, 0.0]

    for i in range(0, 3):
        desc = FM_get_parameter(origin_var, i)

        if desc[0] != 0:
            p[i] = desc[1]

    return var, body, p[0], p[1], p[2]

def set_point_probe(id, quantity, body_id, origin_x, origin_y, origin_z):
    mode = 1
    if quantity == '-':
        mode = 0
    variable = 'ProbePointVar_' + str(id)
    isis = '*** PROBE POINT ' + str(id) + ': PROBE VARIABLE'
    FM_set_custom_parameter(variable,"STRING",isis,mode,0,1,str(quantity).strip().upper())
    body = 'ProbePointBody_' + str(id)
    isis = '*** PROBE POINT ' + str(id) + ': BODY INDEX'
    FM_set_custom_parameter(body,"INTEGER",isis,mode,0,1,body_id)
    origin = 'ProbePointOrigin_' + str(id)
    isis = '*** PROBE POINT ' + str(id) + ': POSITION'
    FM_set_custom_parameter(origin,"REAL",isis,mode,0,3,origin_x,origin_y,origin_z)

    # update PROBE POINT: FILE chain availability
    id = 1

    while id <= 99 and get_point_probe(id)[0] == '-':
        id += 1

    mode = 0 # disable

    if id <= 99:
        # found an active probe -> enable
        mode = 1

    FM_set_custom_parameter("ProbePointFile_", "STRING", "*** PROBE POINT: FILE", mode, 0, 1, "points_probe.dat")
#--------------------------------------------------------------------------------------------#
#---------------------------------- Actuator disk -------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_actuator_disk():
    value = FM_get_actuator_disk_active_flag()
    if value == "YES":
        return 1
    else:
        return 0

def set_actuator_disk(flag):
    value = "NO"
    if flag != 0:
        value = "YES"
    FM_set_actuator_disk_active_flag(value)

def get_actuator_disk_tangential_force():
    value = FM_get_actuator_disk_tangential_force_flag()
    if value == "YES":
        return 1
    else:
        return 0

def set_actuator_disk_tangential_force(flag):
    value = "NO"
    if flag != 0:
        value = "YES"
    FM_set_actuator_disk_tangential_force_flag(value)

NO_SELF_UPDATE  = 0
BODY_DRAG       = 1
OPEN_WATER_DATA = 2
PROPELLER_CODE  = 3

def get_actuator_disk_self_update():
    return FM_get_actuator_disk_self_update_flag()

def set_actuator_disk_self_update(value):
    FM_set_actuator_disk_self_update_flag(value)

def get_actuator_disk_update_frequency():
    return FM_get_actuator_disk_update_frequency()

def set_actuator_disk_update_frequency(value):
    FM_set_actuator_disk_update_frequency(value)

def get_actuator_disk_force_distribution():
    dist = FM_get_actuator_disk_force_distribution()
    update_type = get_actuator_disk_self_update()

    if update_type == PROPELLER_CODE:
        dist = "PROPELLER CODE"

    return dist

def set_actuator_disk_force_distribution(input_value):
    value = input_value.upper()

    if value == "PROPELLER CODE":
        set_actuator_disk_self_update(PROPELLER_CODE)

    FM_set_actuator_disk_force_distribution(value)

def get_actuator_disk_open_water_file(disk_id):
    return FM_get_actuator_disk_open_water_file(disk_id)

def set_actuator_disk_open_water_file(disk_id, filename):
    FM_set_actuator_disk_open_water_file(disk_id, filename)

def get_actuator_disk_list():
    ad_list = FM_get_actuator_disk_list()
    nDisks = len(ad_list)
    out_list = []
    i = 0
    while i < nDisks:
        out_list.append(ad_list[i][1])
        out_list.append(ad_list[i][0])
        i = i + 1
    return nDisks, out_list

def set_actuator_disk_list(nDisks,*list):
    globalList = []
    i = 0
    while i < nDisks:
        globalList.append(list[i][1])
        globalList.append(list[i][0])
        i = i + 1

    FM_set_actuator_disk_list(nDisks, globalList)

# more handy version of set_actuator_disk_list
def set_actuator_disks(names):
    n = len(names)
    lst = []

    for i, diskname in enumerate(names):
        lst.append(diskname)
        lst.append(i + 1)

    FM_set_actuator_disk_list(n, lst)

def _disk_id_exists(lst, disk_id):
    i = 0
    n = len(lst)

    while i < n and lst[i][0] != disk_id:
        i += 1

    return (i < n)

def _disk_name_exists(lst, disk_name):
    i = 0
    n = len(lst)

    while i < n and lst[i][1] != disk_name:
        i += 1

    return (i < n)

def _unique_disk_id(lst, start_id):
    i = start_id

    while _disk_id_exists(lst, i):
        i += 1

    return i

def _unique_disk_name(lst, template, start_num):
    i = start_num

    while _disk_name_exists(lst, template + str(i)):
        i += 1

    return template + str(i)

def set_number_of_actuator_disks(n):
    # do not rename existing disks!
    m, lst = get_actuator_disk_list()
    seplist = []
    i = 0
    lim = min(n, m)

    while i < 2 * lim:
        item = [lst[i], lst[i + 1]]
        i += 2
        seplist.append(item)

    while m < n:
        uid = _unique_disk_id(seplist, m + 1)
        name = _unique_disk_name(seplist, 'Disk_#', uid)
        seplist.append([uid, name])
        m += 1

    set_actuator_disk_list(len(seplist), *seplist)

def get_number_of_actuator_disks():
    n, list = get_actuator_disk_list()
    return n

def get_actuator_disk_name(disk_id):
    n, lst = get_actuator_disk_list()
    i = 0

    while i < 2 * n and lst[i] != disk_id:
        i += 2

    name = ""

    if i + 1 < 2 * n:
        name = lst[i + 1]
    else:
        print 'Error in FM.get_actuator_disk_name: no actuator disk index {}!'.format(disk_id)

    return name

def set_actuator_disk_name(disk_id, name):
    n, lst = get_actuator_disk_list()
    # find the disk
    i = 0

    while i < 2 * n and lst[i] != disk_id:
        i += 2

    if i + 1 < 2 * n:
        lst[i + 1] = name
    else:
        print 'Error in FM.set_actuator_disk_name: no actuator disk index {}!'.format(disk_id)

    # set the disk list
    seplist = []
    i = 0

    while i < 2 * n:
        item = [lst[i], lst[i + 1]]
        seplist.append(item)
        i += 2

    set_actuator_disk_list(len(seplist), *seplist)

def get_actuator_disk_properties(disk_id):
    return FM_get_actuator_disk_properties(disk_id)

def set_actuator_disk_properties(disk_id,thrust,torque,thickness,innerRadius,outerRadius,
    center_x,center_y,center_z,direction_x,direction_y,direction_z,bodyIndex,inflowPlaneDistance):
    FM_set_actuator_disk_properties(disk_id,thrust,torque,thickness,innerRadius,outerRadius,
        center_x,center_y,center_z,direction_x,direction_y,direction_z,bodyIndex,inflowPlaneDistance)

def get_disk_revolution_rate(disk_id):
    return FM_get_disk_revolution_rate(disk_id)

def set_disk_revolution_rate(disk_id, rate):
    FM_set_disk_revolution_rate(disk_id, rate)

def get_actuator_disk_ramp():
    return FM_get_actuator_disk_ramp()

def set_actuator_disk_ramp(ramp):
    FM_set_actuator_disk_ramp(ramp)

def get_actuator_disk_power(diskID):
    return FM_get_actuator_disk_power(diskID)

def set_actuator_disk_power(diskID, on, power):
    FM_set_actuator_disk_power(diskID, on, power)

def get_actuator_disk_max_power(diskID):
    return FM_get_actuator_disk_max_power(diskID)

def set_actuator_disk_max_power(diskID, on, power):
    FM_set_actuator_disk_max_power(diskID, on, power)

#--------------------------------------------------------------------------------------------#
#------------------------------------- Cavitation -------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_cavitation():
    value = get_parameter("Cavitation_",0)
    if value == "YES":
        return 1
    else:
        return 0

def set_cavitation(flag):
    value = "NO"
    if flag != 0:
        value = "YES"
    set_simple_string_parameter("Cavitation_",value)
    #set default parameters
    if flag == 1:
        if FM_get_parameter("CavitationVaporViscosity_",0)[0] == 0:
            FM_set_custom_parameter("CavitationVaporViscosity_","REAL","*** CAVITATION:VAPOR VISCOSITY",flag,0,1,1.e-5)
        if FM_get_parameter("CavitationVaporDensity_",0)[0] == 0:
            FM_set_custom_parameter("CavitationVaporDensity_","REAL","*** CAVITATION:VAPOR DENSITY",flag,0,1,1.0)
        if FM_get_parameter("CavitationReferencePressure_",0)[0] == 0:
            FM_set_custom_parameter("CavitationReferencePressure_","REAL","*** CAVITATION:REFERENCE PRESSURE",flag,0,1,0.0)
        if FM_get_parameter("CavitationRefVelocity_",0)[0] == 0:
            FM_set_custom_parameter("CavitationRefVelocity_","REAL","*** CAVITATION:REFERENCE VELOCITY",flag,0,1,1.0)
        if FM_get_parameter("CavitationRefLength_",0)[0] == 0:
            length = get_parameter("refLength_",0)
            FM_set_custom_parameter("CavitationRefLength_","REAL","*** CAVITATION:REFERENCE LENGTH",flag,0,1,length)
        if FM_get_parameter("CavitationSigmaState_",0)[0] == 0:
            FM_set_custom_parameter("CavitationSigmaState_","STRING","*** CAVITATION:USE_SIGMA",flag,0,1,"ON")
        if FM_get_parameter("CavitationSigmaInit_",0)[0] == 0:
            FM_set_custom_parameter("CavitationSigmaInit_","REAL","*** CAVITATION:INITIAL PARAMETER",flag,0,1,1.0e30)
        if FM_get_parameter("CavitationSigma_",0)[0] == 0:
            FM_set_custom_parameter("CavitationSigma_","REAL","*** CAVITATION:PARAMETER",flag,0,1,1.0e30)
        if FM_get_parameter("CavitationVaporPressure_",0)[0] == 0:
            FM_set_custom_parameter("CavitationVaporPressure_","REAL","*** CAVITATION:VAPOR PRESSURE",0,0,1,-1.0e30)
        if FM_get_parameter("CavitationVaporPressureInit_",0)[0] == 0:
            FM_set_custom_parameter("CavitationVaporPressureInit_","REAL","*** CAVITATION:INITIAL VAPOR PRESSURE",0,0,1,-1.0e30)
        if FM_get_parameter("Cavitation_DT_dec_",0)[0] == 0:
            FM_set_custom_parameter("Cavitation_DT_dec_","REAL","*** CAVITATION:SIGMA DECAY DURATION",flag,0,1,0.0)
        if FM_get_parameter("Cavitation_T_ac_",0)[0] == 0:
            FM_set_custom_parameter("Cavitation_T_ac_","REAL","*** CAVITATION:ACTIVATION TIME",flag,0,1,0.0)
        if FM_get_parameter("CavitationMerkleLiqProdCoef_",0)[0] == 0:
            FM_set_custom_parameter("CavitationMerkleLiqProdCoef_","REAL","*** CAVITATION:CPROD LIQ:MERKLE",0,0,1,100.0)
        if FM_get_parameter("CavitationMerkleLiqDestCoef_",0)[0] == 0:
            FM_set_custom_parameter("CavitationMerkleLiqDestCoef_","REAL","*** CAVITATION:CDEST LIQ:MERKLE",0,0,1,10.0)
        if FM_get_parameter("CavitationKunzLiqProdCoef_",0)[0] == 0:
            FM_set_custom_parameter("CavitationKunzLiqProdCoef_","REAL","*** CAVITATION:CPROD LIQ:KUNZ",0,0,1,455.0)
        if FM_get_parameter("CavitationKunzLiqDestCoef_",0)[0] == 0:
            FM_set_custom_parameter("CavitationKunzLiqDestCoef_","REAL","*** CAVITATION:CDEST LIQ:KUNZ",0,0,1,4100.0)
        if FM_get_parameter("CavitationSauerNucleiDensity_",0)[0] == 0:
            FM_set_custom_parameter("CavitationSauerNucleiDensity_","REAL","*** CAVITATION:NUCLEI DENSITY:SAUER",flag,0,1,1.0e8)

def get_cavitation_model():
    return get_parameter("CavitationModel_",0)

def set_cavitation_model(input_value):
    value = str(input_value).strip().upper()
    if (value != "SAUER" and value != "MERKLE" and value != "KUNZ"):
        raise ValueError, "Wrong cavitation model : " + value
    set_simple_string_parameter("CavitationModel_",value)

def get_cavitation_vapor_viscosity():
    return get_parameter("CavitationVaporViscosity_",0)

def set_cavitation_vapor_viscosity(value):
    set_simple_real_parameter("CavitationVaporViscosity_",value)

def get_cavitation_vapor_density():
    return get_parameter("CavitationVaporDensity_",0)

def set_cavitation_vapor_density(value):
    set_simple_real_parameter("CavitationVaporDensity_",value)

def get_cavitation_reference_pressure():
    return get_parameter("CavitationReferencePressure_",0)

def set_cavitation_reference_pressure(value):
    set_simple_real_parameter("CavitationReferencePressure_",value)

def get_cavitation_reference_velocity():
    return get_parameter("CavitationRefVelocity_",0)

def set_cavitation_reference_velocity(value):
    set_simple_real_parameter("CavitationRefVelocity_",value)

def get_cavitation_reference_length():
    return get_parameter("CavitationRefLength_",0)

def set_cavitation_reference_length(value):
    set_simple_real_parameter("CavitationRefLength_",value)

def get_cavitation_use_sigma():
    value = get_parameter("CavitationSigmaState_",0)
    if value == "ON":
        return 1
    else:
        return 0

def set_cavitation_use_sigma(flag):
    value = "OFF"
    if flag != 0:
        value = "ON"
    set_simple_string_parameter("CavitationSigmaState_",value)

def get_cavitation_sigma_initial():
    return get_parameter("CavitationSigmaInit_",0)

def set_cavitation_sigma_initial(value):
    set_simple_real_parameter("CavitationSigmaInit_",value)

def get_cavitation_sigma():
    return get_parameter("CavitationSigma_",0)

def set_cavitation_sigma(value):
    set_simple_real_parameter("CavitationSigma_",value)

def get_cavitation_vapor_pressure_initial():
    return get_parameter("CavitationVaporPressureInit_",0)

def set_cavitation_vapor_pressure_initial(value):
    set_simple_real_parameter("CavitationVaporPressureInit_",value)

def get_cavitation_vapor_pressure():
    return get_parameter("CavitationVaporPressure_",0)

def set_cavitation_vapor_pressure(value):
    set_simple_real_parameter("CavitationVaporPressure_",value)

def get_cavitation_sigma_decay_duration():
    return get_parameter("Cavitation_DT_dec_",0)

def set_cavitation_sigma_decay_duration(value):
    set_simple_real_parameter("Cavitation_DT_dec_",value)

def get_cavitation_activation_time():
    return get_parameter("Cavitation_T_ac_",0)

def set_cavitation_activation_time(value):
    set_simple_real_parameter("Cavitation_T_ac_",value)

def get_cavitation_MERKLE_liquid_production():
    return get_parameter("CavitationMerkleLiqProdCoef_",0)

def set_cavitation_MERKLE_liquid_production(value):
    set_simple_real_parameter("CavitationMerkleLiqProdCoef_",value)

def get_cavitation_MERKLE_liquid_destination():
    return get_parameter("CavitationMerkleLiqDestCoef_",0)

def set_cavitation_MERKLE_liquid_destination(value):
    set_simple_real_parameter("CavitationMerkleLiqDestCoef_",value)

def get_cavitation_KUNZ_liquid_production():
    return get_parameter("CavitationKunzLiqProdCoef_",0)

def set_cavitation_KUNZ_liquid_production(value):
    set_simple_real_parameter("CavitationKunzLiqProdCoef_",value)

def get_cavitation_KUNZ_liquid_destination():
    return get_parameter("CavitationKunzLiqDestCoef_",0)

def set_cavitation_KUNZ_liquid_destination(value):
    set_simple_real_parameter("CavitationKunzLiqDestCoef_",value)

def get_cavitation_SAUER_nuclei_density():
    return get_parameter("CavitationSauerNucleiDensity_",0)

def set_cavitation_SAUER_nuclei_density(value):
    set_simple_real_parameter("CavitationSauerNucleiDensity_",value)


#--------------------------------------------------------------------------------------------#
#------------------------------ Mooring (anchorage) -----------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_mooring():
    value = FM_get_anchorage_active_flag()
    if value == "YES":
        return 1
    else:
        return 0

def set_mooring(flag):
    value = "NO"
    if flag != 0:
        value = "YES"
    FM_set_anchorage_active_flag(value)

def get_mooring_list():
    nAnchors = get_parameter("AnchorageNumber_",0)
    ad_list = FM_get_mooring_list()
    out_list = []
    i = 0
    while i < nAnchors:
        out_list.append(ad_list[i][1])
        out_list.append(ad_list[i][0])
        i = i + 1
    return nAnchors, out_list

def get_mooring_list2():
    n, moor_list = get_mooring_list()
    m = len(moor_list)
    i = 0
    out_list = []

    while i < m:
        id = moor_list[i]
        name = ''
        i += 1

        if i < m:
            name = moor_list[i]
            i += 1

        out_list.append((id, name))

    return out_list

def set_mooring_list(nAnchors,*list):
    globalList = []
    i = 0
    while i < nAnchors:
        globalList.append(list[i][0])
        globalList.append(list[i][1])
        i = i + 1
    FM_set_mooring_list(nAnchors,globalList)

def set_mooring_list2(moor_list):
    set_mooring_list(len(moor_list), *moor_list)

def get_mooring_properties(disk_id):
    return FM_get_anchor_properties(disk_id)

def set_mooring_properties(disk_id,stiffness,pretension,fairleadDir_x,fairleadDir_y,fairleadDir_z,
    anchoragePoint_x,anchoragePoint_y,anchoragePoint_z,bodyIndex):
    dummy = 0
    FM_set_anchor_properties(disk_id,stiffness,pretension,fairleadDir_x,fairleadDir_y,fairleadDir_z,
        anchoragePoint_x,anchoragePoint_y,anchoragePoint_z,bodyIndex,dummy)

def get_mooring_compress(line):
    return FM_get_mooring_compress(line)

def set_mooring_compress(line, state):
    FM_set_mooring_compress(line, state)


#--------------------------------------------------------------------------------------------#
#----------------------------------------- Tugging ------------------------------------------#
#--------------------------------------------------------------------------------------------#

def get_tugging():
    value = FM_get_tug_line_active_flag()
    if value == "YES":
        return 1
    else:
        return 0

def set_tugging(flag):
    value = "NO"
    if flag != 0:
        value = "YES"
    FM_set_tug_line_active_flag(value)

def get_tugging_list():
    nTugs = get_parameter("TugLineNumber_",0)
    ad_list = FM_get_tugging_list()
    out_list = []
    i = 0
    while i < nTugs:
        out_list.append(ad_list[i][1])
        out_list.append(ad_list[i][0])
        i = i + 1
    return nTugs, out_list

def get_tugging_list2():
    m, tug_list = get_tugging_list()
    n = len(tug_list)
    i = 0
    out_list = []

    while i < n:
        id = tug_list[i]
        name = ''
        i += 1

        if i < n:
            name = tug_list[i]
            i += 1

        out_list.append((id, name))

    return out_list

def set_tugging_list(nTugs,*list):
    globalList = []
    i = 0
    while i < nTugs:
        globalList.append(list[i][0])
        globalList.append(list[i][1])
        i = i + 1
    FM_set_tugging_list(nTugs,globalList)

def set_tugging_list2(tug_list):
    set_tugging_list(len(tug_list), *tug_list)

def get_tugging_properties(disk_id):
    return FM_get_tug_line_properties(disk_id)

def set_tugging_properties(id,stiffness,pretension,p1_x,p1_y,p1_z,p2_x,p2_y,p2_z,bodyIndex1,bodyIndex2):
    dummy = 0
    if bodyIndex1 == bodyIndex2:
        raise ValueError, "This tug line must be linked to different bodies."
    FM_set_tug_line_properties(id,stiffness,pretension,p1_x,p1_y,p1_z,p2_x,p2_y,p2_z,bodyIndex1,bodyIndex2,dummy)

def get_tugging_compress(id):
    return FM_get_tugging_compress(id)

def set_tugging_compress(id, comp):
    FM_set_tugging_compress(id, comp)

#--------------------------------------------------------------------------------------------#
#------------------------------ Outputs selection -------------------------------------------#
#--------------------------------------------------------------------------------------------#

#def select_output( key_name ):
#def unselect_output( key_name ):

#--------------------------------------------------------------------------------------------#
#------------------------------ Launching mode ----------------------------------------------#
#--------------------------------------------------------------------------------------------#
SERIAL   = 0
PARALLEL = 1

#--------------------------------------------------------------------------------------------#
def launch_active_computation():
    # Global parameters => get value of first block.
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( " itm_solver:start" )

def get_launching_mode(task):
    return FM_get_partitions_number(task)

def set_launching_mode(task,mode):
    print 'Launching_mode: '+str(mode)
    if mode == SERIAL:
        FM_set_partitions_number(1)
    else:
        # default value for
        FM_set_partitions_number(2)

def get_number_of_processors(task):
    return FM_get_partitions_number(task)

#--------------------------------------------------------------------------------------------#
#------------------------------ Control variables -------------------------------------------#
#--------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------#
#------------------------------ Initial solution --------------------------------------------#
#--------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------#
#---                          Adaptive Grid Refinement                                    ---#
#--------------------------------------------------------------------------------------------#


# string parameter - see possible values in the Adaptive grid refinement menu,
# Refinement criterion type field
def set_criterion_type(typeName):
    FM_set_criterion_type(typeName)

def get_criterion_type():
	return {'FREE SURFACE': 'Free surface (directional)',
			'FREE SURFACE ISOTROPIC': 'Free surface (isotropic)',
			'PRESSURE GRADIENT ISOTROPIC': 'Pressure gradient (isotropic)',
			'VELOCITY GRADIENT ISOTROPIC': 'Velocity gradient (isotropic)',
			'VORTICITY ISOTROPIC': 'Vorticity (isotropic)',
			'FREE SURFACE TENSOR': 'Free surface (tensor)',
			'PRESSURE HESSIAN TENSOR': 'Pressure Hessian (tensor)',
			'PRESSURE HESSIAN ISOTROPIC': 'Pressure Hessian (isotropic)',
			'FREE SURFACE + PRESSURE HESSIAN': 'Free surface + pressure Hessian',
			'MULTISURFACE TENSOR': 'Multisurface (tensor)',
			'MULTISURFACE + PRESSURE HESSIAN': 'Multisurface + pressure Hessian',
			'MULTISURFACE + FLUX COMPONENT HESSIAN': 'Multisurface + flux component Hessian',
			'FLUX COMPONENT HESSIAN': 'Flux component Hessian',
			'NONE': 'Overset continuity only'
			}.get(get_parameter("raffCritType_",0), 'UNKNOWN CRITERION TYPE')

#--------------------------------------------------------------------------------------------#

# Possible parameter values: 1,0 #or constants YES,NO or ON,OFF
def set_refinement_usage(mode):
    if mode == 0:
        set_simple_string_parameter("useRefinementGrid_","NO");
    else:
        set_simple_string_parameter("useRefinementGrid_","YES");

def get_refinement_usage():
    res = get_parameter("useRefinementGrid_",0)
    if res == "YES":
        return 1
    else:
        return 0

#--------------------------------------------------------------------------------------------#

def set_refinement_threshold(threshold, cavit_threshold=0.0, hessian_threshold=0.0):
	FM_set_ref_threshold(threshold, cavit_threshold, hessian_threshold)

# 0 for primary threshold of the criterion,
# 1 for cavitation surface refinement threshold,
# 2 for hessian threshold of a combined criterion
def get_refinement_threshold(threshold_index=0):
    threshold = FM_get_ref_threshold()
    return threshold[threshold_index]

def get_hessian_eval():
    return FM_get_hessian_eval()

def set_hessian_eval(approach):
    FM_set_hessian_eval(approach)

def get_directional_derefinement():
    return FM_get_directional_derefinement()

def set_directional_derefinement(use):
    FM_set_directional_derefinement(use)

#--------------------------------------------------------------------------------------------#

# float parameter
def set_fraction(value):
    FM_set_fraction(value)

def get_fraction():
    return get_parameter("raffFraction_",0)

#--------------------------------------------------------------------------------------------#

# integer parameter
def set_max_n_generations(value):
    FM_set_max_n_generations(value)

def get_max_n_generations():
    return get_parameter("raffMaxNGenerations_",0)

#--------------------------------------------------------------------------------------------#

# integer parameter
def set_buff_layers_full(value):
    FM_set_buff_layers_full(value)

def get_buff_layers_full():
    return get_parameter("raffBufferLayerFull_",0)

#--------------------------------------------------------------------------------------------#

# integer parameter
def set_buff_layers_fraction(value):
    FM_set_buff_layers_fraction(value)

def get_buff_layers_fraction():
    return get_parameter("raffBufferLayerFraction_",0)

#--------------------------------------------------------------------------------------------#

# possible parameter values for set_bound_layer_protection function
NO_REFINEMENT           = "NO REFINEMENT";
FREE_REFINEMENT         = "FREE REFINEMENT";
LONGITUDINAL_REFINEMENT = "LONGITUDINAL REFINEMENT"
IGNORE_BOUNDARY_LAYERS  = "OFF";

def set_bound_layer_protection(value):
    #set_parameter("raffBoundLayerProtection_",STRING,0,value)
    FM_set_bound_layer_protection(value)

def get_bound_layer_protection():
	return {'LONGITUDINAL REFINEMENT': 'Longitudinal direction only',
			'FREE REFINEMENT': 'Any refinement',
			'OFF': 'Ignore boundary layers',
			'NO REFINEMENT': 'No refinement'
			}.get(get_parameter("raffBoundLayerProtection_",0),
			 'UNKNOWN BOUNDARY LAYER PROTECTION TYPE')


#--------------------------------------------------------------------------------------------#

# boolean parameter
def set_refinement_only_in_box_iso(value):
    if value == 0:
        FM_set_if_only_in_box_iso("NO")
    else:
        FM_set_if_only_in_box_iso("YES")

def get_refinement_only_in_box_iso():
    res = FM_get_if_only_in_box_iso()
    if res == "YES":
        return 1
    else:
        return 0

def get_only_in_box_iso():
    return FM_get_only_in_box_iso()

def set_only_in_box_iso(x_min,x_max,y_min,y_max,z_min,z_max):
    FM_set_only_in_box_iso(x_min,x_max,y_min,y_max,z_min,z_max)

#--------------------------------------------------------------------------------------------#

# boolean parameter
def set_refinement_only_in_box_dir(value):
    if value == 0:
        FM_set_if_only_in_box_dir("NO")
    else:
        FM_set_if_only_in_box_dir("YES")

def get_refinement_only_in_box_dir():
    res = FM_get_if_only_in_box_dir()
    if res == "YES":
        return 1
    else:
        return 0

def get_only_in_box_dir():
    return FM_get_only_in_box_dir()

def set_only_in_box_dir(x_x_min,x_x_max,x_y_min,x_y_max,x_z_min,x_z_max,y_x_min,y_x_max,y_y_min,y_y_max,y_z_min,y_z_max,z_x_min,z_x_max,z_y_min,z_y_max,z_z_min,z_z_max):
    FM_set_only_in_box_dir(x_x_min,x_x_max,x_y_min,x_y_max,x_z_min,x_z_max,y_x_min,y_x_max,y_y_min,y_y_max,y_z_min,y_z_max,z_x_min,z_x_max,z_y_min,z_y_max,z_z_min,z_z_max)

# get_
#    str = "raffXOnlyInBox_";

#--------------------------------------------------------------------------------------------#

def get_steps_before_first_refinement():
    return FM_get_steps_before_first()

def set_steps_before_first_refinement(value):
    FM_set_steps_before_first(value)

def get_steps_between_refinements():
    return FM_get_steps_between()

def set_steps_between_refinements(value):
    FM_set_steps_between(value)

#--------------------------------------------------------------------------------------------#

def get_min_cell_size():
    return get_parameter("raffMinCellSize_",0)

def set_min_cell_size(value):
    FM_set_min_cell_size(value)

def get_free_surface_criterion_smooth_mass():
    res = get_parameter("raffCritCiBaseSm_",0)
    if res == "YES":
        return 1
    else:
        return 0

def set_free_surface_criterion_smooth_mass(value):
    if value == 0:
        set_simple_string_parameter("raffCritCiBaseSm_","NO")
    else:
        set_simple_string_parameter("raffCritCiBaseSm_","YES")

def get_convection_buffer():
    res = get_parameter("raffConvBuffer_",0)
    if res == "YES":
        return 1
    else:
        return 0

def set_convection_buffer(value):
    if value == 0:
        set_simple_string_parameter("raffConvBuffer_","NO")
    else:
        set_simple_string_parameter("raffConvBuffer_","YES")

def get_scalar_product_zone():
    res = get_parameter("raffScalProdRefZone_",0)
    if res == "YES":
        return 1
    else:
        return 0

def set_scalar_product_zone(value):
    if value == 0:
        set_simple_string_parameter("raffScalProdRefZone_","NO")
    else:
        set_simple_string_parameter("raffScalProdRefZone_","YES")

def get_conditional_factor():
    return get_parameter("raffConditionalFactor_",0)

def set_conditional_factor(value):
    FM_set_conditional_factor(value)

def get_repetitions():
    return get_parameter("raffRepetitions_",0)

def set_repetitions(value):
    FM_set_repetitions(value)

def get_mem_max_cells():
    return get_parameter("raffMemMaxCells_",0)

def set_mem_max_cells(value):
    FM_set_mem_max_cells(value)

def get_reinit_after_first_step():
    res = get_parameter("raffReinitialiseAfterFirstStep_",0)
    if res == "YES":
        return 1
    else:
        return 0

def set_reinit_after_first_step(value):
    if value == 0:
        set_simple_string_parameter("raffReinitialiseAfterFirstStep_","NO")
    else:
        set_simple_string_parameter("raffReinitialiseAfterFirstStep_","YES")

def get_projection_surface():
    res = get_parameter("UseProjectionOnSurface_",0)
    if res == "YES":
        return 1
    else:
        return 0

def set_projection_surface(value):
    if value == 0:
        set_simple_string_parameter("UseProjectionOnSurface_","NO")
    else:
        set_simple_string_parameter("UseProjectionOnSurface_","YES")

# returns False or True
def is_rot_frame_active(block):
    cres = FM_is_rot_frame_active(block)

    if cres == 0:
        res = False
    else:
        res = True

    return res

# val is 0 or 1, or False/True
def set_rot_frame_usage(block, val):
    if val:
        cval = 1
    else:
        cval = 0

    FM_set_rot_frame_usage(block, cval)

def quit():
    if is_batch():
        FM_quit(0)
    else:
        eval_tcl_string("itm_project:do_quit 0")

def get_body_type(body):
    return FM_get_body_type(body)

def set_body_type(body, type):
    FM_set_body_type(body, type)

#
# Uncertainty Quantification
#

def get_uncertainty_approach_usage():
    res = FM_get_uncertainty_approach_usage()
    return (res != 0)

def set_uncertainty_approach_usage(usage):
    cusage = 0

    if usage:
        cusage = 1

    FM_set_uncertainty_approach_usage(cusage)

def is_UQ_available():
    res = FM_is_UQ_available()
    return (res != 0)

def get_number_of_uncertainties():
    return FM_number_of_uncertainties()

# index isn't specified: returns number of sub-computations of the current computation
# index is specified: return number of sub-computations of the computation of given index
def get_nb_of_subcomputations(index = None):
    if index is None:
        res = FM_nb_of_subcomputations()
    else:
        res = FM_nb_of_subcomputations(index)

    return res

def get_uncertainty(index):
    return FM_get_uncertainty(index)

def set_uncertainty_usage(block, face, patch, quantity, use):
    cuse = 0

    if use:
        cuse = 1

    FM_set_uncertainty_usage(block, face, patch, quantity, cuse)

def get_uncertainty_usage(block, face, patch, quantity):
    return FM_get_uncertainty_usage(block, face, patch, quantity)

def get_uncertainty_params(block, face, patch, quantity):
    return FM_get_uncertainty_params(block, face, patch, quantity)

def set_uncertainty_params(block, face, patch, quantity, chaos_order, distribution,
                           ave, var, min, max, pdf_file):
    FM_set_uncertainty_params(block, face, patch, quantity, chaos_order, distribution,
                              ave, var, min, max, pdf_file)

def update_uncertainty(restart = 1):
    FM_update_uncertainty(restart)

def collect_uncertainty_results(percent = 10.0):
    FM_collect_uncertainty_results(percent)

def write_uncertainty_report():
    FM_write_uncertainty_report()

def get_forces_list():
    return FM_get_forces_list()

def get_computed_force(body, force):
    return FM_get_computed_force(body, force)

def get_uncertain_force(body, force):
    ave, var, min, max, skew, kurt = get_uncertain_force_2(body, force)
    return ave, var, min, max

def get_uncertain_force_2(body, force):
    return FM_get_uncertain_force_2(body, force)

def get_PDF_reconstruction(mean, variance, skewness, kurtosis, points):
    return FM_get_PDF_reconstruction(mean, variance, skewness, kurtosis, points)

def get_non_determ_cubature_rule():
    return FM_get_non_determ_cubature_rule()

def set_non_determ_cubature_rule(rule):
    FM_set_non_determ_cubature_rule(rule)

def get_collocation_points_nb(block, face, patch, quantity):
    return FM_collocation_points_nb(block, face, patch, quantity)

def get_collocation_point(block, face, patch, quantity, no):
    return FM_get_collocation_point(block, face, patch, quantity, no)

def get_uncertainty_weight(subcompno):
    return FM_get_uncertainty_weight(subcompno)

def get_quantity_value(b, f, p, quantity):
    return FM_get_quantity_value(b, f, p, quantity)

def set_quantity_value(b, f, p, quantity, val):
    FM_set_quantity_value(b, f, p, quantity, val)

def quantity_units(q):
    res = ''

    if q == 'Vx' or q == 'Vy' or q == 'Vz':
        res = 'm/s'
    elif q == "Wave height":
        res = 'm'
    elif q == "Turbulent kinetic energy":
        res = 'm2/s2'
    elif q == "Turbulent dissipation":
        res = 'm2/s3'
    elif q == "Turbulent viscosity":
        res = 'm2/s'
    elif q == "Wave period":
        res = 's'

    return res

def full_quantity_name(q, b, f, p):
    per_patch = ["Vx", "Vy", "Vz", "Turbulent kinetic energy", "Turbulent dissipation", "Turbulent viscosity", "Wave height", "Wave period"]
    res = q

    if q in per_patch:
        res = res + '(' + BCPatch(b, p).get_name() + ')'

    return res

def plot_dependency(computations, b, f, p, quantity, body, force):
    import matplotlib.pyplot as plt
    # create matplotlib figure depicting dependence between
    # quantity and force, then return that figure
    X = []
    Y = []

    # draw deterministic results first
    for c in computations:
        if set_active_computation(c):
            x = get_quantity_value(b, f, p, quantity)
            y = get_computed_force(body, force)
            X.append(x)
            Y.append(y)

    fig = plt.figure()
    fullq = full_quantity_name(quantity, b, f, p)
    title = force + '(' + body + ') vs ' + fullq
    fig.canvas.set_window_title('Figure ' + str(fig.number) + ' - Dependency ' + title)
    fig.suptitle(title)
    ax = fig.add_subplot(111)
    ax.plot(X, Y, "Db-", label='Deterministic results')
    xlab = fullq
    units = quantity_units(quantity)

    if units != '':
        xlab += ' [' + units + ']'

    ax.set_xlabel(xlab)
    ax.set_ylabel(force + '(' + body + ') [N]')

    # add non-deterministic results if any
    X = []
    Y = []
    Xerr = []
    Yerr = []
    addnondet = False

    for c in computations:
        if set_active_computation(c):
            print str(c) + ' is selected'
            if get_uncertainty_approach_usage():
                addnondet = True
                mean, variance, minv, maxv = get_uncertain_force(body, force)
                y = mean
                yerr = 2 * math.sqrt(variance)
                x = get_quantity_value(b, f, p, quantity)
                xerr = 0

                if get_uncertainty_usage(b, f, p, quantity):
                    pc_order, distr, ave, var, minv, maxv, profile = get_uncertainty_params(b, f, p, quantity)

                    if distr == 'Gauss' or distr == 'Truncated Gauss':
                        x = ave
                        xerr = 2 * math.sqrt(var)

                X.append(x)
                Y.append(y)
                Xerr.append(xerr)
                Yerr.append(yerr)

    if addnondet:
        ax.errorbar(X, Y, yerr=Yerr, xerr=Xerr, color='black',
            marker='s', markerfacecolor='green', label='Non-deterministic results', lw = 0.5)

    ax.legend(prop={'size': 'small'})
    ax.ticklabel_format(style='sci', scilimits=(-4,4))
    fig.tight_layout(pad = 1.5)

    return fig

#
# Task management
#

def local_machine():
    """Local host name"""
    return FM_local_machine()

def add_machine(machinename, arch):
    """
    Add a machine into Task Manager using empty password.
    arch can be 'Windows' or 'Linux'.
    """
    FM_add_machine(machinename, arch)

# MPI choices for the solver

OPEN_MPI  = 0
INTEL_MPI = 1
MPICH     = 2

# Queueing system choices

SGE         = 1
PBS         = 2
LSF         = 3
LoadLeveler = 4
WinHPC      = 5

class Task:
    def __init__(self, simfile):
        self.simfile = simfile

    def launch(self):
        """
        Save batch file, launch task and return saved batch file name.
        Note that the batch file isn't used for launching actually.
        """
        return FM_launch_task(self.simfile)

    def kill(self):
        """Kill the solver using stop.now file."""
        FM_kill_task(self.simfile)

    def suspend(self):
        """Suspend the solver using stop.now file."""
        FM_suspend_task(self.simfile)

    def save_batch_file(self):
        """Save the batch file."""
        return FM_save_batch_file(self.simfile)

    # Group of methods to handle sub-tasks

    def enable_preprocessing(self, machine):
        FM_setup_subtask(self.simfile, "Pre-processing", 1, machine)

    def disable_preprocessing(self):
        FM_setup_subtask(self.simfile, "Pre-processing", 0, local_machine())

    def enable_solver(self, machine):
        FM_setup_subtask(self.simfile, "Solver", 1, machine)

    def disable_solver(self):
        FM_setup_subtask(self.simfile, "Solver", 0, local_machine())

    def enable_postprocessing(self, machine):
        FM_setup_subtask(self.simfile, "Post-processing", 1, machine)

    def disable_postprocessing(self):
        FM_setup_subtask(self.simfile, "Post-processing", 0, local_machine())

    def enable_solver_tool(self, toolname, machine):
        FM_setup_solver_tool(self.simfile, toolname, 1, machine)

    def disable_solver_tool(self, toolname):
        FM_setup_solver_tool(self.simfile, toolname, 0, local_machine())

    def set_machines(self, *list):
        """Set machines for the solver."""
        FM_set_machines(self.simfile, *list)

    def get_fullflex_license(self):
        return FM_get_fullflex_license(self.simfile)

    def set_fullflex_license(self, fullflex):
        FM_set_fullflex_license(self.simfile, fullflex)

    def get_MPI(self):
        return FM_get_MPI_choice(self.simfile)

    def set_MPI(self, choice):
        FM_set_MPI_choice(self.simfile, choice)

    def save_queue_job(self, system, queue, jobname, mpi, sgePE):
        """
        Save the queuing system submit script.
        """
        return FM_save_queue_job(self.simfile, system, queue, jobname, mpi, sgePE)

    def get_status(self, tool, field = 'STATUS'):
        """
        Returns information from status.dat file.
        tool can be postmetis, hexpress2isis, 3dto2d, premetis, isiscfd, isis2hexpress,
        isis2cfview and probes2cfview.
        """
        name_value = FM_get_status(self.simfile)
        it = iter(name_value)
        dat = dict(zip(it, it))
        result = ''

        if field == 'STATUS':
            result = dat[tool]
        elif field == 'DATE':
            result = dat['time_' + tool]
        elif field == 'NPART':
            if tool == 'isiscfd':
                result = dat['npart']
            elif tool == 'premetis':
                result = dat['premetis_npart']
        elif field == 'SAVE_COUNTER':
            result = dat['save_count']

        return result

    def get_postmetis_status(self):
        return self.get_status("postmetis")

    def get_hexpress2isis_status(self):
        return self.get_status("hexpress2isis")

    def get_premetis_status(self):
        return self.get_status("premetis")

    def get_isiscfd_status(self):
        return self.get_status("isiscfd")

    def get_isis2hexpress_status(self):
        return self.get_status("isis2hexpress")

    def get_isis2cfview_status(self):
        return self.get_status("isis2cfview")

    def get_probes2cfview_status(self):
        return self.get_status("probes2cfview")

def submit_queue_job(system, batchfile):
    """Submits a batch file to the queuing system."""
    FM_submit_queue_job(system, batchfile)

def add_task(simfile):
    """Add task to Task Manager and return corresponding Task instance."""
    FM_add_task(simfile)
    return Task(simfile)

def remove_task(task):
    """Remove task from Task Manager."""
    FM_remove_task(task.simfile)

def task_list():
    """Return list of all tasks in Task Manager."""
    list = FM_task_list()
    res = []

    for simfile in list:
        task = Task(simfile)
        res.append(task)

    return res

#
# Results analysis
#

# returns number of created figure
def create_figure(title, xtitle, ytitle):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    fig.clf()
    fig.suptitle(title)
    ax = fig.add_subplot(111)
    ax.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)

    return fig.number

def plot_figure(fignum, x, y, legend, marker):
    import matplotlib.pyplot as plt
    fig = plt.figure(fignum)
    ax = fig.gca()

    if len(x) != len(y):
        print 'Error! plot_figure: wrong number of values, ' + str(len(x)) + ' for x axis vs ' + str(len(y)) + ' for y axis.'
        print 'Truncating data...'

        if len(x) > len(y):
            x = x[:len(y)]
        else:
            y = y[:len(x)]

    markerst = ''

    if marker:
        markerst = '.'

    if legend == '':
        ax.plot(x, y, linestyle='-', marker=markerst)
    else:
        ax.plot(x, y, label=legend, linestyle='-', marker=markerst)

def finish_figure(fignum, file, xmin, xmax, ymin, ymax):
    import matplotlib.pyplot as plt
    fig = plt.figure(fignum)
    ax = fig.gca()
    ax.grid(True)

    if xmin is not None:
        ax.set_xlim(left = xmin)

    if xmax is not None:
        ax.set_xlim(right = xmax)

    if ymin is not None:
        ax.set_ylim(bottom = ymin)

    if ymax is not None:
        ax.set_ylim(top = ymax)

    # Add 1% margin between the plot and the border of the plotting area.

    ax.margins(0.01, 0.01)

    save_config = { 'bbox_inches': 'tight' }
    h, l = ax.get_legend_handles_labels()

    if len(l) > 1 or len(l) == 1 and l[0] != '':
        lgd = ax.legend(h, l, prop={'size': 'small'}, loc='best')
        save_config['bbox_extra_artists'] = (lgd,)

    ax.ticklabel_format(style='sci', scilimits=(-4,4))
    fig.savefig(file + ".png", **save_config)

    # Free matplotlib resources.

    plt.close(fig)

class SelfPropAnalysis:
    def __init__(self):
        self.Rttow = 0.0
        self.SFC = 0.0
        self.open_water_file = ''
        self.ship = ''
        self.propeller = ''
        self.D = 0.0
        self.n = 0.0

class ResultsAnalyzer:
    def __init__(self):
        self.__quantities = []
        self.__resist_curve = False
        self.__average_efforts = True
        self.__average_motions = False
        self.__average_percent = 10.0
        self.__conv_crit = 1.0
        self.__apply_median_filter = False
        self.__apply_moving_avg = False
        self.__median_window = 1
        self.__moving_avg_window = 1
        self.__join_quantities = False
        self.__join_comps = False
        self.__xmin = None
        self.__xmax = None
        self.__ymin = None
        self.__ymax = None
        self.__Fx2 = False
        self.__apply_modulus = False
        self.__divide = False # apply dimensionless coefficient
        self.__dimless_name = 'C'
        self.__dimless_value = 1.0
        self.__self_prop = SelfPropAnalysis()

    def set_quantities(self, quantities):
        self.__quantities = quantities

    def get_quantities(self):
        return self.__quantities

    def set_resistance_curve(self, usage):
        self.__resist_curve = usage

    def get_resistance_curve(self):
        return self.__resist_curve

    def track_averaging_on(self, efforts, motions):
        self.__average_efforts = efforts
        self.__average_motions = motions

    def get_averaging_tracking(self):
        return self.__average_efforts, self.__average_motions

    def set_averaging_options(self, use_last_percent, conv_crit):
        self.__average_percent = use_last_percent
        self.__conv_crit = conv_crit

    def get_averaging_options(self):
        return self.__average_percent, self.__conv_crit

    def set_median_filter(self, use, window_width):
        self.__apply_median_filter = use
        self.__median_window = window_width

    def get_median_filter(self):
        return self.__apply_median_filter, self.__median_window

    def set_moving_average(self, use, window_width):
        self.__apply_moving_avg = use
        self.__moving_avg_window = window_width

    def get_moving_average(self):
        return self.__apply_moving_avg, self.__moving_avg_window

    def set_plot_options(self, joint_quantities, joint_computations):
        self.__join_quantities = joint_quantities
        self.__join_comps = joint_computations

    def get_plot_options(self):
        return self.__join_quantities, self.__join_comps

    def set_axis_limits(self, xmin, xmax, ymin, ymax):
        self.__xmin = xmin
        self.__xmax = xmax
        self.__ymin = ymin
        self.__ymax = ymax

    def get_axis_limits(self):
        return (self.__xmin, self.__xmax, self.__ymin, self.__ymax)

    def set_Fx_doubling(self, yes):
        self.__Fx2 = yes

    def get_Fx_doubling(self):
        return self.__Fx2

    def set_abs_plot(self, yes):
        self.__apply_modulus = yes

    def get_abs_plot(self):
        return self.__apply_modulus

    def set_dimensionless_coeff(self, yes, name, value):
        self.__divide = yes
        self.__dimless_name = name
        self.__dimless_value = value

    def get_dimensionless_coeff(self):
        return (self.__divide, self.__dimless_name, self.__dimless_value)

    def get_self_propulsion(self):
        return self.__self_prop

    def set_self_propulsion(self, sp):
        self.__self_prop = sp

    def analyze(self, foldername = 'Convergence_report'):
        limit_xmin = 0
        limit_xmax = 0
        limit_ymin = 0
        limit_ymax = 0
        xmin = 0.0
        xmax = 0.0
        ymin = 0.0
        ymax = 0.0

        if self.__xmin is not None:
            limit_xmin = 1
            xmin = self.__xmin

        if self.__xmax is not None:
            limit_xmax = 1
            xmax = self.__xmax

        if self.__ymin is not None:
            limit_ymin = 1
            ymin = self.__ymin

        if self.__ymax is not None:
            limit_ymax = 1
            ymax = self.__ymax

        sp_enabled = 1
        sp_options = self.__self_prop

        if sp_options is None:
            sp_enabled = 0
            sp_options = FM.SelfPropAnalysis()

        tail = self.__quantities[:];
        tail += [sp_enabled, sp_options.ship, sp_options.propeller,
            sp_options.D, sp_options.Rttow, sp_options.SFC,
            sp_options.n, sp_options.open_water_file]

        FM_convergence_report(foldername,
            self.__average_efforts, self.__average_motions,
            self.__average_percent, self.__conv_crit,
            self.__apply_median_filter, self.__median_window,
            self.__apply_moving_avg, self.__moving_avg_window,
            self.__join_quantities, self.__join_comps,
            self.__resist_curve,
            limit_xmin, xmin, limit_xmax, xmax,
            limit_ymin, ymin, limit_ymax, ymax,
            self.__Fx2, self.__apply_modulus,
            self.__divide, self.__dimless_name, self.__dimless_value,
            len(self.__quantities), *tail)

#
# Modal Approach to Fluid-Structure Interactions
#

def is_modal_approach_available():
    return FM_is_modal_approach_available()

def get_modal_approach_usage():
    return FM_get_modal_approach_usage()

def set_modal_approach_usage(usage):
    FM_set_modal_approach_usage(usage)

def get_coupling_activation(bodyID):
    return FM_is_coupling_active(bodyID)

def set_coupling_activation(bodyID, active):
    FM_set_coupling_activation(bodyID, active)

class ModalStructure:
    def __init__(self, structID):
        self.index = structID

    def get_file(self):
        return FM_get_modal_structure_file(self.index)

    def set_file(self, filename):
        FM_set_modal_structure_file(self.index, filename)

    def get_modes_nb(self):
        return FM_get_modal_structure_modes_nb(self.index)

    def set_modes_nb(self, nb):
        FM_set_modal_structure_modes_nb(self.index, nb)

    def get_name(self):
        return FM_get_modal_structure_name(self.index)

    def set_name(self, name):
        FM_set_modal_structure_name(self.index, name)

    def get_modal_mode(self, mode_no):
        damping = FM_get_modal_mode_damping(self.index, mode_no)
        A0 = FM_get_modal_mode_initial_amplitude(self.index, mode_no)
        amc_estimode = FM_get_modal_mode_amc_estimation_mode(self.index, mode_no)
        amc_value = FM_get_modal_mode_amc_value(self.index, mode_no)
        amc_estim_freq = FM_get_modal_mode_amc_estimation_frequency(self.index, mode_no)
        return (damping, A0, amc_estimode, amc_value, amc_estim_freq)

    def set_modal_mode(self, mode_no, damping, init_ampl, AMC_estimode, AMC_value, AMC_iter):
        FM_set_modal_mode_damping(self.index, mode_no, damping)
        FM_set_modal_mode_initial_amplitude(self.index, mode_no, init_ampl)
        FM_set_modal_mode_amc_estimation_mode(self.index, mode_no, AMC_estimode)
        FM_set_modal_mode_amc_value(self.index, mode_no, AMC_value)
        FM_set_modal_mode_amc_estimation_frequency(self.index, mode_no, AMC_iter)

    def modal_mode(self, mode_no):
        return ModalMode(self.index, mode_no)

class ModalMode:
    def __init__(self, structID, mode_no):
        self.structure = structID
        self.mode_no = mode_no

    def get_damping(self):
        return FM_get_modal_mode_damping(self.structure, self.mode_no)

    def set_damping(self, damping):
        FM_set_modal_mode_damping(self.structure, self.mode_no, damping)

    def get_initial_amplitude(self):
        return FM_get_modal_mode_initial_amplitude(self.structure, self.mode_no)

    def set_initial_amplitude(self, A0):
        FM_set_modal_mode_initial_amplitude(self.structure, self.mode_no, A0)

    def get_amc_estimation_mode(self):
        return FM_get_modal_mode_amc_estimation_mode(self.structure, self.mode_no)

    def set_amc_estimation_mode(self, estimation_mode):
        FM_set_modal_mode_amc_estimation_mode(self.structure, self.mode_no, estimation_mode)

    def get_amc_value(self):
        return FM_get_modal_mode_amc_value(self.structure, self.mode_no)

    def set_amc_value(self, value):
        FM_set_modal_mode_amc_value(self.structure, self.mode_no, value)

    def get_amc_estimation_frequency(self):
        return FM_get_modal_mode_amc_estimation_frequency(self.structure, self.mode_no)

    def set_amc_estimation_frequency(self, iterations):
        FM_set_modal_mode_amc_estimation_frequency(self.structure, self.mode_no, iterations)

    def get_quasi_static_law(self):
        return FM_get_modal_mode_quasi_static_law(self.structure, self.mode_no)

    def set_quasi_static_law(self, law):
        FM_set_modal_mode_quasi_static_law(self.structure, self.mode_no, law)

    def get_quasi_static_starting_time(self):
        return FM_get_modal_mode_quasi_static_starting_time(self.structure, self.mode_no)

    def set_quasi_static_starting_time(self, t0):
        FM_set_modal_mode_quasi_static_starting_time(self.structure, self.mode_no, t0)

    def get_quasi_static_relaxation(self):
        return FM_get_modal_mode_quasi_static_relaxation(self.structure, self.mode_no)

    def set_quasi_static_relaxation(self, r):
        FM_set_modal_mode_quasi_static_relaxation(self.structure, self.mode_no, r)

    def get_quasi_static_intervals_type(self):
        return FM_get_modal_mode_quasi_static_intervals_type(self.structure, self.mode_no)

    def set_quasi_static_intervals_type(self, unit):
        FM_set_modal_mode_quasi_static_intervals_type(self.structure, self.mode_no, unit)

    def get_quasi_static_intervals_sec(self):
        return FM_get_modal_mode_quasi_static_intervals_sec(self.structure, self.mode_no)

    def set_quasi_static_intervals_sec(self, dT2, dT3):
        FM_set_modal_mode_quasi_static_intervals_sec(self.structure, self.mode_no, dT2, dT3)

    def get_quasi_static_intervals_ts(self):
        return FM_get_modal_mode_quasi_static_intervals_ts(self.structure, self.mode_no)

    def set_quasi_static_intervals_ts(self, dT2, dT3):
        FM_set_modal_mode_quasi_static_intervals_ts(self.structure, self.mode_no, dT2, dT3)

def get_body_modal_structure(bodyID):
    return ModalStructure(FM_get_body_modal_structure(bodyID))

def set_body_modal_structure(bodyID, struc):
    FM_set_body_modal_structure(bodyID, struc.index)

def get_modal_structures():
    """Return list of all modal structures."""
    list = FM_get_modal_structures()
    res = []

    for structID in list:
        struc = ModalStructure(structID)
        res.append(struc)

    return res

def add_modal_structure(structID, name):
    FM_add_modal_structure(structID, name)
    return ModalStructure(structID)

def remove_modal_structure(structID):
    FM_remove_modal_structure(structID)

# Expert parameter, it is per-body, although per-modal structure makes more sense.
def get_map_loads_on_init_shape(bodyID):
    return FM_get_map_loads_on_init_shape(bodyID)

def set_map_loads_on_init_shape(bodyID, map_loads):
    FM_set_map_loads_on_init_shape(bodyID, map_loads)

def get_body_fsi_node_reduction(bodyID):
    return FM_get_body_fsi_node_reduction(bodyID)

def set_body_fsi_node_reduction(bodyID, active, tolerance):
    FM_set_body_fsi_node_reduction(bodyID, active, tolerance)

def get_body_fsi_reference_length(bodyID):
    return FM_get_body_fsi_reference_length(bodyID)

def set_body_fsi_reference_length(bodyID, defined, Lref):
    FM_set_body_fsi_reference_length(bodyID, defined, Lref)

def get_body_fsi_deformed_ext(bodyID):
    return FM_get_body_fsi_deformed_ext(bodyID)

def set_body_fsi_deformed_ext(bodyID, active):
    FM_set_body_fsi_deformed_ext(bodyID, active)

def get_body_fsi_quasi_static_active(bodyID):
    return FM_get_body_fsi_quasi_static_active(bodyID)

def set_body_fsi_quasi_static_active(bodyID, active):
    FM_set_body_fsi_quasi_static_active(bodyID, active)

DEFORM_ALL                 = 1
DEFORM_ELIGIBLE_NON_MIRROR = 2
DEFORM_ELIGIBLE            = 3

def get_body_fsi_deform_strategy(bodyID):
    return FM_get_body_fsi_deform_strategy(bodyID)

def set_body_fsi_deform_strategy(bodyID, strategy):
    FM_set_body_fsi_deform_strategy(bodyID, strategy)

#
# Overset grids
#

def get_overset_activation():
    return FM_get_overset_activation()

def set_overset_activation(active):
    FM_set_overset_activation(active)

# convenient 'constants' for the next two methods
OVERLAPPING = 1
BACKGROUND = 2
LINKED = 3

def get_overset_domain_type(blockID):
    return FM_get_overset_domain_type(blockID)

def set_overset_domain_type(blockID, site):
    FM_set_overset_domain_type(blockID, site)

def get_overset_domain_physical_BC(blockID):
    return FM_get_overset_domain_physical_BC(blockID)

def set_overset_domain_physical_BC(blockID, has_bc):
    FM_set_overset_domain_physical_BC(blockID, has_bc)

def get_overset_domain_distance(blockID):
    return FM_get_overset_domain_distance(blockID)

def set_overset_domain_distance(blockID, distance):
    FM_set_overset_domain_distance(blockID, distance)

def get_overset_parent_domain(blockID):
    return FM_get_overset_parent_domain(blockID)

def set_overset_parent_domain(blockID, outerID):
    FM_set_overset_parent_domain(blockID, outerID)

def get_body_of_overset_domain_boundary(bodyID):
    return FM_get_body_of_overset_domain_boundary(bodyID)

def set_body_of_overset_domain_boundary(bodyID, bound):
    FM_set_body_of_overset_domain_boundary(bodyID, bound)

#
# Detection of wave generator parameters
#

# h - mean depth
# H - wave height
# tau - period
# g - gravity intensity
def estimate_wave_order(h, H, tau, g):
    return FM_estimate_wave_order(h, H, tau, g)

def detect_wave_generator_point():
    patch_list = get_bc_patch_list('*')
    wave_gens = []

    for p in patch_list:
        if p.get_bc_name() == 'EXT' and p.get_bc_type()[0] == 45:
            wave_gens.append(p._blockID - 1)
            wave_gens.append(p._patchID - 1)

    return FM_detect_wave_generator_point(len(wave_gens)/2, *wave_gens)

#
# Transition model
#

def get_transition_model_usage():
    return FM_get_transition_model_usage()

def set_transition_model_usage(active):
    FM_set_transition_model_usage(active)

#
# Internal wave generator
#

def get_internal_wave_usage():
    return FM_get_internal_wave_usage()

def set_internal_wave_usage(active):
    FM_set_internal_wave_usage(active)

POSITIVE_X = +1
NEGATIVE_X = -1
BOTH_X     = 2

class InternalWaveParameters:
    def __init__(self):
        self._spectrum = 'REGULAR'
        self._depth    = 5.0
        self._period   = 0.0
        self._height   = 0.0
        self._source_x = 0.0
        self._dir      = BOTH_X
        self._domain   = 1
        self._gamma    = 3.3
        self._data_file = ''

    def get_spectrum(self):
        return self._spectrum

    def set_spectrum(self, spectrum):
        self._spectrum = spectrum

    def get_depth(self):
        return self._depth

    def set_depth(self, depth):
        self._depth = depth

    def get_period(self):
        return self._period

    def set_period(self, period):
        self._period = period

    def get_height(self):
        return self._height

    def set_height(self, height):
        self._height = height

    def get_source_x(self):
        return self._source_x

    def set_source_x(self, x):
        self._source_x = x

    def get_direction(self):
        return self._dir

    def set_direction(self, direction):
        self._dir = direction

    def get_domain(self):
        return self._domain

    def set_domain(self, domain_number):
        self._domain = domain_number

    def get_steepness(self):
        return self._gamma

    def set_steepness(self, gamma):
        self._gamma = gamma

    def get_data_file(self):
        return self._data_file

    def set_data_file(self, filename):
        self._data_file = filename

def get_internal_wave_parameters():
    spectrum, depth, period, height, source_x, direction, \
            domain, gamma, filename = FM_get_internal_wave_parameters()
    p = InternalWaveParameters()
    p.set_spectrum(spectrum)
    p.set_depth(depth)
    p.set_period(period)
    p.set_height(height)
    p.set_source_x(source_x)
    p.set_direction(direction)
    p.set_domain(domain)
    p.set_steepness(gamma)
    p.set_data_file(filename)

    return p

def set_internal_wave_parameters(p):
    FM_set_internal_wave_parameters(p.get_spectrum(),
                                    p.get_depth(),
                                    p.get_period(),
                                    p.get_height(),
                                    p.get_source_x(),
                                    p.get_direction(),
                                    p.get_domain(),
                                    p.get_steepness(),
                                    p.get_data_file())

#
# Sponge layer
#

def get_wave_damping_usage():
    return FM_get_wave_damping_usage()

def set_wave_damping_usage(active):
    FM_set_wave_damping_usage(active)

def get_sponge_layer():
    return FM_get_sponge_layer()

def set_sponge_layer(xsmin, xsmax, ysmin, ysmax):
    FM_set_sponge_layer(xsmin, xsmax, ysmin, ysmax)

def get_model_bounding_box():
    return FM_get_model_bounding_box()

#
# Pressure solver parameters
#

DYNAMIC_SWITCH = 0
PCGSTAB_MB     = 1
BOOMER_AMG     = 2

def get_psolver_method():
    return FM_get_psolver_method()

def set_psolver_method(methodID):
    FM_set_psolver_method(methodID)

class PSolverMethodParams:
    def __init__(self, convCrit, maxIt):
        self.convergenceCrit = convCrit
        self.maxIter = maxIt

    def __eq__(self, params):
        if isinstance(params, PSolverMethodParams):
            return (self.convergenceCrit == params.convergenceCrit and
                    self.maxIter         == params.maxIter)

        return NotImplemented

    def __ne__(self, params):
        if isinstance(params, PSolverMethodParams):
            return not (self == params)

        return NotImplemented

def get_psolver_method_params(methodID):
    convCrit, maxIt = FM_get_psolver_method_params(methodID)
    return PSolverMethodParams(convCrit, maxIt)

def set_psolver_method_params(methodID, method_params):
    FM_set_psolver_method_params(methodID,
                                 method_params.convergenceCrit,
                                 method_params.maxIter)

#
# Passive scalar
#

def get_passive_scalar_usage():
    return FM_get_passive_scalar_usage()

def set_passive_scalar_usage(use):
    FM_set_passive_scalar_usage(use)

def get_passive_scalar_name():
    return FM_get_passive_scalar_name()

def set_passive_scalar_name(name):
    FM_set_passive_scalar_name(name)

def get_passive_scalar_scheme():
    return FM_get_passive_scalar_scheme()

def set_passive_scalar_scheme(scheme):
    FM_set_passive_scalar_scheme(scheme)

#
# Roughness parameters
#

def get_wall_roughness():
    return FM_get_wall_roughness()

def set_wall_roughness(active):
    FM_set_wall_roughness(active)

def get_sand_grain_height():
    return FM_get_sand_grain_height()

def set_sand_grain_height(height):
    FM_set_sand_grain_height(height)

def get_wall_roughness_mode():
    return FM_get_wall_roughness_mode()

def set_wall_roughness_mode(mode):
    FM_set_wall_roughness_mode(mode)

#
# Quasi-static approach
#

def get_quasi_static_active():
    value = get_parameter("Quasi_Static_",0)
    if value == "YES":
        return 1
    else:
        return 0

def set_quasi_static_active(flag):
    value = "NO"
    if flag == 1:
        value = "YES"
    FM_set_quasi_static_active(value)

HULL_QS = 0
FOIL_QS = 1

def get_quasi_static_mode():
    return FM_get_quasi_static_mode()

def set_quasi_static_mode(mode):
    FM_set_quasi_static_mode(mode)

SECONDS   = 0
TIMESTEPS = 1

def get_quasi_static_intervals_type(bodyID):
    return FM_get_quasi_static_intervals_unit(bodyID)

def set_quasi_static_intervals_type(bodyID, unit):
    FM_set_quasi_static_intervals_unit(bodyID, unit)

def get_quasi_static_intervals_sec(bodyID):
    return FM_get_quasi_static_intervals_sec(bodyID)

def set_quasi_static_intervals_sec(bodyID, dT2, dT3):
    FM_set_quasi_static_intervals_sec(bodyID, dT2, dT3)

def get_quasi_static_intervals_ts(bodyID, QSmode):
    return FM_get_quasi_static_intervals_ts(bodyID, QSmode)

def set_quasi_static_intervals_ts(bodyID, QSmode, dT2, dT3):
    FM_set_quasi_static_intervals_ts(bodyID, QSmode, dT2, dT3)

LINEAR_LAW = 0
SMOOTH_LAW = 1

def get_quasi_static_law(bodyID):
    return FM_get_quasi_static_law(bodyID)

def set_quasi_static_law(bodyID, law):
    FM_set_quasi_static_law(bodyID, law)

def get_quasi_static_hull_parameters(bodyID):
    return FM_get_quasi_static_hull_params(bodyID)

def set_quasi_static_hull_parameters(bodyID,
        Tz_T1, Tz_r, Rx_T1, Rx_r, Ry_T1, Ry_r):
    FM_set_quasi_static_hull_params(bodyID,
        Tz_T1, Tz_r, Rx_T1, Rx_r, Ry_T1, Ry_r)

def get_quasi_static_foil_parameters(bodyID):
    return FM_get_quasi_static_foil_params(bodyID)

def set_quasi_static_foil_parameters(bodyID, RyRz_T1, RyRz_r, Fy, Fz):
    FM_set_quasi_static_foil_params(bodyID, RyRz_T1, RyRz_r, Fy, Fz)

def get_quasi_static_parameters(bodyID):
    Tz_T1, Tz_r, Rx_T1, Rx_r, Ry_T1, Ry_r = \
            get_quasi_static_hull_parameters(bodyID)
    dT2, dT3 = get_quasi_static_intervals_sec(bodyID)
    law = get_quasi_static_law(bodyID)
    return (Tz_T1, Tz_r, Rx_T1, Rx_r, Ry_T1, Ry_r, dT2, dT3, law)

def set_quasi_static_parameters(bodyID,
        tz0_t1, tz0_r, rx1_t1, rx1_r, ry2_t1, ry2_r, dt2, dt3, static_law_type):
    set_quasi_static_mode(HULL_QS)
    set_quasi_static_intervals_type(bodyID, SECONDS)
    set_quasi_static_intervals_sec(bodyID, dt2, dt3)
    set_quasi_static_law(bodyID, static_law_type)
    set_quasi_static_hull_parameters(bodyID,
        tz0_t1, tz0_r, rx1_t1, rx1_r, ry2_t1, ry2_r)

def set_quasi_static_params(bodyID,
        tz0_t1, tz0_r, rx1_t1, rx1_r, ry2_t1, ry2_r, dt2, dt3, static_law_type):
    set_quasi_static_parameters(bodyID,
        tz0_t1, tz0_r, rx1_t1, rx1_r, ry2_t1, ry2_r, dt2, dt3, static_law_type)

def get_quasi_static_params(bodyID):
    return get_quasi_static_parameters(bodyID)

#
# Synthetic jets
#

# blowing direction types
LOCAL_NORMAL          = 0
AVERAGED_LOCAL_NORMAL = 1
USER_DEFINED          = 2

# blowing kinematic laws
CONSTANT_SPEED  = 1
PULSED_SPEED    = 2
DYNAMIC_LIBRARY = 98

class Jet:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_name(self, name):
        FM_rename_jet(self._name, name)
        self._name = name

    def get_fluid(self):
        return FM_get_jet_fluid(self._name)

    def set_fluid(self, fluid):
        FM_set_jet_fluid(self._name, fluid)

    def get_direction(self):
        return FM_get_jet_direction(self._name)

    def set_direction(self, direction):
        FM_set_jet_direction(self._name, direction)

    def get_direction_vector(self):
        return FM_get_jet_normal(self._name)

    def set_direction_vector(self, x, y, z):
        FM_set_jet_normal(self._name, x, y, z)

    def get_kinematic_law(self):
        return FM_get_jet_kinematic_law(self._name)

    def set_kinematic_law(self, law):
        FM_set_jet_kinematic_law(self._name, law)

    def get_initial_time(self):
        return FM_get_jet_initial_time(self._name)

    def set_initial_time(self, t0):
        FM_set_jet_initial_time(self._name, t0)

    def get_speed(self):
        return FM_get_jet_speed(self._name)

    def set_speed(self, V):
        FM_set_jet_speed(self._name, V)

    def get_pulsation(self):
        return FM_get_jet_pulsation(self._name)

    def set_pulsation(self, w):
        FM_set_jet_pulsation(self._name, w)

    def get_phase(self):
        return FM_get_jet_phase(self._name)

    def set_phase(self, phi0):
        FM_set_jet_phase(self._name, phi0)

def get_number_of_jets():
    return FM_get_number_of_jets()

def get_jet(jet_index):
    jet_name = FM_get_jet_name(jet_index)
    return Jet(jet_name)

def get_jet_by_name(jet_name):
    return Jet(jet_name)

def create_jet(jet_name):
    FM_create_jet(jet_name)
    return Jet(jet_name)

def update_jets():
    FM_update_jets()

# Domhydro launch

def estimate_inertia_data(bodyID, defineZ, zCoG, precision = 1E-20):
    half_body = (get_solved_motion_geometry(bodyID) == 'half')
    flag, cardan1, cardan2, cardan3 = get_solved_motion_cardan_angle(bodyID)
    free_surf_pos = get_initial_interface_position()
    return FM_domhydro(bodyID, half_body, cardan1, cardan2, cardan3,
                       free_surf_pos, defineZ, zCoG, precision)

def estimate_inertia_data_ITTC(bodyID, mass, x_aligned, Lpp, Beam,
                               cx = 0.37, cy = 0.25, cz = 0.25):
    half_body = (get_solved_motion_geometry(bodyID) == 'half')
    return FM_ITTC_inertia(bodyID, half_body, mass, x_aligned, Lpp, Beam, cx, cy, cz)

X = 0
Y = 1
Z = 2
XMINUS = 3
YMINUS = 4
ZMINUS = 5

def get_primary_axis(bodyID):
    return FM_get_body_primary_axis(bodyID)

def set_primary_axis(bodyID, active):
    FM_set_body_primary_axis(bodyID, active)

def get_primary_axis_alignment(bodyID):
    return FM_get_body_primary_axis_alignment(bodyID)

def set_primary_axis_alignment(bodyID, align):
    FM_set_body_primary_axis_alignment(bodyID, align)
