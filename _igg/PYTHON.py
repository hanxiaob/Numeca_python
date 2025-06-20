
import sys,types

from math     import *
from Grid     import *
from Geometry import *
from Project  import *
from Butterfly import *
from meshConfiguration import *

from Session import *
from Geom    import *
from PythonViewing    import *
from PythonSurfSweep  import *

#-------------------------------------------------------------------------------------------

def switch_to_igg():
	switch_to_igg_()

#-------------------------------------------------------------------------------------------

def switch_to_autogrid5():
	switch_to_autogrid5_()

#-------------------------------------------------------------------------------------------

def connect_patches(patch1,patch2,dir1,dir2,type,tol):
	connect_patches_(patch1.impl,patch2.impl,dir1,dir2,type,tol)

#-------------------------------------------------------------------------------------------

def merge_patches():
	reduce_number_of_patches()

#-------------------------------------------------------------------------------------------
# Given a Block object or a string, interpeted as the block name, return the block pointer

def get_block_ptr_(block):
	if isinstance(block,Block): return block.impl
	else:                       return get_block_by_name_(block)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class GeomGroup:
	def __init__(self,initializer):
		if type(initializer) is types.StringType:	# asuming name of group
			self.impl = GeomGroup_get_group_(0,initializer)
		else:
			self.impl = initializer

	def delete(self):
		GeomGroup_delete_(0,self.impl)
		
	def add_items(self,*items):
		curvs = []
		surfs = []
		extract_curves_surfs_(items,curvs,surfs)
		GeomGroup_add_items_(self.impl,curvs,surfs)

	def remove_items(self,*items):
		curvs = []
		surfs = []
		extract_curves_surfs_(items,curvs,surfs)
		GeomGroup_remove_items_(self.impl,curvs,surfs)

	def get_curves(self):
		curvs = []
		final_list = []
		curvs = get_all_curve_names_(self.impl)
		for curve_obj in curvs:
			final_list.append(Curve(get_curve_by_name_(self.impl,Session.get_context_name(curve_obj))))
		return final_list

	def get_surfaces(self):
		surfs = []
		final_list = []
		surfs = get_all_surface_names_(self.impl)
		for surface_obj in surfs:
			final_list.append(Surface(get_surf_by_name_(self.impl,Session.get_context_name(surface_obj))))
		return final_list

	def get_curve_names(self):
		curvs = []
		curvs = get_all_curve_names_(self.impl)
		return curvs

	def get_surface_names(self):
		surfs = []
		surfs = get_all_surface_names_(self.impl)
		return surfs
		
#------------------------------------------------------------------------------------------------

def create_geometry_group(name,*items):
	gg = GeomGroup(GeomGroup_create_(name))
	for item in items: gg.add_items(item)
	return gg

#------------------------------------------------------------------------------------------------
# Return a geometry group (GeomGroup class) by giving its name and possibly the geometry repository in which it is contained
# (should be of class Geometry). Useful for autogrid import CAD.

def geometry_group(name, geometry_repository=0):
	geom_rep = 0
	if geometry_repository != 0:
		geom_rep = geometry_repository.impl
	group_pointer = GeomGroup_get_group_(geom_rep ,name)
	if group_pointer == 0:
		raise ValueError,"Wrong geometry group name"
	return GeomGroup(group_pointer)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#					Project class
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Project:
	def __init__(self,pointer):
		self.impl = pointer

	def get_geometry(self):
		return Geometry(Project_get_geometry())

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Segment:
    def __init__    (self,pointer)    :    self.impl = pointer
    def onCurve     (self,c)          :    attachCurve(self.impl,c.impl)
#    def reverse     (self)            :     Segment_reverseOrientation (self.impl)

    def smoother_bc(self,type,cell_width=0,exp=1,ncell=1):
        set_elliptic_smoother_bc(self.impl,type,[cell_width,exp,ncell])
    def increase_size(self,new_size):
        Segment_increase_points(self.impl,new_size)

    def set_number_of_points(self,new_size,propagate=1):
        Segment_set_number_of_points(self.impl,new_size,propagate)

    def setUpLimit  (self,upLimit):
        Segment_setUpLimit(self.impl,upLimit)

    def get_number_of_points(self):
        return Segment_num_grid_point_(self.impl)

    def get_discrete_length(self):
        length = 0.
        num_grid_points = self.get_number_of_points()
        for i in range(1,num_grid_points):
            length = length + distance(self.grid_point(i),self.grid_point(i+1))
        return length

    def grid_point(self,i):          # indices from [1.. !!!
        r = Segment_grid_point_(self.impl,i-1)
        return Point(r[0],r[1],r[2])

    def get_distribution_info(self):
        info_list = ("noname",) # added for backward
        info_list = info_list + Segment_get_distrib(self.impl)
        return info_list

    def cluster_start(self,dist):
        Set_distribution(0,self.impl,"START",dist)

    def cluster_end(self,dist):
        Set_distribution(0,self.impl,"END",dist)

    def cluster_both_ends(self,dist):
        Set_distribution(0,self.impl,'START_END',dist)

    def cluster_both_ends2(self,sDist,eDist,nCstCell):
        Set_distribution(0,self.impl,'START_END2',sDist,eDist,nCstCell)

    def cluster_bound_layer(self,spaceS,spaceE,thickS,thickE,nCellS,nCellE):
        Set_distribution(0,self.impl,'BOUND_LAYER',spaceS,nCellS,thickS,spaceE,nCellE,thickE)

    def cluster_tanh(self,sDist,eDist):
        Set_distribution(0,self.impl,'TANH',sDist,eDist)

    def cluster_uniform(self):
        Set_distribution(0,self.impl,'UNIFORM')

    def cluster_curvature(self,ratio,weight):
        Set_distribution(0,self.impl,'CURVAT',ratio,weight)

    def cluster_start_userDef_b2b(self,dist):
        B2BUserDef_cluster_cmd_(0,self.impl,"START",dist)

    def cluster_end_userDef_b2b(self,dist):
        B2BUserDef_cluster_cmd_(0,self.impl,"END",dist)

    def cluster_both_ends_userDef_b2b(self,dist):
        B2BUserDef_cluster_cmd_(0,self.impl,'START_END',dist)

    def cluster_both_ends2_userDef_b2b(self,sDist,eDist,nCstCell):
        B2BUserDef_cluster_cmd_(0,self.impl,'START_END2',sDist,eDist,nCstCell)

    def cluster_bound_layer_userDef_b2b(self,spaceS,spaceE,thickS,thickE,nCellS,nCellE):
        B2BUserDef_cluster_cmd_(0,self.impl,'BOUND_LAYER',spaceS,nCellS,thickS,spaceE,nCellE,thickE)

    def cluster_tanh_userDef_b2b(self,sDist,eDist):
        B2BUserDef_cluster_cmd_(0,self.impl,'TANH',sDist,eDist)

    def cluster_uniform_userDef_b2b(self):
        B2BUserDef_cluster_cmd_(0,self.impl,'UNIFORM')

    def cluster_curvature_userDef_b2b(self,ratio,weight):
        B2BUserDef_cluster_cmd_(0,self.impl,'CURVAT',ratio,weight)

    def get_length(self):
        return Segment_get_length_(self.impl)

    def cluster_user_defined(self,distribution):
        if isinstance(distribution, Distribution):
            result = set_user_defined_distribution_(self.impl,distribution.nopoints,distribution.impl)
            if   result ==  0: raise ValueError("Error in cluster_user_defined: dimensions mismatch")
            elif result == -1: raise ValueError("Error in cluster_user_defined: segment is frozen")
        else:
            raise ValueError("Give object of class Distribution")

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#					class TEdge
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class TEdge:
        def __init__(self,pointer):
                self.impl = pointer
		
	def set_curve_map(self,curve_map):
		TEdge_set_curve_map(self.impl,curve_map)

	def set_surf_map(self,surf_map):
		TEdge_set_surf_map(self.impl,surf_map)

	def set_surf_map_type(self,surf_map_type):
		surf_map = 0
		if   surf_map_type == "param": surf_map = 0
		elif surf_map_type == "plane": surf_map = 4
		else: raise "Wrong arg for set_surf_map_type"
		
		TEdge_set_surf_map_type(self.impl,surf_map)

def tedge(B,F,E,TE):
	return TEdge(Edge_get_tedge(block(B).face(F).edge(E).impl,TE))

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#					class Vertex
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Vertex:
        def __init__(self,pointer): self.impl = pointer

	def delete(self):
		Vertex_delete(self.impl)

	def attach_fix_point(self, edge=0, index=0):
		edgePointer = 0
		if edge and isinstance(edge, Edge): edgePointer = edge.impl
		refIndex = 0
		if index: refIndex = index - 1
		return FixedPoint(Vertex_attach_fix_point(self.impl, edgePointer, refIndex))

	def disconnect(self):
		Vertex_disconnect_(self.impl)

	def get_coords(self):
		res = Vertex_get_point_(self.impl)
		if   res[0]=="Point": return Point(res[1],res[2],res[3])
		elif res[0]=="CurvePointNorm": return CurvePointNorm(res[1],res[2])
		elif res[0]=="SurfPointNorm":  return SurfPointNorm(res[1],res[2],res[3])

	def get_norm_param(self, edge):
		if not isinstance(edge,Edge): return 0
		return Vertex_get_norm_param_(self.impl, edge.impl)
	#
	# Vertex mapping control
	#
	def set_curve_map(self,curve_map):
		TVertex_set_curve_map(self.impl,curve_map)

	def set_curve_int_map(self,map_flag):
		TVertex_set_curve_int_map(self.impl,map_flag)

	def set_curve_end_pt_map(self,map_flag):
		TVertex_set_end_pt_map(self.impl,map_flag)

	def set_surf_map(self,surf_map):
		TVertex_set_surf_map(self.impl,surf_map)


	#
	# Vertex movement
	#
	def move(self,new_pos):
		move_vertex(self,new_pos)

        def on_point(self,p):
		Vertex_move(self.impl,["PT",p.x,p.y,p.z])

        def on_curve(self,curve,param):
		c = get_curve_object(curve)

		# place the vertex
		Vertex_move(self.impl,["CURV",c.impl,param])

	def on_curve_normalized(self,curve,npar):
		c = get_curve_object(curve)

		# caculate absolute value of parameter
		p = c.calc_absolute(npar)

		# place the vertex
		Vertex_move(self.impl,["CURV",c.impl,p])

        def on_surf(self,surf,u,v):
		s = get_surf_object(surf)

		# place the vertex
		Vertex_move(self.impl,["SURF",s.impl,u,v])

	def on_surf_normalized(self,surf,nu,nv):
		s   = get_surf_object(surf)
		u,v = Surf_absolute(s.impl,nu,nv)
		# place the vertex
		Vertex_move(self.impl,["SURF",s.impl,u,v])

        def on_cci(self,c1,c2):
		# place the vertex
		Vertex_move(self.impl,["CCI",get_curve_object(c1).impl,get_curve_object(c2).impl])

	def set_tolerance(self,tol):
		Vertex_set_tol(self.impl,tol)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				class FixedPoint
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class FixedPoint:
	def __init__(self,pointer):
		self.impl = pointer

	def change_index(self,index,edge):
		FixedPoint_change_index_(self.impl,edge.impl,index-1)

	def delete(self):
		FixedPoint_delete_(self.impl)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				class Edge
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Edge:
    def __init__(self,pointer):
        self.impl = pointer

    def disconnect(self):
        Edge_disconnect_(self.impl)

    def num_vertex(self):
        return Edge_num_vertex(self.impl)

    def vertex(self,i):
        return  Vertex(Edge_vertex(self.impl,i-1))

    def delete(self):
        Edge_delete_(self.impl)

    def get_face_1(self):
        return Face(Edge_get_faces_(self.impl)[0])
	
    def get_face_2(self):
        return Face(Edge_get_faces_(self.impl)[1])
	
    def get_other_face(self,face):
        f1 = Edge_get_faces_(self.impl)[0]
        if face.impl == f1: return self.get_face_2()
        else:               return self.get_face_1()
	
    def change_index(self,*args):
        if len(args) == 1:
            f,index = self.get_face_1(),args[0]
        elif len(args) == 2:
            if isinstance(args[1],Face):
                raise ValueError,'Wrong expecting a Face'
            f,index = args[0],args[1]
        Edge_change_index_(f.impl,self.impl,index-1)

    def insert_fixed_point_at_norm_param(self,nparam):
        Edge_insert_fp_nparam(self.impl,nparam)
    def move_fixed_point(self,index,nparam):
        Edge_move_fp(self.impl,index-1,nparam)

    def get_number_of_points(self):
        return Edge_numGridPoint(self.impl)

    def grid_point(self, i):
        r = Edge_grid_point_(self.impl, i-1)
        return Point(r[0],r[1],r[2])
					    
    def num_segments (self)   : return Edge_numSegments(self.impl)
    def segment      (self,i) : return Segment(Edge_segment(self.impl,i-1))
    def insert_vertex(self,norm_param):
        return Vertex(Edge_insert_vertex(self.impl,norm_param))

    def create_curve(self,name=""):
        return Curve(Edge_create_curve_(self.impl,name))

	#
	# Edge movement
	#
    def on_point(self,vertex,p):
        Edge_move(self.impl,vertex.impl,"PT",p.x,p.y,p.z)

    def on_curve(self,vertex,curve,npar):
        c = get_curve_object(curve)
	      
        # place the vertex
        Edge_move(self.impl,vertex.impl,"CURV",c.impl,npar)

    def on_curve_normalized(self,vertex,curve,npar):
        c = get_curve_object(curve)

        # calculate absolute value of parameter
        p = c.calc_absolute(npar)
	      
        # place the vertex
        Edge_move(self.impl,vertex.impl,"CURV",c.impl,p)

    def on_surf(self,vertex,surf,u,v):
        s = get_surf_object(surf)

        # place the vertex
        Edge_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

    def on_surf_normalized(self,vertex,surf,nu,nv):
        s   = get_surf_object(surf)
        u,v = Surf_absolute(s.impl,nu,nv)
        # place the vertex
        Edge_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

    def on_cci(self,vertex,c1,c2):
        # place the vertex
        Edge_move(self.impl,vertex.impl,"CCI",get_curve_object(c1).impl,get_curve_object(c2).impl)

    def show_edge(self):
        show_hide_edges_("edge",1,self.impl)

    def hide_edge(self):
        show_hide_edges_("edge",0,self.impl)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				class Patch
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Patch:
        def __init__(self,pointer):
                self.impl = pointer

	def delete(self):
		Face_delete_patch_(self.impl)		

	# 2 following fcts only kept for backward, arguments order is wrong compare to ones retrieved in C++
	def divide(self,r):
		Patch_divide_(self.impl,r.imin,r.jmin,r.imax,r.jmax)		
	def set_limits(self,r):
		Patch_set_limits_(self.impl,r.imin,r.jmin,r.imax,r.jmax)

	def divide_by_range(self,r):
		Patch_divide_(self.impl,r.imin,r.imax,r.jmin,r.jmax)
		
	def resize(self,r):
		Patch_set_limits_(self.impl,r.imin,r.imax,r.jmin,r.jmax)

        def get_range(self):
                lim = Patch_get_limits_(self.impl)
                return Range(lim[0],lim[1],lim[2],lim[3])

        def num_of_1(self):
                lim = Patch_get_limits_(self.impl)
                return lim[1]-lim[0]+1

        def num_of_2(self):
                lim = Patch_get_limits_(self.impl)
                return lim[3]-lim[2]+1

        def grid_point(self,i,j):			# indices from [1.. !!!
                r = Patch_grid_point_(self.impl,i-1,j-1)
		return Point(r[0],r[1],r[2])

	def get_block_face_patch_indices(self):
		index_list = []
		patch_info = Patch_get_info_(self.impl)
		index_list.append(patch_info[0])
		index_list.append(patch_info[1])
		index_list.append(patch_info[2])
		return index_list
	
	def get_type(self):
		return Patch_get_info_(self.impl)[3]

	def get_connected_patch(self):
		patch_pointer = Patch_get_info_(self.impl)[4]
		if patch_pointer: return Patch(patch_pointer)
		else: return 0

	def get_connected_corner(self):
		return Patch_get_info_(self.impl)[5]

	def get_connected_orient(self):
		return Patch_get_info_(self.impl)[6]
		
	def get_periodic_sign(self):
		return Patch_get_info_(self.impl)[7]

	def set_type(self,type):
		if   type == "UND": itype = 0
		elif type == "CON": itype = 1
		elif type == "EXT": itype = 2
		elif type == "INL": itype = 3
		elif type == "MIR": itype = 4
		elif type == "OUT": itype = 5
		elif type == "PER": itype = 6
		elif type == "SNG": itype = 7
		elif type == "SOL": itype = 8
		elif type == "NMB": itype = 9
		elif type == "ROT": itype = 10
		elif type == "PERNM": itype = 11
                else : itype = 0
		Patch_set_type_(self.impl,itype)

	def get_name(self):
		return Patch_get_name_(self.impl)		
	def set_name(self,name):
		Patch_set_name_(self.impl,name)

        def get_family_name(self):
		return Patch_get_family_name_(self.impl)		
	def set_family_name(self,name):
		Patch_set_family_name_(self.impl,name)
                
	def hide_patches_texture(self):
		hide_patches_texture_(self.impl)
	def show_patches_texture(self,texture):
		show_patches_texture_(self.impl,texture)
	def show_solid(self,r,g,b):
		Patch_show_solid_(self.impl,r/255.,g/255.,b/255.)
	def hide_solid(self):
		Patch_hide_solid_(self.impl)
	def show_grid(self,r,g,b):
		Patch_show_grid_(self.impl,r/255.,g/255.,b/255.)
	def hide_grid(self):
		Patch_hide_grid_(self.impl)
	

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				class Face
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Face:
        def __init__(self,pointer):
		self.impl = pointer

	def disconnect(self):
	    Face_disconnect_(self.impl)

	def get_block(self):
		return Block(Face_get_block_(self.impl))
        def select(self):
                select_face(self.impl)	
	def get_n1(self):
            list = get_face_n1_n2(self.impl)
            return list[0]   
	def get_n2(self):
            list = get_face_n1_n2(self.impl)
            return list[1]   
	def calc_point(self,i,j):
            list = get_face_point(self.impl,i,j)
            return Point(list[0],list[1],list[2])   

	def set_node_coord(self,i,j,point):
            set_face_point(self.impl,i,j,point.x,point.y,point.z)

	def get_center(self):
            list = get_face_n1_n2(self.impl)
            i = (list[0]-1)/2
            j = (list[1]-1)/2
            list = get_face_point(self.impl,i,j)
            return Point(list[0],list[1],list[2])
	def get_center_normal(self):
            list = get_face_n1_n2(self.impl)
            i = (list[0]-1)/2
            j = (list[1]-1)/2
            p1 = self.calc_point(i,j)
            p2 = self.calc_point(i+1,j)
            p3 = self.calc_point(i,j+1)
	    v1 = p2-p1
	    v2 = p3-p1
            return Vector(v1.y*v2.z-v1.z*v2.y,-(v1.x*v2.z-v1.z*v2.x),(v1.x*v2.y-v1.y*v2.x))   

	def get_number(self):
                return Face_get_number_ (self.impl)

	def num_edges(self):
                return Face_numEdges (self.impl)

	def edge(self,i):
                return Edge(Face_edge(self.impl,i-1))

	def num_patches(self):
		return Face_num_patches_(self.impl)

	def patch(self,i):
		return Patch(Face_patch_(self.impl,i-1))

##	def clear_patches(self):
##		Face_clear_patches_(self.impl)

	def delete_patch(self,i):
		Face_delete_patch_(Face_patch_(self.impl,i-1))

	def new_patch(self,r):
		Face_new_patch_(self.impl,r.imin-1,r.imax-1,r.jmin-1,r.jmax-1)

        def get_range(self):
                lim = Face_limits(self.impl)
                return Range([1,lim[0],1,lim[1]])

	def create_internal_edge(self,dir,index):
                return Edge(Face_create_internal_edge(self.impl,dir,index))

	def create_internal_edge_on_curve(self,dir,index,
					  iglRatio1,iglRatio11,
					  iglRatio2,iglRatio22):
                return Edge(Face_create_igl_on_curve_(self.impl,dir,index,
						      iglRatio1,iglRatio11,
						      iglRatio2,iglRatio22))

	def create_grid_point(self,I,J):
		Face_create_igp_(self.impl,I-1,J-1)

	def linear_2Bnd(self,edges,range = 0,edge_map=1):
                if range == 0: range = self.get_range()	#take full face range
                if not isinstance(range,Range): raise TypeError,"Wrong range argument"

		edgem = 1
		if edges == "BND_12"	: edgem = 1
		else			: edgem = 2
		Face_linear2Bnd_(self.impl,edgem,range.imin,range.imax,range.jmin,range.jmax,edge_map)

	def cubic_2Bnd(self,edges,start1,end1,start2,end2,ratio1,ratio2,range = 0,edge_map=1):
                if range == 0: range = self.get_range()	#take full face range
                if not isinstance(range,Range): raise TypeError,"Wrong range argument"

		edgem = 1
		if edges == "BND_12"	: edgem = 1
		else			: edgem = 2
		Face_cubic2Bnd_(self.impl ,edgem,start1,end1,start2,end2,ratio1,ratio2,
				range.imin,range.imax,range.jmin,range.jmax,edge_map)

	def linear_4Bnd(self, range = 0,edge_map=1):
                if range == 0: range = self.get_range()	#take full face range
                if not isinstance(range,Range): raise TypeError,"Wrong range argument"
		
		Face_linear4Bnd_(self.impl,range.imin,range.imax,range.jmin,range.jmax,edge_map)

	def mapping_linear(self,surf,frange = 0,edge_map = 1):
                if frange == 0: frange = self.get_range()	#take full face range
                if not isinstance(frange,Range): raise TypeError,"Wrong range argument"

		surfp = get_surf_object(surf).impl
		Face_mapping_linear_(self.impl,surfp,frange.imin,frange.imax,
				     frange.jmin,frange.jmax,edge_map)
		
	def mapping_cubic(self,surf,edges,start1,end1,start2,end2,ratio1,ratio2,frange = 0,edge_map=1):
                if frange == 0: frange = self.get_range()	#take full face range
                if not isinstance(frange,Range): raise TypeError,"Wrong range argument"

		surfp = get_surf_object(surf).impl

		edgem = 1
		if edges == "BND_12"	: edgem = 1
		else			: edgem = 2
		Face_mapping_cubic_(self.impl,surfp,edgem,start1,end1,start2,end2,ratio1,ratio2,
				    frange.imin,frange.imax,frange.jmin,frange.jmax,edge_map)

	def project_on_surfs(self,surfs,bnd_proj = 0,validation = 2,projRatio = 10,frange = 0):
                if frange == 0: frange = self.get_range()	#take full face range
                if not isinstance(frange,Range): raise TypeError,"Wrong range argument"

		if isinstance(surfs,GeomGroup):
			Face_project_on_surfs_(self.impl,1,surfs.impl,bnd_proj,validation,projRatio,1,
					       frange.imin,frange.imax,frange.jmin,frange.jmax)
			return
		
                all_surfs = []
                if type(surfs) is types.ListType:
			for i in range(len(surfs)):
				all_surfs.append(get_surf_object(surfs[i]).impl)
		elif type(surfs) is types.StringType:	# assuming surface name
			all_surfs.append(get_surf_object(surfs).impl)

		Face_project_on_surfs_(self.impl,0,all_surfs,bnd_proj,validation,projRatio,1,
				       frange.imin,frange.imax,frange.jmin,frange.jmax)

	def smooth(self,smooth_factor = 1.,range = 0,edge_map=1):
                if range == 0: range = self.get_range()	#take full face range
                if not isinstance(range,Range): raise TypeError,"Wrong range argument"
		print range.imin
		print range.imax
		Face_smooth_(self.impl,smooth_factor,range.imin,range.imax,range.jmin,range.jmax,edge_map)

	def smooth_on_surface(self,surf,smooth_factor = 1.,range = 0,edge_map=1):
                if range == 0: range = self.get_range()	#take full face range
                if not isinstance(range,Range): raise TypeError,"Wrong range argument"

		surfp = get_surf_object(surf).impl
		
		Face_smooth_on_surface_(self.impl,surfp,smooth_factor,
					range.imin,range.imax,range.jmin,range.jmax,edge_map)

	def delete_operation(self, index):
		delete_operation_(self.impl, index)

	def copy_face(self, ref_face):
		Face_copy_(self.impl, ref_face.impl)

	#
	# Face movement
	#
        def on_point(self,vertex,p):
              Face_move(self.impl,vertex.impl,"PT",p.x,p.y,p.z)

	def on_curve(self,vertex,curve,npar):
	      c = get_curve_object(curve)
	      
	      # place the vertex
              Face_move(self.impl,vertex.impl,"CURV",c.impl,npar)

        def on_curve_normalized(self,vertex,curve,npar):
	      c = get_curve_object(curve)

	      # caculate absolute value of parameter
              p = c.calc_absolute(npar)
	      
	      # place the vertex
              Face_move(self.impl,vertex.impl,"CURV",c.impl,p)

        def on_surf(self,vertex,surf,u,v):
	      s = get_surf_object(surf)

	      # place the vertex
              Face_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

        def on_surf_normalized(self,vertex,surf,nu,nv):
	      s   = get_surf_object(surf)
	      u,v = Surf_absolute(s.impl,nu,nv)
	      # place the vertex
              Face_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

        def on_cci(self,vertex,c1,c2):
	      # place the vertex
              Face_move(self.impl,vertex.impl,"CCI",get_curve_object(c1).impl,get_curve_object(c2).impl)

	# -------- Coord Saving (according to current coarse grid levels) ------------
	#
	def save_coords(self,filename):
		Face_save_coords_(self.impl,filename)

	def save_patch_coords(self,filename):
		Face_save_patch_coords_(self.impl,filename)

        def save_boundary_coords(self,filename):
		Face_save_boundary_coords_(filename, self.impl)

	# Internal faces functions
	#
	def delete(self,delete_edges = 0):		# can only delete internal face !!
                Face_delete_(self.impl,delete_edges)

	def change_index(self,index):
		Face_change_index_(self.impl,index-1)
		
	#
	# Visualisation related commands
	#
	def show_face_grid(self):
		show_hide_face_grid_("face",1,self.impl)

	def hide_face_grid(self):
		show_hide_face_grid_("face",0,self.impl)

	def show_edges(self):
		show_hide_edges_("face",1,self.impl)

	def hide_edges(self):
		show_hide_edges_("face",0,self.impl)


#------------------------------------------------------------------------------------------------

def copy_face_range(ffrom,rfrom,fto,rto,dir1,dir2):
	Face_copy_range_(ffrom.impl,rfrom.imin,rfrom.imax,rfrom.jmin,rfrom.jmax,
			 fto.impl  ,rto  .imin,rto.imax  ,rto.jmin  ,rto.jmax,
			 dir1,dir2)


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def move_vertex(vertex,new_pos):
	Vertex_move(vertex.impl,format_point(new_pos))

def move_edge(edge,ref_vertex,new_pos):
	Edge_move(edge.impl,ref_vertex.impl,format_point(new_pos))

def move_face(face,ref_vertex,new_pos):
	Face_move(face.impl,ref_vertex.impl,format_point(new_pos))
	
def move_block(block,ref_vertex,new_pos):
	Block_move(block.impl,ref_vertex.impl,format_point(new_pos))
	
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				      class Block
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Block:
        def __init__(self,pointer):
                self.impl = pointer

	def disconnect(self):
		Block_disconnect_(self.impl)

	def delete(self):
		Block_delete_(self.impl)
		self.impl = 0

        def select(self):
                select_block(self.impl)	
		
        def set_size(self,i,j,k,propagate=0):
                Block_set_size(self.impl,i,j,k,propagate)

        def setBlockProperties(self,i):
                Block_set_properties_(self.impl,i)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# return Imax, Jmax, Kmax as array [0..2]

        def get_size(self):
                return Block_get_size(self.impl)

	def get_index(self):
		return Block_get_index_(self.impl)

	# Return RangIJK [1..][1..][1..]
        def get_range(self):
		size = Block_get_size(self.impl)
		return RangeIJK(1,size[0],1,size[1],1,size[2])

	def get_type(self):
		return Block_get_type_(self.impl)

	def set_type(self, value):
		Block_set_type_(self.impl, value)

	def get_repetition(self):
		res = get_repetition_(self.impl)
		type = "NONE"
		if   res[0] == 1: type = "TRANSLATION"
		elif res[0] == 2: type = "ROTATION"
		elif res[0] == 3: type = "MIRROR"
		num_repet = res[1]
		axis = Vector(res[3],res[4],res[5])
		origin = Point(res[6],res[7],res[8])
		result = [type, num_repet, origin, axis]
		return result
	
	def set_repetition(self,type,num_repet,*args):
		if type == "NONE":
			Block_set_repet_(self.impl,type,1)
		elif type == "ROTATION":
			orig = args[0]
			vec  = args[1]

			num_passage = 1
			if len(args) == 3:
				num_passage = args[2]
			Block_set_repet_(self.impl,type,num_repet,orig.x,orig.y,orig.z,vec.x,vec.y,vec.z,num_passage)
		elif type == "TRANSLATION":
			vec  = args[0]
			Block_set_repet_(self.impl,type,num_repet,vec.x,vec.y,vec.z)
		elif type == "MIRROR":
			orig = args[0]
			vec  = args[1]
			Block_set_repet_(self.impl,type,num_repet,orig.x,orig.y,orig.z,vec.x,vec.y,vec.z)
		else: raise ValueError,'Wrong repetition type'
		
        def num_of_I(self):
                return Block_get_size(self.impl)[0]

        def num_of_J(self):
                return Block_get_size(self.impl)[1]

        def num_of_K(self):
                return Block_get_size(self.impl)[2]

        def grid_point(self,i,j,k):			# indices from [1.. !!!
                r = Block_grid_point_(self.impl,i-1,j-1,k-1)
		return Point(r[0],r[1],r[2])

        def num_faces(self):
                return Block_numFaces (self.impl)

        def face(self,i):
                return Face(Block_face(self.impl,i-1))

        def get_all_faces(self):
		all_faces = []
		for i in range(self.num_faces()):
			all_faces.append(Face(Block_face(self.impl,i)))
                return all_faces

        def get_boundary_faces(self):
		all_faces = []
		for i in range(6):
			all_faces.append(Face(Block_face(self.impl,i)))
                return all_faces

	def extend(self,face):
		Block_extend_(face.impl)

	def change_axis(self,I,J,K):
		Block_revert_(self.impl,I,J,K)

	def split_block(self,dir,val):
		pointer_list = Block_split_(self.impl,dir,val)
		block_list = []
		for p in pointer_list:
			block_list.append(Block(p))
		return block_list

	def split_block_at_internal_faces(self):
		pointer_list = Block_split_at_internal_faces_(self.impl, 0) # Last argument 0 to deactivate check on block generation.
		block_list = []
		for p in pointer_list:
			block_list.append(Block(p))
		return block_list

	def update_butterfly(self,butterfly_param):
		update_butterfly_(self.impl,butterfly_param)

	def delete_butterfly(self):
		delete_butterfly_(self.impl)
							     
	def split_butterfly(self):
		pointer_list = split_butterfly_(self.impl)
		block_list = []
		for p in pointer_list:
			block_list.append(Block(p))
		return block_list
	
	def split_and_merge_butterfly(self):
		split_and_merge_butterfly_(self.impl)	

	def smooth_butterfly(self, smoothing_steps, multigrid, expansion_ratio):
		smooth_butterfly_(self.impl, smoothing_steps, multigrid, expansion_ratio)

	def create_butterfly_from_scratch(self,butterfly_param):
		create_butterfly_from_scratch_(self.impl,butterfly_param)

	def get_butterfly_parameters(self):
		return get_butterfly_parameters_(self.impl)

	def refine_block(self, refi, refj, refk):
		Block_refine_(self.impl,refi,refj,refk)

	def create_internal_face(self,dir,val):
                return Face(create_internal_face_(self.impl,dir,val))

	def delete_internal_face(self,face):
		f = _cast_face(face)
                f.delete()

	def num_internal_faces(self):
                return Block_num_internal_faces(self.impl)

        def internal_face(self,i):
                return Face(Block_internal_face(self.impl,i-1))

        def vertex_corner(self,i):
                return Vertex(Block_get_corner_vertex(self.impl,i-1))

##        def extrude_face(self,face,X,Y,Z):
##                Block_extrude_face(self.impl,face.impl,(X,Y,Z))

	def check_generation(self):
                return check_block_generation_(self.impl,2)

        def linear_2_bnd(self):
                Block_linear(self.impl,2)

        def linear_4_bnd(self):
                Block_linear(self.impl,4)

        def linear_6_bnd(self):
                Block_linear(self.impl,6)

	def smooth_3d(self,num_int):
                Block_smooth3D_(self.impl,num_int)

        def set_name(self,name):
                Block_set_name(self.impl,name)

        def get_name(self):
                return Block_get_name(self.impl)

        def get_family_name(self):
		return Block_get_family_name_(self.impl)		
	def set_family_name(self,name):
		Block_set_family_name_(self.impl,name)

	def save_cell_volumes(self,file_name = ""):
                return Block_save_cell_volumes(self.impl,file_name)

	def get_volume(self):
                return Block_get_volume(self.impl)

	# Saving the coords of the block. First specify coarse levels before RangeIJK
	# coarse levels start form 0 (finest level)

	def save_coords(self,file_name,cI,cJ,cK,r = 0):

		if r == 0: r = self.get_range()	#take full face range [1..
		Block_save_coords(self.impl,file_name,cI,cJ,cK,r.imin,r.jmin,r.kmin,
				  r.imax,r.jmax,r.kmax)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

	def show_face_grid(self):
		show_hide_face_grid_("block",1,self.impl)

	def hide_face_grid(self):
		show_hide_face_grid_("block",0,self.impl)

	def show_face_shade(self):
		show_hide_face_shade_("block",1,self.impl)

	def hide_face_shade(self):
		show_hide_face_shade_("block",0,self.impl)

	def show_edges(self):
		show_hide_edges_("block",1,self.impl)

	def hide_edges(self):
		show_hide_edges_("block",0,self.impl)

	#
	# Block movement
	#
        def on_point(self,vertex,p):
              Block_move(self.impl,vertex.impl,"PT",p.x,p.y,p.z)

	def on_curve(self,vertex,curve,npar):
	      c = get_curve_object(curve)
	      
	      # place the vertex
              Block_move(self.impl,vertex.impl,"CURV",c.impl,npar)

        def on_curve_normalized(self,vertex,curve,npar):
	      c = get_curve_object(curve)

	      # caculate absolute value of parameter
              p = c.calc_absolute(npar)
	      
	      # place the vertex
              Block_move(self.impl,vertex.impl,"CURV",c.impl,p)

        def on_surf(self,vertex,surf,u,v):
	      s = get_surf_object(surf)

	      # place the vertex
              Block_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

        def on_surf_normalized(self,vertex,surf,nu,nv):
	      s   = get_surf_object(surf)
	      u,v = Surf_absolute(s.impl,nu,nv)
	      # place the vertex
              Block_move(self.impl,vertex.impl,"SURF",s.impl,u,v)

        def on_cci(self,vertex,c1,c2):
	      # place the vertex
              Block_move(self.impl,vertex.impl,"CCI",get_curve_object(c1).impl,get_curve_object(c2).impl)

#------------------------------------------------------------------------------------------------
#					class BlockGroup
#------------------------------------------------------------------------------------------------

class BlockGroup:
	def __init__(self,pointer):
		if type(pointer) is types.StringType:			# group name
			self.impl = BlockGroup_get_group_(pointer)
		else: self.impl = pointer

	def add_block(self,block):
		 BlockGroup_add_(self.impl,get_block_ptr_(block))

	def remove_block(self,block):
		 BlockGroup_remove_(self.impl,get_block_ptr_(block))

        def delete(self):         
	    BlockGroup_delete_(self.impl)
            self.impl = 0

#------------------------------------------------------------------------------------------------

def create_block_group(name):
		 return BlockGroup(BlockGroup_create_(name))

#------------------------------------------------------------------------------------------------

def block_group(G):
	if type(G) is types.StringType:
		return BlockGroup(BlockGroup_get_group_(G))
	else:   return BlockGroup(G)

#------------------------------------------------------------------------------------------------
#Define a repetition for all groups at once

def set_repetition_all_blocks(type,num_repet,*args):
    if type == "NONE":
        Block_set_repet_(0,type,0)
    elif type == "ROTATION":
        orig = args[0]
        vec  = args[1]

        num_passage = 1
        if len(args) == 3:
            num_passage = args[2]
        Block_set_repet_(0,type,num_repet,orig.x,orig.y,orig.z,vec.x,vec.y,vec.z,num_passage)
    elif type == "TRANSLATION":
        vec  = args[0]
        Block_set_repet_(0,type,num_repet,vec.x,vec.y,vec.z)
    elif type == "MIRROR":
        orig = args[0]
        vec  = args[1]
        Block_set_repet_(0,type,num_repet,orig.x,orig.y,orig.z,vec.x,vec.y,vec.z)

#------------------------------------------------------------------------------------------------
#					Distribution Copy
#------------------------------------------------------------------------------------------------

def copy_distrib(fro,to,dir = "SAME"):
	if   isinstance(fro,Segment) & isinstance(to,Segment):
		Distrib_copy_("SEGMENT",fro.impl,to.impl,dir)
	elif isinstance(fro,Edge) & isinstance(to,Edge):
		Distrib_copy_("EDGE",fro.impl,to.impl)
	elif isinstance(fro,Face) & isinstance(to,Face):
		Distrib_copy_("FACE",fro.impl,to.impl)
	elif isinstance(fro,Block) & isinstance(to,Block):
		Distrib_copy_("BLOCK",fro.impl,to.impl)


#------------------------------------------------------------------------------------------------

class SegmentGroup:
	def __init__(self,pointer):
		self.impl = pointer

	def add_segment(self,seg):
		 SegmentGroup_add_seg_(self.impl,seg.impl)

	def remove_segment(self,seg):
		 SegmentGroup_remove_seg_(self.impl,seg.impl)

	def get_segment_list(self):
		seg_list = SegmentGroup_get_seg_list_(self.impl)
		final_list = []
		for seg in seg_list:
			final_list.append(Segment(seg))
		return final_list	

	def delete(self):         
		SegmentGroup_delete_(self.impl)
		self.impl = 0

	def smoother_bc(self,type,cell_width=0,exp=1,ncell=1):
		SegmentGroup_set_smoother_bc_(self.impl,type,[cell_width,exp,ncell])

	def apply_continuous_distrib(self,start_spacing=0,end_spacing=0):
		SegmentGroup_apply_continuous_distrib_(self.impl,start_spacing,end_spacing)

def create_segment_group(name):
		 return SegmentGroup(SegmentGroup_create_(name))

def segment_group(G):
	if type(G) is types.StringType:
		return SegmentGroup(SegmentGroup_get_group_(G))
	else:   return SegmentGroup(G)
	
#------------------------------------------------------------------------------------------------

class ClusteringGroup:
	def __init__(self,pointer):
		self.impl = pointer

	def add_segment(self,seg,orient):
		 ClusteringGroup_add_seg_(self.impl,seg.impl,orient)

	def remove_segment(self,seg):
		 ClusteringGroup_remove_seg_(self.impl,seg.impl)

	def reverse_segment_orient(self,seg):
		 ClusteringGroup_reverse_seg_(self.impl,seg.impl)

	def get_segment_list(self):
		seg_list = ClusteringGroup_get_seg_list_(self.impl)
		final_list = []
		for seg in seg_list:
			final_list.append(Segment(seg))
		return final_list	

	def delete(self):         
		ClusteringGroup_delete_(self.impl)
		self.impl = 0

	def cluster_start(self,dist):
		Set_distribution(self.impl,0,"START",dist)
		
	def cluster_end(self,dist):
		Set_distribution(self.impl,0,"END",dist)

	def cluster_both_ends(self,dist):
		Set_distribution(self.impl,0,'START_END',dist)

	def cluster_both_ends2(self,sDist,eDist,nCstCell):
		Set_distribution(self.impl,0,'START_END2',sDist,eDist,nCstCell)

	def cluster_bound_layer(self,spaceS,spaceE,thickS,thickE,nCellS,nCellE):
		Set_distribution(self.impl,0,'BOUND_LAYER',spaceS,nCellS,thickS,spaceE,nCellE,thickE)

	def cluster_tanh(self,sDist,eDist):
		Set_distribution(self.impl,0,'TANH',sDist,eDist)

	def cluster_uniform(self):
		Set_distribution(self.impl,0,'UNIFORM')

	def cluster_curvature(self,ratio,weight):
		Set_distribution(self.impl,0,'CURVAT',ratio,weight)

def create_clustering_group(name):
		 return ClusteringGroup(ClusteringGroup_create_(name))

def clustering_group(G):
	if type(G) is types.StringType:
		return ClusteringGroup(ClusteringGroup_get_group_(G))
	else:   return ClusteringGroup(G)

#------------------------------------------------------------------------------------------------

class FaceGroup:
	def __init__(self,pointer):
		self.impl = pointer

	def add_face(self,face):
		 FaceGroup_add_face_(self.impl,face.impl)

	def remove_face(self,face):
		 FaceGroup_remove_face_(self.impl,face.impl)

	def get_face_list(self):
		face_list = FaceGroup_get_face_list_(self.impl)
		final_list = []
		for faceobj in face_list:
			final_list.append(Face(faceobj))
		return final_list	

	def planar_smoothing(self, smoothing_steps=100):
		multigrid = 0
		FaceGroup_smooth_(self.impl, smoothing_steps, multigrid)

	def delete(self):         
		FaceGroup_delete_(self.impl)
		self.impl = 0

def create_face_group(name):
		 return FaceGroup(FaceGroup_create_(name))

def face_group(G):
	if type(G) is types.StringType:
		return FaceGroup(FaceGroup_get_group_(G))
	else:   return FaceGroup(G)

#------------------------------------------------------------------------------------------------
#				         Connections
#------------------------------------------------------------------------------------------------
# Dynamically connect two edges.
# edge1, edge2:  edges to connect (class Edge)
# connect_what:  specify the level of connection. It can be: "VERTEX", "ORPHAN","EDGES", "SEGMENTS"
# tol:		 is absolute tolerance and is optional

def connect_edges(edge1,edge2,connect_what,tol = 1e-5):
	connect_edges_(edge1.impl,edge2.impl,connect_what,tol)
	
#------------------------------------------------------------------------------------------------
# Dynamically connect two faces.
# face1, face2:  faces to connect (class Face)
# connect_what:  specify the level of connection. It can be: "VERTEX", "ORPHAN","EDGES",
#		 "SEGMENTS", "PATCHES" or "ALL"
# tol:		 is absolute tolerance and is optional

def connect_faces(face1,face2,connect_what,tol = 1e-5):
	connect_faces_(face1.impl,face2.impl,connect_what,tol)
	
#------------------------------------------------------------------------------------------------
# Dynamically connect the whole grid
# connect_what:  specify the level of connection. It can be: "VERTEX", "ORPHAN","EDGES",
#		 "SEGMENTS", "PATCHES" or "ALL"
# tol:		 is absolute tolerance and is optional

def connect_whole_grid(connect_what,tol = 1e-5,face_index = -1):
	connect_whole_grid_(connect_what,tol,face_index)

#------------------------------------------------------------------------------------------------
# project_transform_2D_ allows to create 3D mesh for 2D project. It has no action on 3D projects.
def search_connections(tol = 1e-5):
	project_transform_2D_(10)
	search_connections_(tol)
	
#------------------------------------------------------------------------------------------------
#					FNMB Connections
#------------------------------------------------------------------------------------------------

def create_fnmb(name,left_patches,right_patches,is_periodic,
		max_proj_dist=1e+6,min_proj_dist=1e+6,
		n_smooth_normals=20,triangulated_side=0,attraction_tol=1e-4,projection_type=1,search_type=1):
	leftp  = []
	rightp = []
	for patch in left_patches:  leftp .append(patch.impl)
	for patch in right_patches: rightp.append(patch.impl)
	
	create_fnmb_(name,leftp,rightp,is_periodic,max_proj_dist,min_proj_dist,n_smooth_normals,
		     triangulated_side,attraction_tol,projection_type,search_type)

def delete_fnmb(name):
	
	delete_fnmb_(name)

def set_fnmb_parameters(name, param_name, param_value):
	set_fnmb_parameters_(name, param_name, param_value)

def compute_fnmb(name, grid_level):
	return compute_fnmb_(name, grid_level)

def compute_all_fnmbs():
	return compute_all_fnmbs_()

def get_fnmb_list():
        final_fnmb_list = []
        fnmb_list = get_fnmb_list_()
        for fnmb in fnmb_list:
                final_fnmb = []
                final_fnmb.append(fnmb[0])
                left_patch_pointers = fnmb[1]
                right_patch_pointers = fnmb[2]
                left_patch_objects = []
                right_patch_objects = []
                for p in left_patch_pointers: left_patch_objects.append(Patch(p))
                for p in right_patch_pointers: right_patch_objects.append(Patch(p))
                final_fnmb.append(left_patch_objects)
                final_fnmb.append(right_patch_objects)
                for arg in range(3,len(fnmb)): final_fnmb.append(fnmb[arg])
                final_fnmb_list.append(final_fnmb)
	return final_fnmb_list

#------------------------------------------------------------------------------------------------
#					Rotor Stator Connections
#------------------------------------------------------------------------------------------------

def create_bc_rotor_stator(name,left_patches,right_patches):
	leftp  = []
	rightp = []
	for patch in left_patches:  leftp .append(patch.impl)
	for patch in right_patches: rightp.append(patch.impl)
	create_rotor_stator_(name,leftp,rightp)

def delete_bc_rotor_stator(name):
	delete_rotor_stator_(name)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def regenerate_faces(faces):
	if isinstance(faces,Face):
		regenerate_faces_("FACE",faces.impl)
	elif isinstance(faces,Block):
		regenerate_faces_("BLOCK",faces.impl)
	elif isinstance(faces,BlockGroup):
		regenerate_faces_("BLOCK_GROUP",faces.impl)
	elif type(faces) is types.ListType:		
		all_args = []
		for faceobj in faces:
			if isinstance(faceobj,Face):
				all_args.append( ("FACE",faceobj.impl) )
			else: raise ValueError,"Wrong arg to regenerate_faces"
		regenerate_faces_("FACES",all_args)
##	elif type(faces) is types.StringType:
##		try:
##			BlockGroup_get_group_(faces)
##			regenerate_faces_("BLOCK_GROUP",faces)
##		except: pass
	else: raise ValueError,"Wrong arg to regenerate_faces"

def regenerate_all_block_faces():
		regenerate_faces_("ALL_BLOCKS")

def smooth_plane_face_list(faces, smoothing_steps=100, multigrid=0):
	face_list = []
	if isinstance(faces,Face): faces.append(faces.impl)
	elif type(faces) is types.ListType:		
		for faceobj in faces:
			if isinstance(faceobj,Face):
				face_list.append(faceobj.impl)
			else: raise ValueError,"Wrong arg to smooth_plane_face_list"
	else: raise ValueError,"Wrong arg to smooth_plane_face_list"
	
	smooth_plane_face_list_(face_list, smoothing_steps, multigrid)

#------------------------------------------------------------------------------------------------

def set_project_configuration(sdim,axis):
	if   sdim == "2D":     dim = 2
	elif sdim == "3D":     dim = 3
	elif sdim == "AXISYM": dim = 4
	else: raise ValueError,'Wrong dimension'
	
	set_project_configuration_(dim,axis)

#------------------------------------------------------------------------------------------------

def set_2D_project_translation(doubleValue):

	set_2D_project_translation_(doubleValue)

#------------------------------------------------------------------------------------------------

def get_2D_project_translation():

	return get_2D_project_translation_()

#------------------------------------------------------------------------------------------------
#
# Usage:
#	1: new_block()	: creates a block at default position
#	2: new_block(p1,p2,p3,p4,p5,p6,p7,p8) where pi is a kind of Point

def new_block(*args):
      if len(args) == 0 :
	  p1,p2,p3,p4,p5,p6,p7,p8 = Point(0,0,0),Point(1,0,0),Point(0,1,0),Point(1,1,0),\
				    Point(0,0,1),Point(1,0,1),Point(0,1,1),Point(1,1,1)
      else:
	  p1,p2,p3,p4,p5,p6,p7,p8 = args

      return Block(Block_create_H_(
	      format_point(p1),format_point(p2),format_point(p3),format_point(p4),
	      format_point(p5),format_point(p6),format_point(p7),format_point(p8)))


#------------------------------------------------------------------------------------------------
#
# Usage:
#	1: new_block_face()	: creates a block at default position
#	2: new_block_face(p1,p2,p3,p4) where pi is a kind of Point

def new_block_face(p1=Point(0,0,0), p2=Point(1,0,0), p3=Point(0,1,0), p4=Point(1,1,0),
		   direction=2, index=0, block_size=0, a5_user_def=0):

	return Face(Face_create_H_(format_point(p1),format_point(p2),format_point(p3),format_point(p4),
				   direction, index, block_size, a5_user_def))

#------------------------------------------------------------------------------------------------

def extrude_new_block(face,r,magn,dir_mode,dir = 0,connect_topology = 1):
	tdir = dir
	if dir==0:
		if dir_mode==2: raise "extrude_new_block with dir_mode=2 expects a direction"
		tdir = Vector(0,0,1)
	return Block(extrude_new_block_(face.impl,r.imin,r.imax,r.jmin,r.jmax,
					magn,dir_mode,tdir.x,tdir.y,tdir.z,0,connect_topology))

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def block_by_face_extrusion(face,vec,edge_create,geom_create,surfaces = 0):
	if surfaces==0: surfsp = []
	else:		surfsp = collect_surf_pointers_(surfaces)

	Block_extrude_face_(face.impl,(vec.x,vec.y,vec.z),edge_create,geom_create,surfsp)

#------------------------------------------------------------------------------------------------

def block_by_face_extrusion_comb(face,vec,type,orig,angle,scale,edge_create,geom_create,surfaces = 0):
	if surfaces==0: surfsp = []
	else:		surfsp = collect_surf_pointers_(surfaces)

	Block_extrude_face_comb_(face.impl,(vec.x,vec.y,vec.z),type,(orig.x,orig.y,orig.z),
				 angle,scale,edge_create,geom_create,surfsp)

#------------------------------------------------------------------------------------------------

def block_by_face_extrusion_normal(face,magn,edge_create,geom_create,surfaces = 0):
	if surfaces==0: surfsp = []
	else:		surfsp = collect_surf_pointers_(surfaces)

	Block_inflate_face_(face.impl,magn,edge_create,geom_create,surfsp)

#------------------------------------------------------------------------------------------------

def block_by_face_extrusion_radial(face,orig,vec,magn,edge_create,geom_create,surfaces = 0):
	if surfaces==0: surfsp = []
	else:		surfsp = collect_surf_pointers_(surfaces)

	Block_radial_extrude_face_(face.impl,(orig.x,orig.y,orig.z),(vec.x,vec.y,vec.z),magn,edge_create,geom_create,surfsp)

#------------------------------------------------------------------------------------------------
# axis can be "X", "Y" or "Z"
def block_by_face_rotation(face,axis,angle,edge_create,geom_create,surface = 0):
	surfp = 0
	if surface!=0: surfp = get_surf_pointer(surface)

	Block_rotate_face_(face.impl,axis,angle,edge_create,geom_create,surfp)

#------------------------------------------------------------------------------------------------
def block_by_face_sweep(face,point_list,angle=0.0,scale_factor=1.0):
    formatted_point_list = []
    for i in range(len(point_list)):
        formatted_point_list.append(format_point(point_list[i]))

    Block_sweep_face_(face.impl,len(point_list),formatted_point_list,angle,scale_factor)

#------------------------------------------------------------------------------------------------
def blocks_merge(face, topology_merging=1):

	results = Blocks_merge_(face.impl,topology_merging)
	print results[1]

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def duplicate_blocks(blocks,transform,num_duplications,orig,vec,angle,topo_create,snap_vertex):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)
	  
	duplicate_blocks_(len(blocks),blockp,transform,num_duplications,
			  orig.x,orig.y,orig.z,vec.x,vec.y,vec.z,angle,topo_create,snap_vertex)

#------------------------------------------------------------------------------------------------

def duplicate_blocks_translate(blocks,num_duplications,vec,topo_create = 0,snap_vertex = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	duplicate_blocks_(len(blocks),blockp,1,num_duplications,
			  0.,0.,0.,vec.x,vec.y,vec.z,1.,topo_create,snap_vertex)

#------------------------------------------------------------------------------------------------

def duplicate_blocks_rotate(blocks,num_duplications,orig,vec,angle,topo_create = 0,snap_vertex = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	duplicate_blocks_(len(blocks),blockp,2,num_duplications,
			  orig.x,orig.y,orig.z,vec.x,vec.y,vec.z,angle,topo_create,snap_vertex)

#------------------------------------------------------------------------------------------------

def duplicate_blocks_scale(blocks,num_duplications,scale_vec,topo_create = 0,snap_vertex = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	duplicate_blocks_(len(blocks),blockp,4,num_duplications,
			  0.,0.,0.,scale_vec.x,scale_vec.y,scale_vec.z,1.,topo_create,snap_vertex)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def transform_blocks_translate(blocks,vec,geom_create = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	transform_blocks_(len(blocks),blockp,1,
			  0.,0.,0.,vec.x,vec.y,vec.z,1.,geom_create)

#------------------------------------------------------------------------------------------------

def transform_blocks_rotate(blocks,orig,vec,angle,geom_create = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	transform_blocks_(len(blocks),blockp,2,
			  orig.x,orig.y,orig.z,vec.x,vec.y,vec.z,angle,geom_create)

#------------------------------------------------------------------------------------------------

def transform_blocks_scale(blocks,scale_vec,geom_create = 0):
	if type(blocks) != types.ListType:
		raise "duplicate_blocks wrong first arg"
	#
	# Gather block pointers
	blockp = []
	for i in range(len(blocks)):
		blockp.append(block(blocks[i]).impl)

	transform_blocks_(len(blocks),blockp,4,
			  0.,0.,0.,scale_vec.x,scale_vec.y,scale_vec.z,1.,geom_create)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def num_of_blocks():
	return num_of_blocks_(0)

#------------------------------------------------------------------------------------------------

def block(B):				# indices from 1
	if type(B) is types.StringType:		# assuming name of block is given
		return Block(get_block_by_name_(B))
	elif isinstance(B,Block):
		return B
	else:   return Block(get_block_(B))	# assuming index [1.. is passed

#------------------------------------------------------------------------------------------------
# Access function for vertex, fixed_point, segment, edge, patch, face and block
#

def fixed_point(B,F,E,I):		# [1..
	block_index = _get_block_index(B)
	return FixedPoint(Edge_fixed_point_(edge(block_index,F,E).impl,I-1))

def vertex(B,F,E,V):
	block_index = _get_block_index(B)
	return Vertex(Edge_vertex(getEdge(block_index,F,E),V-1))

def segment(B,F,E,S):
	block_index = _get_block_index(B)
        return Segment(getSegment(block_index,F,E,S))

def edge (B,F,E):			# indices from 1
	block_index = _get_block_index(B)
        return Edge(getEdge(block_index,F,E))

def patch (B,F,P):				# indices from 1
	block_index = _get_block_index(B)
        return Patch(get_patch_(block_index,F,P))

def face (B,F):				# indices from 1
	block_index = _get_block_index(B)
        return Face(getFace(block_index,F))

def getActiveFace():
	T = getActiveTopology()
	return face(T[0],T[1])

def _get_block_index(B):
	if type(B) is types.StringType:		# assuming name of block is given
		block_pointer = get_block_by_name_(B)
		return Block_get_index_(block_pointer)
	elif isinstance(B,Block): return Block_get_index_(B.impl)
	else:			  return B	# assuming index was given, simly return it

#------------------------------------------------------------------------------------------------
#				Quality check functions 
#------------------------------------------------------------------------------------------------

def calc_mesh_quality(type,block,axis,range_start,range_end,range_number):
	if type != "Orthogonality" and type != "Aspect Ratio" and type != "Expansion Ratio"\
	       and type != "Cell width" and type != "Angular deviation":
		raise ValueError,'Check quality: wrong criterion'
	if axis != "All" and axis != "I" and axis != "J" and axis != "K":
		raise ValueError,'Check quality: wrong axis'

	block_pointer = 0
	generated = 1
	if block == 0:
		for i in range(num_of_blocks()):
			if generated == 1: generated = check_block_generation_(i+1,2)
	else:
		block_pointer = block.impl
		block_number = Block_get_index_(block_pointer)

		generated = check_block_generation_(block_number,2)

	if not generated: raise ValueError,'Check quality: block needs regeneration'

	initialize_quality_grid_and_subwindow_()
	return calc_mesh_quality_(type,[block_pointer,0,0,"Surface",axis,range_start,range_end,range_number,0])

def get_extremum_quality_values():
	return get_extremum_quality_values_()

def get_statistic_quality_values():
	return get_statistic_quality_values_()

def calc_mesh_quality_inter_block(type,block,range_start,range_end,range_number):
	if type != "Orthogonality" and type != "Angular deviation"\
	and type != "Expansion Ratio" and type != "Cell width" and type != "Cell width at wall":
		raise ValueError,'Check quality inter block: wrong criterion'

	block_pointer = 0
	generated = 1
	if block == 0:
		for i in range(num_of_blocks()):
			if generated == 1: generated = check_block_generation_(i+1,2)
	else:
		block_pointer = block.impl
		block_number = Block_get_index_(block_pointer)

		generated = check_block_generation_(block_number,2)

	if not generated: raise ValueError,'Check quality: block needs regeneration'

	initialize_quality_grid_and_subwindow_()
	return calc_mesh_quality_inter_block_(type,[block_pointer,0,0,range_start,range_end,range_number,0])

def calc_patch_mesh_quality(type,patch,range_start,range_end,range_number):
	if type != "Orthogonality" and type != "Angular deviation"\
	and type != "Expansion Ratio" and type != "Cell width":
		raise ValueError,'Check quality inter block: wrong criterion'

	generated = 1
	patch_pointer = patch.impl

	initialize_quality_grid_and_subwindow_()
	return calc_patch_mesh_quality_(type,[patch_pointer,0,0,range_start,range_end,range_number,0])

def get_extremum_quality_values_inter_block():
	return get_extremum_quality_values_inter_block_()

def calc_mesh_quality_fnmb(type,fnmb_name,range_start,range_end,range_number):
	if type != "Expansion Ratio" and type != "Cell Width Ratio"\
	and type != "Inner Gap" and  type != "Relative Inner Gap":
		raise ValueError,'Check quality fnmb: wrong criterion'

	generated = check_fnmb_generation_(fnmb_name)
	if not generated: raise ValueError,'Check quality: fnmb needs recomputing'

	initialize_quality_grid_and_subwindow_()
	return calc_mesh_quality_fnmb_([type,1,[fnmb_name],0,0,range_start,range_end,range_number,-1,0])

def get_extremum_quality_values_fnmb():
	return get_extremum_quality_values_fnmb_()

def hide_quality():
	set_quality_colormap_(0,"",0,0)
	hide_quality_()

def calc_negative_cells(block,precision,right_handed,levels,cI,cJ,cK):
	if precision != "single" and precision != "double":
		raise ValueError,'Check negative cells: wrong precision'
	
	block_pointer = 0
	generated = 1
	if block == 0:
		for i in range(num_of_blocks()):
			if generated == 1: generated = check_block_generation_(i+1,2)
	else:
		block_pointer = block.impl
		block_number = Block_get_index_(block_pointer)
		generated = check_block_generation_(block_number,2)

	if not generated: raise ValueError,'Check negative cells: block needs regeneration'
	
	return calc_neg_cells_(block_pointer,precision,right_handed,levels,cI,cJ,cK)

def text_message_box(message):
	text_message_box_(message)

def set_text_message_box_height(height_value):
	text_message_box_height_(height_value)

def text_message_box_title(message):
	text_message_box_title_(message)

def export_plot3D(file_name, parameters_list, block_list=[]):
	if len(block_list) == 0:
		export_plot3D_(file_name, parameters_list)
	else:
		if type(block_list) != types.ListType:
			raise "export_plot3D wrong last arg"
		#
		# Gather block pointers
		blockp = []
		for i in range(len(block_list)):
			blockp.append(block(block_list[i]).impl)
		export_plot3D_(file_name, parameters_list, blockp)

# kept for backward : export all blocks without merging
def export_CEDRE(fileName):
    export_CEDRE_(fileName, 3, 0, "", 0, "")

def export_CEDRE_all_blocks(fileName, merging = 1, mergedBlockName = ""):
    export_CEDRE_(fileName, 3, merging, mergedBlockName)
def export_CEDRE_block_group(fileName, groupName, merging = 1, mergedBlockName = ""):
    export_CEDRE_(fileName, 2, merging, mergedBlockName, groupName)
def export_CEDRE_block_list(fileName, blockList, merging = 1, mergedBlockName = ""):
    numBlocks = len(blockList)
    # Gather block pointers
    blockp = []
    for i in range(len(blockList)):
        blockp.append(block(blockList[i]).impl)
    export_CEDRE_(fileName, 1, merging, mergedBlockName, numBlocks, blockp)

def export_FLUENT(file_name):
	export_FLUENT_(file_name)
def export_CFDpp(file_name):
    export_CFDpp_(file_name)
def export_CRUNCH_CFD(file_name):
    export_CRUNCH_CFD_(file_name)
def export_HYDRA(file_name):
    export_HYDRA_(file_name)
def export_OpenFOAM(directory_name, branch="official"):
    if not isinstance(branch, str):
        branch = "official"
    precision = 12
    #if not isinstance(precision, int) or precision <= 0:
    #    precision = 12
    export_OpenFoam_(directory_name, branch, precision)
def export_Abaqus(file_name,element_type="C3D8"):
    if not isinstance(element_type, str):
        element_type = "C3D8"
    export_Abaqus_(element_type,file_name)

#------------------------------------------------------------------------------------------------
#				Viewing functions 
#------------------------------------------------------------------------------------------------

def zoomFromAt(centerx1,centery1,centerz1,centerx2,centery2,centerz2,zoom1,zoomstep,nstep):
	vx = centerx2-centerx1
	vy = centery2-centery1
	vx = vx/nstep
	vy = vy/nstep
	zoom = zoom1
	centerx = centerx1
	centery = centery1
	centerz = centerz1
	for i in range(1,nstep):
		zoom = zoom+zoomstep
		centerx = centerx+vx
		centery = centery+vy
		centerz = centerz
		zoom_at(centerx,centery,centerz,zoom)
	return zoom

def igg_setCameraTargetZoom(centerx2,centery2,centerz2,nstep,zoom):
	P  = igg_get_camera_target()
	centerx1 = P[0]
	centery1 = P[1]
	centerz1 = P[2]
	vx = centerx2-centerx1
	vy = centery2-centery1
	vz = centerz2-centerz1
	vx = vx/nstep
	vy = vy/nstep
	vz = vz/nstep
	centerx = centerx1
	centery = centery1
	centerz = centerz1
	for i in range(0,nstep):
		centerx = centerx+vx
		centery = centery+vy
		centerz = centerz+vz
		igg_camera_target_zoom(centerx,centery,centerz,zoom)

def show_block_list(list,grid,shade,edge=0):
	for b in list:
		if grid==1:
			show_block_grid(b.impl)
		if shade==1:
			show_block_shade(b.impl)
		if edge==1:
			show_block_edge(b.impl)
def show_block_list_solid_patches(list,grid,shade):
	for b in list:
		if grid==1:
			show_block_grid_solid_patches(b.impl)
		if shade==1:
			show_block_shade_solid_patches(b.impl)
def hide_block_list_solid_patches(list,grid,shade):
	for b in list:
		if grid==1:
			hide_block_grid_solid_patches(b.impl)
		if shade==1:
			hide_block_shade_solid_patches(b.impl)
def hide_block_list(list,grid,shade,edge=0):
	for b in list:
		if grid==1:
			hide_block_grid (b.impl)
		if shade==1:
			hide_block_shade(b.impl)
		if edge==1:
			hide_block_edge (b.impl)
def show_face_list(list,grid,shade):
	for b in list:
		if grid==1:
			show_face_grid(b.impl)
		if shade==1:
			show_face_shade(b.impl)
def hide_face_list(list,grid,shade):
	for b in list:
		if grid==1:
			hide_face_grid(b.impl)
		if shade==1:
			hide_face_shade(b.impl)

def show_block_surface_grid(block_index, IJK_direction, IJK_index):
	showSurfGrid_(block_index-1, IJK_direction, IJK_index)

def clear_block_surface_grid():
	clearSurfGrid_()

def hide_block_surface_grid():
	hideSurfGrid_()

#------------------------------------------------------------------------------------------------
#				Private functions 
#------------------------------------------------------------------------------------------------

def _cast_face(face):
	f = 0
	if isinstance(face,Face): f = face
	else:                     raise typeError,'Wrong Face specification'
	return f

#------------------------------------------------------------------------------------------------
#		Geometry commands using Grid information (cannot go in Geom.py)
#------------------------------------------------------------------------------------------------

def create_surface_from_face(face,root_name="emptyName",rename_bnd_curve=0,surface_order=2):
	if not isinstance(face,Face): raise TypeError,"Not a Face object"
	
	return Surface(create_surf_from_face_(face.impl,root_name,rename_bnd_curve,surface_order))

# both following function are not interfaced
def create_surface_from_faces(faces):
	if type(faces) is types.ListType:
			for i in range(len(faces)):
				create_surf_from_face_(faces[i].impl)
	else: create_surf_from_face_(face.impl)

def create_surface_from_patch_with_extension(patch, ext1, ext2):
	if not isinstance(patch,Patch): raise TypeError,"Not a Patch object"
	
	return Surface(create_surf_from_patch_with_extend_(patch.impl, ext1, ext2))

#------------------------------------------------------------------------------------------------
# Viewing commands
import PythonViewing
def set_camera_position(pos,target,up,width,heigth):
	PythonViewing._set_camera_position((pos.x,pos.y,pos.z),(target.x,target.y,target.z),(up.x,up.y,up.z),width,heigth)

#------------------------------------------------------------------------------------------------

def get_clustering_info(length,computeVariable,distributionType,*args):
    # Python implementation of clustering info tool

    if   computeVariable == "STRETCHING_RATIO" or computeVariable == "START_SPACING" or computeVariable == "END_SPACING":
        requiredLength = 1
    elif computeVariable == "NUMBER_OF_POINTS":
        requiredLength = 2
    else:
        raise ValueError("invalid variable name in get_clustering_info")

    if   distributionType == "START" or distributionType == "END" or distributionType == "START_END":
        requiredLength += 1
    elif distributionType == "START_END2":
        requiredLength += 3
    elif distributionType == "TANH":
        requiredLength += 2
    else:
        raise ValueError("invalid distribution type in get_clustering_info")

    if len(args) != requiredLength:
        raise ValueError("number of arguments in get_clustering_info is wrong: %r given, %r required" % (len(args),requiredLength) )

    pos = 0
    if   computeVariable == "STRETCHING_RATIO":
        nPoints        = args[pos]
        stretching     = 0.
        mgLevel        = 0
    elif computeVariable == "NUMBER_OF_POINTS":
        nPoints        = 0
        stretching     = args[pos]
        pos           += 1
        mgLevel        = args[pos]
    elif computeVariable == "START_SPACING" or computeVariable == "END_SPACING":
        nPoints        = args[pos]
        pos           += 1
        stretching     = args[pos]
        mgLevel        = 0
    pos += 1

    if computeVariable == "STRETCHING_RATIO" or computeVariable == "NUMBER_OF_POINTS":
        spacing1       = args[pos]
        pos           += 1
        if distributionType == "START_END2" or distributionType == "TANH":
            spacing2   = args[pos]
            pos       += 1
        else:
            spacing2 = 0.
    elif computeVariable == "START_SPACING" and distributionType == "TANH":
        spacing1       = 0.
        spacing2       = args[pos]
        pos           += 1
    elif computeVariable == "END_SPACING" and distributionType == "TANH":
        spacing1       = args[pos]
        pos           += 1
        spacing2       = 0.
    else:
        spacing1 = 0.
        spacing2 = 0.

    if distributionType == "START_END2":
        noConstantCells = args[pos]
    else:
        noConstantCells = 0

    return get_clustering_info_([length,stretching,nPoints,mgLevel,computeVariable,distributionType,spacing1,spacing2,noConstantCells])

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                    class Distribution
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Distribution:
    def __init__(self,inputdata):
        if isinstance(inputdata, list):
            self.impl     = inputdata
            self.nopoints = len(inputdata)
        elif isinstance(inputdata, int):
            self.nopoints = inputdata
            self.impl     = [float(i)/float(self.nopoints-1) for i in range(0, self.nopoints)]
        else:
            raise ValueError("Wrong argument type")
        if self.nopoints < 2: raise ValueError("Distribution without data points")
        # check that data is monotone
        for i in range(self.nopoints-1):
            if self.impl[i+1] <= self.impl[i]: raise ValueError("Arc length distribution not monotone")

    def __getitem__(self,index):
        if index > self.nopoints: raise ValueError("Index too large " % (index,self.nopoints) )
        return self.impl[index]

    def __len__(self):
        if len(self.impl) != self.nopoints: raise ValueError("Array dimension mismatch " % (len(self.impl),self.nopoints) )
        return self.nopoints

#-----------------------
# distribution types (copied from DistribInfo):
# 0 : START
# 1 : END
# 2 : START_END
# 3 : START_END_CST_CELLS
# 6 : UNIFORM
# 8 : TANH

    def cluster_start(self,dist):
        newArcLength = setDistribution_(self.nopoints,self.impl,0,dist)
        self.impl = newArcLength

    def cluster_end(self,dist):
        newArcLength = setDistribution_(self.nopoints,self.impl,1,dist)
        self.impl = newArcLength

    def cluster_both_ends(self,dist):
        newArcLength = setDistribution_(self.nopoints,self.impl,2,dist)
        self.impl = newArcLength

    def cluster_both_ends2(self,sDist,eDist,nCstCell):
        newArcLength = setDistribution_(self.nopoints,self.impl,3,sDist,eDist,nCstCell)
        self.impl = newArcLength

    def cluster_uniform(self):
        newArcLength = setDistribution_(self.nopoints,self.impl,6)
        self.impl = newArcLength

    def cluster_tanh(self,sDist,eDist):
        newArcLength = setDistribution_(self.nopoints,self.impl,8,sDist,eDist)
        self.impl = newArcLength

    def normalize(self):
        newArcLength = normalizeDistribution_(self.nopoints,self.impl)
        self.impl = newArcLength

    def set_length(self,length):
        newArcLength = setDistributionLength_(self.nopoints,self.impl,length)
        if len(newArcLength) != self.nopoints: raise ValueError("Array dimension mismatch " % (len(newArcLength),self.nopoints) )
        self.impl = newArcLength
