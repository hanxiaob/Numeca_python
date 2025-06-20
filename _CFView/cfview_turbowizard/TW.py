#                                                                             #
#                          Turbo Wizard Module                                #
#_____________________________________________________________________________#
#
#    NUMECA International s.a
#
#    Implementator : Y. Elkouch
#       Date       : 22/07/2016
#______________________________________________________________________________
#
# Description: Turbomachinery post-processing module for CFView
#______________________________________________________________________________

#!/usr/bin/python
# Imports

from cfv import *

import os,sys,fileinput,string,platform,shutil,glob
import os.path

import pylab
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from subprocess import Popen, PIPE, STDOUT

from Tk import *
from math import *
import numpy as np 

def TurboWizard():
    #Interface init    
    pad = 2
    padx_image = 0
    pady_image = 0
    apath = os.path.abspath(__file__)  
    apath = apath.replace('\\','/')
    sys.path.append(apath)
    image_path = os.path.join(os.path.dirname(apath),'images/')
    image_path = image_path.replace('\\','/')
    sys.path.append(image_path)
    
    info = image_path + "info16x16b.gif"
    picture1 = image_path +"CC-Wizard-Workflow1.gif"
    picture2 = image_path +"CC-Wizard-Workflow2.gif"
    picture3 = image_path +"CC-Wizard-Workflow3.gif"
    picture4 = image_path +"CC-Wizard-Workflow4.gif"
    arrow = image_path +"rightfilled.gif"
    pic_dS_dl = [image_path +"ds_tmp.gif",image_path +"dl_tmp.gif"]
    pic_horizontal_line390 = image_path +"horline390.gif"
    pic_horizontal_line300 = image_path +"horline300.gif"

    dashline='-'*150+'\n\n'

    general_doc = 'The \\"TurboWizard\\" enables an automatic post-processing of CFView Turbomachinery\nsolution, through the use of two tools :\n\n+ the averaging of quantities on meridional (RTHZ) stations;\n+ the sampling of quantities on blades at specific span heights.\n\nThe \\"TurboWizard\\" is a 4 steps wizard.\n\n'+dashline[:-1]+dashline

    variable_shortnames={\
    'Massflow': ['Q', ['kg/s', 'kg/s', 'lbf.s/ft', 'lbf.s/ft'], '%3.3f'],\
    'Static Pressure': ['Ps', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Over Static Pressure': ['Psover', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Static Temperature': ['Ts', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Density': ['Rho', ['kg/m3', 'kg/m3', 'lbf.s2/ft4', 'lbf.s2/in4'], '%3.3f'],\
    'Absolute Total Pressure': ['Ptot', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Absolute Total Temperature': ['Ttot', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Static enthalpy': ['Hs', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Absolute total enthalpy': ['Htot', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Relative total enthalpy': ['Htrel', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Relative Total Pressure': ['Ptrel', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Relative Total Temperature': ['Ttrel', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Rotary Total Pressure': ['Ptrot', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Rotary Total Temperature': ['Ttrot', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Absolute Dynamic Pressure': ['Ptotdyn', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Relative Dynamic Pressure': ['Ptreldyn', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Rotary Dynamic Pressure': ['Ptrotdyn', ['Pa', 'Pa', 'lbf/ft2', 'psi'], '%6.0f'],\
    'Absolute Dynamic Temperature': ['Ttotdyn', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Relative Dynamic Temperature': ['Ttreldyn', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Rotary Dynamic Temperature': ['Ttrotdyn', ['K', 'K', 'R', 'R'], '%4.1f'],\
    'Rothalpy': ['Htrot', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Static energy': ['Es', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f','FO'],\
    'Static Energy': ['Es', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f','FT/FO'],\
    'Absolute Energy': ['Etot', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Relative Energy': ['Etrel', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Rotary Energy': ['Etrot', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Absolute Kinetic Energy': ['Etotkin', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Relative Kinetic Energy': ['Etrelkin', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Rotary Kinetic Energy': ['Etrotkin', ['J/kg', 'J/kg', 'ft2/s2', 'in2/s2'], '%6.0f'],\
    'Entropy': ['s', ['J/(kg.K)', 'J/(kg.K)', 'ft2/(s2.R)', 'in2/(s2.R)'], '%5.1f'],\
    'Vx': ['Vx', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vy': ['Vy', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vz': ['Vz', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vaxial': ['Vaxial', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vr': ['Vr', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vm': ['Vm', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Vt': ['Vt', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Wx': ['Wx', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Wy': ['Wy', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Wz': ['Wz', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Wt': ['Wt', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Magnitude of V': ['V', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'Magnitude of W': ['W', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.1f'],\
    'atan(Vt/Vm)': ['alpha', ['deg','deg','rad','rad'], '%3.2f'],\
    'atan(Wt/Wm)': ['beta', ['deg','deg','rad','rad'], '%3.2f'],\
    'Speed Of Sound': ['Vson', ['m/s', 'm/s', 'ft/s', 'in/s'], '%3.2f'],\
    'Absolute Mach Number': ['Ma', ['-','-','-','-'], '%3.3f'],\
    'Relative Mach Number': ['Mr', ['-','-','-','-'], '%3.3f'],\
    'Isentropic Mach Number': ['Mis', ['-','-','-','-'], '%3.3f'],\
    'k': ['k', ['m2/s2', 'm2/s2', 'ft2/s2', 'in2/s2'], '%3.1e'],\
    'epsilon': ['epsilon', ['m2/s3', 'm2/s3', 'ft2/s3', 'in2/s3'], '%3.1e'],\
    'Turbulent Viscosity (Mut/Mu)': ['MutMu', ['-','-','-','-'], '%6.0f'],\
    'Y+': ['Yp', ['-','-','-','-'], '%3.1f'],\
    'Wall Distance': ['WallDistance', ['m','m','ft','in'], '%1.1e'],\
    'Void fraction': ['VoidFraction', ['-','-','-','-'], '%3.4f','FO'],\
    'Void Fraction': ['VoidFraction', ['-','-','-','-'], '%3.4f','FT'],\
    'Dryness fraction': ['DrynessFraction', ['-','-','-','-'], '%3.4f'],\
    'Generalized dryness fraction': ['GeneralizedDrynessFraction', ['-','-','-','-'], '%3.3f'],\
    'Dynamic viscosity': ['DynamicViscosity', ['Pa.s', 'Pa.s', 'lbf.s/ft2', 'psi.s'], '%3.3e'],\
    'Thermal Conductivity': ['ThermalConductivity', ['W/m.K', 'W/m.K', 'lbf/(s.R)', 'lbf/(s.R)'], '%2.5f'],\
    'HeatCapacity': ['HeatCapacity', ['J/(kg.K)', 'J/(kg.K)', 'ft2/(s2.R)', 'in2/(s2.R)'], '%3.2f'],\
    'Gamma': ['Gamma', ['-','-','-','-'], '%2.4f'],\
    'Vorticity': ['Vorticity', ['-','-','-','-'], '%3.3e'],\
    'Vorticity_x': ['Vorticity_x', ['-','-','-','-'], '%3.3e'],\
    'Vorticity_y': ['Vorticity_y', ['-','-','-','-'], '%3.3e'],\
    'Vorticity_z': ['Vorticity_z', ['-','-','-','-'], '%3.3e'],\
    'Cp': ['Cp', ['-','-','-','-'], '%2.4f','FO'],\
    'CP1': ['CP1', ['-','-','-','-'], '%2.4f'],\
    'CP2': ['CP2', ['-','-','-','-'], '%2.4f'],\
    'CP3': ['CP3', ['-','-','-','-'], '%2.4f'],\
    'CP*1': ['CP*1', ['-','-','-','-'], '%2.4f'],\
    'CP*2': ['CP*2', ['-','-','-','-'], '%2.4f'],\
    }

    colornames = ['red','blue','green','black','brown','orange','magenta','grey','indigo','gold','turquoise','olive','lime','navajowhite','springgreen','palevioletred', 'yellow','cyan','peru','crimson','silver','goldenrod','darkviolet','limegreen','palegoldenrod','plum','maroon','yellowgreen','sandybrown','violet','darkolivegreen', 'royalblue','tan','hotpink','darkkhaki','deepskyblue','sienna','mediumpurple','teal','orchid','lightgreen','purple','dimgrey','dodgerblue','indianred','skyblue', 'deeppink','darkslateblue','darkseagreen','cornflowerblue','salmon','lightsteelblue','mediumvioletred','aquamarine']

    class mainclass():
        def __init__(self):

            self.configfile = 'None'
            self.configfilepath = ''
            self.first_step_done = False
            self.second_step_done = False
            self.third_step_done = False
            self.second_step_skipped = True
            self.third_step_skipped = True
            self.stations_dS = []
            self.stations_dl = []
            self.pos_x = 360
            self.pos_y = 155
            self.pos_x2 = 370
            self.pos_y2 = 285
            self.pos_x3 = 800
            self.pos_y3 = 155
            self.quantities_byarea = []
            self.quantities_bymass = []
            self.unit_system = 1 # default
            self.ext = '.dat'

            self.span_heights = []
            self.blades = []
            self.bladepatches = []
            self.sampled_quantities = []

            self.project_type = 'STRUCT'
            self.project_units = 1.
            self.reference_pressure = 1.
            self.reference_temperature = 1.
            self.entropy_derived = False
            self.hub_shroud_file = 'None'
            self.initial_selection = ()
            self.cut_dS_redo = True
            self.cut_dl_redo = True
            self.image_gen_cuts_redo = True
            self.sample_profile_redo = True
            self.image_gen_profiles_redo = True
            self.data_dS = []
            self.data_dl = []
            self.data_profiles = []
            self.added_var = []
            self.Npts_dl = 200
            self.must_be_present = ['Static Pressure','Static Temperature','Density','Absolute Total Pressure','Absolute Total Temperature','Static enthalpy','Absolute total enthalpy','Entropy']
            
            try:
                self.runpath = GetProjectPath()+'/'
                print ' > Path: ' + self.runpath
            except RuntimeError:
                print ' > Could Not Find Project Path'
                CFViewWarning("No project is currently opened. First open a turbomachinery solution and launch this module again.")
            [self.reference_pressure,self.reference_temperature,self.fluid_type] = self.reference_state()
            if self.fluid_type != 'Incompressible': self.must_be_present = self.must_be_present + ['Absolute Mach Number','Relative Mach Number','Isentropic Mach Number']
            
            self.mandatory_quantities()

            os.chdir(self.runpath)

        def start(self):
            self.initial_selection = GetViewActiveSurfacesList()
            self.first = first_window(self,self)
            self.first.open_popup()
                        
        def launch_post(self):
            alldata = vars(self)
            CFViewWarning('launching post-process')

            mainview_ini=ViewName()
            newview=ViewOpen(-0.5,-0.4,0.7,0.8)
            ViewPushBack()

            mainview=ViewName()
            
            self.avers = averages(self,self,self.Npts_dl)
            self.profs = profiles(self,self)
            
            for i in ['stations_dS','stations_dl','quantities_byarea','quantities_bymass','blades','sampled_quantities']:
                for j in range(len(alldata[i])-1,-1,-1):
                    if alldata[i][j]=='': alldata[i].pop(j)

            if not self.second_step_skipped :
                if self.cut_dS_redo : self.data_dS = self.avers.cut_dS(alldata['stations_dS'],alldata['quantities_byarea'],alldata['quantities_bymass'],self.TWdatapath,mainview)
                if self.cut_dl_redo : self.data_dl = self.avers.cut_dl(alldata['stations_dl'],alldata['quantities_byarea'],alldata['quantities_bymass'],self.TWdatapath,mainview)
                if self.image_gen_cuts_redo : self.avers.image_gen_cuts()

            if not self.third_step_skipped :
                if self.sample_profile_redo : self.data_profiles=self.profs.sample_profiles(alldata['blades'],alldata['bladepatches'],alldata['span_heights'],alldata['sampled_quantities'],self.TWdatapath,mainview)
                if self.image_gen_profiles_redo : self.profs.image_gen_profiles()

            ViewClose()
            ViewActivate(mainview_ini)
            SelectFromProject()
            apply(SelectedSurfacesAdd,self.initial_selection)
            self.clean_project()
            CFViewWarning('done')

        def mandatory_quantities(self):
            scalars = ['Static Pressure', 'Static Temperature', 'Density']
            vectors = ['Vxyz','Wxyz']
            config_ok = 1
            for i in scalars:
                if QntFieldExist(i) == 0 : 
                    rawErrorBox(i+" is a mandatory quantity for TurboWizard and is not present. Derive this output and launch this module again.")
                    config_ok = 0
            if QntFieldExist('Vxyz')  == 0 and QntFieldExist('Wxyz') == 0 : 
                rawErrorBox("Either Vxyz or Wxyz is needed for TurboWizard and neither are present. Derive this output and launch this module again.")
                config_ok = 0

            if QntFieldExist('Entropy') == 0 : self.entropy_derived = True
            
            if not config_ok : stop
        
        def intermediate_quantities(self,var):
            if self.project_type == 'STRUCT' : conversion = 1.
            else : conversion = 2.*pi/60.

            if QntFieldExist('Omega') == 0 : 
                QntFieldDerived(0 ,'Omega' ,'rotationSpeed*'+str(conversion) ,'' ,'0')
                self.added_var.append('Omega')
            if QntFieldExist('Vxyz')  == 0 and QntFieldExist('Wxyz') == 1 : 
                QntFieldDerived(2,'Vxyz','Wxyz_X-Omega*y','Wxyz_Y+Omega*x','Wxyz_Z')
                self.added_var.append('Vxyz')
            if QntFieldExist('Wxyz')  == 0 and QntFieldExist('Vxyz') == 1 : 
                QntFieldDerived(2,'Wxyz','Vxyz_X+Omega*y','Vxyz_Y-Omega*x','Vxyz_Z')
                self.added_var.append('Wxyz')

            if QntFieldExist('Vr')    == 0 : 
                QntFieldDerived(0 ,'Vr' ,'(x*Vxyz_X + y*Vxyz_Y)/sqrt(x*x+y*y)' ,'' ,'0')
                self.added_var.append('Vr')
            if QntFieldExist('Vt')    == 0 : 
                QntFieldDerived(0 ,'Vt' ,'(x*Vxyz_Y - y*Vxyz_X)/sqrt(x*x+y*y)' ,'' ,'0')
                self.added_var.append('Vt')
            if QntFieldExist('Vz')    == 0 : 
                QntFieldDerived(0 ,'Vz' ,'Vxyz_Z' ,'' ,'0')
                self.added_var.append('Vz')
            if QntFieldExist('Vm')    == 0 : 
                QntFieldDerived(0 ,'Vm' ,'sqrt((x*Vxyz_X+y*Vxyz_Y)*(x*Vxyz_X+y*Vxyz_Y)/(x*x+y*y)+Vxyz_Z*Vxyz_Z)' ,'' ,'0')
                self.added_var.append('Vm')
            if QntFieldExist('Wt')    == 0 : 
                QntFieldDerived(0 ,'Wt' ,'(x*Wxyz_Y - y*Wxyz_X)/sqrt(x*x+y*y)' ,'' ,'0')
                self.added_var.append('Wt')
            
            if QntFieldExist('radius') == 0 : 
                QntFieldDerived(0 ,'radius','sqrt(x*x+y*y)','' ,'')
                self.added_var.append('radius')
            if QntFieldExist('Z')      == 0 : 
                QntFieldDerived(0 ,'Z' ,'z' ,'' ,'')
                self.added_var.append('Z')
            if QntFieldExist('unity')  == 0 : 
                QntFieldDerived(0 ,'unity' ,'1' ,'' ,'')
                self.added_var.append('unity')
            if QntFieldExist('rz')     == 0 : 
                QntFieldDerived(0 ,'rz' ,'radius+z' ,'' ,'')
                self.added_var.append('rz')
            for i in self.must_be_present:
                if QntFieldExist(i) == 0 and i in var: 
                    if i == 'Entropy': ThermoDynDerQnt(i,str(self.reference_pressure),str(self.reference_temperature) ,'0')
                    else : ThermoDynDerQnt(i)
                    self.added_var.append(i)

        def clean_project(self):
            to_remove = ['unity','Z','radius','rz','Omega','Vr','Vt','Vz','Vm','Wt','Vxyz','Wxyz']
            for i in to_remove + self.must_be_present :
                if QntFieldExist(i) and i in self.added_var : QntFieldRemove(i)

        def getGroupNames(self):
            activeSurfaces  = GetViewActiveSurfacesList()
            projectSurfaces = GetProjectSurfaceList()
            groupNames = []
            for surf in projectSurfaces:
                UnselectTypeFromView('')
                SelectFromProject(surf)
                if len(GetViewActiveSurfacesList()) > 1: groupNames.append(surf)
            if 'Blades' in groupNames:groupNames.remove('Blades')
            UnselectTypeFromView('')
            SelectFromProject(*activeSurfaces)
            return groupNames

        def get_project_type(self):
            runFile=GetProjectName()+'.run'
            abs_runFile=self.runpath+runFile
            f=open(abs_runFile)
            line=f.readline()
            line=f.readline()
            if line.split()[1] == 'HEXA':self.project_type = 'unstructured'
            else : self.project_type = 'structured'
            while line:
                line=f.readline()
                if len(line.split())<2:continue
                if line.split()[0] == 'VALUE_UNITS_NAME': self.unit_system = int(line.split()[2])-1
                if line.split()[0] == 'GRIDUNIT': 
                    self.project_units = float(line.split()[1])
                    break
                
            f.close()
            return [self.project_type,self.project_units,self.unit_system]

        def reference_state(self):
            runFile=GetProjectName()+'.run'
            abs_runFile=self.runpath+runFile
            f=open(abs_runFile)
            lines=f.readlines()
            f.close()
            for i in lines:
                if len(i.split())<2:continue
                if i.split()[0] == 'TEMP_REF': self.reference_temperature = float(i.split()[1])
                if i.split()[0] == 'PRES_REF': self.reference_pressure = float(i.split()[1])
                if i.split()[0] == 'FLUID_TYPE': self.fluid_type = i.split()[1]
            return [self.reference_temperature,self.reference_pressure,self.fluid_type]

    class averages():
        def __init__(self,parent,MainClass,Npts_dl):
            self.parent = parent
            self.MainClass = MainClass
            self.Npts_dl = Npts_dl
            
        def cut_dS(self,cuts_dS,var_area,var_mass,output_path,mainview):
            print 'Data generation for surfacic station averages'
            CFViewWarning('Data generation for surfacic station averages')
            var = var_area + var_mass
            self.MainClass.intermediate_quantities(var)
            moy_dS = {}
            SetProjectWeightEquation('Density*Vxyz_X, Density*Vxyz_Y, Density*Vxyz_Z')

            nvar = len(var)
            varname = ['-']*nvar
            Q = {}
            for i in cuts_dS: moy_dS[i] = {}
            for j in range(nvar):
                if var[j] not in variable_shortnames:variable_shortnames[var[j]]=[var[j].replace(' ','').replace('/','_').replace('(','_').replace(')','_'),['-','-','-','-'],'%3.1e']
                QntFieldScalar(var[j])
                if j < len(var_area): varname[j] = var[j]+' (Area)'
                else : varname[j] = var[j]+' (Mass)'
                for i in cuts_dS:
                    print '    Surfacic average of '+varname[j]+' on '+i
                    SelectFromProject()
                    SelectFromProject(i)
                    Q[i] = Massflow()
                    if j < len(var_area) : moy_dS[i][varname[j]] = SclAverage()
                    else : moy_dS[i][varname[j]] = WeightedIntegral()

            # output files
            f=open(output_path+'stations_dS.dat','w')
            f.write('stations|Mass Flow ['+variable_shortnames['Massflow'][1][self.MainClass.unit_system]+']|')
            for j in range(nvar): f.write(varname[j]+' ['+variable_shortnames[var[j]][1][self.MainClass.unit_system]+']|')
            f.write('\n')
            for i in cuts_dS:
                f.write(i+'|'+str(Q[i])+'|')
                for j in range(nvar): f.write(str(moy_dS[i][varname[j]])+'|')
                f.write('\n')
            f.close()
            self.MainClass.cut_dS_redo = False
            self.MainClass.image_gen_cuts_redo = True
            return moy_dS

        def get_extrpoints(self):
            QntFieldScalar('radius')
            [Rmin,Rmax] = QuantityRangeActiveSurfaces()
            QntFieldScalar('Z')
            [Zmin,Zmax] = QuantityRangeActiveSurfaces()
            QntFieldScalar('rz')
            [rzmin,rzmax] = QuantityRangeActiveSurfaces()
            # determine if Rmin corresponds to Zmin or Zmax
            Rup_Zup = abs(Rmax+Zmax - rzmax)/abs(rzmax)
            Rup_Zdw = abs(Rmax+Zmin - rzmax)/abs(rzmax)
            Rdw_Zup = abs(Rmin+Zmax - rzmax)/abs(rzmax)

            if   Rup_Zup == min(Rup_Zup,Rup_Zdw,Rdw_Zup) :
                R2 = Rmax
                Z2 = Zmax
                R1 = Rmin
                Z1 = Zmin
                span0_R = 'min'
                span100_R = 'max'
                span0_Z = 'min'
                span100_Z = 'max'
            elif Rup_Zdw == min(Rup_Zup,Rup_Zdw,Rdw_Zup) :
                R2 = Rmax
                Z2 = Zmin
                R1 = Rmin
                Z1 = Zmax
                span0_R = 'min'
                span100_R = 'max'
                span0_Z = 'max'
                span100_Z = 'min'
            elif Rdw_Zup == min(Rup_Zup,Rup_Zdw,Rdw_Zup) :
                R2 = Rmin
                Z2 = Zmax
                R1 = Rmax
                Z1 = Zmin
                span0_R = 'max'
                span100_R = 'min'
                span0_Z = 'min'
                span100_Z = 'max'
            return [R1,Z1,R2,Z2,span0_R,span0_Z,span100_R,span100_Z]

        def cut_dl(self,cuts_dl,var_area,var_mass,output_path,mainview):
            print 'Data generation for curvilinear station averages'
            CFViewWarning('Data generation for curvilinear station averages')
            var = var_area + var_mass
            self.MainClass.intermediate_quantities(var)
            RTZview = ViewOpenRTZ(-0.8,0.8,-0.8,0.8)
            ViewActivate(RTZview)
            QntFieldScalar('Density')
            QntFieldScalar('Vm')

            extr   = ['-']*len(cuts_dl)
            R      = ['-']*len(cuts_dl)
            Z      = ['-']*len(cuts_dl)
            angle  = ['-']*len(cuts_dl)
            dl     = ['-']*len(cuts_dl)
            Qdl    = ['-']*len(cuts_dl)
            moy_dl = {}
            p1r    = ['-']*len(cuts_dl)
            p1z    = ['-']*len(cuts_dl)
            p2r    = ['-']*len(cuts_dl)
            p2z    = ['-']*len(cuts_dl)
            fail   = ['-']*len(cuts_dl)
            span0_R = ['-']*len(cuts_dl)
            span0_Z = ['-']*len(cuts_dl)
            span100_R = ['-']*len(cuts_dl)
            span100_Z = ['-']*len(cuts_dl)

            for i in range(len(cuts_dl)):
                SelectFromProject()
                SelectFromProject(cuts_dl[i])
                print cuts_dl[i]
                [R1,Z1,R2,Z2,span0_R[i],span0_Z[i],span100_R[i],span100_Z[i]] = self.get_extrpoints()
                
                angle[i] = atan2(R2-R1,Z2-Z1)-pi/2.
                moy_dl[cuts_dl[i]] = {}
                extr[i] = []
                R[i]   = []
                Z[i]   = []
                dl[i]  = []
                Qdl[i] = []
                p1r[i] = []
                p1z[i] = []
                p2r[i] = []
                p2z[i] = []
                fail[i] = []
                for s in range(self.Npts_dl):
                    extr[i].append((1. - cos( pi * (s + 1) / (self.Npts_dl + 1) )) / 2.)
                    R[i].append(R1 + (R2 - R1) * extr[i][s])
                    Z[i].append(Z1 + (Z2 - Z1) * extr[i][s])

                    p1r[i].append(R[i][s] + sin(angle[i]))
                    p1z[i].append(Z[i][s] + cos(angle[i]))
                    p2r[i].append(R[i][s] - sin(angle[i]))
                    p2z[i].append(Z[i][s] - cos(angle[i]))

                    SetProjectEquation(0,'eq','unity')
                    dl[i].append(CurveSegmentIntegral(p1r[i][s],0,p1z[i][s],p2r[i][s],0,p2z[i][s],0,1,0))
                    if dl[i][s] == 0.0 : # this is the case when the curvesegmentintegral() did not find the intersection between the station and (p1,p2) line.
                        # It can happen in 2 circumstances:
                        # 1. station is not restricted to the channel, i.e. it cuts other parts : in this case it will fail for all values of s. This leads to an error message and stops
                        # 2. station is ok, but the first/last points are too close to hub/shroud and therefore intersection is slightly outside domain. These points are simply disregarded in the profile. 
                        print s,extr[i][s],R[i][s],Z[i][s],angle[i]*180/pi,p1r[i][s],p1z[i][s],p2r[i][s],p2z[i][s]
                        fail[i].append(s)
                        Qdl[i].append(0.0)
                        continue

                    SetProjectEquation(0,'eq','Density*Vm')
                    Qdl[i].append(CurveSegmentIntegral(p1r[i][s],0,p1z[i][s],p2r[i][s],0,p2z[i][s],0,1,0))
                    if Qdl[i][s] == 0.0 :
                        print s,extr[i][s],R[i][s],Z[i][s],angle[i]*180/pi,p1r[i][s],p1z[i][s],p2r[i][s],p2z[i][s]
                        fail[i].append(s)
                        dl[i][s] == 0.0
                        continue

                if len(fail[i]) == self.Npts_dl : # if all points fail => bad definition of station
                    print 'for hub-to-shroud profile of azimuthal averages, stations should be restricted to the channel and cut it only once.'
                    rawErrorBox('for hub-to-shroud profile of azimuthal averages, stations should be restricted to the channel and cut it only once.')
                    stop

            nvar = len(var)
            varname = ['-']*nvar
            for j in range(nvar):
                if var[j] not in variable_shortnames:variable_shortnames[var[j]]=[var[j].replace(' ','').replace('/','_').replace('(','_').replace(')','_'),['-','-','-','-'],'%3.1e']
                QntFieldScalar(var[j])
                if j < len(var_area):
                    SetProjectEquation(0,'eq',var[j])
                    pond = dl
                    varname[j] = var[j]+' (Area)'
                else : 
                    SetProjectEquation(0,'eq','Density*Vm*'+var[j])
                    pond = Qdl
                    varname[j] = var[j]+' (Mass)'
                for i in range(len(cuts_dl)):
                    print '    Curvilinear average of '+varname[j]+' on '+cuts_dl[i]
                    #CFViewWarning('    Curvilinear average of '+varname[j]+' on '+cuts_dl[i])
                    SelectFromProject()
                    SelectFromProject(cuts_dl[i])
                    moy_dl[cuts_dl[i]][varname[j]] = ['-']*self.Npts_dl
                    for s in range(self.Npts_dl): 
                        if s not in fail[i] : moy_dl[cuts_dl[i]][varname[j]][s] = CurveSegmentIntegral(p1r[i][s],0,p1z[i][s],p2r[i][s],0,p2z[i][s],0,1,0) / pond[i][s]
                        else :                moy_dl[cuts_dl[i]][varname[j]][s] = 0.0
            ViewClose()

            # output files
            for files in glob.glob(output_path+'*_dl.dat'): os.remove(files)
            for i in range(len(cuts_dl)):
                f=open(output_path+cuts_dl[i]+'_dl.dat','w')
                f.write('span 0pc   corresponds to R_'+span0_R[i]+' and Z_'+span0_Z[i]+'\n')
                f.write('span 100pc corresponds to R_'+span100_R[i]+' and Z_'+span100_Z[i]+'\n')
                f.write('-----------------------------------------\n')
                f.write('span (pc)|z (m)|radius (m)|')
                for j in range(nvar): f.write(varname[j]+' ['+variable_shortnames[var[j]][1][self.MainClass.unit_system]+']'+'|')
                f.write('\n')
                for s in range(self.Npts_dl):
                    if s not in fail[i]:
                        f.write(str(extr[i][s])+'|'+str(Z[i][s])+'|'+str(R[i][s])+'|')
                        for j in range(nvar):f.write(str(moy_dl[cuts_dl[i]][varname[j]][s])+'|')
                        f.write('\n')
                f.close()

            ViewActivate(mainview)
            self.MainClass.cut_dl_redo = False
            self.MainClass.image_gen_cuts_redo = True
            return moy_dl
        
        def image_gen_cuts(self):

            self.MainClass.image_gen_cuts_redo = False
            
            abscissa = []
            abscissa_in_pc = []

            # various sizes
            Pic_Width_Inch  = 10
            Pic_Height_Inch = 5.5
            FontsizeTitle  = 18
            FontsizeLabel  = 16
            FontsizeLegend = 12
            FontsizeTicks  = 14
            FontsizeInsertText = 9

            for s in range(self.Npts_dl): 
                abscissa.append((1. - cos( pi * (s + 1) / (self.Npts_dl + 1) )) / 2.)
                abscissa_in_pc.append(abscissa[-1]*100)

            allcuts = []
            alltypes = []
            for i in self.MainClass.stations_dS: 
                allcuts.append(i)
                SelectFromProject()
                SelectFromProject(i)
                alltypes.append(self.get_extrpoints())
            for i in self.MainClass.stations_dl:
                if i not in allcuts:
                    allcuts.append(i)
                    SelectFromProject()
                    SelectFromProject(i)
                    alltypes.append(self.get_extrpoints())
            if len(allcuts) > 1 : 
                [R1,Z1,R2,Z2,span0_R,span0_Z,span100_R,span100_Z]=alltypes[0]
                same=True
                for i in range(1,len(allcuts)):
                    if alltypes[i][4]!=span0_R or alltypes[i][5]!=span0_Z or alltypes[i][6]!=span100_R or alltypes[i][7]!=span100_Z:same=False
                if same: alltypes.append(alltypes[0])
                else : alltypes.append([R1,Z1,R2,Z2,'mix','mix','mix','mix'])
                allcuts.append('all')
                    
            for files in glob.glob(self.MainClass.TWpicturepath+'average_*'): os.remove(files)
            print 'Picture generation for station averages'
            CFViewWarning('Picture generation for station averages')
            for i in range(len(allcuts)):
                [R1,Z1,R2,Z2,span0_R,span0_Z,span100_R,span100_Z]=alltypes[i]
                varj = []
                for j in self.MainClass.quantities_byarea+self.MainClass.quantities_bymass :
                    if j in varj:continue
                    if j not in variable_shortnames:variable_shortnames[j]=[j.replace(' ','').replace('/','_').replace('(','_').replace(')','_'),['-','-','-','-'],'%3.1e']
                    varj.append(j)
                    Figtitle = 'Spanwise evolution on '+allcuts[i]
                    ordinates = []
                    LegendList = []
                    ColorList   = []
                    LineStyleList = []
                    print '   ',j,'on',allcuts[i]
                    if allcuts[i] != 'all':
                        if allcuts[i] in self.MainClass.stations_dl:
                            if j in self.MainClass.quantities_byarea: 
                                LegendList.append('Area - profile')
                                ColorList.append(colornames[2*i])
                                LineStyleList.append('-')
                                ordinates.append(self.MainClass.data_dl[allcuts[i]][j+' (Area)'])
                            if j in self.MainClass.quantities_bymass: 
                                LegendList.append('Mass - profile')
                                ColorList.append(colornames[2*i+1])
                                LineStyleList.append('-')
                                ordinates.append(self.MainClass.data_dl[allcuts[i]][j+' (Mass)'])
                        if allcuts[i] in self.MainClass.stations_dS:
                            if j in self.MainClass.quantities_byarea:
                                LegendList.append('Area - average')
                                ColorList.append(colornames[2*i])
                                LineStyleList.append('--')
                                ordinates.append([self.MainClass.data_dS[allcuts[i]][j+' (Area)']]*self.Npts_dl)
                            if j in self.MainClass.quantities_bymass: 
                                LegendList.append('Mass - average')
                                ColorList.append(colornames[2*i+1])
                                LineStyleList.append('--')
                                ordinates.append([self.MainClass.data_dS[allcuts[i]][j+' (Mass)']]*self.Npts_dl)
                    else:
                        Figtitle = Figtitle + ' stations'
                        for k in range(len(allcuts)-1):
                            if allcuts[k] in self.MainClass.stations_dl:
                                if j in self.MainClass.quantities_byarea: 
                                    LegendList.append('Area - profile - '+allcuts[k])
                                    ColorList.append(colornames[2*k])
                                    LineStyleList.append('-')
                                    ordinates.append(self.MainClass.data_dl[allcuts[k]][j+' (Area)'])
                                if j in self.MainClass.quantities_bymass: 
                                    LegendList.append('Mass - profile - '+allcuts[k])
                                    ColorList.append(colornames[2*k+1])
                                    LineStyleList.append('-')
                                    ordinates.append(self.MainClass.data_dl[allcuts[k]][j+' (Mass)'])
                            if allcuts[k] in self.MainClass.stations_dS:
                                if j in self.MainClass.quantities_byarea:
                                    LegendList.append('Area - average - '+allcuts[k])
                                    ColorList.append(colornames[2*k])
                                    LineStyleList.append('--')
                                    ordinates.append([self.MainClass.data_dS[allcuts[k]][j+' (Area)']]*self.Npts_dl)
                                if j in self.MainClass.quantities_bymass: 
                                    LegendList.append('Mass - average - '+allcuts[k])
                                    ColorList.append(colornames[2*k+1])
                                    LineStyleList.append('--')
                                    ordinates.append([self.MainClass.data_dS[allcuts[k]][j+' (Mass)']]*self.Npts_dl)

                    FigWindow = plt.figure(figsize=(Pic_Width_Inch, Pic_Height_Inch))
                    Figaxis = FigWindow.add_subplot(111)
                    Figaxis.spines['right'].set_visible(False)
                    Figaxis.spines['top'].set_visible(False)
                    Figaxis.xaxis.set_ticks_position('bottom')
                    Figaxis.yaxis.set_ticks_position('left')

                    minord = []
                    maxord = []
                    for k in range(len(ordinates)): 
                        ord_array  = np.ma.array(ordinates[k])
                        ord_masked = np.ma.masked_where(ord_array == 0.0 , ord_array)
                        pylab.plot(ord_masked, abscissa_in_pc, ColorList[k], linestyle=LineStyleList[k],label=LegendList[k])
                        ord_MaJ = filter(lambda a: a != 0.0, ordinates[k])
                        minord.append(min(ord_MaJ))
                        maxord.append(max(ord_MaJ))

                    plt.title(Figtitle,color='k',size=FontsizeTitle)

                    Figaxis.set_xlabel('Averaged '+j+' ('+variable_shortnames[j][1][self.MainClass.unit_system]+')', fontsize=FontsizeLabel)
                    Figaxis.set_ylabel('Span (%)', fontsize=FontsizeLabel)

                    min_all = min(minord)
                    max_all = max(maxord)
                    scope = max_all - min_all 
                    eps = 0.1
                    if scope == 0.0:scope = 0.2*min_all+eps

                    # max number of major ticks
                    nb_xticks_max = max(6,min(9,13 - floor(log10(max(1e-10,abs(min_all)))))) # number of major ticks between 6 and 9

                    # adapting digits with the scope
                    xticks_digits = variable_shortnames[j][2]
                    nb_decim = int(xticks_digits[-2])
                    decim = xticks_digits[-1]=='f' # decimal format
                    expo = xticks_digits[-1]=='e' # scientific format
                    mean = 0.5*(min_all+max_all)
                    delt = scope/(nb_xticks_max-1)
                    if expo : 
                        mean = xticks_digits % mean
                        delt = xticks_digits % delt
                        nb_mean = int(mean[mean.index('e')+1:])
                        nb_delt = int(delt[delt.index('e')+1:])

                    # too few digits in decimal format                   
                    while decim and scope < 10**(-nb_decim+1):
                        nb_decim = nb_decim + 1
                        xticks_digits = xticks_digits[:3]+str(nb_decim)+'f'
                        if nb_decim > 5 : break
                    
                    # too many digits in decimal format
                    while decim and delt > 10**(-nb_decim+1) and nb_decim > 0:
                        nb_decim = nb_decim - 1
                        xticks_digits = xticks_digits[:3]+str(nb_decim)+'f'

                    if nb_decim == 0 and max_all < 1000: # keep one decimal for values below 1000   
                        nb_decim = nb_decim + 1
                        xticks_digits = xticks_digits[:3]+str(nb_decim)+'f'
                        
                    # too few digits in scientific format                   
                    while expo and nb_delt < nb_mean - nb_decim:
                        nb_decim = nb_decim + 1
                        xticks_digits = xticks_digits[:3]+str(nb_decim)+'e'
                        if nb_decim > 5 : break

                    # too many digits in scientific format                   
                    while expo and nb_delt > nb_mean - nb_decim + 1 and nb_decim > 0:
                        nb_decim = nb_decim - 1
                        xticks_digits = xticks_digits[:3]+str(nb_decim)+'e'

                    if abs(float(mean)) < 1e-3 and decim : xticks_digits = '%1.1e'
                    if abs(float(mean)) < 1e-10 : xticks_digits = '%1.0e'

                    # rounding units
                    delta_min = scope / nb_xticks_max
                    nb_digits_delta_min = ceil(log10(max(1e-10,delta_min)))
                    if   delta_min < 5.0 * 10**(nb_digits_delta_min-1) : xticks_scale = 1. * 10**(nb_digits_delta_min-1)
                    elif delta_min < 10.0 *10**(nb_digits_delta_min-1) : xticks_scale = 5. * 10**(nb_digits_delta_min-1)

                    # find out the appropriate interval to display, based on rounding units
                    min_xticks = xticks_scale*floor(min_all / xticks_scale)
                    max_xticks = xticks_scale*ceil(max_all / xticks_scale)

                    if min_all == 0. and max_all == 0.:
                        min_xticks = -1e-3
                        max_xticks = 1e-3
                        nb_xticks_max = 10
                        xticks_scale = 0.0002
                    
                    Figaxis.axis([min_xticks,max_xticks,-2,102])
                    plt.minorticks_on()
                    minorLocator = AutoMinorLocator(5)
                    Figaxis.xaxis.set_minor_locator(minorLocator)

                    Figaxis.grid(True)
                    xtext = Figaxis.get_xticklabels()
                    plt.setp(xtext, fontsize=FontsizeTicks)

                    # find out real number of major ticks and delta between ticks
                    delta_xticks_min2 = float(max_xticks - min_xticks)/float(nb_xticks_max)
                    delta_xticks_max2 = float(max_xticks - min_xticks)/float(6.)
                    delta_xticks2 = xticks_scale*ceil(min(delta_xticks_min2,delta_xticks_max2)/float(xticks_scale))

                    plt.xticks(np.arange(min_xticks,max_xticks+2*delta_xticks2,delta_xticks2))

                    xx, locs = plt.xticks()
                    xx2 = [xticks_digits % a for a in xx]
                    plt.xticks(xx, xx2)

                    ytext = Figaxis.get_yticklabels()
                    plt.setp(ytext, fontsize=FontsizeTicks)

                    plt.yticks(np.arange(0, 110, 10))
                    yticks_digits = '%.0f'

                    yy, locs = plt.yticks()
                    yy2 = [yticks_digits % a for a in yy]
                    plt.yticks(yy, yy2)

                    pos1 = Figaxis.get_position() # get the original position 
                    pos2 = [pos1.x0 - 0.03, pos1.y0 + 0.02,  pos1.width * 1.1, pos1.height * 1.0] 
                    Figaxis.set_position(pos2) # set a new position

                    plt.text(-0.085,0,r'$R_{'+span0_R+'}$\n'+r'$Z_{'+span0_Z+'}$',transform=Figaxis.transAxes,fontsize=FontsizeInsertText)
                    plt.text(-0.085,.96,r'$R_{'+span100_R+'}$\n'+r'$Z_{'+span100_Z+'}$',transform=Figaxis.transAxes,fontsize=FontsizeInsertText)
                    leg = Figaxis.legend(loc=0,labelspacing=0.2,borderpad=0.5,numpoints=1,handletextpad=0.4,handlelength=1.5,prop={'size':FontsizeLegend})

                    frame  = leg.get_frame()  
                    frame.set_facecolor('0.95')

                    figname = 'average_'+variable_shortnames[j][0]+'_'+allcuts[i].replace(' ','_')+'.png'

                    plt.savefig(self.MainClass.TWpicturepath+figname, facecolor='w', edgecolor='w', format='png')
                    plt.close()
                    # below are different conversion png->gif methods that do not work within CFView as the Image module is absent
                    #os.system('convert '+self.MainClass.TWpicturepath+figname+' '+self.MainClass.TWpicturepath+figname[:-3]+'gif')
                    #os.system('python png2gif.py '+figname)

    class profiles():
        def __init__(self,parent,MainClass):
            self.parent = parent
            self.MainClass = MainClass

        def sample_profiles(self,blades,bladepatches,spans,variables,output_path,mainview):
            print 'Data generation for blade profiles'
            CFViewWarning('Data generation for blade profiles')
            self.MainClass.intermediate_quantities(variables)

            for files in glob.glob(output_path+'profile_*.dat'): os.remove(files)
            profile_output_files = []
            for j in variables:
                if j not in variable_shortnames:variable_shortnames[j]=[j.replace(' ','').replace('/','_').replace('(','_').replace(')','_'),['-','-','-','-'],'%3.1e']
                QntFieldScalar(j)
                for i in range(len(blades)):
                    SelectFromProject()
                    apply(SelectedSurfacesAdd,bladepatches[i])
                    for s in range(len(spans)):
                        print '    Profile of',j,'on',blades[i],'at span height',spans[s],'%'
                        plotview=RprSection(float(spans[s])/100.,-10,0,float(spans[s])/100.,10,1e5,0,1.0,0.0,'',2 ,'',0)
                        ViewActivate(plotview)
                        ViewIconize()
                        PlotFctOfM()
                        FitAbscissa()
                
                        curves=GetViewCurveList()
                        apply(SelectPlotCurves,curves)
                        if len(curves)>1: merged=apply(PlotCurvesMerge,curves)
                        else : merged = curves[0]
                        curves=GetViewCurveList()
                        if len(curves)>1:merged=merged[0]
                        SelectPlotCurves(merged)
                        profile_output_files.append(output_path+'profile_'+variable_shortnames[j][0]+'_'+blades[i]+'_h'+str(spans[s])+'pc')
                        ActivePlotCurveOutput(profile_output_files[-1]+'.dat' ,merged)
                        file_saved=glob.glob(profile_output_files[-1]+'*FctOfM*.dat')[-1]
                        self.MainClass.ext = '.dat'
                        # modify filename if project is unsteady
                        if '_t' in file_saved[file_saved.index('FctOfM'):]: self.MainClass.ext=file_saved[file_saved.index('FctOfM')+len('FctOfM'):]
                        DeletePlotCurves(merged)
                        ViewActivate(mainview)

                ViewActivate(plotview)
                ViewClose()
                ViewActivate(mainview)
            self.MainClass.sample_profile_redo = False
            self.MainClass.image_gen_profiles_redo = True
            return profile_output_files

        def image_gen_profiles(self):

            self.MainClass.image_gen_profiles_redo = False
            
            abscissa = []
            abscissa_in_pc = []

            # various sizes
            Pic_Width_Inch  = 10
            Pic_Height_Inch = 5.5
            FontsizeTitle  = 18
            FontsizeLabel  = 16
            FontsizeLegend = 12
            FontsizeTicks  = 14
            FontsizeInsertText = 9

            # reading sampled data on blades
            val = []
            for j in self.MainClass.sampled_quantities :
                if j not in variable_shortnames:variable_shortnames[j]=[j.replace(' ','').replace('/','_').replace('(','_').replace(')','_'),['-','-','-','-'],'%3.1e']
                val.append([])
                chord = []
                for k in self.MainClass.blades :
                    val[-1].append([])
                    chord.append([])
                    for s in self.MainClass.span_heights :
                        nameXYZ = self.MainClass.TWdatapath+'profile_'+variable_shortnames[j][0]+'_'+k+'_h'+str(s)+'pc'+self.MainClass.ext
                        nameM = nameXYZ[:-len(self.MainClass.ext)]+j.replace(' ','').replace('/','_').replace('(','_').replace(')','_')+'FctOfM'+self.MainClass.ext
                        M = []
                        f = open(nameXYZ,'r')
                        g = open(nameM,'r')
                        linef = f.readline()
                        lineg = g.readline()
                        nb_pts = int(linef.split()[2])-1
                        val[-1][-1].append([])
                        for i in range(nb_pts):
                            linef = f.readline()
                            lineg = g.readline()
                            [X,Y,Z,v] = linef.split()
                            [Mad,v]   = lineg.split()
                            R = sqrt(float(X)**2+float(Y)**2) 
                            val[-1][-1][-1].append(float(v))
                            M.append(float(Mad)*R)
                        f.close()
                        g.close()
                        # compute corresponding chord %
                        min_M = min(M)
                        max_M = max(M)
                        chord[-1].append(['-']*nb_pts)
                        for i in range(nb_pts): chord[-1][-1][i] = (M[i]-min_M)/(max_M-min_M)*100.

            allvars = self.MainClass.sampled_quantities
            allblades = []
            for k in self.MainClass.blades:allblades.append(k)
            if len(self.MainClass.blades) > 1 : allblades.append('all')
            allspans = []
            for s in self.MainClass.span_heights:allspans.append(s)
            if len(self.MainClass.span_heights) > 1 : allspans.append('all')
            
            print 'Picture generation for blade profiles'
            CFViewWarning('Picture generation for blade profiles')

            for files in glob.glob(self.MainClass.TWpicturepath+'profile_*'): os.remove(files)

            for j in range(len(allvars)) :
                for k in range(len(allblades)) :
                    for s in range(len(allspans)) :
                        LegendList = []
                        ColorList   = []
                        LineStyleList = []
                        abscissas = []
                        ordinates = []
                        if allspans[s] != 'all' and allblades[k] != 'all': # one picture for each blade on each span height
                            Figtitle = 'Profile of '+variable_shortnames[allvars[j]][0]+' on '+allblades[k]+' at S='+str(allspans[s])+'%'
                            print '   ',Figtitle
                            LegendList.append('')
                            ColorList.append(colornames[s+k*(len(allspans)-('all' in allspans))])
                            LineStyleList.append('-')
                            abscissas.append(chord[k][s])
                            ordinates.append(val[j][k][s])
                        elif allblades[k] != 'all': # one picture for each blade on all span heights
                            Figtitle = 'Profile of '+variable_shortnames[allvars[j]][0]+' on '+allblades[k]+' at all spans'
                            print '   ',Figtitle
                            for n in range(len(allspans)-('all' in allspans)) :
                                LegendList.append('S = '+str(allspans[n])+'%')
                                ColorList.append(colornames[n+k*(len(allspans)-('all' in allspans))])
                                LineStyleList.append('-')
                                abscissas.append(chord[k][n])
                                ordinates.append(val[j][k][n])
                        elif allspans[s] != 'all': # one picture for all blades on each span height
                            Figtitle = 'Profile of '+variable_shortnames[allvars[j]][0]+' on all blades at S='+str(allspans[s])+'%'
                            print '   ',Figtitle
                            for m in range(len(allblades)-('all' in allblades)) :
                                LegendList.append(allblades[m])
                                ColorList.append(colornames[s+m*(len(allspans)-('all' in allspans))])
                                LineStyleList.append('-')
                                abscissas.append(chord[m][s])
                                ordinates.append(val[j][m][s])
                        else : # one picture for all blades on all span heights
                            Figtitle = 'Profile of '+variable_shortnames[allvars[j]][0]+' on all blades at all spans'
                            print '   ',Figtitle
                            for m in range(len(allblades)-('all' in allblades)) :
                                for n in range(len(allspans)-('all' in allspans)) :
                                    LegendList.append(allblades[m]+' - S = '+str(allspans[n])+'%')
                                    ColorList.append(colornames[n+m*(len(allspans)-('all' in allspans))])
                                    LineStyleList.append('-')
                                    abscissas.append(chord[m][n])
                                    ordinates.append(val[j][m][n])

                        FigWindow = plt.figure(figsize=(Pic_Width_Inch, Pic_Height_Inch))
                        Figaxis = FigWindow.add_subplot(111)
                        Figaxis.spines['right'].set_visible(False)
                        Figaxis.spines['top'].set_visible(False)
                        Figaxis.xaxis.set_ticks_position('bottom')
                        Figaxis.yaxis.set_ticks_position('left')

                        minord = []
                        maxord = []
                        for l in range(len(ordinates)): 
                            pylab.plot(abscissas[l], ordinates[l], ColorList[l], linestyle=LineStyleList[l],label=LegendList[l])
                            minord.append(min(ordinates[l]))
                            maxord.append(max(ordinates[l]))
                        
                        plt.title(Figtitle,color='k',size=FontsizeTitle)

                        Figaxis.set_xlabel('Chord (%)', fontsize=FontsizeLabel)
                        Figaxis.set_ylabel(allvars[j]+' ('+variable_shortnames[allvars[j]][1][self.MainClass.unit_system]+')', fontsize=FontsizeLabel)

                        plt.xticks(np.arange(0, 110, 10))
                        xticks_digits = '%.0f'

                        xx, locs = plt.xticks()
                        xx2 = [xticks_digits % a for a in xx]
                        plt.xticks(xx, xx2)

                        xtext = Figaxis.get_xticklabels()
                        plt.setp(xtext, fontsize=FontsizeTicks)

                        min_all = min(minord)
                        max_all = max(maxord)
                        scope = max_all - min_all
                        eps = 0.1
                        if scope == 0.0:scope = 0.2*min_all+eps
                    
                        # max number of major ticks
                        nb_yticks_max = max(6,min(9,13 - floor(log10(max(1e-10,abs(min_all)))))) # number of major ticks between 6 and 9

                        # adapting digits with the scope
                        yticks_digits = variable_shortnames[allvars[j]][2]
                        nb_decim = int(yticks_digits[-2])
                        decim = yticks_digits[-1]=='f' # decimal format
                        expo = yticks_digits[-1]=='e' # scientific format
                        mean = 0.5*(min_all+max_all)
                        delt = scope/(nb_yticks_max-1)
                        if expo : 
                            mean = yticks_digits % mean
                            delt = yticks_digits % delt
                            nb_mean = int(mean[mean.index('e')+1:])
                            nb_delt = int(delt[delt.index('e')+1:])

                        # too few digits in decimal format                   
                        while decim and scope < 10**(-nb_decim+1):
                            nb_decim = nb_decim + 1
                            yticks_digits = yticks_digits[:3]+str(nb_decim)+'f'
                        
                        # too many digits in decimal format
                        while decim and delt > 10**(-nb_decim+1) and nb_decim > 0:
                            nb_decim = nb_decim - 1
                            yticks_digits = yticks_digits[:3]+str(nb_decim)+'f'
                        if nb_decim == 0 and max_all < 1000: # keep one decimal for values below 1000   
                            nb_decim = nb_decim + 1
                            yticks_digits = yticks_digits[:3]+str(nb_decim)+'f'
                            
                        # too few digits in scientific format                   
                        while expo and nb_delt < nb_mean - nb_decim:
                            nb_decim = nb_decim + 1
                            yticks_digits = yticks_digits[:3]+str(nb_decim)+'e'

                        # too many digits in scientific format                   
                        while expo and nb_delt > nb_mean - nb_decim + 1 and nb_decim > 0:
                            nb_decim = nb_decim - 1
                            yticks_digits = yticks_digits[:3]+str(nb_decim)+'e'

                        if abs(float(mean)) < 1e-3 and decim : yticks_digits = '%1.1e'
                        if abs(float(mean)) < 1e-10 : yticks_digits = '%1.0e'

                        # rounding units
                        delta_min = scope / nb_yticks_max
                        nb_digits_delta_min = ceil(log10(max(1e-10,delta_min)))
                        if   delta_min < 5.0 * 10**(nb_digits_delta_min-1) : yticks_scale = 1. * 10**(nb_digits_delta_min-1)
                        elif delta_min < 10.0 *10**(nb_digits_delta_min-1) : yticks_scale = 5. * 10**(nb_digits_delta_min-1)

                        # find out the appropriate interval to display, based on rounding units
                        min_yticks = yticks_scale*floor(min_all / yticks_scale)
                        max_yticks = yticks_scale*ceil(max_all / yticks_scale)
                        if min_all == 0. and max_all == 0.:
                            min_yticks = -1e-3
                            max_yticks = 1e-3
                            nb_yticks_max = 10
                            yticks_scale = 0.0002
                            
                        Figaxis.axis([-2,102,min_yticks,max_yticks])
                        plt.minorticks_on()
                        minorLocator = AutoMinorLocator(5)
                        Figaxis.yaxis.set_minor_locator(minorLocator)

                        Figaxis.grid(True)
                        ytext = Figaxis.get_yticklabels()
                        plt.setp(ytext, fontsize=FontsizeTicks)
    
                        # find out real number of major ticks and delta between ticks
                        delta_yticks_min2 = float(max_yticks - min_yticks)/float(nb_yticks_max)
                        delta_yticks_max2 = float(max_yticks - min_yticks)/float(6.)
                        delta_yticks2 = yticks_scale*ceil(min(delta_yticks_min2,delta_yticks_max2)/float(yticks_scale))
                        plt.yticks(np.arange(min_yticks,max_yticks+delta_yticks2,delta_yticks2))

                        yy, locs = plt.yticks()
                        yy2 = [yticks_digits % a for a in yy]
                        plt.yticks(yy, yy2)

                        pos1 = Figaxis.get_position() # get the original position 
                        pos2 = [pos1.x0 , pos1.y0 + 0.02,  pos1.width * 1.1, pos1.height * 1.0] 
                        Figaxis.set_position(pos2) # set a new position

                        if LegendList != ['']:
                            leg = Figaxis.legend(loc=0,labelspacing=0.2,borderpad=0.5,numpoints=1,handletextpad=0.4,handlelength=1.5,prop={'size':FontsizeLegend})
                            frame  = leg.get_frame()  
                            frame.set_facecolor('0.95')
                        
                        figname = 'profile_'+variable_shortnames[allvars[j]][0]+'_'+allblades[k].replace(' ','_')+'_'+str(allspans[s])+'pc'+self.MainClass.ext.replace('dat','png')
                        plt.savefig(self.MainClass.TWpicturepath+figname, facecolor='w', edgecolor='w', format='png')
                        plt.close()
        
    class first_window(DialogueBox):
        def __init__(self,parent,MainClass):
            self.parent = parent
            self.MainClass = MainClass

            self.first_window_doc = general_doc+'The \\"TurboWizard\\" first step is the configuration file definition: an existing file can be\nloaded or a new one can be created.\n\nThe configuration file is a template file containing all the inputs of the\\"TurboWizard\\":\n\n+ the absolute path of the CFView Turbomachinery solution (\\".run\\" file);\n+ the type of the project (\\"structured\\" or \\"unstructured\\");\n+ the stations used for averaging with specified averaging type;\n+ the quantities to average on meridional (RTHZ) stations with specified weighting\nfactor;\n+ the absolute path of the hub & shroud definition file (only for \\"unstructured\\" project);\n+ the span heights;\n+ the name of the blades;\n+ the quantities to sample on blades.\n\nAll modifications applied in the \\"TurboWizard\\" are automatically recorded in the\nconfiguration file.\n\n'
            self.first_window_doc = self.first_window_doc +dashline+'The \\"Cancel\\" button stops the \\"TurboWizard\\" without saving.\nThe \\"Next\\" button allows to go to step 2. The button is not active when no\nconfiguration file is selected.\n'
            
        def showAt(self,x=0,y=0):
            eval_tcl_string( "wm deiconify " + self._tclName() )
            eval_tcl_string("set absx "+str(x)+" ; \
            set absy "+str(y)+" ; \
            wm geometry  " + self._tclName() + " \"+$absx+$absy\"")

        def open_popup(self):
            if isinstance(self.parent, DialogueBox): self.parent.close() # parent class is a dialog box : it is closed
            else : self.MainClass = self.parent # parent class is mainclass
            DialogueBox.__init__(self,"TurboWizard - step 1",enableBalloons = True)

            self.showAt(self.MainClass.pos_x,self.MainClass.pos_y)

            self.second = second_window(self,self.MainClass)
            self.third = third_window(self,self.MainClass)

            # Display first_step in main frame
            self.mainFrame = self.frame()
            self.mainFrame.pack(side="top",fill="both")
            self.mainFrame.image(picture1).pack(side="bottom",fill="x",padx = padx_image,pady =pady_image )
            self.docFrame = self.mainFrame.frame().pack(side="top",fill="both")
            infodoc = self.docFrame.image(info).pack(side="right",padx = pad,pady =pad)
            self.addBalloonToControl(infodoc,self.first_window_doc)

            self.configframe = self.labelframe(label="Configuration file selection").pack(side="top",fill="x",expand="yes",padx=pad,pady=pad)    

            if self.MainClass.configfile == 'None':configfile_updated = 'None'
            else : configfile_updated = self.MainClass.configfile
            self.show_config = self.configframe.label('Configuration file selected: '+configfile_updated,anchor='center').pack(side='bottom',padx=10, pady=10)
            if self.MainClass.configfile != 'None': self.addBalloonToControl(self.show_config,self.MainClass.TWpath+self.MainClass.configfile)

            self.new_config = self.configframe.button(text="Create new configuration file",command = Command(self.new_config_file)).pack(side='bottom',fill="x",expand="yes",padx=pad,pady=pad)

            self.select_config = self.configframe.button(text="Load configuration file",command = Command(self.open_config_file)).pack(side='bottom',fill="x",expand="yes",padx=pad,pady=pad)

            commonframe1  = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            self.nextstep = commonframe1.button(text="Next >>",command = Command(self.second.open_popup) ).pack(side='right',anchor ='w')
            cancel_button = commonframe1.button(text="Cancel",command = Command(self.close)).pack(side="right",anchor="w",padx=pad,pady=pad)
            self.nextstep.enable(self.MainClass.first_step_done)
 
        def new_config_file(self):
            filters = "{\
            {{*.in}\
            {*.in  -- Turbo Wizard configuration files}}\
            {{*.*}     {*.*       -- all files}}\
            }"

            FileChooserWrite("Create a new TurboWizard configuration file",command = Command(self.confignew), filter = filters)

        def confignew(self,filename):
            print 'Creation of a new configuration file'
            self.MainClass.configfile = os.path.basename(filename)
            if os.path.isfile(filename) and 'TurboWizard_' in filename :
                shutil.move(filename,filename[:filename.index('TurboWizard_')])
                filename = filename[:filename.index('TurboWizard_')]+self.MainClass.configfile

            self.MainClass.configfilepath = os.path.dirname(filename)+'/'
            self.MainClass.TWpath = self.MainClass.configfilepath+'TurboWizard_'+self.MainClass.configfile[:self.MainClass.configfile.index('.in')] + '/'
            self.MainClass.TWdatapath    = self.MainClass.TWpath + 'datafiles' + '/'
            self.MainClass.TWpicturepath = self.MainClass.TWpath + 'picturefiles' + '/'

            if os.path.isdir(self.MainClass.TWpath) :
                if os.path.isfile(self.MainClass.TWpath+self.MainClass.configfile):
                    rawErrorBox('configuration file already exists. Please select another name.')
                    return
                else:  shutil.rmtree(self.MainClass.TWpath)

            os.mkdir(self.MainClass.TWpath)
            os.mkdir(self.MainClass.TWdatapath)
            os.mkdir(self.MainClass.TWpicturepath)
            os.chdir(self.MainClass.TWpath)
            
            self.MainClass.first_step_done = True
            self.MainClass.second_step_done = False
            self.MainClass.third_step_done = False
            self.MainClass.stations_dS = []
            self.MainClass.stations_dl = []
            self.MainClass.quantities_byarea = []
            self.MainClass.quantities_bymass = []

            self.MainClass.span_heights = []
            self.MainClass.blades = []
            self.MainClass.sampled_quantities = []

            self.MainClass.project_type = 'STRUCT'
            self.MainClass.hub_shroud_file = 'None'

            f=open(filename,'w')
            f.write('runPath: '+self.MainClass.runpath+'\n')
            f.write('stations_dS: \n')
            f.write('stations_dl: \n')
            f.write('quantities_byarea: \n')
            f.write('quantities_bymass: \n')
            f.write('span_heights: \n')
            f.write('blades: \n')
            f.write('sampled_quantities: \n')
            f.write('project_type: \n')
            f.write('hub_shroud_file: \n')
            f.close()
            shutil.move(filename,self.MainClass.TWpath+self.MainClass.configfile)
            filename = self.MainClass.TWpath+self.MainClass.configfile
            
            self.addBalloonToControl(self.show_config,filename)
            self.show_config.updateLabel('Configuration file selected: '+self.MainClass.configfile)
            self.nextstep.enable(True)

        def open_config_file(self):
            filters = "{\
            {{*.in}\
            {*.in  -- Turbo Wizard configuration files}}\
            {{*.*}     {*.*       -- all files}}\
            }"

            FileChooserRead("Choose the TurboWizard configuration file", filters,command = Command(self.configread))
            
        def configread(self,filename):
            print 'Load of an existing configuration file'
            self.MainClass.configfile = os.path.basename(filename)
            self.MainClass.configfilepath = os.path.dirname(filename)+'/'

            if 'TurboWizard_' not in filename: 
                self.MainClass.configfilepath = self.MainClass.configfilepath+'TurboWizard_'+self.MainClass.configfile[:self.MainClass.configfile.index('.in')] + '/'
                if not os.path.isdir(self.MainClass.configfilepath): os.mkdir(self.MainClass.configfilepath)
                shutil.move(filename,self.MainClass.configfilepath+self.MainClass.configfile)
                
            self.MainClass.TWpath = self.MainClass.configfilepath
            self.MainClass.TWdatapath    = self.MainClass.TWpath + 'datafiles' + '/'
            self.MainClass.TWpicturepath = self.MainClass.TWpath + 'picturefiles' + '/'
            if not os.path.isdir(self.MainClass.TWdatapath): os.mkdir(self.MainClass.TWdatapath)
            if not os.path.isdir(self.MainClass.TWpicturepath): os.mkdir(self.MainClass.TWpicturepath)

            os.chdir(self.MainClass.TWpath)
            filename = self.MainClass.TWpath+self.MainClass.configfile
            self.MainClass.first_step_done = True
            self.MainClass.second_step_done = False
            self.MainClass.third_step_done = False
            f=open(filename,'r')
            lines=f.readlines()
            f.close()

            for i in lines :
                if i=='' or i=='\n':continue
                varname   = i.split(':',1)[0].strip()
                varvalues = i.split(':',1)[1].split(',')
                for j in range(len(varvalues)):
                    if varvalues[j][0]   == ' '  : varvalues[j] = varvalues[j][1:]
                    if varvalues[j][-1:] == '\n' : varvalues[j] = varvalues[j][:-1]
                    if varvalues[j][-1:] == '\r' : varvalues[j] = varvalues[j][:-1]
                    if varvalues[j].strip() == '': varvalues[j] = ''
                if varname=='runPath':runpath_read = varvalues[0]
                else:setattr(self.MainClass,varname,varvalues)
            if self.MainClass.stations_dS == [''] : self.MainClass.stations_dS = []
            if self.MainClass.stations_dl == [''] : self.MainClass.stations_dl = []
            if self.MainClass.quantities_byarea == [''] : self.MainClass.quantities_byarea = []
            if self.MainClass.quantities_bymass == [''] : self.MainClass.quantities_bymass = []
            if self.MainClass.span_heights == [''] : self.MainClass.span_heights = []
            if self.MainClass.blades == [''] : self.MainClass.blades = []
            if self.MainClass.sampled_quantities == [''] : self.MainClass.sampled_quantities = []

            self.MainClass.project_type=self.MainClass.project_type[0]
            self.MainClass.hub_shroud_file=self.MainClass.hub_shroud_file[0]
            
            # check if variables in configfile match the project
            config_ok = 1
            
            run_read = runpath_read.split('/')[-1]
            if run_read == '' or run_read == '\r' or run_read == '\n' : run_read =  runpath_read.split('/')[-2]
            run_open = self.MainClass.runpath.split('/')[-1]
            if run_open == '' or run_open == '\r' or run_open == '\n' : run_open =  self.MainClass.runpath.split('/')[-2]
            
            if runpath_read != self.MainClass.runpath and run_read != run_open: 
                config_ok = 0
                rawErrorBox('configuration file not loaded as it corresponds to another project: '+runpath_read)
            for i in self.MainClass.stations_dS+self.MainClass.stations_dl:
                if i not in self.second.cutnames and i != '': 
                    config_ok = 0
                    rawErrorBox('configuration file not loaded as it corresponds to other station names: '+i)
            for i in self.MainClass.quantities_byarea+self.MainClass.quantities_bymass:
                if i not in self.second.avevars and i != '': 
                    config_ok = 0
                    rawErrorBox('configuration file not loaded as it corresponds to unknown quantities: '+i)
            for i in self.MainClass.blades:
                if i not in self.third.bladenames and i != '': 
                    config_ok = 0
                    rawErrorBox('configuration file not loaded as it corresponds to other blade names: '+i)
            for i in self.MainClass.sampled_quantities:
                if i not in self.third.locvars and i != '': 
                    config_ok = 0
                    rawErrorBox('configuration file not loaded as it corresponds to unknown quantities: '+i)

            self.MainClass.bladepatches = []
            if config_ok == 0:
                self.MainClass.configfile = 'None'
                self.MainClass.stations_dS = []
                self.MainClass.stations_dl = []
                self.MainClass.quantities_byarea = []
                self.MainClass.quantities_bymass = []
                self.MainClass.span_heights = []
                self.MainClass.blades = []
                self.MainClass.sampled_quantities = []
                self.MainClass.project_type = 'STRUCT'
                self.MainClass.hub_shroud_file = 'None'
            else : 
                self.addBalloonToControl(self.show_config,filename)
                self.show_config.updateLabel('Configuration file selected: '+self.MainClass.configfile)
                self.nextstep.enable(True)
                if len(self.MainClass.stations_dS+self.MainClass.stations_dl) and len(self.MainClass.quantities_byarea+self.MainClass.quantities_bymass): self.MainClass.second_step_done = True

                for i in range(len(self.MainClass.blades)):
                    ind = self.third.bladenames.index(self.MainClass.blades[i])
                    self.MainClass.bladepatches.append(self.third.bladepatches[ind])
            
                if len(self.MainClass.span_heights) and self.MainClass.project_type == 'unstructured' and self.MainClass.hub_shroud_file != 'None' and len(self.MainClass.blades) and len(self.MainClass.sampled_quantities) : LoadHubAndShroud(self.MainClass.hub_shroud_file)

                if len(self.MainClass.span_heights) and (self.MainClass.project_type == 'structured' or self.MainClass.hub_shroud_file != 'None') and len(self.MainClass.blades) and len(self.MainClass.sampled_quantities) : self.MainClass.third_step_done = True

        def save_config_file(self):
            alldata = vars(self.MainClass)
            filename = self.MainClass.TWpath+self.MainClass.configfile
            f=open(filename,'w')
            f.write('runPath: '+self.MainClass.runpath+'\n')
            f.write('stations_dS: '+', '.join(map(str,alldata['stations_dS']))+'\n')
            f.write('stations_dl: '+', '.join(map(str,alldata['stations_dl']))+'\n')
            f.write('quantities_byarea: '+', '.join(map(str,alldata['quantities_byarea']))+'\n')
            f.write('quantities_bymass: '+', '.join(map(str,alldata['quantities_bymass']))+'\n')
            f.write('span_heights: '+', '.join(map(str,alldata['span_heights']))+'\n')
            f.write('blades: '+','.join(map(str,alldata['blades']))+'\n')
            f.write('sampled_quantities: '+', '.join(map(str,alldata['sampled_quantities']))+'\n')
            f.write('project_type: '+str(alldata['project_type'])+'\n')
            f.write('hub_shroud_file: '+str(alldata['hub_shroud_file'])+'\n')
            f.close()

    class second_window(DialogueBox):
        def __init__(self,parent,MainClass):
            self.parent = parent
            self.MainClass = MainClass
            self.openboxnames = []
            self.doc_stations = ['',"Surfacic average of the quantity on the whole station","hub-shroud profile of azimuthal averages along the station span"]
            self.doc_avevars = ['All scalar quantities from the Quick Access Pad are available, except:\nWall Distance, Y+, Cf, Residuals and Harmonics.\n\nMoreover, if absent, the following derivable quantities are also selectable:\nVr, Vt, Vz, Wt, Static Enthalpy, Entropy, Absolute Total Pressure,\nTemperature and Enthalpy.\n']
            if self.MainClass.fluid_type != 'Incompressible' : self.doc_avevars[0] = self.doc_avevars[0][:-2]+', Absolute, Relative and Isentropic Mach numbers.\n'

            self.doc_avevars = self.doc_avevars + ['An area-averaged quantity uses no weighting factor','A mass-averaged quantity uses a RhoV weighting factor']

            self.second_window_doc = 'The \\"TurboWizard\\" second step is used to define the inputs for the post-processing\ntool dedicated to meridional (RTHZ) station averages:\n\n+ the meridional stations to use for averaging;\n+ the quantities to average on meridional (RTHZ) stations with specified weighting\nfactor.\n\n'
            self.second_window_doc = self.second_window_doc + dashline + 'The \\"Stations\\" entry allows to select available stations. Only meridional stations\n(RTHZ) should be selected. For each station two types of averaging can be selected:\n\n+ a surfacic average on the whole station: output one value per station;\n+ a profile of azimuthal averages along the spanwise direction of the station: output\na hub-shroud profile per station.\n\n\n'
            self.second_window_doc = self.second_window_doc + 'The \\"Quantities\\" entry allows to select available quantities to be averaged on the\nmeridional stations. The button is not active until \\"Stations\\" have been defined. For\neach quantity two types of averaging can be selected:\n\n+ an area-averaging using no weighting factor;\n+ a mass-averaging using a RhoV weighting factor.\n\n'
            self.second_window_doc = self.second_window_doc + dashline + 'The \\"Cancel\\" button stops the \\"TurboWizard\\" without saving.\nThe \\"Back\\" button allows to go back to step 1.\nThe \\"Skip\\" button allows to skip the post-processing tool dedicated to meridional\n(RTHZ) station averages.\nThe \\"Next\\" button allows to go to step 3. The button is not active until both \\"Stations\\"\nand \\"Variables\\" have been defined.\n\n'
            self.second_window_doc = self.second_window_doc + dashline + 'Notes:\n+ the \\"TurboWizard\\" is not creating stations or quantities and only checks their\navailability in the project before loading the wizard. If no stations are detected, a\nwarning \\"No stations were found in the project. Skip this step or create cutting planes\nprior to launch the TurboWizard\\" will raise and the \\"Quantities\\" entry is not accessible.\nThe stations and quantities should be created before launching the \\"TurboWizard\\";\n+ For hub-shroud profiles of azimuthal averages, the stations should be restricted\nto the channel and cut it only once;\n+ Due to a current limitation, span=0% (100%) does not always correspond to hub\n(shroud) but to minimum (maximum) extrema in R,Z;\n+ The mass flow through the selected stations is also computed.\n'
          
            # gather cutnames
            SelectTypeFromProject('')
            UnselectTypeFromView('SOL')
            UnselectTypeFromView('INL')
            UnselectTypeFromView('OUT')
            UnselectTypeFromView('EXT')
            UnselectTypeFromView('MIR')
            UnselectTypeFromView('ROT')
            UnselectTypeFromView('CON')
            UnselectTypeFromView('CMB')
            UnselectTypeFromView('NMB')
            UnselectTypeFromView('PER')
            UnselectTypeFromView('PMB')
            UnselectTypeFromView('PNM')
            UnselectTypeFromView('SNG')
            SelectedSurfacesRemove('Meridional Patches')
            SelectedSurfacesRemove('Blades')
            SelectedSurfacesRemove('Connections')
            SelectedSurfacesRemove('Hub')
            SelectedSurfacesRemove('Shroud')
            UnselectFromViewRegExp('B2B*')            
            self.allcuts = GetViewActiveSurfacesList() # means it only works if cuts are created before launching the wizard

            allgroups = self.MainClass.getGroupNames()
            self.cutnames = []
            for i in self.allcuts:
                SelectFromProject(i)
                area = GmtArea()
                if area > 0. and (('.D' in i and i[:i.index('.D')] not in allgroups) or '.D' not in i): self.cutnames.append(i)

            for i in range(len(self.allcuts)):
                SelectFromProject()
                SelectFromProject(self.allcuts[i])
                sub = GetViewActiveSurfacesList()
                if len(sub)>1 : # group found : remove mixed-type groups
                    UnselectTypeFromView('SOL')
                    UnselectTypeFromView('INL')
                    UnselectTypeFromView('OUT')
                    UnselectTypeFromView('EXT')
                    UnselectTypeFromView('MIR')
                    UnselectTypeFromView('ROT')
                    UnselectTypeFromView('CON')
                    UnselectTypeFromView('CMB')
                    UnselectTypeFromView('NMB')
                    UnselectTypeFromView('PER')
                    UnselectTypeFromView('PMB')
                    UnselectTypeFromView('PNM')
                    UnselectTypeFromView('SNG')
                    sub2 = GetViewActiveSurfacesList() # means it only works if cuts are created before launching the wizard
                    if len(sub) != len(sub2) : self.cutnames.remove(sub[-1])

            # gather variable names
            allvars = GetSclQntDomainList()
            allVecvars = GetVecQntDomainList()
            if ('Wxyz' in allVecvars or 'Vxyz' in allVecvars):
                if 'Vr' not in allvars : allvars = allvars+('Vr',)
                if 'Vt' not in allvars : allvars = allvars+('Vt',)
                if 'Vz' not in allvars : allvars = allvars+('Vz',)
                if 'Wt' not in allvars : allvars = allvars+('Wt',)
            for i in self.MainClass.must_be_present:
                if i not in allvars : allvars = allvars + (i,)
            self.avevars = list(allvars)
            to_remove = ['Omega','radius','Z','unity','rz','Wall Distance','Y+','Cf']
            for i in range(len(allvars)):
                if allvars[i] in to_remove : self.avevars.remove(allvars[i])
                if 'Residual' in allvars[i]: self.avevars.remove(allvars[i])
                if 'Harmonic' in allvars[i]: self.avevars.remove(allvars[i]) # removed for now to avoid too long list

        def showAt(self,x=0,y=0):
            eval_tcl_string( "wm deiconify " + self._tclName() )
            eval_tcl_string("set absx "+str(x)+" ; \
            set absy "+str(y)+" ; \
            wm geometry  " + self._tclName() + " \"+$absx+$absy\"")
            
        def open_popup(self):
            if isinstance(self.parent, DialogueBox): self.parent.close()
            else : self.MainClass = self.parent
            DialogueBox.__init__(self,"TurboWizard - step 2",enableBalloons = True)
            self.showAt(self.MainClass.pos_x,self.MainClass.pos_y)

            self.secondFrame = self.frame()
            self.secondFrame.pack(side="top",fill="both")
            self.secondFrame.image(picture2).pack(side="bottom",fill="x",padx = padx_image,pady =pady_image )
            self.docFrame = self.secondFrame.frame().pack(side="top",fill="both")
            infodoc = self.docFrame.image(info).pack(side="right",padx = pad,pady =pad)
            self.addBalloonToControl(infodoc,self.second_window_doc)

            self.ini_dS = [0]*(len(self.cutnames)+1)
            self.ini_dl = [0]*(len(self.cutnames)+1)
            for i in range(1,len(self.cutnames)+1):
                if self.cutnames[i-1] in self.MainClass.stations_dS : self.ini_dS[i] = 1
                if self.cutnames[i-1] in self.MainClass.stations_dl : self.ini_dl[i] = 1
            
            self.ini_area = [0]*(len(self.avevars)+1)
            self.ini_mass = [0]*(len(self.avevars)+1)
            for i in range(1,len(self.avevars)+1):
                if self.avevars[i-1] in self.MainClass.quantities_byarea : self.ini_area[i] = 1
                if self.avevars[i-1] in self.MainClass.quantities_bymass : self.ini_mass[i] = 1

            self.station_names = list_checkbuttons(self.MainClass, 'stations','Select stations','For each available station, choose average possibilities',self.doc_stations,39,self.cutnames,['',''],[self.ini_dS,self.ini_dl],self.openboxnames,self)
            self.averaged_vars = list_checkbuttons(self.MainClass, 'avevars','Select quantities to average','For each desired quantity, choose the weighting factor', self.doc_avevars,39,self.avevars,['Area','Mass'],[self.ini_area,self.ini_mass],self.openboxnames,self)
            
            stationframe = self.labelframe(label="Stations").pack(side="top",fill="x",padx=pad,pady=pad)    
            self.select_station_names = stationframe.button(text="",command = Command(self.openstation_popup),image_path=arrow ).pack(side='left',padx=pad,pady=pad)
            self.infotext_station_names = stationframe.label("Choose stations on which to perform averages").pack(side='left',padx=pad,pady=pad)

            stationvarframe = self.labelframe(label="Quantities").pack(side="top",fill="x",padx=pad,pady=pad)    
            self.select_station_vars  = stationvarframe.button(text="",command = Command(self.averaged_vars.open_popup),image_path=arrow ).pack(side='left',padx=pad,pady=pad)
            self.infotext_station_vars = stationvarframe.label("Choose quantities to average").pack(side='left',padx=pad,pady=pad)

            self.select_station_vars.enable(False)
            if len(self.MainClass.stations_dS) or len(self.MainClass.stations_dl) : self.select_station_vars.enable(True)

            self.first = first_window(self,self.MainClass)
            self.third = third_window(self,self.MainClass)

            commonframe1  = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            self.nextstep = commonframe1.button(text="Next >>",command = Command(self.do_not_skip)).pack(side='right',anchor ='w')
            self.skip_button = commonframe1.button(text="Skip",command = Command(self.skip) ).pack(side='right',anchor ='w')
            self.backstep = commonframe1.button(text="<< Back",command = Command(self.first.open_popup)).pack(side='right',anchor ='w')
            cancel_button = commonframe1.button(text="Cancel",command = Command(self.close)).pack(side="right",anchor="w",padx=pad,pady=pad)

            self.nextstep.enable(self.MainClass.second_step_done)

        def openstation_popup(self):
            if len(self.cutnames) == 0: rawErrorBox('No stations were found in the project. Skip this step or create cutting planes prior to launch the TurboWizard')
            else : self.station_names.open_popup()

        def skip(self):
            self.MainClass.second_step_skipped = True
            self.third.open_popup()
            self.third.skip_button.enable(False)

        def do_not_skip(self):
            self.MainClass.second_step_skipped = False
            if len(self.cutnames) == 0: rawErrorBox('No stations were found in the project. Skip this step or create cutting planes prior to launch the TurboWizard')
            else : self.third.open_popup()

    class third_window(DialogueBox):
        def __init__(self,parent,MainClass):
            self.parent = parent
            self.MainClass = MainClass
            self.spanposts = []
            self.openboxnames = []
            self.hubshroudUnitsCombo  = None
            self.optional_factor_entry = None
            self.scaled_factor_value = 1.0
            self.doc_locvars = ['All scalar quantities from the Quick Access Pad are available, except:\nTurbulent Viscosity Ratio, Cf, Total quantities, Absolute and Relative\nMach numbers, Residuals and Harmonics.\n\nMoreover, if absent, the following derivable quantities are also\nselectable: Vt, Wt, Static Enthalpy, Entropy.\n']
            if self.MainClass.fluid_type != 'Incompressible':self.doc_locvars[0] = self.doc_locvars[0][:-2]+', Isentropic Mach number.\n'

            third_window_doc1 = 'The \\"TurboWizard\\" third step is used to define the inputs for the post-processing tool\ndedicated to the blade profiles:\n\n+ the span heights;\n+ the blade surfaces;\n+ the quantities to sample on the selected blade at the specified span heights.\n\n'
            
            STM_doc = dashline +'For this post-processing, the STM coordinates are required: As the project is\nunstructured, a hub and shroud file must be specified in order to compute the STM\ncoordinates: The syntax of this file is described in the CFView documentation.\n\n'

            third_window_doc2 = 'The \\"Span heights (%)\\" entry allows to impose the number and location in % of the\nspan heights where the blade profiles will be computed.\n\nThe \\"Blades\\" entry allows to select available blades (or group of solid patches) on\nwhich the profiles will be computed.\n\nThe \\"Quantities\\" entry allows to select available quantities to be sampled on the blades.\nThe list of quantities is independent from the quantity list selected for station averaging.\n\n'
            third_window_doc2 = third_window_doc2 +dashline +'The \\"Cancel\\" button stops the \\"TurboWizard\\" without saving.\nThe \\"Back\\" button allows to go back to step 2.\nThe \\"Skip\\" button allows to skip the post-processing tool dedicated to the blade profiles\nand to start the post-processing tool dedicated to meridional (RTHZ) station averages\nonly.\nThe \\"Start\\" button allows to start the post-processing that generates the output data\nand PNG picture files in 2 subfolders at the location of the configuration file.\n\n'
            third_window_doc2 = third_window_doc2 +dashline +'Note: the \\"TurboWizard\\" is not creating quantities and only checks their availability in\nthe project before loading the wizard. The quantities should be created before launching\nthe \\"TurboWizard\\".\n' 

            select_amongst_blades = 'Choose blades on which to sample'
            select_amongst_groups = 'Blade names not directly found.\nChoose blades amongst solid groups'

            [self.MainClass.project_type,self.MainClass.project_units,self.MainClass.unit_system] = self.MainClass.get_project_type()
            if self.MainClass.project_type != 'unstructured': STM_doc=''
            self.third_window_doc = third_window_doc1+ STM_doc + dashline + third_window_doc2

            # gather solid group names
            SelectFromProject('')
            SelectTypeFromProject('SOL')
            SelectedSurfacesRemove('Hub')
            SelectedSurfacesRemove('Shroud')
            SelectedSurfacesRemove('Blades')
            allcuts = GetViewActiveSurfacesList()
            allgroups = self.MainClass.getGroupNames()
            self.solid_groups = []
            for i in allcuts:
                if i in allgroups: self.solid_groups.append(i)
            [self.n_blades,self.bladenames,self.bladepatches] = self.distinguishBlades(self.solid_groups)
            if self.n_blades == 0: 
                self.text_blade_popup = select_amongst_groups
                self.doc_blades=['TurboWizard could not detect automatically the blade patches.\nThe user should select the blades amongst the solid groups.\n']
            else : 
                self.text_blade_popup = select_amongst_blades
                self.doc_blades=['TurboWizard detected automatically the blades, allowing\nthe user to select directly amongst the blade names.\n']

            allvars    = GetSclQntDomainList()
            allVecvars = GetVecQntDomainList()

            if ('Wxyz' in allVecvars or 'Vxyz' in allVecvars):
                if 'Vt' not in allvars : allvars = allvars+('Vt',)
                if 'Wt' not in allvars : allvars = allvars+('Wt',)
            
            for i in self.MainClass.must_be_present:
                if i not in allvars : allvars = allvars + (i,)
            self.locvars = list(allvars)
            to_remove = ['Omega','radius','Z','unity','rz','Cf','Vr','Vz','Vm','Turbulent Viscosity (Mut/Mu)','Absolute Total Pressure','Absolute Total Temperature','Absolute total enthalpy','Absolute Mach Number','Relative Mach Number']
            for i in range(len(allvars)):
                if allvars[i] in to_remove : self.locvars.remove(allvars[i])
                if 'Residual' in allvars[i]: self.locvars.remove(allvars[i])
                if 'Harmonic' in allvars[i]: self.locvars.remove(allvars[i]) # removed for now to avoid too long list

        def showAt(self,x=0,y=0):
            eval_tcl_string( "wm deiconify " + self._tclName() )
            eval_tcl_string("set absx "+str(x)+" ; \
            set absy "+str(y)+" ; \
            wm geometry  " + self._tclName() + " \"+$absx+$absy\"")

        def open_popup(self):
            if isinstance(self.parent, DialogueBox): 
                self.parent.close()
                if 'allprocesses' in vars(self.parent):
                    for i in self.parent.allprocesses:
                        if i.poll() == None: i.terminate()
                    
            else : self.MainClass = self.parent
            DialogueBox.__init__(self,"TurboWizard - step 3",enableBalloons = True)
            self.showAt(self.MainClass.pos_x,self.MainClass.pos_y)

            self.thirdFrame = self.frame()
            self.thirdFrame.pack(side="top",fill="both")
            self.thirdFrame.image(picture3).pack(side="bottom",fill="x",padx = padx_image,pady =pady_image )
            self.docFrame = self.thirdFrame.frame().pack(side="top",fill="both")
            infodoc = self.docFrame.image(info).pack(side="right",padx = pad,pady =pad)
            self.addBalloonToControl(infodoc,self.third_window_doc)

            self.ini_blades = [0]*(len(self.bladenames)+1)
            for i in range(1,len(self.bladenames)+1):
                if self.bladenames[i-1] in self.MainClass.blades : self.ini_blades[i] = 1

            self.ini_loc = [0]*(len(self.locvars)+1)
            for i in range(1,len(self.locvars)+1):
                if self.locvars[i-1] in self.MainClass.sampled_quantities : self.ini_loc[i] = 1

            if self.MainClass.project_type == 'unstructured' : self.hub_shroud_file_chooser()

            self.allspan = self.labelframe(label="Span heights (%)").pack(side="top",fill="x",padx=pad,pady=pad)

            self.span1   = self.allspan.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            for i in range(len(MainClass.span_heights)):
                self.newentry = self.span1.entry(label=" ",value = MainClass.span_heights[i],width = 4,command=Command(self.save_spans)).pack(side = "left",fill = "y",padx = pad)
                self.spanposts.append(self.newentry)
            if not len(self.spanposts):
                self.firsth = self.span1.entry(label=" " , value = 0.0 , width = 4,command=Command(self.save_spans)).pack( side = "left" , fill = "y" , padx = pad)
                self.spanposts.append(self.firsth)
            self.newentry   = self.span1.entry(label=" " , value = 0.0 , width = 4,command=Command(self.save_spans)).unpack()

            self.span2       = self.allspan.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            self.moinsbutton = self.span2.button(text="-",command = Command(self.delspanentry)).pack(side='left',expand="no")
            self.plusbutton  = self.span2.button(text="+",command = Command(self.addspanentry)).pack(side='left',expand="no")
            if self.MainClass.project_type == 'unstructured' and self.MainClass.hub_shroud_file == 'None' :
                self.moinsbutton.enable(False)
                self.plusbutton.enable(False)

            blade_names = list_checkbuttons(self.MainClass, 'blades','Select blades',self.text_blade_popup,self.doc_blades,33,self.bladenames,[''],[self.ini_blades],self.openboxnames,self)
            local_vars  = list_checkbuttons(self.MainClass, 'locvars','Select quantities','Choose quantities to sample on blades', self.doc_locvars,33,self.locvars,[''],[self.ini_loc],self.openboxnames,self)

            spanbuttonblade = self.labelframe(label="Blades").pack(side="top",fill="x",padx=pad,pady=pad)    
            self.select_blade_names  = spanbuttonblade.button(text="",command = Command(blade_names.open_popup),image_path=arrow).pack(side='left',padx=pad,pady=pad)
            self.infotext_blade_names = spanbuttonblade.label("Choose blades on which to sample local profiles").pack(side='left',padx=pad,pady=pad)
            self.select_blade_names.enable(False)
            if len(self.MainClass.span_heights) and (self.MainClass.project_type == 'structured' or self.MainClass.hub_shroud_file != 'None'):self.select_blade_names.enable(True)

            spanbuttonvars    = self.labelframe(label="Quantities").pack(side="top",fill="x",padx=pad,pady=pad)    
            self.select_profile_vars = spanbuttonvars.button(text="",command = Command(local_vars.open_popup ),image_path=arrow).pack(side='left',padx=pad,pady=pad)
            self.infotext_profile_vars = spanbuttonvars.label("Choose quantities to sample on blades").pack(side='left',padx=pad,pady=pad)

            if len(self.MainClass.span_heights) and (self.MainClass.project_type == 'structured' or self.MainClass.hub_shroud_file != 'None') and len(self.MainClass.blades) : self.select_profile_vars.enable(True)
            else : self.select_profile_vars.enable(False)

            self.second = second_window(self,self.MainClass)
            self.fourth = fourth_window(self,self.MainClass)

            commonframe1  = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            self.launch_button = commonframe1.button(text="Start",command = Command(self.do_not_skip) ).pack(side='right',anchor ='w',padx=pad,pady=pad)
            self.skip_button = commonframe1.button(text="Skip",command = Command(self.skip) ).pack(side='right',anchor ='w',padx=pad,pady=pad)
            self.backstep  = commonframe1.button(text="<< Back",command = Command(self.second.open_popup)).pack(side='right',anchor ='w',padx=pad,pady=pad)
            cancel_button = commonframe1.button(text="Cancel",command = Command(self.close)).pack(side="right",anchor="w",padx=pad,pady=pad)
            self.launch_button.enable(self.MainClass.third_step_done)

        def skip(self):
            self.MainClass.third_step_skipped = True
            self.fourth.open_popup()

        def do_not_skip(self):
            self.MainClass.third_step_skipped = False
            self.fourth.open_popup()

        def distinguishBlades(self,solid_groups):
            # create patches lists for each solid group
            solid_group_patches = ['-']*len(solid_groups)
            for i in range(len(solid_groups)):
                SelectFromProject()
                SelectFromProject(solid_groups[i])
                solid_group_patches[i] = list(GetViewActiveSurfacesList())[:-1]

            # figure out number of blades and current grouping situation
            SelectFromProject()
            SelectFromViewRegExp('skin_blade')
            SelectFromViewRegExp('skinUp_blade')
            SelectFromViewRegExp('skinDown_blade')
            SelectFromViewRegExp('skin.Imin blade')
            SelectFromViewRegExp('skinUp.Imin blade')
            SelectFromViewRegExp('skinDown.Imin blade')
            n_blades = len(GetViewActiveSurfacesList()) / 2
            if n_blades == 0: 
                print 'blade names not found, showing solid group names'
                return [n_blades,solid_groups,solid_group_patches]

            allgroups = self.MainClass.getGroupNames()
            inigroups = []
            for i in range(len(allgroups)):
                SelectFromProject()
                SelectFromProject(allgroups[i])
                allpatches = GetViewActiveSurfacesList()
                for j in range(len(allpatches)):
                    if 'skin_blade' in allpatches[j] or 'skinUp_blade' in allpatches[j] or 'skinDown_blade' in allpatches[j] or 'skin.Imin blade' in allpatches[j]:
                        if allgroups[i] not in inigroups : inigroups.append(allgroups[i])

            # figure out blades names
            SelectFromProject()
            SelectFromViewRegExp('skin_blade')
            SelectFromViewRegExp('skinUp_blade')
            SelectFromViewRegExp('skinDown_blade')
            SelectFromViewRegExp('skin.Imin blade')
            allpatches = GetViewActiveSurfacesList()
            bladenames = []
            for j in range(len(allpatches)):
                if 'skin_blade' in allpatches[j]: prefix = allpatches[j][:allpatches[j].index('skin_blade')-1]
                elif 'skinUp_blade' in allpatches[j]: prefix = allpatches[j][:allpatches[j].index('skinUp_blade')-1]
                elif 'skinDown_blade' in allpatches[j]: prefix = allpatches[j][:allpatches[j].index('skinDown_blade')-1]
                elif 'skin.Imin blade' in allpatches[j]: prefix = allpatches[j][:allpatches[j].index('skin.Imin blade')-1]
                if prefix not in bladenames : bladenames.append(prefix)
            # handle badly grouped blade patches
            
            if len(inigroups) == n_blades: 
                print 'blades already correctly grouped'
                bladenames=inigroups
                bladepatches = []
                for j in bladenames:
                    SelectFromProject()
                    SelectFromProject(j)
                    bladepatches.append(list(GetViewActiveSurfacesList()))

            elif len(inigroups) == 0: # if blade patches are not grouped, a temp group is created
                print 'blade patches are not grouped'
                SelectTypeFromProject('SOL')
                for i in allgroups: UnselectFromViewRegExp(i)
                indiv_sol_patches = list(GetViewActiveSurfacesList())
                if 'Blades' in indiv_sol_patches:indiv_sol_patches.remove('Blades')
                inigroups = ['tmp_group']
                apply(CreateSurfaceGroup,inigroups+indiv_sol_patches)

            if len(inigroups) != n_blades: 
                print 'blades are not separated in independent groups'
                # associate blade names with lists of patches
                bladepatches_unsorted = []
                for i in inigroups: # will work only if all the patches of a blade are included in the same group
                    for j in range(n_blades):
                        SelectFromProject()
                        SelectFromProject(i)
                        bladepatches_unsorted.append(list(GetViewActiveSurfacesList()))
                         # remove patches unrelated to the current blade
                        for k in range(len(bladepatches_unsorted[-1])-1,-1,-1):
                            if bladenames[j] not in bladepatches_unsorted[-1][k]: bladepatches_unsorted[-1].remove(bladepatches_unsorted[-1][k])
                        if len(bladepatches_unsorted[-1]) == 0:bladepatches_unsorted.pop()
                        # remove temporary group
                        if i == 'tmp_group':GroupRemove(i)

                # sort correctly bladepatches, if necessary
                bladepatches = ['']*n_blades
                for i in range(n_blades):
                    for j in range(len(bladepatches_unsorted)):
                        if bladenames[i] in bladepatches_unsorted[j][0]:bladepatches[i]=bladepatches_unsorted[j]
                        
            return [n_blades,bladenames,bladepatches]
            
        def hub_shroud_file_chooser(self):
            self.hubshroud = self.labelframe(label="Hub & Shroud File Selection").pack(side="top",fill="x",padx=pad,pady=pad)

            conversion_factor = 'found' # CFView finds automatically the conversion to apply => following code is obsolete
            if conversion_factor == 'not_found':
                self.hubshroudUnitsFrame1 = self.hubshroud.frame().pack(side="top",fill="x",padx=pad,pady=pad)

                self.hubshroudUnitsName = self.hubshroudUnitsFrame1.frame().pack(side="left",expand="no")
                name = self.hubshroudUnitsName.label(text='Units            ').pack(side="left",expand="no")

                self.hubshroudUnitsAvailable = ['    --- Choose Units ---','Millimeters','Centimeters','Meters','Inches','User defined scale factor']
                self.hubshroudUnitsCombo  = self.hubshroudUnitsFrame1.combobox( items=self.hubshroudUnitsAvailable,command=Command(self.adapthubshroudunits))
                self.hubshroudUnitsCombo.pack(side="left",expand="no")
                self.optional_factor_entry = self.hubshroudUnitsFrame1.entry(label="Factor: " , value = 1.0 , width = 4,command=Command(self.scaled_factor)).unpack()

            filtersHS = "{\
            {{*hub_shroud.dat *.cgns}\
            {*hub_shroud.dat *.cgns -- Hub & Shroud .dat & .cgns files}}\
            {{*hub_shroud.dat}\
            {*hub_shroud.dat  -- Hub & Shroud .dat files}}\
            {{*.cgns}\
            {*.cgns  -- Hub & Shroud .cgns files}}\
            {{*.*}     {*.*       -- all files}}\
            }"
            self.hubshroudFileChooser = FileEntry(self.hubshroud,label = " File name      ",title = "Select a valid Hub and Shroud File",value=self.MainClass.hub_shroud_file,filter = filtersHS,command = Command(self.loadhubshroudFile))
            self.hubshroudFileChooser.pack(side="top", fill="x", expand="yes", padx=pad, pady=10)

        def adapthubshroudunits(self,info=""):
            if self.hubshroudUnitsCombo != None : 
                HS_unitname = self.hubshroudUnitsCombo.getValue()
                if HS_unitname == 'Millimeters': HS_units = 0.001
                elif HS_unitname == 'Centimeters' : HS_units = 0.01
                elif HS_unitname == 'Meters' : HS_units = 1.0
                elif HS_unitname == 'Inches' : HS_units = 0.0254
                else : HS_units = self.scaled_factor_value

                if 'User' in HS_unitname : self.optional_factor_entry.pack(side="right",expand="no")
                else :  self.optional_factor_entry.unpack()

                if HS_units != MainClass.project_units:
                    conversion = HS_units/MainClass.project_units
                    SetAG5Conversion(conversion)
                    print 'lets do something about it', conversion

        def scaled_factor(self):
            if self.optional_factor_entry != None : 
                try: 
                    self.scaled_factor_value = self.optional_factor_entry.getFloatValue()
                    self.adapthubshroudunits("")
                except ValueError:rawErrorBox('Please enter a float value.')
            
        def loadhubshroudFile(self,filename):
            LoadHubAndShroud(filename)
            self.MainClass.hub_shroud_file = filename
            if self.MainClass.hub_shroud_file != 'None':
                self.moinsbutton.enable(True)
                self.plusbutton.enable(True)
                self.MainClass.first.save_config_file()
                if len(self.MainClass.span_heights):
                    self.select_blade_names.enable(True)
                    if len(self.MainClass.blades): self.select_profile_vars.enable(True)
    
        def addspanentry(self):
            self.newentry.pack(side = "left" , fill = "y" , padx = pad)
            self.spanposts.append(self.newentry)
            self.newentry = self.span1.entry(label=" " , value = 0.0 , width = 4,command=Command(self.save_spans)).unpack()

        def delspanentry(self):
            if len(self.spanposts)>1:
                self.spanposts[-1].unpack()
                self.spanposts.pop()
                if self.spanposts[0].getFloatValue()!=0.0: self.save_spans()

        def save_spans(self):
            
            new_span_heights = []
            value = ['-']*len(self.spanposts)
            for i in range(len(self.spanposts)): 
                try : 
                    value[i] = self.spanposts[i].getFloatValue()
                    if value[i] < 0.0 or value[i] > 100.0 : rawErrorBox('Please enter a float between 0. and 100.')
                    else : new_span_heights.append(value[i])
                except ValueError : rawErrorBox('Please enter a float between 0. and 100.')

            if self.MainClass.span_heights != new_span_heights:
                self.MainClass.sample_profile_redo = True
                self.MainClass.span_heights = new_span_heights
                    
            print 'selected span heights (%): ',self.MainClass.span_heights
            self.select_blade_names.enable(False)
            
            if len(self.MainClass.span_heights) and (self.MainClass.project_type == 'structured' or self.MainClass.hub_shroud_file != 'None'):
                self.select_blade_names.enable(True)
                if len(self.MainClass.blades) : 
                    self.select_profile_vars.enable(True)
                    if len(self.MainClass.sampled_quantities):
                        self.launch_button.enable(True)
                        self.MainClass.third_step_done = True
            else :
                self.select_blade_names.enable(False)
                self.select_profile_vars.enable(False)
                self.launch_button.enable(False)
            self.MainClass.first.save_config_file()

    class fourth_window(DialogueBox):
        def __init__(self,parent,MainClass):
            self.parent = parent
            self.MainClass = MainClass

            self.stationvariablesCombo  = None
            self.bladevariablesCombo  = None
            self.stationimagepath = 'None'
            self.stationimagename = 'None'
            self.bladeimagename = 'None'
            self.bladeimagepath = 'None'
            self.allprocesses = []

            self.fourth_window_doc_general1 = 'The \\"TurboWizard\\" fourth step is used to display the output picture by selecting the\noptions in the dropdown menus. If one post-processing is skipped, only the dropdown\nmenu of the performed one will be displayed:\n\n+ station averages outputs;\n+ blade profiles outputs.\n\n'

            self.fourth_window_doc_station1 = dashline +'The \\"Station averages outputs\\" section allows to select the station average picture to\ndisplay:\n\n+ The first dropdown menu includes all the stations used for averaging in step 2. The\noption \\"all\\" in the menu enables to visualize all available stations in the same graph;\n+ The second dropdown menu includes all the available averaged quantities selected\nin step 2.\n\n'

            self.fourth_window_doc_blade1 = dashline +'The \\"Blade profiles outputs\\" section allows to select the blade profile picture to display:\n\n+ The first dropdown menu includes all the span heights selected in step 3 where the\nblade profiles has been computed. The option \\"all\\" in the menu enables to visualize all\navailable span heights in the same graph;\n+ The second dropdown menu includes all the blades (or group of solid patches)\nselected in step 3 on which the profiles has been computed;\n+ The third dropdown menu includes all the available quantities selected in step 3\nsampled on the blades.\n\n'
            
            self.fourth_window_doc_general2 = dashline +'The \\"Show\\" button in each section allows to display the picture of the selection.\nSeveral pictures can be shown independently in separate windows.\n\n'
                        
            self.fourth_window_doc_station2 = 'For station averages, to each station corresponds maximum 2 colors related to the\ndifferent weighting factors \\"area average\\" and/or \\"mass-average\\". The vertical\ndiscontinuous line, labelled as \\"average\\" in the legend, represents the surfacic\naverage scalar value on the station. The continuous line, labelled as \\"profile\\" in the\nlegend, represents the profile from span=0% (extremum at min R/Z) to span=100%\n(extremum at max R/Z) of the curvilinear azimuthal averages on the station.\n\n\n'
            
            self.fourth_window_doc_blade2 = 'For blade profiles, a specific color corresponds to each combination of blade and span\nheight. Each continuous line represents the profile from leading edge (chord=0%) to\ntrailing edge (chord=100%) of the selected quantity sampled at the specific span height\nalong both pressure and suction sides. Blade names and span heights are labelled in\nthe legend.\n\n'

            self.fourth_window_doc_general3 = dashline +'The \\"Back\\" button allows to go back to step 3.\nThe \\"Close\\" button allows to close the \\"TurboWizard\\".\n'
 
        def showAt(self,x=0,y=0):
            eval_tcl_string( "wm deiconify " + self._tclName() )
            eval_tcl_string("set absx "+str(x)+" ; \
            set absy "+str(y)+" ; \
            wm geometry  " + self._tclName() + " \"+$absx+$absy\"")

        def cropify(self,control,maxl,name,bal):
                firstl = (maxl - 4) / 2
                lastl  = (maxl - 4) / 2
                if len(name)<maxl+1:cropped = name
                else : 
                    cropped = name[:firstl]+'\[...\]'+name[-lastl:]
                    if bal : self.addBalloonToControl(control,name)
                return cropped

        def open_popup(self):
            if isinstance(self.parent, DialogueBox): self.parent.close()
            else : self.MainClass = self.parent
            DialogueBox.__init__(self,"TurboWizard - step 4",enableBalloons = True)
            self.showAt(self.MainClass.pos_x,self.MainClass.pos_y)

            self.StationsAvailable = ['--- Choose Station ---'] + self.MainClass.stations_dS
            for i in self.MainClass.stations_dl:
                if i not in self.StationsAvailable : self.StationsAvailable.append(i)
            if len(self.StationsAvailable) > 2 : self.StationsAvailable.append('all')
            elif len(self.StationsAvailable) == 2 : self.StationsAvailable = [self.StationsAvailable[-1]]
                
            self.StationVariablesAvailable = ['--- Choose Quantity ---'] + self.MainClass.quantities_byarea
            for i in self.MainClass.quantities_bymass:
                if i not in self.StationVariablesAvailable : self.StationVariablesAvailable.append(i)
            if len(self.StationVariablesAvailable) == 2 : self.StationVariablesAvailable = [self.StationVariablesAvailable[-1]]

            self.BladeVariablesAvailable = ['--- Choose Quantity ---'] + self.MainClass.sampled_quantities
            if len(self.BladeVariablesAvailable) == 2 : self.BladeVariablesAvailable = [self.BladeVariablesAvailable[-1]]
            self.BladesAvailable = ['--- Choose Blade ---'] + self.MainClass.blades
            if len(self.BladesAvailable) > 2 : self.BladesAvailable.append('all')
            elif len(self.BladesAvailable) == 2 : self.BladesAvailable = [self.BladesAvailable[-1]]
            self.BladeSpansAvailable = ['--- Choose Height ---'] + self.MainClass.span_heights
            if len(self.BladeSpansAvailable) > 2 : self.BladeSpansAvailable.append('all')
            elif len(self.BladeSpansAvailable) == 2 : self.BladeSpansAvailable = [self.BladeSpansAvailable[-1]]

            self.fourthFrame = self.frame()
            self.fourthFrame.pack(side="top",fill="both")
            self.fourthFrame.image(picture4).pack(side="bottom",fill="x",anchor='center',padx = padx_image,pady =pady_image )
            self.docFrame = self.fourthFrame.frame().pack(side="top",fill="both")
            infodoc = self.docFrame.image(info).pack(side="right",padx = pad,pady =pad)

            if self.MainClass.second_step_skipped:
                self.fourth_window_doc_station1 = ''
                self.fourth_window_doc_station2 = ''
            if self.MainClass.third_step_skipped:
                self.fourth_window_doc_blade1 = ''
                self.fourth_window_doc_blade2 = ''
            self.fourth_window_doc = self.fourth_window_doc_general1 + self.fourth_window_doc_station1 + self.fourth_window_doc_blade1 + self.fourth_window_doc_general2 + self.fourth_window_doc_station2 + self.fourth_window_doc_blade2 + self.fourth_window_doc_general3
            
            self.addBalloonToControl(infodoc,self.fourth_window_doc)

            self.showframe    = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            self.MainClass.launch_post() 

            if not self.MainClass.second_step_skipped:
                self.stationoutputFrame = self.showframe.labelframe(label="Station averages outputs").pack(side="top",fill="x",padx=pad,pady=pad)    
                self.stationoutputFrame1 = self.stationoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.stationCombo  = self.stationoutputFrame1.combobox( items=self.StationsAvailable,command=Command(self.checkoutputs)).pack(side="left",fill="y",padx=pad)
                self.stationshowbutton  = self.stationoutputFrame1.button(text="Show",command = Command(self.stationshowgraphs)).pack(side='right',fill="y",padx=pad)
                self.stationshowbutton.enable(False)
                self.stationoutputFrame2 = self.stationoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.stationvariablesCombo  = self.stationoutputFrame2.combobox( items=self.StationVariablesAvailable,command=Command(self.checkoutputs)).pack(side="left",expand="no")
                self.stationoutputFrame3 = self.stationoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.stationpathlabel = self.stationoutputFrame3.label('Image Filename: '+self.stationimagename).pack(side='left',expand="no")
                self.checkstationoutput()

            if not self.MainClass.third_step_skipped:
                self.bladeoutputFrame = self.showframe.labelframe(label="Blade profiles outputs").pack(side="top",fill="x",padx=pad,pady=pad)    
                self.bladeoutputFrame1 = self.bladeoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.bladespansCombo = self.bladeoutputFrame1.combobox( items=self.BladeSpansAvailable,command=Command(self.checkoutputs)).pack(side="left",fill="y",padx=pad)
                self.bladeshowbutton = self.bladeoutputFrame1.button(text="Show",command = Command(self.bladeshowgraphs)).pack(side='right',fill="y",padx=pad)
                self.bladeshowbutton.enable(False)
                self.bladeoutputFrame2 = self.bladeoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.bladeCombo = self.bladeoutputFrame2.combobox( items=self.BladesAvailable,command=Command(self.checkoutputs)).pack(side="left",expand="no")
                self.bladeoutputFrame3 = self.bladeoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.bladevariablesCombo = self.bladeoutputFrame3.combobox( items=self.BladeVariablesAvailable,command=Command(self.checkoutputs)).pack(side="left",expand="no")
                self.bladeoutputFrame4 = self.bladeoutputFrame.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                self.bladepathlabel = self.bladeoutputFrame4.label('Image Filename: '+self.bladeimagename).pack(side='left',expand="no")
                self.checkbladeoutput()

            self.third = third_window(self,self.MainClass)
            commonframe1  = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
            cancel_button = commonframe1.button(text="Close",command = Command(self.close_and_kill)).pack(side="right",anchor="w",padx=pad,pady=pad)
            self.backstep = commonframe1.button(text="<< Back",command = Command(self.third.open_popup)).pack(side='right',anchor ='w',padx=pad,pady=pad)

        def checkstationoutput(self):
            if 'Choose' in self.stationCombo.getValue() or 'Choose' in self.stationvariablesCombo.getValue(): self.stationshowbutton.enable(False)
            else : 
                self.stationshowbutton.enable(True)
                self.stationimagename = 'average_'+variable_shortnames[self.stationvariablesCombo.getValue()][0]+'_'+self.stationCombo.getValue().replace(' ','_')+'.png'
                self.stationimagename_cropped = self.cropify(self.stationpathlabel,44,self.stationimagename,0)
                self.stationimagepath = self.MainClass.TWpicturepath+self.stationimagename
                self.stationpathlabel.updateLabel('Image Filename: '+self.stationimagename_cropped)
                self.addBalloonToControl(self.stationpathlabel,self.stationimagepath)
            
        def checkbladeoutput(self):
            if 'Choose' in self.bladeCombo.getValue() or 'Choose' in self.bladevariablesCombo.getValue() or 'Choose' in self.bladespansCombo.getValue(): self.bladeshowbutton.enable(False)
            else : 
                self.bladeshowbutton.enable(True)
                self.bladeimagename = 'profile_'+variable_shortnames[self.bladevariablesCombo.getValue()][0]+'_'+self.bladeCombo.getValue().replace(' ','_')+'_'+self.bladespansCombo.getValue()+'pc'+self.MainClass.ext.replace('dat','png')
                self.bladeimagename_cropped = self.cropify(self.bladepathlabel,44,self.bladeimagename,0)
                self.bladeimagepath = self.MainClass.TWpicturepath+self.bladeimagename
                self.bladepathlabel.updateLabel('Image Filename: '+self.bladeimagename_cropped)
                self.addBalloonToControl(self.bladepathlabel,self.bladeimagepath)

        def checkoutputs(self,info=""):
            if self.stationvariablesCombo != None: self.checkstationoutput()
            if self.bladevariablesCombo != None: self.checkbladeoutput()

        def stationshowgraphs(self):
            # within a Tk frame : is not working because png->gif conversion needs Image module that is not supported in Python libraries of CFView
            #title='Average of '+self.stationvariablesCombo.getValue()+' in '+self.stationCombo.getValue()
            #graphwindow=DialogueBox(title)
            ##graphwindow.showAt(self.MainClass.pos_x3,self.MainClass.pos_y3)
            #graphwindow.graphFrame = graphwindow.frame()
            #graphwindow.graphFrame.pack(side="top",fill="both")
            #graphwindow.graphFrame.image(self.stationimagepath).pack(side="top",fill="x",anchor='center',padx = padx_image,pady =pady_image )

            image = self.stationimagepath[:-3]+'png'
            if not os.path.isfile(image): rawErrorBox(image +" file could not be found")
                                            
            if platform.system() == 'Windows' and os.path.isfile(image) : 
#                p = Popen(["rundll32.exe","shimgvw.dll,ImageView_Fullscreen",image.replace('/','\\')], stdout = PIPE, stderr = PIPE)
                p = Popen(["explorer.exe",image.replace('/','\\')], stdout = PIPE, stderr = PIPE)
                self.allprocesses.append(p)
            elif platform.system() == 'Linux' : 
                p = Popen(["eog",image], stdout = PIPE, stderr = PIPE)
                self.allprocesses.append(p)
            
            
        def bladeshowgraphs(self):
            # within a Tk frame : is not working because png->gif conversion needs Image module that is not supported in Python libraries of CFView
            #title='Profile of '+self.bladevariablesCombo.getValue()+' along '+self.bladeCombo.getValue()+' at '+self.bladespansCombo.getValue()+'\%  span height'
            #graphwindow=DialogueBox(title)
            ##graphwindow.showAt(self.MainClass.pos_x3,self.MainClass.pos_y3)
            #graphwindow.graphFrame = graphwindow.frame()
            #graphwindow.graphFrame.pack(side="top",fill="both")
            #graphwindow.graphFrame.image(self.bladeimagepath).pack(side="top",fill="x",anchor='center',padx = padx_image,pady =pady_image )

            image = self.bladeimagepath[:-3]+'png'
            if not os.path.isfile(image): rawErrorBox(image +" file could not be found")

            if platform.system() == 'Windows' and os.path.isfile(image) : 
#                p = Popen(["rundll32.exe","shimgvw.dll,ImageView_Fullscreen",image.replace('/','\\')], stdout = PIPE, stderr = PIPE)
                p = Popen(["explorer.exe",image.replace('/','\\')], stdout = PIPE, stderr = PIPE)
                self.allprocesses.append(p)
            elif platform.system() == 'Linux' : 
                p = Popen(["eog",image], stdout = PIPE, stderr = PIPE)
                self.allprocesses.append(p)

        def close_and_kill(self):
            for i in self.allprocesses:
                if i.poll() == None: i.terminate()
            self.close()

    class list_checkbuttons(DialogueBox):
        def __init__(self,MainClass2,type2,title2,com2,doc2,maxl2,button_names2,box_names2,box_ini2,openboxnames2,parent2):
            self.typeb = type2
            self.valid = parent2
            self.MainClass = MainClass2
            self.title = title2
            self.com = com2
            self.doc = doc2
            self.maxl = maxl2
            self.openboxnames = openboxnames2
            self.button_names = button_names2 
            self.nb_buttons = len(self.button_names) # number of rows - 1
            self.entropydoc = ''
            self.opened = 0
            self.nb_box = len(box_names2) # number of columns
            self.box_list   = ['-'] * self.nb_box
            self.box_list_before = ['-'] * self.nb_box
            self.box_button = ['-'] * self.nb_box
            self.box_ini    = ['-'] * self.nb_box
            self.box_names  = ['-'] * self.nb_box
            for j in range(self.nb_box): 
                self.box_names[j]  = box_names2[j]
                self.box_ini[j]    = box_ini2[j]
                self.box_list[j]   = ['-'] * (self.nb_buttons+1)
                self.box_list_before[j] = ['-'] * (self.nb_buttons+1)
                self.box_button[j] = [0]   * (self.nb_buttons+1)

        def showAt(self,x=0,y=0):
            eval_tcl_string( "wm deiconify " + self._tclName() )
            eval_tcl_string("set absx "+str(x)+" ; \
            set absy "+str(y)+" ; \
            wm geometry  " + self._tclName() + " \"+$absx+$absy\"")

        def cropify(self,control,maxl,name,bal):
                firstl = (maxl - 4) / 2
                lastl  = (maxl - 4) / 2
                if len(name)<maxl+1:cropped = name
                else : 
                    cropped = name[:firstl]+'\[...\]'+name[-lastl:]
                    if bal : self.addBalloonToControl(control,name)
                return cropped

        def open_popup(self):
            self.entropydoc = 'The reference state used for entropy derivation is: '+str(self.MainClass.reference_pressure)+' Pa and '+str(self.MainClass.reference_temperature)+' K.'

            try: self.winfo_exists()
            except AttributeError: self.opened = 0
            if self.title in self.openboxnames and not self.opened: self.openboxnames.remove(self.title)
            
            if self.title not in self.openboxnames :
                DialogueBox.__init__(self,self.title,enableBalloons = True)
                self.openboxnames.append(self.title)
                self.showAt(self.MainClass.pos_x2,self.MainClass.pos_y2)
                self.winfo_exists()
                
                self.SelectorFrame = self.frame().pack(side="top",fill="both",expand="yes")
                
                if self.typeb != 'stations':
                    self.docFrame = self.SelectorFrame.frame().pack(side="top",fill="both")
                    infodoc = self.docFrame.image(info).pack(side="right",padx = pad,pady =pad)
                    self.addBalloonToControl(infodoc,self.doc[0])

                self.Mylabelframe  = self.SelectorFrame.labelframe(label=self.com).pack(side="top",fill="both",expand="yes",padx=pad,pady=pad)    
                
                newframe = self.Mylabelframe.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                for j in range(self.nb_box-1,-1,-1):
                    if self.typeb == 'stations': im=newframe.image(pic_dS_dl[j]).pack(side="right",anchor="w")
                    
                    self.box_ini[j][0] = int(all(item==1 for item in self.box_ini[j][1:]))
                    self.box_button[j][0] = newframe.checkbutton(self.box_names[j], initValue = self.box_ini[j][0], command=Command(self.update_list_all)).pack(side="right",anchor="w")
                    if j == 0: name = newframe.label(text='(un)select all  ').pack(side='left',anchor ='w')
                    if self.typeb == 'stations' : self.addBalloonToControl(im,self.doc[j+1])
                    elif self.typeb == 'avevars': self.addBalloonToControl(self.box_button[j][0],self.doc[j+1])

                newframe = self.Mylabelframe.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                if self.nb_box>1:newframe.image(pic_horizontal_line390).pack(side="right",fill="x")
                else :newframe.image(pic_horizontal_line300).pack(side="right",fill="x")

                buttons = self.Mylabelframe.scrolled_frame(height=150).pack(side="top",fill="both",expand = "yes")
                for i in range(1,self.nb_buttons+1):
                    newframe = buttons.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                    for j in range(self.nb_box-1,-1,-1):
                        if self.typeb == 'stations':newframe.image(pic_dS_dl[j]).pack(side="right",anchor="w")
                        self.box_button[j][i] = newframe.checkbutton(self.box_names[j], initValue = self.box_ini[j][i], command=Command(self.update_list)).pack(side="right",anchor="w")
                        if j == 0: 
                            name = newframe.label(text='')
                            cropped = self.cropify(name,self.maxl,self.button_names[i-1],1)
                            name.updateLabel(cropped)
                            name.pack(side='left',anchor ='w')
                            if 'Entropy' in self.button_names[i-1] and self.MainClass.entropy_derived:self.addBalloonToControl(name,self.entropydoc)

                ok_cancel = self.frame().pack(side="top",fill="x",padx=pad,pady=pad)
                cancel_button = ok_cancel.button(text="Cancel",command = Command(self.closebox)).pack(side="right",anchor="w",padx=pad,pady=pad)
                ok_button = ok_cancel.button(text="OK"    ,command = Command(self.savedata)).pack(side='right',anchor ='w',padx=pad,pady=pad)

        def closebox(self):
            self.openboxnames.remove(self.title)
            self.close()
            for j in range(self.nb_box):
                for i in range(self.nb_buttons+1):
                    self.box_list[j][i] =  self.box_list_before[j][i]

        def winfo_exists(self):
            self.opened = int(eval_tcl_string( "winfo exists " + self._tclName() ))

        def savedata(self):
            data = ['-']*self.nb_box
            self.openboxnames.remove(self.title)
            for j in range(self.nb_box):
                data[j] = []
                for i in range(1,self.nb_buttons+1):
                    if self.box_list[j][i] == 1 or (self.box_list[j][i] == '-' and self.box_ini[j][i] == 1): data[j].append(self.button_names[i-1])
                    if self.box_list[j][i] != '-' : self.box_ini[j][i] = self.box_list[j][i]
            
            if self.typeb == 'stations' : 
                if self.MainClass.stations_dS != data[0]:
                    self.MainClass.cut_dS_redo = True
                    self.MainClass.stations_dS = data[0]
                print 'stations selected for surfacic average',self.MainClass.stations_dS
                if self.MainClass.stations_dl != data[1]:
                    self.MainClass.stations_dl = data[1]
                    self.MainClass.cut_dl_redo = True
                print 'stations selected for azimuthal average',self.MainClass.stations_dl

                if len(self.MainClass.stations_dS) or len(self.MainClass.stations_dl) : 
                    self.valid.select_station_vars.enable(True)
                    if len(self.MainClass.quantities_byarea) or len(self.MainClass.quantities_bymass):
                        self.MainClass.second_step_done = True
                        self.valid.nextstep.enable(True)
                else : 
                    self.valid.select_station_vars.enable(False)
                    self.valid.nextstep.enable(False)

            elif self.typeb == 'avevars' : 
                if self.MainClass.quantities_byarea != data[0]:
                    self.MainClass.quantities_byarea = data[0]
                    self.MainClass.cut_dS_redo = True
                    self.MainClass.cut_dl_redo = True
                print 'averaged quantities by area',self.MainClass.quantities_byarea
                if self.MainClass.quantities_bymass != data[1]:
                    self.MainClass.quantities_bymass = data[1]
                    self.MainClass.cut_dS_redo = True
                    self.MainClass.cut_dl_redo = True
                print 'averaged quantities by massflow',self.MainClass.quantities_bymass
                self.MainClass.second_step_done = False
                self.valid.nextstep.enable(False)
                if len(self.MainClass.quantities_byarea) or len(self.MainClass.quantities_bymass):
                    self.MainClass.second_step_done = True
                    self.valid.nextstep.enable(True)

            elif self.typeb == 'blades' : 
                if self.MainClass.blades != data[0]:
                    self.MainClass.blades = data[0]
                    self.MainClass.bladepatches = []
                    self.MainClass.sample_profile_redo = True
                    for i in range(len(data[0])):
                        ind = self.valid.bladenames.index(data[0][i])
                        self.MainClass.bladepatches.append(self.valid.bladepatches[ind])
                    
                print 'blades selected for local profiles',self.MainClass.blades
                if len(self.MainClass.blades) : 
                    self.valid.select_profile_vars.enable(True)
                    if len(self.MainClass.sampled_quantities): 
                        self.MainClass.third_step_done = True
                        self.valid.launch_button.enable(True)
                else : 
                    self.valid.select_profile_vars.enable(False)
                    self.valid.launch_button.enable(False)
            else : 
                if self.MainClass.sampled_quantities != data[0]:
                    self.MainClass.sampled_quantities = data[0]
                    self.MainClass.sample_profile_redo = True
                print 'Quantities sampled on local profiles',self.MainClass.sampled_quantities
                if len(self.MainClass.sampled_quantities):
                    self.MainClass.third_step_done = True
                    self.valid.launch_button.enable(True)
                else : self.valid.launch_button.enable(False)
            self.MainClass.first.save_config_file()
            self.close()

        def update_list(self):
            for j in range(self.nb_box):
                self.box_list_before[j][0] =  self.box_ini[j][0]
                for i in range(1,self.nb_buttons+1):
                    self.box_list_before[j][i] =  self.box_ini[j][i]
                    self.box_list[j][i] = self.box_button[j][i].getState()
                    if self.box_list[j][i] == 0 : self.box_button[j][0].variable.setValue('0')
                if 0 not in self.box_list[j][1:]:
                        self.box_button[j][0].variable.setValue('1')
                        self.box_list[j][0] = self.box_button[j][0].getState()
        def update_list_all(self):
            values = ['-']*self.nb_box
            for j in range(self.nb_box):
                values[j] = ['-']*(self.nb_buttons+1)
                for i in range(self.nb_buttons+1):
                    self.box_list_before[j][i] =  self.box_ini[j][i]
                    values[j][i] = self.box_button[j][i].getState()
            for j in range(self.nb_box):
                if values[j][0] == 1 :
                    for i in range(self.nb_buttons+1): 
                        self.box_button[j][i].variable.setValue('1')
                        self.box_list[j][i] = 1
                if values[j][0] == 0 and 0 not in values[j][1:] : 
                    for i in range(self.nb_buttons+1): 
                        self.box_button[j][i].variable.setValue('0')
                        self.box_list[j][i] = 0

    MainClass = mainclass()
    MainClass.start()
