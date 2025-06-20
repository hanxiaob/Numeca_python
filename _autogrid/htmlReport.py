
from Grid import *
from Autogrid5_configuration import *
from Autogrid5_fileManager   import *
from Autogrid5_meridional    import *
from Autogrid5_technoEffect  import *
from Autogrid5_viewa5        import *
from Autogrid                  import *
from Autogrid5_NIQualityReport import *
import HTMLgen
import barchart
from HTMLcolors import * 

a5_lineSeparator = HTMLgen.HR()
a5_dummyLine     = HTMLgen.BR(1)
## init main page

def a5_html_report_init_header(doc):
    doc.title    = 'Autogrid mesh generation report'
    ## header
    doc.append(HTMLgen.Center(HTMLgen.Font('Autogrid mesh generation report', color=BLUE,size='+1')))
    list = NIGridQualityReport_getHeaderValue(0)
    doc.append(HTMLgen.Center(HTMLgen.Font('Version :'+list[0]+' - Compilation Date :'+list[1], color=BLUE,size='-1')))
    ## Test Case
    doc.append(HTMLgen.Center(HTMLgen.Font('Test Case: '+a5_get_project_name_(), color=BLUE,size='+3')))
    ## Generation Time
    doc.append(HTMLgen.Center(HTMLgen.Font('Last Generation Date: '+list[2], color=BLACK,size='+1')))
    ## Generation Time
    doc.append(HTMLgen.Center(HTMLgen.Font('Last Generation time: '+list[3], color=BLACK,size='+1')))
    doc.append(a5_lineSeparator)
    doc.append(a5_dummyLine)

def a5_html_report_init(save_b2bview,save_3dView):
    # init the directory used to stored the html report file and all the images
    fileprefix = a5_init_html_report_file_()
    prefix     = a5_get_project_prefix_()
    a5_html_report_create_picture(fileprefix)
    ## report file name
    reportfile = fileprefix+".html"
    reportfile = fileprefix+".html"

    ## initialize the document
    doc = HTMLgen.BasicDocument()
    a5_html_report_init_header(doc)

    ## Meridional View
    imagefile = prefix+"_zr_view.png"
    mainfileurl  = prefix+"_main.html"
    mainfile  = fileprefix+"_main.html"

    doc.append(HTMLgen.Center(HTMLgen.Href(mainfileurl,HTMLgen.Image(imagefile))))
    doc.append(a5_dummyLine)
    doc.append(HTMLgen.Center(HTMLgen.Font('Meridional View', color=BLACK,size='+1')))
    doc.append(a5_dummyLine)
    doc.append(a5_dummyLine)
    doc.append(a5_dummyLine)
    text = HTMLgen.Font('Click to Enter', color=RED,size='+3')
    doc.append(HTMLgen.Center(HTMLgen.Href(mainfileurl,text)))
    doc.write(reportfile)
    a5_html_report_init_global_page(mainfile,fileprefix,prefix,save_b2bview,save_3dView)
    
## init global page
def a5_html_report_init_global_page(file,fileprefix,prefix,save_b2bview,save_3dView):
    doc = HTMLgen.BasicDocument()
    a5_html_report_init_header(doc)
    a5_html_report_init_global_table  (doc,fileprefix,prefix,save_b2bview,save_3dView)
    row_list = []
    if save_3dView == 1:
	a5_html_report_init_global_picture_table(doc,fileprefix,prefix,row_list)
    doc.write(file)	

## init global table
def a5_html_report_init_global_table(doc,fileprefix,prefix,save_b2bview,save_3dView):
    table = HTMLgen.Table('Global Parameters')
    heading = ['Quality Field','Number of Pts','Neg. Cells','Min. Skewness','Max. Asp. Ratio',
               'Max. Exp. Ratio','Min. Span Skewness','Max. Span Exp. Ratio','Generation Time']    
    table.heading = heading
    body = []
    n  = NIGridQualityReport_getQualityPointerNumber()
    nrows  = a5_getNumberOfRows_()
    for i in range(0,n):
        rowbody = []
	rowqualitypointer = 0
        rowpointer        = 0
        name       = 'Entire Mesh'
	if i > 0:
	   rowqualitypointer  = NIGridQualityReport_getQualityPointerbyIndex(i-1)
	   name	       = NIGridQualityReport_getQualitiesName(rowqualitypointer)
        if i > 0 and i <=nrows:
            rowpointer = row(i).impl
	    rowfile    = fileprefix+'_row_'+`i`+'.html'
	    rowfileurl = prefix+'_row_'+`i`+'.html'
            rowbody.append(HTMLgen.Href(rowfileurl,name))
	    a5_html_report_init_row_file(rowfile,fileprefix+'_row_'+`i`,prefix+'_row_'+`i`,
					 rowqualitypointer,name,save_b2bview,save_3dView,rowpointer)
        else: rowbody.append(name)
        a =  NIGridQualityReport_getQualityCharacteristics(rowqualitypointer)
        for j in range(1,8):
	    if a[0] > 0: rowbody.append(a[j-1])
	    else:        rowbody.append('undefined')
        cpu =  NIGridQualityReport_getGenerationTime(rowqualitypointer)
        rowbody.append(cpu)
        body.append(rowbody)
    table.body = body
    doc.append(HTMLgen.Center(table))

## init global pictures table
def a5_html_report_init_global_picture_table(doc,fileprefix,prefix,row_list):
    a5_focus_3D_view()
    a5_full_view()
    table = HTMLgen.Table('Global Pictures')
    heading = ['Point of Views','solid model','blade grid Level 1','blade grid Level 2',
                                'hub&blade grid level 1','hub&blade grid level 2']    
    table.heading = heading
    body = []
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Front_Zoom_0',
							     'Front Zoom(1)',0,1,row_list))
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Front_Zoom_0.5',
							     'Front Zoom(0.5)',0,0.5,row_list))
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Front_Zoom_0.75',
							     'Front Zoom(0.25)',0,0.25,row_list))
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Back_Zoom_0',
							     'Back Zoom(1)',1,1,row_list))
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Back_Zoom_0.5',
							     'Back Zoom(0.5)',1,0.5,row_list))
    body.append(a5_html_report_init_global_picture_table_row(fileprefix,prefix,'Back_Zoom_0.75',
							     'Back Zoom(0.25)',1,0.25,row_list))
    table.body = body
    doc.append(HTMLgen.Center(table))

## init global pictures table row
def a5_html_report_init_global_picture_table_row(fileprefix,prefix1,prefix2,name,
						 pointOfView,zoom,row_list):

    list = []
    list.append(name)
    list.append(a5_html_report_init_global_picture_table_row_view
		(fileprefix,prefix1,prefix2,'solid_model',pointOfView,0,zoom,0,row_list))
    list.append(a5_html_report_init_global_picture_table_row_view
		(fileprefix,prefix1,prefix2,'blade_grid_1',pointOfView,0,zoom,1,row_list))
    list.append(a5_html_report_init_global_picture_table_row_view
		(fileprefix,prefix1,prefix2,'blade_grid_2',pointOfView,1,zoom,1,row_list))
    list.append(a5_html_report_init_global_picture_table_row_view
		(fileprefix,prefix1,prefix2,'hubblade_grid_1',pointOfView,0,zoom,2,row_list))
    list.append(a5_html_report_init_global_picture_table_row_view
		(fileprefix,prefix1,prefix2,'hubblade_grid_2',pointOfView,1,zoom,2,row_list))
    return list


## init global pictures table row view
def a5_html_report_init_global_picture_table_row_view(fileprefix,prefix,prefix1,prefix2,
						      pointOfView,coarse,zoom,grid,row_list):
    a5_view_3d_mesh(coarse,pointOfView,zoom,grid,row_list)	
    imagefile    = fileprefix+'_'+prefix1+'_'+prefix2+'.png'
    imagefileurl = prefix+'_'+prefix1+'_'+prefix2+'.png'
    print_as("png",imagefile)
    hoops_Update()
    tupl = HTMLgen.Href(imagefileurl,HTMLgen.Image(imagefileurl,height=80,width=100))
    return tupl
 

## init row page
def a5_html_report_init_row_file(file,fileprefix,prefix,rowqualitypointer,name,save_b2bview,save_3dView,rowpointer):
    doc = HTMLgen.BasicDocument()
    a5_html_report_init_header(doc)
    doc.append(a5_dummyLine)
    doc.append(HTMLgen.Center(HTMLgen.Font('Quality of '+name, color=BLUE,size='+2')))
    doc.append(a5_dummyLine)   
    a5_html_report_init_row_topology(doc,rowqualitypointer)
    doc.append(a5_lineSeparator)   
    a5_html_report_init_row_quality_criteria(doc,rowqualitypointer,'Skewness',2)
    a5_html_report_init_row_quality_criteria(doc,rowqualitypointer,'Aspect Ratio',3)
    a5_html_report_init_row_quality_criteria(doc,rowqualitypointer,'Expansion Ratio',4)
    a5_html_report_init_row_quality_criteria(doc,rowqualitypointer,'Spanwise Skewness Angle',5)
    a5_html_report_init_row_quality_criteria(doc,rowqualitypointer,'Spanwise Expansion Ratio',6)
    doc.append(a5_lineSeparator)   
    a5_html_report_init_row_meridional_quality_criteria(doc,rowpointer,fileprefix,prefix,7)    
    doc.append(a5_lineSeparator) 
    if save_b2bview == 1 :  
	a5_html_report_init_row_b2b_quality_criteria(doc,rowpointer,fileprefix,prefix,8)    
    doc.append(a5_lineSeparator)   
    row_list = []
    row_list.append(rowpointer)
    if save_3dView == 1 :
	a5_html_report_init_global_picture_table(doc,fileprefix,prefix,row_list)
    doc.write(file)	

## init row b2b quality
def a5_html_report_init_row_b2b_quality_criteria(doc,rowpointer,fileprefix,prefix,n):
    a5_focus_B2B_view()
    a5_full_view()
    table = HTMLgen.Table('Blade to Blade Quality')
    heading = ['Quality Criteria','Hub Mesh','Hub Expansion Ratio','Hub Skewness',
               'Shroud Mesh','Shroud  Expansion Ratio','Shroud Skewness']    
    table.heading = heading
    body = []
    item = a5_html_report_create_b2b_views_names(rowpointer)
    body.append(item) 
    set_active_control_layer_index(0)
    select_(rowpointer)
    a5_generate_b2b()
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"hub","mesh"))
    row_list = []
    row_list.append(rowpointer)
    calc_row_pointer_2D_mesh_quality("Expansion Ratio",row_list,1,5,5,1,0,1)    
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"hub","exp_ratio"))
    calc_row_pointer_2D_mesh_quality("Orthogonality",row_list,0,90,5,1,0,1)    
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"hub","skewness"))
    hide_quality_()
    set_active_control_layer_index(100)
    a5_generate_b2b()
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"shroud","mesh"))
    row_list = []
    row_list.append(rowpointer)
    calc_row_pointer_2D_mesh_quality("Expansion Ratio",row_list,1,5,5,1,0,1)    
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"shroud","exp_ratio"))
    calc_row_pointer_2D_mesh_quality("Orthogonality",row_list,0,90,5,1,0,1)    
    body.append(a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,"shroud","skewness"))
    hide_quality_()
    n = len(item)
    newbody = []
    for j in range(0, n):
        list = []
	for i in range(0, 7):
	   list.append(body[i][j])
	newbody.append(list)
    table.body = newbody	    	
    doc.append(table)

## init row meridional quality
def a5_html_report_init_row_meridional_quality_criteria(doc,rowpointer,fileprefix,prefix,n):
    unselect_all()
    select_(rowpointer)
    a5_focus_ZR_view()
    a5_full_view()
    a5_focus_on_active_entity_zr_()  
    imagefile    = fileprefix+'_merid.png' 
    imagefileurl = prefix+'_merid.png' 
    print_as("png",imagefile)
    hoops_Update()
    doc.append(HTMLgen.Heading(1,HTMLgen.Font(`n`+'. Meridional Quality', color=BLACK,size='+1'),align='left'))	
    doc.append(HTMLgen.Center(HTMLgen.Image(imagefileurl)))

## init row topology
def a5_html_report_init_row_topology(doc,rowpointer):
    doc.append(a5_dummyLine)
    text = NIGridQualityReport_getTopology(rowpointer)
    doc.append(HTMLgen.Heading(1,HTMLgen.Font('1. Topology', color=BLACK,size='+1'),align='left'))	
    for i in range(0, len(text)):
	doc.append(HTMLgen.Font(text[i], color=BLACK,size='+1'))	
	doc.append(a5_dummyLine)	

## init row topology
def a5_html_report_init_row_quality_criteria(doc,rowpointer,criteria,n):
    doc.append(a5_dummyLine)
    doc.append(HTMLgen.Heading(1,HTMLgen.Font(`n`+'. '+criteria, color=BLACK,size='+1'),align='left'))	
    qualitypointer   = NIGridQualityReport_getQualityPointerByName(rowpointer,criteria)
    interval = 	NIGridQualityReport_getQualityIntervalLimits(qualitypointer)
    values   = 	NIGridQualityReport_getQualityIntervalValues(qualitypointer)
    ninterval = interval[2]
    start    = interval[0]
    end      = interval[1]
    step = (end-start)/ninterval
    list = []
    for i in range(0, ninterval):
	a = []
        a.append(`start`+'-'+`start+step`)
        a.append(values[i])
        start = start+step
        list.append(a)
    text =  NIGridQualityReport_getQualityCharacteristics2(qualitypointer)
    for i in range(0, len(text)):
	doc.append(HTMLgen.Font(text[i], color=BLACK,size='+1'))	
	doc.append(a5_dummyLine)	
    doc.append(barchart.BarChart(barchart.DataList(list)))
    
    
def a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,prefix2,prefix3):
    imagefile    = fileprefix+"_"+prefix1+prefix2+prefix3+".png"
    imagefileurl = prefix+"_"+prefix1+prefix2+prefix3+".png"
    print_as("png",imagefile)
    hoops_Update()
    tupl = HTMLgen.Href(imagefileurl,HTMLgen.Image(imagefileurl,height=80,width=100))
    return tupl
            
## create b2b views name for active rows
def a5_html_report_create_b2b_views_names(rowpointer):
    list = []
    list.append(HTMLgen.Font('Global View', color=BLACK,size='+1'))
    list.append(HTMLgen.Font('Inlet', color=BLACK,size='+1'))
    list.append(HTMLgen.Font('Outlet', color=BLACK,size='+1'))
    arow=Row(rowpointer)
    nb = arow.num_blades()
    for j in range(1,nb+1):
	list.append(HTMLgen.Font('Blade '+`j`+': Leading edge zoom(1)', color=BLACK,size='+1'))
	list.append(HTMLgen.Font('Blade '+`j`+': Trailing edge zoom(1)', color=BLACK,size='+1'))
	list.append(HTMLgen.Font('Blade '+`j`+': Leading edge zoom(0.25)', color=BLACK,size='+1'))
	list.append(HTMLgen.Font('Blade '+`j`+': Trailing edge zoom(0.25)', color=BLACK,size='+1'))
    return list

## create b2b views for active rows
def a5_html_report_create_b2b_views(rowpointer,fileprefix,prefix,prefix1,prefix2):
    a5_focus_b2b_view_on_active_rows()
    arow = Row(rowpointer)
    list = []
    list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_b2b_view_',prefix2))
    arow.zoom_at_inlet(1,0)
    list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_b2b_view_INLET_',prefix2))
    arow.zoom_at_outlet(1,0)
    list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_b2b_view_OUTLET_',prefix2))
    nb = arow.num_blades()
    for j in range(1,nb+1):
	arow.blade(j).zoom_at_leading_edge(1)
	list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_blade_'+`j`+'_b2b_view_LE1_',prefix2))
	arow.blade(j).zoom_at_trailing_edge(1)
	list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_blade_'+`j`+'_b2b_view_TE1_',prefix2))
	arow.blade(j).zoom_at_leading_edge(0.25)
	list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_blade_'+`j`+'_b2b_view_LE2_',prefix2))
	arow.blade(j).zoom_at_trailing_edge(0.25)
	list.append(a5_hr_create_image_for_bulleted_list(fileprefix,prefix,prefix1,'_blade_'+`j`+'_b2b_view_TE2_',prefix2))
    return list        

def a5_html_report_create_picture(fileprefix):
    a5_focus_ZR_view()
    a5_full_view()
    unselect_all()
    select_all_rows()
    a5_generate_flow_paths();
    imagefile = fileprefix+"_zr_view.png"
    a5_print_ZR_png(imagefile)

