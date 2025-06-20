#--------------------------------------------------------------------------------------#
#                          efficiency 3D                                               #
#--------------------------------------------------------------------------------------#
#    NUMECA International                                                              #
#       E. Robin                                                            nov 1999   #
#--------------------------------------------------------------------------------------#
# Description : group the various operations to be done for the computation of an      #
#               efficiency on a 3D                                                     #
#--------------------------------------------------------------------------------------#

from CFView import *
from math import *

#--------------------------------------------------------------------------------------#

def computeSurfaceMassFlow(surfName):
    SelectFromProject(surfName)
    QntFieldVector('Vxyz')
    return VectorWeightedFlux('Density')

#--------------------------------------------------------------------------------------#

def computeTorque(axis):
    SelectFromViewRegExp('*Solid*')
    QntFieldScalar('Static Pressure')
    d = axis[0]
    p = axis[1]
    return SclBoundaryTorqueAmplitude(p[0],p[1],p[2],d[0],d[1],d[2])

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoPt(surfName):
    if 0==QntFieldExist('RhoPt') :
	QntFieldDerived(0,'RhoPt','Density*Absolute Total Pressure')

    SelectFromProject(surfName)
    QntFieldVector('Vxyz')
    return VectorWeightedFlux('RhoPt')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoTt(surfName):
    if 0==QntFieldExist('RhoTt') :
	QntFieldDerived(0,'RhoTt','Density*Absolute Total Temperature')

    SelectFromProject(surfName)
    QntFieldVector('Vxyz')
    return VectorWeightedFlux('RhoTt')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoPs(surfName):
    if 0==QntFieldExist('RhoPs') :
	QntFieldDerived(0,'RhoPs','Density*Static Pressure')

    SelectFromProject(surfName)
    QntFieldVector('Vxyz')
    return VectorWeightedFlux('RhoPs')

#--------------------------------------------------------------------------------------#

def computeSurfaceRhoTs(surfName):
    if 0==QntFieldExist('RhoPs') :
	QntFieldDerived(0,'RhoPs','Density*Static Temperature')
    return VectorWeightedFlux('RhoTs')

#--------------------------------------------------------------------------------------#

def compressorIsentropicTot2Tot(inletName, outletName, gamma):
    if 0==QntFieldExist('Density'):
	errorBox('Quantity \'Density\' does not exist')
	return 
    if 0==QntFieldExist('Vxyz'):
	errorBox('Quantity \'Vxyz\' does not exist')
	return

    pt1=computeSurfaceRhoPt(inletName)
    tt1=computeSurfaceRhoTt(inletName)
    pt2=computeSurfaceRhoPt(outletName)
    tt2=computeSurfaceRhoTt(outletName)
	
    return ((pt2/pt1)**((gamma-1)/gamma)-1) / ((tt2/tt1)-1)

#--------------------------------------------------------------------------------------#

def turbineIsentropicTot2Tot(inletName, outletName, gamma):
    if 0==QntFieldExist('Density'):
	errorBox('Quantity \'Density\' does not exist')
	return 
    if 0==QntFieldExist('Vxyz'):
	errorBox('Quantity \'Vxyz\' does not exist')
	return

    pt1=computeSurfaceRhoPt(inletName)
    tt1=computeSurfaceRhoTt(inletName)
    pt2=computeSurfaceRhoPt(outletName)
    tt2=computeSurfaceRhoTt(outletName)
	
    return 100*(1-(tt2/tt1)) / (1-(pt2/pt1)**((gamma-1)/gamma))

#--------------------------------------------------------------------------------------#

def compressorIncompressibleTot2Tot(inletName, outletName, rho, omega, axis):
    if 0==QntFieldExist('Density'):
	errorBox('Quantity \'Density\' does not exist')
	return 
    if 0==QntFieldExist('Vxyz'):
	errorBox('Quantity \'Vxyz\' does not exist')
	return

    m1 = abs(computeSurfaceMassFlow(inletName))
    m2 = abs(computeSurfaceMassFlow(outletName))

    pt1= abs(computeSurfaceRhoPt(inletName)/m1)
    pt2= abs(computeSurfaceRhoPt(outletName)/m2)

    torque = abs(computeTorque(axis))

    return m2*(pt2-pt1) / rho / omega / torque

#--------------------------------------------------------------------------------------#
#                          efficiency 3D                                               #
#--------------------------------------------------------------------------------------#
