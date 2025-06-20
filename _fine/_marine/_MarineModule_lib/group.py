#                                                                             #
#                         Group patches by type                              #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : B. Mallol
#       Date	  : 2012
#______________________________________________________________________________
#
# Description: Group patches by type
# Changes:
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 08-10-2013		A. Mir			Extend to multi-domain cases
# 23-10-2018		A. Mir			#34559 extend to periodic BCs
#______________________________________________________________________________


from cfv import *

def Group_patches_by_type():
	
	print ' '
	print ' > START OF SCRIPT: GROUP_PATCHES_BY_TYPE'
	print ' '
			
	# check if surface probes
	qnt_exist_mf = 0
	qnt_exist_mf = QntFieldExist('Identifier')
	if qnt_exist_mf == 1:
		print "Grouping is not possible for surface probes"
		CFViewWarning("Grouping is not possible for surface probes")
		print '\n > END OF SCRIPT\n'
		return
	
	# delete all current groups
	def getGroupNames():
		activeSurfaces = GetViewActiveSurfacesList()
		projectSurfaces = GetProjectSurfaceList()
		groupNames = []
		for surf in projectSurfaces:
			UnselectTypeFromView('')
			SelectFromProject(surf)
			tmpSurf = GetViewActiveSurfacesList()
			nSurf = len(tmpSurf)
			if nSurf > 1:
				groupNames.append(surf)
		UnselectTypeFromView('')
		SelectFromProject(*activeSurfaces)
		return groupNames
		
	tstGroups = getGroupNames()
	for group in tstGroups:
		GroupRemove(group)
		
	# Check if there are multiple domains
	ndom = NumberOfDomains()
	print ' > Number of domains in this project: ' + str(ndom)
	
	for i in range(ndom):
		if ndom > 1:
			dom_name = GetDomainNameByIndex(i+1) + '_'
		else:
			# Single domain: groups do not contain the domain name
			dom_name = ''

		# group Dom_i SOL
		UnselectTypeFromView('')  # Unselect all
		ActivateSurfacesFromDomainIndex(i+1,'SOL')
		group_SOL = GetViewActiveSurfacesList()
		if len(group_SOL) >= 2:
			group_name = dom_name + 'Solid'
			CreateSurfaceGroup(group_name, *group_SOL)

		# group Dom_i EXT
		UnselectTypeFromView('')
		ActivateSurfacesFromDomainIndex(i+1, 'EXT')
		group_EXT = GetViewActiveSurfacesList()
		if len(group_EXT) >= 2:
			group_name = dom_name + 'External'
			CreateSurfaceGroup(group_name,*group_EXT)

		# group Dom_i FNMB
		UnselectTypeFromView('')
		ActivateSurfacesFromDomainIndex(i+1, 'ConnectionNonMatching')
		group_FNMB = GetViewActiveSurfacesList()
		if len(group_FNMB) >= 2:
			group_name = dom_name + 'FNMB'
			CreateSurfaceGroup(group_name, *group_FNMB)

		# group Dom_i MIR
		UnselectTypeFromView('')
		ActivateSurfacesFromDomainIndex(i+1, 'MIR')
		group_MIR = GetViewActiveSurfacesList()
		if len(group_MIR) >= 2:
			group_name = dom_name + 'Mirror'
			CreateSurfaceGroup(group_name, *group_MIR)

		# 34559 group Dom_i PER
		UnselectTypeFromView('')
		ActivateSurfacesFromDomainIndex(i+1, 'PER')
		group_PER = GetViewActiveSurfacesList()
		if len(group_PER) >= 2:
			group_name = dom_name + 'Periodic'
			CreateSurfaceGroup(group_name, *group_PER)

	# clean and reselect Solid patches from Domain 1 only
	UnselectTypeFromView('')
	dom_name = GetDomainNameByIndex(1)
	group_name = dom_name + 'Solid'
	SelectFromProject(group_name)

	print '\n > END OF SCRIPT\n'