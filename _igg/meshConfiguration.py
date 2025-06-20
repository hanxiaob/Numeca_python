#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         V.S.                                                          September  2007      #
#--------------------------------------------------------------------------------------------#

import types
from IGG_MeshConfiguration import *
#--------------------------------------------------------------------------------------------#

def meshConfiguration_mainProject():				
	return MeshConfigurationDomain(meshConfiguration_mainProject_())
def meshConfiguration_subProjectNumber():				
	return meshConfiguration_subProjectNumber_()
def meshConfiguration_subProject(index):				
	return MeshConfigurationDomain(meshConfiguration_subProject_(index-1))

# kept for backward
def meshConfiguration_merge():				
	mergeDomainSelection_py()

def meshConfiguration_mergeList(domainList):
    domainString = ""
    nProjects = 0
    for domain in domainList:
        if isinstance(domain, MeshConfigurationDomain):
            domainString = domainString + str(domain.impl) + " "
            nProjects = nProjects+1
    if nProjects > 1:
        mergeDomainSelection(nProjects, domainString)

def meshConfiguration_bc_number(domain,type):				
	return get_mesh_interface_list_lenght(domain.impl,type)
def meshConfiguration_inlet_bc_number(domain):				
	return get_mesh_interface_list_lenght(domain.impl,"Inlet")
def meshConfiguration_outlet_bc_number(domain):				
	return get_mesh_interface_list_lenght(domain.impl,"Outlet")
def meshConfiguration_solid_bc_number(domain):				
	return get_mesh_interface_list_lenght(domain.impl,"Solid")
def meshConfiguration_External_bc_number(domain):				
	return get_mesh_interface_list_lenght(domain.impl,"External")
def meshConfiguration_Rotor_Stator_bc_number(domain):				
	return get_mesh_interface_list_lenght(domain.impl,"Rotor-Stator")
def meshConfiguration_inlet_bc(domain):				
	return get_mesh_interface_list(domain.impl,"Inlet")
def meshConfiguration_outlet_bc(domain):				
	return get_mesh_interface_list(domain.impl,"Outlet")
def meshConfiguration_solid_bc(domain):				
	return get_mesh_interface_list(domain.impl,"Solid")
def meshConfiguration_External_bc(domain):				
	return get_mesh_interface_list(domain.impl,"External")
def meshConfiguration_Rotor_Stator_bc(domain):				
	return get_mesh_interface_list(domain.impl,"Rotor-Stator")
def meshConfiguration_connect_as_rotor_stator(interface1,interface2):				
	a = `interface1.impl`+" "+`interface2.impl`
	connectInterfaceSelection(2,a,"rs")
def meshConfiguration_merge_bcs(interface1,interface2):				
	a = `interface1.impl`+" "+`interface2.impl`
	mergeInterfaceSelection(2,a)
def meshConfiguration_ungroup_bcs(interface):				
	ungroupInterfaceSelection(1,interface.impl)
class MeshConfigurationDomain:
        def __init__(self,pointer):
                self.impl = pointer
        def numberOfSubDomain(self):
                return meshConfiguration_subDomainNumber(self.impl)
        def subDomain(self,index):
                return MeshConfigurationDomain(meshConfiguration_subDomain(self.impl,index-1))
        def subDomainByName(self,name):
                return MeshConfigurationDomain(meshConfiguration_subDomainByName(self.impl,name))
        def numberOfInterfaces(self):
                return meshConfiguration_subDomainInterfacesNumber(self.impl)
        def interface(self,index):
                return MeshConfigurationDomainBcs(meshConfiguration_subDomainInterface(self.impl,index-1))
        def interfaceByName(self,name):
                return MeshConfigurationDomainBcs(meshConfiguration_subDomainInterfaceByName(self.impl,name))
        def highlight(self):
                meshConfiguration_highLight(self.impl)
        def unhighlight(self):
                meshConfiguration_unhighLight(self.impl)
        def duplicate(self):
                meshConfiguration_subDomain_duplidate(self.impl)
        def delete(self):
                meshConfiguration_subDomain_delete(self.impl)
        def close(self):
                meshConfiguration_close(self.impl)
        def select(self):
                meshConfiguration_select(self.impl)
        def unselect(self):
                meshConfiguration_unselect(self.impl)
        def save(self):
                exportDomainSelection(self.impl)
        def load(self):
		meshConfiguration_subDomain_load(self.impl)
        def rename(self,value):
		MeshConfiguration_rename(self.impl,value)
class MeshConfigurationDomainBcs:
        def __init__(self,pointer):
                self.impl = pointer
        def highlight(self):
                meshConfiguration_highLight(self.impl)
        def unhighlight(self):
                meshConfiguration_unhighLight(self.impl)
        def close(self):
                meshConfiguration_close(self.impl)
        def select(self):
                meshConfiguration_select(self.impl)
        def unselect(self):
                meshConfiguration_unselect(self.impl)
        def export(self):
                return exportBcsSelection(self.impl)
        def ungroup(self):
                ungroupInterfaceSelection(1,`self.impl`)
        def rename(self,value):
		MeshConfiguration_rename(self.impl,value)
            
