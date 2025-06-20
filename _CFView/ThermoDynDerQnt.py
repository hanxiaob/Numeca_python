#--------------------------------------------------------------------------------------------#
#                     ThermoDynDerQnt.py                                                     #
#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         Etienne Robin                                                           jan 2000   #
#--------------------------------------------------------------------------------------------#
# Description : implements the thermodynamics quantities that can be derived from basic ones #
# Note : added Units System conversion (rotationSpeed and Cp are always in MKS)              #
#--------------------------------------------------------------------------------------------#

from CFView import *

#--------------------------------------------------------------------------------------------#

def computeWxyz() :
    if 0==QntFieldExist('Vxyz') : 
	rawErrorBox('Unable to compute Wxyz, Vxyz not available')
	return

    QntFieldDerived(2,
		    'Wxyz',
		    'Vxyz_X+velocityCF * rotationSpeed * y/lengthCF',
		    'Vxyz_Y-velocityCF * rotationSpeed * x/lengthCF',
		    'Vxyz_Z')

#--------------------------------------------------------------------------------------------#

def computeVxyz() :
    if 0==QntFieldExist('Wxyz') : 
	rawErrorBox('Unable to compute Vxyz, Wxyz not available')
	return

    QntFieldDerived(2,
		    'Vxyz',
		    'Wxyz_X-velocityCF * rotationSpeed * y/lengthCF',
		    'Wxyz_Y+velocityCF * rotationSpeed * x/lengthCF',
		    'Wxyz_Z')

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def computePGWxyz() : computeWxyz()
def computePGVxyz() : computeVxyz()

#--------------------------------------------------------------------------------------------#

def computePGAbsoluteTotalTemperature() :
    print 'computePGAbsoluteTotalTemperature'
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Total Temperature",
		    "Static Temperature + temperatureCF* 0.5* (Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/velocityCF/velocityCF / cp")

#--------------------------------------------------------------------------------------------#

def computePGRelativeTotalTemperature() :
    print 'computePGRelativeTotalTemperature'
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Total Temperature",
		    "Static Temperature + temperatureCF* 0.5*(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/velocityCF/velocityCF/ cp")

#--------------------------------------------------------------------------------------------#

def computePGAbsoluteTotalPressure() :
    print 'computePGAbsoluteTotalPressure'
    if 0==QntFieldExist('Static Temperature')         : 
	rawErrorBox('Static Temperature is not available')
	return
    if 0==QntFieldExist('Static Pressure')            : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Absolute Total Temperature') : computePGAbsoluteTotalTemperature()

    QntFieldDerived(0,
		    "Absolute Total Pressure",
		    "Static Pressure*exp(gamma/(gamma-1)*log(Absolute Total Temperature/Static Temperature))")

#--------------------------------------------------------------------------------------------#

def computePGRelativeTotalPressure() :
    print 'computePGRelativeTotalPressure'
    if 0==QntFieldExist('Static Temperature')         : 
	rawErrorBox('Static Temperature is not available')
	return
    if 0==QntFieldExist('Static Pressure')            : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Relative Total Temperature') : computePGRelativeTotalTemperature()

    QntFieldDerived(0,
		    "Relative Total Pressure",
		    "Static Pressure*exp(gamma/(gamma-1)*log(Relative Total Temperature/Static Temperature))")

#--------------------------------------------------------------------------------------------#

def computePGSpeedOfSound() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return
    if 0==QntFieldExist('Density')         : 
	rawErrorBox('Density is not available')
	return

    QntFieldDerived(0,
		    "Speed of Sound",
		    "velocityCF* sqrt(gamma*(Static Pressure/pressureCF)/(Density/densityCF))")

#--------------------------------------------------------------------------------------------#

def computePGAbsoluteMachNumber() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return
    if 0==QntFieldExist('Density')         : 
	rawErrorBox('Density is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Mach Number",
		    "sqrt(((Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/(lengthCF*lengthCF))*(Density/densityCF)/(gamma*Static Pressure/pressureCF))")

#--------------------------------------------------------------------------------------------#

def computePGRelativeMachNumber() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return
    if 0==QntFieldExist('Density')         : 
	rawErrorBox('Density is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Mach Number",
		    "sqrt(((Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/(lengthCF*lengthCF))*(Density/densityCF)/(gamma*Static Pressure/pressureCF))")

#--------------------------------------------------------------------------------------------#

def computePGInternalEnergy() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return
    if 0==QntFieldExist('Density')         : 
	rawErrorBox('Density is not available')
	return

    QntFieldDerived(0,
		    "Internal Energy",
		    "enthalpyCF * (Static Pressure/pressureCF) / (Density/densityCF) / (gamma-1)")

#--------------------------------------------------------------------------------------------#

def computePGAbsoluteTotalEnthalpy() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Total Enthalpy",
		    "enthalpyCF* cp * (Static Temperature/temperatureCF) + enthalpyCF* 0.5*(Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/velocityCF/velocityCF")

#--------------------------------------------------------------------------------------------#

def computePGRelativeTotalEnthalpy() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Total Enthalpy",
		    "enthalpyCF* cp * (Static Temperature/temperatureCF) + enthalpyCF* 0.5*(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/velocityCF/velocityCF")

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def computeINCWxyz() : computeWxyz()
def computeINCVxyz() : computeVxyz()

#--------------------------------------------------------------------------------------------#

def computeINCAbsoluteTotalTemperature() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Total Temperature",
		    "Static Temperature + temperatureCF* 0.5* (Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/velocityCF/velocityCF / cp")

#--------------------------------------------------------------------------------------------#

def computeINCRelativeTotalTemperature() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Total Temperature",
		    "Static Temperature + temperatureCF* 0.5* (Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/velocityCF/velocityCF / cp")

#--------------------------------------------------------------------------------------------#

def computeINCAbsoluteTotalPressure() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Total Pressure",
		    "Static Pressure + pressureCF* 0.5* (Density/densityCF) *(Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/velocityCF/velocityCF")

#--------------------------------------------------------------------------------------------#

def computeINCRelativeTotalPressure() :
    if 0==QntFieldExist('Static Pressure') : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Total Pressure",
		    "Static Pressure + pressureCF* 0.5* (Density/densityCF) *(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/velocityCF/velocityCF")


#--------------------------------------------------------------------------------------------#

def computeINCInternalEnergy() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return

    QntFieldDerived(0,
		    "Internal Energy",
		    "enthalpyCF* cp * (Static Temperature/temperatureCF)")

#--------------------------------------------------------------------------------------------#

def computeINCAbsoluteTotalEnthalpy() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return
    if 0==QntFieldExist('Static Pressure')    : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Vxyz') : computeVxyz()

    QntFieldDerived(0,
		    "Absolute Total Enthalpy",
		    "enthalpyCF* (cp* (Static Temperature/temperatureCF) + (Static Pressure/pressureCF) / (Density/densityCF) + 0.5*(Vxyz_X*Vxyz_X+Vxyz_Y*Vxyz_Y+Vxyz_Z*Vxyz_Z)/velocityCF/velocityCF)")

#--------------------------------------------------------------------------------------------#

def computeINCRelativeTotalEnthalpy() :
    if 0==QntFieldExist('Static Temperature') : 
	rawErrorBox('Static Temperature is not available')
	return
    if 0==QntFieldExist('Static Pressure')    : 
	rawErrorBox('Static Pressure is not available')
	return

    if 0==QntFieldExist('Wxyz') : computeWxyz()

    QntFieldDerived(0,
		    "Relative Total Enthalpy",
		    "enthalpyCF* (cp* (Static Temperature/temperatureCF) + (Static Pressure/pressureCF)/ (Density/densityCF) + 0.5*(Wxyz_X*Wxyz_X+Wxyz_Y*Wxyz_Y+Wxyz_Z*Wxyz_Z)/velocityCF/velocityCF)")

#--------------------------------------------------------------------------------------------#
#                     ThermoDynDerQnt.py                                                     #
#--------------------------------------------------------------------------------------------#
