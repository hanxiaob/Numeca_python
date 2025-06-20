#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#--------------------------------------------------------------------------------------------#

import sys,os,math,copy,string

import fnmatch, re ; # regular expressions

import types

from Geom      import *
from IGGSystem import *

from TurboModuleCommands import *
from TurboOutputsCommands import *
from TaskModuleCommands import *


#--------------------------------------------------------------------------------------------#
#				Global query functions					     #
#--------------------------------------------------------------------------------------------#

def is_batch():
    for arg in sys.argv:
        if arg == "-batch":
            return 1
    return 0

#--------------------------------------------------------------------------------------------#
# Fine/Turbo version (i.e 10_1)
#--------------------------------------------------------------------------------------------#
def get_fine_turbo_version ():
    return FT_get_fine_turbo_version()

#--------------------------------------------------------------------------------------------#
# Get version number (i.e: 10.1-2 --> 10,1,2)
#--------------------------------------------------------------------------------------------#
def get_version_number():
    majorVer = 0;
    minorVer = 0;
    patchVer = 0;

    # -------------------------------
    # Get current version
    # Assume format is: x.y[-z[-z1]]
    #   x: major version
    #   y: minor version
    #   z: patch version (optional)
    # -------------------------------
    versionStr = FT_get_fine_turbo_version_number_()

    # Get major version (number before first '.')
    majorVer = int(string.split(versionStr,'.')[0])

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
    if (len(string.split(s,'-'))>1):
        s2 = string.split(s,'-')[1]
        # ... Trim first letter (alpha version for example)
        pattern = re.compile('[a-z]')
        if (pattern.search(s2)):
            index1 = pattern.search(s2).start()
            patchVer = int(s2[0:index1])
        else:
            patchVer = int(s2)

    return majorVer, minorVer, patchVer
#--------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------#
#------------------------------ PROJECT MANAGEMENT ------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# Create project
#--------------------------------------------------------------------------------------------#
def create_project(projectname):
    dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
    basename = os.path.basename(projectname)

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string( "itf_do_new_project \"" + projectname +"\"")
        eval_tcl_string( "global itf_adm; destroy $itf_adm(choose_grid_window)")
    else:
        ## BATCH MODE
        FT_create_new_project(basename,dirname)
        FT_init_computations_position_()
        
#--------------------------------------------------------------------------------------------#
# Open project
#--------------------------------------------------------------------------------------------#
def open_project (projectname):
    dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
    basename = os.path.basename(projectname)
    if not is_batch():
        eval_tcl_string( "itf_do_open_project \"" + projectname + "\"")
    else:
        FT_open_project (basename,dirname)
        FT_init_computations_position_()

    # Update steering data
    FT_computationSteering_createActiveSteeringNamesFine
    FT_computationSteering_saveDataActiveProject

#--------------------------------------------------------------------------------------------#
# Save project
#--------------------------------------------------------------------------------------------#
def save_project():
    # Save current project, without confirmation
    askConfirm = 0
    FT_save_project(askConfirm)

    # Update steering data
    FT_computationSteering_createActiveSteeringNamesFine
    FT_computationSteering_saveDataActiveProject

#--------------------------------------------------------------------------------------------#
# Save As
#--------------------------------------------------------------------------------------------#
def save_project_as(projectname,duplicateResults):
    dirname  = os.path.abspath(os.path.dirname(projectname))+os.sep
    basename = os.path.basename(projectname)
    if not is_batch():
        eval_tcl_string( "global itf_save_as; set itf_save_as(duplicateComputation) "+str(duplicateResults) )
        eval_tcl_string( "itf_do_save_as_new_project2 " + projectname)
    else:
        FT_duplicate_project (basename,dirname,0,duplicateResults)



#--------------------------------------------------------------------------------------------#
#------------------------------ MESH MANAGEMENT ---------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# Mesh selection
#--------------------------------------------------------------------------------------------#
def link_mesh_file (filename,use_config):
    if not is_batch():
        eval_tcl_string( "itf_adm:setIGGFile \"" + filename + "\"")
        eval_tcl_string( "global itf_adm(config_groups); set itf_adm(config_groups) " +str(use_config))
        eval_tcl_string( "itf_adm:config_groups")
        eval_tcl_string("global itf_adm(mesh_units_dialog); destroy $itf_adm(mesh_units_dialog)")
    else:
        FT_set_project_igg_file_name(filename)
        FT_initialize_after_linking_the_mesh(use_config)

#--------------------------------------------------------------------------------------------#
# Mesh file properties
#--------------------------------------------------------------------------------------------#
def get_mesh_file():
    path = FT_get_mesh_path()
    name = FT_get_mesh_name()
    return os.path.join(path,name)
#--------------------------------------------------------------------------------------------#
def get_mesh_path ():
    return FT_get_mesh_path()
#--------------------------------------------------------------------------------------------#
def get_mesh_name ():
    return FT_get_mesh_name()

#--------------------------------------------------------------------------------------------#
# Mesh unit ratio
#--------------------------------------------------------------------------------------------#
METER      = 1.0
CENTIMETER = 0.01
MILLIMETER = 0.001
INCH       = 0.0254
#--------------------------------------------------------------------------------------------#
def get_unit_ratio():
    return FT_get_unit_ratio()
#--------------------------------------------------------------------------------------------#
def set_unit_ratio(ratio):
    if not is_batch():
        ## INTERACTIVE MODE
        ratio_ = "User"
        if ratio == 1:
            ratio_ = "Meters"
        elif ratio == 0.01:
            ratio_= "Centimeters"
        elif ratio == 0.001:
            ratio_= "Millimeters"
        elif ratio == 0.0254:
            ratio_= "Inches"

        eval_tcl_string("global itf_adm; set itf_adm(scale_factor) "+str(ratio))
        eval_tcl_string("global itf_adm; set itf_adm(grid_units) "+ratio_)
        eval_tcl_string("itf_adm:set_unit_ratio" )
    else:
        ## BATCH MODE
        FT_set_unit_ratio(ratio)


#--------------------------------------------------------------------------------------------#
# Mesh viewing
#--------------------------------------------------------------------------------------------#
def view_mesh ():
    if not is_batch():
        eval_tcl_string( "itf_browser:viewMesh")

def unload_mesh ():
    if not is_batch():
        eval_tcl_string( "itf_browser:checkAndUnLoadMesh")





#--------------------------------------------------------------------------------------------#
#------------------------------ COMPUTATIONS MANAGEMENT -------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# New computation
#--------------------------------------------------------------------------------------------#
def new_computation (*args):
    name = ''
    nc = get_nb_computations()

    if len(args)==1:
        # One argument: new computation name
        name=args[0]

        # Check if name already exists
        for i in range( nc ):
            if (get_computation_name(i) == name):
                raise ValueError, "Computation : " + name + ' already exists.'

    if not is_batch():
        eval_tcl_string( "itf_computations:new")
        set_active_computations([nc])
        if name != '':
            # Modify default computation name
            eval_tcl_string( "global itf_adm; set itf_adm(new_computation_name) " + name)
            eval_tcl_string( "itf_adm:do_rename_selected_computation")
    else:
        FT_set_nb_computations(nc+1)

        # Set computation name (ensure it is unique)
        if name == '':
            name = 'new_'+get_computation_name(nc)
            while True:
                found=0
                for i in range( nc ):
                    if (get_computation_name(i) == name):
                        name = 'new_'+name
                        found=1
                        break
                if found==0:
                    break

        FT_set_new_computation_name(nc,name,1)

        # Update steering data
        FT_computationSteering_createActiveSteeringNamesFine
        FT_computationSteering_saveDataActiveProject

    save_selected_computations()

#--------------------------------------------------------------------------------------------#
def set_nb_computations(nb):
    FT_set_nb_computations(nb)

#--------------------------------------------------------------------------------------------#
# Get number of computations
#--------------------------------------------------------------------------------------------#
def get_nb_computations():
    nc = FT_get_nb_computations()
    return nc

#--------------------------------------------------------------------------------------------#
# Get computation name
#--------------------------------------------------------------------------------------------#
def get_computation_name(index):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    rc = FT_get_computation_name(index)
    return rc[0]

#--------------------------------------------------------------------------------------------#
# Get computation filename
#--------------------------------------------------------------------------------------------#
def get_computation_filename(index):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    result = FT_get_computation_filename(index)
    return result

#--------------------------------------------------------------------------------------------#
# Get active computation(s)
#--------------------------------------------------------------------------------------------#
def get_active_computations():
    idxList = []

    nc = FT_get_nb_active_computations()
    if nc<1:
        return idxList

    for i in range (0,nc):
        idx = FT_get_active_computation_index(i)
        idxList.append(idx)

    return idxList

#--------------------------------------------------------------------------------------------#
# Set active computations
#--------------------------------------------------------------------------------------------#
def set_active_computations(indexList):
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_browser:clear_selection ")
        for idx in indexList:
            eval_tcl_string(" itf_browser:set_selected_computation " + str(idx) )
        eval_tcl_string(" itf_browser:select_computation ")
    else:
        ## BATCH MODE
        FT_clear_active_computations()
        for idx in indexList:
            FT_set_active_computations(str(idx))

#--------------------------------------------------------------------------------------------#
# Set computation name
#--------------------------------------------------------------------------------------------#
def set_computation_name(index,name):
    if (index<0 or index>=get_nb_computations()):
        raise IndexError,"Computation index out of bounds : " + str(index)

    # Check if name already exists
    nc = get_nb_computations()
    print "get_nb_computations: ", nc
    for i in range( nc ):
        if (get_computation_name(i) == name):
            raise ValueError, "Computation : " + name + ' already exists.'

    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_rename_selected_computation " + str(index) + " " + name + " " + str(1) )
        eval_tcl_string(" itf_adm:get_computations_names ")
        ##FT_save_project()
    else:
        ## BATCH MODE
        FT_rename_computation(index,name,1)
        ###FT_set_new_computation_name(index,name,1)
        ##FT_save_project()

#--------------------------------------------------------------------------------------------#
# Save selected computation(s)
#--------------------------------------------------------------------------------------------#
def save_selected_computations():
    FT_save_active_computation ()

    # Update steering data
    FT_computationSteering_createActiveSteeringNamesFine()
    FT_computationSteering_saveDataActiveProject()

#--------------------------------------------------------------------------------------------#
# clean selected computation(s)
#--------------------------------------------------------------------------------------------#
def clean_selected_computations( deepDelete ):
    result = FT_clean_active_computations_( deepDelete )
    isOk = result[0]
    if (isOk==0):
        errMess = result[2]
        print 'Warning:'
        print errMess

    # Update steering data
    FT_computationSteering_createActiveSteeringNamesFine
    FT_computationSteering_saveDataActiveProject()


#--------------------------------------------------------------------------------------------#
# Move up/down selected computation(s)
#--------------------------------------------------------------------------------------------#
def move_up_selected_computations():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_computations:move_up_selection ")
    else:
        ## BATCH MODE
        FT_move_up_active_computations_()

#--------------------------------------------------------------------------------------------#
def move_down_selected_computations():
    if not is_batch():
        ## INTERACTIVE MODE
        eval_tcl_string(" itf_computations:move_down_selection ")
    else:
        ## BATCH MODE
        FT_move_down_active_computations_()



#--------------------------------------------------------------------------------------------#
#------------------------------ UNIT SYSTEM -------------------------------------------------#
#--------------------------------------------------------------------------------------------#
UNIT_SI        = 1
UNIT_DEFAULT   = 2
UNIT_BRITISH_1 = 3
UNIT_BRITISH_2 = 4
#--------------------------------------------------------------------------------------------#
def get_quantity_unit_system( quantity_name ):
    return FT_get_quantity_unit_system_(quantity_name)

#--------------------------------------------------------------------------------------------#
def get_quantity_unit_conversion_factor( quantity_name, system_1, system_2 ):
    return FT_get_quantity_unit_conversion_factor_(quantity_name, system_1, system_2)

#--------------------------------------------------------------------------------------------#
def set_unit_system( new_system ):
    FT_change_unit_system_(new_system)

#--------------------------------------------------------------------------------------------#
def set_quantity_unit_system( quantity_name, new_system ):
    FT_change_quantity_unit_system_(quantity_name, new_system)





#--------------------------------------------------------------------------------------------#
#------------------------------ FLUID MODEL -------------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# Fluid selection
#--------------------------------------------------------------------------------------------#
def select_fluid_from_database(fluid_name,fluid_type):
    # sets the specified fluid for all selected (active) computations
    rc = FT_set_last_used_fluid_name(fluid_name,0,fluid_type)
    if rc==-1:
         raise ValueError, "fluid : " + fluid_name + " of type : '" + fluid_type + "' does not exist."

    FT_select_fluid_from_database(fluid_name)

    if (fluid_type == "Incompressible"):
        set_expert_parameter("IRSMCH,I,1,1,0",2)
        ipreco = 1
        set_preconditioning(ipreco)




#--------------------------------------------------------------------------------------------#
# Fluid Properties
#--------------------------------------------------------------------------------------------#
# Specific Heat laws:
CONSTANT_CP_AND_GAMMA    = 10 ; # Perfect/Incompressible gas
CP_T_AND_GAMMA_T_PROFILE = 20 ; # Real gas
CP_T_AND_GAMMA_T_FORMULA = 30 ; # Real gas
CP_T_PROFILE_AND_R       = 21 ; # Real gas
CP_T_FORMULA_AND_R       = 31 ; # Real gas
GAMMA_T_PROFILE_AND_R    = 22 ; # Real gas
GAMMA_T_FORMULA_AND_R    = 32 ; # Real gas
# Heat Conduction laws
CONSTANT_K            = 1 ; # Perfect/Real/Incompressible gas
K_T_PROFILE           = 2 ; # Perfect/Real/Incompressible gas
K_T_FORMULA           = 3 ; # Perfect/Real/Incompressible gas
PRANDTL               = 6 ; # Perfect/Real/Incompressible gas
# Viscosity laws
CONSTANT_VISCOSITY    = 1 ; # Perfect/Real/Incompressible gas
VISCOSITY_T_PROFILE   = 2 ; # Perfect/Real/Incompressible gas
VISCOSITY_T_FORMULA   = 3 ; # Perfect/Real/Incompressible gas
SUTHERLAND            = 4 ; # Perfect/Real gas
# Viscosity types
DYNAMIC_VISCOSITY     = 1
KINEMATIC_VISCOSITY   = 0
# Density laws
BOUSSINESQ            = 0 ; # Incompressible gas
BAROTROPIC_PROFILE    = 1 ; # Incompressible gas
BAROTROPIC_FORMULA    = 2 ; # Incompressible gas
#--------------------------------------------------------------------------------------------#
class FluidProperties:
    def __init__(self,fname,ftype,*args):
        self._name = fname
        self._type = ftype
        nb_args = len(args)
        if (nb_args==1):
            self._specIdx = args[0]
        else:
            self._specIdx = -1
            
    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    # --------------------------------------
    # Laws
    # --------------------------------------
    def get_specific_heat_law(self):
        return FT_get_fluid_params(self._specIdx)[0]
    def get_heat_conduction_law(self):
        return FT_get_fluid_params(self._specIdx)[1]
    def get_viscosity_law(self):
        return FT_get_fluid_params(self._specIdx)[2]
    def get_density_law(self):
        return FT_get_fluid_params(self._specIdx)[3]

    # --------------------------------------
    # Values
    # --------------------------------------
    def get_compressibility(self):
        result =  FT_get_fluid_properties("compressibility", self._specIdx)
        return result

    def get_dilatation(self):
        result =  FT_get_fluid_properties("dilatation", self._specIdx)
        return result

    def get_R_const(self):
        result =  FT_get_fluid_properties("const_r", self._specIdx)
        return result

    def get_Prandtl(self):
        result =  FT_get_fluid_properties("prandtl", self._specIdx)
        return result

    def get_viscosity(self):
        result =  FT_get_fluid_properties("viscosity", self._specIdx)
        return result

    def get_density(self):
        result =  FT_get_fluid_properties("density", self._specIdx)
        return result

    def get_cp(self):
        result =  FT_get_fluid_properties("cp", self._specIdx)
        return result

    def get_gamma(self):
        result =  FT_get_fluid_properties("gamma", self._specIdx)
        return result

    def get_conductivity(self):
        result =  FT_get_fluid_properties("kappa", self._specIdx)
        return result

    def get_thermo_tables_path(self):
        if self.get_type() == "Condensable Gas":
            return FT_get_thermo_tables_dir()
        else:
            print 'Warning: path to thermodynamic tables not defined for '+self.get_type()

    # --------------------------------------
    # Number of species (for "Mixture" fluid)
    # --------------------------------------
    def get_number_of_species(self):
        if self.get_type() == "Mixture":
            return FT_get_fluid_properties("number_of_species", self._specIdx)
        else:
            print 'Warning:  '+self.get_name()+" is not a mixture !"
            return 0

    # --------------------------------------
    # Properties of a species (for "Mixture" fluid)
    # --------------------------------------
    def get_species_properties(self,specIdx):
        if self.get_type() == "Mixture":
            return get_fluid_properties(specIdx)
        else:
            print 'Warning:  '+self.get_name()+" is not a mixture !"
            return None


#--------------------------------------------------------------------------------------------#
def get_fluid_properties(*args):
    nb_args = len(args)
    if (nb_args==0):
        fname   = FT_get_fluid_name()
        ftype   = FT_get_fluid_type()
        specIdx = -1
    else:
        specIdx = args[0]
        fname = FT_get_fluid_name(specIdx)
        ftype = FT_get_fluid_type(specIdx)

    if (ftype == "Perfect gas"):
        ftype = "Perfect Gas"
    if (ftype == "Liquid"):
        ftype = "Incompressible"
    if (ftype == "Condensable Fluid"):
        ftype = "Condensable Gas"

    return FluidProperties(fname,ftype,specIdx)
#--------------------------------------------------------------------------------------------#

def fluid_exists(fluid_name):
    # Check fluid existence
    if FT_fluid_exists(fluid_name):
        return True
    else:
        return False

# db_choice_; // DataBase which will store the fluid (0=Numeca, 1=User)
def add_new_fluid(new_fluid_name,db_choice):
    # Ensure fluid does not already exist
    alreadyExists = fluid_exists(new_fluid_name)
    if alreadyExists==True:
        raise ValueError, "fluid : '" + new_fluid_name + "' already exists."

    FT_add_new_fluid(new_fluid_name,db_choice)
    FT_set_fluid_name(new_fluid_name)
    ftype = FT_get_fluid_type()
    if (ftype == "UNDEFINED"):
        ftype = "Perfect Gas"
    FT_set_fluid_type(ftype)
    FT_select_fluid_from_database(new_fluid_name)



def remove_fluid_from_DB(fluid_name):
    FT_remove_from_DB(fluid_name)


def set_fluid_name(name):
    FT_set_fluid_name(name)

# Perfect Gas, Real Gas, Incompressible, Condensable Gas
def set_fluid_type(type):
    FT_set_fluid_type(type)


def set_fluid_viscosity_law_choice(viscosity):
    FT_set_fluid_visc_law_choice(viscosity)

def set_fluid_conductivity_law_choice(conductivity):
    FT_set_fluid_conductivity_law_choice(conductivity)

def set_fluid_cp_law_choice(cp):
    FT_set_fluid_cp_law_choice(cp)

def set_fluid_density_law_choice(density):
    FT_set_fluid_baro_law_choice(density)

def set_thermo_tables_path(path):
    FT_set_thermo_tables_path(path)


# REFERENCE quantities

def set_fluid_reference_temperature(TRef):
    FT_set_fluid_reference_temperature(TRef)

def set_fluid_reference_pressure(PRef):
    FT_set_fluid_reference_pressure(PRef)

# CONSTANT values

# is_dynamic -> kinematic or dynamic viscosity
def set_fluid_viscosity(is_dynamic,viscosity):
    FT_set_fluid_viscosity(is_dynamic,viscosity)


def set_fluid_heatConductivity(heatConductivity):
    FT_set_fluid_heatConductivity(heatConductivity)

def set_fluid_density(barotropicDensity):
    FT_set_fluid_density(barotropicDensity)

def set_fluid_heatCapacity(heatCapacity):
    FT_set_fluid_heatCapacity(heatCapacity)

def set_fluid_Gamma(Gamma):
    FT_set_fluid_Gamma(Gamma)


def get_fluid_constant_viscosity():
    test = FT_get_fluid_params()[2]
    print "get_viscosity, test is ",test
    if test != 1:
        if test != 4:
            # ... CONSTANT and also SUTHERLAND
            raise ValueError, "viscosity type is not constant"
    result =  FT_get_fluid_properties("viscosity")
    is_dynamic = result[1]
    print "get_fluid_constant_viscosity, is_dynamic: ",is_dynamic
    return result

def get_fluid_constant_density():
    test = FT_get_fluid_params()[3]
    if test != 0:
        raise ValueError, "density type is not constant"
    result =  FT_get_fluid_properties("density")
    return result




# ... CONSTANT_CP_AND_GAMMA = 10

def get_fluid_constant_cp():
    test = FT_get_fluid_params()[0]
    print "get_fluid_constant_cp, test is: ",test
    if test != 10:
        raise ValueError, "Cp type is not constant"
    result =  FT_get_fluid_properties("cp")
    return result

def get_fluid_constant_gamma():
    test = FT_get_fluid_params()[0]
    if test != 10:
        raise ValueError, "Gamma type is not constant"
    result =  FT_get_fluid_properties("gamma")
    return result

def get_fluid_constant_conductivity():
    test = FT_get_fluid_params()[1]
    print "get_conductivity, test is: ",test
    if test != 1:
        if test != 6:
            raise ValueError, "Conductivity type is not constant"
    result =  FT_get_fluid_properties("kappa")
    return result



def set_fluid_Prandtl(Prandtl):
    FT_set_fluid_Prandtl(Prandtl)

def set_fluid_compressibility(compressibility):
    FT_set_fluid_compressibility(compressibility)

def set_fluid_dilatation(dilatation):
    FT_set_fluid_dilatation(dilatation)


# Sutherland law
def set_infinite_temperature(T):
    FT_set_infinite_temperature(T)

def set_Sutherland_temperature(T):
    FT_set_Sutherland_temperature(T)

def set_Sutherland_density(density):
    FT_set_Sutherland_density(density)


def set_R_gas_constant(R):
    FT_set_R_gas_constant(R)

def set_real_gas_model(model):
    FT_set_real_gas_model(model)


def set_reference_temperature_min(T):
    FT_set_reference_temperature_min(T)

def set_reference_temperature_max(T):
    FT_set_reference_temperature_max(T)

def set_reference_pressure_min(P):
    FT_set_reference_pressure_min(P)

def set_reference_pressure_max(P):
    FT_set_reference_pressure_max(P)


### FORMULAE

def set_fluid_viscosity_formula(*args):
    nb_args = len(args)
    if nb_args<8 or nb_args>9:
        raise ValueError," "+str(args)+": 8 or 9 arguments are expected."
    is_dynamic = args[0]
    v1         = args[1]
    v2         = args[2]
    v3         = args[3]
    v4         = args[4]
    v5         = args[5]
    v6         = args[6]
    v7         = args[7]

    if nb_args==8:
        # Backward compatibility
        v8     = 0
    else:
        v8     = args[8]
    
    FT_set_fluid_viscosity_formula(is_dynamic,v1,v2,v3,v4,v5,v6,v7,v8)


def get_fluid_viscosity_formula():
    test = FT_get_fluid_params()[2]
    print "get_fluid_viscosity_formula, test: ",test
    if test != 3:
        raise ValueError, "viscosity type is not formula"
    name = "viscosity"
    result = FT_get_fluid_properties(name)
    last = len(result)-1
    is_dynamic = result[last]
    print "get_fluid_viscosity_formula, is_dynamic: ",is_dynamic
    return result


def set_fluid_heatConductivity_formula(*args):
    nb_args = len(args)
    if nb_args<7 or nb_args>8:
        raise ValueError," "+str(args)+": 7 or 8 arguments are expected."

    hc1         = args[0]
    hc2         = args[1]
    hc3         = args[2]
    hc4         = args[3]
    hc5         = args[4]
    hc6         = args[5]
    hc7         = args[6]

    if nb_args==7:
        # Backward compatibility
        hc8     = 0
    else:
        hc8     = args[7]

    FT_set_fluid_heatConductivity_formula(hc1,hc2,hc3,hc4,hc5,hc6,hc7,hc8)

def get_fluid_heatConductivity_formula():
    test = FT_get_fluid_params()[1]
    if test != 2:
        raise ValueError, "density type is not formula"
    name = "kappa"
    result = FT_get_fluid_properties(name)
    return result



def set_fluid_density_formula(*args):
    nb_args = len(args)
    if nb_args<7 or nb_args>8:
        raise ValueError," "+str(args)+": 7 or 8 arguments are expected."

    d1         = args[0]
    d2         = args[1]
    d3         = args[2]
    d4         = args[3]
    d5         = args[4]
    d6         = args[5]
    d7         = args[6]

    if nb_args==7:
        d8     = 0
    else:
        d8     = args[7]

    FT_set_fluid_density_formula(d1,d2,d3,d4,d5,d6,d7,d8)


def get_fluid_density_formula():
    test = FT_get_fluid_params()[3]
    if test != 2:
        raise ValueError, "density type is not formula"
    name = "density"
    result = FT_get_fluid_properties(name)
    return result



def set_fluid_heatCapacity_formula(*args):
    nb_args = len(args)
    if nb_args<7 or nb_args>8:
        raise ValueError," "+str(args)+": 7 or 8 arguments are expected."

    cp1         = args[0]
    cp2         = args[1]
    cp3         = args[2]
    cp4         = args[3]
    cp5         = args[4]
    cp6         = args[5]
    cp7         = args[6]

    if nb_args==7:
        # Backward compatibility
        cp8 = 0
    else:
        cp8 = args[7]

    FT_set_fluid_heatCapacity_formula(cp1,cp2,cp3,cp4,cp5,cp6,cp7,cp8)


def get_fluid_heatCapacity_formula():
    test = FT_get_fluid_params()[0]
    print "get_fluid_heatCapacity_formula, test is ",test
    if test != 30:
        if test != 31:
            raise ValueError, "heatCapacity type is not formula"
    name = "cp"
    result = FT_get_fluid_properties(name)
    return result



def set_fluid_Gamma_formula(*args):
    nb_args = len(args)
    if nb_args<7 or nb_args>8:
        raise ValueError," "+str(args)+": 7 or 8 arguments are expected."

    g1         = args[0]
    g2         = args[1]
    g3         = args[2]
    g4         = args[3]
    g5         = args[4]
    g6         = args[5]
    g7         = args[6]

    if nb_args==7:
        # Backward compatibility
        g8     = 0
    else:
        g8     = args[7]

    FT_set_fluid_Gamma_formula(g1,g2,g3,g4,g5,g6,g7,g8)


def get_fluid_Gamma_formula():
    test = FT_get_fluid_params()[0]
    print "get_fluid_Gamma_formula, test is ",test
    if test != 30:
        if test != 32:
            raise ValueError, "Gamma type is not formula"
    name = "gamma"
    result = FT_get_fluid_properties(name)
    return result


### PROFILES

def set_fluid_viscosity_profile(is_dynamic,viscosity_profile):
    FT_set_fluid_viscosity_profile(is_dynamic,viscosity_profile)

def get_fluid_viscosity_profile():
    test = FT_get_fluid_params()[2]
    if test != 2:
        raise ValueError, "viscosity type is not profile"
    name = "viscosity"
    result = FT_get_fluid_properties(name)
    last = len(result)-1
    is_dynamic = result[last]
    print "get_fluid_viscosity_profile, is_dynamic: ",is_dynamic
    return result


def set_fluid_heatConductivity_profile(heatConductivity_profile):
    FT_set_fluid_heatConductivity_profile(heatConductivity_profile)

def get_fluid_heatConductivity_profile():
    test = FT_get_fluid_params()[1]
    if test != 2:
        raise ValueError, "heatConductivity type is not profile"
    name = "kappa"
    result = FT_get_fluid_properties(name)
    return result



def set_fluid_density_profile(density_profile):
    FT_set_fluid_density_profile(density_profile)

def get_fluid_density_profile():
    test = FT_get_fluid_params()[3]
    if test != 2:
        raise ValueError, "density type is not profile"
    name = "density"
    result = FT_get_fluid_properties(name)
    return result


def set_fluid_heatCapacity_profile(heatCapacity_profile):
    FT_set_fluid_heatCapacity_profile(heatCapacity_profile)


def get_fluid_heatCapacity_profile():
    test = FT_get_fluid_params()[0]
    if test != 20:
        if test != 21:
            raise ValueError, "heatCapacity type is not profile"
    name = "cp"
    result = FT_get_fluid_properties(name)
    return result


def set_fluid_Gamma_profile(Gamma_profile):
    FT_set_fluid_Gamma_profile(Gamma_profile)

def get_fluid_Gamma_profile():
    test = FT_get_fluid_params()[0]
    if test != 20:
        if test != 22:
            raise ValueError, "Gamma type is not profile"
    name = "gamma"
    result = FT_get_fluid_properties(name)
    return result


#--------------------------------------------------------------------------------------------#
#				Set configuration functions	         		     #
#--------------------------------------------------------------------------------------------#

def set_cyl_cart_configuration (cyl_or_cart):
    FT_set_cyl_cart(cyl_or_cart)

#--------------------------------------------------------------------------------------------#
def set_space_configuration (I2D,AXISYM,AXIDX,AXIDY,AXIDZ,IINT):
    FT_set_configuration (I2D,AXISYM,AXIDX,AXIDY,AXIDZ,IINT)




#--------------------------------------------------------------------------------------------#
#------------------------------ FLOW MODEL --------------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# TIME CONFIGURATION (Steady/Unsteady)             in 2015 added HARMONIC configuration
#--------------------------------------------------------------------------------------------#
STEADY   = 0
UNSTEADY = 1
HARMONIC = 2
#--------------------------------------------------------------------------------------------#
def get_time_configuration ():
    return FT_get_unsteady_type ()
#--------------------------------------------------------------------------------------------#
def set_time_configuration (val):
    if val == STEADY or val == UNSTEADY or val == HARMONIC:
        FT_set_unsteady_type (val)
        # Adapt boundary conditions
        if (val == STEADY):
            FT_update_conditional_boundary_conditions(1)
            FT_update_conditional_boundary_conditions(8)
        elif (val == UNSTEADY):
            FT_update_conditional_boundary_conditions(0)
            FT_update_conditional_boundary_conditions(8)
        elif (val == HARMONIC):
            FT_update_conditional_boundary_conditions(6)
            FT_update_conditional_boundary_conditions(11)

        if not is_batch():
            # INTERACTIVE MODE
            # ... to update parameter tree in case of harmonics
            eval_tcl_string( "itf_adm:update_browser_tree_entries")
            
    else:
        raise ValueError, "'val' should be 0 or 1 or 2"


#--------------------------------------------------------------------------------------------#
# MATHEMATICAL MODEL = [INSEUL,ITURB,MTETUR]
#--------------------------------------------------------------------------------------------#
EULER                              = [0,0,0]
LAMINAR                            = [1,0,0]
BALDWIN_LOMAX                      = [1,1,0]
SPALART_ALLMARAS                   = [1,3,0]
SPALART_ALLMARAS_EXT_WALL_FUNCTION = [1,3,1]
K_EPS_LOW_RE_CHIEN                 = [1,2,101]
K_EPS_EXT_WALL_FUNCTION            = [1,2,102]
K_EPS_LOW_RE_LAUNDER_SHARMA        = [1,2,103]
K_EPS_LOW_RE_YANG_SHIH             = [1,2,104]
V2_F                               = [1,2,301]
SST                                = [1,2,401]
K_OMEGA_WILCOX                     = [1,2,402]
SST_EXT_WALL_FUNCTION              = [1,2,403]
EARSM                              = [1,2,411]
EARSM_EXT_WALL_FUNCTION            = [1,2,413]
#--------------------------------------------------------------------------------------------#
def get_mathematical_model():
    inseul,iturb,mtetur = FT_get_equation()
    return [inseul,iturb,mtetur]
#--------------------------------------------------------------------------------------------#
def set_mathematical_model (model):
    inseul    = model[0]
    iturb     = model[1]
    mtetur    = model[2]
    FT_set_equation (inseul, iturb, mtetur)

#--------------------------------------------------------------------------------------------#
# GRAVITY
#--------------------------------------------------------------------------------------------#
def get_gravity_flag():
    IPRECO, IROVAR, ICONAT, ICOVIC = FT_get_preconditionning_parameters()
    return ICONAT
#--------------------------------------------------------------------------------------------#
def set_gravity_flag(flag):
    FT_set_gravity_flag(flag)
#--------------------------------------------------------------------------------------------#
def get_gravity_vector():
    gx, gy, gz = FT_get_gravity_vector()
    return Vector(gx, gy, gz)
#--------------------------------------------------------------------------------------------#
def set_gravity_vector(g):
    if (type(g) is types.InstanceType) and isinstance(g,Vector):
        FT_set_gravity_vector(g.x, g.y, g.z)
    else:
        raise TypeError," "+str(g)+": argument must be an instance of Vector."

#--------------------------------------------------------------------------------------------#
# PRECONDITIONING
#--------------------------------------------------------------------------------------------#
def get_preconditioning():
    IPRECO, IROVAR, ICONAT, ICOVIC = FT_get_preconditionning_parameters();
    return IPRECO
#--------------------------------------------------------------------------------------------#
def set_preconditioning(ipreco):
    FT_set_preconditioning(ipreco)

#--------------------------------------------------------------------------------------------#
# TRACERS
#--------------------------------------------------------------------------------------------#
def get_tracer():
    n = FT_get_tracer()
    return n
#--------------------------------------------------------------------------------------------#
def set_tracer(nb):
    FT_set_tracer(nb)

#--------------------------------------------------------------------------------------------#
# REFERENCE PARAMETERS
#--------------------------------------------------------------------------------------------#
def get_reference_length ():
    return FT_get_reference_length ()
#--------------------------------------------------------------------------------------------#
def set_reference_length (L):
    FT_set_reference_length (L)
#--------------------------------------------------------------------------------------------#
def get_reference_velocity ():
    return FT_get_reference_speed ()
#--------------------------------------------------------------------------------------------#
def set_reference_velocity (V):
    FT_set_reference_speed (V)
#--------------------------------------------------------------------------------------------#
def get_reference_density ():
    return FT_get_reference_density ()
#--------------------------------------------------------------------------------------------#
def set_reference_density (RHO):
    FT_set_reference_density (RHO)
#--------------------------------------------------------------------------------------------#
def get_reference_temperature ():
    return FT_get_reference_temperature ()
#--------------------------------------------------------------------------------------------#
def set_reference_temperature (T):
    FT_set_reference_temperature (T)
#--------------------------------------------------------------------------------------------#
def get_reference_pressure ():
    return FT_get_reference_pressure ()
#--------------------------------------------------------------------------------------------#
def set_reference_pressure (P):
    FT_set_reference_pressure (P)
#--------------------------------------------------------------------------------------------#
def get_reynolds_number():
    return FT_get_reynolds ()
#--------------------------------------------------------------------------------------------#
def set_reynolds_number (Re):
    FT_set_reynolds (Re)




#--------------------------------------------------------------------------------------------#
#------------------------------ ROTATING MACHINERY  -----------------------------------------#
#--------------------------------------------------------------------------------------------#

# ---
# Get/Set phase lagged flag
# ---
def get_phase_lagged():
    return FT_get_phase_lagged()[0]

def set_phase_lagged(flag):
        if ( flag==0 or flag==1 ):

            iDomScal = 0
            nbRS = get_nb_bc_groups("ROTOR-STATOR")
            if (get_time_configuration()==UNSTEADY and nbRS>0 and flag==0):
                iDomScal = 1
            FT_set_phase_lagged(flag, iDomScal)

            if (flag == 1):
                FT_update_conditional_boundary_conditions(5)
            else:
                FT_update_conditional_boundary_conditions(4)

        else:
            raise ValueError, "Unexpected value: "+str(flag)+" for 1st argument. Must be 0 or 1"

#--------------------------------------------------------------------------------------------#
# Rotating blocks group
#--------------------------------------------------------------------------------------------#
DIR_I = 1
DIR_J = 2
DIR_K = 3
#--------------------------------------------------------------------------------------------#
class RotatingBlockGroup:
    def __init__(self,blockGroupID):
        self._blockGroupID = blockGroupID

    def get_group_name(self):
        return FT_get_rot_group_name(self._blockGroupID)

    def get_nb_blocks(self):
        return FT_get_rot_group_nb_blocks(self._blockGroupID)

    def get_block_index(self,idx):
        if (idx<0 or idx>=self.get_nb_blocks()):
            raise ValueError, "Index out of bound : " + str(idx)
        else:
            blockIdx = FT_get_rot_group_block_index(self._blockGroupID,idx)
            return blockIdx

    # ---
    # Get/Set streamwise dir
    # ---
    def get_streamwise_direction(self):
        return FT_get_rot_block_parameters(self._blockGroupID)[0]
    def set_streamwise_direction(self,dir):
        if ( dir==DIR_I or dir!=DIR_J or dir!=DIR_K ):
            nblade = FT_get_rot_block_nb_blade(self._blockGroupID)
            result = FT_get_rot_block_parameters(self._blockGroupID)
            FT_set_rot_block_parameters(self._blockGroupID,nblade,dir,result[1],result[2],result[3],result[4])
        else:
            raise ValueError, "Unexpected value: "+str(dir)+" for 1st argument. Must be 1(=dirI), 2(=DIR_J) or 3(=DIR_J)"

    # ---
    # Get/Set spanwise dir
    # ---
    def get_spanwise_direction(self):
        return FT_get_rot_block_parameters(self._blockGroupID)[1]
    def set_spanwise_direction(self,dir):
        if ( dir==DIR_I or dir!=DIR_J or dir!=DIR_K ):
            nblade = FT_get_rot_block_nb_blade(self._blockGroupID)
            result = FT_get_rot_block_parameters(self._blockGroupID)
            FT_set_rot_block_parameters(self._blockGroupID,nblade,result[0],dir,result[2],result[3],result[4])
        else:
            raise ValueError, "Unexpected value: "+str(dir)+" for 1st argument. Must be 1(=dirI), 2(=DIR_J) or 3(=DIR_J)"

    # ---
    # Get/Set azimuthal dir
    # ---
    def get_azimuthal_direction(self):
        return FT_get_rot_block_parameters(self._blockGroupID)[2]
    def set_azimuthal_direction(self,dir):
        if ( dir==DIR_I or dir!=DIR_J or dir!=DIR_K ):
            nblade = FT_get_rot_block_nb_blade(self._blockGroupID)
            result = FT_get_rot_block_parameters(self._blockGroupID)
            FT_set_rot_block_parameters(self._blockGroupID,nblade,result[0],result[1],dir,result[3],result[4])
        else:
            raise ValueError, "Unexpected value: "+str(dir)+" for 1st argument. Must be 1(=dirI), 2(=DIR_J) or 3(=DIR_J)"

    # ---
    # Get/Set rotational speed
    # ---
    def get_rotational_speed(self):
        return FT_get_rot_block_parameters(self._blockGroupID)[3]
    def set_rotational_speed(self,speed):
        nblade = FT_get_rot_block_nb_blade(self._blockGroupID)
        result = FT_get_rot_block_parameters(self._blockGroupID)
        FT_set_rot_block_parameters(self._blockGroupID,nblade,result[0],result[1],result[2],speed,result[4])


#--------------------------------------------------------------------------------------------#
def get_nb_rotating_block_groups():
    return  FT_get_nb_blockGroups()

#--------------------------------------------------------------------------------------------#
def get_rotating_block_group(arg):
    if (type(arg) is types.IntType):
        groupIndex=arg
        return RotatingBlockGroup(groupIndex)
    elif (type(arg) is types.StringType):
        groupName=arg
        groupIndex = FT_get_rot_group_index(groupName)
        if (groupIndex == -1):
            raise ValueError," Rotating block group '"+arg+"' cannot be found !"
        else:
            return RotatingBlockGroup(groupIndex)

#--------------------------------------------------------------------------------------------#
# Rotating blocks Grouping/Ungrouping
#--------------------------------------------------------------------------------------------#
def create_rotating_block_group(name,value):
    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to group
        blocks_list = value
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        blocks_list = get_blocks_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    for block in blocks_list:
        FT_group_block(name,block)
    FT_update_rot_blocks_groups()


#--------------------------------------------------------------------------------------------#
def ungroup_rotating_block_group(arg):
    if (type(arg) is types.IntType):
        groupIndex=arg
        FT_ungroup_rot_blocks(groupIndex)
        FT_update_rot_blocks_groups()
    elif (type(arg) is types.StringType):
        groupName=arg
        groupIndex = FT_get_rot_group_index(groupName)
        FT_ungroup_rot_blocks(groupIndex)
        FT_update_rot_blocks_groups()


###--------------------------------------------------------------------------------------------#
##def get_rotating_machinery_parameters(groupIndex):
##    axi_dir,rad_dir,azi_dir,speed,lagged = FT_get_rot_block_parameters(groupIndex)
##    return axi_dir,rad_dir,azi_dir,speed,lagged

###--------------------------------------------------------------------------------------------#
##def set_rotating_machinery_parameters(groupIndex,nb_blade,axi_dir,rad_dir,azi_dir,speed,lagged):
##    FT_save_rot_block_parameters(groupIndex,nb_blade,axi_dir,rad_dir,azi_dir,speed,lagged)


###--------------------------------------------------------------------------------------------#
##def set_rotating_machinery_block_speed(groupIndex,speed):
##    print "save_rot_block_speed start"
##    nb = FT_get_nb_blockGroups()
###    print groupIndex
###    print speed
##    if (0<groupIndex <0 or groupIndex >= FT_get_nb_blockGroups()):
##        raise IndexError,"Block group index out of bounds : " + str(groupIndex)
##    print "save_rot_block_speed 2"
##    FT_save_rot_block_speed(groupIndex,speed)
##    print "save_rot_block_speed end"





#--------------------------------------------------------------------------------------------#
#------------------------------ BOUNDARY CONDITIONS -----------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# BC Group
#--------------------------------------------------------------------------------------------#
class BCGroup:
    def __init__(self,BCType,index):
        self._BCType = BCType
        self._index  = index

    def get_type(self):
        return self._BCType

    def get_index(self):
        return self._index

    def get_bc_type(self):
        bc_id,bc_opsel = FT_get_bc_values(self._index,self._BCType)
        return [bc_id,bc_opsel]

    def set_bc_type(self,value):
        print "set_bc_type: ", value
        bc_id    = value[0]
        bc_opsel = value[1]
        print "bc_id: ", bc_id
        print "bc_opsel: ", bc_opsel
        FT_set_bc_values(self._index,self._BCType,bc_id,bc_opsel)

    def get_group_name(self):
        return FT_get_group_name(self._index,self._BCType)

    def get_nb_patches(self):
        return FT_get_nb_patches(self._index,self._BCType)

    def get_patch(self,idx):
        if (idx<0 or idx>=self.get_nb_patches()):
            raise ValueError, "Index out of bound : " + str(idx)
        else:
            b,f,p =  FT_get_group_patch(self._index,idx,self._BCType)
            return get_bc_patch(b,f,p)

    def get_patches_names(self):
        return FT_get_patches_names(self._index,self._BCType)

    def ungroup(self):
        FT_ungroup_patches(self._BCType,self._index)

    def get_parameter_value(self,name):
        value = FT_get_bc_parameter_value(self._index,self._BCType,name)
        if value!=None:
            return value
        else:
            raise ValueError, "Could not find parameter : " + name + " for patch " + str(self.get_group_name())

    def set_parameter_value(self,name,value):
        # Set value according to its type
        value_type=""
        if (type(value) is types.IntType):
            FT_set_bc_parameter_value(self._index,self._BCType,name,"INTEGER",value)
        elif (type(value) is types.FloatType):
            FT_set_bc_parameter_value(self._index,self._BCType,name,"REAL",value)

        elif (type(value) is types.TupleType) or (type(value) is types.ListType):
            if (type(value[0]) is types.TupleType) or (type(value[0]) is types.ListType):
                # Backward : set dummy interpolation type that will be ignored
                FT_set_bc_parameter_value(self._index,self._BCType,name,"PROFILE",-1,len(value),value)
            else:
                if (len(value)==2 and (type(value[1]) is types.TupleType or type(value[1]) is types.ListType)):
                    FT_set_bc_parameter_value(self._index,self._BCType,name,"PROFILE",value[0],len(value[1]),value[1])
                else:
                    FT_set_bc_parameter_value(self._index,self._BCType,name,"VECTOR",value)
        elif (type(value) is types.InstanceType) and isinstance(value,Vector):
                FT_set_bc_parameter_value(self._index,self._BCType,name,"VECTOR",[value.x,value.y,value.z])
        elif (type(value) is types.InstanceType) and isinstance(value,Point):
                FT_set_bc_parameter_value(self._index,self._BCType,name,"VECTOR",[value.x,value.y,value.z])
        else:
            # WRONG TYPE FOR 'value'
            raise ValueError, "Wrong type : " + str(type(value)) + " for parameter name " + name

    def set_acoustic_impedance_value (self,ind,freq,re,im):
        name = self.get_group_name()
        print "set_acoustic_impedance_value, name is: ",name
        FT_set_acoustic_impedance_value (self._BCType,name,ind,freq,re,im)



    def get_acoustic_impedance_value (self,ind):
        bc_patch = self.get_patch(0)
        patch = bc_patch.get_block_face_patch()

        print "get_acoustic_impedance_value, patch is: ",patch

        b = patch[0]
        f = patch[1]
        p = patch[2]

        test = get_acoustic_impedance_number_of_frequencies(b-1,f-1,p-1)
        print "get_acoustic_impedance_value, test is: ",test
        if (ind<0 or ind>=test):
            raise ValueError, "Index out of bound : " + str(ind)
        else:
            result = FT_get_acoustic_impedance_value (b,f,p,ind)
            freq = result[0]
            re   = result[1]
            im   = result[2]
            return result



    def set_bc_profile_from_file(self,name,type,file):
        FT_set_bc_profile(self._index,self._BCType,name,type,file)

    def get_force_and_torque(self):
        return FT_get_bc_force_and_torque(self._index,self._BCType)

    def set_force_and_torque(self,value):
        FT_set_bc_force_and_torque(self._index,self._BCType,value)

#--------------------------------------------------------------------------------------------#
def get_bc_group(*args):
    if len(args)==1:
        # One argument: BCPatch type expected
        value=args[0]
        if (type(value) is types.InstanceType) and isinstance(value,BCPatch):
            # Get group containing the BCPatch
            bcPatch = value
            BCType = bcPatch.get_bc_name()
            b,f,p  = bcPatch.get_block_face_patch()
            index  = FT_get_bc_group_index_by_bfp(BCType,b,f,p)
            if (index < 0):
                raise ValueError, "BC patch with indices: ("+str(b-1)+","+str(f-1)+","+str(p-1)+") cannot be found in "+BCType+" list."
            else:
                return BCGroup(BCType,index)
    elif len(args)==2:
        # Two arguments: (BCType,groupIndex) or (BCType,groupName) expected
        BCType=args[0]
        if ( not (type(BCType) is types.StringType) ):
            raise TypeError," "+str(BCType)+": 1st argument must be a string."

        value =args[1]
        if ( type(value) is types.IntType ):
            # Get group by index
            index = value
            return BCGroup(BCType,index)
        elif ( type(value) is types.StringType ):
            # Get group by name
            name = value
            index = FT_get_bc_group_index_by_name(BCType,name)
            if (index < 0):
                raise ValueError, "BC group with name: " +name+ " cannot be found!"
            else:
                return BCGroup(BCType,index)
        else:
            raise TypeError," "+str(value)+": 2nd argument must be an integer or a string."
    else:
        raise ValueError," "+str(args)+": 1 or 2 arguments are expected."

#--------------------------------------------------------------------------------------------#
def get_bc_group_by_name(BCType,name):
    index = FT_get_bc_group_index_by_name(BCType,name)
    if (index < 0):
        raise ValueError, "BC Group: " + name + ' not found!'
    else:
        return BCGroup(BCType,index)

#--------------------------------------------------------------------------------------------#
def get_nb_bc_groups (type):
    return FT_get_nb_bc_groups(type)



#--------------------------------------------------------------------------------------------#
# BC Patch
#--------------------------------------------------------------------------------------------#
class BCPatch:
    def __init__(self,blockID,faceID,patchID):
        self._blockID    = blockID
        self._faceID     = faceID
        self._patchID    = patchID

    def get_bc_name(self):
        return FT_get_bc_name(self._blockID,self._faceID,self._patchID)

    def get_patch_name(self):
        return FT_get_patch_name(self._blockID,self._faceID,self._patchID)

    def get_block_face_patch(self):
        return self._blockID, self._faceID, self._patchID



#--------------------------------------------------------------------------------------------#
def get_bc_patch(blockID,faceID,patchID):
    return BCPatch(blockID+1,faceID+1,patchID+1)

#--------------------------------------------------------------------------------------------#
def get_bc_patch_by_name(BCType, name):
    b,f,p = FT_get_bc_patch_by_name(BCType, name)
    return get_bc_patch(b,f,p)

#--------------------------------------------------------------------------------------------#
def get_bc_patch_by_index(BCType, index):
    b,f,p = FT_get_bc_patch_by_index(BCType, index)
    return get_bc_patch(b,f,p)

#--------------------------------------------------------------------------------------------#
def get_nb_bc_patches (type):
    return FT_get_nb_bc_patches(type)



#--------------------------------------------------------------------------------------------#
# Copy b.c from group ref_index to indexList
#--------------------------------------------------------------------------------------------#
def apply_bc_to_the_group(BCType,ref_index,indexList):
    FT_apply_bc_to_the_group(len(indexList),BCType,ref_index,indexList)

def change_type_for_all_RS(value):
    bc_id    = value[0]
    bc_opsel = value[1]
    FT_change_type_for_all_RS(bc_id,bc_opsel)


## ........................................................................................
##                                          B.C Types
## ........................................................................................
## BC_NAME                                                                         [id,opsel]
## ........................................................................................

## ... INLETs
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION                                   = [124, 1]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION_V_EXTRAPOLATED                    = [124, 2]
SUBSONIC_CYLINDRICAL_TOTAL_ENTHALPY_DRYNESS_FRACTION_CONDENSABLE_GAS_ANGLE        = [124,22]
SUBSONIC_CYLINDRICAL_TOTAL_ENTHALPY_DRYNESS_FRACTION_CONDENSABLE_GAS_VELOCITY     = [124,24]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_AXIAL_DIRECTION_VZ_EXTRAPOLATED                   = [124, 3]
SUBSONIC_CYLINDRICAL_VELOCITY_DIRECTION_V_EXTRAPOLATED                            = [124, 4]
SUBSONIC_CYLINDRICAL_TANGENTIAL_VELOCITY_AND_MERIDIONAL_ANGLE_VM_EXTRAPOLATED     = [124, 8]
SUBSONIC_CYLINDRICAL_FLOW_ANGLE_AND_TOTAL_COND_UPSTREAM_ROT_FRAME_VM_EXTRAPOLATED = [124, 9]
SUBSONIC_CYLINDRICAL_ANGLE_FROM_MERIDIONAL_DIRECTION_STATIC_PRESSURE_EXTRAPOLATED = [124, 5]
SUBSONIC_CYLINDRICAL_VELOCITY_COMPONENTS_STATIC_PRESSURE_EXTRAPOLATED             = [124, 7]
SUBSONIC_CYLINDRICAL_STATIC_QUANTITIES_DISTRIBUTION_HARMONIC                      = [324, 4]
SUBSONIC_CYLINDRICAL_FROM_ROTOR_STATOR                                            = [ 49, 1]
SUBSONIC_CARTESIAN_STATIC_PRESSURE_EXTRAPOLATED                                   = [ 24, 1]
SUBSONIC_CARTESIAN_MACH_NUMBER_EXTRAPOLATED                                       = [ 24, 2]
SUBSONIC_CARTESIAN_MAGNITUDE_OF_ABSOLUTE_VELOCITY_EXTRAPOLATED                    = [ 24, 3]
SUPERSONIC_CARTESIAN_VELOCITY_COMPONENTS_IMPOSED                                  = [ 23, 0]
SUPERSONIC_CYLINDRICAL_TOTAL_QUANTITIES_VELOCITY_COMPONENTS_IMPOSED               = [ 23, 1]
SUPERSONIC_CYLINDRICAL_STATIC_QUANTITIES_VELOCITY_COMPONENTS_IMPOSED              = [ 23, 2]
SUBSONIC_CYLINDRICAL_MERIDIONAL_FLOW_ANGLE_AND_TANGENTIAL_VELOCITY                = [ 28, 1]
SUBSONIC_CYLINDRICAL_VELOCITY_DIRECTION                                           = [ 28, 2]
SUBSONIC_CARTESIAN_VELOCITY_DIRECTION                                             = [ 28, 3]

## ... OUTLETs
SUBSONIC_STATIC_PRESSURE_IMPOSED                                                  = [ 25,10]
SUBSONIC_AVERAGED_STATIC_PRESSURE                                                 = [ 27,40]
SUBSONIC_RADIAL_EQUILIBRIUM                                                       = [125,10]
SUPERSONIC_EXTRAPOLATION                                                          = [ 22, 0]
SUBSONIC_VELOCITY_SCALING                                                         = [ 27,20]
SUBSONIC_PRESSURE_ADAPTATION                                                      = [ 27,30]
SUBSONIC_ABSOLUTE_MACH_NUMBER_WITH_PRESSURE_ADAPTATION                            = [ 27,50]
SUBSONIC_RELATIVE_MACH_NUMBER_WITH_PRESSURE_ADAPTATION                            = [ 27,60]
SUBSONIC_RIEMANN_INVARIANT                                                        = [ 29, 1]
SUBSONIC_FROM_ROTOR_STATOR                                                        = [ 49, 2]
SUBSONIC_MASSFLOW_PRESSURE_ADAPTATION                                             = [ 27, 30]

## ... SOLIDs
NS_CYLINDRICAL_ADIABATIC_CONSTANT_ROTATION_SPEED                                  = [113, 0]
EULER_EULER_SOLID_WALL                                                            = [ 16, 0]
NS_CYLINDRICAL_ADIABATIC_AREA_DEFINED_ROTATION_SPEED                              = [113, 1]
NS_CYLINDRICAL_HEAT_FLUX_IMPOSED_CONSTANT_ROTATION_SPEED                          = [110, 0]
NS_CYLINDRICAL_HEAT_FLUX_IMPOSED_AREA_DEFINED_ROTATION_SPEED                      = [110, 1]
NS_CYLINDRICAL_TEMPERATURE_IMPOSED_CONSTANT_ROTATION_SPEED                        = [114, 0]
NS_CYLINDRICAL_TEMPERATURE_IMPOSED_AREA_DEFINED_ROTATION_SPEED                    = [114, 1]
NS_CARTESIAN_ADIABATIC                                                            = [ 13, 0]
NS_CARTESIAN_HEAT_FLUX_IMPOSED                                                    = [ 10, 0]
NS_CARTESIAN_TEMPERATURE_IMPOSED                                                  = [ 14, 0]
NS_CYLINDRICAL_CHT_CONNECTION_CONSTANT_ROTATION_SPEED                             = [114, 20]
NS_CYLINDRICAL_ROTATION_SPEED_ACOUSTIC_IMPEDANCE                                  = [113, 2]
NS_CARTESIAN_ACOUSTIC_IMPEDANCE                                                   = [13, 2]
EULER_ACOUSTIC_IMPEDANCE                                                          = [16, 2]

## ... EXTERNALs
EXTERNAL_STATIC_QUANTITIES                                                        = [ 21, 1]
EXTERNAL_CONSTANT_WIND_INCIDENCE_RELATIVE_Z                                       = [ 21, 2]

## ... ROTOR-STATORs
RS_CONSERVATIVE_COUPLING_PITCHWISE_ROW                                            = [ 43, 1]
RS_LOCAL_CONSERVATIVE_COUPLING                                                    = [ 44, 1]
RS_FULL_NON_MATCHING_MIXING_PLANE                                                 = [ 45, 1]
RS_FULL_NON_MATCHING_FROZEN_ROTOR                                                 = [ 46, 1]
RS_NON_REFLECTING_1D                                                              = [ 48, 1]
RS_NON_REFLECTING_2D                                                              = [ 48, 2]
RS_DOMAIN_SCALING                                                                 = [ 47, 1]
RS_PHASE_LAGGED                                                                   = [ 47, 2]

## ... PERIODICs
ROTATION_PERIODICITY                                                              = [  2,-1]
TRANSLATION_PERIODICITY                                                           = [  3,-1]
ROTATION_PERIODICITY_2D_NON_MATCHING                                              = [  8,-1]
TRANSLATION_PERIODICITY_2D_NON_MATCHING                                           = [  9,-1]

#--------------------------------------------------------------------------------------------#
# WALL TYPES
#--------------------------------------------------------------------------------------------#
SMOOTH = 1
ROUGH  = 2

#--------------------------------------------------------------------------------------------#
# PROFILE: INTERPOLATION TYPES
#--------------------------------------------------------------------------------------------#
## ... 1D
INTERPOLATION_1D_ALONG_X           =  1
INTERPOLATION_1D_ALONG_Y           =  2
INTERPOLATION_1D_ALONG_Z           =  3
INTERPOLATION_1D_ALONG_R           =  4
INTERPOLATION_1D_ALONG_THETA       =  5
## ... 2D
INTERPOLATION_2D_ALONG_X_Y         = 51
INTERPOLATION_2D_ALONG_X_Z         = 52
INTERPOLATION_2D_ALONG_Y_Z         = 53
INTERPOLATION_2D_ALONG_R_THETA     = 54
INTERPOLATION_2D_ALONG_R_Z         = 55
INTERPOLATION_2D_ALONG_THETA_Z     = 56

#--------------------------------------------------------------------------------------------#
#--- BC patch grouping
#--------------------------------------------------------------------------------------------#
def get_nb_faces(b):
    return FT_get_nb_faces(b)

def get_nb_patches_by_block(b,f):
    return FT_get_nb_patches_by_block(b,f)

def get_bc_group_name (index,type):
    result = FT_get_bc_group_name(index,type)
    print "get_bc_group_name, index is: ",index,", type is: ", type, ", result is: ",result
    return result

#--------------------------------------------------------------------------------------------#
def get_bc_patch_list(pattern):
    patch_list = []
    regexp = fnmatch.translate(pattern) ; # convert pattern to regular expression
    reobj = re.compile(regexp)
    for b in range( get_nb_blocks() ):
        for f in range( get_nb_faces(b) ):
            for p in range( get_nb_patches_by_block(b,f) ):
                patch =  get_bc_patch(b,f,p)
                if (reobj.match(patch.get_patch_name())):
                    patch_list.append(patch)
    return patch_list

#--------------------------------------------------------------------------------------------#
def create_BC_group(name,value):
    print "create_BC_group, name: ",name," value: ",value
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
        b,f,p = bc_patch.get_block_face_patch()
        patchList.append([b,f,p])
    FT_group_patches(name,len(patchList),patchList)
    print "create_BC_group END"


#--------------------------------------------------------------------------------------------#

def ungroup_BC_patches (bc_type,group_name):
    bcGroup = get_bc_group_by_name(bc_type,group_name)
    FT_ungroup_patches(bcGroup.get_type(),bcGroup.get_index())





#--------------------------------------------------------------------------------------------#
#------------------------------ NUMERICAL MODEL ---------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# CFL
#--------------------------------------------------------------------------------------------#
def get_CFL_number():
    return FT_get_CFL()
#--------------------------------------------------------------------------------------------#
def set_CFL_number(CFL):
    FT_set_CFL(CFL)

#--------------------------------------------------------------------------------------------#
# MULTIGRID
#--------------------------------------------------------------------------------------------#
def get_current_grid_level():
    return FT_get_current_grid_level()
#--------------------------------------------------------------------------------------------#
def set_current_grid_level(i,j,k):
    FT_set_current_grid_level(i,j,k)
#--------------------------------------------------------------------------------------------#
def get_MG_level_number():
    return FT_get_number_of_grid()
#--------------------------------------------------------------------------------------------#
def set_MG_level_number(ngrid):
    FT_set_number_of_grid(ngrid)
#--------------------------------------------------------------------------------------------#
def get_MG_flag():
    return FT_get_full_multigrid()
#--------------------------------------------------------------------------------------------#
def set_MG_flag(fmg):
    FT_set_full_multigrid(fmg)

#--------------------------------------------------------------------------------------------#
# FULL MULTIGRID parameters
#--------------------------------------------------------------------------------------------#
def get_MG_sweeps_definition():
    return FT_get_sweeps_definition()
#--------------------------------------------------------------------------------------------#
def set_MG_sweeps_definition(val):
    FT_set_sweeps_definition(val)

    if val == 0:
        set_MG_number_of_sweeps(1,2,3,4,5,6,7,8,9,10)
    if val == 1:
        nb_grid = get_MG_level_number()
        if nb_grid == 1:
            set_MG_number_of_sweeps(1,2,3,4,5,6,7,8,9,10)
        if nb_grid == 2:
            set_MG_number_of_sweeps(1,4,3,4,5,6,7,8,9,10)
        if nb_grid == 3:
            set_MG_number_of_sweeps(1,2,16,4,5,6,7,8,9,10)
        if nb_grid == 4:
            set_MG_number_of_sweeps(1,2,3,32,5,6,7,8,9,10)
        if nb_grid == 5:
            set_MG_number_of_sweeps(1,2,3,4,64,6,7,8,9,10)
        if nb_grid == 6:
            set_MG_number_of_sweeps(1,2,3,4,5,128,7,8,9,10)


#--------------------------------------------------------------------------------------------#
def get_MG_number_of_sweeps():
    result = FT_get_nb_sweeps()
    for i in range (10):
        print "sweeps (",i,") is: ",result[i]
    return result
#--------------------------------------------------------------------------------------------#
def set_MG_number_of_sweeps(*values):
    print "PYTHON: set_number_of_sweeps START"
    vals = []
    test = len(values)
    print "PYTHON: set_number_of_sweeps, lenght args is: ", test

##    if len(values) == 0:
##          raise ValueError,"set_number_of_sweeps: - NO ARGUMENTS"
    for i in range (test):
        print "PYTHON: set_number_of_sweeps, i is: ", i
        print "PYTHON: set_number_of_sweeps, values[i] is: ", values[i]
##        vals[i] = values[i]
        vals.append(values[i])

    for i in range (test):
        print "PYTHON: set_number_of_sweeps, vals[i] is: ", vals[i]


    print "PYTHON: set_number_of_sweeps vals: ", vals
    FT_set_nb_sweeps(*vals)
    print "PYTHON: set_number_of_sweeps END"
#--------------------------------------------------------------------------------------------#
def get_MG_number_of_cycles():
    return FT_get_max_number_of_full_multigrid_cycles()
#--------------------------------------------------------------------------------------------#
def set_MG_number_of_cycles(mnfmg):
    FT_set_max_number_of_full_multigrid_cycles(mnfmg)
#--------------------------------------------------------------------------------------------#
def get_MG_convergence_criteria():
    return FT_get_convergence_criteria_for_full_multigrid()
#--------------------------------------------------------------------------------------------#
def set_MG_convergence_criteria(ccfmg):
    FT_set_convergence_criteria_for_full_multigrid(ccfmg)


#--------------------------------------------------------------------------------------------#
# CPU BOOSTER
#--------------------------------------------------------------------------------------------#
def get_cpubooster():
    available,cpuboo = FT_get_cpubooster()
    return cpuboo
#--------------------------------------------------------------------------------------------#
def set_cpubooster(cpuboo):
    FT_set_cpubooster(cpuboo)


#--------------------------------------------------------------------------------------------#
# PRECONDITIONING models
#--------------------------------------------------------------------------------------------#
HAKIMI = 0
MERKLE = 1
#--------------------------------------------------------------------------------------------#
def get_preconditioning_model():
    return FT_get_preconditionning_model()
#--------------------------------------------------------------------------------------------#
def set_preconditioning_model(model):
    prec = get_preconditioning()
    if prec == 0:
        print "set_preconditioning_model, model: ", model
#        raise ValueError, "Preconditioning model is not accessible for non-preconditioning project."

    else:
        if model == 1:
            smooth = 3
        else:
            smooth = 2

        FT_set_residual_smoothing(smooth)
        FT_set_preconditionning_model(model)


#--------------------------------------------------------------------------------------------#
# PRECONDITIONING parameters
#--------------------------------------------------------------------------------------------#
def get_preconditioning_model_params():
    result = FT_get_preconditionning_model_params()
    #print "get_preconditionning_model_params, beta star is ", result[0]
    #print "get_preconditionning_model_params, qRef is ", result[1]
    #print "get_preconditionning_model_params, local velocity scaling is ", result[2]
    return result[0],result[2]

def set_preconditioning_model_params(beta,locScal):
    ##FT_set_reference_speed(vel)
    FT_set_preconditionning_model_params(beta,locScal)


#--------------------------------------------------------------------------------------------#
# SPATIAL DISCRETIZATION parameters
#--------------------------------------------------------------------------------------------#
def get_spatial_discretization_scheme():
    result = FT_get_spatial_discretization_parameters()
    return result[0]

def set_spatial_discretization_scheme( val ):
    result = FT_get_spatial_discretization_parameters()
    FT_set_spatial_discretization_parameters(val,       result[1], result[2], result[3],
                                             result[4], result[5], result[6], result[7],
                                             result[8], result[9])

#--------------------------------------------------------------------------------------------#
def get_spatial_discretization_upwind_order():
    result = FT_get_spatial_discretization_parameters()
    return result[6]

def set_spatial_discretization_upwind_order( val ):
    result = FT_get_spatial_discretization_parameters()
    FT_set_spatial_discretization_parameters(result[0], result[1], result[2],result[3],
                                             result[4], result[5], val,      result[7],
                                             result[8], result[9])

#--------------------------------------------------------------------------------------------#
def get_spatial_discretization_upwind_scheme():
    result = FT_get_spatial_discretization_parameters()
    return result[7]

def set_spatial_discretization_upwind_scheme( val ):
    result = FT_get_spatial_discretization_parameters()
    FT_set_spatial_discretization_parameters(result[0], result[1], result[2], result[3],
                                             result[4], result[5], result[6], val,
                                             result[8], result[9])

#--------------------------------------------------------------------------------------------#
def get_spatial_discretization_upwind_linear_field_limiter():
    result = FT_get_spatial_discretization_parameters()
    return result[8]

def set_spatial_discretization_upwind_linear_field_limiter( val ):
    result = FT_get_spatial_discretization_parameters()
    FT_set_spatial_discretization_parameters(result[0], result[1], result[2], result[3],
                                             result[4], result[5], result[6], result[7],
                                             val,       result[9])

#--------------------------------------------------------------------------------------------#
def get_spatial_discretization_upwind_nonlinear_field_limiter():
    result = FT_get_spatial_discretization_parameters()
    return result[9]

def set_spatial_discretization_upwind_nonlinear_field_limiter( val ):
    result = FT_get_spatial_discretization_parameters()
    FT_set_spatial_discretization_parameters(result[0], result[1], result[2], result[3],
                                             result[4], result[5], result[6], result[7],
                                             result[8], val)


#--------------------------------------------------------------------------------------------#
# TEMPORAL DISCRETIZATION parameters
#--------------------------------------------------------------------------------------------#
def get_time_stepping_technique():
    result = FT_get_time_stepping_choice()
    return result

def set_time_stepping_technique( val ):
    FT_set_time_stepping_choice(val)


#--------------------------------------------------------------------------------------------#
# DUAL TIME STEP parameters (for unsteady case)
#--------------------------------------------------------------------------------------------#
def get_dual_time_step_convergence_criteria():
    result = FT_get_num_model_unsteady_parameters()
    return result[0]

def set_dual_time_step_convergence_criteria(val):
    result = FT_get_num_model_unsteady_parameters()
    FT_set_num_model_unsteady_parameters(val,result[1])
#--------------------------------------------------------------------------------------------#
def get_dual_time_step_max_number_of_iteration():
    result = FT_get_num_model_unsteady_parameters()
    return result[1]

def set_dual_time_step_max_number_of_iteration(val):
    result = FT_get_num_model_unsteady_parameters()
    FT_set_num_model_unsteady_parameters(result[0],val)



#--------------------------------------------------------------------------------------------#
# HARMONIC parameters
#--------------------------------------------------------------------------------------------#
#
# following 2 routines should not be used anymore, they are kept for backward compatibility only
#           please use get/set time configuration functions instead
#
#--------------------------------------------------------------------------------------------#

def get_harmonic_configuration():
    return FT_get_harmonic_config()

def set_harmonic_configuration(val):
    if val != 0 and val != 1 and val != 2 and val != 3:
        raise ValueError, "Harmonic configuration must be 0, 1 or 2, or 3, not: " + str(val)
    else:
        FT_set_harmonic_config(val)
        FT_update_conditional_boundary_conditions(6)
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#


def get_acoustic_configuration():
    return FT_get_acoustic_configuration()

def set_acoustic_configuration (val):
    harm = FT_get_harmonic_config()
    if harm == 0 and val == 1:
        raise ValueError, "Acoustic configuration not accessible for non-harmonic project."
    else:
        FT_set_acoustic_configuration(val)

#--------------------------------------------------------------------------------------------#
# following 2 routines should not be used anymore, they are kept for backward compatibility only
#
# ... clocking:
# ... value => 1 = ON, 0 = OFF; type => 1 = fixed, 0 = variable

def get_clocking ():
    result = FT_get_clocking()
    print "get_clocking, clocking is ",result[0]
    print "get_clocking, variable or fixed is ",result[1]
    return result


def set_clocking (value, type):
    harm = FT_get_harmonic_config()
    if harm == 0 and value == 1:
        raise ValueError, "Clocking is not accessible for non-harmonic project."
    else:
        FT_set_clocking(value, type)

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
# ... new routines to change only clocking type, #25880

def get_clocking_type ():
    result = FT_get_clocking()
    return result[1]


def set_clocking_type (type):
    result = FT_get_clocking()
    DEPHAR = result[0]
    FT_set_clocking(DEPHAR, type)


#--------------------------------------------------------------------------------------------#
def get_nb_harmonic_frequencies():
    return FT_get_nb_harmonic_freq()

def set_nb_harmonic_frequencies(nb):
    FT_set_nb_harmonic_freq(nb)
#--------------------------------------------------------------------------------------------#
def get_nb_harmonic_perturbations_per_blade_row():
    return FT_get_nb_harmonic_rs()

def set_nb_harmonic_perturbations_per_blade_row(nb):
    FT_set_nb_harmonic_rs(nb)

#--------------------------------------------------------------------------------------------#
# HARMONIC parameters - rank 2
#--------------------------------------------------------------------------------------------#

BASIC     = 0
CLOCKING  = 1
MULTIRANK = 2

def set_harmonic_configuration_type(conf):
    if (conf == 1):
        result = FT_get_clocking()
        print "set_harmonic_configuration_type, clocking is ",result[0]
        print "set_harmonic_configuration_type, variable or fixed is ",result[1]

        type_ = result[1]
        FT_set_clocking(1, type_)
    else:
        FT_set_harmonic_configuration_type(conf)


# returns 0 - Basic, 1 - Clocking, 2 - Multi-rank
def get_harmonic_configuration_type():
    return FT_get_harmonic_configuration_type()

#--------------------------------------------------------------------------------------------#
# Max rank

def get_harmonic_maximum_rank():
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    return FT_get_maximum_rank()

def set_harmonic_maximum_rank(maxrank):
    test = FT_get_harmonic_configuration_type()
    print "set_harmonic_maximum_rank, test: ",test
##    if (test == 0):
##        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    FT_set_maximum_rank(maxrank)

#--------------------------------------------------------------------------------------------#
# nb harmonics per rank

def get_nb_harmonics_of_rank(ind):
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    return FT_get_nb_harmonics_of_rank(ind)

def set_nb_harmonics_of_rank(nb,ind):
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    FT_set_nb_harmonics_of_rank(nb,ind)

#--------------------------------------------------------------------------------------------#
# Number of harmonics per disturber for block (or group of blocks)

def get_nb_disturber_per_group(block_group_idx):
    nb = FT_get_nb_harmonic_disturbers_per_block(block_group_idx)
    return nb

def get_nb_harmonics_per_disturber(block_group_idx, group_idx):
    result = FT_get_g_name_for_harmonic_disturber(block_group_idx, group_idx)
    return result[1]

def set_nb_harmonics_per_disturber(block_group_idx, group_idx, nhar):
    FT_set_NLH_nb_dist_harmonics_per_block(block_group_idx, nhar, group_idx)




#--------------------------------------------------------------------------------------------#
# The state can be either 1 to activate or 0 to deactivate the harmonic with the index harm_ind

def set_harmonic_active_state(block_group_ind, harm_ind, state):
    FT_set_harmonic_active_state(block_group_ind, harm_ind, state)

def get_harmonic_active_state(block_group_ind, harm_ind):
    state = FT_get_harmonic_active_state(block_group_ind, harm_ind)
    return state

def set_multiple_harmonic_active_state(block_group_ind, harm_indices_list, state):


    test = len(harm_indices_list)
    for i in range (test):
        FT_set_harmonic_active_state(block_group_ind, harm_indices_list[i], state)



#--------------------------------------------------------------------------------------------#

# interaction

def get_harmo_multi_rank_interaction():
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    result = FT_get_harmo_multi_rank_interaction()
    return result


def set_harmo_multi_rank_interaction(val):
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    FT_set_harmo_multi_rank_interaction(val)

def get_harmo_max_order_interaction():
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    result = FT_get_harmo_max_order_interaction()
    return result


def set_harmo_max_order_interaction(val):
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    FT_set_harmo_max_order_interaction(val)


def calculate_harmonics_distibution():
    FT_set_multirank_update_flag(1)
    result = FT_calculate_harmonics_distibution()
    print "calculate_harmonics_distibution, result is: ",result
    return result

def get_harmo_multirk_partial():
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    result = FT_get_multirk_partial()
    return result


def set_harmo_multirk_partial(val):
    test = FT_get_harmonic_configuration_type()
    if (test == 0):
        raise ValueError, "Error, this routine must be used only with NLH multirank configuration"

    FT_set_multirk_partial(val)



#--------------------------------------------------------------------------------------------#
#    NLH Inner Perturbations

def add_harmonic_inner_perturbation (blockGroupInd):
    FT_add_harmonic_inner_perturbation (blockGroupInd)


def remove_harmonic_inner_perturbation (blockGroupInd):
    FT_remove_harmonic_inner_perturbation (blockGroupInd)


def set_harmonic_inner_perturbation_params(blockGroupInd, pertInd, freq, mode):
    FT_set_harmonic_inner_perturbation_params(blockGroupInd, pertInd, freq, mode)

def get_harmonic_inner_perturbation_params(blockGroupInd, pertInd):
    result = FT_get_harmonic_inner_perturbation_params(blockGroupInd, pertInd)
    return result

def get_nb_harmonic_inner_perturbations(blockGroupInd):
    result = FT_get_nb_harmonic_inner_perturbations(blockGroupInd)
    return result


#--------------------------------------------------------------------------------------------#
#------------------------------ COOLING - BLEED ---------------------------------------------#
#--------------------------------------------------------------------------------------------#


def get_nb_solid_patches():
    result = FT_get_nb_solid_patches()
    print "get_nb_solid_patches, result: ",result
    return result

def get_solid_patches():
    result = FT_get_solid_patches()
    print "get_solid_patches, result: ",result
    return result

def get_nb_injectors():
    result = FT_get_nb_injectors()
    print "get_nb_injectors, result: ",result
    return result


#--------------------------------------------------------------------------------------------#
# ... type: Line = 0, Point = 1, Slot = 2, Points = 3;
# ... mode: Relative = 0, Space Cart = 1, Space Cyl = 3, Grid = 2;
# ... role (string): Cooling or Bleed;
# ... dir_choice: Grid Indices = 0, XYZ = 1, r,theta,Z = 2;
# ... index: the index of existing injector from which the new will be a copy (positioning and all other parameters of the second wizard page)

def add_new_injector (name,type_,mode,role,dir_choice,index_):
    print "add_new_injector, START"
##    print "add_new_injector, name: ",name
##    print "add_new_injector, type: ",type_
##    print "add_new_injector, index: ",index_
##    print "add_new_injector, role: ",role

    nb_inj = FT_get_nb_injectors()
    print "add_new_injector, nb existing: ",str (nb_inj)
    if (nb_inj > 0):
        for ind in range (nb_inj):
            print "add_new_injector, ind is: ", str (ind)
            test_name = FT_get_injector_name(ind)
            print "add_new_injector, test_name is: ", test_name
            if (test_name == name):
                raise ValueError, "Can not create injector, name already exists: " + name
            else:
                print "add_new_injector, name OK ", name

        print "add_new_injector,index: ",str (index_)
        print "add_new_injector,nb: ",str (nb_inj)
        if (index_ >= nb_inj):
            index_ = -1
            print "add_new_injector, invalid index, the new injector wil be a copy of the last existing injector"
        else:
            print "add_new_injector, index OK"
    else:
        print "add_new_injector, no existing injectors in project, the new one will have default parameters"


#    print "add_new_injector, 1 role: ",role
    FT_add_new_cooling_bleed_injector(name,type_,mode,role,dir_choice,index_)
    nb1 = FT_get_nb_injectors()
#    print "add_new_injector, new nb: ",nb1
    print "add_new_injector, END"

#--------------------------------------------------------------------------------------------#
#------------------------------ READ/MODIFY INJECTOR PARAMETERS -----------------------------#

def get_injector_index (name):
    result = FT_get_injector_index(name)
    return result

#--------------------------------------------------------------------------------------------#
# ... patches
def store_injector_patch (name,b,f,p):
    FT_cooling_bleed_store_injector_patches(name,b,f,p)


# ... returns nb_patches,b1,f1,p1,b2,f2,p2 ... etc
def get_patches_in_cooling_bleed_injector(name):
    result = FT_get_patches_in_cooling_bleed_injector(name)
    return result

#--------------------------------------------------------------------------------------------#
# ... name
def get_injector_name (ind):
    result = FT_get_injector_name(ind)
    return result

def set_injector_name(old_name, new_name):
    FT_set_injector_name(old_name, new_name)

#--------------------------------------------------------------------------------------------#
# ... type
def get_injector_type (name):
    result = FT_get_injector_type(name)
    return result

def set_injector_type(name, type):
    FT_set_injector_type(name, type)
#--------------------------------------------------------------------------------------------#
# ... role
def get_injector_role (name):
    param = "role"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_role(name, role):
    param = "role"
    FT_set_injector_parameter(name, param, role)
#--------------------------------------------------------------------------------------------#
# ... mode
def get_injector_mode (name):
    param = "mode"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_mode(name, mode):
    param = "mode"
    FT_set_injector_parameter(name, param, mode)
#--------------------------------------------------------------------------------------------#
# ... direction_choice
def get_injector_direction_choice (name):
    param = "direction_choice"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_direction_choice(name, direction_choice):
    param = "direction_choice"
    FT_set_injector_parameter(name, param, direction_choice)
#--------------------------------------------------------------------------------------------#
# ... diameter
def get_injector_diameter (name):
    param = "diameter"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_diameter(name, diameter):
    param = "diameter"
    FT_set_injector_parameter(name, param, diameter)
#--------------------------------------------------------------------------------------------#
# ... number of holes
def get_injector_number_holes (name):
    param = "number_holes"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_number_holes(name, number_holes):
    param = "number_holes"
    FT_set_injector_parameter(name, param, number_holes)
#--------------------------------------------------------------------------------------------#
# ... temperature
def get_injector_temperature (name):
    param = "temperature"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_temperature(name, temperature):
    param = "temperature"
    FT_set_injector_parameter(name, param, temperature)
#--------------------------------------------------------------------------------------------#
# ... k
def get_injector_k (name):
    param = "k"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_k(name, k):
    param = "k"
    FT_set_injector_parameter(name, param, k)
#--------------------------------------------------------------------------------------------#
# ... epsilon
def get_injector_epsilon (name):
    param = "epsilon"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_epsilon(name, epsilon):
    param = "epsilon"
    FT_set_injector_parameter(name, param, epsilon)
#--------------------------------------------------------------------------------------------#
# ... intensity
def get_injector_intensity (name):
    param = "intensity"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_intensity (name, intensity):
    param = "intensity"
    FT_set_injector_parameter(name, param, intensity)
#--------------------------------------------------------------------------------------------#
# ... viscosity
def get_injector_viscosity (name):
    param = "viscosity"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_viscosity (name, viscosity):
    param = "viscosity"
    FT_set_injector_parameter(name, param, viscosity)
#--------------------------------------------------------------------------------------------#
# ... mass_flow
def get_injector_mass_flow (name):
    param = "mass_flow"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_mass_flow (name, mass_flow):
    param = "mass_flow"
    FT_set_injector_parameter(name, param, mass_flow)
#--------------------------------------------------------------------------------------------#
# ... mass_flow_factor
def get_injector_mass_flow_factor (name):
    param = "mass_flow_factor"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_mass_flow_factor (name, mass_flow_factor):
    param = "mass_flow_factor"
    FT_set_injector_parameter(name, param, mass_flow_factor)
#--------------------------------------------------------------------------------------------#
# ... temperature_choice
def get_injector_temperature_choice (name):
    param = "temperature_choice"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_temperature_choice (name, temperature_choice):
    param = "temperature_choice"
    FT_set_injector_parameter(name, param, temperature_choice)
#--------------------------------------------------------------------------------------------#
# ... mass_flow_choice
def get_injector_mass_flow_choice (name):
    param = "mass_flow_choice"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_mass_flow_choice (name, mass_flow_choice):
    param = "mass_flow_choice"
    FT_set_injector_parameter(name, param, mass_flow_choice)
#--------------------------------------------------------------------------------------------#
# ... turbulence_choice
def get_injector_turbulence_choice (name):
    param = "turbulence_choice"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_turbulence_choice (name, turbulence_choice):
    param = "turbulence_choice"
    FT_set_injector_parameter(name, param, turbulence_choice)
#--------------------------------------------------------------------------------------------#
# ... first_angle
def get_injector_first_angle (name):
    param = "first_angle"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_first_angle (name, first_angle):
    param = "first_angle"
    FT_set_injector_parameter(name, param, first_angle)
#--------------------------------------------------------------------------------------------#
# ... second_angle
def get_injector_second_angle (name):
    param = "second_angle"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_second_angle (name, second_angle):
    param = "second_angle"
    FT_set_injector_parameter(name, param, second_angle)
#--------------------------------------------------------------------------------------------#
# ... third_angle
def get_injector_third_angle (name):
    param = "third_angle"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_third_angle (name, third_angle):
    param = "third_angle"
    FT_set_injector_parameter(name, param, third_angle)
#--------------------------------------------------------------------------------------------#
# ... slot_width
def get_injector_slot_width (name):
    param = "slot_width"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_slot_width (name, slot_width):
    param = "slot_width"
    FT_set_injector_parameter(name, param, slot_width)
#--------------------------------------------------------------------------------------------#
# ... inlet_group_name
def get_injector_inlet_group_name (name):
    param = "inlet_group_name"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_inlet_group_name (name, inlet_group_name):
    param = "inlet_group_name"
    FT_set_injector_parameter(name, param, inlet_group_name)
#--------------------------------------------------------------------------------------------#
# ... axial_coordinates
def get_injector_axial_coordinates (name):
    param = "axial_coordinates"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_axial_coordinates (name, axial_coordinates):
    param = "axial_coordinates"
    FT_set_injector_parameter(name, param, axial_coordinates)
#--------------------------------------------------------------------------------------------#
# ... side_one_or_two
def get_injector_side_one_or_two (name):
    param = "side_one_or_two"
    result = FT_get_injector_parameter(name, param)
    return result

def set_injector_side_one_or_two (name, side_one_or_two):
    param = "side_one_or_two"
    FT_set_injector_parameter(name, param, side_one_or_two)

#--------------------------------------------------------------------------------------------#
# ... coordinates
def get_injector_coordinates (name):
    index_ = FT_get_injector_index(name)
    result = FT_get_injector_coordinates(index_)

    x1                = result[2]
    y1                = result[3]
    z1                = result[4]
    x2                = result[5]
    y2                = result[6]
    z2                = result[7]

    return result
#--------------------------------------------------------------------------------------------#
def set_injector_coordinates (name,x1,y1,z1,x2,y2,z2):
    index_ = FT_get_injector_index(name)
    FT_set_injector_coordinates(index_,x1,y1,z1,x2,y2,z2)


#--------------------------------------------------------------------------------------------#
# ... positioning_patches (only backward compatibility)
def get_injector_positioning_patches (name):
    result = FT_get_injector_positioning_patches(name)
    return result

def set_injector_positioning_patches (name,patch1,patch2):
    FT_set_injector_positioning_patches (name,patch1,patch2)

#--------------------------------------------------------------------------------------------#
# ... positioning_patch
def get_injector_positioning_patch (name):
    result = FT_get_injector_positioning_patches(name)
    return result[0]

def set_injector_positioning_patch (name,patch):
    FT_set_injector_positioning_patches (name,patch,patch)


#--------------------------------------------------------------------------------------------#
# ... points type of injector routines
#--------------------------------------------------------------------------------------------#
# ... points data - for each point(hole): X, Y, Z, Vx, Vy, Vz, validity(0/1)

# ...
def get_injector_pointsdata (name):
    result = FT_get_injector_pointsdata (name)
    return result

# ... add hole
def add_injector_pointsdata(name,index):
    FT_add_injector_pointsdata (name,index)

# ... modify existing hole data
def set_injector_pointsdata (name,index,x,y,z,Vx,Vy,Vz):
    FT_set_injector_pointsdata (name,index,x,y,z,Vx,Vy,Vz)

#--------------------------------------------------------------------------------------------#
def injector_reverseHolesAxis(name,n):
    FT_injector_reverseHolesAxis(name,n)

# ... remove hole
def injector_remove_pointsdata(name,n):
    FT_injector_remove_pointsdata(name,n)

#--------------------------------------------------------------------------------------------#
# ... get/set number of periodic repetitions
def get_injector_pointsrepet(name):
    result = FT_get_injector_pointsrepet(name)
    return result

def set_injector_pointsrepet(name,index):
    FT_set_injector_pointsrepet(name,index)


#--------------------------------------------------------------------------------------------#
# ... Passive tracers
#--------------------------------------------------------------------------------------------#
def get_injector_cooling_bleed_tracers(name):
    result = FT_get_injector_cooling_bleed_tracers(name)
    if type(result) is types.NoneType:
        return None
    else:
        return result

def set_injector_cooling_bleed_tracers(name,tracers):
    nbTracers = len(tracers)
    FT_set_injector_cooling_bleed_tracers(name,nbTracers,tracers)

#--------------------------------------------------------------------------------------------#
# ... Mixture species
#--------------------------------------------------------------------------------------------#
def get_injector_cooling_bleed_species(name):
    result = FT_get_injector_cooling_bleed_species(name)
    if type(result) is types.NoneType:
        return None
    else:
        return result

def set_injector_cooling_bleed_species(name,speciesList):
    nbSpecies = len(speciesList)
    FT_set_injector_cooling_bleed_species(name,nbSpecies,speciesList)


#--------------------------------------------------------------------------------------------#
#           REMOVE
#--------------------------------------------------------------------------------------------#
def remove_all_injectors():
    FT_remove_all_injectors()

#--------------------------------------------------------------------------------------------#
def remove_cooling_bleed_injector(name):
    FT_remove_cooling_bleed_injector(name)

#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
#           READ / WRITE FILE
#--------------------------------------------------------------------------------------------#
def read_cooling_holes_file (filename, prefix):
    FT_read_cooling_holes_file (filename, prefix)

def write_cooling_holes_file (filename):
    FT_write_cooling_holes_file (filename)

def write_selected_injectors_to_cooling_holes_file (filename,nb,list_names):
    FT_write_selected_cooling_holes_to_file(filename,nb,list_names)


#--------------------------------------------------------------------------------------------#
# ... spreading of the holes: => 3 = ON, 2 = OFF

def get_injector_spreading ():
    result = FT_get_injector_spreading ()
    return result

def set_injector_spreading (spreading):
    FT_set_injector_spreading (spreading)



#--------------------------------------------------------------------------------------------#
#------------------------------ INITIAL SOLUTION --------------------------------------------#
#--------------------------------------------------------------------------------------------#
CONSTANT_VALUES            = 'const'
FROM_FILE                  = 'file'
FOR_TURBOMACHINERY         = 'turbo'
CARTESIAN_COORDS           = 'abs'
CYLINDRICAL_COORDS         = 'rel'
RESET_CONVERGENCE_HISTORY  = 1
IMPORT_CONVERGENCE_HISTORY = 0
#--------------------------------------------------------------------------------------------#
class InitialSolution:
    def __init__(self,blockGroupID):
        self._blockGroupID = blockGroupID

#--------------------------------------------------------------------------------------------#
# Get name of this group
#--------------------------------------------------------------------------------------------#
    def get_group_name(self):
        return FT_get_initial_solution_group_name(self._blockGroupID)

#--------------------------------------------------------------------------------------------#
# Get blocks of this group
#--------------------------------------------------------------------------------------------#
    def get_nb_blocks(self):
        return FT_get_initial_solution_block_names(self._blockGroupID)[0]

    def get_block_index(self,idx):
        return FT_get_initial_solution_block_index(self._blockGroupID,idx)

    def get_block_names(self):
        result = FT_get_initial_solution_block_names(self._blockGroupID)
        nb = result[0]
        blockNames = []
        for i in range (nb):
            blockNames.append(result[i+1])
        return blockNames

#--------------------------------------------------------------------------------------------#
# Mode ('const', 'file', 'turbo', 'auto', or 'through'
#--------------------------------------------------------------------------------------------#
    def get_mode(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[0]

    def set_mode(self,mode):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           mode,       result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);

#--------------------------------------------------------------------------------------------#
# In case of Constant Initial Solution mode
#--------------------------------------------------------------------------------------------#
# coord. system are:
# 'abs', 'rel'
#--------------------------------------------------------------------------------------------#
    def get_coord_system(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[6]
    def set_coord_system(self,cs):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], cs,
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
# ---
# OLD
# ---
    def get_constant_mode(self):
        return FT_get_initial_solution_constant_mode(self._blockGroupID)
    def set_constant_mode(self,mode):
        FT_set_initial_solution_constant_mode(self._blockGroupID,mode)

#--------------------------------------------------------------------------------------------#
# Initial Pressure
#--------------------------------------------------------------------------------------------#
    def get_pressure(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[1]
    def set_pressure(self,P):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], P,          result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
        FT_set_constant_numeric_parameter(self._blockGroupID,"pressure",P)
#--------------------------------------------------------------------------------------------#
# Initial Temperature
#--------------------------------------------------------------------------------------------#
    def get_temperature(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[2]
    def set_temperature(self,T):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], T,          result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Velocity [Vx,Vy,Vz] or [Vr,Vt,Vz]
#--------------------------------------------------------------------------------------------#
    def get_velocity(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return Vector(result[3], result[4], result[5])
    def set_velocity(self,vel):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], vel.x,      vel.y,      vel.z,      result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial k (in case of k-e turbulence model activated)
#--------------------------------------------------------------------------------------------#
    def get_k(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[7]
    def set_k(self,k):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           k,          result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial epsilon (in case of k-e turbulence model activated)
#--------------------------------------------------------------------------------------------#
    def get_epsilon(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[8]
    def set_epsilon(self,eps):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], eps,        result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Flow Direction ('None', 'I', 'J', 'K', 'Reverse I', 'Reverse J' or 'Reverse K')
#--------------------------------------------------------------------------------------------#
    def get_flow_direction(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[9]
    def set_flow_direction(self,direction):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], direction,  result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Velocity Fitting, in case of cylindrical coordinate system ('W' or 'Vm')
#--------------------------------------------------------------------------------------------#
    def get_velocity_fitting(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[10]
    def set_velocity_fitting(self,fitting):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], fitting,    result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Pressure Field, ('Constant' or 'Radial equilibrium with factor')
#--------------------------------------------------------------------------------------------#
    def get_pressure_field(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[11]
    def set_pressure_field(self,pressField):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], pressField, result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Radial Equilibrium Factor
#--------------------------------------------------------------------------------------------#
    def get_radial_equilibrium_factor(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[14]
    def set_radial_equilibrium_factor(self,factor):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           factor,     result[15], result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Turbulent Viscosity
#--------------------------------------------------------------------------------------------#
    def get_turbulent_viscosity(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[15]
    def set_turbulent_viscosity(self, viscosity):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], viscosity,  result[16], result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Turbulent Computation Method
#--------------------------------------------------------------------------------------------#
    def get_turbulent_computation_method(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[16]
    def set_turbulent_computation_method(self, method):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], method,     result[17], result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Set Turbulent Intensity, must be in the interval 0-100%
#--------------------------------------------------------------------------------------------#
    def get_turbulent_intensity(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[17]
    def set_turbulent_intensity(self, intensity):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], intensity,  result[18], result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Turbulent Length Scale
#--------------------------------------------------------------------------------------------#
    def get_turbulent_length_scale(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[18]
    def set_turbulent_length_scale(self, lscale):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], lscale,     result[19], result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Turbulent Viscosity Ratio
#--------------------------------------------------------------------------------------------#
    def get_turbulent_viscosity_ratio(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[19]
    def set_turbulent_viscosity_ratio(self, ratio):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], ratio,      result[20], result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Hydraulic Diameter
#--------------------------------------------------------------------------------------------#
    def get_hydraulic_diameter(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[20]
    def set_hydraulic_diameter(self, diameter):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], diameter,   result[21]);
#--------------------------------------------------------------------------------------------#
# Initial Modified Turbulent Viscosity (for Spalart-Allmaras only)
#--------------------------------------------------------------------------------------------#
    def get_modified_turbulent_viscosity(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[21]
    def set_modified_turbulent_viscosity(self, modVisc):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], modVisc);
#--------------------------------------------------------------------------------------------#
# Initial Species Mass-Fraction
#--------------------------------------------------------------------------------------------#
    def get_species_mass_fraction_value(self,arg):
        specIndex = -1
        if (type(arg) is types.IntType):
            specIndex = arg
            result = FT_get_initial_solution_species_(self._blockGroupID,specIndex)
            return result[1]
        elif (type(arg) is types.StringType):
            my_fluid = get_fluid_properties()
            nsp = my_fluid.get_number_of_species()
            for idx in range( nsp ):
                result = FT_get_initial_solution_species_(self._blockGroupID,idx)
                if (result[0] == arg):
                    return result[1]
        else:
            raise TypeError," "+str(arg)+": unexpected type "+str(type(arg))+". Should be integer or string."

    def get_species_mass_fraction_name(self,index):
        specIndex = -1
        if (type(index) is types.IntType):
            result = FT_get_initial_solution_species_(self._blockGroupID,specIndex)
            return result[0]
        else:
            raise TypeError," "+str(index)+": unexpected type "+str(type(index))+". Should be integer."

    def set_species_mass_fraction(self,arg,value):
        specIndex = -1
        if (type(arg) is types.IntType):
            specIndex = arg
            FT_set_initial_solution_species_mass_fraction_(self._blockGroupID,specIndex,value)
        elif (type(arg) is types.StringType):
            my_fluid = get_fluid_properties()
            nsp = my_fluid.get_number_of_species()
            for idx in range( nsp ):
                result = FT_get_initial_solution_species_(self._blockGroupID,idx)
                if (result[0] == arg):
                    specIndex = idx
                    FT_set_initial_solution_species_mass_fraction_(self._blockGroupID,specIndex,value)
        else:
            raise TypeError," "+str(arg)+": unexpected type "+str(type(arg))+". Should be integer or string."

#--------------------------------------------------------------------------------------------#
# OLD : constant numeric parameter names are:
# pressure, temperature, v1, v2, v3, k, eps, "pressure field factor" turbulent_viscosity
    def get_constant_numeric_parameter(self,name):
        return FT_get_constant_numeric_parameter(self._blockGroupID,name)
    def set_constant_numeric_parameter(self,name,value):
        FT_set_constant_numeric_parameter(self._blockGroupID,name,value)

#--------------------------------------------------------------------------------------------#
# OLD: choice parameters names (values) are:
# abs_rel_velocity (rel/abs), flow_direction (I/J/K), velocity_fitting (Vm/W), pressure_field (Constant/Radial equilibrium with factor)
    def get_constant_choice_parameter(self,name):
        return FT_get_constant_choice_parameter(self._blockGroupID,name)
    def set_constant_choice_parameter(self,name,value):
        FT_set_constant_choice_parameter(self._blockGroupID,name,value)

#--------------------------------------------------------------------------------------------#
# In case of Initial Solution "from file" mode
#--------------------------------------------------------------------------------------------#
    def get_restart_filename(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[12]
    def set_restart_filename(self,filename):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], filename,   result[13],
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);

#--------------------------------------------------------------------------------------------#
# In case of Initial Solution "from throughflow" mode
#--------------------------------------------------------------------------------------------#
    def get_throughflow_filename(self):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        return result[13]
    def set_throughflow_filename(self,filename):
        result = FT_get_initial_solution_parameters(self._blockGroupID)
        FT_set_initial_solution_parameters(self._blockGroupID,
                                           result[ 0], result[ 1], result[ 2], result[ 3], result[ 4], result[ 5], result[ 6],
                                           result[ 7], result[ 8], result[ 9], result[10], result[11], result[12], filename,
                                           result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21]);


#--------------------------------------------------------------------------------------------#
# In case of Initial Solution "turbo" mode
#--------------------------------------------------------------------------------------------#
# Channel selected patches
#--------------------------------------------------------------------------------------------#
    def get_turbo_entrance_patch(self):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        return get_bc_patch(result[0], result[1], result[2])
    def set_turbo_entrance_patch(self,bcpatch):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        bfp = bcpatch.get_block_face_patch()
        FT_set_channel_selected_bcgroups(self._blockGroupID,
                                         bfp[0]-1,  bfp[1]-1,  bfp[2]-1,
                                         result[3], result[4], result[5],
                                         result[6], result[7], result[8])

    def get_turbo_exit_patch(self):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        return get_bc_patch(result[3], result[4], result[5])
    def set_turbo_exit_patch(self,bcpatch):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        bfp = bcpatch.get_block_face_patch()
        FT_set_channel_selected_bcgroups(self._blockGroupID,
                                         result[0], result[1], result[2],
                                         bfp[0]-1,  bfp[1]-1,  bfp[2]-1,
                                         result[6], result[7], result[8])

    def get_turbo_exitup_patch(self):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        return get_bc_patch(result[6], result[7], result[8])
    def set_turbo_exitup_patch(self,bcpatch):
        result = FT_get_channel_selected_bcgroups(self._blockGroupID)
        bfp = bcpatch.get_block_face_patch()
        FT_set_channel_selected_bcgroups(self._blockGroupID,
                                         result[0], result[1], result[2],
                                         result[3], result[4], result[5],
                                         bfp[0]-1,  bfp[1]-1,  bfp[2]-1)

#--------------------------------------------------------------------------------------------#
# Pressure Type (CONSTANT=0 / RADIALEQUILIBRIUM=1)
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_pressure_type(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[0]
    def set_turbo_patch_pressure_type(self,BCtype,BCGroupName,pressureType):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  pressureType,result[1],result[2],result[3],result[4],result[5],result[6])
#--------------------------------------------------------------------------------------------#
# Pressure value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_pressure(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[1]
    def set_turbo_patch_pressure(self,BCtype,BCGroupName,pressure):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],pressure,result[2],result[3],result[4],result[5],result[6])
#--------------------------------------------------------------------------------------------#
# Radius (for radial equilibrium)
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_radius(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[2]
    def set_turbo_patch_radius(self,BCtype,BCGroupName,radius):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],result[1],radius,result[3],result[4],result[5],result[6])
#--------------------------------------------------------------------------------------------#
# Temperature value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_temperature(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[3]
    def set_turbo_patch_temperature(self,BCtype,BCGroupName,temperature):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],result[1],result[2],temperature,result[4],result[5],result[6])
#--------------------------------------------------------------------------------------------#
# Vr value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vr(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[4]
    def set_turbo_patch_vr(self,BCtype,BCGroupName,Vr):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],result[1],result[2],result[3],Vr,result[5],result[6])
#--------------------------------------------------------------------------------------------#
# Vt value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vt(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[5]
    def set_turbo_patch_vt(self,BCtype,BCGroupName,Vt):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],result[1],result[2],result[3],result[4],Vt,result[6])
#--------------------------------------------------------------------------------------------#
# Vz value
#--------------------------------------------------------------------------------------------#
    def get_turbo_patch_vz(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        return result[6]
    def set_turbo_patch_vz(self,BCtype,BCGroupName,Vz):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,
                                  result[0],result[1],result[2],result[3],result[4],result[5],Vz)

#   Pressure Type (CONSTANT=0/RADIALEQUILIBRIUM=1), pressure, radius
    def get_turbo_patch_params(self,BCtype,BCGroupName):
        result = FT_get_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName)
        #print "get_turbo_patch_params, pressureType: ",result[0]
        #print "get_turbo_patch_params, pressure: ",result[1]
        #print "get_turbo_patch_params, radius: ",result[2]
        #print "get_turbo_patch_params, temperature: ",result[3]
        #print "get_turbo_patch_params, Vr: ",result[4]
        #print "get_turbo_patch_params, Vt: ",result[5]
        #print "get_turbo_patch_params, Vz: ",result[6]
        #print "get_turbo_patch_params, nb_patches: ",result[7]
        #for i in range (result[7]):
        #    j = i + 8
        #    k = i + 9
        #    l = i + 10
        #    print "get_turbo_patch_params, b: ",result[j]
        #    print "get_turbo_patch_params, f: ",result[k]
        #    print "get_turbo_patch_params, p: ",result[l]
        return result

    def set_turbo_patch_params(self,BCtype,BCGroupName,pressureType,pressure,radius):
        params = self.get_turbo_patch_params(BCtype,BCGroupName)
        T  = params[3]
        Vr = params[4]
        Vt = params[5]
        Vz = params[6]
        FT_set_turbo_patch_params(BCtype,self._blockGroupID,BCGroupName,pressureType,pressure,radius,T,Vr,Vt,Vz)


#--------------------------------------------------------------------------------------------#
def get_initial_solution_nb_groups():
    return FT_get_initial_solution_nb_groups()
#--------------------------------------------------------------------------------------------#
def get_initial_solution(blockGroupID):
    return InitialSolution(blockGroupID)

#--------------------------------------------------------------------------------------------#
# this is a global parameter, but is applicable only in "from file" mode (which is block dependant)
def get_restart_mode():
        return FT_get_reset_convergence_history()
def set_restart_mode(mode):
        FT_set_reset_convergence_history(mode)

#--------------------------------------------------------------------------------------------#
# Initial Solution blocks grouping/ungrouping
#--------------------------------------------------------------------------------------------#
def create_initial_solution_block_group(name,value):
    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to group
        blocks_list = []
        for block_name in value:
            blockIdx = get_block_group_index(block_name)
            blocks_list.append(blockIdx)

    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        blocks_list = get_blocks_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    FT_group_initial_solution_block(name,len(blocks_list),blocks_list)
    FT_update_initial_solution_blocks_groups()
#--------------------------------------------------------------------------------------------#
def ungroup_initial_solution_block_group(arg):
    if (type(arg) is types.IntType):
        groupIndex=arg
        FT_ungroup_initial_solution_blocks(groupIndex)
        FT_update_initial_solution_blocks_groups()
    elif (type(arg) is types.StringType):
        groupName=arg
        groupIndex = FT_get_initial_solution_group_index(groupName)
        FT_ungroup_initial_solution_blocks(groupIndex)
        FT_update_initial_solution_blocks_groups()
#--------------------------------------------------------------------------------------------#
# Default grouping for "Turbomachinery" mode
#--------------------------------------------------------------------------------------------#
def reset_initial_solution_turbo_groups():
    FT_reset_initial_solution_turbo_groups()



#--------------------------------------------------------------------------------------------#
#                                                                                            #
#				Outputs/Computed vars               	      		     #
#                                                                                            #
#--------------------------------------------------------------------------------------------#
def select_output( key_name ):
    FT_select_quantity_(key_name)

#--------------------------------------------------------------------------------------------#
def unselect_output( key_name ):
    FT_unselect_quantity_(key_name)

#--------------------------------------------------------------------------------------------#
def set_output_flags_from_file(filename,profilename):
        return FT_set_output_flags_from_file(filename,profilename)

#--------------------------------------------------------------------------------------------#
def get_mesh_type():
        return FT_get_mesh_type()
#--------------------------------------------------------------------------------------------#
def set_mesh_type(type):
        return FT_set_mesh_type(type)

#--------------------------------------------------------------------------------------------#
# Obsolete.
# Keep for backward compatibility.
#--------------------------------------------------------------------------------------------#
def get_output_flag(VarCode):
        return FT_get_output_flag(VarCode)
#--------------------------------------------------------------------------------------------#
def set_output_flag(VarCode,flag):
        return FT_set_output_flag(VarCode,flag)
#--------------------------------------------------------------------------------------------#
def get_azimuthal_output_flag(VarCode):
        return FT_get_azimuthal_output_flag(VarCode)
#--------------------------------------------------------------------------------------------#
def set_azimuthal_output_flag(VarCode,flag):
        return FT_set_azimuthal_output_flag(VarCode,flag)



#--------------------------------------------------------------------------------------------#
#                                                                                            #
#				Outputs/Surface Averaged vars                 		     #
#                                                                                            #
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
#                                                                                            #
#				Outputs/Azimuthal Averaged vars                 	     #
#                                                                                            #
#--------------------------------------------------------------------------------------------#
def select_azi_output( key_name ):
    FT_select_azi_quantity_(key_name)

#--------------------------------------------------------------------------------------------#
def unselect_azi_output( key_name ):
    FT_unselect_azi_quantity_(key_name)



#--------------------------------------------------------------------------------------------#
#------------------------------ CONTROL VARIABLES -------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# Maximum number of iterations
#--------------------------------------------------------------------------------------------#
def get_nb_iter_max():
        return FT_get_max_nb_of_iterations()
def set_nb_iter_max(nb):
        FT_set_max_nb_of_iterations(nb)

#--------------------------------------------------------------------------------------------#
# Convergence criteria
#--------------------------------------------------------------------------------------------#
def get_convergence_criteria():
        return FT_get_convergence_criteria()
def set_convergence_criteria(value):
        FT_set_convergence_criteria(value)

#--------------------------------------------------------------------------------------------#
# Output writing frequency
#--------------------------------------------------------------------------------------------#
def get_output_writing_frequency():
        return FT_get_save_solution_rate()
def set_output_writing_frequency(value):
        FT_set_save_solution_rate(value)

#--------------------------------------------------------------------------------------------#
# Minimum output choice
#--------------------------------------------------------------------------------------------#
def get_residuals_per_row():
        return FT_get_residuals_per_row()
def set_residuals_per_row(value):
        FT_set_residuals_per_row(value)

#--------------------------------------------------------------------------------------------#
# Residuals per row
#--------------------------------------------------------------------------------------------#
def get_min_output_choice():
        return FT_get_min_output_choice()
def set_min_output_choice(value):
        FT_set_min_output_choice(value)

#--------------------------------------------------------------------------------------------#
# Memory estimation
#--------------------------------------------------------------------------------------------#
def get_automatic_memory_estimation():
    return FT_get_automatic_memory_estimation()
def set_automatic_memory_estimation(value):
    if (value == 1):
        # Automatic memory estimation: compute harmonics and set requested memory amount
        test = FT_get_harmonic_configuration_type()
        if (test != 0):
            calculate_harmonics_distibution()
        FT_set_default_memory_estimation()
    FT_set_automatic_memory_estimation(value)
#--------------------------------------------------------------------------------------------#
def get_user_memory_estimation():
    # If automatic estimation: ensure requested memory is initialized.
    if (get_automatic_memory_estimation() == 1):
        # Ensure default requested memory is computed
        set_automatic_memory_estimation(1)
    return FT_get_user_memory_estimation()
def set_user_memory_estimation(nbR,nbI):
        FT_set_user_memory_estimation(nbR,nbI)

#--------------------------------------------------------------------------------------------#
#   Unsteady Control Variables parameters
#--------------------------------------------------------------------------------------------#
def get_unsteady_time_step_choice():
    return FT_get_unsteady_time_steps_choice()
def set_unsteady_time_step_choice(timeStepChoice):
    FT_set_unsteady_time_steps_choice(timeStepChoice)

#--------------------------------------------------------------------------------------------#
#   Number of angular positions
def get_number_of_angular_positions():
    return FT_get_number_of_angular_positions()
def set_number_of_angular_positions(n):
    FT_set_number_of_angular_positions(n)

#--------------------------------------------------------------------------------------------#
#   Include time-averaged solution in output ?
def get_time_averaged_output_flag():
    return FT_get_time_averaged_output_flag()
def set_time_averaged_output_flag(flag):
    FT_set_time_averaged_output_flag(flag)

#--------------------------------------------------------------------------------------------#
def get_physical_time_step():
    return FT_get_physical_time_step()
def set_physical_time_step(physTimeStep):
    FT_set_physical_time_step(physTimeStep)

#--------------------------------------------------------------------------------------------#
#  Number of Physical Time Steps
def get_nb_of_time_steps():
    return FT_get_max_nb_of_iterations()
def set_nb_of_time_steps(nb):
    FT_set_max_nb_of_iterations(nb)

#--------------------------------------------------------------------------------------------#
def get_nb_of_steady_iterations():
    return FT_get_nb_of_steady_iterations()
def set_nb_of_steady_iterations(nb):
    FT_set_nb_of_steady_iterations(nb)

#--------------------------------------------------------------------------------------------#
# Save Steady Solution Every xx Iterations
def get_output_unsteady_writing_frequency():
    return FT_get_output_unsteady_writing_frequency()
def set_output_unsteady_writing_frequency(value):
    FT_set_output_unsteady_writing_frequency(value)




#--------------------------------------------------------------------------------------------#
# Solver precision

def get_user_solver_precision():
    return FT_get_user_solver_precision()
def set_user_solver_precision(prec):
    FT_set_user_solver_precision(prec)

#--------------------------------------------------------------------------------------------#
#--- Expert parameters
#--------------------------------------------------------------------------------------------#
def get_expert_parameter (name):

    print "get_expert_parameter, name: ",name
    name = FT_get_expert_parameter_name(name)
    print "get_expert_parameter, after search, expert name is: ",name

    # ... Get expert parameter value
    value = FT_get_expert_parameter(name)
    if value!=None:
        if len(value)==1:
            return value[0]
        else:
            valueList = []
            for i in range( len(value) ):
                valueList.append(value[i])
            return valueList
    else:
        raise ValueError,"Could not access parameter : " + name

#--------------------------------------------------------------------------------------------#
def set_expert_parameter (name,value):
    valueList = []

    print "set_expert_parameter, name: ",name
    print "set_expert_parameter, value: ",value
    name = FT_get_expert_parameter_name(name)
    print "set_expert_parameter, after search, expert name is: ",name

    if ( (type(value) is types.IntType) or (type(value) is types.FloatType)):
        valueList.append(value)
    elif (type(value) is types.ListType):
        valueList = value
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value)) + " for parameter name " + name

    FT_set_expert_parameter(name,len(valueList),valueList)

    print "set_expert_parameter END"

#--------------------------------------------------------------------------------------------#
def get_names_values_info_of_modified_expert_parameters():
    # ... this routine is still not properly working, only names are OK
    names = FT_get_names_of_modified_expert_parameters()
    nb_args = FT_get_nb_args_of_modified_expert_parameters()
    values = FT_get_values_of_modified_expert_parameters()
    def_vals = FT_get_def_vals_of_modified_expert_parameters()
    info =  FT_get_info_of_modified_expert_parameters()
    return names,nb_args,values,def_vals,info


#--------------------------------------------------------------------------------------------#
def get_output_for_visualization():
    choice_1 = FT_get_min_output_choice()
    choice_2 = FT_get_IMULOU()
    return choice_1,choice_2
def set_min_output_choice_for_visualization(value1,value2):
    FT_set_min_output_choice(value1)
    FT_set_IMULOU(value2)

def set_IMULOU(value):
    FT_set_IMULOU(value)
def set_min_output_choice(value):
    FT_set_min_output_choice(value)

#--------------------------------------------------------------------------------------------#
#                                                                                            #
#				Steering   	      		     #
#                                                                                            #
#--------------------------------------------------------------------------------------------#
def create_steering_files():
    FT_computationSteering_createActiveSteeringNamesFine()
    FT_computationSteering_saveDataActiveProject()


#--------------------------------------------------------------------------------------------#
#                                                                                            #
#				General Interface management functions	      		     #
#                                                                                            #
#--------------------------------------------------------------------------------------------#


def quit_interface ():
    if not is_batch():
        eval_tcl_string( "itf_do_quit ")
    else:
        ## ... maybe no need to implement, batch exits automatically when the script is finished
        return




#--------------------------------------------------------------------------------------------#
#------------------------------ TURBOMACHINERY CONFIGURATION --------------------------------#
#--------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------#
#--- Blocks
#--------------------------------------------------------------------------------------------#
def get_nb_blocks():
    return FT_get_nb_blocks()

def get_block_names ():
    return FT_get_block_names()

def get_blocks_list(pattern):
    print "get_blocks_list START"
    block_list = []
    regexp = fnmatch.translate(pattern) ; # convert pattern to regular expression
    print "get_blocks_list regexp: ",regexp
    reobj = re.compile(regexp)
    print "get_blocks_list reobj: ",reobj
    for b in range( get_nb_blocks() ):
        ##params = get_block_params(b)
        block_name = FT_get_block_params(b)[0]
        ##print "get_blocks_list block_name is: ",block_name
        if (reobj.match(block_name)):
            ##print "get_blocks_list FOUND  block with index: ",b
            block_list.append(b)
    print "get_blocks_list END"
    return block_list

#--------------------------------------------------------------------------------------------#
def get_block_group_index(name):
    for b in range( get_nb_blocks() ):
        if (get_block_name(b) == name):
            return b
    return -1

#--------------------------------------------------------------------------------------------#
def get_block_name(index):
    if (index<0 or index>=get_nb_blocks()):
        raise ValueError, "Index out of bound : " + str(index)
    return FT_get_block_params(index)[0]

#--------------------------------------------------------------------------------------------#
def get_block_old_name(index):
    if (index<0 or index>=get_nb_blocks()):
        raise ValueError, "Index out of bound : " + str(index)
    return FT_get_block_params(index)[1]

#--------------------------------------------------------------------------------------------#
def get_block_imax(index):
    if (index<0 or index>=get_nb_blocks()):
        raise ValueError, "Index out of bound : " + str(index)
    return FT_get_block_params(index)[4]

#--------------------------------------------------------------------------------------------#
def get_block_jmax(index):
    if (index<0 or index>=get_nb_blocks()):
        raise ValueError, "Index out of bound : " + str(index)
    return FT_get_block_params(index)[5]

#--------------------------------------------------------------------------------------------#
def get_block_kmax(index):
    if (index<0 or index>=get_nb_blocks()):
        raise ValueError, "Index out of bound : " + str(index)
    return FT_get_block_params(index)[6]

#--------------------------------------------------------------------------------------------#
def get_block_params (index):
    result = FT_get_block_params(index)
#    name,old_name,rotating_group_name,init_sol_group_name,ind_i,ind_j,ind_k = FT_get_block_name(index)
    print "get_block_params, index is: ",index, ", name is: " ,result[0]
    if result[0] is "error":
        raise ValueError, "get_block_params, wrong block index: " + index


    print "get_block_params, index is: ",index,", old_name is: ",result[1]

    print "get_block_params, index is: ",index,", rotating_group_name is: ",result[2]
    print "get_block_params, index is: ",index,", init_sol_group_name is: ",result[3]
    print "get_block_params, index is: ",index,", ind_i is: ",result[4]
    print "get_block_params, index is: ",index,", ind_j is: ",result[5]
    print "get_block_params, index is: ",index,", ind_k is: ",result[6]

    return result

#--------------------------------------------------------------------------------------------#
def create_block_group(comp_index,group_index,name,value):
    print "create_block_group, comp_index: ",comp_index," name:",name," value",value
    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to group
        blocks_list = value
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        blocks_list = get_blocks_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    blockhList=[]
    for block in blocks_list:
        FT_group_block(comp_index,group_index,name,block)
    print "create_block_group END"


#--------------------------------------------------------------------------------------------#
def ungroup_blocks (comp_index,page_index,group_name):
    FT_ungroup_blocks_generic(comp_index,page_index,group_name)



#--------------------------------------------------------------------------------------------#
#--- Rows
#--------------------------------------------------------------------------------------------#
class Row:
    def __init__(self,index):
        self._index = index
        self._name  = FT_get_row_params(index)[0]

    def get_name(self):
        return self._name

    def get_nb_blocks(self):
        return FT_get_row_params(self._index)[1]

    def get_rotation_speed(self):
        return FT_get_row_params(self._index)[2]

    def get_nb_blades(self):
        return FT_get_row_params(self._index)[3]

    def get_repetition(self):
        return FT_get_row_params(self._index)[4]

    def get_block_name(self,idx):
        return FT_get_row_params(self._index)[5+idx]

#--------------------------------------------------------------------------------------------#
def get_nb_rows ():
    return FT_get_nb_rows()
#--------------------------------------------------------------------------------------------#
def get_row(arg):
    if   ( type(arg) is types.StringType):
        # Get row from its name
        name = arg
        for index in range (get_nb_rows()):
            row = Row(index)
            if (row.get_name() == name):
                return row
        raise ValueError,"Row with name: '" +name+"' cannot be found !"

    elif ( type(arg) is types.IntType ):
        # Get row from index
        index = arg
        if (index<0 or index>get_nb_rows()):
            raise IndexError,"Row index out of bounds : " + str(index)
        else:
            return Row(index)

#--------------------------------------------------------------------------------------------#
def get_row_params (index):
    result = FT_get_row_params(index)

##    print "get_row_params, row index  is: ",index,", row name  is: ",result[0]
##    print "get_row_params, row index is: ",index,", nb blocks  is: ",result[1]
##    print "get_row_params, row index is: ",index,", rot speed  is: ",result[2]
##    print "get_row_params, row index is: ",index,", nb blades  is: ",result[3]
##    print "get_row_params, row index is: ",index,", repetition  is: ",result[4]

##    for i in range (result[1]):
##        j = i + 5
##        print "get_row_params, block index is: ",i,", block name is: ",result[j]

    return result

def to_which_row_belongs_this_block(block):
    return FT_to_which_row_belongs_this_block(block)


#--------------------------------------------------------------------------------------------#
#--- Blades
#--------------------------------------------------------------------------------------------#
class Blade:
    def __init__(self,index):
        self._index = index
        self._name  = FT_get_blade_params(index)[0]

    def get_name(self):
        return self._name

    def get_group_name(self):
        return FT_get_blade_params(self._index)[1]

    def get_leading_edge(self):
        result = FT_get_blade_leading_edge_indices(self._index)
        return result

    def get_trailing_edge(self):
        result = FT_get_blade_trailing_edge_indices(self._index)
        return result

    def get_pressure_side(self):
        result = FT_get_blade_meri_ps_indices(self._index)
        return result

    def get_suction_side(self):
        result = FT_get_blade_meri_ss_indices(self._index)
        return result

    def get_row(self):
        blockName = self.get_leading_edge()[7] # First block of LE
        # Get row containing this block
        for rowIdx in range (get_nb_rows()):
            row = Row(rowIdx)
            for blkIdx in range (row.get_nb_blocks()):
                if (row.get_block_name(blkIdx) == blockName):
                    return row
        raise ValueError,"Blade with name: '" +self._name+"' does not belongs to a row !"
#--------------------------------------------------------------------------------------------#
def get_nb_blades ():
    return FT_get_nb_blades()
#--------------------------------------------------------------------------------------------#
def get_blade(arg):
    if   ( type(arg) is types.StringType):
        # Get blade from its name
        name = arg
        for index in range (get_nb_blades()):
            blade = Blade(index)
            if (blade.get_name() == name):
                return blade
        raise ValueError,"Blade with name: '" +name+"' cannot be found !"

    elif ( type(arg) is types.IntType ):
        # Get blade from index
        index = arg
        if (index<0 or index>get_nb_blades()):
            raise IndexError,"Blade index out of bounds : " + str(index)
        else:
            return Blade(index)

#--------------------------------------------------------------------------------------------#
def get_blades_list(pattern):
    ##print "get_blades_list START"
    blades_list = []
    regexp = fnmatch.translate(pattern) ; # convert pattern to regular expression
    ##print "get_blades_list regexp: ",regexp
    reobj = re.compile(regexp)
    ##print "get_blades_list reobj: ",reobj
    for b in range( get_nb_blades() ):
        ##params = get_block_params(b)
        blade_name = get_blade_params(b)[0]
        ##print "get_blocks_list block_name is: ",block_name
        if (reobj.match(blade_name)):
            ##print "get_blocks_list FOUND  block with index: ",b
            blades_list.append(b)
    ##print "get_blades_list END"
    return blades_list

#--------------------------------------------------------------------------------------------#
def get_blade_params (index):
    result = FT_get_blade_params(index)

    print "get_blade_params, blade index is: ",index,", blade name  is: ",result[0]
    print "get_blade_params, blade index is: ",index,", blade group name  is: ",result[1]

    return result


def get_blade_leading_edge_indices (blade_index):
    result = FT_get_blade_leading_edge_indices (blade_index)

    print "get_blade_leading_edge_indices, blade index: ",blade_index, " nb_leading_edges: ",result[0]
    for m in range (result[0]):
        imin = m + 1
        imax = m + 2
        jmin = m + 3
        jmax = m + 4
        kmin = m + 5
        kmax = m + 6
        block_name = m + 7
        print "get_blade_leading_edge_indices, imin is: ",result[imin]
        print "get_blade_leading_edge_indices, imax is: ",result[imax]
        print "get_blade_leading_edge_indices, jmin is: ",result[jmin]
        print "get_blade_leading_edge_indices, jmax is: ",result[jmax]
        print "get_blade_leading_edge_indices, kmin is: ",result[kmin]
        print "get_blade_leading_edge_indices, kmax is: ",result[kmax]
        print "get_blade_leading_edge_indices, block_name is: ",result[block_name]

        return result

def get_blade_trailing_edge_indices (blade_index):
    result =  FT_get_blade_trailing_edge_indices (blade_index)

    print "get_blade_trailing_edge_indices, blade_index: ",blade_index, " nb_trailing_edges: ",result[0]
    for m in range (result[0]):
        imin = m + 1
        imax = m + 2
        jmin = m + 3
        jmax = m + 4
        kmin = m + 5
        kmax = m + 6
        block_name = m + 7
        print "get_blade_trailing_edge_indices, imin is: ",result[imin]
        print "get_blade_trailing_edge_indices, imax is: ",result[imax]
        print "get_blade_trailing_edge_indices, jmin is: ",result[jmin]
        print "get_blade_trailing_edge_indices, jmax is: ",result[jmax]
        print "get_blade_trailing_edge_indices, kmin is: ",result[kmin]
        print "get_blade_trailing_edge_indices, kmax is: ",result[kmax]
        print "get_blade_trailing_edge_indices, block_name is: ",result[block_name]
    return result


def get_blade_meri_ps_indices (blade_index):
    print "get_blade_meri_ps_indices, START blade_index: ",blade_index
    result = FT_get_blade_meri_ps_indices (blade_index)
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " block ind: ",result[0]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index1Min: ",result[1]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index1Max: ",result[2]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index2Min: ",result[3]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index2Max: ",result[4]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index3Min: ",result[5]
    print "get_blade_meri_ps_indices, blade_index: ",blade_index, " index3Max: ",result[6]

    return result

def get_blade_meri_ss_indices (blade_index):
    print "get_blade_meri_ss_indices, START blade_index: ",blade_index
    result = FT_get_blade_meri_ss_indices (blade_index)

    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " block ind: ",result[0]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index1Min: ",result[1]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index1Max: ",result[2]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index2Min: ",result[3]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index2Max: ",result[4]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index3Min: ",result[5]
    print "get_blade_meri_ss_indices, blade_index: ",blade_index, " index3Max: ",result[6]

    return result


#--------------------------------------------------------------------------------------------#

def update_tcl_computations_tree():
    print "PYTHON: update_tcl"
    if not is_batch():
        eval_tcl_string( "itf_adm:update_tcl_computations_tree_from_python")


#--------------------------------------------------------------------------------------------#
# --------------------------------- Cavitation
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
def get_cavitation_model ():
    result = FT_get_cavitation_model ()
    return result

#--------------------------------------------------------------------------------------------#
def set_cavitation_model (flag):
    FT_set_cavitation_model (flag)

#--------------------------------------------------------------------------------------------#
def set_cavitation_parameters (rhol, rhov, muliq, mugas, prref, prtlv, cplref, cpvref):
    FT_set_cavitation_parameters (rhol, rhov, muliq, mugas, prref, prtlv, cplref, cpvref)


#--------------------------------------------------------------------------------------------#
def get_cavitation_vapor_parameters():
    result = FT_get_cavitation_vapor_parameters()
    print "get_cavitation_vapor_parameters, RHOV: "   ,result[0]
    print "get_cavitation_vapor_parameters, MUGAS: "  ,result[1]
    print "get_cavitation_vapor_parameters, PRTLV: "  ,result[2]
    print "get_cavitation_vapor_parameters, CPVREF: " ,result[3]
    return result

def set_cavitation_vapor_parameters (rhov, mugas, prtlv, cpvref):
    FT_set_cavitation_vapor_parameters (rhov, mugas, prtlv, cpvref)
#--------------------------------------------------------------------------------------------#

# the following 4 commands replace the above set_cavitation_vapor_parameters

#--------------------------------------------------------------------------------------------#
def set_cavitation_vapor_density (rhov):
    FT_set_cavitation_vapor_density (rhov)
#--------------------------------------------------------------------------------------------#

def set_cavitation_vapor_dynamic_viscosity (mugas):
    FT_set_cavitation_vapor_dynamic_viscosity (mugas)
#--------------------------------------------------------------------------------------------#

def set_cavitation_vapor_prandtl_number (prtlv):
    FT_set_cavitation_vapor_prandtl_number (prtlv)
#--------------------------------------------------------------------------------------------#

def set_cavitation_vapor_heat_capacity (cpvref):
    FT_set_cavitation_vapor_heat_capacity (cpvref)
#--------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------#
def get_cavitation_liquid_density ():
    result = FT_get_cavitation_liquid_density()
    print "get_cavitation_liquid_density, RHOL: ",result
    return result

def set_cavitation_liquid_density (rhol):
    FT_set_cavitation_liquid_density(rhol)
#--------------------------------------------------------------------------------------------#

def get_cavitation_liquid_dynamic_viscosity ():
    result = FT_get_cavitation_liquid_dynamic_viscosity()
    print "get_cavitation_liquid_dynamic_viscosity, MULIQ: ",result
    return result

def set_cavitation_liquid_dynamic_viscosity (muliq):
    FT_set_cavitation_liquid_dynamic_viscosity(muliq)
#--------------------------------------------------------------------------------------------#

def get_cavitation_liquid_prandtl_number ():
    result = FT_get_cavitation_liquid_prandtl_number()
    print "get_cavitation_liquid_prandtl_number, PRREF: ",result
    return result

def set_cavitation_liquid_prandtl_number (prref):
    FT_set_cavitation_liquid_prandtl_number(prref)
#--------------------------------------------------------------------------------------------#

def get_cavitation_liquid_heat_capacity ():
    result = FT_get_cavitation_liquid_heat_capacity()
    print "get_cavitation_liquid_heat_capacity, CPLREF: ",result
    return result

def set_cavitation_liquid_heat_capacity (cplref):
    FT_set_cavitation_liquid_heat_capacity(cplref)

#--------------------------------------------------------------------------------------------#

def get_cavitation_coefficients():
    result = FT_get_cavitation_coefficients()
    print "get_cavitation_coefficients, PVAPS: ",result[0]
    print "get_cavitation_coefficients, AMIN: " ,result[1]
    return result

def set_cavitation_coefficients (pvaps,amin):
    FT_set_cavitation_coefficients (pvaps,amin)


#--------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------#
#------------------------------ CHT parameters ----------------------------------------------#
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
def get_nb_cht_block_groups():
    return FT_get_nb_cht_block_groups


#--------------------------------------------------------------------------------------------#
def get_block_type (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    block_type = FT_get_block_type(group_index)
    return block_type

#--------------------------------------------------------------------------------------------#
def set_block_type (group_index,type):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    FT_set_block_type(group_index,type)

#--------------------------------------------------------------------------------------------#


# solid conductivity - get
#--------------------------------------------------------------------------------------------#
def get_solid_conductivity_type (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_conductivity(group_index)
    return results[1]

#--------------------------------------------------------------------------------------------#

def get_solid_conductivity_value (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_conductivity(group_index)
    return results[0]

#--------------------------------------------------------------------------------------------#


def get_solid_conductivity_profile(group_index):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"CHT group  index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "1":
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    result = FT_get_cht_solid_conductivity_profile(group_index)
    print "get_solid_conductivity_profile",result
    return result

#--------------------------------------------------------------------------------------------#


# solid conductivity - set
#--------------------------------------------------------------------------------------------#
def set_solid_conductivity_type (group_index,type_):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_conductivity(group_index)
    val = results[0]
    FT_set_cht_solid_conductivity(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_conductivity_value (group_index,val):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_conductivity(group_index)
    type_ = results[1]
    FT_set_cht_solid_conductivity(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_conductivity_profile (group_index,profile_data):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    nb = len(profile_data)
    FT_set_cht_solid_conductivity_profile(group_index,nb,profile_data)

#--------------------------------------------------------------------------------------------#

# solid density - get
#--------------------------------------------------------------------------------------------#
def get_solid_density_type (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_density(group_index)
    return results[1]

#--------------------------------------------------------------------------------------------#

def get_solid_density_value (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_density(group_index)
    return results[0]

#--------------------------------------------------------------------------------------------#

def get_solid_density_profile(group_index):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"CHT group  index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "1":
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    result = FT_get_cht_solid_density_profile(group_index)
    print "get_solid_density_profile",result
    return result

#--------------------------------------------------------------------------------------------#


# solid density - set
#--------------------------------------------------------------------------------------------#
def set_solid_density_type (group_index,type_):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_density(group_index)
    val = results[0]
    FT_set_cht_solid_density(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_density_value (group_index,val):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_density(group_index)
    type_ = results[1]
    FT_set_cht_solid_density(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_density_profile (group_index,profile_data):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    nb = len(profile_data)
    FT_set_cht_solid_density_profile(group_index,nb,profile_data)

#--------------------------------------------------------------------------------------------#

# solid capacity - get
#--------------------------------------------------------------------------------------------#
def get_solid_capacity_type (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_capacity(group_index)
    return results[1]

#--------------------------------------------------------------------------------------------#

def get_solid_capacity_value (group_index):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    if get_block_type(group_index) != 1:
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    results = FT_get_cht_solid_capacity(group_index)
    return results[0]

#--------------------------------------------------------------------------------------------#

def get_solid_capacity_profile(group_index):
    if (iBlock<0 or iBlock>=get_nb_domains()):
        raise IndexError,"CHT group  index out of bounds : " + str(iBlock)
    if get_block_type(iBlock) != "1":
        raise IndexError,"CHT group  #" + str(group_index) + " is not solid!"
    result = FT_get_cht_solid_capacity_profile(group_index)
    print "get_solid_capacity_profile",result
    return result

#--------------------------------------------------------------------------------------------#


# solid capacity - set
#--------------------------------------------------------------------------------------------#
def set_solid_capacity_type (group_index,type_):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_capacity(group_index)
    val = results[0]
    FT_set_cht_solid_capacity(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_capacity_value (group_index,val):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    results = FT_get_cht_solid_capacity(group_index)
    type_ = results[1]
    FT_set_cht_solid_capacity(group_index,val,type_)

#--------------------------------------------------------------------------------------------#

def set_solid_capacity_profile (group_index,profile_data):
    if (group_index<0 or group_index>=get_nb_cht_block_groups()):
        raise IndexError,"CHT group index out of bounds : " + str(group_index)
    nb = len(profile_data)
    FT_set_cht_solid_capacity_profile(group_index,nb,profile_data)

#--------------------------------------------------------------------------------------------#
#------------------------------ FSI MODAL approach parameters -------------------------------#
#--------------------------------------------------------------------------------------------#

# ... imovgr - Global Mechanical Coupling
# ... imodal - Elastic Deformation/Modal

def get_modal_parameters ():
    result = FT_get_modal_parameters()
    print "get_modal_parameters, impcci: " ,result[0]
    print "get_modal_parameters, imovgr: " ,result[1]
    print "get_modal_parameters, imvtyp: " ,result[2]
    print "get_modal_parameters, imodal: " ,result[3]
    return result


def set_modal_parameters (impcci,imovgr,imvtyp,imodal):
    FT_set_modal_parameters (impcci,imovgr,imvtyp,imodal)

#--------------------------------------------------------------------------------------------#

def get_global_mechanical_coupling():
    result = FT_get_modal_parameters()
    return result[1]


def set_global_mechanical_coupling(on_or_off):
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],on_or_off,test[2],test[3])

#--------------------------------------------------------------------------------------------#

def get_rigid_motion_or_elastic_deformation():
    test = FT_get_modal_parameters()
    if (test[2] == 2):
        result = "Elastic_deformation"
    else:
        result = "Rigid_motion"
    return result


def set_rigid_motion():
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,1,0)

def set_elastic_deformation():
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,2,0)



#--------------------------------------------------------------------------------------------#

def get_rigid_motion_type():
    test = FT_get_modal_parameters()

    if (test[2] == 0):
        result = "Oscilating_body"
    if (test[2] == 1):
        result = "Off_centered_rotor"
    if (test[2] == -1):
        result = "Generalized_motion"

    return result

#--------------------------------------------------------------------------------------------#
def set_rigid_motion_oscilating_body():
    test = FT_get_modal_parameters()
    FT.set_modal_parameters(test[0],1,0,0)

def set_rigid_motion_off_centered_rotor():
    test = FT_get_modal_parameters()
    FT.set_modal_parameters(test[0],1,1,0)

def set_rigid_motion_generalized_motion():
    test = FT_get_modal_parameters()
    FT.set_modal_parameters(test[0],1,-1,0)

#--------------------------------------------------------------------------------------------#
# ... flag: 0 -> Oscilating_body, 1 -> Off_centered_rotor, -1 -> Generalized_motion
def set_rigid_motion_type (flag):
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,flag,0)



#--------------------------------------------------------------------------------------------#
def get_elastic_deformation_type():
    test = FT_get_modal_parameters()

    if (test[3] == 0):
        result = "MPCCI"
    else:
        result = "Modal"

    return result

#--------------------------------------------------------------------------------------------#
# ... flag: 0 -> MPCCI, 1 -> Modal
def set_elastic_deformation_type (flag):
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,2,flag)

#--------------------------------------------------------------------------------------------#

def set_elastic_deformation_MPCCI ():
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,2,0)

def set_elastic_deformation_Modal ():
    test = FT_get_modal_parameters()
    FT_set_modal_parameters(test[0],1,2,1)

#--------------------------------------------------------------------------------------------#


def apply_mechanical_coupled(group_ind,coupled):
    FT_apply_mechanical_coupled(group_ind,coupled)

def get_mechanical_coupled(group_ind):
    return FT_get_mechanical_coupled(group_ind)


#--------------------------------------------------------------------------------------------#
def get_structure_id_to_patch(group_ind):
    result = FT_get_structure_id_to_patch(group_ind)
    return result

def set_structure_id_to_patch(group_ind,str_id):
    FT_set_structure_id_to_patch(group_ind,str_id)


#--------------------------------------------------------------------------------------------#
def read_mechanical_coupling_parameters(group_ind,mode):
    result = FT_read_mechanical_coupling_parameters(1,group_ind,mode)

    structureFile                = result[0]
    name                         = result[1]
    initialDeformation           = result[2]
    str_id                       = result[3]
    generalizedDisplacementType  = result[4]
    generalizedDisplacementValue = result[5]
    isForced                     = result[6]
    damping                      = result[7]
    numberOfModes                = result[8]

    print "read_mechanical_coupling_parameters, str_id: ",str_id

    return result


#--------------------------------------------------------------------------------------------#
def get_modal_damping_coefficient(group_ind,mode):
    result = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    damping = result[7]
    return damping

#--------------------------------------------------------------------------------------------#
def set_modal_damping_coefficient(group_ind,mode,damping):
    param = "damping"
    FT_set_mechanical_coupling_parameter(group_ind, param, mode, damping)

#--------------------------------------------------------------------------------------------#
def get_mechanical_coupling_number_of_groups():
    result = FT_get_mechanical_coupling_number_of_groups()
    return result

#--------------------------------------------------------------------------------------------#
def get_mechanical_coupling_structureFile(group_ind):
    param = "structureFile"
    result = FT_get_mechanical_coupling_parameter(group_ind, param)
    return result

def set_mechanical_coupling_structureFile(group_ind, structureFile):
    param = "structureFile"
    FT_set_mechanical_coupling_parameter(group_ind, param, structureFile)

#--------------------------------------------------------------------------------------------#


def get_mechanical_coupling_structureName(group_ind):
    param = "structureName"
    result = FT_get_mechanical_coupling_parameter(group_ind, param)
    return result

def set_mechanical_coupling_structureName(group_ind, structureName):
    param = "structureName"
    FT_set_mechanical_coupling_parameter(group_ind, param, structureName)

#--------------------------------------------------------------------------------------------#

def get_mechanical_coupling_structureID(group_ind):
    param = "structureID"
    result = FT_get_mechanical_coupling_parameter(group_ind, param)
    return result


def set_mechanical_coupling_structureID(group_ind, ID):
    param = "structureID"
    FT_set_mechanical_coupling_parameter(group_ind, param, ID)

#--------------------------------------------------------------------------------------------#

def get_mechanical_coupling_isForced(group_ind):
    param = "isForced"
    result = FT_get_mechanical_coupling_parameter(group_ind, param)
    return result

def set_mechanical_coupling_isForced(group_ind, isForced):
    param = "isForced"
    FT_set_mechanical_coupling_parameter(group_ind, param, isForced)

#--------------------------------------------------------------------------------------------#

def get_mechanical_coupling_numberOfModes(group_ind):
    param = "numberOfModes"
    result = FT_get_mechanical_coupling_parameter(group_ind, param)
    return result

def set_mechanical_coupling_numberOfModes(group_ind, nbModes):
    param = "numberOfModes"
    FT_set_mechanical_coupling_parameter(group_ind, param, nbModes)

#--------------------------------------------------------------------------------------------#

def get_generalized_displacement_type(group_ind, mode):
    result = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    generalizedDisplacementType  = result[4]
    return generalizedDisplacementType

def set_generalized_displacement_type(group_ind, mode, type):
    param = "displacementType"
    FT_set_mechanical_coupling_parameter(group_ind, param, mode, type)

#--------------------------------------------------------------------------------------------#

def get_generalized_displacement_value(group_ind, mode):
    result = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    generalizedDisplacementValue = result[5]
    return generalizedDisplacementValue

def set_generalized_displacement_value(group_ind, mode, val):
    param = "displacementValue"
    FT_set_mechanical_coupling_parameter(group_ind, param, mode, val)

def set_generalized_displacement_profile (group_index,profile_data,mode):
    nb = len(profile_data)
    FT_set_modal_generalized_displacement_profile(group_index,nb,profile_data,mode)

def get_generalized_displacement_profile (group_index,mode):
    result = FT_get_modal_generalized_displacement_profile(group_index,mode)
    return result



#--------------------------------------------------------------------------------------------#
# FSI Modal + NLH --->
#--------------------------------------------------------------------------------------------#
def get_generalized_displacement_NLH_frequency(group_ind, mode):
    result = FT_get_patch_modal_NLH_parameters(1,group_ind, mode)
    ibpa = result[0]
    freq = result[1]
    return freq

def set_generalized_displacement_NLH_frequency(group_ind, mode, freq):
    result = FT_get_patch_modal_NLH_parameters(1,group_ind, mode)
    ibpa = result[0]
    str_ind = get_mechanical_coupling_structureID(group_ind)
    result2 = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    generalizedDisplacementValue = result2[5]
    mean = generalizedDisplacementValue
    FT_store_mechanical_coupling_parameters_NLH(0,group_ind, str_ind, mode, ibpa, freq, mean)

#--------------------------------------------------------------------------------------------#
def get_generalized_displacement_NLH_IBPA(group_ind, mode):
    result = FT_get_patch_modal_NLH_parameters(1,group_ind, mode)
    ibpa = result[0]
    freq = result[1]
    return ibpa

def set_generalized_displacement_NLH_IBPA(group_ind, mode, ibpa):
    result = FT_get_patch_modal_NLH_parameters(1,group_ind, mode)
    freq = result[1]
    str_ind = get_mechanical_coupling_structureID(group_ind)
    result2 = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    generalizedDisplacementValue = result2[5]
    mean = generalizedDisplacementValue
    print "set_generalized_displacement_NLH_IBPA, ibpa: ",ibpa
    print "set_generalized_displacement_NLH_IBPA, mean: ",mean
    print "set_generalized_displacement_NLH_IBPA, freq: ",freq
    FT_store_mechanical_coupling_parameters_NLH(0,group_ind, str_ind, mode, ibpa, freq, mean)


#--------------------------------------------------------------------------------------------#
# ... mean and generalized_displacement are one and same value, stored at one and same place
def get_generalized_displacement_NLH_mean(group_ind, mode):
    result = FT_read_mechanical_coupling_parameters(1,group_ind,mode)
    generalizedDisplacementValue = result[5]
    mean = generalizedDisplacementValue
    return mean

def set_generalized_displacement_NLH_mean(group_ind, mode, mean):
    param = "displacementValue"
    FT_set_mechanical_coupling_parameter(group_ind, param, mode, mean)


#--------------------------------------------------------------------------------------------#
# number of harmonics is a global value, not depending on any FSI parameters
def get_generalized_displacement_NLH_harmonics_number():
    result = FT_get_nb_harmonic_freq()
    return result

#--------------------------------------------------------------------------------------------#
# for each harmonic
def get_generalized_displacement_NLH_harmonics_real_value(group_ind, mode, harmonic):
    result = FT_get_fsi_harmonic_profile_value(harmonic, 0, group_ind, mode)
    real = result[1]
    return real

def set_generalized_displacement_NLH_harmonics_real_value(group_ind, mode, harmonic, real):
    result = FT_get_fsi_harmonic_profile_value(harmonic, 0, group_ind, mode)
    img = result[2]
    FT_store_fsi_harmonic_frequency_point(0,group_ind, mode, harmonic, real, img)

#--------------------------------------------------------------------------------------------#
# for each harmonic
def get_generalized_displacement_NLH_harmonics_imag_value(group_ind, mode, harmonic):
    result = FT_get_fsi_harmonic_profile_value(harmonic, 0, group_ind, mode)
    img = result[2]
    return img

def set_generalized_displacement_NLH_harmonics_imag_value(group_ind, mode, harmonic, img):
    result = FT_get_fsi_harmonic_profile_value(harmonic, 0, group_ind, mode)
    real = result[1]
    FT_store_fsi_harmonic_frequency_point(0,group_ind, mode, harmonic, real, img)

#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# Acoustic Impedance
#--------------------------------------------------------------------------------------------#

def get_acoustic_impedance_number_of_frequencies (block, face, patch):
    result = FT_get_acoustic_impedance_number_of_frequencies(block, face, patch)
    return result



#--------------------------------------------------------------------------------------------#
# CPUBooster + FMG
#--------------------------------------------------------------------------------------------#
def get_CPUBooster_FMG_parameters ():
    result = FT_get_CPUBooster_FMG_parameters()
    boofmg = result[0]
    cflbmg = result[1]
    return result

def set_CPUBooster_FMG_parameters (boofmg,cflbmg):
    FT_set_CPUBooster_FMG_parameters(boofmg,cflbmg)



#--------------------------------------------------------------------------------------------#
# ANSYS Module
#--------------------------------------------------------------------------------------------#
def get_ansys_parameters ():
    result = FT_get_ansys_parameters ()
    return result

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
#   'Input' filename
#   'Output' filename
#   'Grid units'
#   'Scale factor'
# =================================
def get_ANSYS_pressure_code():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return P
#--------------------------------------------------------------------------------------------#
def set_ANSYS_pressure_code(pressureCode):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(pressureCode,T,HTC,HF,inputFile,gridUnits,scale,outputFile)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_pressure_unit():
    res = FT_get_ansys_units_parameters()
    unitSystem = res[0]
    factor     = res[4]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_pressure_unit(unitSystem):
    FT_set_ansys_units_parameters(0,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_temperature_code():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return T
#--------------------------------------------------------------------------------------------#
def set_ANSYS_temperature_code(temperatureCode):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(P,temperatureCode,HTC,HF,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_temperature_unit():
    res = FT_get_ansys_units_parameters()
    unitSystem = res[1]
    factor     = res[5]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_temperature_unit(unitSystem):
    FT_set_ansys_units_parameters(1,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_transfer_coefficient_code():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return HTC
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_transfer_coefficient_code(htcCode):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(P,T,htcCode,HF,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_transfer_coefficient_unit():
    res = FT_get_ansys_units_parameters()
    unitSystem = res[3]
    factor     = res[7]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_transfer_coefficient_unit(unitSystem):
    FT_set_ansys_units_parameters(3,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_flux_code():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return HF
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_flux_code(heatfluxCode):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(P,T,HTC,heatfluxCode,inputFile,gridUnits,scale,outputFile)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_heat_flux_unit():
    res = FT_get_ansys_units_parameters()
    unitSystem = res[2]
    factor     = res[6]
    return unitSystem, factor
#--------------------------------------------------------------------------------------------#
def set_ANSYS_heat_flux_unit(unitSystem):
    FT_set_ansys_units_parameters(2,unitSystem)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_input_filename():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return inputFile
#--------------------------------------------------------------------------------------------#
def set_ANSYS_input_filename(inputFilename):
    # Set and read 'inputFilename'
    id1 = get_ANSYS_pressure_code()
    id2 = get_ANSYS_temperature_code()
    id3 = get_ANSYS_heat_transfer_coefficient_code()
    id4 = get_ANSYS_heat_flux_code()
    for compIdx in get_active_computations():
        FT_read_ansys_input_file(inputFilename,compIdx,id1,id2,id3,id4)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_output_filename():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return outputFile
#--------------------------------------------------------------------------------------------#
def set_ANSYS_output_filename(outputFilename):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(P,T,HTC,HF,inputFile,gridUnits,scale,outputFilename)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_grid_units():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return gridUnits
#--------------------------------------------------------------------------------------------#
def set_ANSYS_grid_units(gridunit):
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    FT_set_ansys_parameters(P,T,HTC,HF,inputFile,gridunit,scale,outputFile)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_scale_factor():
    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    return scale
#--------------------------------------------------------------------------------------------#
def set_ANSYS_scale_factor(scaleFactor):

    P,T,HTC,HF,inputFile,gridUnits,scale,outputFile = FT_get_ansys_parameters()
    
    gridUnits = 4
    if scaleFactor == 1:
        gridUnits = 2
    elif scaleFactor == 0.01:
        gridUnits = 1
    elif scaleFactor == 0.001:
        gridUnits = 0
    elif scaleFactor == 0.0254:
       gridUnits = 3
       
    FT_set_ansys_parameters(P,T,HTC,HF,inputFile,gridUnits,scaleFactor,outputFile)
        
#--------------------------------------------------------------------------------------------#

# =============================
# Get/Set reference systems :
#   Origin, point1, point2, point3 for FLUID mesh
#   Origin, point1, point2, point3 for ANSYS mesh
# =============================
def get_ANSYS_solid_mesh_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FT_get_ansys_points_parameters()
    return Point(F_ORIx, F_ORIy, F_ORIz), Point(F_PT1x, F_PT1y, F_PT1z), Point(F_PT2x, F_PT2y, F_PT2z), Point(F_PT3x, F_PT3y, F_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_mesh_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FT_get_ansys_points_parameters()
    FT_set_ansys_points_parameters(S_ORIx, S_ORIy, S_ORIz,
                                     orig.x, orig.y, orig.z,
                                     S_PT1x, S_PT1y, S_PT1z,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     S_PT2x, S_PT2y, S_PT2z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     S_PT3x, S_PT3y, S_PT3z,
                                     pnt3.x, pnt3.y, pnt3.z)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_fluid_mesh_reference_system():
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z = FT_get_ansys_points_parameters()
    return Point(S_ORIx, S_ORIy, S_ORIz), Point(S_PT1x, S_PT1y, S_PT1z), Point(S_PT2x, S_PT2y, S_PT2z), Point(S_PT3x, S_PT3y, S_PT3z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_fluid_mesh_reference_system(orig, pnt1, pnt2, pnt3):
    S_ORIx, S_ORIy, S_ORIz, F_ORIx, F_ORIy, F_ORIz, S_PT1x, S_PT1y, S_PT1z, F_PT1x, F_PT1y, F_PT1z, S_PT2x, S_PT2y, S_PT2z, F_PT2x, F_PT2y, F_PT2z, S_PT3x, S_PT3y, S_PT3z, F_PT3x, F_PT3y, F_PT3z  = FT_get_ansys_points_parameters()
    FT_set_ansys_points_parameters(orig.x, orig.y, orig.z,
                                     F_ORIx, F_ORIy, F_ORIz,
                                     pnt1.x, pnt1.y, pnt1.z,
                                     F_PT1x, F_PT1y, F_PT1z,
                                     pnt2.x, pnt2.y, pnt2.z,
                                     F_PT2x, F_PT2y, F_PT2z,
                                     pnt3.x, pnt3.y, pnt3.z,
                                     F_PT3x, F_PT3y, F_PT3z)


#--------------------------------------------------------------------------------------------#
def clear_ansys_surfaces( sID ):
    FT_remove_all_patches_from_code_ansys( sID )

#--------------------------------------------------------------------------------------------#


# =============================
# Connect patch(es) to a ANSYS face
# =============================
#   Patches list [[b1,p1], [b2,p2], ...] are connected to specified ANSYS surface (idx)

def connect_ansys_solid_face_to_patch( *args ):
    idx = args[0]
    patchList = args[1]
    FT_set_ansys_patches( idx, len(patchList), patchList )
#--------------------------------------------------------------------------------------------#

# =============================
# Get/Set connected fluid patch parameters :
#   Periodic flag
#   Rotation angle (around Z)
#   Translation vector ????
#   Partial flag
#   Nb repetitions
# =============================
def get_ANSYS_connected_fluid_patch_periodic_flag(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    return periodic_flag
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_periodic_flag(surfID, patchID, flag):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    FT_set_ansys_fluid_patch_parameters(surfID, patchID, partial_flag, flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_rotation_angle(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    return rot_angle
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_rotation_angle(surfID, patchID, angle):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    FT_set_ansys_fluid_patch_parameters(surfID, patchID, partial_flag, periodic_flag, angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_translation_vector(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    return Vector(trans_x, trans_y, trans_z)
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_translation_vector(surfID, patchID, translation):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    FT_set_ansys_fluid_patch_parameters(surfID, patchID, partial_flag, periodic_flag, rot_angle, trans_flag, translation.x, translation.y, translation.z, nb_repet)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_partial_flag(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    return partial_flag
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_partial_flag(surfID, patchID, flag):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    FT_set_ansys_fluid_patch_parameters(surfID, patchID, flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet)
#--------------------------------------------------------------------------------------------#
def get_ANSYS_connected_fluid_patch_nb_repet(surfID, patchID):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    return nb_repet
#--------------------------------------------------------------------------------------------#
def set_ANSYS_connected_fluid_patch_nb_repet(surfID, patchID, nb_repet_):
    partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet = FT_get_ansys_fluid_patch_parameters(surfID, patchID)
    FT_set_ansys_fluid_patch_parameters(surfID, patchID, partial_flag, periodic_flag, rot_angle, trans_flag, trans_x, trans_y, trans_z, nb_repet_)
#--------------------------------------------------------------------------------------------#

# =============================
# Get/Set surface parameters :
#   Interpolation type (0: non-conservative  /  1: conservative)
#   Maxi distance
# =============================
def get_ANSYS_solid_surface_list():
    surfaces = []
    surfacestmp = FT_get_ansys_surfaces()
    for sid in surfacestmp:
        surfaces.append(sid)
    return surfaces

#--------------------------------------------------------------------------------------------#
def get_ANSYS_solid_surface_interpolation_type( sID ):
    interp,max_dist = FT_get_ansys_solid_surface_parameters(sID)
    return interp
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_surface_interpolation_type( sID, interp_type ):
    interp,max_dist = FT_get_ansys_solid_surface_parameters(sID)
    FT_set_ansys_solid_surface_parameters(sID, interp_type, max_dist)

#--------------------------------------------------------------------------------------------#
def get_ANSYS_solid_surface_maximum_distance( sID ):
    interp,max_dist = FT_get_ansys_solid_surface_parameters(sID)
    return max_dist
#--------------------------------------------------------------------------------------------#
def set_ANSYS_solid_surface_maximum_distance( sID, max_distance):
    interp,max_dist = FT_get_ansys_solid_surface_parameters(sID)
    FT_set_ansys_solid_surface_parameters(sID, interp, max_distance)
#--------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------#
# TRANSITION Module
#--------------------------------------------------------------------------------------------#
# Get/set the main choice
#     0: Transition OFF
#     1: "Global Correlation Transition Model"
#     2: "Generalized Transition Model"
#--------------------------------------------------------------------------------------------#
TRANSITION_OFF                = 0
GLOBAL_CORRELATION_TRANSITION = 1
GENERALIZED_TRANSITION        = 2
#--------------------------------------------------------------------------------------------#
def get_transition_model ():
    result = FT_get_transition_model ()
    return result

def set_transition_model (model):
    # ...
    # Check transition model validity
    # ...
    if (model!=0 and model!=1 and model!=2):
        raise ValueError, "Wrong value for transition model. Must be 0, 1 or 2."
    elif model==1 or model==2:
        test = get_possible_transition_models()
        generalized_model   = test[0]
        global_correl_model = test[1]
        if (model==1 and global_correl_model==0):
            raise ValueError, "Global correlation tansition model cannot be activated with current mathematical model."
        elif (model==2 and generalized_model==0):
            raise ValueError, "Generalized transition model cannot be activated with current mesh and/or mathematical model."

    # ...
    # Model is valid, apply it !
    # ...
    FT_set_transition_model(model)


#--------------------------------------------------------------------------------------------#
# Get/set selected blade/group of blades parameters
# for Global Correlation Transition Model
#
# Model PS/SS values can be:
#
# 1 - Fully Turbulent
# 2 - Fully Laminar
# 3 - Forced Transition
# 4 - AGS model

# Hub/Shroud values for PS and SS must be in the interval 0-100%
#--------------------------------------------------------------------------------------------#
FULLY_TURBULENT   = 1
FULLY_LAMINAR     = 2
FORCED_TRANSITION = 3
AGS_MODEL         = 4
#--------------------------------------------------------------------------------------------#

def get_blade_modelPS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[0]

def set_blade_modelPS(groupID,modelPS):
    modelPS_old,hubPS,shroudPS,modelSS,hubSS,shroudSS = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

def get_blade_hubPS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[1]

def set_blade_hubPS(groupID,hubPS):
    modelPS,hubPS_old,shroudPS,modelSS,hubSS,shroudSS = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

def get_blade_shroudPS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[2]

def set_blade_shroudPS(groupID,shroudPS):
    modelPS,hubPS,shroudPS_old,modelSS,hubSS,shroudSS = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

def get_blade_modelSS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[3]

def set_blade_modelSS(groupID,modelSS):
    modelPS,hubPS,shroudPS,modelSS_old,hubSS,shroudSS = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

def get_blade_hubSS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[4]

def set_blade_hubSS(groupID,hubSS):
    modelPS,hubPS,shroudPS,modelSS,hubSS_old,shroudSS = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

def get_blade_shroudSS(groupID):
    result = FT_get_blade_parameters (groupID)
    return result[5]

def set_blade_shroudSS(groupID,shroudSS):
    modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS_old = FT_get_blade_parameters (groupID)
    FT_set_blade_parameters(groupID,modelPS,hubPS,shroudPS,modelSS,hubSS,shroudSS)

#--------------------------------------------------------------------------------------------#
def get_transition_group_blades_number ():
    result =  FT_get_names_of_blade_groups()
    nb_groups = result[0]
    return nb_groups

#--------------------------------------------------------------------------------------------#
def get_possible_transition_models ():

    test = get_mathematical_model()
    inseul = test[0]
    iturb  = test[1]
    mtetur = test[2]

    global_model_possible = 1
    local_model_possible  = 1

    if inseul == 0:
        global_model_possible = 0
        local_model_possible = 0
    else:
        if iturb == 3:
            if mtetur == 0:
                global_model_possible = 0
            else:
                global_model_possible = 0
                local_model_possible = 0
        elif iturb==2:
            if mtetur==101 or mtetur==102 or mtetur==103 or mtetur==106 or mtetur==301 or mtetur==403 or mtetur==413:
                global_model_possible = 0
                local_model_possible = 0
            elif mtetur == 411:
                local_model_possible = 0
            elif mtetur==104 or mtetur == 402:
                global_model_possible = 0

    harmo = get_harmonic_configuration()
    if harmo != 0:
        global_model_possible = 0

    cpuboo = get_cpubooster()
    if cpuboo != 0:
        global_model_possible = 0

    nb_blades = get_transition_group_blades_number()
    if nb_blades <= 0:
        local_model_possible = 0

    return [global_model_possible,local_model_possible]


#--------------------------------------------------------------------------------------------#
# ----------- GROUP / UNGROUP Blades
#--------------------------------------------------------------------------------------------#
def create_blade_group(name,value):

    if ( type(value) is types.ListType ):
        # Exhaustive list of blocks to group
        blades_list = value
    elif ( type(value) is types.StringType ):
        # Construct list from pattern
        pattern = value
        blades_list = get_blades_list(pattern)
    else:
        # WRONG TYPE FOR 'value'
        raise ValueError, "Wrong type : " + str(type(value))

    FT_group_transition_blades_(len(blades_list), blades_list, name)
    FT_update_blade_groups()


#--------------------------------------------------------------------------------------------#
def ungroup_blades(groupIndex):
    FT_ungroup_transition_blades(groupIndex)
    FT_update_blade_groups()


#--------------------------------------------------------------------------------------------#
# ----------- FINE TURBO Convergence History Page
#--------------------------------------------------------------------------------------------#

def steering_add(file, name, *values):

    index = steering_available_get_index(name)
    if index == -1:
      return

    position = steering_selected_get_count(file)
    type = FT_computationSteering_get_typeName(index, 0)

    newName = name
    count = 2
    while steering_selected_get_index(file, newName) != -1:
      newName = name + " " + str(count)
      count += 1

    if position < 0:
      return ""
    FT_computationSteering_addEntry(file, index, type)
    FT_computationSteering_setActiveDataName(file, position, newName)

    numbersOfEntries = FT_computationSteering_getActiveDataNumber(file, position)

    i = 0
    for number in xrange(len(numbersOfEntries)):
      countOfEntry = numbersOfEntries[number]
      for j in xrange(countOfEntry):
        if number == 1:
          if i + 2 >= len(values):
            print "Warning: wrong count of arguments"
          FT_computationSteering_setActiveData(file, position, number, countOfEntry, j, values[i], values[i+1], values[i+2])
          i = i + 3
        else:
          if i >= len(values):
            print "Warning: wrong count of arguments"
          FT_computationSteering_setActiveData(file, position, number, countOfEntry, j, values[i])
          i = i + 1
    return steering_selected_get_name(file, position)

def steering_add2(file, name):
    index = steering_selected_get_index(file, name)
    FT_computationSteering_addEntry2(file, index)



def steering_remove(file, name):
    index = steering_selected_get_index(file, name)
    FT_computationSteering_deleteData(file, index)

def steering_renameActiveDataValueDrawing(file, name, newName):
    index = steering_selected_get_index(file, name)
    FT_computationSteering_renameActiveDataValueDrawing(file, index, newName)

def steering_rename(file, name, newName):
    if steering_selected_get_index(file, newName) != -1:
        print "Warning: ", newName, " already exists"
        return False
    index = steering_selected_get_index(file, name)
    FT_computationSteering_setActiveDataName(file, index, newName)
    return True



def steering_set_parameters(file, name, *values):

    index = steering_selected_get_index(file, name)

    numbersOfEntries = FT_computationSteering_getActiveDataNumber(file, index)

    i = 0
    for number in xrange(len(numbersOfEntries)):
      countOfEntry = numbersOfEntries[number]
      for j in xrange(countOfEntry):
        if number == 1:
          if i+2 >= len(values):
            print "Warning: wrong count of arguments"
          FT_computationSteering_setActiveData(file, index, number, countOfEntry, j, values[i], values[i+1], values[i+2])
          i = i + 3
        else:
          if i >= len(values):
            print "Warning: wrong count of arguments"
          FT_computationSteering_setActiveData(file, index, number, countOfEntry, j, values[i])
          i = i + 1

def steering_get_parameters(file, name):

    index = steering_selected_get_index(file, name)
    list = FT_computationSteering_getActiveData(file, index)
    parameters = []
    for l in list:
        for x in l:
            parameters.append(x)
    return parameters

def steering_export_to_file(fileName, file, *variables):
    for variable in variables:
        num = steering_selected_get_index(file, variable)
        FT_computationSteering_prepare_curves_to_write(file, num)
    FT_computationSteering_write_curves_to_file(fileName)

# Additional functions

def steering_get_unsteady_type(file):
    return FT_computationSteering_get_unsteadyType_from_file(file)

def steering_get_group_names(file):
    return FT_computationSteering_get_groupNames_from_file(file)

# For selected variables

def steering_selected_get_count(file):
    return FT_computationSteering_getNumberOfEntries(file) - 1

def steering_selected_set_type(file, name, typeName):
    index = steering_selected_get_index(file, name)
    typeIndex = FT_computationSteering_getIndexOfType(typeName)
    return FT_computationSteering_setActiveDataType(file, index, typeIndex)


def steering_selected_get_type(file, name):
    index = steering_selected_get_index(file, name)
    return FT_computationSteering_getActiveDataType(file, index)

def steering_selected_get_name(file, index):
    return FT_computationSteering_getActiveDataName(file, index)

def steering_selected_get_index(file, name):
    for i in xrange(steering_selected_get_count(file)):
      if steering_selected_get_name(file, i) == name:
        return i
    print "Warning: wrong selected variable name: ", name
    return -1


# For available variables

def steering_available_get_count():
    return FT_computationSteering_get_entriesNumber()

def steering_available_get_type(name):
    index = steering_available_get_index(name)
    return FT_computationSteering_get_typeName(index, 0)

def steering_available_get_name(index):
    return FT_computationSteering_get_entryName(index)

def steering_available_get_index(name):
    for i in xrange(steering_available_get_count()):
      if steering_available_get_name(i) == name:
        return i
    print "Warning: wrong available variable name: ", name
    return -1


#--------------------------------------------------------------------------------------------#
# ----------- TASK MANAGER
#--------------------------------------------------------------------------------------------#
# ----------- Hosts definition page
#--------------------------------------------------------------------------------------------#
def add_host(machineName, machineType, lo_opt):
    FT_add_machine(machineName, machineType, lo_opt)

def get_hosts():
    return FT_get_machine_names()

def remove_host(machineName):
    FT_remove_machine(machineName)

def task_manager_shutdown():
    FT_task_manager_shutdown()

#--------------------------------------------------------------------------------------------#
# ----------- Tasks definition page
#--------------------------------------------------------------------------------------------#
def task(index):
    return Task(index)

def get_task_number():
    return FT_get_task_number()

def get_task_index(name):
    for i in xrange(FT_get_task_number()):
        if FT_get_task_name(i) == name:
            return i
    return -1 # No task with this name

def new_task(index = -1):
    FT_new_task(index)
    return Task(get_task_number() - 1)

class Task:
    def __init__(self, index):
        self.index = index

    def new_subtask(self, subindex = -1):        
        if subindex == -1:
            subTaskType = "euranusTurbo" # by default
        else:
            subTaskType = FT_get_subtask_executable(self.index, subindex)
        FT_new_subtask(self.index, subindex, subTaskType)
        new_ind =  FT_get_subtask_number(self.index)
        subindex = new_ind - 1
        FT_init_subtask_arguments(self.index, subindex)        
        return Subtask(self.index, self.get_subtask_number() - 1)

    def subtask(self, subindex):
        return Subtask(self.index, subindex)

    def remove(self):
        FT_remove_task(self.index)

    def rename(self, newName):
        number = get_task_index(newName)
        if number == -1:
            FT_set_task_name(self.index, "{", newName, "}")
            return True
        else:
            print "Warning: ", newName, " already exists"
            return False

    def save(self):
        FT_save_task_files(self.index, 0)

    def start(self):
        FT_save_task_files(self.index, 0)
        FT_start_task(self.index, 0)

    def kill(self):
        FT_stop_task(self.index)

    def delay_time(self, startTime):
        FT_set_task_startingDate(self.index, startTime)

    def delay_after_task(self, name):
        FT_set_task_startingDate(self.index, -2)
        FT_set_task_starting_after_task(self.index, "{", name, "}")

    def get_status(self):
        return FT_get_task_status(self.index)

    def get_name(self):
        return FT_get_task_name(self.index)

    def get_subtask_number(self):
        return FT_get_subtask_number(self.index)


#--------------------------------------------------------------------------------------------#
# GPU acceleration
GPU_OFF = 0 ; # GPU deactivated
GPU_ON  = 1 ; # GPU activated


# GPU memory usage
GPU_HIGH_PERF = 0 ; # High performance 
GPU_LOW_MEM   = 1 ; # Low memory
#--------------------------------------------------------------------------------------------#
class Subtask:

    def __init__(self, index, subindex):
        self.index = index
        self.subindex = subindex

    def remove(self):
        FT_remove_subtask(self.index, self.subindex)

    def kill(self):
        FT_stop_subtask(self.index, self.subindex)

    def stop(self):
        FT_suspend_subtask(self.index, self.subindex)

    def set_executable(self, subTaskType):
        FT_set_subtask_executable(self.index, self.subindex, subTaskType)
        if subTaskType!="euranusTurbo" and subTaskType!="euranusTurbodp" and subTaskType!="hexstream":
            FT_set_queuing_system_mode(self.index, self.subindex, 0)
        FT_init_subtask_arguments(self.index, self.subindex)

    def get_executable(self):
        return FT_get_subtask_executable(self.index, self.subindex)

    def set_hostName(self, subtaskHostName):
        FT_set_subtask_hostName(self.index, self.subindex, subtaskHostName)

    def get_hostName(self):
        return FT_get_subtask_hostName(self.index, self.subindex)

    def get_flag(self, number, file):
        if self.get_hostName() != FT_get_local_machine_name():
          if get_hosts()[1] != "WIN32":
            if file != "undefined":
              FT_set_subtask_localFileFlag(self.index, self.subindex, number, 1)
        return FT_get_subtask_localFileFlag(self.index, self.subindex, number)

    def set_run_file(self, run_file):
        subTaskType = self.get_executable()
        if subTaskType == "cfview":
          flag = FT_get_subtask_arguments(self.index, self.subindex, 1)[1]
          FT_set_subtask_arguments(self.index, self.subindex, 1, "-project", run_file, flag)
        else:
          flag = FT_get_subtask_arguments(self.index, self.subindex, 0)[1]          
          FT_set_subtask_arguments(self.index, self.subindex, 0, "none", run_file, flag)
          steering_file = FT_get_steering_file(run_file)
          FT_set_subtask_arguments(self.index, self.subindex, 2, "-steering", steering_file, 0)

    def get_run_file(self):
        subTaskType = self.get_executable()
        if subTaskType == "cfview":
          return FT_get_subtask_arguments(self.index, self.subindex, 1)[0][0]
        else:
          return FT_get_subtask_arguments(self.index, self.subindex, 0)[0][0]


    def set_macro_file(self, py_file):
        flag = FT_get_subtask_arguments(self.index, self.subindex, 2)[1]
        FT_set_subtask_arguments(self.index, self.subindex, 2, "-macro", py_file, flag)

    def get_macro_file(self):
        return FT_get_subtask_arguments(self.index, self.subindex, 2)[0][0]

    def set_template_file(self, trb_file):
        flag = FT_get_subtask_arguments(self.index, self.subindex, 2)[1]
        FT_set_subtask_arguments(self.index, self.subindex, 2, "none", trb_file, flag)

    def get_template_file(self):
        return FT_get_subtask_arguments(self.index, self.subindex, 2)[0][0]

    def set_geometry_file(self, geomTurbo_file):
        flag = FT_get_subtask_arguments(self.index, self.subindex, 3)[1]
        FT_set_subtask_arguments(self.index, self.subindex, 3, "none", geomTurbo_file, flag)

    def get_geometry_file(self):
        return FT_get_subtask_arguments(self.index, self.subindex, 3)[0][0]

    def set_mesh_file(self, igg_file):
        flag = FT_get_subtask_arguments(self.index, self.subindex, 4)[1]
        FT_set_subtask_arguments(self.index, self.subindex, 4, "none", igg_file, flag)

    def get_mesh_file(self):
        return FT_get_subtask_arguments(self.index, self.subindex, 4)[0][0]

    def set_condition(self, condition):
        FT_set_subtask_condition(self.index, self.subindex, condition)

    def get_condition(self):
        return FT_get_subtask_condition(self.index, self.subindex)

    def set_parallel_mode(self, parallel_mode):
        FT_set_parallel_mode(self.index, self.subindex, parallel_mode)
        if parallel_mode > 0:
            self.parallel_automatic_load_balancing()

    def get_parallel_mode(self):
        return FT_get_parallel_mode(self.index, self.subindex)

    def set_licence_type(self, licenceType):
        FT_set_subtask_fflex_licence_type(self.index, self.subindex, licenceType)

    def get_licence_type(self):
        return FT_get_subtask_fflex_licence_type(self.index, self.subindex)

# ----------- Solver configuration

    def set_compiler(self, compiler):
        FT_set_compiler_choice_subtask(self.index, self.subindex, compiler)
        ##FT_set_subtask_MPI_type(self.index, self.subindex, compiler)

    def get_compiler(self):
        return FT_get_compiler_choice_subtask(self.index, self.subindex)
        ##return FT_get_subtask_MPI_type(self.index, self.subindex)

    def get_GPU_acceleration(self):
        return FT_get_GPU_settings_subtask(self.index, self.subindex)[0]

    def set_GPU_acceleration(self, flag):
        FT_set_GPU_acceleration_subtask(self.index, self.subindex, flag)

    def get_GPU_memory_level(self):
        return FT_get_GPU_settings_subtask(self.index, self.subindex)[1]

    def set_GPU_memory_level(self, value):
        FT_set_GPU_memory_level_subtask(self.index, self.subindex, value)

    def get_GPU_number_of_devices(self):
        return FT_get_GPU_settings_subtask(self.index, self.subindex)[2]

    def set_GPU_number_of_devices(self, nb):
        FT_set_GPU_nb_devices_subtask(self.index, self.subindex, nb)

# ----------- Queuing System Mode

    def set_queuing_system(self, mode):
        FT_set_queuing_system_mode(self.index, self.subindex, mode)

    def get_queuing_system(self):
        return FT_get_queuing_system_mode(self.index, self.subindex)

    def set_number_queuing_system_processors(self, number):
        FT_set_nb_queuing_system_processor(self.index, self.subindex, number)

    def get_number_queuing_system_processors(self):
        return FT_get_nb_queuing_system_processor(self.index, self.subindex)

    def set_queuing_system_environment(self, environment):
        FT_set_queuing_system_pe(self.index, self.subindex, environment)

    def get_queuing_system_environment(self):
        return FT_get_queuing_system_pe(self.index, self.subindex)

    def get_queuing_system_environment_list(self):
        return FT_get_queuing_system_pe_list(self.index, self.subindex)

    def set_queuing_system_queue(self, queue):
        FT_set_queuing_system_queue(self.index, self.subindex, queue)

    def get_queuing_system_queue(self):
        return FT_get_queuing_system_queue(self.index, self.subindex)

    def get_queuing_system_queue_list(self):
        return FT_get_queuing_system_queue_list(self.index, self.subindex)

    def set_queuing_system_template(self, template):
        FT_set_queuing_system_template(self.index, self.subindex, template)

    def get_queuing_system_template(self):
        return FT_get_queuing_system_template(self.index, self.subindex)

    def get_queuing_system_template_list(self):
        return FT_get_queuing_system_template_list(self.index, self.subindex)

# ----------- Parallel Partitioned Settings

    def parallelpart_processes_get_count(self, pName):
        return FT_get_subtask_processes(self.index, self.subindex).count(pName)

    def parallelpart_processes_add(self, pNumber, pName):
        number = FT_get_number_of_process_name(self.index, self.subindex)
        FT_insert_subtask_processes(self.index, self.subindex, number, pNumber, pName)
        # FIX 31537
        nprocs = FT_get_number_of_process_name(self.index, self.subindex)
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        FT_set_subtask_virtual_partition(self.index, self.subindex, nprocs, result[1], result[2],
                                         result[3], result[4], result[5], result[6], result[7], result[8])

    def parallelpart_processes_change_host(self, old_pname, new_pname):
        FT_replace_all_subtask_processes(self.index, self.subindex, old_pname, new_pname)

    def parallelpart_processes_remove(self, pName):
        FT_remove_all_subtask_processes(self.index, self.subindex, pName)

    def parallelpart_set_balanceEfficiency(self, efficiency):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], efficiency,
                                        result[3], result[4], result[5], result[6], result[7], result[8])

    def parallelpart_get_balanceEfficiency(self):
        return FT_get_subtask_virtual_partition(self.index, self.subindex)[2]

    def parallelpart_set_split_block(self, split_block):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        if split_block == "INTO_TWO_SUB_BLOCKS":
            FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                                1, result[4], result[5], result[6], result[7], result[8])
        elif split_block == "INTO_N_SUB_BLOCKS":
            FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                                0, result[4], result[5], result[6], result[7], result[8])
        else:
            print "Wrong split block type!"

    def parallelpart_get_split_block(self):
        split_block = FT_get_subtask_virtual_partition(self.index, self.subindex)[3]
        if split_block == 1:
            return "INTO_TWO_SUB_BLOCKS"
        else:
            return "INTO_N_SUB_BLOCKS"

    def parallelpart_automatic_load_balancing(self):
        file = FT_get_subtask_arguments(self.index, self.subindex, 0)[0][0]
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        vnp = FT_apply_virtual_partitioning(file, result[0], result[1], result[2], result[3], 1, result[5])
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        if result[6] == 1:
            nb = FT_get_memory_estimation_from_partition(self.index, self.subindex)
            FT_set_subtask_virtual_partition(self.index, self.subindex, vnp, result[1], result[2],
                                            result[3], result[4], result[5], result[6], nb[0], nb[1])

    def parallelpart_set_static_requested_memory(self, static):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        if static == 0:
            FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                            result[3], result[4], result[5], 1, result[7], result[8])
        else:
            FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                            result[3], result[4], result[5], 0, result[7], result[8])

    def parallelpart_get_static_requested_memory(self):
        if FT_get_subtask_virtual_partition(self.index, self.subindex)[6] == 1:
            return 0
        else:
            return 1

    def parallelpart_set_requested_memory(self, nb_real, nb_int):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                        result[3], result[4], result[5], 0, nb_int, nb_real)

    def parallelpart_get_requested_memory(self):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        return result[8], result[7]

    def parallelpart_automatic_requested_memory(self):
        result = FT_get_subtask_virtual_partition(self.index, self.subindex)
        FT_set_subtask_virtual_partition(self.index, self.subindex, result[0], result[1], result[2],
                                        result[3], result[4], result[5], 1, result[7], result[8])
        self.parallelpart_automatic_load_balancing()

# ----------- Parallel Settings

    def parallel_processes_get_count(self, pName):
        return FT_get_subtask_processes(self.index, self.subindex).count(pName)

    def parallel_processes_change_host(self, subindex2, value):
        FT_change_subtask_processes(self.index, self.subindex, subindex2, value)

    def parallel_processes_change_host_perf_curve(self, subindex2, value):
        FT_change_subtask_processes_perf_curve(self.index, self.subindex, subindex2, value)

    def parallel_processes_add(self, host):
        FT_add_subtask_processes(self.index, self.subindex, host)

    def parallel_processes_remove(self, *removeIndexes):
        stringOfIndexes = str(len(removeIndexes)) + ', ' + ' '.join([str(i) for i in removeIndexes])
        FT_remove_subtask_processes(self.index, self.subindex, stringOfIndexes)

    def parallel_automatic_load_balancing(self):
        numProcs = len(FT_get_subtask_processes(self.index, self.subindex))
        FT_get_parallel_default(self.index, self.subindex, numProcs)
        FT_parallel_memory_estimation(self.index, self.subindex)

    def parallel_set_static_requested_memory(self, static):
        if static == 1:
            nb_real, nb_int = FT_get_user_memory_estimation_parallel(self.index, self.subindex)
            FT_set_user_memory_estimation_parallel(self.index, self.subindex, nb_real, nb_int)
        else:
            FT_parallel_memory_estimation(self.index, self.subindex)

    def parallel_get_static_requested_memory(self):
        if FT_get_type_of_memory_estimation_parallel(self.index, self.subindex)[0] == 1:
            return 0
        else:
            return 1

    def parallel_set_requested_memory(self, nb_real, nb_int):
        FT_set_user_memory_estimation_parallel(self.index, self.subindex, nb_real, nb_int)

    def parallel_get_requested_memory(self):
        return FT_get_user_memory_estimation_parallel(self.index, self.subindex)

    def parallel_automatic_requested_memory(self):
        FT_parallel_memory_estimation(self.index, self.subindex)

    def parallel_processes_get_block_count(self):
        return len(FT_get_subtask_blockProcessName(self.index, self.subindex))

    def parallel_processes_set_process_for_block(self, blockIndex, processIndex):
        FT_set_subtask_blockProcessName(self.index, self.subindex, blockIndex, processIndex)

    def parallel_processes_get_process_for_block(self, blockIndex):
        return FT_get_subtask_blockProcessName(self.index, self.subindex)[blockIndex]

#--------------------------------------------------------------------------------------------#
