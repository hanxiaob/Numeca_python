#                                                                             #
#                         Represent water line                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 2012
#______________________________________________________________________________
#
# Description: Represent water line
# Changes:
#
# DATE        IMPLEMENTER         TYPE OF MODIFICATION
#
#______________________________________________________________________________


from cfv import *

def Represent_water_line():
	
	print ' '
	print ' > START OF SCRIPT: REPRESENT_WATER_LINE'
	print ' '
	
	# check if mono or multi-fluid project
	qnt_exist_mf = 0
	qnt_exist_mf2 = 0
	qnt_exist_mf = QntFieldExist('Mass Fraction')
	qnt_exist_mf2 = QntFieldExist('MASS FRACTION')
	if qnt_exist_mf == 0 and qnt_exist_mf2 == 0:
		print "Water line representation is not possible for mono-fluid projects and surface probes"
		#Warning("Water line representation is not possible for mono-fluid projects and surface probes")
		CFViewWarning("Water line representation is not possible for mono-fluid projects and surface probes")
		print ' '
		print ' > END OF SCRIPT'
		print ' '
	else:
		def is_under_water():
			eps=1e-8
			MF_min=0.1
			if qnt_exist_mf == 1:
				qntName = 'Mass Fraction'
			else:
				qntName = 'MASS FRACTION'
			qntDef=qntName+'>'+str(MF_min)
			QntFieldScalar(qntName)
			surfList=GetViewSurfaceList()
			UnselectTypeFromView('')
			SelectTypeFromProject('SOL')    
			qnt_exist_mf3 = QntFieldExist('underwater')
			if qnt_exist_mf3 == 0:
				QntSurfaceDerived(0 ,'underwater' ,qntDef ,'' ,'0')
			QntSolidScalar('underwater')
			area=GmtArea()
			integ=SclIntegral()
			SelectFromProject(*surfList)
			QntSolidRemove('underwater')
			if area -  integ < eps:
				return 1
			else:
				return 0

		if is_under_water() == 0:
			UnselectFromViewRegExp('')
			SelectTypeFromProject('SOL')
			if qnt_exist_mf == 1:
				QntFieldScalar('Mass Fraction')
			else:
				QntFieldScalar('MASS FRACTION')
			SclIsolineValue(0.5)
		else:
			print "Body is fully submerged. Impossible to draw the water line."
			#Warning("Body is fully submerged. Impossible to draw the water line.")
			CFViewWarning("Body is fully submerged. Impossible to draw the water line.")
			print ' '
			print ' > END OF SCRIPT'
			print ' '
	
	print ' '
	print ' > END OF SCRIPT'
	print ' '