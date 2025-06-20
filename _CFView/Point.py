#--------------------------------------------------------------------------------------------#
#                       Point.py                                                             #
#--------------------------------------------------------------------------------------------#
#      Numeca International                                                                  #
#         Etienne Robin                                                           oct 1999   #
#--------------------------------------------------------------------------------------------#
# Description : point as a set of 3 floats                                                   #
#--------------------------------------------------------------------------------------------#

from math  import *
from types import *

#--------------------------------------------------------------------------------------------#

class Point:

    # constructor and destructor
    def __init__(self, x=0., y=0., z=0.):
	if (type(x) is FloatType) | (type(x) is IntType) | (type(x) is LongType) :
	    self.x_=x
	    self.y_=y
	    self.z_=z
	elif (type(x) is ListType) | (type(x) is TupleType) :
	    l=len(x)
	    if l>0 : 
		self.x_=x[0]
	    else :
		self.x_=0.
	    if l>1 : 
		self.y_=x[1]
	    else :
		self.y_=0.
	    if l>2 : 
		self.z_=x[2]
	    else :
		self.z_=0.
	else :
	    raise ValueError, 'unexpected argument type : '+type(x)

    def __repr__(self):
	return "(%f, %f, %f)"%(self.x_, self.y_, self.z_)

    def __str__(self):
	return "(%f, %f, %f)"%(self.x_, self.y_, self.z_)

    def asTuple(self):
	return [self.x_, self.y_, self.z_]

    # numeric type emulation
    def __add__(self, q):
	if (type(q) is FloatType) | (type(q) is IntType) | (type(q) is LongType) :
	    return Point(self.x_+q,self.y_+q,self.z_+q)
	elif (type(q) is ListType) | (type(q) is TupleType) :
	    l=len(q)
	    if l>2 : 
		return Point(self.x_+q[0], self.y_+q[1], self.z_+q[2])
	    elif l>1 : 
		return Point(self.x_+q[0], self.y_+q[1], self.z_)
	    elif l>0 : 
		return Point(self.x_+q[0], self.y_, self.z_)
	elif (type(q) is InstanceType) & (q.__class__.__name__ == 'Point') :
	    return Point(self.x_+q.x_,self.y_+q.y_,self.z_+q.z_)
	else :
	    raise TypeError, 'Point operator + : unexepected operand type '+type(q)
	
    def __sub__(self, q):
	if (type(q) is FloatType) | (type(q) is IntType) | (type(q) is LongType) :
	    return Point(self.x_-q,self.y_-q,self.z_-q)
	elif (type(q) is ListType) | (type(q) is TupleType) :
	    l=len(q)
	    if l>2 : 
		return Point(self.x_-q[0], self.y_-q[1], self.z_-q[2])
	    elif l>1 : 
		return Point(self.x_-q[0], self.y_-q[1], self.z_)
	    elif l>0 : 
		return Point(self.x_-q[0], self.y_, self.z_)
	elif (type(q) is InstanceType) & (q.__class__.__name__ == 'Point') :
	    return Point(self.x_-q.x_,self.y_-q.y_,self.z_-q.z_)
	else :
	    raise TypeError, 'Point operator + : unexepected operand type '+type(q)

    def __mul__(self, q):
	if (type(q) is FloatType) | (type(q) is IntType) | (type(q) is LongType) :
	    return Point(self.x_*q,self.y_*q,self.z_*q)
	elif (type(q) is ListType) | (type(q) is TupleType) :
	    l=len(q)
	    if l>2 : 
		return Point(self.x_*q[0], self.y_*q[1], self.z_*q[2])
	    elif l>1 : 
		return Point(self.x_*q[0], self.y_*q[1], self.z_)
	    elif l>0 : 
		return Point(self.x_*q[0], self.y_, self.z_)
	elif (type(q) is InstanceType) & (q.__class__.__name__ == 'Point') :
	    return Point(self.x_*q.x_,self.y_*q.y_,self.z_*q.z_)
	else :
	    raise TypeError, 'Point operator + : unexepected operand type '+type(q)

    def __div__(self, q):
	if (type(q) is FloatType) | (type(q) is IntType) | (type(q) is LongType) :
	    return Point(self.x_/q,self.y_/q,self.z_/q)
	elif (type(q) is ListType) | (type(q) is TupleType) :
	    l=len(q)
	    if l>2 : 
		return Point(self.x_/q[0], self.y_/q[1], self.z_/q[2])
	    elif l>1 : 
		return Point(self.x_/q[0], self.y_/q[1], self.z_)
	    elif l>0 : 
		return Point(self.x_/q[0], self.y_, self.z_)
	elif (type(q) is InstanceType) & (q.__class__.__name__ == 'Point') :
	    return Point(self.x_/q.x_,self.y_/q.y_,self.z_/q.z_)
	else :
	    raise TypeError, 'Point operator + : unexepected operand type '+type(q)
 

    
#--------------------------------------------------------------------------------------------#

def norm(p):
    if p.__class__.__name__ == 'Point' :
	return sqrt(p.x_*p.x_+p.y_*p.y_+p.z_*p.z_)
    else :
	raise TypeError, 'norm : unexpected argument type '+type(p)

#--------------------------------------------------------------------------------------------#
#                       Point.py                                                             #
#--------------------------------------------------------------------------------------------#
