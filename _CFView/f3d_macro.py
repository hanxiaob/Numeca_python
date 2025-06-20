#------------------------------------------------------------------------------#
#                          efficiency 3D                                       #
#------------------------------------------------------------------------------#
#    NUMECA International                                                      #
#       E. Robin                                                    nov 1999   #
#       update S. Pierret                                           jan 2001   #
#------------------------------------------------------------------------------#
# Description : group the various operations to be done for the computation    #
#               of an efficiency on a 3D                                       #
#------------------------------------------------------------------------------#
# Changes                                                                      #
#    03/05/2011     Y.Deletrain     Initial support for Hexstream              #
#------------------------------------------------------------------------------#

# To check (May 2011)
# - search_Torque : removed search for 'exit' - required?
# -

from CFView import *
from math import *
from Point import *
import string
import os
import re

#from string import * 

#------------------------------------------------------------------------------#
#                         UTILITY FUNCTIONS
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
def f3d_search_quantity_in_file ( fileName , searchString , fieldNumber ):
    '''
        Search a quantity by regular expression in a file
        Once found, the value read at the given field position is returned
        If not found or not read correctly, 'None' is returned
    '''
    if searchString == "":
        return None
    try:
        fp = open(fileName,'r',-1)
    except:
        print "[error] failed to open file '" + fileName + "'"
        return None

    found = 0
    pos   = 1
    value = 0.0
    myregexpr = re.compile(searchString)

    for line in fp:
        if myregexpr.search(line):
            print "matched line #" + str(pos) + " '" + line + "'"
            value = get_float(line,fieldNumber)
            found = 1
            break
        pos += 1
    fp.close()

    if found:
        print "[info] found value for field '" + searchString + "': " + str(value)
    else:
        print "[info] value not found for field '" + searchString + "' in file '" + fileName + "'"
        return None

    return value

#------------------------------------------------------------------------------#
#contains fix for #26756
def f3d_search_quantities_in_file ( fileName , searchString , fieldNumber=0 ):
    '''
        Search all occurences of a quantity by regular expression in a file
        Once found, the value read at the given field position is returned
        If not found or not read correctly, 'None' is returned
    '''

    if searchString == "":
        return None
    try:
        fp = open(fileName,'r',-1)
    except:
        print "[error] failed to open file '" + fileName + "'"
        return None

    pos    = 1
    values = []
    myregexpr = re.compile(searchString)

    for line in fp:
        if myregexpr.search(line):
            print "matched line #" + str(pos) + " '" + line + "'"
            if fieldNumber > 0 :
                values.append (get_float(line,fieldNumber))
            else:
                words = string.splitfields(line)
                for word in words:
                    try:
                        myval = float(word)
                        values.append (myval)
                    except:
                        # word cannot be converted to float
                        print '\tignoring \'\'' + word + '\''
        pos += 1
    fp.close()

    if len(values):
        print "[info] found " + str(len(values)) + " value(s) for field '" + searchString + "': " + str(values)
    else:
        print "[info] value not found for field '" + searchString + "' in file '" + fileName + "'"
        return None

    return values

#------------------------------------------------------------------------------#
def f3d_list_subtract ( list1 , list2 ):
    '''
        Create a new list by removing items present in list2 from list1
        In addition, each occurence is unique in the new list
    '''

    newlist = []

    # Convert tuples to lists
    if isinstance(list1,tuple):
        list1 = list(list1)
    if isinstance(list2,tuple):
        list2 = list(list2)

    # Check type
    if not isinstance(list1,list):
        print '[error] argument #1 is not a list!'
        return newlist
    if not isinstance(list2,list):
        print '[error] argument #2 is not a list!'
        return newlist

    for item in list1:
        if list2.count(item) == 0:
            if newlist.count(item) == 0:
                newlist.append(item)

    return newlist

#------------------------------------------------------------------------------#
def f3d_list_union ( list1 , list2 ):
    '''
        Create a new list by merging items from both lists
        Each occurence is unique in the new list
    '''

    newlist = []

    # Convert tuples to lists
    if isinstance(list1,tuple):
        list1 = list(list1)
    if isinstance(list2,tuple):
        list2 = list(list2)

    # Check type
    if not isinstance(list1,list):
        print '[error] argument #1 is not a list!'
        return newlist
    if not isinstance(list2,list):
        print '[error] argument #2 is not a list!'
        return newlist

    for item in list1:
        if newlist.count(item) == 0:
            newlist.append(item)
    for item in list2:
        if newlist.count(item) == 0:
            newlist.append(item)

    return newlist

#------------------------------------------------------------------------------#
def Get_Inlet():
    SelectFromViewRegExp('inlet')
    RemoveFromViewRegExp('Trail')
    RemoveFromViewRegExp('Gap')

#------------------------------------------------------------------------------#
def Get_Outlet():
    SelectFromViewRegExp('outlet')
    RemoveFromViewRegExp('Lead')
    RemoveFromViewRegExp('Gap')

#------------------------------------------------------------------------------#
#                     COMPUTATION ON ONLY ONE SURFACE
#------------------------------------------------------------------------------#

def computeSurfaceMassFlow():

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('Density')

#--------------------------------------------------------------------------------------#

def computeTorqueOld():
    UnselectFromViewRegExp  ('*')
    SelectFromProjectRegExp ('*Solid*')
    if 0==QntFieldExist('Static Pressure'):
        errorBox('Quantity \'Static Pressure\' does not exist')
        return

    QntFieldScalar('Static Pressure')

    d = axis[0]
    p = axis[1]
    return SclBoundaryTorqueAmplitude(p[0],p[1],p[2],d[0],d[1],d[2])

#--------------------------------------------------------------------------------------#

def computeTorque():

    UnselectFromViewRegExp  ('*')
    SelectFromProjectRegExp ('*Solid*')

    SetTorqueAxis(0.0,  0.04,   0.0,
                  0.0,  0.0,    1.0,
                  0,    1,      0,
                  0,    0.04,   0,
                  0,    0,  1,
                  0,    0)
    MechanicsQntSurfaceDerived('Force')
    QntFieldVector('Force')
    MechanicsQntSurfaceDerived('Vector Torque')
    QntFieldVector('Vector Torque')

    return VectorFlux()

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoRho():
    if 0==QntFieldExist('RhoRho') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return
        QntFieldDerived(0,'RhoRho','Density*Density')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoRho')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoPt():
    if 0==QntFieldExist('RhoPt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Absolute Total Pressure'):
            if 0==QntFieldExist('Total Pressure'):
                errorBox('Quantity \'Absolute Total Pressure\' does not exist')
                return
            else:
                QntFieldDerived(0,'RhoPt','Density*Total Pressure')
        else:
            QntFieldDerived(0,'RhoPt','Density*Absolute Total Pressure')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoPt')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoTt():
    if 0==QntFieldExist('RhoTt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Absolute Total Temperature'):
            if 0==QntFieldExist('Total Temperature'):
                errorBox('Quantity \'Absolute Total Temperature\' does not exist')
                return
            else:
                QntFieldDerived(0,'RhoTt','Density*Total Temperature')
        else:
            QntFieldDerived(0,'RhoTt','Density*Absolute Total Temperature')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoTt')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoPs():
    if 0==QntFieldExist('RhoPs') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Static Pressure'):
            errorBox('Quantity \'Static Pressure\' does not exist')
            return
        QntFieldDerived(0,'RhoPs','Density*Static Pressure')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoPs')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoTs():
    if 0==QntFieldExist('RhoTs') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Static Temperature'):
            errorBox('Quantity \'Static Temperature\' does not exist')
            return
        QntFieldDerived(0,'RhoTs','Density*Static Temperature')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoTs')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoVz():
    if 0==QntFieldExist('RhoVz') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vz'):
            errorBox('Quantity \'Vz\' does not exist')
            return
        QntFieldDerived(0,'RhoVz','Density*Vz')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoVz')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoRVt():
    if 0==QntFieldExist('RhoRVt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vt'):
            errorBox('Quantity \'Vt\' does not exist')
            return
        QntFieldDerived(0,'RhoRVt','sqrt(x*x+y*y)*Density*Vt')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoRVt')



#--------------------------------------------------------------------------------------#

def computeSurfaceRhoVt():
    if 0==QntFieldExist('RhoVt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vt'):
            errorBox('Quantity \'Vt\' does not exist')
            return
        QntFieldDerived(0,'RhoVt','Density*Vt')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoVt')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoVr():
    if 0==QntFieldExist('RhoVr') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vr'):
            errorBox('Quantity \'Vr\' does not exist')
            return
        QntFieldDerived(0,'RhoVr','Density*Vr')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    return VectorWeightedFlux('RhoVr')


#--------------------------------------------------------------------------------------#
# same type of integral by on a group of surfaces                                      #
#--------------------------------------------------------------------------------------#

def computeSurfaceGroupMassFlow():

    if 0==QntFieldExist('Density'):
        errorBox('Quantity \'Density\' does not exist')
        return 
        
    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('Density')
    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoRho():
    if 0==QntFieldExist('RhoRho') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return
        QntFieldDerived(0,'RhoRho','Density*Density')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoRho')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoPt():
    if 0==QntFieldExist('RhoPt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Absolute Total Pressure'):
            if 0==QntFieldExist('Total Pressure'):
                errorBox('Quantity \'Absolute Total Pressure\' does not exist')
                return
            else:
                QntFieldDerived(0,'RhoPt','Density*Total Pressure')
        else:
            QntFieldDerived(0,'RhoPt','Density*Absolute Total Pressure')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoPt')
    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoTt():
    if 0==QntFieldExist('RhoTt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Absolute Total Temperature'):
            if 0==QntFieldExist('Total Temperature'):
                errorBox('Quantity \'Absolute Total Temperature\' does not exist')
                return
            else:
                QntFieldDerived(0,'RhoTt','Density*Total Temperature')
        else:
            QntFieldDerived(0,'RhoTt','Density*Absolute Total Temperature')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoTt')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoPs():
    if 0==QntFieldExist('RhoPs') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Static Pressure'):
            errorBox('Quantity \'Static Pressure\' does not exist')
            return
        QntFieldDerived(0,'RhoPs','Density*Static Pressure')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoPs')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoTs():
    if 0==QntFieldExist('RhoTs') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Static Temperature'):
            errorBox('Quantity \'Static Temperature\' does not exist')
            return
        QntFieldDerived(0,'RhoTs','Density*Static Temperature')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoTs')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoVz():
    if 0==QntFieldExist('RhoVz') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vz'):
            errorBox('Quantity \'Vz\' does not exist')
            return
        QntFieldDerived(0,'RhoVz','Density*Vz')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoVz')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoRVt():
    if 0==QntFieldExist('RhoRVt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vt'):
            errorBox('Quantity \'Vt\' does not exist')
            return
        QntFieldDerived(0,'RhoRVt','sqrt(x*x+y*y)*Density*Vt')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = q + VectorWeightedFlux('RhoRVt')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoVt():
    if 0==QntFieldExist('RhoVt') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vt'):
            errorBox('Quantity \'Vt\' does not exist')
            return
        QntFieldDerived(0,'RhoVt','Density*Vt')

    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoVt')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRhoVr():
    if 0==QntFieldExist('RhoVr') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('Vr'):
            errorBox('Quantity \'Vr\' does not exist')
            return
        QntFieldDerived(0,'RhoVr','Density*Vr')
    
    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = VectorWeightedFlux('RhoVr')

    return q

#--------------------------------------------------------------------------------------#

def computeSurfaceGroupRho_atanVtVm():
    if 0==QntFieldExist('Rho_atanVtVm') :
        if 0==QntFieldExist('Density'):
            errorBox('Quantity \'Density\' does not exist')
            return 
        if 0==QntFieldExist('atan(Vt/Vm)'):
            errorBox('Quantity \'atan(Vt/Vm)\' does not exist')
            return
        QntFieldDerived(0,'Rho_atanVtVm','Density*atan(Vt/Vm)')
    
    vfield = ''    
    if 0==QntFieldExist('Vxyz'):
        if 0==QntFieldExist('Velocity'):
            errorBox('Quantity \'Vxyz\' or \'Velocity\' does not exist')
            return
        else:
            vfield = 'Velocity'
    else:
        vfield = 'Vxyz'
    
    QntFieldVector(vfield)
    q = q + VectorWeightedFlux('Rho_atanVtVm')

    return q

#**************************************************************************************#
#
#
#                              COMPRESSIBLE FLOWS
#
#
#**************************************************************************************#

#--------------------------------------------------------------------------------------#
#                   
#                                      COMPRESSOR PARAMETER
#
#--------------------------------------------------------------------------------------#

def compressorIsentropicEfficiencyTot2Tot(gamma):

    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2
    
    tt1 = tt1 / m1
    tt2 = tt2 / m2
    
    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
  
    return ((pt2/pt1)**((gamma-1)/gamma)-1) / ((tt2/tt1)-1)

#--------------------------------------------------------------------------------------#

def compressorIsentropicEfficiencyTot2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    pt1 = pt1 / m1
    ps2 = ps2 / m2

    tt1 = tt1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print pt1
    print ps2

    print tt1
    print ts2
 
    return ((ps2/pt1)**((gamma-1)/gamma)-1) / ((ts2/tt1)-1)

#--------------------------------------------------------------------------------------#

def compressorIsentropicEfficiencyStatic2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    ts1 = computeSurfaceGroupRhoTs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    ts1 = ts1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print ps1
    print ps2

    print ts1
    print ts2
 
    return ((ps2/ps1)**((gamma-1)/gamma)-1) / ((ts2/ts1)-1)
#--------------------------------------------------------------------------------------#

def compressorPolytropicEfficiencyTot2Tot(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    tt1 = tt1 / m1
    tt2 = tt2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
 
    return ((gamma-1)/gamma)*log(pt2/pt1)/log(tt2/tt1)

#--------------------------------------------------------------------------------------#

def compressorPolytropicEfficiencyTot2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    pt1 = pt1 / m1
    ps2 = ps2 / m2

    tt1 = tt1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print pt1
    print ps2

    print tt1
    print ts2
 
    return ((gamma-1)/gamma)*log(ps2/pt1)/log(ts2/tt1)

#--------------------------------------------------------------------------------------#

def compressorPolytropicEfficiencyStatic2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    ts1 = computeSurfaceGroupRhoTs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    ts1 = ts1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print ps1
    print ps2

    print ts1
    print ts2
 
    return ((gamma-1)/gamma)*log(ps2/ps1)/log(ts2/ts1)


#--------------------------------------------------------------------------------------#

def compressorEfficiency_Entropy(gamma):

    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    tt1 = tt1 / m1
    tt2 = tt2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
  
    eff = 1 - log((tt2/tt1)/(pt2/pt1)**((gamma-1)/gamma)) / (1 - tt1/tt2)
    
    return eff 

#--------------------------------------------------------------------------------------#
#                   
#                                      TURBINE PARAMETER
#
#--------------------------------------------------------------------------------------#

def turbineIsentropicEfficiencyTot2Tot(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 

    pt1 = pt1 / m1
    pt2 = pt2 / m2

    tt1 = tt1 / m1
    tt2 = tt2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
    
    
    return (1-(tt2/tt1)) / (1-(pt2/pt1)**((gamma-1)/gamma))


#--------------------------------------------------------------------------------------#

def turbineIsentropicEfficiencyTot2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    pt1 = pt1 / m1
    ps2 = ps2 / m2

    tt1 = tt1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print pt1
    print ps2

    print tt1
    print ts2
    
    return (1-(ts2/tt1)) / (1-(ps2/pt1)**((gamma-1)/gamma))

#--------------------------------------------------------------------------------------#

def turbineIsentropicEfficiencyStatic2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    ts1 = computeSurfaceGroupRhoTs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    ts1 = ts1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print ps1
    print ps2

    print ts1
    print ts2
    
    return (1-(ts2/ts1)) / (1-(ps2/ps1)**((gamma-1)/gamma))
#--------------------------------------------------------------------------------------#

def turbinePolytropicEfficiencyTot2Tot(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    tt1 = tt1 / m1
    tt2 = tt2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
    
    return ((gamma)/(gamma-1))*log(tt2/tt1)/log(pt2/pt1)
#--------------------------------------------------------------------------------------#

def turbinePolytropicEfficiencyTot2Static(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    pt1 = pt1 / m1
    ps2 = ps2 / m2

    tt1 = tt1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print pt1
    print ps2

    print tt1
    print ts2
  
    return ((gamma)/(gamma-1))*log(ts2/tt1)/log(ps2/pt1)
#--------------------------------------------------------------------------------------#

def turbinePolytropicEfficiencyStatic2Static(gamma):
    
    Get_Inlet()

    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    ts1 = computeSurfaceGroupRhoTs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    ts2 = computeSurfaceGroupRhoTs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    ts1 = ts1 / m1
    ts2 = ts2 / m2

    print m1
    print m2

    print ps1
    print ps2

    print ts1
    print ts2
    
    return ((gamma)/(gamma-1))*log(ts2/ts1)/log(ps2/ps1)

#--------------------------------------------------------------------------------------#

def turbineEfficiency_Entropy(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    tt1 = computeSurfaceGroupRhoTt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    tt2 = computeSurfaceGroupRhoTt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    tt1 = tt1 / m1
    tt2 = tt2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print tt1
    print tt2
 
    eff = (1-(tt2/tt1)) / (1-(tt2/tt1)+(tt2/tt1)*log((tt2/tt1)/(pt2/pt1)**((gamma-1)/gamma) ))
    
    return eff 

#--------------------------------------------------------------------------------------#

def turbineEnthalpyLossCoefficient(gamma):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    ps1 = computeSurfaceGroupRhoPs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    ps2 = computeSurfaceGroupRhoPs() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    ps1 = ps1 / m1
    ps2 = ps2 / m2

    print m1
    print m2

    print pt1
    print pt2

    print ps1
    print ps2
    
    return (1-(ps2/pt2)**((gamma-1)/gamma)) / (1-(ps2/pt1)**((gamma-1)/gamma))


#**************************************************************************************#
#
#
#                              INCOMPRESSIBLE FLOWS
#
#
#**************************************************************************************#

#--------------------------------------------------------------------------------------#
#                                  PUMP PARAMETER
#--------------------------------------------------------------------------------------#

def pumpIncompressibleTotal( rho, omega, torque, mass_flow):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    print pt1
    print pt2
    
    return mass_flow*(pt2-pt1) / rho / omega / torque

#--------------------------------------------------------------------------------------#

def pumpIncompressibleStatic( rho, omega, torque, mass_flow):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    print ps1
    print ps2
    return  mass_flow*(ps2-ps1)/rho/omega/torque
    
#--------------------------------------------------------------------------------------#
#                                  TURBINE PARAMETER
#--------------------------------------------------------------------------------------#

def turbineIncompressibleTotal( rho, omega, torque, mass_flow):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    pt1 = computeSurfaceGroupRhoPt()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    pt2 = computeSurfaceGroupRhoPt() 
    
    pt1 = pt1 / m1
    pt2 = pt2 / m2

    print pt1
    print pt2
    
    return  rho*omega*torque/( mass_flow*(pt2-pt1))

#--------------------------------------------------------------------------------------#

def turbineIncompressibleStatic( rho, omega, torque,mass_flow):
    
    Get_Inlet()
    m1 = computeSurfaceGroupMassFlow() 
    ps1 = computeSurfaceGroupRhoPs()
    
    Get_Outlet()
    m2 = computeSurfaceGroupMassFlow() 
    ps2 = computeSurfaceGroupRhoPs() 
    
    ps1 = ps1 / m1
    ps2 = ps2 / m2

    print ps1
    print ps2
    
    return  rho*omega*torque/( mass_flow*(ps2-ps1))
#--------------------------------------------------------------------------------------#
#                          efficiency 3D                                               #
#--------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------#
#                          Search of data in .run file                                 #
#--------------------------------------------------------------------------------------#
## def search_ROTATION_UNIT(file):
##     word=' '
##     f=open(file)
##     while get_string(word,2)!='rotational_speed':
##         word=f.readline()    
##     value=get_integer(word,3)
##     f.close
##     if value==1 :
##          print "--------------------------------------"
##          print "       PROJECT IS IN RAD/S            "
##          print "--------------------------------------"
##     if value==2 :
##         print "--------------------------------------"
##         print "       PROJECT IS IN RPM              "
##         print "--------------------------------------"
    
##     return value
         

def search_UNIGAS(file,default_value):
    value=default_value
    word=' '
    f=open(file)
    while get_string(word,1)!='NI_BEGIN' or get_string(word,2)!='solver_parameters':
        word=f.readline()    
    test=0
    while test==0 :
        word=f.readline()
        if get_string(word,1)=='UNIGAS' :
            word=f.readline()
            value=get_float(word,1)
            test=1
        else:
            if get_string(word,1)=='exit':
                test=1
    
    f.close()
    print "--------------------------------------"
    print "        CONSTANT GAS  VALUE           "
    print "--------------------------------------"
    print value


    return value
    

def search_CP(file):
    word=' '
    f=open(file)
    while get_string(word,1)!='NI_BEGIN' or get_string(word,2)!='solver_parameters':
        word=f.readline()    
    while get_string(word,1)!='CP' :
        word=f.readline()    
    word=f.readline()
    value=get_float(word,1)
    f.close()

    print "--------------------------------------"
    print "             CP  VALUE                "
    print "--------------------------------------"
    print value


    return value
    
def search_RHO(file):
    word=' '
    f=open(file)
    while get_string(word,1)!='NI_BEGIN' or get_string(word,2)!='solver_parameters':
        word=f.readline()    
    while get_string(word,1)!='ROREF' : #Reference value of rho
        word=f.readline()    
    word=f.readline()
    value=get_float(word,1)
    f.close()

    print "--------------------------------------"
    print "             RHO VALUE                "
    print "--------------------------------------"
    print value


    return value
    
#-------------------------------------------------------------------------------------#
#                          Search of data in .mf file                                 #
#-------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------#
def search_GAMMA(file):
    print "--------------------------------------"
    print "            GAMMA VALUE               "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Specific_heat_ratio",          2)

    return value

#--------------------------------------------------------------------------------------#
def search_OMEGA(file):
    print "--------------------------------------"
    print "        ROTATION SPEED                "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    values = []

    # euranus - contains fix for #26756
    if len(values) == 0:
        values = f3d_search_quantities_in_file (res_file, "Rotational_speed")
    # hexstream
    if len(values) == 0:
        values = f3d_search_quantities_in_file (res_file, "Rotational speed", 4)

    # Return first non zero value (limitation)
    for d in values:
        if abs(d) > 1e-9:
            value = d
            break

    print "value = " + str(value)

    return value

#--------------------------------------------------------------------------------------#
def search_Mass_Flow(file):
    return search_Mass_Flow_Outlet(file)

#--------------------------------------------------------------------------------------#
def search_Mass_Flow_Inlet(file):
    print "--------------------------------------"
    print "        MASS FLOW VALUE (INLET)       "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Mass_flow",          2)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Mass flow at inlet", 6)

    return value

#--------------------------------------------------------------------------------------#
def search_Mass_Flow_Outlet(file):
    print "--------------------------------------"
    print "        MASS FLOW VALUE (OUTLET)      "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Mass_flow",           2)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Mass flow at outlet", 6)

    return value

#--------------------------------------------------------------------------------------#
def search_Torque(file):
    print "--------------------------------------"
    print "            TORQUE VALUE              "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Torque",            2)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Torque",            3)

    if value == None: # retrieved from old function - why?
        value = 1e-6
        print "[warning] value not found - set to " + str(value)

    return value

#--------------------------------------------------------------------------------------#
def search_STA_PRES_RATIO(file):
    print "--------------------------------------"
    print "        STA_PRES_RATIO VALUE          "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static_pressure_ratio", 2)
    # hexstream
    #if value == None:
    #    value = f3d_search_quantity_in_file (res_file, "xxxxxxx", 3)

    return value

#--------------------------------------------------------------------------------------#
def search_TOT_PRES_RATIO(file):
    print "--------------------------------------"
    print "        TOT_PRES_RATIO VALUE          "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute_total_pressure_ratio", 2)
    # hexstream
    #if value == None:
    #    value = f3d_search_quantity_in_file (res_file, "xxxxxxx", 3)

    return value

#--------------------------------------------------------------------------------------#

def search_STA_PRES_RISE(file):
    print "--------------------------------------"
    print "        STA_PRES_RISE VALUE           "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static_pressure_rise", 2)
    # hexstream
    #if value == None:
    #    value = f3d_search_quantity_in_file (res_file, "xxxxxxx", 3)

    return value

#--------------------------------------------------------------------------------------#
def search_TOT_PRES_RISE(file):
    print "--------------------------------------"
    print "        TOT_PRES_RISE VALUE           "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute_total_pressure_rise", 2)
    # hexstream
    #if value == None:
    #    value = f3d_search_quantity_in_file (res_file, "xxxxxxx", 3)

    return value

#--------------------------------------------------------------------------------------#
def search_PS_inlet(file):
    print "--------------------------------------"
    print "        PS INLET VALUE                "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static_pressure", 2)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static pressure", 4)

    return value

#--------------------------------------------------------------------------------------#
def search_PS_outlet(file):
    print "--------------------------------------"
    print "        PS OUTLET VALUE               "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static_pressure", 3)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Static pressure", 5)

    return value

#--------------------------------------------------------------------------------------#
def search_PT_inlet(file):
    print "--------------------------------------"
    print "        PT INLET VALUE                "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute_total_pressure", 2)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute total pressure", 5)

    return value

#--------------------------------------------------------------------------------------#
def search_PT_outlet(file):
    print "--------------------------------------"
    print "        PT OUTLET VALUE               "
    print "--------------------------------------"

    res_file = (os.path.splitext(file))[0] + '.mf'

    value = None
    # euranus
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute_total_pressure", 3)
    # hexstream
    if value == None:
        value = f3d_search_quantity_in_file (res_file, "Absolute total pressure", 6)

    return value

#--------------------------------------------------------------------------------------#
def search_TS_inlet(file):
    
    length=len(file)
    Results_file=file[0:length-3]+'mf'
    
    word=' '
    f=open(Results_file)
    while get_string(word,1)!='Static_temperature' :
        word=f.readline()    
    value=get_float(word,2)
    print "--------------------------------------"
    print "         TS INLET VALUE               "
    print "--------------------------------------"
    print value
    f.close() 
    return value

#--------------------------------------------------------------------------------------#
def search_TS_outlet(file):
    
    length=len(file)
    Results_file=file[0:length-3]+'mf'
    
    word=' '
    f=open(Results_file)
    while get_string(word,1)!='Static_temperature' :
        word=f.readline()    
    value=get_float(word,3)
    print "--------------------------------------"
    print "         TS OUTLET VALUE               "
    print "--------------------------------------"
    print value
    f.close() 
    return value
#--------------------------------------------------------------------------------------#
def search_TT_inlet(file):
    
    length=len(file)
    Results_file=file[0:length-3]+'mf'
    
    word=' '
    f=open(Results_file)
    while get_string(word,1)!='Absolute_total_temperature' :
        word=f.readline()    
    value=get_float(word,2)
    print "--------------------------------------"
    print "         TT INLET VALUE               "
    print "--------------------------------------"
    print value
    f.close() 
    return value

#--------------------------------------------------------------------------------------#
def search_TT_outlet(file):
    
    length=len(file)
    Results_file=file[0:length-3]+'mf'
    
    word=' '
    f=open(Results_file)
    while get_string(word,1)!='Absolute_total_temperature' :
        word=f.readline()    
    value=get_float(word,3)
    print "--------------------------------------"
    print "         TT OUTLET VALUE               "
    print "--------------------------------------"
    print value
    f.close() 
    return value

def search_quantity_interface_RS(file,rotor_stator_interface,quantity,position):
    
                
    length=len(file)
    Results_file=file[0:length-3]+'mf'
    #print 'rotor_stator_interface=',rotor_stator_interface
    if rotor_stator_interface[0]!=0:
        word=' '
        f=open(Results_file)
        exit=0;
        while exit==0:
            while get_string(word,1)!='*' :
                
                #print 'get_string(word,1)=',get_string(word,1)
                #print 'word=',word
                word=f.readline()
            #print 'found a star'
            #print "get_nb_string(word)=",get_nb_string(word)
            if get_nb_string(word)==9:
                if get_string(word,5)=="ROTOR/STATOR":
                    if get_integer(word,8)==rotor_stator_interface[0]:
                        exit=1
            word=f.readline()
        
        word=' '
        while get_string(word,1)!=quantity :
            word=f.readline()    
    
    
        value=get_float(word,position)
        f.close() 
        return value
    else:
        word=' '
        f=open(Results_file)
        exit=0;
        while get_string(word,1)!=quantity :        
                    word=f.readline()    
        
    
        value=get_float(word,rotor_stator_interface[1])
        f.close() 
        return value

#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
def get_string(string_,i):       #search the ith string
                                 #words are separeted by coma or by space
    if (string_!=''):
        character=string_[0]
        n0=0
        n1=0
        list=range(0,i)
        length=len(string_)
        for j in list:        
            n0=n1
            while character==' ' or character=='\t':
                if character!=',':
                    if n0<length :
                        character=string_[n0]
                        n0=n0+1
                    else:
                        break
                else:
                    break
            n1=n0
            while character!=' ' and character!='\t':
                if character!=',':
                    if n1<length :
                        character=string_[n1]
                        n1=n1+1
                    else:
                        break
                else:
                    break
        if string_[length-1]=="\n":
            n1=n1-1
        if n0>=1 :
            string_2=string_[n0-1:n1]
        else:
            string_2=string_[n0:n1]
        return string_2
    else:
        return 'exit'

def get_nb_string(string_):       #search the ith string
                                 #words are separeted by coma or by space
    if (string_!=''):
        character=string_[0]
        n0=0
        n1=0
        length=len(string_)
        exit=0
        nb_string=0
        while exit==0:
            n0=n1
            while character==' ' or character=='\t':
                if character!=',':
                    if n0<length :
                        character=string_[n0]
                        n0=n0+1
                    else:
                        break
                else:
                    break
            n1=n0
            while character!=' ' and character!='\t':
                if character!=',':
                    if n1<length :
                        character=string_[n1]
                        n1=n1+1
                    else:
                        break
                else:
                    break
            if n1>=length:
                exit=1
            else:
                if string_[n1]=="\n":
                    exit=1
            nb_string=nb_string+1        
        return nb_string
    else:
        return 'exit'

#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
def get_float(string_,i):              #search the ith float
    string_2 = get_string(string_,i)
    return float(string_2)

#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
def get_integer(string_,i):                #search the ith integer
    string_2 = get_string(string_,i)
    return int(string_2)

#--------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------#
#                          Select a block in multistage configuration                  #
#--------------------------------------------------------------------------------------#

def select_patches_of_the_block (string_):    
    block_name =string_
    block_name_length=len(block_name)
    block_name_extension=block_name[block_name_length-4:block_name_length]
    #----------[ Get the list of patches which correspond to the block ]----------------------------------------------
    GmtToggleBoundary()
    PATCHES_TO_REMOVE=[]
    PATCHES_TO_REMOVE=GetViewSurfaceList()
    #print "PATCHES_TO_REMOVE=",PATCHES_TO_REMOVE
    if len(PATCHES_TO_REMOVE)>0:
        apply(RemoveFromView,PATCHES_TO_REMOVE)

    PATCHES=[]
    #SOLID=GetViewActiveSurfacesList()
    SOLID=GetProjectSurfaceList()
    #print "block_name=",block_name
    #print 'block_name_extension=',block_name_extension
    if block_name_extension==".igg":
        for patch in  SOLID :
            length=len(patch)
            nb_white_space=string.count(patch,' ',0,length)
            if (nb_white_space==3):
                test=string.find(patch,'#',0,length)
                if string.find(patch,'#',0,length)==-1:
                    PATCHES.append(patch)
    else:
        for patch in  SOLID :
            #print 'patch=',patch
            GroupRemove(patch)
        for patch in  SOLID :
            length=len(patch)
            i=0
            include_patch=0
            while patch[i:i+1]!='#':
                if i>length:
                    break
                i=i+1
            if patch[0:i]==block_name:
                PATCHES.append(patch)

    return PATCHES
#--------------------------------------------------------------------------------------#
def search_rotor_stator_interface(project_file):
    OUTLET_SURFACE=[]
    OUTLET_SURFACE=GetViewActiveSurfacesList()
    #print 'OUTLET_SURFACE=',OUTLET_SURFACE
    patch_name=get_string(OUTLET_SURFACE[0],4)
    dobreak=0
    rotor_stator_interface_position=[]
    #print 'patch_name=',patch_name
    f=open(project_file)
    word=""
    while dobreak==0:
        while get_string(word,1)!='NI_BEGIN' and get_string(word,2)!='face': #Reference value of rho
            word=f.readline()
        while get_string(word,1)!='NI_BEGIN' and get_string(word,2)!='boundary_condition': #Reference value of rho
            word=f.readline()
        while get_string(word,1)!='NAME': #Reference value of rho
            word=f.readline()
        patch_tmp= get_string(word,2)
        #print 'patch_tmp=',patch_tmp
        if patch_tmp==patch_name:
            while get_string(word,1)!='BC_PARAMETERS_INDEX': #Reference value of rho
                word=f.readline()
            #print 'word=',word
            boundary_conditions=get_integer(word,2)
            dobreak=1        
    f.close()
    #print 'patch found'
    #print 'search rotor-stator interface'
    dobreak=0
    f=open(project_file)
    integer_entry_list=[]
    while dobreak==0:
        while get_string(word,1)!='NI_BEGIN' and get_string(word,2)!='bc_parameters': #Reference value of rho
            word=f.readline()
        while get_string(word,1)!='BC_PARAMETERS_INDEX': #Reference value of rho
            word=f.readline()
        boundary_conditions_tmp=get_integer(word,2)
        while get_string(word,1)!='TYPE': #Reference value of rho
            word=f.readline()
        if get_string(word,2)=='ROTOR-STATOR':
            while get_string(word,1)!='INTEGER_ENTRY': #Reference value of rho
                word=f.readline()
            integer_entry_tmp=get_integer(word,4)
            integer_entry_list.append(integer_entry_tmp)
            #print 'boundary_conditions_tmp=',boundary_conditions_tmp
            #print 'boundary_conditions=',boundary_conditions
            if boundary_conditions_tmp==boundary_conditions:
                dobreak=1
        else:
            if boundary_conditions_tmp==boundary_conditions:
                if get_string(word,2)=='INLET':
                    rotor_stator_interface_position.append(0)
                    rotor_stator_interface_position.append(2)
                    return rotor_stator_interface_position
                if get_string(word,2)=='OUTLET':
                    rotor_stator_interface_position.append(0)
                    rotor_stator_interface_position.append(3)
                    return rotor_stator_interface_position
            
        
    f.close()
    last_position=len(integer_entry_list)
    rotor_stator_interface_position.append(integer_entry_list[last_position-1])
    return rotor_stator_interface_position
#--------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------#
def search_block_domain(block_name):
    name_of_the_project=ProjectFile()
    local_block_name=block_name
    block_name_length=len(block_name)
    block_name_extension=block_name[block_name_length-4:block_name_length]
    f=open(name_of_the_project)
    integer_entry_list=[]
    j=1
    domain_list=[]
    word="initial_value"
    dobreak=0
    while dobreak==0:
        dobreak2=0
        while dobreak2==0:
            #print 'dobreak2=',dobreak2
            word=f.readline()
            #print 'word=',word
            if word=='':
                dobreak2=1
                break
            #print 'get_string(word,1)=',get_string(word,1)
            #print 'get_string(word,2)=',get_string(word,2)
            if get_string(word,1)!='NI_BEGIN':
                continue
            if get_string(word,2)!='block':
                continue
            dobreak2=1
            
        dobreak2=0
        while dobreak2==0:
            word=f.readline()
            if word=="":
                dobreak2=1
                break
            if get_string(word,1)!='NAME': #Reference value of rho
                continue
            dobreak2=1
            
        if word=="":
            dobreak=1
            continue
        name_of_the_block=get_string(word,2)
        #print 'name_of_the_block=',name_of_the_block
        length=len(name_of_the_block)
        if block_name_extension!=".igg":
            test=string.find(name_of_the_block,local_block_name,0,length)
        else:
            print 'name_of_the_block=',name_of_the_block
            #patch which has # were imprted so they are not needed since the block opened is searched
            test=string.find(name_of_the_block,"#",0,length)
            test=test*(-1)
        if test>-1:
            domain_list.append(j)
        j=j+1
    f.close()
    return domain_list

#--------------------------------------------------------------------------------------#

def is_this_block_HOH(block_number):
    Size=StructuredDomainSize(block_number)
    if 0==QntFieldExist('Abscissa') :
        QntFieldDerived(0,'Abscissa','x')
    else:
        QntFieldScalar('Abscissa')
    x_start=ProbeIJK(block_number,1,1,1)
    x_end=ProbeIJK(block_number,1,1,Size[2])
        
    if 0==QntFieldExist('Ordonate') :
        QntFieldDerived(0,'Ordonate','y')
    else:
        QntFieldScalar('Ordonate')
    y_start=ProbeIJK(block_number,1,1,1)
    y_end=ProbeIJK(block_number,1,1,Size[2])

    if 0==QntFieldExist('Height') :
        QntFieldDerived(0,'Height','z')
    else:
        QntFieldScalar('Height')
    z_start=ProbeIJK(block_number,1,1,1)
    z_end=ProbeIJK(block_number,1,1,Size[2])
    Z_range=[]
    Z_range=QuantityRangeDomain(block_number,0,1,0,1,0,1)
    if 0==QntFieldExist('Radius') :
        QntFieldDerived(0,'Radius','sqrt(x*x+y*y)')
    else:
        QntFieldScalar('Radius')
    R_range=[]
    R_range=QuantityRangeDomain(block_number,0,1,0,1,0,1)
    if R_range[1]<(Z_range[1]-Z_range[0]):
        Characteristic_length1=R_max
    else:
        Characteristic_length1=Z_range[1]-Z_range[0]
    if (sqrt((x_start-x_end)*(x_start-x_end)+(y_start-y_end)*(y_start-y_end)+(z_start-z_end)*(z_start-z_end))<Characteristic_length1/1000):
        HOH=1
    else:
        HOH=0
    return HOH
#--------------------------------------------------------------------------------------#

def search_meridional_blade_patches(project_file):
    f=open(project_file)
    word=""
    nb_domain=0
    while get_string(word,1)!="" and (get_string(word,1)!='MERIDIONNAL_PATCHPS' and get_string(word,1)!='MERIDIONNAL_PATCHSS'): 
        word=f.readline()
    while (get_string(word,1)=='MERIDIONNAL_PATCHPS' or get_string(word,1)=='MERIDIONNAL_PATCHSS') and get_string(word,1)!="": #Reference value of rho
        nb_domain=1+nb_domain
        word=f.readline()
    f.close()
    return nb_domain

def select_nearest_meridional_patch(R1,R0,Z1,Z0):
    R_Middle=(R1+R0)/2
    Z_Middle=(Z1+Z0)/2
    radius=sqrt(pow(R_Middle-R0,2)+pow(Z_Middle-Z0,2))
    active_surface=[]
    coef=0.1
    #print 'pi=',pi
    while (len(active_surface)==0):
        Coordinates_List=[]
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(pi/4.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(pi/4.0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(pi/2.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(pi/2.0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(3*pi/4.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(3*pi/4.0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(pi))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(pi))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(5*pi/4.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(5*pi/4.0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(3*pi/2.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(3*pi/2.0))
        Coordinates_List.append(Coordinates_List_tmp)
        Coordinates_List_tmp=[]
        Coordinates_List_tmp.append(R_Middle+radius*cos(7*pi/4.0))
        Coordinates_List_tmp.append(Z_Middle+radius*sin(7*pi/4.0))
        Coordinates_List.append(Coordinates_List_tmp)
        active_surface=[]
        for coor in Coordinates_List:
            SurfaceActivate(coor[1],coor[0],0,coor[1],coor[0],1)
            active_surface=GetViewActiveSurfacesList()
            if (len(active_surface))!=0:
                break
        coef=coef+0.1
