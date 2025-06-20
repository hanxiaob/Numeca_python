#                                                                             #
#                         Streamlines to upright position                     #
#_____________________________________________________________________________#
#
#	NUMECA International s.a
#
#	Implementator : A. Mir
#       Date	  : 2014
#______________________________________________________________________________
#
# Description: Streamlines to upright position
# Changes:
#
# DATE			IMPLEMENTER			TYPE OF MODIFICATION
# 08/08/2017	Julien Roulle		Changed the manner to check whether it's a 2D project or not		  
#_10/05/2019	Anna Mir			#37119___________________________________________


from cfv import *
import os
import numpy as np

def Streamlines_to_upright_position():
	
	def get_paths():

		#If any condition is not met, end = 1 will be return to stop the script
		end = [0]
			
		# Check 2D/3D first and stop if 2D
		qnt_exist_1 = 0
		qnt_exist_2 = 0
		qnt_exist_1 = QntFieldExist('Relative Velocity_Z')
		qnt_exist_2 = QntFieldExist('Velocity_Z')
		if qnt_exist_1 == 1:
			QntFieldRemove('Relative Velocity_Z')
		if qnt_exist_2 == 1:
			QntFieldRemove('Velocity_Z')
		if QntFieldExist('Relative Velocity') == 1:
			QntFieldDerived(0 ,'Relative Velocity_Z' ,'Relative Velocity_Z' ,'' ,'0')
			QntFieldVector('Relative Velocity_Z')
		if QntFieldExist('Velocity') == 1:
			QntFieldDerived(0 ,'Velocity_Z' ,'Velocity_Z' ,'' ,'0')
			QntFieldVector('Velocity_Z')
		SelectFromProjectRegExp('')
		range_vel = []
		range_vel = QuantityRangeActiveSurfaces()
		check_2d = 0
		if range_vel[0] == range_vel[1] and range_vel[0] == 0:
			check_2d = 1
		# Clean temporary quantities
		qnt_exist_1 = QntFieldExist('Relative Velocity_Z')
		qnt_exist_2 = QntFieldExist('Velocity_Z')
		if qnt_exist_1 == 1:
			QntFieldRemove('Relative Velocity_Z')
		if qnt_exist_2 == 1:
			QntFieldRemove('Velocity_Z')
		if check_2d == 1:  # If 2D project stop plugin
			print " > This plugin is not available for 2D projects."
			Warning("This plugin is not available for 2D projects.")
			return
			
	#Get Project path
		path = GetProjectPath()
		print ' > Computation path: ' + path

	#Get cfv project name	
		cfv_file = GetProjectName()
		computation = cfv_file[:-4]

	#Get sim file path	
		sim_file = computation + '.sim'
		sim_file = path + os.sep + sim_file
		print ' > sim file: '+  sim_file
		if (os.path.exists(sim_file) == 0):
			print "SIM file is not present in the computation path"
			#Warning("SIM file is not present in the computation path")
			CFViewWarning("SIM file is not present in the computation path")
			end[0] = 1
			return end
			
	#Get the body_param.dat files
		param_file = computation + '_body_param.dat'
		param_file = path + os.sep + param_file
		if (os.path.exists(param_file) == 0): 
			print 'body_param.dat file is not present in the computation path'
			#Warning("body_param.dat file is not present in the computation path")
			CFViewWarning("body_param.dat file is not present in the computation path")
			end[0] = 1
			return end
	#Get the bodies
		f = open(param_file, 'r')
		param_lines = f.readlines()
		n_bodies = 0
			
		for i in range(len(param_lines)):
			if ('Number of moving bodies' in param_lines[i]):
				n_bodies = param_lines[i+2].split()
				n_bodies = int(n_bodies[0])			
				print ' > Number of bodies: ' + str(n_bodies)
				if (n_bodies != 1):
					print 'This plugin is not available when more than one body is defined'
					#Warning("This plugin is not available when more than one body is defined")
					CFViewWarning("This plugin is not available when more than one body is defined")
					end[0] = 1
					return end
			
			if ('Parameters of the body' in param_lines[i]):
				b_name = str(param_lines[i].split()[6])
				print ' > Body name: ' + str(b_name)
				break
			
		f.close()

	#Get Mvt_<body>.dat file
		mvt_file = 'Mvt_' + str(b_name) + '.dat'
		mvt_file = path + os.sep + mvt_file
		print ' > Mvt file: '+  mvt_file
		if (os.path.exists(mvt_file) == 0):
			print 'Mvt file is not present in the computation path'
			#Warning("Mvt file is not present in the computation path")
			CFViewWarning("Mvt file is not present in the computation path")
			end[0] = 1
			return end
		
	#Get isis2cfview.input
		i2c_file = path + os.sep + 'isis2cfview.input'
		print ' > isis2cfview.input file: ' + i2c_file
		if (os.path.exists(i2c_file) == 0): 
			print "isis2cfview.input file is not present in the computation path"
			#Warning("isis2cfview.input file is not present in the computation path")
			CFViewWarning("isis2cfview.input file is not present in the computation path")
			end[0] = 1
			return end
		
	#Set streamline file paths
		streamline_file = 'streamlines_final_position.dat'
		streamline_file = path + os.sep + streamline_file
		name_exists = os.path.exists(streamline_file)
		i = 0
		while (name_exists == 1):
			if (os.path.exists(streamline_file) == 1):
				i+= 1
				print ' > The file ' + streamline_file + ' already exists. Renaming file'
				streamline_file = 'streamlines_final_position_' + str(i) + '.dat'
				streamline_file = path + os.sep + streamline_file
				name_exists = os.path.exists(streamline_file)
				
			else:
				name_exists = 0		
		file_num = i	
		print ' > Streamline file: ' + streamline_file
		
	#Set out_file (same number as teh streamline file)
		if (file_num == 0):
			out_file = 'streamlines_upright_position.dat'
			out_file = path + os.sep + out_file
		else:
			out_file = 'streamlines_upright_position_' + str(file_num) + '.dat'
			out_file = path + os.sep + out_file
		
		return [mvt_file, sim_file, i2c_file, streamline_file, out_file]

		
	def export_streamlines(streamline_file):
		
		# If any condition is not met, end = 1 will be return to stop the script
		end = 0
		selectedLines = GetSelectedStreamlines()	
		
		# No streamlines selected in the interface
		if (selectedLines is None):
			print 'Select at least one streamline to export into upright position'
			#Warning("Select at least one streamline to export into upright position")
			CFViewWarning("Select at least one streamline to export into upright position")
			end = 1
		
		# Streamlines "Vector lines from section"
		elif ('Streamlines from section' in selectedLines):
			print ' > Streamlines drawn from section'
			list_lines = [streamline_file, selectedLines]
			# list_lines.append(streamline_file)
			# list_lines.append(selectedLines)
			ExportStreamLine(*list_lines)	
			
		# Streamlines from "Local Vector Line"	
		else:
			print ' > Local Streamlines'
			nlines = len(selectedLines)
			print ' > Number of streamlines = '+ str(nlines)		
			list_lines = []
			list_lines.append(streamline_file)
			for i in range(nlines):
				list_lines.append(selectedLines[i])
			
			print' > Exported streamlines:'
			for i in range (nlines):
				print '\t',selectedLines[i]
			
			ExportStreamLine(*list_lines)
			
		return end

	def read_streamlines(streamline_file):
		
		# Read the streamline file to store info
		with open(streamline_file, 'r') as f:
			s_lines = f.readlines()

			# First read of file to check number points for each streamline
			nstreamlines = 0
			npointsmax = 0
			npoints = []

			for i in range (len(s_lines)):
				if 'XYZ' in s_lines[i]:
					npoints.append(int(s_lines[i+1]))
					if npoints[nstreamlines] > npointsmax:
						npointsmax = npoints[nstreamlines]
					nstreamlines += 1

			print '------------------------------------------------------------------------------------------------'
			print ' > Number of streamlines read from file:', nstreamlines
			print ' > Number of points in each streamline:', npoints
			print ' > Initial coordinates:'

			# Second read of file to store coordinates
			coordinates = np.zeros ((nstreamlines, 3, npointsmax))
			for i in range(nstreamlines):
				if i == 0:
					initial = 3
				else:
					initial += npoints[i-1] + 3

				for k in range(npoints[i]):
					for j in range(3):
						coordinates[i][j][k] = float(s_lines[initial+k].split(' ')[j])

				print coordinates[i,:,:]
				
		return [coordinates, npoints, nstreamlines]
			
	def get_translation_rotation(mvt_file, sim_file, i2c_file):
		""" INPUT: Mvt_file_name, sim file
			Returns:trans(3x1), rot(3x3)"""
		
		# Variable initialization
		cardan_active = 0
		trans = np.zeros((3))
		anglex = 0.0
		angley = 0.0
		anglez = 0.0
		rotx = np.identity(3)
		roty = np.identity(3)
		rotz = np.identity(3)
		
		# Get initial position from SIM file (cardan angle, initial GC/reference point position)
		with open(sim_file, 'r') as f:
			sim_lines = f.readlines()
		print '------------------------------------------------------------------------------------------------'
		for i in range (len(sim_lines)):
			# Check if cardan angles are active. If yes, save them in angle variables
			if 'CARDAN ANGLES'in sim_lines[i] and  'YES' in sim_lines[i+2]:
					cardan_active = 1			
					print ' > Cardan angles are active in this computation'
					
			if 'ORIENTATION' in sim_lines[i] and cardan_active ==1:
				anglex = -float(sim_lines[i+2].split()[0])
				angley = -float(sim_lines[i+2].split()[1])
				anglez = -float(sim_lines[i+2].split()[2])
				print ' > Cardan angle values recorded [rad]:'
				print -anglex,-angley, -anglez
							
		# Look for the initial CG position and store it
			if 'POSITION GC' in sim_lines[i]:
				for j in range(3):
					trans[j] = -float(sim_lines[i+2].split()[j])
						
			if 'BODY' in sim_lines[i] and 'REFERENCE POINT' in sim_lines[i]:
				for j in range(3):
					trans[j] = -float(sim_lines[i+2].split()[j]) 
				
		print ' >  Initial CG position recorded [m]:'
		print -trans		

		# Get final position of body from Mvt file
		with open(mvt_file, 'r') as f:
			mvt_lines = f.readlines()
		
		for i in range(len(mvt_lines)):
			# print i
			if 'VARIABLES' in mvt_lines[i]:
				dofs = mvt_lines[i].split(',')

				for j in range(len(dofs)):
					# print j
					
					if dofs[j] == '"Tx0"':
						trans[0] += float(mvt_lines[len(mvt_lines)-1].split()[j])
						trans[0] = -trans[0]
										
					if dofs[j] == '"Ty0"':
						trans[1] += float(mvt_lines[len(mvt_lines)-1].split()[j])				
						trans[1] = -trans[1]
						
					if dofs[j] == '"Tz0"':
						trans[2] += float(mvt_lines[len(mvt_lines)-1].split()[j])
						trans[2] = -trans[2]	
						
					if dofs[j] == '"Rx0"' or dofs[j] == '"Rx1"' or dofs[j] == '"Rx2"':
						anglex += float(mvt_lines[len(mvt_lines)-1].split()[j])
						
						if anglex > 2*np.pi: anglex = anglex % 2 * np.pi
											
						anglex = -anglex
						c = np.cos(anglex)
						s = np.sin(anglex)
						
						rotx = ([[1.0, 0.0, 0.0],
								 [0.0, c, -s],
								 [0.0, s, c]])
											
					if dofs[j] == '"Ry0"' or dofs[j] == '"Ry1"' or dofs[j] == '"Ry2"':
						angley += float(mvt_lines[len(mvt_lines)-1].split()[j])
						
						if angley > 2*np.pi: angley = angley % 2*np.pi
						
						angley = -angley
						c = np.cos(angley)
						s = np.sin(angley)
						
						roty = ([[c, 0.0, s],
								[0.0, 1.0, 0.0],
								[-s, 0.0, c]])
									
					if dofs[j] == '"Rz0"' or dofs[j] == '"Rz1"' or dofs[j] == '"Rz2"':
						anglez += float(mvt_lines[len(mvt_lines)-1].split()[j])
						
						if anglez > 2*np.pi: anglez = anglez % 2 * np.pi
						
						anglez = -anglez
						c = np.cos(anglez)
						s = np.sin(anglez)
						
						rotz = ([[c, -s, 0.0],
								[s, c, 0.0],
								[0.0, 0.0, 1.0]])
										
					if '"Vx"' in dofs[j] or '"Vy"' in dofs[j] or '"Vz"' in dofs[j] or 'dR' in dofs[j]:
						# print 'Lets stop!'
						break
				break

		# Check travelling shot used in isis2cfview
		with open(i2c_file, 'r') as f:
			i2c_lines = f.readlines()

		trshot_body = 0
		for i in range(len(i2c_lines)):
			if 'BODY INDEX FOR TRAVELLING SHOT'in i2c_lines[i]:
				trshot_body = i2c_lines[i+1].split()
				if trshot_body == 0:
					break
						
			if 'DOF ACTIVATION FOR TRAVELLING SHOT' in i2c_lines[i]:
				if trshot_body != 0:
						trshot = i2c_lines[i+1].split()
						print ' > Travelling shot parameters:'
						print trshot
									
						if int(trshot[0]) == 1:
							trans[0] = 0.0
				
						if int(trshot[1]) == 1:
							trans[1] = 0.0
			
						if int(trshot[2]) == 1:
							trans[2] = 0.0
				
						if int(trshot[3]) == 1:
							rotx = np.identity(3)
				
						if int(trshot[4]) == 1:
							roty = np.identity(3)
				
						if int(trshot[5]) == 1:
							rotz = np.identity(3)
						break

		# Compute translation and rotation matrix

		rot = np.dot(roty,rotz)
		rot = np.dot(rotx, rot)
		print '------------------------------------------------------------------------------------------------'
		print ' > Total translation [m]', trans
		print ' > Rotation angles [rad]', anglex, angley, anglez
		print ' > Rotation Matrix\n', 
		print rot
		print '------------------------------------------------------------------------------------------------'
			
		return [trans, rot]

	def transform(coordinates, trans, rot, nstreamlines, npoints):
		""" INPUT = coordinates, trans, rotation
			Returns: coordinates"""
		# print ' > Coordinates after translation [m]:'
		for i in range(nstreamlines):
			for k in range(npoints[i]):
				for j in range(3):
					coordinates[i][j][k] += trans[j]
			# print coordinates [i,:,:]

		print '------------------------------------------------------------------------------------------------'
		print ' > Coordinates after translation and rotation [m]:'
		for i in range(nstreamlines):
			coordinates[i,:,:] = np.dot(rot, coordinates[i,:,:])
			print coordinates[i,:,:]
		print '------------------------------------------------------------------------------------------------'
		return coordinates

	def write_output(coordinates, out_file, npoints):
		""" Write new streamlines in out_file"""

		header = ' > Streamline coordinates in initial position (before computation motions)\n'
		with open(out_file, 'w') as g:
			g.write(header)
			counter = 1
			for data_slice in coordinates:
				g.write('Streamline %s \n' % counter)
				g.write('XYZ \n')
				g.write(('%s \n' % npoints[counter-1]))
				np.savetxt(g, np.transpose(data_slice))
				counter += 1
		return

	def main():
		""" Run all other functions"""

		print '\n > START OF SCRIPT: STREAMLINES_TO_UPRIGHT_POSITION\n'

		# Get all necessary files paths
		paths = get_paths()
		end = paths[0]			
		if end == 1:  # Some files missing, 2D...
			return
		else:
			mvt = paths[0]
			sim = paths[1]
			i2c = paths[2]
			streamline_file = paths[3]
			out_file = paths[4]
				
			# Call function to export streamlines selecetd in the GUI of CFView
			export_fail = export_streamlines(streamline_file)
			if export_fail == 1:
				return
			else:
				# Store streamline coordinates and data
				stream = read_streamlines(streamline_file)			
				coord = stream[0]
				npoints = stream[1]
				nstreamlines = stream[2]

				# 37598 stop if no streamlines selected
				if nstreamlines == 0:
					txt = 'Please select at least one streamline in the graphical interface.'
					print ' > {}'.format(txt)
					cfv.Warning(txt)
					return

				# Get translation and rotation matrixes
				transformation = get_translation_rotation(mvt, sim, i2c)
				translation = transformation[0]
				rotation = transformation [1]

				# Transform coordinates and save them in the out_file
				final_coord = transform (coord, translation, rotation, nstreamlines, npoints)
				
				write_output(final_coord, out_file, npoints)

				print '\n > The modified streamlines have been successfully saved in the file {}\n'.format(out_file)

	main()
	print '\n > END OF SCRIPT\n'
