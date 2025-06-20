#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         M.P.                                                           Jan 2001            #
#--------------------------------------------------------------------------------------------#

import sys,types,re,fnmatch

from math     import *
from Grid     import *
from Geometry import *
from Project  import *

import Session

#--------------------------------------------------------------------------------------------#

class Point:
    def __init__(self,a,b,c,i=-1):
        self.x    = a
        self.y    = b
        self.z    = c
        self.i    = i
    def __add__(self,right):
        return Point(self.x+right.x,self.y+right.y,self.z+right.z)
    def __sub__(self,right):
        return Point(self.x-right.x,self.y-right.y,self.z-right.z)
    def __div__(self,d):
        return Point(self.x/d,self.y/d,self.z/d)
    def __mul__(self,d):
        return Point(self.x*d,self.y*d,self.z*d)
    def __rmul__(self,d):
        return Point(self.x*d,self.y*d,self.z*d)
    def __neg__(self):
        return Point(-self.x,-self.y,-self.z)
    def __repr__(self):
        return "(%f, %f, %f)" % (self.x, self.y, self.z)
    def __str__(self):
        return "(%f, %f, %f)" % (self.x, self.y, self.z)
    def norm(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def normalize(self):
        d = self.norm()
        if d < 1e-12: return
        self.x = self.x/d
        self.y = self.y/d
        self.z = self.z/d
    def get_perpendicular_dir(self):
        if abs(self.x)>1e-8 or abs(self.y)>1e-8: return Point(-self.y,self.x,0)
        return Point(-self.z,0,self.x)
    def rotate(self, line, angle):
        if not isinstance(line,Line): return
        angle = angle*pi/180
        plane = Plane(self,line.v);
        p = intersect_line_plane(line,plane)
        v1 = self - p;
        r  = sqrt(scalarProduct(v1,v1));
        if r < 1e-12: return self
        v1.normalize();
        v2 = crossProduct(line.v, v1)
        v2.normalize();
        line1 = Line(p,v1);
        p1 = line1.p + line1.v*r*cos(angle)
        line2 = Line(p1,v2);
        p2 = line2.p + line2.v*r*sin(angle)
        return p2

#------------------------------------------------------------------------------------------------

class Vector(Point):
	def __init__(self,a,b,c):
		Point.__init__(self,a,b,c)

#------------------------------------------------------------------------------------------------

def radial_distance(point,origin=Point(0.,0.,0.),axis=Point(0.,0.,1.)):
    return radial_distance_(point.x,point.y,point.z,origin.x,origin.y,origin.z,axis.x,axis.y,axis.z)

#--------------------------------------------------------------------------------------------#
# Line defined by a Point (p) and a Vector (v). v is supposed to be normalized
#
class Line:
	def __init__(self,p,v):
		if isinstance(p,Plane) and isinstance(v,Plane):
			direction = crossProduct(p.normal, v.normal)
			direction.normalize()
			self.v = direction
			line2 = Line(p.point, p.normal.get_perpendicular_dir())
			self.p = intersect_line_plane(line2, v)
		else:
			self.p = p
			self.v = v
	def get_point_at_param(self,t):
		return self.p + self.v*t

#--------------------------------------------------------------------------------------------#

class Plane:
	def __init__(self,pt,norm):
		self.normal = norm
		self.point  = pt

#--------------------------------------------------------------------------------------------#

class PlanePPP(Plane):
	def __init__(self,p1,p2,p3):
		
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		Plane.__init__(self,p1,crossProduct(p2-p1,p3-p1))
	
#--------------------------------------------------------------------------------------------#

def scalarProduct(p1,p2):
	return p1.x*p2.x + p1.y*p2.y + p1.z*p2.z

#--------------------------------------------------------------------------------------------#

def distance(p1,p2):
	dx = p2.x-p1.x
	dy = p2.y-p1.y
	dz = p2.z-p1.z
	return sqrt(abs(dx*dx+dy*dy+dz*dz))

#--------------------------------------------------------------------------------------------#

def crossProduct(p1,p2):
	x = p1.y*p2.z-p1.z*p2.y
	y = p1.z*p2.x-p1.x*p2.z
	z = p1.x*p2.y-p1.y*p2.x
	return Point(x,y,z)

#--------------------------------------------------------------------------------------------#

def intersect_line_plane(line,plane):
	d   = scalarProduct(plane.point ,plane.normal)
	div = scalarProduct(plane.normal,line.v)

	if(div==0):  div = 1e-8
	t = (d-(scalarProduct(plane.normal,line.p)))/div

	return line.get_point_at_param(t)
	
#--------------------------------------------------------------------------------------------#

class CartesianPoint(Point):
	def __init__(self,*arg):
		if len(arg) == 3:
			x,y,z = arg[0],arg[1],arg[2]
			self.impl = cartesian_point_(x,y,z)
		elif len(arg) == 1:
			pt = arg[0]
			if (type(pt) is types.TupleType) | (type(pt) is types.ListType):
				x,y,z = pt[0],pt[1],pt[2]
				self.impl = cartesian_point_(x,y,z)
			elif isinstance(pt,Point):
				x,y,z = pt.x,pt.y,pt.z
				self.impl = cartesian_point_(x,y,z)
			else:
				self.impl = pt
				x,y,z = GeomPoint_get_coords_(pt)
		else:
			raise ValueError,"Wrong number of arguments for GeometryPoint"
        
		Point.__init__(self,x,y,z)	# Base class initialization

	def delete(self):         
		delete_cartesian_point_(self.impl)
		self.impl = 0

#--------------------------------------------------------------------------------------------#

def extract_point_(*arg):
    x,y,z = 0,0,0
    if len(arg) == 3:
        x,y,z = arg[0],arg[1],arg[2]
    elif len(arg) == 1:
        pt = arg[0]
        if (type(pt) is types.TupleType) | (type(pt) is types.ListType):
            x,y,z = pt[0],pt[1],pt[2]
        elif isinstance(pt,Point):
            return pt
    return Point(x,y,z)
    
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------

class Curve:
    def __init__(self,curve):
        if type(curve) is types.StringType:
            self.impl = _get_curve_by_name(curve)
        elif isinstance(curve,Curve): self.impl = curve.impl
        else:	self.impl = curve
    def __eq__(self,curve):
        if isinstance(curve,Curve): return self.impl == curve.impl
        else: return self.impl == curve

    def set_discretisation(self,n)   : set_curve_discretization(n,self)

    def num_ctr_pnt (self)           : return Curve_numCtrPnt  (self.impl)
    def get_ctr_pnt (self,i)         :
        list = Curve_ctrPnt(self.impl,i)
        return Point(list[0],list[1],list[2])
    def get_control_point (self,i)         :
        list = Curve_ctrPnt(self.impl,i-1)
        return Point(list[0],list[1],list[2])
    def first_ctr_pnt(self)     :    return self.get_ctr_pnt(0)
    def last_ctr_pnt(self)      :
                        numPt = Curve_numCtrPnt(self.impl)
                        return self.get_ctr_pnt(numPt-1)

##	def getTangent	(self,i)	:	return Curve_tangent    (self.impl,i)

    def get_box     (self)    : return Box(Curve_get_box(self.impl))
    def get_length  (self)    : return Curve_get_properties(self.impl)[0]
    def get_p_min   (self)    : return Curve_getMinParam(self.impl)
    def get_p_max   (self)    : return Curve_getMaxParam(self.impl)
    def delta_p     (self)    : return Curve_getMaxParam(self.impl)-Curve_getMinParam(self.impl)
	
    def get_tangent (self,param)	:
        list = Curve_get_tangent(self.impl,param)
        return Point(list[0],list[1],list[2])

    def calc_point   (self,param):
        list = Curve_get_point(self.impl,param)
        return Point(list[0],list[1],list[2])

    def start_point(self):
        return CurvePointNorm(self, 0)

    def end_point(self):
        return CurvePointNorm(self, 1)

    def project_point(self,p):
        abs_param = Curve_project_point_(self.impl,(p.x,p.y,p.z))
        return abs_param

    def project_on_surface(self,surf,normal):
        c = Curve_project_on_surf_(self.impl, surf.impl, (normal.x,normal.y,normal.z));
        clist = []
        for curve in c: clist.append(Curve(curve))
        return clist

	# return the absolute value of the normalized parameter value
	#
    def calc_absolute(self,param):
        if param<0 or param>1:
            raise ValueError, 'Parameter not normalized: %s' % param
        return Curve_absolute(self.impl,param)

    def calc_normalize(self, abs_param):
        return Curve_normalize(self.impl,abs_param)

    def select  (self)      :    Curve_select_         (self.impl)
    def unselect(self)      :    Curve_unselect_       (self.impl)
    def set_name(self,n)    :    Curve_set_name_       (self.impl,n)
    def get_name(self)      :    return Curve_get_name_(self.impl)

    def intersectPlane(self,p)	:
        p1 = p.point
        p2 = p.normal
        return  Curve_intersectPlane(self.impl,(p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z))
    def save    (self)          :    Curve_save     (self.impl)
    def printa  (self)          :    Curve_print    (self.impl)
    def split   (self,param)    :
        c1,c2 = Curve_split(self.impl,param)
        return Curve(c1),Curve(c2)

    def show    (self)    :    showCurve(self.impl)
    def hide    (self)    :    hideCurve(self.impl)

    def add_point(self,p):
        Curve_add_point(self.impl,format_point(p))
		
    def insert_point(self,index,p):
        Curve_add_point(self.impl,format_point(p),index-1)
		
    def remove_point(self,index):
        Curve_remove_point(self.impl,index-1)
		
    def move_point(self,index,p,regen_dependent_egdes = 0):
        Curve_move_point(self.impl,index-1,format_point(p),regen_dependent_egdes)

    def reverse(self, revert_param = 0):
        Curve_reverse(self.impl,revert_param)

    def delete(self):
        delete_curves_(self.impl)
        self.impl = 0

    def distribute_points(self,distribution):
        coordinates = Curve_distribute_points(self.impl,distribution.nopoints,distribution.impl)
        points = []
        for i in range(0, len(coordinates)):
            points.append(Point(coordinates[i][0],coordinates[i][1],coordinates[i][2]))
        return points

#------------------------------------------------------------------------------------------------

class CurvePoint(Point):
	def __init__(self,curve,p,i=-1):
	      c = 0
	      if isinstance(curve,Curve): c = curve
	      else:                       c = _get_curve_by_name(curve)
	      self.c    = c
	      self.p    = p
	      t         = c.calc_point(p)
	      Point.__init__(self,t.x,t.y,t.z,i)

#------------------------------------------------------------------------------------------------
# Point at curve-curve intersection

class CCPoint(Point):
	def __init__(self,cu1,cu2):
	      c1 = 0
	      c2 = 0
	      if isinstance(cu1,Curve): c1 = cu1
	      else:                     c1 = Curve(_get_curve_by_name(cu1))
	      if isinstance(cu2,Curve): c2 = cu2
	      else:                     c2 = Curve(_get_curve_by_name(cu2))

	      self.c1   = c1
	      self.c2   = c2

#------------------------------------------------------------------------------------------------
# Point on Curve at normalized parameter
#
class CurvePointNorm(Point):
	def __init__(self,curve,p,i=-1):
	      c = 0
	      if isinstance(curve,Curve): c = curve
	      else:                       c = Curve(_get_curve_by_name(curve))

	      self.c    = c
	      self.p    = c.calc_absolute(p)
	      t         = c.calc_point   (self.p)
	      Point.__init__(self,t.x,t.y,t.z,i)

#--------------------------------------------------------------------------------------------#
# Examples:
#	curve_plane_intersection(Point,Vector,curve_list)
#	curve_plane_intersection(Plane,curve_list)

def curve_plane_intersection(p1,p2,*list):

	curves = collect_curves_pointers_(list)
	
	if isinstance(p1,Plane):
		origin = p1.point
		normal = p1.normal
		curv = get_curve_pointer(p2)
		curves.append(curv)
	else:
		if not (isinstance(p1,Point) | isinstance(p2,Point)):
			raise ValueError,"Wrong curve plane intersection args"
		else:
			origin = p1
			normal = p2
	plist = curv_plane_inters_(curves,(origin.x,origin.y,origin.z),
				   (normal.x,normal.y,normal.z))
	points = []
	for pt in plist:
		points.append(CartesianPoint(pt))
	return points

#--------------------------------------------------------------------------------------------#

def curve_surface_intersection(surface,*list):

	curves = collect_curves_pointers_(list)
	
	plist = curv_surface_inters_(get_surf_object(surface).impl, curves)
	points = []
	for pt in plist:
		points.append(CartesianPoint(pt))
	return points

#--------------------------------------------------------------------------------------------#
# curve_curve_intersection("curve_1","curve_2",...)
# set clist = ["curve_1","curve_2",...]
# curve_curve_intersection(clist)

def curve_curve_intersection(*list):
	curvs = []
	extract_curves_(list,curvs)
	plist = curv_curv_inters_(curvs)
	points = []
	for pt in plist:
		points.append(CartesianPoint(pt))
	return points

#--------------------------------------------------------------------------------------------#

def intersect_curves(cu1,cu2):
              c1 = get_curve_object(cu1)
              c2 = get_curve_object(cu2)
	      return curve_curve_intersect([c1.impl,c2.impl])

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				global construction utilities
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# Construct a polyline in IGG repository. Possible calls are:
# new_polyline()			: empty polyline - auto naming
# new_polyline(p1,...pi)		: polyline with specified points. Auto naming
# new_polyline("name",p1,..pi)		: polyline with specified name and points

def new_polyline( *args ):
	sindex = 0
	name   = ""
	if len(args) > 0:
		if type(args[0]) is types.StringType:
			name = Session.get_context_name(args[0])
			sindex = 1
	# create the cpline (1) in IGG
	curve = Curve(new_curve_(3,name))

	for i in range(sindex,len(args)):
		if isinstance(args[i],Point): curve.add_point(args[i])
		else:
			raise 'Wrong point argument'
	return curve

#------------------------------------------------------------------------------------------------
# Construct a polyline in IGG repository. Possible calls are:
# new_polyline()			: empty polyline - auto naming
# new_polyline(p1,...pi)		: polyline with specified points. Auto naming
# new_polyline("name",p1,..pi)		: polyline with specified name and points

def new_parametric_polyline( *args ):
	sindex = 0
	name   = ""
	if len(args) > 0:
		if type(args[0]) is types.StringType:
			name = Session.get_context_name(args[0])
			sindex = 1
	# create the cpline (1) in IGG
	curve = Curve(new_curve_(-8,name))

	for i in range(sindex,len(args)):
		if isinstance(args[i],Point): curve.add_point(args[i])
		else:
			raise 'Wrong point argument'
	return curve

#------------------------------------------------------------------------------------------------

def new_cspline( *args ):
	sindex = 0
	name   = ""
	if len(args) > 0:
		if type(args[0]) is types.StringType:
			name = Session.get_context_name(args[0])
			sindex = 1
	# create the cpline (1) in IGG
	curve = Curve(new_curve_(1,name))

	for i in range(sindex,len(args)):
		if isinstance(args[i],Point): curve.add_point(args[i])
		else:
			raise 'Wrong point argument'
	return curve

#------------------------------------------------------------------------------------------------

def new_bspline( *args ):
	sindex = 0
	name   = ""
	if len(args) > 0:
		if type(args[0]) is types.StringType:
			name = Session.get_context_name(args[0])
			sindex = 1
	# create the bpline (2) in IGG
	curve = Curve(new_curve_(2,name))

	for i in range(sindex,len(args)):
		if isinstance(args[i],Point): curve.add_point(args[i])
		else:
			raise 'Wrong point argument'
	return curve

#------------------------------------------------------------------------------------------------
# Construct a polyline in IGG repository. Possible calls are:
# new_cspline()			: empty polyline - auto naming
# new_cspline(p1,...pi)		: polyline with specified points. Auto naming
# new_cspline("name",p1,..pi)	: polyline with specified name and points

def new_curve_impl(type, args ):
	sindex = 0
	name   = ""
	if len(args) > 0:
		if type(args[0]) is types.StringType:
			name = Session.get_context_name(args[0])
			sindex = 1
	# create the polyline (3) in IGG
	curve = Curve(new_curve_(type,name))

	for i in range(sindex,len(args)):
		if isinstance(args[i],Point): curve.add_point(args[i])
		else:
			raise 'Wrong point argument'
	return curve

#------------------------------------------------------------------------------------------------

def create_arc_ppp(p1,p2,p3,name = ""):
	if name != "": name = Session.get_context_name(name)
	return Curve(arc_ppp_((p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z),(p3.x,p3.y,p3.z),name))

#------------------------------------------------------------------------------------------------

def create_circle_ppp(p1,p2,p3,name = ""):
	if name != "": name = Session.get_context_name(name)
	return Curve(circle_ppp_((p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z),(p3.x,p3.y,p3.z),name))

#------------------------------------------------------------------------------------------------

def create_arc_cnpp(orig,normal,startP,endP,name=""):
	if name != "": name = Session.get_context_name(name)
	return Curve(arc_cnpp_((orig.x,orig.y,orig.z),(normal.x,normal.y,normal.z),
			       (startP.x,startP.y,startP.z),(endP.x,endP.y,endP.z),name))

#------------------------------------------------------------------------------------------------

def create_arc_nppr(normal,p1,p2,radius,sense,name=""):
	if name != "": name = Session.get_context_name(name)
	return Curve(arc_nppr_((normal.x,normal.y,normal.z),(p1.x,p1.y,p1.z),
			       (p2.x,p2.y,p2.z),radius,sense,name))

#------------------------------------------------------------------------------------------------
#old procedure only for backward compatibility do not use it anymore !!

def create_arc(normal,orig,startP,endP,name=""):
	if name != "": name = Session.get_context_name(name)
	return Curve(arc_cnpp_((orig.x,orig.y,orig.z),(normal.x,normal.y,normal.z),
			    (startP.x,startP.y,startP.z),(endP.x,endP.y,endP.z),name))

#------------------------------------------------------------------------------------------------

def create_circle_ncr(normal,orig,radius,name=""):
	if name != "": name = Session.get_context_name(name)
	return Curve(circle_ncr_((normal.x,normal.y,normal.z),(orig.x,orig.y,orig.z),
				 radius,name))

#------------------------------------------------------------------------------------------------

def delete_curves(*args):
	curves = []
	extract_curves_(args,curves)

##	for i in range(len(args)):
##		curve = args[i]
		
##		try: c = get_curve_pointer(curve)
##		except: pass
##		else:   curves.append(c)
	delete_curves_(curves)

#------------------------------------------------------------------------------------------------

def extend_curves(start_extend,end_extend,*curves):
	curvs = []
	extract_curves_(curves,curvs)
	c = extend_curves_(curvs,start_extend,end_extend)
	clist = []
	for curve in c: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def offset_curves(normal,start_offset,*curves):
	curvs = []
	extract_curves_(curves,curvs)
	c = offset_curves_(curvs,(normal.x,normal.y,normal.z),start_offset,0)
	clist = []
	for curve in c: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def offset_curves_linear(normal,start_offset,end_offset,*curves):
	curvs = []
	extract_curves_(curves,curvs)
	c = offset_curves_(curvs,(normal.x,normal.y,normal.z),start_offset,end_offset)
	clist = []
	for curve in c: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def trim_curve(curve,param):
	c1 = get_curve_pointer(curve)
	c = trim_curve_(c1,param)
	clist = []
	for curve in c: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def set_curve_discretization(num_pts,*curves):
	curvs = []
	extract_curves_(curves,curvs)
	set_curve_discretization_(curvs,num_pts)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#					Geometry class
#------------------------------------------------------------------------------------------------
# Desc: Class referencing a Geometry repository in IGG.
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Geometry:
    def __init__(self,pointer):
        self.impl = pointer

    def add_curve(self,curve):
        Geometry_add_curve(curve)

def extract_geometry_pointer(geometry_rep):
    if isinstance(geometry_rep,Geometry):
        return geometry_rep.impl
    else:
        return geometry_rep

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#			   Private function used for internal management
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def get_all_curves(geometry_rep=0):
    geometry = extract_geometry_pointer(geometry_rep)
    curves = get_curves_(geometry)
    final_list = []
    for curve in curves: final_list.append(Curve(curve))
    return final_list

def get_all_curves_name(geometry_rep=0):
    geometry = extract_geometry_pointer(geometry_rep)
    return get_all_curve_names_(geometry)

def _get_curve_by_name(name):
	return get_curve_by_name_(0,Session.get_context_name(name))

## this function seems unused and is replaced by get_all_curves_name which conforms
## with naming convention
#def Curve_all_curves_name_(geometry_rep):
#    return get_all_curve_names_(geometry_rep)

#------------------------------------------------------------------------------------------------

def get_curve_object(cu1):
	c1 = 0
	if isinstance(cu1,Curve): c1 = cu1
	else:                     c1 = Curve(_get_curve_by_name(cu1))
	return c1

def get_curve_pointer(cu1):
	c1 = 0
	if isinstance(cu1,Curve): c1 = cu1.impl
	else:                     c1 = _get_curve_by_name(cu1)
	return c1

#--------------------------------------------------------------------------------------------#
# given a list of  curves, extract the curve pointers
# and output them in the appropriate list

def extract_curves_(item,curvs):
        if (type(item) is types.TupleType) | (type(item) is types.ListType):
		for sitem in item:
			extract_curves_(sitem,curvs)
	elif isinstance(item,Curve):
		curvs.append(item.impl)
	else:
		try:    c = _get_curve_by_name(item)
		except: raise "Wrong specified curve ",item
		else:	curvs.append(c)			
		
#-------------------------------------------------------------------------------------------
# Given a list of Curve objects or curve names (as strings) return a list of pointers
# Input can also be only one curve

def collect_curves_pointers_(item):
	plist = []
        if (type(item) is types.TupleType) | (type(item) is types.ListType):
		for sitem in item: plist = plist + collect_curves_pointers_(sitem)
	elif isinstance(item,Curve):
		plist.append(item.impl)
	else:
		try:    c = _get_curve_by_name(item)
		except: raise "Wrong curve name ",item
		else:	plist.append(c)
	return plist

#-------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
#					Surface class
#------------------------------------------------------------------------------------------------

class Surface:
        def __init__(self,surf):
		if type(surf) is types.StringType:
			self.impl = get_surf_by_name_(0,Session.get_context_name(surf))
		elif isinstance(surf,Surface): self.impl = surf.impl
		else:	self.impl = surf

        def get_boundary_curves(self):
		c = Surface_get_boundary_curves(self.impl)
		clist = []
		for curve in c: clist.append(Curve(curve))
		return clist
        def get_boundary_curve (self,i):	return Curve(Surface_get_boundary_curves(self.impl)[i-1])
        def get_box	       (self):		return Box(Surf_get_box(self.impl))
        def get_uv_box	       (self):		return Range(Surf_get_uv_box(self.impl))
        def set_name           (self,n):	Surf_set_name_(self.impl,n)
	def get_name		(self):		return Surf_get_name_(self.impl)
        def get_lofting_curves	(self):
		c = Surface_get_lofting_curves (self.impl)
		clist = []
		for curve in c: clist.append(Curve(curve))
		return clist
	def get_trimming_curves(self):
		c = Surface_get_trimming_curves(self.impl)
		clist = []
		for curve in c: clist.append(Curve(curve))
		return clist
        def split               (self,dir,val): return Surface_split(self.impl,dir,val)
	def split_by_surface	(self,surf,root_name=""):
		surf_impl = 0
		if type(surf) is types.StringType:
			surf_impl = get_surf_by_name_(0,Session.get_context_name(surf))
		elif isinstance(surf,Surface): surf_impl = surf.impl
		else:	surf_impl = surf
		s = surface_surface_split_(self.impl, surf_impl, root_name)
		slist = []
		for surface in s: slist.append(Surface(surface))
		return slist
	def split_by_plane	(self,plane_spec,root_name=""):
		return surfaces_plane_split(self,plane_spec,root_name)
		
	# Add u cst or v cst curve according to absolute parameter
	def add_uv_curve	(self,par,dir): return Curve(Surf_add_uv_curve_(self.impl,par,dir))

	def show    (self)		:	show_surface_(self.impl)
	def hide    (self)		:	hide_surface_(self.impl)
	def select  (self)		:	Surface_select_     (self.impl)
	def unselect(self)		:	Surface_unselect_   (self.impl)
        def delete(self):         
	    Surface_delete(self.impl)
            self.impl = 0
        def save(self,fileName):         
	    surface_save(self.impl,fileName)

	# return the absolute value of the normalized (u,v) parameters
	#
	def calc_absolute(self,u,v):
#		if u<0 or u>1 or v<0 or v>1:
#		    raise ValueError, 'Parameter not normalized: %f %f' % (u,v)
		return Surf_absolute(self.impl,u,v)

	def calc_point(self,u,v):
            list = Surf_get_point(self.impl,u,v)
            return Point(list[0],list[1],list[2])

        def calc_normal(self,u,v):
            list = Surf_get_normal(self.impl,u,v)
            return Vector(list[0],list[1],list[2])

	def project_point(self,p):
		return Surf_project_point_(self.impl,(p.x,p.y,p.z))

#------------------------------------------------------------------------------------------------
# Point on Surface at normalized (u,v) parameters
#

class SurfPointNorm(Point):
	def __init__(self,surf,u,v):
	      s = 0
	      if isinstance(surf,Surface): s = surf
	      else:			   s = Surface(get_surf_by_name_(0,Session.get_context_name(surf)))
	      
	      self.s        = s
	      self.u,self.v = s.calc_absolute(u,v)
	      t             = s.calc_point   (self.u,self.v)
	      Point.__init__(self,t.x,t.y,t.z)

class SurfPointAbs(SurfPointNorm):
	def __init__(self,surf,u,v):
	      s = 0
	      if isinstance(surf,Surface): s = surf
	      else:			   s = Surface(get_surf_by_name_(0,Session.get_context_name(surf)))
	      
	      self.s = s
	      self.u = u
	      self.v = v
	      t             = s.calc_point   (self.u,self.v)
	      Point.__init__(self,t.x,t.y,t.z)

#------------------------------------------------------------------------------------------------
##	# intersect the surface with a plane, given as argument
##        # arg is one of :
##	#	- Plane
##	#	- CurvePoint	i.e. CurvePoint("a_curve",0.4)
	
##	def intersect_plane(self,arg):
##		if isinstance(arg,Plane):
##			p = arg.point
##			n = arg.norm
##			surf_plane_intersect_([self.impl],("PLANE",p.x,p.y,p.z,
##							   n.x,n.y,n.z ))
##		else:
##			try:    p = format_point(arg)
##			except: raise "Wrong argument to Surface.plane_intersect"
##			surf_plane_intersect_([self.impl],p)

#------------------------------------------------------------------------------------------------
##	# intersect the surface with another surface, given as argument
##        # arg is one of :
##	#	- Surface
##	#	- String (surface name)
	
##	def intersect_surf(self,surf,root_name=""):
##		    return surf_surf_intersection(self,surf,root_name)


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#				Surface utilities
#------------------------------------------------------------------------------------------------
# public
def get_all_surfaces(geometry_rep=0):
    geometry = extract_geometry_pointer(geometry_rep)
    surfaces = get_surfaces_(geometry)
    final_list = []
    for surf in surfaces: final_list.append(Surface(surf))
    return final_list

def get_all_surfaces_name(geometry_rep=0):
    geometry = extract_geometry_pointer(geometry_rep)
    return get_all_surface_names_(geometry)

def delete_surfaces(*args):
	curves = []
	surfaces = []
	extract_curves_surfs_(args,curves,surfaces)

##	for i in range(len(args)):
##		surface = args[i]
		
##		try: s = get_surf_pointer(surface)
##		except: pass
##		else:   surfaces.append(s)
	delete_surfaces_(surfaces)

def Surface_delete(surface_pointer):
	delete_surfaces_(surface_pointer)

#------------------------------------------------------------------------------------------------

def surf_surf_intersection(s1,s2,root_name = ""):	# return list of Curve
        c = surf_surf_intersect_(get_surf_object(s1).impl,get_surf_object(s2).impl,root_name)
	clist = []
	for curve in c: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

##def surf_plane_intersection(s1,plane_spec,name = ""):
##	if isinstance(plane_spec,Plane):
##		p  = plane_spec.point
##		n  = plane_spec.norm
##		cl = surf_plane_intersect_([self.impl],("PLANE",p.x,p.y,p.z,
##							       n.x,n.y,n.z ),name)
##	else:
##		try:    p = format_point(plane_spec)
##		except: raise "Wrong argument to Surface.plane_intersect"
##		cl = surf_plane_intersect_([self.impl],p,name)
##	clist = []
##	for curve in cl: clist.append(Curve(c))
##	return clist
		
##        c = surf_plane_intersect_(get_surf_object(s1).impl,get_surf_object(s2).impl)
##	clist = []
##	for curve in c: clist.append(Curve(curve))
##	return clist

#------------------------------------------------------------------------------------------------
# Intersect one surface by a Plane. See next function for a descritpion of the args

def surface_intersect_plane(s1,plane_spec,name = ""):
	return surfaces_intersect_plane([s1],plane_spec,name)

#------------------------------------------------------------------------------------------------
#Intersect a list of surfaces by a Plane. The plane is defined in one of the following ways:
#
# surfaces_intersect_plane(surf_list,p1,p2,p3,name = "")
# surfaces_intersect_plane(surf_list,plane,name = "")
# surfaces_intersect_plane(surf_list,curvepoint,name = "")
#
def surfaces_intersect_plane(slist,*args):
	plist = collect_surf_pointers_(slist)
	name = ""
	if isinstance(args[0],Plane):
		# Extract point & normal
		p  = args[0].point
		n  = args[0].normal

		# If a second arg is passed it is interpreted as the name:
		try: name = args[1]
		except: pass
		
		cl = surf_plane_intersect_(plist,("PLANE",p.x,p.y,p.z,
							  n.x,n.y,n.z ),name)
	elif isinstance(args[0],PlanePPP):

		p1 = format_point(args[0].p1)
		p2 = format_point(args[0].p2)
		p3 = format_point(args[0].p3)

		# If a second arg is passed it is interpreted as the name:
		try: name = args[1]
		except: pass

		cl = surf_plane_intersect_(plist,("PLANE_PPP",p1,p2,p3),name)
		
	elif isinstance(args[0],CurvePoint) or isinstance(args[0],CurvePointNorm):
##		if len(args) >= 3:
##			print "3POINTS"
##			p0 = format_point(args[0])
##			p1 = format_point(args[1])
##			p2 = format_point(args[2])
##			try: name = args[3]
##			except: pass
##			cl = surf_plane_intersect_(plist,("PLANE_PPP",p0,p1,p2),name)
##		elif len(args) <=2:
			curvep = format_point(args[0])

			try: name = args[1]
			except: pass
			cl = surf_plane_intersect_(plist,curvep,name)
	else:
		raise "Wrong args for surfaces_intersect_plane"
	#
	# Collect the result of intersection and return Curve objects
	clist = []
	for curve in cl: clist.append(Curve(curve))
	return clist

def surfaces_intersect_plane2(slist,plane_spec,name = ""):
	plist = collect_surf_pointers_(slist)

	cl = []
	if isinstance(plane_spec,Plane):
		p  = plane_spec.point
		n  = plane_spec.normal
		cl = surf_plane_intersect_(plist,("PLANE",p.x,p.y,p.z,
							  n.x,n.y,n.z ),name)
	else:
		try:    p = format_point(plane_spec)
		except: raise "Wrong argument to surfaces_intersect_plane"
		cl = surf_plane_intersect_(plist,p,name)
	#
	# Collect the result of intersection and return Curve objects
	clist = []
	for curve in cl: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def surface_intersect_plane_ppp(s1,plane_spec,name = ""):
	return surfaces_intersect_plane_ppp([s1],plane_spec,name)

#------------------------------------------------------------------------------------------------

def surfaces_intersect_plane_ppp(slist,plane,name = ""):
	name = Session.get_context_name(name)
	plist = collect_surf_pointers_(slist)

	if isinstance(plane,PlanePPP):
		p1  = format_point(plane.p1)
		p2  = format_point(plane.p2)
		p3  = format_point(plane.p3)
		cl = surf_plane_ppp_intersect_(plist,("PLANE_PPP",p1,p2,p3),name)
	else:
		raise "Wrong argument to surfaces_intersect_plane_ppp"
	#
	# Collect the result of intersection and return Curve objects
	clist = []
	for curve in cl: clist.append(Curve(curve))
	return clist

#------------------------------------------------------------------------------------------------

def surfaces_plane_split(slist,plane_spec,root_name = ""):
	plist = collect_surf_pointers_(slist)
	sl = []

	if isinstance(plane_spec,Plane):
		p  = plane_spec.point
		n  = plane_spec.normal		
		sl = surfaces_plane_split_(plist,("PLANE",p.x,p.y,p.z,n.x,n.y,n.z ),root_name)
	elif isinstance(plane_spec,PlanePPP):
		p1 = format_point(plane_spec.p1)
		p2 = format_point(plane_spec.p2)
		p3 = format_point(plane_spec.p3)
		sl = surfaces_plane_split_(plist,("PLANE_PPP",p1,p2,p3),root_name)		
	elif isinstance(plane_spec,CurvePoint) or isinstance(plane_spec,CurvePointNorm):
		curvep = format_point(plane_spec)
		sl = surfaces_plane_split_(plist,curvep,root_name)
	else:
		raise "Wrong args for surface_plane_split_"
	slist = []
	for surface in sl: slist.append(Surface(surface))
	return slist

#------------------------------------------------------------------------------------------------

def extract_underlying_surfaces(slist):
	plist = collect_surf_pointers_(slist)
	extract_underlying_surfaces_(0,plist)

#------------------------------------------------------------------------------------------------

def surface_revolution(curves,orig,axis,angle, name = ""):
	name = Session.get_context_name(name)
	surfs = surface_revol_(collect_curves_pointers_(curves),
			       [orig.x,orig.y,orig.z],[axis.x,axis.y,axis.z],angle,name)
	if len(surfs) == 1: return Surface(surfs[0])
	else:
		slist = []
		for surf in surfs: slist.append(Surface(surf))
		return slist

#------------------------------------------------------------------------------------------------

def lofted_surface(curves,name = "emptyName",rename_bnd_curve=0):
#	name = Session.get_context_name(name)
       	surf = lofted_surf_(collect_curves_pointers_(curves),name,rename_bnd_curve)
	if surf == 0: raise "Could not create lofted surface"
	else: return Surface(surf)

#------------------------------------------------------------------------------------------------

def coons_surface(curve1,curve2,curve3,curve4,root_name="emptyName",rename_bnd_curve=0):
	surf = create_coons_surf_(get_curve_pointer(curve1),get_curve_pointer(curve2),
				  get_curve_pointer(curve3),get_curve_pointer(curve4),root_name,rename_bnd_curve)
	if surf == 0: raise "Could not create coons surface"
	else: return Surface(surf)

#------------------------------------------------------------------------------------------------

def linear_sweep_surface(curve1,curve2,root_name="emptyName",rename_bnd_curve=0):
	surf = create_linear_sweep_surf_(get_curve_pointer(curve1),get_curve_pointer(curve2),root_name,rename_bnd_curve)
	if surf == 0: raise "Could not create linear sweep surface"
	else: return Surface(surf)

#------------------------------------------------------------------------------------------------

def offset_surface(surface,offset_dist,root_name="emptyName",rename_bnd_curve=0):
	surfs = collect_surf_pointers_(surface)
       	surf = offset_surface_(surfs[0],offset_dist,root_name,rename_bnd_curve)
	if surf == 0: raise "Could not create offset surface"
	else: return Surface(surf)

#------------------------------------------------------------------------------------------------

def surfaces_set_representation(surfaces,n1,n2):
	plist = collect_surf_pointers_(surfaces)

	surf = surfs_set_represent_(plist,n1,n2)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#			   Private function used for internal management
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def get_surface(name):			# return a Surface object from a name
        return Surface(get_surf_by_name_(0,name))

#------------------------------------------------------------------------------------------------

def get_surf_pointer(surf):
	s1 = 0
	if isinstance(surf,Surface): s1 = surf.impl
	else:                        s1 = get_surf_by_name_(0,surf)
	return s1

#------------------------------------------------------------------------------------------------
#private
def get_surf_object(surf):		# return a Surface object a Surface object or a name
	s = 0
	if isinstance(surf,Surface): s = surf
	else:                        s = Surface(get_surf_by_name_(0,surf))
	return s

#-------------------------------------------------------------------------------------------
# Given a list of Surface objects -or- surface names (as strings) return a list of pointers
# Input can also be one surface

def collect_surf_pointers_(slist):
	plist = []
	if type(slist) is types.ListType :		
		for i in range(len(slist)):
			plist.append(get_surf_object(slist[i]).impl)
	else:		plist.append(get_surf_object(slist).impl)
	return plist

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Box:
	def __init__(self,lim):
		self.xmin = lim[0]
		self.xmax = lim[1]
		self.ymin = lim[2]
		self.ymax = lim[3]
		self.zmin = lim[4]
		self.zmax = lim[5]

	def get_min_size(self):
		dx = abs(self.xmax-self.xmin)
		dy = abs(self.ymax-self.ymin)
		dz = abs(self.zmax-self.zmin)
		if dx<dy : side,len,min,max = 'X',dx,self.xmin,self.xmax
		else	 : side,len,min,max = 'Y',dy,self.ymin,self.ymax
		if dz<len: side,len,min,max = 'Z',dz,self.zmin,self.zmax
		return [side,len,min,max]
	def get_max_size(self):
		dx = abs(self.xmax-self.xmin)
		dy = abs(self.ymax-self.ymin)
		dz = abs(self.zmax-self.zmin)
		max_dist = dx
		if dy>max_dist: max_dist = dy
		if dz>max_dist: max_dist = dz
		return max_dist

	def get_min(self):
		xmin = self.xmin
		return Point(self.xmin,self.ymin,self.zmin)
	def get_max(self):
		return Point(self.xmax,self.ymax,self.zmax)
	def get_center(self):
		return Point( (self.xmax + self.xmin)/2. ,(self.ymax + self.ymin)/2. ,(self.zmax + self.zmin)/2. )

	def origin(self):
	        return Point(self.xmin,self.ymin,self.zmin)
	def dx(self):	return abs(self.xmax-self.xmin)
	def dy(self):	return abs(self.ymax-self.ymin)
	def dz(self):	return abs(self.zmax-self.zmin)

	def contains(self,item):
		if isinstance(item,Point):
			if item.x > self.xmin and item.x < self.xmax and\
			   item.y > self.ymin and item.y < self.ymax and\
			   item.z > self.zmin and item.z < self.zmax: return 1
			return 0
		elif isinstance(item,Box):
			pmin = item.get_min()
			pmax = item.get_max()

			if self.contains(pmin) and self.contains(pmax):
				return 1
			return 0
		return 0

	def inflate(self,alpha):

		center = self.get_center();

		dtx =  self.dx() / 2.
		dty =  self.dy() / 2.
		dtz =  self.dz() / 2.
		if dtx < 1e-12:
			dtx = 1e-3
		if dty < 1e-12:
			dty = 1e-3
		if dtz < 1e-12:
			dtz = 1e-3

		dtx = dtx * alpha
		dty = dty * alpha
		dtz = dtz * alpha
		
		self.xmin = center.x - dtx
		self.ymin = center.y - dty
		self.zmin = center.z - dtz
		
		self.xmax = center.x + dtx
		self.ymax = center.y + dty
		self.zmax = center.z + dtz

		return self
 
		if isinstance(item,Point):
			if item.x > self.xmin and item.x < self.xmax and\
			   item.y > self.ymin and item.y < self.ymax and\
			   item.z > self.zmin and item.z < self.zmax: return 1
			return 0
		else:
			pmin = item.get_min()
			pmax = item.get_max()

			if self.contains(pmin) and self.contains(pmax):
				return 1
			return 0
		return 0

	def __add__(self,b):
		xmin = self.xmin
		if b.xmin < xmin : xmin = b.xmin
		ymin = self.ymin
		if b.ymin < ymin : ymin = b.ymin
		zmin = self.zmin
		if b.zmin < zmin : zmin = b.zmin

		xmax = self.xmax
		if b.xmax > xmax : xmax = b.xmax
		ymax = self.ymax
		if b.ymax > ymax : ymax = b.ymax
		zmax = self.zmax
		if b.zmax > zmax : zmax = b.zmax

		return Box([xmin,xmax,ymin,ymax,zmin,zmax])

	def printo(self):
		print self.xmin,self.ymin,self.zmin,self.xmax,self.ymax,self.zmax

#------------------------------------------------------------------------------------------------

class BoxRTZ:
	def __init__(self,lim):
		self.rmin = lim[0]
		self.rmax = lim[1]
		self.tmin = lim[2]
		self.tmax = lim[3]
		self.zmin = lim[4]
		self.zmax = lim[5]

	def dr(self):	return abs(self.rmax-self.rmin)
	def dt(self):	return abs(self.tmax-self.tmin)
	def dz(self):	return abs(self.zmax-self.zmin)
	def printo(self):
		print "rmin,rmax = %f %f" % (self.rmin,self.rmax)
		print "tmin,tmax = %f %f" % (self.tmin,self.tmax)
		print "zmin,zmax = %f %f" % (self.zmin,self.zmax)

	def __add__(self,b):
		rmin = self.rmin
		if b.rmin < rmin : rmin = b.rmin
		tmin = self.tmin
		if b.tmin < tmin : tmin = b.tmin
		zmin = self.zmin
		if b.zmin < zmin : zmin = b.zmin

		rmax = self.rmax
		if b.rmax > rmax : rmax = b.rmax
		tmax = self.tmax
		if b.tmax > tmax : tmax = b.tmax
		zmax = self.zmax
		if b.zmax > zmax : zmax = b.zmax

		return BoxRTZ([rmin,rmax,tmin,tmax,zmin,zmax])

#--------------------------------------------------------------------------------------------#
# Utils.py
# given a list of mixed curves and surfaces, extract the curves and surfaces pointers
# and output them in the appropriate list

def extract_curves_surfs_(item,curvs,surfs):
	
        if (type(item) is types.TupleType) | (type(item) is types.ListType):
		for sitem in item:
			extract_curves_surfs_(sitem,curvs,surfs)
	elif isinstance(item,Curve):
		curvs.append(item.impl)
	elif isinstance(item,Surface):
		surfs.append(item.impl)
	else:
		try:    c = _get_curve_by_name(item)
		except: pass
		else:	curvs.append(c)
			
		try:	s = get_surf_by_name_(0,item)
		except: pass
		else:	surfs.append(s)
		
#--------------------------------------------------------------------------------------------#

def format_point(p):
      if isinstance(p,CurvePoint) or isinstance(p,CurvePointNorm):
	  return ( ("CURV",p.c.impl,p.p) )
      elif isinstance(p,SurfPointNorm):
	  return ( ("SURF",p.s.impl,p.u,p.v) )
      elif isinstance(p,CCPoint):
	  return ("CCI",p.c1.impl,p.c2.impl)
      elif isinstance(p,Point):
	  return ("PT",p.x,p.y,p.z)
      else:
	  raise ValueError,"format_point unkown value"

#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

def geom_duplicate(curv_list,surf_list,root_name = ""):
	curvs     = []
	surfs     = []
	for item in curv_list:
		if isinstance(item,Curve):
			curvs.append(item.impl)
		else:
			try:    c = _get_curve_by_name(item)
			except: pass
			else:	curvs.append(c)
	for item in surf_list:
		if isinstance(item,Surface):
			surfs.append(item.impl)
		else:
			try:    c = get_surf_by_name_(item)
			except: pass
			else:	surfs.append(c)

        results = Geom_duplic_(curvs,surfs,root_name)
        clist = []
        slist = []
	for curve in results[0]: clist.append(Curve(curve))
        for surf  in results[1]: slist.append(Surface(surf))
        results = []
        results.append(clist)
        results.append(slist)
        return results

#--------------------------------------------------------------------------------------------#
#old function. MUST stay for backward purpose
def geometry_duplicate(*entities):
	curvs     = []
	surfs     = []
	root_name = ""
	extract_curves_surfs_(entities,curvs,surfs)
	results = Geom_duplic_(curvs,surfs,root_name)
        clist = []
        slist = []
	for curve in results[0]: clist.append(Curve(curve))
        for surf  in results[1]: slist.append(Surface(surf))
        results = []
        results.append(clist)
        results.append(slist)
        return results

#--------------------------------------------------------------------------------------------#
# m is transform mode (1,2,3)
# s is prefix for duplicate (mode 3)
def geometry_translate(v,m,s,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_translate_(curvs,surfs,(v.x,v.y,v.z),m,s)

#--------------------------------------------------------------------------------------------#
#old function. MUST stay for backward purpose
def translate(v,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_translate_(curvs,surfs,(v.x,v.y,v.z))

#--------------------------------------------------------------------------------------------#
# angle in degrees
def geometry_rotate(o,v,angle,m,s,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_rotate_(curvs,surfs,(o.x,o.y,o.z),(v.x,v.y,v.z),angle,m,s)

#--------------------------------------------------------------------------------------------#
#old function. MUST stay for backward purpose
def rotate(o,v,angle,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_rotate_(curvs,surfs,(o.x,o.y,o.z),(v.x,v.y,v.z),angle)

#--------------------------------------------------------------------------------------------#
def geometry_scale(v,m,s,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_scale_(curvs,surfs,(v.x,v.y,v.z),m,s)

#--------------------------------------------------------------------------------------------#
#old function. MUST stay for backward purpose
def scale(v,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_scale_(curvs,surfs,(v.x,v.y,v.z))

#--------------------------------------------------------------------------------------------#
def geometry_mirror(o,v,m,s,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_mirror_(curvs,surfs,(o.x,o.y,o.z),(v.x,v.y,v.z),m,s)

#--------------------------------------------------------------------------------------------#
#old function. MUST stay for backward purpose
def mirror(o,v,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	Geom_mirror_(curvs,surfs,(o.x,o.y,o.z),(v.x,v.y,v.z))

#--------------------------------------------------------------------------------------------#

def group_curves(tol,*list):
	curvs = []
	extract_curves_(list,curvs)
	return Curve(group_curves_(curvs,tol))

#--------------------------------------------------------------------------------------------#

def ungroup_curves(*list):
	curvs = []
	extract_curves_(list,curvs)
	ungroup_curves_(curvs)

#--------------------------------------------------------------------------------------------#

def convert_to_cspline(nb_points,distrib_type,ratio,weight,*list):
	curvs = []
	extract_curves_(list,curvs)
	new_curves_pointer = convert_to_cspline_(curvs,nb_points,distrib_type,ratio,weight)
	new_curves_python = []
	for cpointer in new_curves_pointer:
	    new_curves_python.append(Curve(cpointer))
	return new_curves_python

#--------------------------------------------------------------------------------------------#

def save_geometry_entities(filename,*entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities,curvs,surfs)
	save_geometry_entities_(filename,curvs,surfs)

#--------------------------------------------------------------------------------------------#

def save_curve_ctr_points(filename,*list):
	curvs = []
	extract_curves_(list,curvs)
	save_curve_ctr_points_ (filename,curvs)

#--------------------------------------------------------------------------------------------#

def export_to_iges(filename,unit_flag):
	export_to_iges_(filename, 0, unit_flag)

#--------------------------------------------------------------------------------------------#

def export_to_parasolid(filename, *entities):
	curvs = []
	surfs = []
	extract_curves_surfs_(entities, curvs, surfs)
	export_to_parasolid_(filename, curvs, surfs)

#--------------------------------------------------------------------------------------------#

def search_list_by_pattern(name_list,pattern,glob=0,ignorecase=0):
    matches = []
    if glob:
        pattern = fnmatch.translate(pattern)
    if ignorecase:
        regex = re.compile(pattern,re.IGNORECASE|re.LOCALE)
    else:
        regex = re.compile(pattern,re.LOCALE)
    for name in name_list:
        if regex.search(name):
            matches.append(name)
    return matches

#--------------------------------------------------------------------------------------------#

def reset_geometry_counters():
    reset_geometry_counters_()

#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------#

class Range:
    #
    # Two constructors Range(0,1,0,10) or Range([0,1,0,10])
    #
    def __init__(self,*lim):
	     if len(lim) == 1:
		 lim = lim[0]
                 self.imin = lim[0]
                 self.imax = lim[1]
                 self.jmin = lim[2]
                 self.jmax = lim[3]
	     elif len(lim) == 4:
                 self.imin = lim[0]
                 self.imax = lim[1]
                 self.jmin = lim[2]
                 self.jmax = lim[3]
	     else:
		 raise "Range wrong number of arguments"
    def printo(self):
            print self.imin,self.imax,self.jmin,self.jmax

#--------------------------------------------------------------------------------------------#

class RangeIJK:
    #
    # One constructors Range(0,10, 0,10, 0,10) 
    #
    def __init__(self,*lim):
	    if len(lim) == 6:
		    self.imin = lim[0]
		    self.imax = lim[1]
		    self.jmin = lim[2]
		    self.jmax = lim[3]
		    self.kmin = lim[4]
		    self.kmax = lim[5]
	    else:
		    raise "RangeIJK wrong number of arguments"

#--------------------------------------------------------------------------------------------#
