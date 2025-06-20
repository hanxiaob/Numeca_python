import sys,types

from IGG_MeshConfiguration import *
from meshConfiguration import *
from Grid     import *
from Geometry import *
from Project import *
from IGGSystem import *
from Autogrid5_configuration import *
from Autogrid5_fileManager   import *
from Autogrid5_meridional    import *
from Autogrid5_technoEffect  import *
from Autogrid5_viewa5        import *
from PythonViewing           import *
from Project                 import *
from Autogrid5_effect3d      import *
from Autogrid5_geometry_import import *
from Autogrid5_WizardLETE import *
from Autogrid5_rowWizard import *
from Autogrid5_globalRowWizard import *
from Autogrid5_B2BMesh import *
from Autogrid5_acousticWizard import *
from Geom    import *
from PYTHON  import *

#------------------------------------------------------------------------------------------------
#---------------------- PROJECT MANAGEMENT (open, save, export) ---------------------------------
#------------------------------------------------------------------------------------------------

def a5_new_project(bypass):
    a5_new_project_(bypass)
def a5_init_new_project_from_a_geomTurbo_file(geomTurbo):
    a5_init_from_geomTurbo_file(geomTurbo)
def a5_open_project(trb):
    a5_open_template_(trb, 1)
def a5_init_html_report_file():
    return a5_init_html_report_file_()
def a5_open_template(trb):
    a5_open_template_(trb, 0)
def a5_save_template(trb):
    fileName = a5_get_file_name_(trb)
    filePath = a5_get_file_path_(trb)
    a5_save_as_template_(fileName, filePath)
def a5_save_project(trb = "current"):
    if trb == "current":
        a5_save_project_()
    else:
        fileName = a5_get_file_name_(trb)
        filePath = a5_get_file_path_(trb)
        a5_save_as_project_(fileName, filePath)
def a5_save_mesh(igg):
    a5_save_mesh_(igg)
def a5_save_mesh_V72(igg):
    a5_save_meshAsFine72_(igg)
def a5_save_mesh_V86(igg):
    a5_save_meshAsFine86_(igg)
def a5_save_and_merge_project_mesh():
    a5_save_and_merge_mesh_()

# kept for backward : export all blocks without merging
def a5_export_CEDRE(fileName):
    a5_export_CEDRE_(fileName, 3, 0, "", 0, "")

def a5_export_CEDRE_all_blocks(fileName, merging = 1, mergedBlockName = ""):
    a5_export_CEDRE_(fileName, 3, merging, mergedBlockName)

def a5_export_CEDRE_row_by_row(fileName, merging = 1, mergedBlockName = ""):
    a5_export_CEDRE_(fileName, 4, merging, mergedBlockName)

def a5_export_CEDRE_block_group(fileName, groupName, merging = 1, mergedBlockName = ""):
    a5_export_CEDRE_(fileName, 2, merging, mergedBlockName, groupName)

def a5_export_CEDRE_block_list(fileName, blockList, merging = 1, mergedBlockName = ""):
    numBlocks = len(blockList)
    # Gather block pointers
    blockp = []
    for i in range(len(blockList)):
        blockp.append(block(blockList[i]).impl)
    a5_export_CEDRE_(fileName, 1, merging, mergedBlockName, numBlocks, blockp)

def a5_export_FLUENT(mesh_file):
    a5_export_FLUENT_(mesh_file)
def a5_export_CFDpp(mesh_file):
    a5_export_CFDpp_(mesh_file)
def a5_export_CRUNCH_CFD(mesh_file):
    a5_export_CRUNCH_CFD_(mesh_file)
def a5_export_HYDRA(mesh_file):
    a5_export_HYDRA_(mesh_file)
def a5_export_OpenFOAM(directory_name, branch = "official"):
    if not isinstance(branch, str):
        branch = "official"
    precision = 12
    #if not isinstance(precision, int) or precision <= 0:
    #    precision = 12
    a5_export_OpenFoam_(directory_name, branch, precision)
def a5_export_Abaqus(mesh_file,element_type="C3D8"):
    if not isinstance(element_type, str):
        element_type = "C3D8"
    a5_export_Abaqus_(element_type,mesh_file)
def a5_export_meridional_mesh(mesh_file, row_list):
    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)
    a5_exportMeridionalMesh_(mesh_file, number_of_rows, row_pointer_list)
def a5_export_B2B_mesh(mesh_file, row_list, spanwiseLayerPercentage):
    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)
    a5_exportB2BMesh_(mesh_file, number_of_rows, row_pointer_list, spanwiseLayerPercentage)
def a5_export_fluid_mesh():
    igg_exportFluidDomain()

#------------------------------------------------------------------------------------------------
#---------------------- GENERATION  ---------------------------------
#------------------------------------------------------------------------------------------------

def a5_generate_flow_paths_rows(row_list):
    row_pointer_list = []
    for i in range(len(row_list)):
        row_pointer_list.append(row(row_list[i]).impl)
    return a5_generate_flow_paths_rows_(row_pointer_list)
def a5_initialize_topology_rows(row_list, layer_percentage):
    row_pointer_list = []
    for i in range(len(row_list)):
        row_pointer_list.append(row(row_list[i]).impl)
    return a5_init_rows_topology_(row_pointer_list, layer_percentage)
def a5_generate_b2b_rows(row_list, layer_percentage):
    row_pointer_list = []
    for i in range(len(row_list)):
        row_pointer_list.append(row(row_list[i]).impl)
    return a5_generate_b2b_rows_(row_pointer_list, layer_percentage)
def a5_generate_3d(*args):
    if not len(args):
        return a5_generate_3d_all_()
    elif len(args) == 1:
        row_pointer_list = []
        meridional_effect_pointer_list = []
        row_3D_effect_pointer_list = []
        for entity in args[0]:
            if isinstance(entity, Row):
                row_pointer_list.append(entity.impl)
            elif isinstance(entity, TechnologicalEffectZR):
                meridional_effect_pointer_list.append(entity.impl)
            elif isinstance(entity, TechnologicalEffect3D):
                row_3D_effect_pointer_list.append(entity.impl)
            else:
                raise ValueError,'a5_generate_3d: wrong entity to generate'
        return a5_generate_3d_entities_(row_pointer_list, meridional_effect_pointer_list, row_3D_effect_pointer_list, 1, 1, 1)
    else:
        raise ValueError,'a5_generate_3d: wrong arguments'
def a5_avoid_blocks_conversion_after_3d_generation():
    avoidBlocksConversion_(1)

# old generation commands depending on TCL and tree selection. Does not work in real-batch. Should not be used anymore
def a5_start_3d_generation():
    a5_start_3d_generation_(1,1,1)
def a5_control_and_start_3d_generation(holes,endwall,endwallholes):
    a5_start_3d_generation_(holes,endwall,endwallholes)
def a5_reset_default_topology(): # deprecated
    a5_reset_default_topology_()
def a5_initialize_topology():
    a5_reset_default_topology_()
def a5_generate_b2b():
    a5_generate_b2b_()
def a5_generate_flow_paths():
    a5_generate_flow_paths_()
def a5_generate_basin_mesh():
    a5_generate_basin_mesh_()
def set_active_control_layer_index(a):
    a5_set_active_layer_(a)

#------------------------------------------------------------------------------------------------
#---------------------- PROJECT QUALITY  ---------------------------------
#------------------------------------------------------------------------------------------------

def calc_row_2D_mesh_quality(type,row_list,range_start,range_end,range_number,show=0,show_marker=0,show_cells=1):
    if type != "Orthogonality" and type != "Aspect Ratio" and type != "Expansion Ratio":
        raise ValueError,'Check quality: wrong criterion'

    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)

    a5_focus_B2B_view_()
    initialize_quality_grid_and_subwindow_()

    if show:
        set_quality_colormap_(1,type,range_start,range_end)

    return calc_2D_mesh_quality_([type,number_of_rows,row_pointer_list,show_marker,show_cells,
                                  range_start,range_end,range_number,show])

def calc_row_pointer_2D_mesh_quality(type,row_pointer_list,range_start,range_end,range_number,show=0,show_marker=0,show_cells=1):
    if type != "Orthogonality" and type != "Aspect Ratio" and type != "Expansion Ratio":
        raise ValueError,'Check quality: wrong criterion'

    a5_focus_B2B_view_()
    initialize_quality_grid_and_subwindow_()

    if show:
        set_quality_colormap_(1,type,range_start,range_end)

    return calc_2D_mesh_quality_([type,len(row_pointer_list),row_pointer_list,show_marker,show_cells,
                                  range_start,range_end,range_number,show])

def calc_row_2D_mesh_quality_inter_block(type,row_list,range_start,range_end,range_number,show=0,show_marker=0,show_cells=1):
    if type != "Orthogonality" and type != "Angular Deviation" and type != "Expansion Ratio":
        raise ValueError,'Check quality: wrong criterion'

    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)

    a5_focus_B2B_view_()
    initialize_quality_grid_and_subwindow_()

    if show:
        set_quality_colormap_(1,type,range_start,range_end)

    return calc_2D_mesh_quality_inter_block_([type,number_of_rows,row_pointer_list,show_marker,show_cells,
                                              range_start,range_end,range_number,show])

def calc_row_meridional_mesh_quality(type,row_list,range_start,range_end,range_number,show=0,show_marker=0,show_cells=1):
    if type != "Expansion Ratio" and type != "Overlap":
        raise ValueError,'Check quality: wrong criterion'

    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)

    a5_focus_ZR_view_()
    initialize_quality_grid_and_subwindow_()

    if show:
        set_quality_colormap_(1,type,range_start,range_end)

    return calc_2D_mesh_quality_([type,number_of_rows,row_pointer_list,show_marker,show_cells,
                                  range_start,range_end,range_number,show])

def calc_row_meridional_mesh_quality_inter_block(type,row_list,range_start,range_end,range_number,show=0,show_marker=0,show_cells=1):
    if type != "Expansion Ratio":
        raise ValueError,'Check quality: wrong criterion'

    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        row_pointer_list.append(row(row_list[i]).impl)

    a5_focus_ZR_view_()
    initialize_quality_grid_and_subwindow_()

    if show:
        set_quality_colormap_(1,type,range_start,range_end)

    return calc_2D_mesh_quality_inter_block_([type,number_of_rows,row_pointer_list,show_marker,show_cells,
                                              range_start,range_end,range_number,show])

#------------------------------------------------------------------------------------------------
#---------------------- DEMO  MANAGEMENT ---------------------------------
#------------------------------------------------------------------------------------------------

def a5_sleep_seconds(wait):
    a5_sleep(wait)

fullAutomaticMode = 0
def a5_view_popup(index,wait):
    if a5_is_windows_session()==1:
        return
    timed = 1
    if wait==1:
        timed=0
    if fullAutomaticMode==1:
        timed=0
    a5_tclCommand("turboConfig:openPopup "+`index`+" "+`timed`)
    if timed==0:
        a5_waitLeftClick()
        a5_tclCommand("turboConfig:closePopup")
def a5_view_mc_popup(index,wait):
    if a5_is_windows_session()==1:
        return
    timed = 1
    if wait==1:
        timed=0
    if fullAutomaticMode==1:
        timed=0
    a5_tclCommand("meshconfiguration:openPopup "+`index`+" "+`timed`)
    if timed==0:
        a5_waitLeftClick()
        a5_tclCommand("meshconfiguration:closePopup")

def a5_toggle_ag_left_menu():
    a5_tclCommand("Autogrid:Layout:pack_left_menu CONFIG")
def a5_toggle_igg_left_menu():
    a5_tclCommand("Autogrid:Layout:pack_left_menu XYZ")
def a5_switch_to_wizard_mode():
    a5_tclCommand("autogrid5:choose_wizard_mode")
def a5_switch_to_basic_mode():
    a5_tclCommand("autogrid5:choose_wizard_mode")
def a5_switch_to_expert_mode():
    a5_tclCommand("autogrid5:choose_expert_mode")

#------------------------------------------------------------------------------------------------
#---------------------- VIEW  MANAGEMENT ---------------------------------
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
        a5_zoom_at(centerx,centery,centerz,zoom)
    return zoom
# following routine keep the same view normal
def a5_get_camera_target_point():
    list = a5_get_camera_target()
    return Point(list[0],list[1],list[2])
def a5_get_camera_position_point():
    list = a5_get_camera_position()
    return Point(list[0],list[1],list[2])
def zoomFromAt2(centerx2,centery2,centerz2,zoom1,zoomstep,nstep):
    P  = a5_get_camera_target()
    centerx1 = P[0]
    centery1 = P[1]
    centerz1 = P[2]
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
        a5_zoom_at(centerx,centery,centerz,zoom)
    return zoom
# following routine do not keep the same view normal
def setCameraTargetZoom(centerx2,centery2,centerz2,nstep,zoom):
    P  = a5_get_camera_target()
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
        a5_camera_target_zoom(centerx,centery,centerz,zoom)
def a5_CameraRotateU(angle,nstep):
    a5_camera_rotate_u(angle,nstep)
def a5_CameraRotateV(angle,nstep):
    a5_camera_rotate_v(angle,nstep)
def a5_CameraLocation(x,y,z,nstep):
    a5_set_camera_location(x,y,z,nstep)
def a5_moveCameraAt(x,y,z,vx,vy,vz,nstep,zoom,percentage):
    a5_camera_align_n(vx,vy,vz,x,y,z,nstep,zoom,percentage)
def a5_moveCameraAlongV(vx,vy,vz,distance,nstep):
    a5_moveCameraAlong(vx,vy,vz,distance,nstep)
def a5_CameraPerspectiveMode():
    a5_camera_perpective()
def a5_change_camera_direction(u,v,nstep):
    a5_set_camera_uv(u,v,nstep)
## set a global view of the mesh
## coarseLevel : 0,1,2,... (default 0)
## pointOfView: 0 : front, 1 : back (default 0)
## zoom : default 1
## grid : 0 : no grid representation, 1 : blade grid representation,
##        2: blade and hub grid representation
## row_list: representation field (empty list = entire mesh)
def a5_hide_3d_mesh():
    a5_hide3DMesh_()
def a5_view_3d_mesh_default():
    a5_view3DMesh_(0,1,1,2,0,0,0)
def a5_view_3d_mesh_default():
    a5_view3DMesh_(0,1,1,2,0,0,0)
def a5_view_3d_mesh  (coarseLevel,pointOfView,zoom,grid,row_list):
    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        if not isinstance(row_list[i], Row):
            row_pointer_list.append(row_list[i])
        else:
            row_pointer_list.append(row(row_list[i]).impl)
    a5_view3DMesh_(coarseLevel,pointOfView,zoom,grid,1,1,len(row_pointer_list),row_pointer_list)
def a5_view_3d_mesh_fixed_2  (coarseLevel,pointOfView,zoom,grid,row_list):
    row_pointer_list = []
    number_of_rows = len(row_list)
    for i in range(number_of_rows):
        if not isinstance(row_list[i], Row):
            row_pointer_list.append(row_list[i])
        else:
            row_pointer_list.append(row(row_list[i]).impl)
    a5_view3DMesh_(coarseLevel,pointOfView,zoom,grid,-1,0,len(row_pointer_list),row_pointer_list)
def a5_view_3d_mesh_fixed  ():
    a5_view3DMesh_(0,0,1,2,-1,0,0)
def a5_view_3d_mesh_fixed_repet  ():
    a5_view3DMesh_(0,0,1,2,-2,0,0)
def a5_focus_3D_view  ():
    a5_focus_3D_view_()
def a5_focus_ZR_view  ():
    a5_focus_ZR_view_()
def a5_focus_B2B_view  ():
    a5_focus_B2B_view_()
def a5_full_view  ():
    a5_full_view_()
def a5_multi_view  ():
    a5_multi_view_()
def a5_focus_b2b_view_on_active_rows  ():
    a5_focus_on_active_entity_()
def a5_view_b2b_repetition  ():
    a5_focus_B2B_view()
    view_repetition_(1)
def a5_hide_b2b_repetition  ():
    a5_focus_B2B_view()
    view_repetition_(0)
def a5_view_b2b_repetition_number  (n):
    a5_focus_B2B_view()
    a5_setB2BRepetition(n)
def a5_print_b2b_png  (file):
    a5_focus_B2B_view()
    a5_full_view()
    print_as("png",file)
    hoops_Update()
def a5_print_3D_png  (file):
    a5_focus_3D_view()
    a5_full_view()
    print_as("png",file)
    hoops_Update()
def a5_print_ZR_png  (file):
    a5_focus_ZR_view()
    a5_full_view()
    print_as("png",file)
    hoops_Update()
def a5_enable_full_display_smoothing_mode  ():
    a5_display_smoothing_step_by_step_(1)
def a5_disable_full_display_smoothing_mode  ():
    a5_display_smoothing_step_by_step_(0)
## type : 'Orthogonality' 'Aspect Ratio' 'Expansion Ratio'
def a5_enable_full_display_quality_mode  (type):
    a5_display_smoothing_step_by_step_quality_(type)
def a5_disable_full_display_quality_mode  ():
    a5_display_smoothing_step_by_step_quality_('none')


def a5_remove_Cooling_Wall_B2B_Rep  (blade):
    a5_removeCoolingWallB2BRep(blade)
def a5_toggle_b2b_mesh  ():
    a5_b2b_toggle_rep(0,'face_grid')
def a5_toggle_b2b_grid_point  ():
    a5_b2b_toggle_rep(0,'grid_points')
def a5_toggle_b2b_edges  ():
    a5_b2b_toggle_rep(0,'data_points')

def a5_merge_fnmb  (name1,name2,sens):
    a5_merge_fnmb_(name1,name2,sens)

#------------------------------------------------------------------------------------------------
#---------------------- DIALOG BOX  MANAGEMENT FOR DEMO PURPOSE ONLY ----------------------------
#------------------------------------------------------------------------------------------------


def a5_waitLeftClick  ():
    a5_waitLeftClick_()
def a5_disable_waitLeftClick  ():
    a5_disable_waitLeftClick_()
def a5_enable_waitLeftClick  ():
    a5_enable_waitLeftClick_()
def a5_tclUpdate  ():
    a5_tclUpdate_()
def a5_init_demo_text_box  ():
    a5_init_demo_text_box_()
def a5_init_demo(resize_left_panel=1):
    a5_tclCommand("autogrid5:choose_expert_mode")
    a5_disable_new_camera_repositionning_for_face_displacement()
    a5_demo_mode_enabled()
    if resize_left_panel: a5_tclCommand("igg:resizeLeftPaneWindow 410")
    a5_tclCommand("igg:FullSizeForTopWindow")
    a5_tclCommand("close_proj_sensitive_dialog")
    set_preference("Autogrid5_b2b_mesh_optimization_full_visibility",0)
    set_preference("Autogrid5_b2b_mesh_optimization_full_visibility",0)
    set_preference("geometry_curve_width",2)
    set_preference ("Autogrid5_meridional_channel_shading",1)
    set_preference ("CGNS_patch_info_saving",0)
    set_preference ("gui_progress_status_window",0)
    a5_init_demo_text_box()
    text_message_box_("-->")
    a5_tclCommand("TextMessageBox:place 420 0")
def a5_move_TextMessageBox_demo_at_bottom  ():
    x  = 420
    y1 = 0
    y2 = 1000
    for i in range(1,60):
        y = y1 + i*(y2-y1)/60
        cmd = "TextMessageBox:place "+`x`+" "+`y`
        a5_tclCommand(cmd)

def a5_move_TextMessageBox_demo_at_up  ():
    cmd = "TextMessageBox:place 420 0"
    a5_tclCommand(cmd)

## row properties
def a5_open_dialog_box_row_properties  ():
    a5_openDialogBox_("rowProperties:rowProperties 0 0")
def a5_close_dialog_box_row_properties ():
    a5_closeDialogBox_("rowProperties:~rowProperties")

## meridional control line
def a5_open_dialog_box_control_line  ():
    a5_openDialogBox_("row_bndProperties:row_bndProperties 0 0")
def a5_close_dialog_box_control_line ():
    a5_closeDialogBox_("row_bndProperties:~row_bndProperties")

## optimization
def a5_open_dialog_box_optimization  ():
    a5_openDialogBox_("optiProperties:optiProperties 0 0")
def a5_close_dialog_box_optimization ():
    a5_closeDialogBox_("optiProperties:~optiProperties")

## flow path control
def a5_open_dialog_box_flow_path_control  ():
    a5_openDialogBox_("zrTopologyProperties:zrTopologyProperties 0 0")
def a5_close_dialog_box_flow_path_control ():
    a5_closeDialogBox_(".zrTopologyProperties")

## gap control
def a5_open_dialog_box_gap_control  ():
    a5_openDialogBox_("gapProperties:gapProperties 0 0 Gap")
def a5_close_dialog_box_gap_control ():
    a5_closeDialogBox_("gapProperties:~gapProperties")

## partial gap control
def a5_open_dialog_box_partial_gap_control  ():
    a5_openDialogBox_("partialGapProperties:partialGapProperties 0 0 ")
def a5_close_dialog_box_partial_gap_control ():
    a5_closeDialogBox_("partialGapProperties:~partialGapProperties")

## b2b control
def a5_open_dialog_box_b2b_control  ():
    a5_openDialogBox_("b2bSkinTopology:b2bSkinTopology2 0 0")
def a5_close_dialog_box_b2b_control ():
    a5_closeDialogBox_("b2bSkinTopology:destroy")

def a5_open_row_mesh_control  ():
    a5_openRowControl_()
def a5_close_row_mesh_control  ():
    a5_closeRowControl_()
def a5_open_active_b2b_layer  ():
    a5_openActiveB2BLayer_()
def a5_close_active_b2b_layer  ():
    a5_closeActiveB2BLayer_()

def a5_update_dialog_box():
    a5_updateDialogBox_()




#------------------------------------------------------------------------------------------------
#---------------------- LIBRARY MANAGEMENT ---------------------------------
#------------------------------------------------------------------------------------------------

def delete_row_topology(name):
    a5_remove_row_topology_(name)
def delete_b2b_topology(name):
    a5_remove_b2b_topology_(name)

#------------------------------------------------------------------------------------------------
#                                     Configuration management
#------------------------------------------------------------------------------------------------

def a5_get_configuration_units():
    return a5_getConfigUnits_()
def a5_set_configuration_units(units, unitsFactor=1):
    a5_setConfigUnits_(units, unitsFactor)
    a5_tclCommand("autogrid5:getUnits")
def a5_get_configuration_units_factor():
    return a5_getConfigUnitsFactor_()

def a5_get_bypass_project():
    return a5_get_config_bypass_()

def a5_set_cascade_project(cascade):
    a5_set_config_cascade_(cascade)    
def a5_get_cascade_project():
    return a5_get_config_cascade_()

def a5_get_project_path():
    return a5_getProjectPath_()

def a5_get_project_name():
    return a5_getProjectName_()

def a5_set_configuration_number_of_grid_levels(numberOfGridLevel):
    a5_setConfigUserDefinedNumberOfGridLevel_(numberOfGridLevel)
def a5_get_configuration_number_of_grid_levels():
    return a5_getConfigUserDefinedNumberOfGridLevel_()

def a5_get_row_number():
    return a5_getNumberOfRows_()

def a5_row_at_the_end_of_the_channel():
    a5_add_row_(0)
# possibly if by-pass configuration
def a5_row_on_the_nozzle_of_the_engine():
    a5_add_row_(1)
def a5_row_in_the_bypass():
    a5_add_row_(2)
def a5_row_at_the_outlet_of_the_compressor():
    a5_add_row_(3)

def a5_set_support_curve_control_pts(value):
    set_support_curve_control_pts_(value)
def a5_get_support_curve_control_pts():
    return get_support_curve_control_pts_()

def z_cst_line(name):
    return RSInterface(get_rs_pointer_(name))
def get_all_z_cst_lines():
    linePointerList = get_all_z_cst_lines_()
    lineObjectList = []
    for pointer in linePointerList:
        lineObjectList.append(RSInterface(pointer))
    return lineObjectList
def get_row_z_cst_lines_upstream(row_object):
    if not isinstance(row_object, Row): raise ValueError,'wrong row object in argument'
    linePointerList = get_row_z_cst_lines_upstream_(row_object.impl)
    lineObjectList = []
    for pointer in linePointerList:
        lineObjectList.append(RSInterface(pointer))
    return lineObjectList
def get_row_z_cst_lines_downstream(row_object, layer_index=0):
    if not isinstance(row_object, Row): raise ValueError,'wrong row object in argument'
    linePointerList = get_row_z_cst_lines_downstream_(row_object.impl, layer_index)
    lineObjectList = []
    for pointer in linePointerList:
        lineObjectList.append(RSInterface(pointer))
    return lineObjectList
def get_row_z_cst_lines_on_blade(row_object, layer_index=0):
    if not isinstance(row_object, Row): raise ValueError,'wrong row object in argument'
    linePointerList = get_row_z_cst_lines_on_blade_(row_object.impl, layer_index)
    lineObjectList = []
    for pointer in linePointerList:
        lineObjectList.append(RSInterface(pointer))
    return lineObjectList
def delete_z_cst_line(rs):
    rs_object = 0
    if isinstance(rs,RSInterface): rs_object = rs
    else: rs_object = RSInterface(get_rs_pointer_(rs))
    delete_z_cst_line_(rs_object.impl)
def compute_default_z_cst_line(point, channel_curve_type):
    rs = compute_default_z_cst_line_(format_point(point), channel_curve_type)
    if rs: return RSInterface(rs)
    else: return 0
def compute_default_relative_z_cst_line(row_ref,row_location,relative_location):
    rs = compute_default_rel_z_cst_line_(row(row_ref).impl,row_location,relative_location)
    if rs: return RSInterface(rs)
    else: return 0

#------------------------------------------------------------------------------------------------
#                                     Geometry import
#------------------------------------------------------------------------------------------------

def a5_set_import_geometry_rotation_axis(orig, direction, span_dir=Vector(1,0,0)):
    AutoGrid_Import_rot_axis_((orig.x,orig.y,orig.z), (direction.x,direction.y,direction.z),
                              (span_dir.x,span_dir.y,span_dir.z))

#import a geometry file and replace the geometry
def a5_import_and_replace_geometry_file(file_name):
    a5_openGeometryFile(file_name)
#import a geometry file into the import CAD window
def a5_import_geometry_file(file_name):
    AutoGrid_import_geometry_(file_name)

def a5_get_import_geometry_repository():
    return Geometry(AutoGrid_Import_get_geom_())

def a5_clean_import_geometry():
    AutoGrid_Import_close_geom_()

def a5_focus_importCAD():
    AutoGrid_Focus_Import_()

def a5_link_to_hub(curve_names):
    curve_pointers = []
    for i in range(len(curve_names)):
        curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
    AutoGrid_link_hub_(curve_pointers)

def a5_link_to_hub_surface(row,surface_names):
    surface_pointers = []
    for i in range(len(surface_names)):
        surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
    AutoGrid_link_hub_surface_(row.impl,surface_pointers)

def a5_link_to_shroud_surface(row,surface_names):
    surface_pointers = []
    for i in range(len(surface_names)):
        surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
    AutoGrid_link_shroud_surface_(row.impl,surface_pointers)

def a5_link_to_tip_gap_surface(row,surface_names):
    surface_pointers = []
    for i in range(len(surface_names)):
        surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
    AutoGrid_link_tip_gap_surface_(row.impl,surface_pointers)

def a5_link_to_shroud(curve_names):
    curve_pointers = []
    for i in range(len(curve_names)):
        curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
    AutoGrid_link_shroud_(curve_pointers)

def a5_link_to_nozzle(curve_names):
    curve_pointers = []
    for i in range(len(curve_names)):
        curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
    AutoGrid_link_nozzle_(curve_pointers)

def a5_link_to_basic_curve(curve_names):
    curve_pointers = []
    for i in range(len(curve_names)):
        curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
    AutoGrid_link_basic_curve_(curve_pointers)

def a5_define_hub(point_list):
    formatted_point_list = []
    for i in range(len(point_list)):
        formatted_point_list.append(format_point(point_list[i]))
    AutoGrid_define_channel_curve_(0,len(point_list),formatted_point_list)

def a5_define_shroud(point_list):
    formatted_point_list = []
    for i in range(len(point_list)):
        formatted_point_list.append(format_point(point_list[i]))
    AutoGrid_define_channel_curve_(1,len(point_list),formatted_point_list)

def a5_define_nozzle(point_list):
    formatted_point_list = []
    for i in range(len(point_list)):
        formatted_point_list.append(format_point(point_list[i]))
    AutoGrid_define_channel_curve_(2,len(point_list),formatted_point_list)

#------------------------------------------------------------------------------------------------

class CurvePointNormMerid(CurvePointNorm):
    def __init__(self,curve,p):
        c = 0
        if isinstance(curve,Curve): c = curve
        else:                       c = Curve(get_curve_by_name_(AutoGrid_Merid_get_geom_(),curve))

        CurvePointNorm.__init__(self,c,p)

#------------------------------------------------------------------------------------------------
#                                     basic class NIConfigurationEntities
#------------------------------------------------------------------------------------------------

class NIConfigurationEntities:
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def unselect(self):
        unselect_(self.impl)
    def meshConfigurationDomain(self):
        return MeshConfigurationDomain(a5_meshConfigurationDomain(self.impl))
    def select_configuration(self):
        select_configuration_(self.impl)
    def unselect_configuration(self):
        unselect_configuration_(self.impl)
    def parent(self):
        pointer = get_parent_(self.impl)
        if pointer == 0 : return 0
        else : return NIConfigurationEntities(pointer)

    def generation_success(self):
        return a5_generation_success_(self.impl)
    def generation_error_message(self):
        return a5_generation_error_message_(self.impl)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class B2B Cut
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def a5_add_B2B_cut():
    B2BMesh_new()

class B2BCut(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def delete(self):
        B2BMesh_delete(self.impl)
        self.impl = 0
    def select(self):
        select_(self.impl)

    def set_name(self,name):
        B2BMesh_setName(self.impl,name)
    def get_name(self):
        return B2BMesh_getName(self.impl)
    def create(self):
        return B2BMesh3DGeneration(self.impl)
    # 0->100
    def set_width(self,value):
        B2BMesh_setDefaultParameters(self.impl,"spanwiseWidth",value)
    def get_width(self):
        return B2BMesh_getDefaultParameters(self.impl,"spanwiseWidth")
    # 0->100
    def set_location(self,value):
        B2BMesh_setDefaultParameters(self.impl,"spanwiseLocation",value)
    def get_location(self):
        return B2BMesh_getDefaultParameters(self.impl,"spanwiseLocation")

def b2bCut(B):                          # indices from 1
    if type(B) is types.StringType:         # assuming name of row is given
        return B2BCut(B2BMesh_pointer(B))
    elif isinstance(B,Row):
        return B
    else:   return B2BCut(B2BMesh_pointer(B2BMesh_getNameByIndex(B-1)))


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     Bulb parameters
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def set_inlet_bulb_sharp_topology():
    setBulbParametersByName(0,"topologyType",0)

def set_inlet_bulb_rounded_topology():
    setBulbParametersByName(0,"topologyType",1)

def set_inlet_bulb_radial_topology():
    setBulbParametersByName(0,"topologyType",2)

def set_inlet_bulb_streamwise_number_of_points(value):
    setBulbParametersByName(0,"limit",value)

def set_inlet_bulb_H_streamwise_number_of_points(value):
    setBulbParametersByName(0,"stagnationPoint",value)

def set_inlet_bulb_spanwise_number_of_points(value):
    setBulbParametersByName(0,"numberOfStreamwisePoints",value)

def set_inlet_bulb_C_block_number_of_points(value):
    setBulbParametersByName(0,"numberOfSpanwisePoints",value)

def set_inlet_bulb_radial_number_of_points(value):
    setBulbParametersByName(0,"numberOfSpanwisePoints",value)

def set_inlet_bulb_singular_line(value):
    if value:
      setBulbParametersByName(0,"Rmin",0)
    else:
      setBulbParametersByName(0,"Rmin",1)

def set_inlet_bulb_smoothing_steps(value):
    setBulbParametersByName(0,"smoothingSteps",value)

def set_inlet_bulb_butterfly_smoothing_steps(value):
    setBulbParametersByName(0,"butterflySmoothingSteps",value)

def set_outlet_bulb_sharp_topology():
    setBulbParametersByName(1,"topologyType",0)

def set_outlet_bulb_rounded_topology():
    setBulbParametersByName(1,"topologyType",1)

def set_outlet_bulb_radial_topology():
    setBulbParametersByName(1,"topologyType",2)

def set_outlet_bulb_streamwise_number_of_points(value):
    setBulbParametersByName(1,"limit",value)

def set_outlet_bulb_H_streamwise_number_of_points(value):
    setBulbParametersByName(1,"stagnationPoint",value)

def set_outlet_bulb_spanwise_number_of_points(value):
    setBulbParametersByName(1,"numberOfStreamwisePoints",value)

def set_outlet_bulb_C_block_number_of_points(value):
    setBulbParametersByName(1,"numberOfSpanwisePoints",value)

def set_outlet_bulb_radial_number_of_points(value):
    setBulbParametersByName(1,"numberOfSpanwisePoints",value)

def set_outlet_bulb_singular_line(value):
    if value:
      setBulbParametersByName(1,"Rmin",0)
    else:
      setBulbParametersByName(1,"Rmin",1)

def set_outlet_bulb_smoothing_steps(value):
    setBulbParametersByName(1,"smoothingSteps",value)

def set_outlet_bulb_butterfly_smoothing_steps(value):
    setBulbParametersByName(1,"butterflySmoothingSteps",value)


def get_inlet_bulb_topology():
    return getBulbParametersByName(0,"topologyType") #0:H, 1:C, 2:RADIAL

def get_inlet_bulb_streamwise_number_of_points():
    return getBulbParametersByName(0,"limit")

def get_inlet_bulb_H_streamwise_number_of_points():
    return getBulbParametersByName(0,"stagnationPoint")

def get_inlet_bulb_spanwise_number_of_points():
    return getBulbParametersByName(0,"numberOfStreamwisePoints")

def get_inlet_bulb_C_block_number_of_points():
    return getBulbParametersByName(0,"numberOfSpanwisePoints")

def get_inlet_bulb_radial_number_of_points():
    return getBulbParametersByName(0,"numberOfSpanwisePoints")

def get_inlet_bulb_singular_line():
    a = getBulbParametersByName(0,"Rmin")
    if a:
        return 0
    else:
        return 1

def get_inlet_bulb_smoothing_steps():
    return getBulbParametersByName(0,"smoothingSteps")

def get_inlet_bulb_butterfly_smoothing_steps():
    return getBulbParametersByName(0,"butterflySmoothingSteps")

def get_outlet_bulb_topology():
    return getBulbParametersByName(1,"topologyType") #0:H, 1:C, 2:RADIAL

def get_outlet_bulb_streamwise_number_of_points():
    return getBulbParametersByName(1,"limit")

def get_outlet_bulb_H_streamwise_number_of_points():
    return getBulbParametersByName(1,"stagnationPoint")

def get_outlet_bulb_spanwise_number_of_points():
    return getBulbParametersByName(1,"numberOfStreamwisePoints")

def get_outlet_bulb_C_block_number_of_points():
    return getBulbParametersByName(1,"numberOfSpanwisePoints")

def get_outlet_bulb_radial_number_of_points():
    return getBulbParametersByName(1,"numberOfSpanwisePoints")

def get_outlet_bulb_singular_line():
    a = getBulbParametersByName(1,"Rmin")
    if a:
        return 0
    else:
        return 1

def get_outlet_bulb_smoothing_steps():
    return getBulbParametersByName(1,"smoothingSteps")

def get_outlet_bulb_butterfly_smoothing_steps():
    return getBulbParametersByName(1,"butterflySmoothingSteps")


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class Row
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Row(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def delete(self):
        delete_row_(self.impl)
        self.impl = 0

    def get_index(self):
        return get_row_index_(self.impl)

    def load_geometry(self,name):
        a5_import_geomTurbo_file_for_row_(self.impl,name)

    def add_row_upstream(self):
        add_row_up_down_(self.impl,0)

    def add_row_downstream(self):
        add_row_up_down_(self.impl,1)

## 3d blocks list

    def block_list(self):
        blist = []
        for pointer in a5_get_entity_block_list_(self.impl):
            blist.append(Block(pointer))
        return blist


## graphics geometry repetition

    def setGraphicsRepetition(self,value):
        a5_setRowRepetition(self.impl,value,0)
    def setDefaultGraphicsRepetition(self):
        a5_setRowRepetition(self.impl,1,1)


## zoom

##       -1< where < 1 && level>0
    def zoom_at_inlet(self,level,where):
        a5_zoom_at_inlet_(self.impl,level,where)
    def zoom_at_outlet(self,level,where):
        a5_zoom_at_outlet_(self.impl,level,where)
    def zoom_at_inlet_up(self,level):
        a5_zoom_at_inlet_(self.impl,level,1)
    def zoom_at_outlet_up(self,level):
        a5_zoom_at_outlet_(self.impl,level,1)
    def zoom_at_inlet_down(self,level):
        a5_zoom_at_inlet_(self.impl,level,-1)
    def zoom_at_outlet_down(self,level):
        a5_zoom_at_outlet_(self.impl,level,-1)

# row topology library

    def load_topology(self,name):
        a5_load_row_topology_(self.impl,name)

    def save_topology(self,name):
        a5_save_row_topology_(self.impl,name)

    def copy_topology(self):
        a5_copy_topology_(self.impl,"0")

    def paste_topology(self):
        a5_paste_topology_(self.impl,"0")

# b2b topology library

    def save_b2b_topology(self,name):
        a5_save_b2b_topology_(self.impl,name)
    def load_b2b_topology(self,name):
        a5_load_b2b_topology_(self.impl,name)


# bnd access

    def inlet(self):
        return RSInterface(get_row_inlet_(self.impl))
    def outlet(self):
        return RSInterface(get_row_outlet_(self.impl,0))
    def outlet2(self):
        return RSInterface(get_row_outlet_(self.impl,1))

# TechnologicalEffect3D

    def num_effect3D(self):
        return technoEffect3d_number_(self.impl)

    def effect3D(self,i):
        return TechnologicalEffect3D(technoEffect3d_getByName_(self.impl,technoEffect3d_getNameByIndex_(self.impl,i-1)))

    def new_effect3D(self):
        technoEffect3d_new_(self.impl)
        return self.effect3D(self.num_effect3D())

# blade

    def num_blades(self):
        return get_row_number_of_blade_(self.impl)

    def blade(self,i):
        return Blade(get_blade_by_name_(self.impl,get_blade_name_by_index_(self.impl,i-1)))

    def add_blade(self):
        a5_add_blade_(self.impl)

# gaps, fillets
    def add_hub_gap(self):
        for i in range(1, self.num_blades()+1):
            self.blade(i).add_hub_gap()

    def add_shroud_gap(self):
        for i in range(1, self.num_blades()+1):
            self.blade(i).add_shroud_gap()

    def add_hub_fillet(self):
        for i in range(1, self.num_blades()+1):
            self.blade(i).add_hub_fillet()

    def add_shroud_fillet(self):
        for i in range(1, self.num_blades()+1):
            self.blade(i).add_shroud_fillet()

# snubbers
    def get_number_of_snubbers(self):
        return getNumberOfSnubbers_(self.impl)
    def add_snubber(self):
        snubberPtr = addRowSnubber_(self.impl)
        return Snubber(snubberPtr)
    def snubber(self, index):
        return Snubber(getSnubberPointer_(self.impl, getSnubberNameByIndex_(self.impl, index-1)))

    def set_name(self,name):
        set_row_name_(self.impl,name)
    def get_name(self):
        return get_row_name_(self.impl)

    def get_row_flow_path_number(self):
        return get_row_flow_path_number_(self.impl)
    def set_row_flow_path_number(self, n):
        set_row_flow_path_number_(self.impl,n)

#       n=1 for coarse, 2 for medium, 3 for fine and 4 for userdef. If n==4, target should be specified.
    def set_coarse_grid_level(self, n, target=250000):
        set_coarse_grid_level_(self.impl,n,target)
    def get_coarse_grid_level(self):
        result = get_row_accuracy_(self.impl)
        return result[0]
    def get_coarse_grid_level_target(self):
        result = get_row_accuracy_(self.impl)
        return result[1]
    def set_streamwise_weight(self, inlet, outlet, blade):
        set_streamwise_weight_(self.impl, inlet, outlet, blade)
    def get_streamwise_weight_inlet(self):
        result = get_row_accuracy_(self.impl)
        return result[2]
    def get_streamwise_weight_blade(self):
        result = get_row_accuracy_(self.impl)
        return result[3]
    def get_streamwise_weight_outlet(self):
        result = get_row_accuracy_(self.impl)
        return result[4]

    def select(self):
        select_(self.impl)

    def unselect(self):
        unselect_(self.impl)

## generation

    def generate_flow_paths2(self,checkquality):
        generate_flow_paths2_(self.impl,checkquality)
    def generate_flow_paths(self):
        generate_flow_paths_(self.impl)

##################### Properties ###############

    def set_periodicity(self, a):
        return set_row_properties_(self.impl,"numberOfBlades",a)
    def get_periodicity(self):
        return get_row_properties_(self.impl,"numberOfBlades")

    def set_number_of_periodicity_geometry(self, a):
        return set_row_properties_(self.impl,"geometryRepetition",a)
    def get_number_of_periodicity_geometry(self):
        return get_row_properties_(self.impl,"geometryRepetition")

    def set_rotation_speed(self, a):
        return set_row_properties_(self.impl,"rotationSpeed",a)
    def get_rotation_speed(self):
        return get_row_properties_(self.impl,"rotationSpeed")

    def set_upstream_block_relaxation(self, a):
        set_row_properties_(self.impl,"relaxUpstreamInletClustering",a)
    def get_upstream_block_relaxation(self):
        return get_row_properties_(self.impl,"relaxUpstreamInletClustering")
    def set_downstream_block_relaxation(self, a):
        set_row_properties_(self.impl,"relaxDowstreamOutletClustering",a)
    def get_downstream_block_relaxation(self):
        return get_row_properties_(self.impl,"relaxDowstreamOutletClustering")
    def set_downstream_block_relaxation_before_nozzle(self, a):
        set_row_properties_(self.impl,"relaxDowstreamOutletClusteringBeforeNozzle",a)
    def get_downstream_block_relaxation_before_nozzle(self):
        return get_row_properties_(self.impl,"relaxDowstreamOutletClusteringBeforeNozzle")

    def set_untwist_upstream_block(self, a):
        set_row_properties_(self.impl,"untwistInlet",a)
    def get_untwist_upstream_block(self):
        return get_row_properties_(self.impl,"untwistInlet")
    def set_untwist_downstream_block(self, a):
        set_row_properties_(self.impl,"untwistOutlet",a)
    def get_untwist_downstream_block(self):
        return get_row_properties_(self.impl,"untwistOutlet")
    def set_untwist_upstream_block_stream_location(self, a):
        set_row_properties_(self.impl,"untwistInletStreamLocation",a)
    def get_untwist_upstream_block_stream_location(self):
        return get_row_properties_(self.impl,"untwistInletStreamLocation")
    def set_untwist_downstream_block_stream_location(self, a):
        set_row_properties_(self.impl,"untwistOutletStreamLocation",a)
    def get_untwist_downstream_block_stream_location(self):
        return get_row_properties_(self.impl,"untwistOutletStreamLocation")
    def set_hub_gap_interpolation(self, a):
        set_row_properties_(self.impl,"hubGapInterpolation",a)
    def get_hub_gap_interpolation(self):
        return get_row_properties_(self.impl,"hubGapInterpolation")
    def set_shroud_gap_interpolation(self, a):
        set_row_properties_(self.impl,"shroudGapInterpolation",a)
    def get_shroud_gap_interpolation(self):
        return get_row_properties_(self.impl,"shroudGapInterpolation")
    def set_hub_gap_interpolation_span_location(self, a):
        set_row_properties_(self.impl,"hubGapInterpolationSpanLocation",a)
    def get_hub_gap_interpolation_span_location(self):
        return get_row_properties_(self.impl,"hubGapInterpolationSpanLocation")
    def set_shroud_gap_interpolation_span_location(self, a):
        set_row_properties_(self.impl,"shroudGapInterpolationSpanLocation",a)
    def get_shroud_gap_interpolation_span_location(self):
        return get_row_properties_(self.impl,"shroudGapInterpolationSpanLocation")
    def set_enforce_cell_width_at_blade_wall(self, a):
        set_row_properties_(self.impl,"enforceCellWidthAtBladeWall",a)
    def get_enforce_cell_width_at_blade_wall(self):
        return get_row_properties_(self.impl,"enforceCellWidthAtBladeWall")
    def set_swap_blade_patches_name(self, a):
        set_row_properties_(self.impl,"swapBladePatchesName",a)
    def get_swap_blade_patches_name(self):
        return get_row_properties_(self.impl,"swapBladePatchesName")
    def set_bladeless_mesh(self, a):
        set_row_properties_(self.impl,"bladelessMesh",a)
    def get_bladeless_mesh(self):
        return get_row_properties_(self.impl,"bladelessMesh")

    def get_clustering(self):
        result = get_row_clustering_(self.impl)
        return result[1]
    def set_clustering(self,value):
        set_row_clustering_(self.impl,value)


    def is_acoustic_source(self):
        return get_row_properties_(self.impl,"acousticSource")
    def enable_acoustic_source(self):
        set_row_properties_(self.impl,"acousticSource",1)
    def disable_acoustic_source(self):
        set_row_properties_(self.impl,"acousticSource",0)

    def enable_low_memory_usage(self):
        set_row_properties_(self.impl,"memory_use",1)
    def disable_low_memory_usage(self):
        return set_row_properties_(self.impl,"memory_use",0)
    def get_low_memory_usage(self):
        return get_row_properties_(self.impl,"memory_use")

    def enable_full_mesh_generation(self):
        set_row_properties_(self.impl,"full_mesh","yes")
    def disable_full_mesh_generation(self):
        set_row_properties_(self.impl,"full_mesh","no")
    def get_full_mesh_generation(self):
        return get_row_properties_(self.impl,"full_mesh")

    def set_number_of_meshed_passage(self,value,meshGeneration=0):
        set_row_properties_(self.impl,"fullMeshPy",value,meshGeneration)
    def get_number_of_meshed_passage(self):
        return get_row_properties_(self.impl,"meshed_passages")

    def is_a_tandem_row_with_next(self):
        return set_row_properties_(self.impl,"tandem_row",2)
    def is_a_tandem_row_with_previous(self):
        return set_row_properties_(self.impl,"tandem_row",3)
    def is_not_a_tandem_row(self):
        return set_row_properties_(self.impl,"tandem_row",0)
    def get_is_a_tandem_row(self):
        return get_row_properties_(self.impl,"tandem_row")

    def is_a_rotor(self):
        return 0
    def is_a_stator(self):
        return 0
    def is_a_inducer(self):
        return 0
    def is_a_pump(self):
        return 0
    def is_a_impeller(self):
        return 0
    def is_a_diffuser(self):
        return 0
    def is_a_return_channel(self):
        return 0
    def get_row_type(self):
        return 0

    def get_bypass_location(self):
        return get_row_properties_(self.impl,"bypassLocation") #0:NORMAL, 1:ON_NOZZLE, 2:IN_BYPASS, 3:DOWN_BYPASS

    def is_axial(self):
        return 0
    def is_centrifugal(self):
        return 0
    def get_row_orientation(self):
        return 0

#####################  optimization  Properties ###############
#             optimization  steps
    def set_span_interpolation(self,value):
        set_row_interpolation_spacing_(self.impl,value)
    def get_span_interpolation(self):
        return get_row_interpolation_spacing_(self.impl)
    # old commands kept for backward
    def set_row_interpolation_spacing(self,value):
        set_row_interpolation_spacing_(self.impl,value)
    def get_row_interpolation_spacing(self):
        return get_row_interpolation_spacing_(self.impl)

    def set_row_optimization_steps_in_gap(self,value):
        set_row_optimization_(self.impl,"rowsNumberOfGapOptimizationSteps",value)
    def get_row_optimization_steps_in_gap(self):
        return get_row_optimization_(self.impl,"rowsNumberOfGapOptimizationSteps")
    def set_row_optimization_steps(self,value):
        set_row_optimization_(self.impl,"rowsNumberOfOptimizationSteps",value)
    def get_row_optimization_steps(self):
        return get_row_optimization_(self.impl,"rowsNumberOfOptimizationSteps")
    def set_row_full_multigrid_optimization_steps(self,value):
        set_row_optimization_(self.impl,"fullMultigridOptimization",value)
    def get_row_full_multigrid_optimization_steps(self):
        return get_row_optimization_(self.impl,"fullMultigridOptimization")
    def set_row_bnd_optimization_steps(self,value):
        set_row_optimization_(self.impl,"optimizationBndControl",value)
    def get_row_bnd_optimization_steps(self):
        return get_row_optimization_(self.impl,"optimizationBndControl")
    def get_row_straight_bnd_control(self):
        return get_row_optimization_(self.impl,"straightBndControl")
    # optimization nmb control : 0<=value<=1
    def set_row_straight_bnd_control(self,value):
        set_row_optimization_(self.impl,"straightBndControl",value)
    def get_row_multisplitter_bnd_control(self):
        return get_row_optimization_(self.impl,"multisplitterBndControl")
    def set_row_multisplitter_bnd_control(self):
        set_row_optimization_(self.impl,"multisplitterBndControl")
    def set_row_optimization_freeze_skin_mesh(self,value):
        set_row_optimization_(self.impl,"HOHSkinFixSkin",value)
    def get_row_optimization_freeze_skin_mesh(self):
        return get_row_optimization_(self.impl,"HOHSkinFixSkin")

#             skewness control : value = "yes" or "no" or "medium"
    def set_row_optimization_skewness_control(self,value):
        if type(value) is types.IntType:
            set_row_optimization_(self.impl,"rowsOptimizationType",value)
        else:
            set_row_optimization_(self.impl,"skewnessControl",value)
    def get_row_optimization_type(self):
        return get_row_optimization_(self.impl,"rowsOptimizationType")

#             skewness control in gaps : value = "yes" or "no" or "medium"
    def set_row_optimization_skewness_control_in_gap(self,value):
        if type(value) is types.IntType:
            set_row_optimization_(self.impl,"rowsOptimizationTypeGap",value)
        else:
            set_row_optimization_(self.impl,"skewnessControlgap",value)
    def get_row_optimization_type_in_gap(self):
        return get_row_optimization_(self.impl,"rowsOptimizationTypeGap")

#             orthogonality control : 0 < value < 1
    def set_row_optimization_orthogonality_control(self,value):
        set_row_optimization_(self.impl,"rowsOptimizationLevel",value)
    def get_row_optimization_orthogonality_control(self):
        return get_row_optimization_(self.impl,"rowsOptimizationLevel")

    def set_row_optimization_orthogonality_control_in_gap(self,value):
        set_row_optimization_(self.impl,"rowsOptimizationLevelGap",value)
    def get_row_optimization_orthogonality_control_in_gap(self):
        return get_row_optimization_(self.impl,"rowsOptimizationLevelGap")

#             orthogonality wake control : 0 < value < 1
    def set_row_optimization_wake_control(self,value):
        set_row_optimization_(self.impl,"wakeControlOptimizationLevel",value)
    def get_row_optimization_wake_control(self):
        return get_row_optimization_(self.impl,"wakeControlOptimizationLevel")

#             optimization multigrid control : value "yes" or "no"
    def set_row_optimization_multigrid_control(self,value):
        set_row_optimization_(self.impl,"multigrid",value)
    def get_row_optimization_multigrid_control(self):
        return get_row_optimization_(self.impl,"multigrid")

#             optimization nmb control : 0<=value<=1
    def set_row_optimization_nmb_control(self,value):
        set_row_optimization_(self.impl,"nmb_control",value)
    def get_row_optimization_nmb_control(self):
        return get_row_optimization_(self.impl,"nmb_control")

#####################  Non axi endwall control ###############
#
    # kept for backward
    def unset_non_axisymmetric_hub(self):
        set_row_properties_(self.impl,"axihub",0)
    def unset_non_axisymmetric_hub_repair_damage(self):
        set_row_properties_(self.impl,"axihubrepair",0)
    # end of backward

    def set_non_axisymmetric_hub(self,value=1):
        set_row_properties_(self.impl,"axihub",value)
    def get_non_axisymmetric_hub(self):
        return get_row_properties_(self.impl,"axihub")
    def set_non_axisymmetric_hub_display(self,value):
        set_row_properties_(self.impl,"displayaxihub",value)
    def set_non_axisymmetric_hub_repair_damage(self,value=1):
        set_row_properties_(self.impl,"axihubrepair",value)
    def get_non_axisymmetric_hub_repair_damage(self):
        return get_row_properties_(self.impl,"axihubrepair")

    def set_non_axisymmetric_hub_projection_type_face_normal(self):
        set_row_properties_(self.impl,"axihubprojection",1)
    def get_non_axisymmetric_hub_projection_type_face_normal(self):
        return get_row_properties_(self.impl,"axihubprojection")
    def set_non_axisymmetric_hub_projection_type_spanwise_grid_line(self):
        set_row_properties_(self.impl,"axihubprojection",2)

    def set_non_axisymmetric_hub_repetition(self,value):
        set_row_properties_(self.impl,"axihubrepet",value)
    def get_non_axisymmetric_hub_repetition(self):
        return get_row_properties_(self.impl,"axihubrepet")

    # kept for backward
    def unset_non_axisymmetric_shroud(self):
        set_row_properties_(self.impl,"axishroud",0)
    def unset_non_axisymmetric_shroud_repair_damage(self):
        set_row_properties_(self.impl,"axishroudrepair",0)
    # end of backward

    def set_non_axisymmetric_shroud(self,value=1):
        set_row_properties_(self.impl,"axishroud",value)
    def get_non_axisymmetric_shroud(self):
        return get_row_properties_(self.impl,"axishroud")
    def set_non_axisymmetric_shroud_display(self,value):
        set_row_properties_(self.impl,"displayaxishroud",value)
    def set_non_axisymmetric_shroud_repair_damage(self,value=1):
        set_row_properties_(self.impl,"axishroudrepair",value)
    def get_non_axisymmetric_shroud_repair_damage(self):
        return get_row_properties_(self.impl,"axishroudrepair")

    def set_non_axisymmetric_shroud_projection_type_face_normal(self):
        set_row_properties_(self.impl,"axishroudprojection",1)
    def get_non_axisymmetric_shroud_projection_type_face_normal(self):
        return get_row_properties_(self.impl,"axishroudprojection")
    def set_non_axisymmetric_shroud_projection_type_spanwise_grid_line(self):
        set_row_properties_(self.impl,"axishroudprojection",2)

    def set_non_axisymmetric_shroud_repetition(self,value):
        set_row_properties_(self.impl,"axishroudrepet",value)
    def get_non_axisymmetric_shroud_repetition(self):
        return get_row_properties_(self.impl,"axishroudrepet")

    # kept for backward
    def unset_non_axisymmetric_tip_gap(self):
        set_row_properties_(self.impl,"axitipgap",0)
    def unset_non_axisymmetric_tip_gap_repair_damage(self):
        set_row_properties_(self.impl,"axitipgaprepair",0)
    # end of backward

    def set_non_axisymmetric_tip_gap(self,value=1):
        set_row_properties_(self.impl,"axitipgap",value)
    def get_non_axisymmetric_tip_gap(self):
        return get_row_properties_(self.impl,"axitipgap")
    def set_non_axisymmetric_tip_gap_display(self,value):
        set_row_properties_(self.impl,"displayaxitipgap",value)
    def set_non_axisymmetric_tip_gap_repair_damage(self,value=1):
        set_row_properties_(self.impl,"axitipgaprepair",value)
    def get_non_axisymmetric_tip_gap_repair_damage(self):
        return get_row_properties_(self.impl,"axitipgaprepair")

    def set_non_axisymmetric_tip_gap_repetition(self,value):
        set_row_properties_(self.impl,"axitipgaprepet",value)
    def get_non_axisymmetric_tip_gap_repetition(self):
        return get_row_properties_(self.impl,"axitipgaprepet")

#####################  flow path control ###############
#
    def set_flow_path_control_hub_clustering(self,value):
        set_row_zr_properties_(self.impl,"hubClustering",value)
    def get_flow_path_control_hub_clustering(self):
        return get_row_zr_properties_(self.impl,"hubClustering")
    def set_flow_path_control_shroud_clustering(self,value):
        set_row_zr_properties_(self.impl,"tipClustering",value)
    def get_flow_path_control_shroud_clustering(self):
        return get_row_zr_properties_(self.impl,"tipClustering")
    def set_flow_path_control_cst_cells_number(self,value):
        set_row_zr_properties_(self.impl,"constantCellsNumber",value)
    def get_flow_path_control_cst_cells_number(self):
        return get_row_zr_properties_(self.impl,"constantCellsNumber")
    def set_flow_path_control_control_point_number(self,value):
        set_row_zr_properties_(self.impl,"controlPointsNumber",value)
    def get_flow_path_control_control_point_number(self):
        return get_row_zr_properties_(self.impl,"controlPointsNumber")
    def set_flow_path_control_intermediate_point_number(self,value):
        set_row_zr_properties_(self.impl,"intermediatePointsNumber",value)
    def get_flow_path_control_intermediate_point_number(self):
        return get_row_zr_properties_(self.impl,"intermediatePointsNumber")
    def set_flow_path_control_smoothing_steps(self,value):
        set_row_zr_properties_(self.impl,"smoothingSteps",value)
    def get_flow_path_control_smoothing_steps(self):
        return get_row_zr_properties_(self.impl,"smoothingSteps")
    def set_flow_path_control_distribution_smoothing_steps(self,value):
        set_row_zr_properties_(self.impl,"smoothingStepsDistrib",value)
    def get_flow_path_control_distribution_smoothing_steps(self):
        return get_row_zr_properties_(self.impl,"smoothingStepsDistrib")
#    def set_flow_path_control_hub_distribution_uniform(self):
#        set_row_zr_properties_(self.impl,"hubPointDistribution",0)
#    def set_flow_path_control_hub_distribution_curvature(self):
#        set_row_zr_properties_(self.impl,"hubPointDistribution",2)
#    def get_flow_path_control_hub_distribution(self):
#        return get_row_zr_properties_(self.impl,"hubPointDistribution")
#    def set_flow_path_control_shroud_distribution_same(self):
#        set_row_zr_properties_(self.impl,"shroudPointDistribution",4)
#    def set_flow_path_control_shroud_distribution_projection(self):
#        set_row_zr_properties_(self.impl,"shroudPointDistribution",1)
#    def set_flow_path_control_shroud_distribution_minimal_distance(self):
#        set_row_zr_properties_(self.impl,"shroudPointDistribution",3)
#    def get_flow_path_control_shroud_distribution(self):
#        return get_row_zr_properties_(self.impl,"shroudPointDistribution")

    def get_inlet_flow_path_control_section(self):
        return FlowPathControlSection(get_flow_path_control_section_(self.impl, -1), self)
    def get_outlet_flow_path_control_section(self):
        return FlowPathControlSection(get_flow_path_control_section_(self.impl, -2), self)
    def get_outlet2_flow_path_control_section(self):
        return FlowPathControlSection(get_flow_path_control_section_(self.impl, -3), self)
    def get_z_cst_line_flow_path_control_section(self, index):
        return FlowPathControlSection(get_flow_path_control_section_(self.impl, index-1), self)

#--------------- wizards
    def propeller_wizard(self):
        a = getWindTurbineWizard(self.impl)
        if a !=0 : return RowWizard(a)
        return RowWizard(setWindTurbineWizard(self.impl,1))
    def wind_turbine_wizard(self):
        a = getWindTurbineWizard(self.impl)
        if a !=0 : return RowWizard(a)
        return RowWizard(setWindTurbineWizard(self.impl,0))
    def row_wizard(self):
        a = a5_getRowWizard(self.impl)
        if a !=0 : return RowWizard(a)
    def acoustic_wizard(self):
        return RowAcousticWizard(self.impl)
        
#--------------- ROW CHT MODULE : end wall
    def hub_end_wall(self):
        a = a5_getRowHubEndWall(self.impl)
        if a !=0 : return EndWall(a)
        return self.add_hub_end_wall()
    def shroud_end_wall(self):
        a = a5_getRowShroudEndWall(self.impl)
        if a !=0 : return EndWall(a)
        return self.add_shroud_end_wall()

    def add_hub_end_wall(self):
        return EndWall(a5_setRowHubWall(self.impl))

    def add_shroud_end_wall(self):
        return EndWall(a5_setRowShroudWall(self.impl))

#--------------- automatic blades reference angle

    def initialize_blades_reference_angle(self):
        return calculate_reference_angle_(self.impl,0)

#------------------------------------------------------------------------------------------------

def row(B):                             # indices from 1
    if type(B) is types.StringType:         # assuming name of row is given
        return Row(get_row_by_name_(B))
    elif isinstance(B,Row):
        return B
    else:   return Row(get_row_by_name_(get_row_name_by_index_(B-1)))

#------------------------------------------------------------------------------------------------
#---------------------- ROW SELECTION -----------------------------------------------------------
#------------------------------------------------------------------------------------------------

def select_all_rows():
    select_all_rows_()

def unselect_all_rows():
    unselect_all_rows_()

def select_all():
    select_all_()

def unselect_all():
    unselect_all_()

#------------------------------------------------------------------------------------------------
#---------------              BLADE CONTROL                 -------------------------------------
#------------------------------------------------------------------------------------------------

class Blade(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def delete(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        delete_blade_(parent_row.impl,self.impl)
        self.impl = 0
    def select(self):
        select_(self.impl)
    def add_basin(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Blade(a5_define_basin_(parent_row.impl, self.impl))
    def basin(self):
        return self.add_basin()


    def sheet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return BladeSheet(a5_addBladeSheet(parent_row.impl,self.impl))

    def hub_gap(self):
        return self.add_hub_gap()
    def shroud_gap(self):
        return self.add_shroud_gap()
    def add_hub_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Gap(a5_add_hub_gap_to_blade_(parent_row.impl, self.impl))
    def add_shroud_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Gap(a5_add_shroud_gap_to_blade_(parent_row.impl, self.impl))
    def get_hub_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        gap_pointer = get_blade_gap_(parent_row.impl, self.impl)[0]
        if gap_pointer: return Gap(gap_pointer)
        else: return 0
    def get_shroud_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        gap_pointer = get_blade_gap_(parent_row.impl, self.impl)[1]
        if gap_pointer: return Gap(gap_pointer)
        else: return 0


    def hub_partial_gap(self):
        return self.add_hub_partial_gap()
    def shroud_partial_gap(self):
        return self.add_shroud_partial_gap()
    def add_hub_partial_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return PartialGap(a5_add_hub_partial_gap_to_blade_(parent_row.impl, self.impl))
    def add_shroud_partial_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return PartialGap(a5_add_shroud_partial_gap_to_blade_(parent_row.impl, self.impl))
    def get_hub_partial_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        partial_gap_pointer = get_blade_partial_gap_(parent_row.impl, self.impl)[0]
        if partial_gap_pointer: return PartialGap(partial_gap_pointer)
        else: return 0
    def get_shroud_partial_gap(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        partial_gap_pointer = get_blade_partial_gap_(parent_row.impl, self.impl)[1]
        if partial_gap_pointer: return PartialGap(partial_gap_pointer)
        else: return 0

    def hub_fillet(self):
        return self.add_hub_fillet()
    def shroud_fillet(self):
        return self.add_shroud_fillet()
    def add_hub_fillet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Fillet(a5_add_hub_fillet_to_blade_(parent_row.impl, self.impl))
    def add_shroud_fillet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Fillet(a5_add_shroud_fillet_to_blade_(parent_row.impl, self.impl))
    def get_hub_fillet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        fillet_pointer = get_blade_fillet_(parent_row.impl, self.impl)[0]
        if fillet_pointer: return Fillet(fillet_pointer)
        else: return 0
    def get_shroud_fillet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        fillet_pointer = get_blade_fillet_(parent_row.impl, self.impl)[1]
        if fillet_pointer: return Fillet(fillet_pointer)
        else: return 0

# -------------- Retrieve leading/trailing edge curves

    def get_meridional_leading_edge (self, params=None):
        if params is None:
            params = []
        if type(params) is types.ListType:
            responses = getMeridionalLeadingEdgeCompositePointer(self.parent().impl,self.impl)
            if len(responses) == 3:
                curve = Curve(responses[0])
                params.append(responses[1])
                params.append(responses[2])
                return curve
        return None
    def get_meridional_trailing_edge (self, params=None):
        if params is None:
            params = []
        if type(params) is types.ListType:
            responses = getMeridionalTrailingEdgeCompositePointer(self.parent().impl,self.impl)
            if len(responses) == 3:
                curve = Curve(responses[0])
                params.append(responses[1])
                params.append(responses[2])
                return curve
        return None

    def get_3d_leading_edge (self, params=None):
        if params is None:
            params = []
        if type(params) is types.ListType:
            responses = get3DLeadingEdgeCompositePointer(self.parent().impl,self.impl)
            if len(responses) == 3:
                curve = Curve(responses[0])
                params.append(responses[1])
                params.append(responses[2])
                return curve
        return None
    def get_3d_trailing_edge (self, params=None):
        if params is None:
            params = []
        if type(params) is types.ListType:
            responses = get3DTrailingEdgeCompositePointer(self.parent().impl,self.impl)
            if len(responses) == 3:
                curve = Curve(responses[0])
                params.append(responses[1])
                params.append(responses[2])
                return curve
        return None

#--------------- commands for detecting undulations at leading and trailing edge
    def detect_undulations_LE(self,width,amplitude,debugOutput=0):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        resultList = a5_detect_undulations_(parent_row.impl,self.impl,"LE",width,amplitude,debugOutput)
        if not resultList: return []
        finalList  = []
        for p in range(0, len(resultList)):
            finalList.append([resultList[p][0], resultList[p][1], Point(resultList[p][2],resultList[p][3],resultList[p][4])])
        return finalList

    def detect_undulations_TE(self,width,amplitude,debugOutput=0):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        resultList = a5_detect_undulations_(parent_row.impl,self.impl,"TE",width,amplitude,debugOutput)
        if not resultList: return []
        finalList  = []
        for p in range(0, len(resultList)):
            finalList.append([resultList[p][0], resultList[p][1], Point(resultList[p][2],resultList[p][3],resultList[p][4])])
        return finalList

#--------------- wizard le te
    def wizard_le_te(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a = getWizardLETE(parent_row.impl,self.impl)
        if a !=0 : return WizardLETE(a)
        return WizardLETE(setWizardLETE(parent_row.impl,self.impl))
#       -------------- CHT MODULE

    def generate_holes(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_generateHoles(parent_row.impl,self.impl)

    def number_of_holes_lines(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfHoles(parent_row.impl, self.impl)
    def add_holes_line(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return HolesLine(a5_addHoles(parent_row.impl, self.impl))
    def holes_line(self,i):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return HolesLine(a5_getHolesPointer(parent_row.impl,self.impl,a5_getHolesNameByIndex(parent_row.impl,self.impl,i-1)))

#       --- add pin fins channel box:
    def add_pin_fins_channel(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return PinFinsChannel(a5_addInnerPinFinsChannel(parent_row.impl,self.impl))

#       --- solid body configuration type:
#           0: disable solid body mesh generation
#           1: basin+cooling channel
#           2: basin
#           3: cooling channel
#           4: radial holes without basin and without cooling channel
#           5: solid body alone
#           6: cooling channel without tip wall (gtre backward)
#           7: pennies at hub
#           8: pennies at shroud
#           9: pennies at hub&shroud
#           10: squiller tip on lower side
#           11: squiller tip on upper side
#           12: squiller tip on camber line

    def set_solid_body_configuration(self,type):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_setBladeSolidBodyConfiguration(parent_row.impl, self.impl,type)
    def get_solid_body_configuration(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_getBladeSolidBodyConfiguration(parent_row.impl, self.impl)
    def solid_body(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return Blade(get_blade_cooling_(parent_row.impl, self.impl))
    def cooling_channel(self):
        parent_blade = Blade(get_parent_blade(self.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return CoolingChannel(getBladeCoolingChannel(parent_row.impl,parent_blade.impl, self.impl))

#       parametric definition of the basin or cooling channel shape
    def is_solid_body_parametric(self):
        return a5_getCoolingParameters(self.impl,"parametricDefinition")
    def enable_solid_body_parametric_definition(self):
        return a5_setCoolingParameters(self.impl,"parametricDefinition",1)
    def disable_solid_body_parametric_definition(self):
        return a5_setCoolingParameters(self.impl,"parametricDefinition",0)
    def get_solid_body_shape_blunt_trailing_edge(self):
        return a5_getCoolingParameters(self.impl,"bluntTrailingEdge")
    def enable_solid_body_shape_blunt_trailing_edge(self):
        return a5_setCoolingParameters(self.impl,"bluntTrailingEdge",1)
    def disable_solid_body_shape_blunt_trailing_edge(self):
        return a5_setCoolingParameters(self.impl,"bluntTrailingEdge",0)
    def get_solid_body_shape_number_of_control_points(self):
        return a5_getCoolingParameters(self.impl,"numberOfControlPoints")
    def set_solid_body_shape_number_of_control_points(self,value):
        return a5_setCoolingParameters(self.impl,"numberOfControlPoints",value)
    def get_solid_body_shape_start_location(self):
        return a5_getCoolingParameters(self.impl,"startLocationPercentageOfChordLenght")
    def set_solid_body_shape_start_location(self,value):
        return a5_setCoolingParameters(self.impl,"startLocationPercentageOfChordLenght",value)
    def get_solid_body_shape_end_location(self):
        return a5_getCoolingParameters(self.impl,"endLocationPercentageOfChordLenght")
    def set_solid_body_shape_end_location(self,value):
        return a5_setCoolingParameters(self.impl,"endLocationPercentageOfChordLenght",value)
    def get_solid_body_shape_start_width(self):
        return a5_getCoolingParameters(self.impl,"startWidthPercentageOfBladeWidth")
    def set_solid_body_shape_start_width(self,value):
        return a5_setCoolingParameters(self.impl,"startWidthPercentageOfBladeWidth",value)
    def get_solid_body_shape_middle_width(self):
        return a5_getCoolingParameters(self.impl,"middleWidthPercentageOfBladeWidth")
    def set_solid_body_shape_middle_width(self,value):
        return a5_setCoolingParameters(self.impl,"middleWidthPercentageOfBladeWidth",value)
    def get_solid_body_shape_end_width(self):
        return a5_getCoolingParameters(self.impl,"endWidthPercentageOfBladeWidth")
    def set_solid_body_shape_end_width(self,value):
        return a5_setCoolingParameters(self.impl,"endWidthPercentageOfBladeWidth",value)
#       external definition of the basin or cooling channel shape
    def set_solid_body_geometry_from_geomTurbo_file(self,value):
        return a5_defineSolidBodyInternalGeometry(self.impl,value,1)

#       mesh topology control in the cht area
#       type of distribution along solid body shape in blade to blade view
#       0: same as blade distribution
#       1: adapted at the blade trailing edge
    def get_solid_body_streamwise_distribution_type(self):
        return a5_getCoolingParameters(self.impl,"streamdistrib")
    def set_solid_body_streamwise_distribution_type_same_as_blade(self):
        a5_setCoolingParameters(self.impl,"streamdistrib",2)
    def set_solid_body_streamwise_distribution_type_adapted(self):
        a5_setCoolingParameters(self.impl,"streamdistrib",1)
    def get_solid_body_number_of_points_azimutal(self):
        return a5_getCoolingParameters(self.impl,"HOHSkinNBndLayerGap2")
    def set_solid_body_number_of_points_azimutal(self,value):
        a5_setCoolingParameters(self.impl,"HOHSkinNBndLayerGap2",value)
    def get_solid_body_B2B_mesh_relaxation(self):
        return a5_getCoolingParameters(self.impl,"solidBodyMeshRelaxation")
    def set_solid_body_B2B_mesh_relaxation(self,value):
        a5_setCoolingParameters(self.impl,"solidBodyMeshRelaxation",value)
    def get_solid_body_keep_blade_solid_mesh(self):
        return a5_getCoolingParameters(self.impl,"keep_blade_cht_mesh")
    def set_solid_body_keep_blade_solid_mesh(self,value):
        a5_setCoolingParameters(self.impl,"keep_blade_cht_mesh",value)
    def get_solid_body_keep_mesh_around_skin(self):
        return a5_getCoolingParameters(self.impl,"keep_blading_mesh")
    def set_solid_body_keep_mesh_around_skin(self,value):
        a5_setCoolingParameters(self.impl,"keep_blading_mesh",value)
    def get_solid_body_keep_mesh_in_cooling_channel(self):
        return a5_getCoolingParameters(self.impl,"keep_cooling_mesh")
    def set_solid_body_keep_mesh_in_cooling_channel(self,value):
        a5_setCoolingParameters(self.impl,"keep_cooling_mesh",value)
    def get_solid_body_keep_skin_mesh(self):
        return a5_getCoolingParameters(self.impl,"keep_skin_mesh")
    def set_solid_body_keep_skin_mesh(self,value):
        a5_setCoolingParameters(self.impl,"keep_skin_mesh",value)

#       basin holes definition applied to solid body instance

    def number_of_basin_holes(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfBassinHoles(parent_row.impl, self.impl)
    def add_basin_hole(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return BasinHole(a5_addBassinHoles(parent_row.impl, self.impl))
    def basin_hole(self,i):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return BasinHole(a5_getBassinHolesPointer(parent_row.impl,self.impl,a5_getBassinHolesNameByIndex(parent_row.impl,self.impl,i-1)))
    def init_basin_holes_from_external_file(self,filename):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_setbassinholesGeometryFromFile(parent_row.impl,self.impl,filename)
    def export_basin_holes_geometry(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_exportbassinholesGeometry(parent_row.impl,self.impl,0)
    def export_basin_holes_definition(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_exportbassinholesGeometry(parent_row.impl,self.impl,1)

#       basin separator definition applied to solid body instance

    def number_of_basin_separators(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfBassinSeparators(parent_row.impl, self.impl)
    def add_basin_separator(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return BasinHole(a5_addBassinSeparator(parent_row.impl, self.impl))
    def basin_separator(self,i):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return BasinHole(a5_getBassinSeparatorPointer(parent_row.impl,self.impl,a5_getBassinSeparatorNameByIndex(parent_row.impl,self.impl,i-1)))


#       -------------- end CHT MODULE


    def get_name(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_blade_name_(parent_row.impl, self.impl)
    def set_name(self,name):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return set_blade_name_(parent_row.impl, self.impl,name)

    def zoom_at_leading_edge(self,level):
        a5_zoom_at_leading_edge_(self.impl,level)
    def zoom_at_trailing_edge(self,level):
        a5_zoom_at_trailing_edge_(self.impl,level)

    def leadingEdgeControl(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return StagnationPoint(get_leading_edge_control_(parent_row.impl,self.impl))
    def trailingEdgeControl(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return StagnationPoint(get_trailing_edge_control_(parent_row.impl,self.impl))


    def load_geometry(self,name):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_import_geomTurbo_file_for_blade_(parent_row.impl,self.impl,name,1)
    def export_geometry(self,useflowpath,numsections,ninlet,nblade,noutlet,ncst,leadwidth,trailwidth,exportendwall):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_exportBladeGeomTurboFile(self.impl,useflowpath,numsections,ninlet,nblade,noutlet,ncst,leadwidth,trailwidth,exportendwall,0)

    def link_geometry(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_blade_(self.impl, surface_pointers)

    def link_pressure(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_pressure_(self.impl, surface_pointers)

    def link_suction(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_suction_(self.impl, surface_pointers)

    def link_to_leading_edge(self,curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_leading_edge_(self.impl, curve_pointers)

    def link_to_trailing_edge(self,curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_trailing_edge_(self.impl, curve_pointers)

    def link_to_hub_gap(self,curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_gap_(self.impl, 0, curve_pointers)

    def link_to_shroud_gap(self,curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_gap_(self.impl, 1, curve_pointers)

    def link_to_hub_fillet(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_fillet_(self.impl, 0, surface_pointers)

    def link_to_shroud_fillet(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_fillet_(self.impl, 1, surface_pointers)

#------------------------------------------------------------------------------------------------
#---------------              BLADE GEOMETRY CHECK        -------------------------------------
#------------------------------------------------------------------------------------------------

    def set_geometry_data_reduction_distance_criteria(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"distanceCriteria",a)

    # angle is to be given in degrees
    def set_geometry_data_reduction_angle_criteria(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"angleCriteria",a)

    def set_geometry_data_reduction(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"dataReduction",a)

    def set_geometry_control_points_redistribution(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsRedistribution",a)

    def set_geometry_control_points_redistribution_npts_at_le(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberAtLE",a)

    def set_geometry_control_points_redistribution_npts_on_middle(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberOnMiddle",a)
    def set_geometry_control_points_redistribution_cst_cells_on_middle(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"constCellsNumberOnMiddle",a)

    def set_geometry_control_points_redistribution_npts_at_te(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberAtTE",a)

    def set_geometry_control_points_redistribution_spacing_at_le(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsSpacingAtLE",a)

    def set_geometry_control_points_redistribution_spacing_at_te(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"controlPointsSpacingAtTE",a)

    def set_geometry_sewing_tolerance(self,a):
      set_blade_geometry_check_parameter_by_name(self.impl,"sewingTolerance",a)


    def get_geometry_data_reduction_distance_criteria(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"distanceCriteria")

    # angle is returned in degrees
    def get_geometry_data_reduction_angle_criteria(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"angleCriteria")

    def get_geometry_data_reduction(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"dataReduction")

    def get_geometry_control_points_redistribution(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsRedistribution")

    def get_geometry_control_points_redistribution_npts_at_le(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberAtLE")

    def get_geometry_control_points_redistribution_npts_on_middle(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberOnMiddle")
    def get_geometry_control_points_redistribution_cst_cells_on_middle(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"constCellsNumberOnMiddle")

    def get_geometry_control_points_redistribution_npts_at_te(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsNumberAtTE")

    def get_geometry_control_points_redistribution_spacing_at_le(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsSpacingAtLE")

    def get_geometry_control_points_redistribution_spacing_at_te(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"controlPointsSpacingAtTE")

    def get_geometry_sewing_tolerance(self):
      return get_blade_geometry_check_parameter_by_name(self.impl,"sewingTolerance")

    # returns a list containing:
    # 1) a1 = minimum distance
    # 2) a2 = maximum angular deviation
    def check_geometry(self):
      return set_blade_geometry_check(self.impl)
    # returns 1 if update has been performed, 0 otherwise.
    def apply_data_reduction(self):
      return apply_blade_geometry_data_reduction(self.impl)

#------------------------------------------------------------------------------------------------
#---------------              BLADE DUPLICATION CONTROL        -------------------------------------
#------------------------------------------------------------------------------------------------

    def compute_default_blade_rotation_axis(self,location):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        unselect_all()
        self.select()
        a5_computeDefaultBladeAxis(parent_row.impl,self.impl,location)
    def duplicate(self,Zangle,bladeAngle,numRepet=1,*args):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationNumber"        ,numRepet)
        a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationZAngle"        ,Zangle)
        a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAngle"    ,bladeAngle)
        if len(args) == 2:
            orig = args[0]
            vec  = args[1]
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisPtX"  ,orig.x)
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisPtY"  ,orig.y)
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisPtZ"  ,orig.z)
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisX"    ,vec.x)
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisY"    ,vec.y)
            a5_setBladeDuplication(parent_row.impl,self.impl,"duplicationBladeAxisZ"    ,vec.z)
        a5_applyBladeDuplication(parent_row.impl,self.impl)

#    Set blade properties
#-----------------------
# stitch surfaces:
# 0 : none
# 1 : inverse lofting
# 2 : lofting with guide

    def set_stitch_surfaces_at_LE_TE(self,option):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        if   option == 0:
            optionString = "None"
        elif option == 1:
            optionString = "Inverse lofting"
        elif option == 2:
            optionString = "Lofting with guide"
        else:
            raise ValueError,'invalid option for set_stitch_surfaces_at_LE_TE'
        setBladeProperties(parent_row.impl,self.impl,"surfacesStitching",optionString)

    def get_stitch_surfaces_at_LE_TE(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        results = getBladeProperties(parent_row.impl, self.impl)
        inverseLofting   = results[17]
        loftingWithGuide = results[18]
        if inverseLofting != 0 and loftingWithGuide != 0:
            raise ValueError,'get_stitch_surfaces_at_LE_TE'
        elif inverseLofting != 0:
            return 1
        elif loftingWithGuide != 0:
            return 2
        return 0

#------------------------------------------------------------------------------------------------
#---------------              BLADE ROTATION CONTROL                 -------------------------------------
#------------------------------------------------------------------------------------------------

    def apply_rotation(self,x,y,z,vx,vy,vz,angle):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        V = `vx`+" "+`vy`+" "+`vz`
        X = `x`+" "+`y`+" "+`z`
        setBladeRotationProperties(parent_row.impl,self.impl,1,V,X,angle,0,0)

#------------------------------------------------------------------------------------------------
#---------------              BLADE EXPANSION CONTROL                 -------------------------------------
#------------------------------------------------------------------------------------------------

    def expand_at_hub(self, expansion_factor=0, extent_offset=0):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_blade_treatment_properties_(parent_row.impl,self.impl,[0,1,expansion_factor,0,0,0,extent_offset])

    def expand_at_shroud(self, expansion_factor=0, extent_offset=0):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_blade_treatment_properties_(parent_row.impl,self.impl,[1,1,expansion_factor,0,0,0,extent_offset,0])

# treatmentType:
# 0 : no expansion
# 1 : expansion
# 2 : treat blend
# 3 : treat blend with offset
# 4 : cut fillet
# 5 : section extension (only shroud)

    def set_expansion_treatment(self, location, treatmentType, args):
        parent_row = self.parent()
        if parent_row == 0 : return 0

        if treatmentType == 0 or treatmentType == 4:
            set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,0,0,0,0,0,0])
        elif treatmentType == 1:
            if len(args) == 1:
                results = getBladeProperties(parent_row.impl, self.impl)
                if location == 1:
                    expansionOffset = results[15]
                else:
                    expansionOffset = results[10]
                set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,args[0],0,0,0,expansionOffset,0])
            elif len(args) == 2:
                set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,args[0],0,0,0,args[1],0])
            elif len(args) == 0:
                results = getBladeProperties(parent_row.impl, self.impl)
                if location == 1:
                    expansionFactor = results[11]
                    expansionOffset = results[15]
                else:
                    expansionFactor = results[6]
                    expansionOffset = results[10]
                set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,expansionFactor,0,0,0,expansionOffset,0])
            else:
                return 0
        elif treatmentType == 2:
            if len(args) != 3: return 0
            set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,0,args[0],args[1],0,args[2],0])
        elif treatmentType == 3:
            if len(args) != 2: return 0
            set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,0,0,0,args[0],args[1],0])
        elif treatmentType == 5:
            if len(args) != 1 or location == 0: return 0
            set_blade_treatment_properties_(parent_row.impl,self.impl,[location,treatmentType,0,0,0,0,0,args[0]])
        else: return 0
        return 1

    def set_shroud_treatment(self, treatmentType, *args):
        if not self.set_expansion_treatment(1, treatmentType, args):
            raise ValueError,"set_shroud_treatment: wrong input"

    def set_hub_treatment(self, treatmentType, *args):
        if not self.set_expansion_treatment(0, treatmentType, args):
            raise ValueError,"set_hub_treatment: wrong input"

    def get_shroud_treatment(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        results = getBladeProperties(parent_row.impl, self.impl)
        treatmentType = results[4]

        if treatmentType == 0 or treatmentType == 4:
            return [treatmentType]
        elif treatmentType == 1:
            geomTurboCAD = results[5]
            expansionFactor = results[11]
            expansionOffset = results[15]
            if geomTurboCAD == 0: return treatmentType, expansionFactor
            else: return treatmentType, expansionFactor, expansionOffset
        elif treatmentType == 2:
            radius          = results[12]
            minimumAngle    = results[13]
            extensionOffset = results[15]
            return treatmentType, radius, minimumAngle, extensionOffset
        elif treatmentType == 3:
            cutOffset       = results[14]
            extensionOffset = results[15]
            return treatmentType, cutOffset, extensionOffset
        elif treatmentType == 5:
            spanCutPercentage = results[16]
            return treatmentType, spanCutPercentage
        else: return 0

    def get_hub_treatment(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        results = getBladeProperties(parent_row.impl, self.impl)
        treatmentType = results[3]

        if treatmentType == 0 or treatmentType == 4:
            return [treatmentType]
        elif treatmentType == 1:
            geomTurboCAD = results[5]
            expansionFactor = results[6]
            expansionOffset = results[10]
            if geomTurboCAD == 0: return treatmentType, expansionFactor
            else: return treatmentType, expansionFactor, expansionOffset
        elif treatmentType == 2:
            radius          = results[7]
            minimumAngle    = results[8]
            extensionOffset = results[10]
            return treatmentType, radius, minimumAngle, extensionOffset
        elif treatmentType == 3:
            cutOffset       = results[9]
            extensionOffset = results[10]
            return treatmentType, cutOffset, extensionOffset
        else: return 0

#------------------------------------------------------------------------------------------------
#---------------              BLUNT TREATMENT                 -------------------------------------
#------------------------------------------------------------------------------------------------

    # kept for backward
    def unset_blunt_treatment_at_leading_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtLead",0)
    def unset_blunt_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtTrail",0)
   # end of backward

    def set_blunt_treatment_at_leading_edge(self,value=1):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtLead",value)
    def set_blunt_treatment_at_trailing_edge(self,value=1):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtTrail",value)
    def get_blunt_treatment_at_leading_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtLead")
    def get_blunt_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"bluntAtTrail")


#------------------------------------------------------------------------------------------------
#---------------              SHARP TREATMENT                 -------------------------------------
#------------------------------------------------------------------------------------------------

    # kept for backward
    def unset_sharp_treatment_at_leading_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtLeadingEdge",0)
    def unset_sharp_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtTrailingEdge",0)
    # end of backward

    def set_sharp_treatment_at_leading_edge(self,value=1):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtLeadingEdge",value)
    def set_sharp_treatment_at_trailing_edge(self,value=1):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtTrailingEdge",value)
    def get_sharp_treatment_at_leading_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtLeadingEdge")
    def get_sharp_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"isSharpAtTrailingEdge")


#------------------------------------------------------------------------------------------------
#---------------              ROUNDED TREATMENT               -------------------------------------
#------------------------------------------------------------------------------------------------

    # kept for backward
    def unset_rounded_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"blentTreatmentAtTrailingEdge",0)
    # end of backward

    def set_rounded_treatment_at_trailing_edge(self,value=1):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"blentTreatmentAtTrailingEdge",value)
    def get_rounded_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"blentTreatmentAtTrailingEdge")

#------------------------------------------------------------------------------------------------
#---------------              BLEND TREATMENT               -------------------------------------
#------------------------------------------------------------------------------------------------

    def set_blend_treatment_at_trailing_edge(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"blentAtTrailingEdge",value)
    def get_blend_treatment_at_trailing_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"blentAtTrailingEdge")

    def set_blend_treatment_at_leading_edge(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"blentAtLeadingEdge",value)
    def get_blend_treatment_at_leading_edge(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"blentAtLeadingEdge")

#------------------------------------------------------------------------------------------------
#---------------              BLADE TO BLADE MESH CONTROL                 -------------------------------------
#------------------------------------------------------------------------------------------------
#---------------------------------
# blade to blade control dialog box
#---------------------------------
    def copy_topology(self):
        a5_copy_topology_(self.impl,"0")

    def paste_topology(self):
        a5_paste_topology_(self.impl,"0")

# global topology control
#       topology type value : 0 (default) 1 (hoh) 2 (user defined)
    def set_b2b_topology_type(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"type",value)
    def get_b2b_topology_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"type")

###----------------
#  default topology
###----------------

#    topology control
#--------------------
#       default topology type : 0 (streamwise) 1 (rounded azimuthal) 2 (rounded streamwise)
    def set_b2b_default_topology_type(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"defaultType",value)
    def get_b2b_default_topology_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"defaultType")


#       default topology periodicity type : 0 (non matching periodicity) 1 (matching periodicity)

    def set_b2b_default_topology_periodicity_type(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinPeriodicMatching",value)
    def get_b2b_default_topology_periodicity_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinPeriodicMatching")

#       high staggered blade optimization

    def set_b2b_default_topology_enable_high_staggered_optimization(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinStaggeredTopology",1)
    def set_b2b_default_topology_disable_high_staggered_optimization(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinStaggeredTopology",0)
    def get_b2b_default_topology_high_staggered_optimization(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinStaggeredTopology")

#       high staggered blade detection

    def set_b2b_default_topology_disable_high_staggered_detection(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"automaticDetection",0)
    def set_b2b_default_topology_enable_high_staggered_detection(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"automaticDetection",1)
    def get_b2b_default_topology_high_staggered_detection(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"automaticDetection")

#       high staggered blade manual type setting
#       inlet
    def set_b2b_default_topology_normal_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"inletType",0)
    def set_b2b_default_topology_low_staggered_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"inletType",1)
    def set_b2b_default_topology_high_staggered_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"inletType",2)
    def get_b2b_default_topology_inlet_staggered_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"inletType")
#       throat control
    def set_b2b_default_topology_throat_control(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"numberOfPointsInThroat",value)
    def set_b2b_default_topology_throat_projection_type(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"throatProjection",value)
    def set_b2b_default_topology_throat_projection_inlet_relaxation(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"inletRelaxationLevel",value)
    def set_b2b_default_topology_throat_projection_outlet_relaxation(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"outletRelaxationLevel",value)

    def get_b2b_default_topology_throat_control(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"numberOfPointsInThroat")
    def get_b2b_default_topology_throat_projection_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"throatProjection")
    def get_b2b_default_topology_throat_projection_inlet_relaxation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"inletRelaxationLevel")
    def get_b2b_default_topology_throat_projection_outlet_relaxation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"outletRelaxationLevel")
#       outlet
    def set_b2b_default_topology_normal_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"outletType",0)
    def set_b2b_default_topology_low_staggered_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"outletType",1)
    def set_b2b_default_topology_high_staggered_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"outletType",2)
    def get_b2b_default_topology_outlet_staggered_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"outletType")

#    grid points control
#-----------------------
#
    def set_b2b_default_topology_grid_point_number_azimutal_inlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInlet",value)
    def set_b2b_default_topology_grid_point_number_azimutal_outlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutlet",value)
    def set_b2b_default_topology_grid_point_number_azimutal_inlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInletUp",value)
    def set_b2b_default_topology_grid_point_number_azimutal_outlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutletUp",value)
    def set_b2b_default_topology_grid_point_number_azimutal_inlet_down(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInletDown",value)
    def set_b2b_default_topology_grid_point_number_azimutal_outlet_down(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutletDown",value)
    def set_b2b_default_topology_grid_point_number_streamwise_inlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrInlet",value)
    def set_b2b_default_topology_grid_point_number_streamwise_outlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrOutlet",value)
    def set_b2b_default_topology_grid_point_number_streamwise_blade_upper_side(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrBladeUp",value)
    def set_b2b_default_topology_grid_point_number_streamwise_blade_lower_side(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrBladeDown",value)
    def set_b2b_default_topology_grid_point_number_in_boundary_layer(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNBndLayer",value)
    def set_b2b_default_topology_grid_point_number_in_boundary_layer_of_gaps(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNBndLayerGap",value)
    def set_b2b_default_topology_grid_point_number_leading_edge_index(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"streamwiseIndexLEDefault",value)
    def set_b2b_default_topology_grid_point_number_trailing_edge_index(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"streamwiseIndexTEDefault",value)

    def get_b2b_default_topology_grid_point_number_azimutal_inlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInlet")
    def get_b2b_default_topology_grid_point_number_azimutal_outlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutlet")
    def get_b2b_default_topology_grid_point_number_azimutal_inlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInletUp")
    def get_b2b_default_topology_grid_point_number_azimutal_outlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutletUp")
    def get_b2b_default_topology_grid_point_number_azimutal_inlet_down(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNInletDown")
    def get_b2b_default_topology_grid_point_number_azimutal_outlet_down(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNOutletDown")
    def get_b2b_default_topology_grid_point_number_streamwise_inlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrInlet")
    def get_b2b_default_topology_grid_point_number_streamwise_outlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrOutlet")
    def get_b2b_default_topology_grid_point_number_streamwise_blade_upper_side(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrBladeUp")
    def get_b2b_default_topology_grid_point_number_streamwise_blade_lower_side(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNStrBladeDown")
    def get_b2b_default_topology_grid_point_number_in_boundary_layer(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNBndLayer")
    def get_b2b_default_topology_grid_point_number_in_boundary_layer_of_gaps(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinNBndLayerGap")
    def get_b2b_default_topology_grid_point_number_leading_edge_index(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"streamwiseIndexLEDefault")
    def get_b2b_default_topology_grid_point_number_trailing_edge_index(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"streamwiseIndexTEDefault")

#    Mesh control
#-----------------------
#
    def set_b2b_default_topology_cell_width_at_wall(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClustering",value)
    def set_b2b_default_topology_cell_width_at_wall_at_hub(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringHub",value)
    def set_b2b_default_topology_cell_width_at_wall_at_shroud(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringShroud",value)
    def set_b2b_default_topology_bnd_layer_width(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringWidth",value)
    def set_b2b_default_topology_cell_width_at_wall_interpolation(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringInterpolation",value)
    def set_b2b_default_topology_cell_width_at_trailing_edge(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"trailingEdgeClustering",value)
    def set_b2b_default_topology_cell_width_at_leading_edge(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"leadingEdgeClustering",value)
    def set_b2b_default_topology_expansion_ratio_in_bnd_layer(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinExpansionRatio",value)
    def set_b2b_default_topology_skin_block_expansion_ratio_control(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"skinNBndLayerMaxExpRatio",value)
    def set_b2b_default_topology_free_outlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFreeOutlet",value)
    def set_b2b_default_topology_free_inlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFreeInlet",value)
    def set_b2b_default_topology_fix_outlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixOutlet",value)
    def set_b2b_default_topology_fix_inlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixInlet",value)
    def set_b2b_default_topology_fix_outlet_mesh(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixOutletMesh",value)
    def set_b2b_default_topology_fix_inlet_mesh(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixInletMesh",value)
    def set_b2b_default_topology_outlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinOutletAngleRef",value)
    def set_b2b_default_topology_inlet_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinInletAngleRef",value)
    def set_b2b_default_topology_enable_wake_control(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"wakeControl",1)
    def set_b2b_default_topology_disable_wake_control(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"wakeControl",0)
    def set_b2b_default_topology_enable_wake_prolongation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"wakeProlongation",1)
    def set_b2b_default_topology_wake_control_prolongation(self, value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"wakeProlongation", value)
    def set_b2b_default_topology_enable_leading_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtLeadingEdge",1)
    def set_b2b_default_topology_disable_leading_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtLeadingEdge",0)
    def get_b2b_default_topology_leading_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtLeadingEdge")
    def set_b2b_default_topology_enable_trailing_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtTrailingEdge",1)
    def set_b2b_default_topology_disable_trailing_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtTrailingEdge",0)
    def get_b2b_default_topology_trailing_edge_zcstline(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinZCstLineAtTrailingEdge")
    def set_b2b_default_topology_wake_control_deviation_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"wakeDeviation",value)
    def set_b2b_default_topology_chord_control_points_number(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"chordNumberOfPoints",value)

    def get_b2b_default_topology_cell_width_at_wall(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClustering")
    def get_b2b_default_topology_cell_width_at_wall_at_hub(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringHub")
    def get_b2b_default_topology_cell_width_at_wall_at_shroud(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringShroud")
    def get_b2b_default_topology_bnd_layer_width(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringWidth")
    def get_b2b_default_topology_cell_width_at_wall_interpolation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClusteringInterpolation")
    def get_b2b_default_topology_expansion_ratio_in_bnd_layer(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinExpansionRatio")
    def get_b2b_default_topology_skin_block_expansion_ratio_control(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"skinNBndLayerMaxExpRatio")
    def get_b2b_default_topology_free_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFreeOutlet")
    def get_b2b_default_topology_free_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFreeInlet")
    def get_b2b_default_topology_fix_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixOutlet")
    def get_b2b_default_topology_fix_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixInlet")
    def get_b2b_default_topology_fix_outlet_mesh(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixOutletMesh")
    def get_b2b_default_topology_fix_inlet_mesh(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinFixInletMesh")
    def get_b2b_default_topology_outlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinOutletAngleRef")
    def get_b2b_default_topology_inlet_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinInletAngleRef")
    def get_b2b_default_topology_wake_control(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"wakeControl")
    def get_b2b_default_topology_wake_control_prolongation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"wakeProlongation")
    def get_b2b_default_topology_wake_control_deviation_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"wakeDeviation")
    def get_b2b_default_topology_chord_control_points_number(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"chordNumberOfPoints")

#    Intersection control
#-----------------------
#
#       intersection level: 0 (low) 1 (high)
    def set_b2b_default_topology_intersection_quality(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"intersectionType",value)
    def get_b2b_default_topology_intersection_quality(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"intersectionType")
#       intersection law: 0 (Curvature) 1 (Uniform)
    def set_b2b_default_topology_intersection_law(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"intersectionLaw",value)
    def get_b2b_default_topology_intersection_law(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"intersectionLaw")
#       intersection points number (only if intersection law set up to uniform && low quality level)
    def set_b2b_default_topology_intersection_control_point_number(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"intersectionNpts",value)
    def get_b2b_default_topology_intersection_control_point_number(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"intersectionNpts")
#       intersection check ratio
    def set_b2b_intersection_precision_check_ratio(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"intersectionCheckRatio",value)
    def get_b2b_intersection_precision_check_ratio(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"intersectionCheckRatio")
#       blade reference angle (radian)
    def set_b2b_blade_reference_angle(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"thetaRef",value)
    def get_b2b_blade_reference_angle(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"thetaRef")

###----------------
#  HOH topology
###----------------

#    topology control
#--------------------
#       inlet extension block : 0 (no extension block) 1 (extension block)
    def set_b2b_hoh_topology_enable_inlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInlet",1)
    def set_b2b_hoh_topology_disable_inlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInlet",0)
    def get_b2b_hoh_topology_inlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInlet")
#       outlet extension block : 0 (no extension block) 1 (extension block)
    def set_b2b_hoh_topology_enable_outlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutlet",1)
    def set_b2b_hoh_topology_disable_outlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutlet",0)
    def get_b2b_hoh_topology_outlet_extension(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutlet")
#       inlet extension type : 0 (H) 1 (I)
    def set_b2b_hoh_topology_inlet_I_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletType",1)
    def set_b2b_hoh_topology_inlet_H_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletType",2)
    def get_b2b_hoh_topology_inlet_H_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletType")
#       outlet extension type : 0 (H) 1 (I)
    def set_b2b_hoh_topology_outlet_I_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletType",1)
    def set_b2b_hoh_topology_outlet_H_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletType",2)
    def get_b2b_hoh_topology_outlet_H_extension_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletType")
#       inlet extension location
    def set_b2b_hoh_topology_inlet_extension_location(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletPos",value)
    def get_b2b_hoh_topology_inlet_extension_location(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletPos")
#       outlet extension location
    def set_b2b_hoh_topology_outlet_extension_location(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletPos",value)
    def get_b2b_hoh_topology_outlet_extension_location(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletPos")

#    grid point control
#--------------------
#       inlet extension block : streamwise number of points
    def set_b2b_hoh_topology_inlet_extension_streamwise_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletNpt",value)
    def get_b2b_hoh_topology_inlet_extension_streamwise_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshInletNpt")
#       inlet extension block : streamwise number of points
    def set_b2b_hoh_topology_outlet_extension_streamwise_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletNpt",value)
    def get_b2b_hoh_topology_outlet_extension_streamwise_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHMeshOutletNpt")
#       O block : number of points in the boundary layer
    def set_b2b_hoh_topology_npts_in_boundary_layer(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHAzimutalNpts1",value)
    def get_b2b_hoh_topology_npts_in_boundary_layer(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHAzimutalNpts1")
#       O block : number of points around the boundary layer
    def set_b2b_hoh_topology_npts_around_boundary_layer(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHAzimutalNpts2",value)
    def get_b2b_hoh_topology_npts_around_boundary_layer(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHAzimutalNpts2")

#       pressure and suction side grid points number
    def set_b2b_hoh_topology_suction_and_pressure_side_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt1",value)
    def get_b2b_hoh_topology_suction_and_pressure_side_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt1")

#       inlet azimuthal grid points number
    def set_b2b_hoh_topology_H_inlet_azimuthal_npts_1(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt2",value)
    def set_b2b_hoh_topology_H_inlet_azimuthal_npts_2(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt8",value)
    def set_b2b_hoh_topology_H_inlet_azimuthal_npts_3(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt7",value)
    def set_b2b_hoh_topology_I_inlet_azimuthal_npts  (self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt2",value)
    def get_b2b_hoh_topology_H_inlet_azimuthal_npts_1(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt2")
    def get_b2b_hoh_topology_H_inlet_azimuthal_npts_2(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt8")
    def get_b2b_hoh_topology_H_inlet_azimuthal_npts_3(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt7")
    def get_b2b_hoh_topology_I_inlet_azimuthal_npts  (self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt2")
#       outlet azimuthal grid points number
    def set_b2b_hoh_topology_H_outlet_azimuthal_npts_1(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt4",value)
    def set_b2b_hoh_topology_H_outlet_azimuthal_npts_2(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt6",value)
    def set_b2b_hoh_topology_H_outlet_azimuthal_npts_3(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt5",value)
    def set_b2b_hoh_topology_I_outlet_azimuthal_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt4",value)
    def get_b2b_hoh_topology_H_outlet_azimuthal_npts_1(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt4")
    def get_b2b_hoh_topology_H_outlet_azimuthal_npts_2(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt6")
    def get_b2b_hoh_topology_H_outlet_azimuthal_npts_3(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt5")
    def get_b2b_hoh_topology_I_outlet_azimuthal_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt4")

#       inlet periodic grid points number
    def set_b2b_hoh_topology_I_inlet_periodic_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt7",value)
    def get_b2b_hoh_topology_I_inlet_periodic_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt7")
#       outlet periodic grid points number
    def set_b2b_hoh_topology_I_outlet_periodic_npts(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt5",value)
    def get_b2b_hoh_topology_I_outlet_periodic_npts(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHbladeNpt5")

#       gap control
    def set_b2b_hoh_topology_gap_matching_with_main_channel(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_type",1)
    def set_b2b_hoh_topology_gap_non_matching_with_main_channel(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_type",0)

    def set_b2b_hoh_topology_gap_azimuthal_O_number_of_points(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_azi",value)
    def set_b2b_hoh_topology_gap_azimuthal_H_number_of_points(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_n1",value)
    def set_b2b_hoh_topology_gap_streamwise_H_number_of_points(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_n2",value)
    def set_b2b_hoh_topology_gap_d1_d2_addition(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHlead_gap_position_control1",value)
    def set_b2b_hoh_topology_gap_d1_d2_ratio(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHlead_gap_position_control2",value)
    def set_b2b_hoh_topology_gap_d3_d4_addition(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHtrail_gap_position_control1",value)
    def set_b2b_hoh_topology_gap_d3_d4_ratio(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHtrail_gap_position_control2",value)

    def get_b2b_hoh_topology_gap_matching_with_main_channel(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_type")

    def get_b2b_hoh_topology_gap_azimuthal_O_number_of_points(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_azi")
    def get_b2b_hoh_topology_gap_azimuthal_H_number_of_points(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_n1")
    def get_b2b_hoh_topology_gap_streamwise_H_number_of_points(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOH_gap_n2")
    def get_b2b_hoh_topology_gap_d1_d2_addition(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHlead_gap_position_control1")
    def get_b2b_hoh_topology_gap_d1_d2_ratio(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHlead_gap_position_control2")
    def get_b2b_hoh_topology_gap_d3_d4_addition(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHtrail_gap_position_control1")
    def get_b2b_hoh_topology_gap_d3_d4_ratio(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHtrail_gap_position_control2")
#    blade point control
#--------------------
#       leading edge grid point distribution control
    def set_b2b_hoh_leading_edge_control_type_none(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLead",0)
    def set_b2b_hoh_leading_edge_control_type_absolute_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLead",1)
    def set_b2b_hoh_leading_edge_control_type_relative_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLead",2)
    def set_b2b_hoh_leading_edge_control_type_cell_length(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLead",3)
    def set_b2b_hoh_leading_edge_control_absolute_distance(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadDistance",value)
    def set_b2b_hoh_leading_edge_control_relative_distance(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadRelativeDistance",value)
    def set_b2b_hoh_leading_edge_control_cell_length(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadLenght",value)
    def get_b2b_hoh_leading_edge_control_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLead")
    def get_b2b_hoh_leading_edge_control_absolute_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadDistance")
    def get_b2b_hoh_leading_edge_control_relative_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadRelativeDistance")
    def get_b2b_hoh_leading_edge_control_cell_length(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlLeadLenght")
#       trailing edge grid point distribution control
    def set_b2b_hoh_trailing_edge_control_type_none(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrail",0)
    def set_b2b_hoh_trailing_edge_control_type_absolute_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrail",1)
    def set_b2b_hoh_trailing_edge_control_type_relative_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrail",2)
    def set_b2b_hoh_trailing_edge_control_type_cell_length(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrail",3)
    def set_b2b_hoh_trailing_edge_control_absolute_distance(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailDistance",value)
    def set_b2b_hoh_trailing_edge_control_relative_distance(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailRelativeDistance",value)
    def set_b2b_hoh_trailing_edge_control_cell_length(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailLenght",value)
    def get_b2b_hoh_trailing_edge_control_type(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrail")
    def get_b2b_hoh_trailing_edge_control_absolute_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailDistance")
    def get_b2b_hoh_trailing_edge_control_relative_distance(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailRelativeDistance")
    def get_b2b_hoh_trailing_edge_control_cell_length(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlTrailLenght")

    def set_b2b_hoh_blade_points_distribution_smoothing_steps(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlSmooth",value)
    def get_b2b_hoh_blade_points_distribution_smoothing_steps(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeDistributionControlSmooth")

    def set_b2b_hoh_wake_clustering(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHdragDistributionControl",value)
    def get_b2b_hoh_wake_clustering(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHdragDistributionControl")

#    mesh control
#--------------------
#       boundary layer factor
    def set_b2b_mesh_control_bnd_layer_factor(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeToBladeclusteringRatio",value)
    def get_b2b_mesh_control_bnd_layer_factor(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHBladeToBladeclusteringRatio")
    def set_b2b_mesh_control_bnd_layer_cell_width(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClustering",value)
    def get_b2b_mesh_control_bnd_layer_cell_width(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HOHSkinClustering")

###----------------
#  HI topology
###----------------

#    topology control
#--------------------
#
    def set_b2b_HI_topology_H_full(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HIHTopology",value)
    def get_b2b_HI_topology_H_full(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HIHTopology")
    def set_b2b_HI_topology_H_inlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HIHInlet",value)
    def get_b2b_HI_topology_H_inlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HIHInlet")
    def set_b2b_HI_topology_H_outlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HIHOutlet",value)
    def get_b2b_HI_topology_H_outlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HIHOutlet")
    def set_b2b_HI_topology_skin_block(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HISkinBlock",value)
    def get_b2b_HI_topology_skin_block(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HISkinBlock")

#    grid points control
#-----------------------
#
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_inlet_down(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeInletDown",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_down(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeDown",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_lower_side(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINPreviousBladeUp",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_outlet_down(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeOutletDown",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_inlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeInletUp",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeUp",value)
    def set_b2b_HI_topology_grid_point_number_streamwise_blade_outlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeOutletUp",value)
    def set_b2b_HI_topology_grid_point_number_azimutal_inlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaBluntInlet",value)
    def set_b2b_HI_topology_grid_point_number_azimutal_outlet(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaBluntOutlet",value)
    def set_b2b_HI_topology_grid_point_number_azimutal_inlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaInlet",value)
    def set_b2b_HI_topology_grid_point_number_azimutal_outlet_up(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaOutlet",value)
    def set_b2b_HI_topology_grid_point_number_leading_edge_index(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HILEIndex",value)
    def set_b2b_HI_topology_grid_point_number_trailing_edge_index(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HITEIndex",value)

    def get_b2b_HI_topology_grid_point_number_streamwise_blade_inlet_down(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeInletDown")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_down(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeDown")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_lower_side(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINPreviousBladeUp")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_outlet_down(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeOutletDown")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_inlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeInletUp")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeUp")
    def get_b2b_HI_topology_grid_point_number_streamwise_blade_outlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINBladeOutletUp")
    def get_b2b_HI_topology_grid_point_number_azimutal_inlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaBluntInlet")
    def get_b2b_HI_topology_grid_point_number_azimutal_outlet(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaBluntOutlet")
    def get_b2b_HI_topology_grid_point_number_azimutal_inlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaInlet")
    def get_b2b_HI_topology_grid_point_number_azimutal_outlet_up(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HINThetaOutlet")

#    Mesh control
#-----------------------
#
    def set_b2b_HI_topology_automatic_clustering_relaxation(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HIAutoClusteringRelax",value)
    def get_b2b_HI_topology_automatic_clustering_relaxation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HIAutoClusteringRelax")
    def set_b2b_HI_topology_clustering_relaxation(self,value):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        set_b2b_topology_control_(parent_row.impl,self.impl,"HIClusteringRelax",value)
    def get_b2b_HI_topology_clustering_relaxation(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return get_b2b_topology_control_(parent_row.impl,self.impl,"HIClusteringRelax")

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Gap(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteGap(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0

    def link_non_axisymmetric_geometry(self,surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_hub_surface_(self.impl, surface_pointers)

    # kept for backward
    def unset_non_axisymmetric_hub(self):
        a5_set_gap_control_(self.impl,"non_axisymmetric_hub",0)
    def unset_non_axisymmetric_hub_repair_damage(self):
        a5_set_gap_control_(self.impl,"non_axisymmetric_hub_repair_damages",0)
    # end of backward

    def set_non_axisymmetric_hub(self,value=1):
        a5_set_gap_control_(self.impl,"non_axisymmetric_hub",value)
    def set_non_axisymmetric_hub_repair_damage(self,value=1):
        a5_set_gap_control_(self.impl,"non_axisymmetric_hub_repair_damages",value)

    def create_chimera_block(self):
        a5_set_gap_control_(self.impl,"keep_chimera_blocks",1)
    def skip_chimera_block(self):
        a5_set_gap_control_(self.impl,"keep_chimera_blocks",0)
    def set_topology_HO(self):
        a5_set_gap_control_(self.impl,"topologyType",0)
    def set_topology_O(self):
        a5_set_gap_control_(self.impl,"topologyType",1)
    def set_topology_O2H(self):
        a5_set_gap_control_(self.impl,"topologyType",3)
    def get_topology_type(self):
        return a5_get_gap_control_(self.impl,"topologyType")
    def set_width_at_leading_edge(self,value):
        a5_set_gap_control_(self.impl,"widthAtLeadingEdge",value)
    def get_width_at_leading_edge(self):
        return a5_get_gap_control_(self.impl,"widthAtLeadingEdge")
    def set_width_at_trailing_edge(self,value):
        a5_set_gap_control_(self.impl,"widthAtTrailingEdge",value)
    def get_width_at_trailing_edge(self):
        return a5_get_gap_control_(self.impl,"widthAtTrailingEdge")
    def set_clustering(self,value):
        a5_set_gap_control_(self.impl,"clustering",value)
    def get_clustering(self):
        return a5_get_gap_control_(self.impl,"clustering")
    def set_constant_cell_number(self,value):
        a5_set_gap_control_(self.impl,"constantCellsNumber",value)
    def get_constant_cell_number(self):
        return a5_get_gap_control_(self.impl,"constantCellsNumber")
    def set_number_of_points_in_spanwise_direction(self,value):
        a5_set_gap_control_(self.impl,"numberOfSpanwisePoints",value)
    def get_number_of_points_in_spanwise_direction(self):
        return a5_get_gap_control_(self.impl,"numberOfSpanwisePoints")
    def enable_defined_shape(self):
        a5_set_gap_control_(self.impl,"definedShape",1)
    def disable_defined_shape(self):
        a5_set_gap_control_(self.impl,"definedShape",0)
    def define_shape(self,curvefile):
        a5_set_gap_curve_(self.impl,curvefile)
    def get_defined_shape(self):
        return a5_get_gap_control_(self.impl,"definedShape")

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class PartialGap(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deletePartialGap(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0

    def set_chord_length_at_leading_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"chordLengthAtLeadingEdge",value)
    def get_chord_length_at_leading_edge(self):
        return a5_get_partial_gap_control_(self.impl,"chordLengthAtLeadingEdge")

    def set_chord_length_at_trailing_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"chordLengthAtTrailingEdge",value)
    def get_chord_length_at_trailing_edge(self):
        return a5_get_partial_gap_control_(self.impl,"chordLengthAtTrailingEdge")

    def set_number_of_points_at_leading_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"numberOfPointsNearLeadingEdge",value)
    def get_number_of_points_at_leading_edge(self):
        return a5_get_partial_gap_control_(self.impl,"numberOfPointsNearLeadingEdge")

    def set_number_of_points_at_trailing_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"numberOfPointsNearTrailingEdge",value)
    def get_number_of_points_at_trailing_edge(self):
        return a5_get_partial_gap_control_(self.impl,"numberOfPointsNearTrailingEdge")

    def set_streamwise_cell_width(self,value):
        a5_set_partial_gap_control_(self.impl,"streamwiseCellWidth",value)
    def get_streamwise_cell_width(self):
        return a5_get_partial_gap_control_(self.impl,"streamwiseCellWidth")

    def set_clustering_relaxation(self,value):
        a5_set_partial_gap_control_(self.impl,"clusteringRelaxation",value)
    def get_clustering_relaxation(self):
        return a5_get_partial_gap_control_(self.impl,"clusteringRelaxation")

    def set_width_at_leading_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"widthAtLeadingEdge",value)
    def get_width_at_leading_edge(self):
        return a5_get_partial_gap_control_(self.impl,"widthAtLeadingEdge")

    def set_width_at_trailing_edge(self,value):
        a5_set_partial_gap_control_(self.impl,"widthAtTrailingEdge",value)
    def get_width_at_trailing_edge(self):
        return a5_get_partial_gap_control_(self.impl,"widthAtTrailingEdge")

    def set_spanwise_cell_width(self,value):
        a5_set_partial_gap_control_(self.impl,"spanwiseCellWidth",value)
    def get_spanwise_cell_width(self):
        return a5_get_partial_gap_control_(self.impl,"spanwiseCellWidth")

    def set_constant_cell_number(self,value):
        a5_set_partial_gap_control_(self.impl,"constantCellsNumber",value)
    def get_constant_cell_number(self):
        return a5_get_partial_gap_control_(self.impl,"constantCellsNumber")

    def set_number_of_points_in_spanwise_direction(self,value):
        a5_set_partial_gap_control_(self.impl,"numberOfSpanwisePoints",value)
    def get_number_of_points_in_spanwise_direction(self):
        return a5_get_partial_gap_control_(self.impl,"numberOfSpanwisePoints")

    def enable_defined_shape(self):
        a5_set_partial_gap_control_(self.impl,"definedShape",1)
    def disable_defined_shape(self):
        a5_set_partial_gap_control_(self.impl,"definedShape",0)
    def define_shape(self,curvefile):
        a5_set_partial_gap_curve_(self.impl,curvefile)
    def get_defined_shape(self):
        return a5_get_partial_gap_control_(self.impl,"definedShape")

    def enable_definition_by_cylinder(self):
        a5_set_partial_gap_control_(self.impl,"definitionByCylinder",1)
    def disable_definition_by_cylinder(self):
        a5_set_partial_gap_control_(self.impl,"definitionByCylinder",0)
    def get_definition_by_cylinder(self):
        return a5_get_partial_gap_control_(self.impl,"definitionByCylinder")

    def set_cylinder_diameter(self,value):
        a5_set_partial_gap_control_(self.impl,"cylinderDiameter",value)
    def get_cylinder_diameter(self):
        return a5_get_partial_gap_control_(self.impl,"cylinderDiameter")

    def set_cylinder_axis(self,x,y,z):
        a5_set_partial_gap_control_(self.impl,"axis",x,y,z)
    def get_cylinder_axis(self):
        list = a5_get_partial_gap_control_(self.impl,"axis")
        return Point(list[0],list[1],list[2])

    def set_cylinder_origin(self,x,y,z):
        a5_set_partial_gap_control_(self.impl,"origin",x,y,z)

    def get_cylinder_origin(self):
        list = a5_get_partial_gap_control_(self.impl,"origin")
        return Point(list[0],list[1],list[2])


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Fillet(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteFillet(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0

    def set_radius_at_leading_edge(self,value):
        a5_set_fillet_control_(self.impl,"widthAtLeadingEdge",value)
    def get_radius_at_leading_edge(self):
        return a5_get_fillet_control_(self.impl,"widthAtLeadingEdge")
    def set_radius_at_trailing_edge(self,value):
        a5_set_fillet_control_(self.impl,"widthAtTrailingEdge",value)
    def get_radius_at_trailing_edge(self):
        return a5_get_fillet_control_(self.impl,"widthAtTrailingEdge")
    def set_minimum_angle(self,value):
        a5_set_fillet_control_(self.impl,"minimumAngle",value)
    def get_minimum_angle(self):
        return a5_get_fillet_control_(self.impl,"minimumAngle")
    def set_clustering(self,value):
        a5_set_fillet_control_(self.impl,"clusteringAtLE",value)
        a5_set_fillet_control_(self.impl,"clusteringAtTE",value)
    def get_clustering(self):
        return a5_get_fillet_control_(self.impl,"clusteringAtLE")
    def set_clustering_at_leading_edge(self,value):
        a5_set_fillet_control_(self.impl,"clusteringAtLE",value)
    def get_clustering_at_leading_edge(self):
        return a5_get_fillet_control_(self.impl,"clusteringAtLE")
    def set_clustering_at_trailing_edge(self,value):
        a5_set_fillet_control_(self.impl,"clusteringAtTE",value)
    def get_clustering_at_trailing_edge(self):
        return a5_get_fillet_control_(self.impl,"clusteringAtTE")
    def set_clustering_from_spanwise_channel_height(self,value):
        a5_compute_gap_cell_width_from_span_channel_height_(self.impl,value)
    def set_constant_cell_number(self,value):
        a5_set_fillet_control_(self.impl,"constantCellsNumber",value)
    def get_constant_cell_number(self):
        return a5_get_fillet_control_(self.impl,"constantCellsNumber")
    def set_number_of_points_in_spanwise_direction(self,value):
        a5_set_fillet_control_(self.impl,"numberOfSpanwisePoints",value)
    def get_number_of_points_in_spanwise_direction(self):
        return a5_get_fillet_control_(self.impl,"numberOfSpanwisePoints")
    def set_butterfly_topology(self,value):
        a5_set_fillet_control_(self.impl,"butterflyTopology",value)
    def get_butterfly_topology(self):
        return a5_get_fillet_control_(self.impl,"butterflyTopology")
    def set_butterfly_radial_number_of_points(self,value):
        a5_set_fillet_control_(self.impl,"butterflyRadialNpts",value)
    def get_butterfly_radial_number_of_points(self):
        return a5_get_fillet_control_(self.impl,"butterflyRadialNpts")
    def set_create_geometry(self,value):
        a5_set_fillet_control_(self.impl,"createGeometry",value)
    def get_create_geometry(self):
        return a5_get_fillet_control_(self.impl,"createGeometry")
    def set_constant_radius(self,value):
        a5_set_fillet_control_(self.impl,"constantRadius",value)
    def get_constant_radius(self):
        return a5_get_fillet_control_(self.impl,"constantRadius")
    def enable_defined_shape(self):
        a5_set_fillet_control_(self.impl,"definedShape",1)
    def disable_defined_shape(self):
        a5_set_fillet_control_(self.impl,"definedShape",0)
    def define_shape(self,curvefile):
        a5_set_fillet_curve_(self.impl,curvefile)
    def get_defined_shape(self):
        return a5_get_fillet_control_(self.impl,"definedShape")

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class Snubber(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)        
    def delete(self):
        deleteRowSnubber_(self.impl)
        self.impl = 0

    def link_to_meridional_curve_up(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_meridional_curve_(self.impl, 0, curve_pointers)        
    def link_to_meridional_curve_down(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_meridional_curve_(self.impl, 1, curve_pointers)
    def link_to_geometry_on_blade_pressure_side(self, surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_snubber_surfaces_(self.impl, surface_pointers, 1)
    def link_to_geometry_on_blade_suction_side(self, surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_snubber_surfaces_(self.impl, surface_pointers, 0)
    def link_to_leading_edge_on_blade_pressure_side(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_leading_edge_(self.impl, curve_pointers, 1)
    def link_to_leading_edge_on_blade_suction_side(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_leading_edge_(self.impl, curve_pointers, 0)
    def link_to_trailing_edge_on_blade_pressure_side(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_trailing_edge_(self.impl, curve_pointers, 1)
    def link_to_trailing_edge_on_blade_suction_side(self, curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_snubber_trailing_edge_(self.impl, curve_pointers, 0)
    def link_to_fillet_on_blade_pressure_side(self, surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_snubber_fillet_(self.impl, surface_pointers, 1)
    def link_to_fillet_on_blade_suction_side(self, surface_names):
        surface_pointers = []
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_snubber_fillet_(self.impl, surface_pointers, 0)

    def set_name(self, name):
        setSnubberName_(self.impl, name)
    def get_name(self):
        return getSnubberName_(self.impl)
    def set_clustering(self, value):
        setSnubberParameter_(self.impl, "clustering", value)
    def get_clustering(self):
        return getSnubberParameter_(self.impl, "clustering")
    def set_skin_expansion_ratio(self, value):
        setSnubberParameter_(self.impl, "skinExpansionRatio", value)
    def get_skin_expansion_ratio(self):
        return getSnubberParameter_(self.impl, "skinExpansionRatio")
    def set_leading_edge_relative_control_distance(self, value):
        setSnubberParameter_(self.impl, "LERelativeControlDistance", value)
    def get_leading_edge_relative_control_distance(self):
        return getSnubberParameter_(self.impl, "LERelativeControlDistance")
    def set_trailing_edge_relative_control_distance(self, value):
        setSnubberParameter_(self.impl, "TERelativeControlDistance", value)
    def get_trailing_edge_relative_control_distance(self):
        return getSnubberParameter_(self.impl, "TERelativeControlDistance")
    def set_spanwise_index(self, value):
        setSnubberParameter_(self.impl, "spanwiseIndex", value)
    def get_spanwise_index(self):
        return getSnubberParameter_(self.impl, "spanwiseIndex")
    def set_skin_number_of_points(self, value):
        setSnubberParameter_(self.impl, "skinNpts", value)
    def get_skin_number_of_points(self):
        return getSnubberParameter_(self.impl, "skinNpts")
    def set_upstream_number_of_points(self, value):
        setSnubberParameter_(self.impl, "upstreamNpts", value)
    def get_upstream_number_of_points(self):
        return getSnubberParameter_(self.impl, "upstreamNpts")
    def set_downstream_number_of_points(self, value):
        setSnubberParameter_(self.impl, "downstreamNpts", value)
    def get_downstream_number_of_points(self):
        return getSnubberParameter_(self.impl, "downstreamNpts")
    def set_spanwise_number_of_points(self, value):
        setSnubberParameter_(self.impl, "LETENpts", value)
    def get_spanwise_number_of_points(self):
        return getSnubberParameter_(self.impl, "LETENpts")
    def set_fillet_butterfly_radial_number_of_points(self, value):
        setSnubberParameter_(self.impl, "filletButterflyRadialNpts", value)
    def get_fillet_butterfly_radial_number_of_points(self):
        return getSnubberParameter_(self.impl, "filletButterflyRadialNpts")
      

#------------------------------------------------------------------------------------------------
# class blade sheet
#------------------------------------------------------------------------------------------------

class BladeSheet(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteBladeSheet(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0

    def lower_zone(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return Gap(a5_getBladeSheetLowerZone(parent_row.impl,parent_blade.impl,self.impl))
    def upper_zone(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return Gap(a5_getBladeSheetUpperZone(parent_row.impl,parent_blade.impl,self.impl))

#       type  = 0: on lower side, 1: on upper side, 2: on both side
    def set_type(self,value):
        a5_setBladeSheetParameters_py(self.impl,"type",value)
    def get_type(self):
        a5_getBladeSheetParametersByName(self.impl,"type")
    def set_width(self,value):
        a5_setBladeSheetParameters_py(self.impl,"width",value)
    def get_width(self):
        return a5_getBladeSheetParametersByName(self.impl,"width")
    def get_distance_from_leading_edge(self):
        a5_getBladeSheetParametersByName(self.impl,"distanceFromLeadingEdge")
    def set_distance_from_leading_edge(self,value):
        a5_setBladeSheetParameters_py(self.impl,"distanceFromLeadingEdge",value)
    def get_distance_from_trailing_edge(self):
        a5_getBladeSheetParametersByName(self.impl,"distanceFromTrailingEdge")
    def set_distance_from_trailing_edge(self,value):
        a5_setBladeSheetParameters_py(self.impl,"distanceFromTrailingEdge",value)
    def get_npts_near_leading_edge(self):
        a5_getBladeSheetParametersByName(self.impl,"streamwisePointFromLeadingEdge")
    def set_npts_near_leading_edge(self,value):
        a5_setBladeSheetParameters_py(self.impl,"streamwisePointFromLeadingEdge",value)
    def get_npts_near_trailing_edge(self):
        a5_getBladeSheetParametersByName(self.impl,"streamwisePointFromTrailingEdge")
    def set_npts_near_trailing_edge(self,value):
        a5_setBladeSheetParameters_py(self.impl,"streamwisePointFromTrailingEdge",value)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class ZR effect
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class TechnologicalEffectZR(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        technoEffectmeridional_delete_effect_(self.impl)
## 3d blocks list
    def block_list(self):
        blist = []
        for pointer in a5_get_entity_block_list_(self.impl):
            blist.append(Block(pointer))
        return blist
    def set_name(self,name):
        technoEffectmeridional_setName_(self.impl,name)
    def get_name(self):
        return technoEffectmeridional_getName_(self.impl)

## expMax : maximum expansion ratio
## w      : wall cell width
## opt    : smoothing steps
## cst    : percentage constant cell
## exp    : radial expansion
## opt2   : far field smooth smoothing steps
## per    : periodic fnmb
## co     : coarse grid level
## tol    : connection tolerance
## p      : propagate theta deviation
    def set_parameters(self,expMax,w,opt,cst,exp,opt2,per,coarse,tol,p,rs1=0,rs2=0,rs3=1):
        cluster_relax_angle = self.get_clustering_relaxation_angle()
        azi_npts = self.get_azimuthal_number_of_points()
        technoEffectmeridional_set_parameter_(self.impl,500,expMax,expMax,expMax,cluster_relax_angle,w,opt,cst,exp,opt2,per,coarse,tol,p,azi_npts,rs1,rs2,rs3)
    def technoEffectmeridional_toggle_grid_rep():
        technoEffectmeridional_toggle_rep_(self.impl,"face_grid")
    def set_rotating_boundaries_rotation_speed(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"boundariesRotationSpeed",i)
    def set_maximum_expansion_ratio(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatio",i)
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatioInBoundaryLayer",i)
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatioAlongBoundary",i)
    def set_maximum_expansion_ratio_general(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatio",i)
    def set_maximum_expansion_ratio_in_boundary_layer(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatioInBoundaryLayer",i)
    def set_maximum_expansion_ratio_along_boundary(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"maxExpansionRatioAlongBoundary",i)
    def set_clustering_relaxation_angle(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"clusteringRelaxationAngle",i)
    def set_special_distribution_for_boundary_layer(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"specialDistributionForBndLayer", i)
    def set_solid_wall_clustering(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"solidWallClustering",i)
    def set_number_of_smoothing_steps(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"smoothingSteps",i)
    def set_constant_cells_percentage(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"cstCellPercentage",i)
    def set_radial_expansion(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"radialExpansion",i)
    def set_smoothing_steps_far_field(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"smoothFarField",i)
    def set_periodic_fnmb_row_connexion(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"periodicFnmb",i)
    def set_tolerance(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"tolerance",i)
    def set_theta_deviation_propagation(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"propagateThetaDeviation",i)
    def set_azimuthal_number_of_points(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"azimuthalNumberOfPoints",i)        
    def set_periodic_fnmb_connexion_at_rs(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"PeriodicFNMBAtRS",i)
    def set_periodic_connexion_at_rs(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"PeriodicAtRS",i)
    def set_matching_connexion_at_rs(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"MatchingAtRS",i)
    def set_H_topology_around_corners(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"HTopologyTreatmentAtCorners",i)
    def set_H_topology_around_thin_films(self,i):
        technoEffectmeridional_set_parameter_by_name_(self.impl,"HTopologyTreatmentAtThinFilms",i)

    def get_rotating_boundaries_rotation_speed(self):
        return technoEffectmeridional_get_parameter_(self.impl,"boundariesRotationSpeed")
    def get_maximum_expansion_ratio(self):
        return technoEffectmeridional_get_parameter_(self.impl,"maxExpansionRatio")
    def get_maximum_expansion_ratio_general(self):
        return technoEffectmeridional_get_parameter_(self.impl,"maxExpansionRatio")
    def get_maximum_expansion_ratio_in_boundary_layer(self):
        return technoEffectmeridional_get_parameter_(self.impl,"maxExpansionRatioInBoundaryLayer")
    def get_maximum_expansion_ratio_along_boundary(self):
        return technoEffectmeridional_get_parameter_(self.impl,"maxExpansionRatioAlongBoundary")
    def get_clustering_relaxation_angle(self):
        return technoEffectmeridional_get_parameter_(self.impl,"clusteringRelaxationAngle")
    def get_solid_wall_clustering(self):
        return technoEffectmeridional_get_parameter_(self.impl,"solidWallClustering")
    def get_number_of_smoothing_steps(self):
        return technoEffectmeridional_get_parameter_(self.impl,"smoothingSteps")
    def get_constant_cells_percentage(self):
        return technoEffectmeridional_get_parameter_(self.impl,"cstCellPercentage")
    def get_radial_expansion(self):
        return technoEffectmeridional_get_parameter_(self.impl,"radialExpansion")
    def get_smoothing_steps_far_field(self):
        return technoEffectmeridional_get_parameter_(self.impl,"smoothFarField")
    def get_periodic_fnmb_row_connexion(self):
        return technoEffectmeridional_get_parameter_(self.impl,"periodicFnmb")
    def get_tolerance(self):
        return technoEffectmeridional_get_parameter_(self.impl,"tolerance")
    def get_theta_deviation_propagation(self):
        return technoEffectmeridional_get_parameter_(self.impl,"propagateThetaDeviation")
    def get_azimuthal_number_of_points(self):
        return technoEffectmeridional_get_parameter_(self.impl,"azimuthalNumberOfPoints")
    def get_periodic_fnmb_connexion_at_rs(self):
        return technoEffectmeridional_get_parameter_(self.impl,"PeriodicFNMBAtRS")
    def get_periodic_connexion_at_rs(self):
        return technoEffectmeridional_get_parameter_(self.impl,"PeriodicAtRS")
    def get_matching_connexion_at_rs(self):
        return technoEffectmeridional_get_parameter_(self.impl,"MatchingAtRS")
    def get_H_topology_around_corners(self):
        return technoEffectmeridional_get_parameter_(self.impl,"HTopologyTreatmentAtCorners")
    def get_H_topology_around_thin_films(self):
        return technoEffectmeridional_get_parameter_(self.impl,"HTopologyTreatmentAtThinFilms")

    def start_editing(self):
        technoEffectmeridional_startEditing_(self.impl)
    def stop_editing(self):
        technoEffectmeridional_stopEditing_(self.impl)

    def detect_unmapped_edges(self):
        return technoEffectmeridional_detectZRUnmappedEdgesTool_(self.impl)

#------------------------------------------------------------------------------------------------
def a5_get_ZR_effect_number():
    return technoEffectmeridional_getNumber_()
def technologicalEffectZR(B):                           # indices from 1
    if type(B) is types.StringType:         # assuming name of zr effect is given
        return TechnologicalEffectZR(technoEffectmeridional_pointer_(B))
    elif isinstance(B,TechnologicalEffectZR):
        return B
    else:   return TechnologicalEffectZR(technoEffectmeridional_pointer_(technoEffectmeridional_getNameByIndex_(B-1)))
def a5_new_ZR_effect():
    return TechnologicalEffectZR(technoEffectmeridional_new_effect_())

# following functions kept for backward only
def technoEffectmeridional_computeDefaultMesh():
    technoEffectmeridional_compute_default_mesh_()
def technoEffectmeridional_connectBlocks():
    technoEffectmeridional_connect_blocks_()
def zr_techno_effect_computeDefaultMesh_cmd():
    technoEffectmeridional_compute_default_mesh_()
def zr_techno_effect_connectBlocks_cmd():
    technoEffectmeridional_connect_blocks_()
def technoEffectmeridional_start_edit_mode():
    technoEffectmeridional_start_edit_mode_()
def technoEffectmeridional_stop_edit_mode():
    technoEffectmeridional_stop_edit_mode_()
# end of backward

def zr_techno_effect_compute_default_mesh():
    technoEffectmeridional_compute_default_mesh_()
def zr_techno_effect_connect_blocks():
    technoEffectmeridional_connect_blocks_()
def zr_techno_effect_automatic_blocking():
    technoEffectmeridional_automatic_blocking_()
def zr_techno_effect_delete_blocks():
    technoEffectmeridional_delete_blocks_()
def zr_techno_effect_automatic_z_cst_line():
    technoEffectmeridional_automatic_z_cst_line_()
def zr_techno_effect_set_boundary_point(i,gp):
    technoEffectmeridional_set_boundary_point_(i,format_point(gp))
def zr_techno_effect_reset_boundary_point(i):
    technoEffectmeridional_reset_boundary_point_(i)
def zr_techno_effect_start_edit_mode():
    technoEffectmeridional_start_edit_mode_()
def zr_techno_effect_stop_edit_mode():
    technoEffectmeridional_stop_edit_mode_()

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class 3D effect
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class TechnologicalEffect3D(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def delete(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        technoEffect3d_delete_(parent_row.impl,self.impl)
        self.impl = 0
    def set_name(self,name):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        technoEffect3d_setName_(parent_row.impl,self.impl,name)

## 3d blocks list

    def block_list(self):
        blist = []
        for pointer in a5_get_entity_block_list_(self.impl):
            blist.append(Block(pointer))
        return blist

    def load_geometry(self,file):
        technoEffect3d_defineGeometry_(self.impl,file)
    def load_topology(self,name):
        a5_apply_topology_to_technological_effect(self.impl,name)
    def save_topology(self,name):
        a5_save_topology_of_technological_effect(self.impl,1,name,0)
    def copy_topology(self):
        a5_copy_topology_(self.impl,"0")

    def paste_topology(self):
        a5_paste_topology_(self.impl,"0")
    def link_geometry(self,curve_names, surface_names):
        curve_pointers = []
        surface_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_3D_entity_(self.impl, curve_pointers, surface_pointers)

    def start_editing(self):
        technoEffect3d_startEditing_(self.impl)
    def stop_editing(self):
        technoEffect3d_stopEditing_(self.impl)

#------------------------------------------------------------------------------------------------
# kept for backward
def techno_effect_3d_start_edit_mode():
    technoEffect3d_start_edit_()

# kept for backward
def techno_effect_3d_stop_edit_mode():
    technoEffect3d_stop_edit_()

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class Stagnation Point
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class StagnationPoint(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def set_distribution_type_absolute_distance(self):
        a5_set_edge_control_(self.impl,"controlDistanceType",1)
    def set_distribution_type_relative_distance(self):
        a5_set_edge_control_(self.impl,"controlDistanceType",2)
    def set_distribution_type_cell_length(self):
        a5_set_edge_control_(self.impl,"controlDistanceType",3)
    def get_distribution_type(self):
        return a5_get_edge_control_(self.impl,"controlDistanceType")
    def set_distribution_cell_length(self,value):
        a5_set_edge_control_(self.impl,"cellLenght",value)
    def get_distribution_cell_length(self):
        return a5_get_edge_control_(self.impl,"cellLenght")
    def set_distribution_absolute_distance(self,value):
        a5_set_edge_control_(self.impl,"absoluteControlDistance",value)
    def get_distribution_absolute_distance(self):
        return a5_get_edge_control_(self.impl,"absoluteControlDistance")
    def set_distribution_relative_distance(self,value):
        a5_set_edge_control_(self.impl,"relativeControlDistance",value)
    def get_distribution_relative_distance(self):
        return a5_get_edge_control_(self.impl,"relativeControlDistance")
    def enable_distribution_from_expansion_ratio(self):
        a5_set_edge_control_(self.impl,"imposedExpansionRatio",1)
    def disable_distribution_from_expansion_ratio(self):
        a5_set_edge_control_(self.impl,"imposedExpansionRatio",0)
    def get_distribution_from_expansion_ratio(self):
        return a5_get_edge_control_(self.impl,"imposedExpansionRatio")
    def desired_expansion_ratio(self,value):
        a5_set_edge_control_(self.impl,"desiredExpansionRatio",value)
    def get_desired_expansion_ratio(self):
        return a5_get_edge_control_(self.impl,"desiredExpansionRatio")
    def set_percentage_cst_cell(self,value):
        a5_set_edge_control_(self.impl,"cstcell",value)
    def get_percentage_cst_cell(self):
        return a5_get_edge_control_(self.impl,"cstcell")
    def get_parametric_location(self):
        return a5_get_edge_control_(self.impl,"parametricLocation")
    def set_parametric_location(self,value):
        a5_set_edge_control_(self.impl,"parametricLocation", value)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class RSInterface
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class RSInterface(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def select(self):
        select_(self.impl)
    def copy_left_meridional_distribution(self):
        a5_copy_topology_(self.impl,"left")
    def copy_right_meridional_distribution(self):
        a5_copy_topology_(self.impl,"right")
    def paste_left_meridional_distribution(self):
        a5_paste_topology_(self.impl,"left")
    def paste_right_meridional_distribution(self):
        a5_paste_topology_(self.impl,"right")
    def merge_meridional_distribution(self):
        rs_merge_distributions_(self.impl)

    def set_name(self,value):
        set_rs_parameters_(self.impl,"rsname",value)
    def get_name(self):
        return get_rs_parameters_(self.impl,"rsname")
    def streamwise_number_of_points(self,value):
        set_rs_parameters_(self.impl,"stream_npts",value)
    def get_streamwise_number_of_points(self):
        return get_rs_parameters_(self.impl,"stream_npts")
    def streamwise_index(self,value):
        set_rs_parameters_(self.impl,"stream_index",value)
    def get_streamwise_index(self):
        return get_rs_parameters_(self.impl,"stream_index")
    def enable_b2b_control(self):
        set_rs_parameters_(self.impl,"b2b_control",1)
    def disable_b2b_control(self):
        set_rs_parameters_(self.impl,"b2b_control",0)
    def get_b2b_control(self):
        return get_rs_parameters_(self.impl,"b2b_control")
    def geometry_is_fixed(self):
        set_rs_parameters_(self.impl,"fixed",1)
    def geometry_is_not_fixed(self):
        set_rs_parameters_(self.impl,"fixed",0)
    def get_geometry_is_fixed(self):
        return get_rs_parameters_(self.impl,"fixed")
    def cell_width_in_streamwise_direction(self,value):
        set_rs_parameters_(self.impl,"cell_width",value)
    def get_cell_width_in_streamwise_direction(self):
        return get_rs_parameters_(self.impl,"cell_width")

    # available keywords: "None", "Hub", "Shroud", Mid_Span"
    def set_clustering_relaxation_location(self,keyword):
        if keyword == "None":
            set_rs_parameters_(self.impl,"relaxationLocation",0)
        elif keyword == "Hub":
            set_rs_parameters_(self.impl,"relaxationLocation",1)
        elif keyword == "Shroud":
            set_rs_parameters_(self.impl,"relaxationLocation",2)
        elif keyword == "Mid_Span":
            set_rs_parameters_(self.impl,"relaxationLocation",3)
        else: raise ValueError,'Relaxation Location: Unsupported Keyword'
    def get_clustering_relaxation_location(self):
        return get_rs_parameters_(self.impl,"relaxationLocation")
    def set_clustering_relaxation_factor(self,value):
        set_rs_parameters_(self.impl,"relaxationFactor",value)

    def get_clustering_relaxation_factor(self):
        return get_rs_parameters_(self.impl,"relaxationFactor")

    def set_linear_shape(self):
        set_rs_parameters_(self.impl,"shape",0,0,0,0,0)
    def set_curvilinear_shape(self):
        set_rs_parameters_(self.impl,"shape",1,0,0,0,0)
    def set_user_defined_shape(self):
        set_rs_parameters_(self.impl,"shape",2,0,0,0,0)    
    def set_default_shape(self):
        set_rs_parameters_(self.impl,"shape",3,0,0,0,0)
    def set_z_cst_shape(self,value):
        set_rs_parameters_(self.impl,"shape",5,0,1,0,value)
    def set_r_cst_shape(self,value):
        set_rs_parameters_(self.impl,"shape",4,1,0,value,0)
    def set_relative_location(self,value):
        set_rs_parameters_(self.impl,"relative_location",value)
    def set_external_curve(self,filename):
        set_rs_external_curve_(self.impl,filename)
    def link_geometry(self,curve_names):
        curve_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        AutoGrid_link_rs_interface_(self.impl, curve_pointers)
    def clear_distribution(self):
        clear_distribution_(self.impl)
    def export_geometry(self,filename):
        exportRSInterface_(self.impl,filename)
    def get_shape(self):
        return get_rs_parameters_(self.impl,"shape")
    def get_r_cst_value(self):
        return get_rs_parameters_(self.impl,"r_cst_value")
    def get_z_cst_value(self):
        return get_rs_parameters_(self.impl,"z_cst_value")
    def get_reference_frame(self):
        return get_rs_parameters_(self.impl,"ref_frame")
    def set_reference_frame_relative(self):
        return set_rs_parameters_(self.impl,"ref_frame",1)
    def set_reference_frame_absolute(self):
        return set_rs_parameters_(self.impl,"ref_frame",0)
    def get_relative_location(self):
        return get_rs_parameters_(self.impl,"relative_location")
    def get_reference_row(self):
        pointer = get_rs_parameters_(self.impl,"reference_row")
        if pointer: return Row(pointer)
        else: return 0
    def get_reference_row_location(self):
        return get_rs_parameters_(self.impl,"reference_row_location")
    def get_number_of_control_points(self):
        return get_rs_num_control_points_(self.impl)
    def get_control_point(self,i):
        z,r = get_rs_control_point_(self.impl, i)
        return Point(z,r,0)
    def move_control_point(self,i,point):
        move_rs_control_point_(self.impl, i, format_point(point))
    def get_curve(self):
        curve = get_rs_curve_(self.impl)
        if curve: return Curve(curve)
        else:     return 0
    def compute_npts_according_to_max_cell_width(self, max_cell_width):
        a5_compute_z_cst_line_npts_to_respect_max_cell_size_(self.impl, max_cell_width)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class FlowPathControlSection
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class FlowPathControlSection():
    def __init__(self, pointer, row):
        self.impl = pointer
        self.row  = row

    def get_main_subdivision(self):
        return FlowPathSubdivision(get_main_flow_path_subdivision_(self.row.impl, self.impl))
    def get_hub_gap_subdivision(self, index):
        return FlowPathSubdivision(get_hub_gap_flow_path_subdivision_(self.row.impl, self.impl, index-1))
    def get_tip_gap_subdivision(self, index):
        return FlowPathSubdivision(get_tip_gap_flow_path_subdivision_(self.row.impl, self.impl, index-1))
    def get_snubber_subdivision(self):
        return FlowPathSubdivision(get_snubber_flow_path_subdivision_(self.row.impl, self.impl, 0))
    # kept for backward
    def get_fin_subdivision(self):
        return self.get_snubber_subdivision()
    def get_snubber_secondary_subdivision(self):
        return FlowPathSubdivision(get_snubber_secondary_flow_path_subdivision_(self.row.impl, self.impl, 0))
    def get_main_bypass_subdivision(self):
        return FlowPathSubdivision(get_main_bypass_flow_path_subdivision_(self.row.impl, self.impl))
    def get_upstream_bypass_subdivision(self):
        return FlowPathSubdivision(get_upstream_bypass_flow_path_subdivision_(self.row.impl, self.impl))


#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class FlowPathSubdivision
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

class FlowPathSubdivision():
    def __init__(self, pointer):
        self.impl = pointer

    def set_end_parameter(self, norm_param):
        set_flow_path_subdivision_end_param_(self.impl, norm_param)
    def add_fixed_point(self, index, norm_param):
        flow_path_subdivision_add_fixed_point_(self.impl, index-1, norm_param)
    def remove_fixed_point(self, index):
        flow_path_subdivision_remove_fixed_point_(self.impl, index-1)
    def get_number_of_fixed_points(self):
        return flow_path_subdivision_get_num_fixed_points_(self.impl)

    def cluster_uniform(self, index):
        return flow_path_subdivision_set_distribution_(self.impl, index-1, 'UNIFORM')
    def cluster_start(self, index, dist):
        return flow_path_subdivision_set_distribution_(self.impl, index-1, 'START', dist)
    def cluster_end(self, index, dist):
        return flow_path_subdivision_set_distribution_(self.impl, index-1, 'END', dist)
    def cluster_both_ends2(self, index, sDist, eDist, nCstCell):
        return flow_path_subdivision_set_distribution_(self.impl, index-1, 'START_END2', sDist, eDist, nCstCell)
    def cluster_tanh(self, index, sDist, eDist):
        return flow_path_subdivision_set_distribution_(self.impl, index-1, 'TANH', sDist, eDist)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#                                     class BasicCurve
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

def basic_curve(name):
    return BasicCurve(get_basic_curve_by_name_(name))

class BasicCurve(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

    def delete(self):
        delete_basic_curve_(self.impl)
        self.impl = 0

    def set_discretisation(self, i):
        set_basic_curve_discretisation_(self.impl,i)
    def get_discretisation(self):
        return get_basic_curve_discretisation_(self.impl)

    def set_rotating_property(self, i):
        set_basic_curve_rotation_(self.impl,i)
    def get_rotating_property(self):
        return get_basic_curve_rotation_(self.impl)

    def get_data_reduction(self):
        result = get_basic_curve_data_reduction_(self.impl)
        return result[0]
    def get_data_reduction_minimal_distance(self):
        result = get_basic_curve_data_reduction_(self.impl)
        return result[1]
    def get_data_reduction_maximum_angle(self):
        result = get_basic_curve_data_reduction_(self.impl)
        return result[2]
    def check_geometry(self):
        data_reduction = self.get_data_reduction()
        min_dist = self.get_data_reduction_minimal_distance()
        max_angle = self.get_data_reduction_maximum_angle()
        result = set_basic_curve_data_reduction_(self.impl, 0, min_dist, max_angle, data_reduction)
        results = []
        results.append(result[0])
        results.append(result[1])
        return results
    def set_data_reduction(self, reduction, min_dist=1e-6, max_angle=80):
        result = set_basic_curve_data_reduction_(self.impl, 0, min_dist, max_angle, reduction)
        results = []
        results.append(result[0])
        results.append(result[1])
        return results

#------------------------------------------------------------------------------------------------
#                                     By-pass management
#------------------------------------------------------------------------------------------------

#       H:0, C: 1
def get_by_pass_configuration_topologyType():
    return a5_getNozzleParameters("topologyType")
def get_by_pass_configuration_Bnd_layer_Width():
    return a5_getNozzleParameters("relativeWidth")
def get_by_pass_configuration_nozzle_index():
    return a5_getNozzleParameters("nozzleIndex")
def get_by_pass_configuration_clustering():
    return a5_getNozzleParameters("clustering")
def get_by_pass_configuration_numberOfSpanwisePoints():
    return a5_getNozzleParameters("numberOfSpanwisePoints")
def get_by_pass_configuration_numberOfStreamwisePoints():
    return a5_getNozzleParameters("numberOfStreamwisePoints")
def get_by_pass_configuration_relativeControlDistance():
    return a5_getNozzleParameters("relativeControlDistance")
def get_by_pass_configuration_nup():
    return a5_getNozzleParameters("nozzleUp")
def get_by_pass_configuration_ndown():
    return a5_getNozzleParameters("nozzleDown")
def get_by_pass_configuration_relax_inlet_distribution():
    return a5_getNozzleParameters("relaxInletDistribution")

def set_by_pass_configuration_topologyType(value):
    return a5_setNozzleParameters("topologyType",value)
def set_by_pass_configuration_Bnd_layer_Width(value):
    return a5_setNozzleParameters("relativeWidth",value)
def set_by_pass_configuration_nozzle_index(value):
    return a5_setNozzleParameters("nozzleIndex",value)
def set_by_pass_configuration_clustering(value):
    return a5_setNozzleParameters("clustering",value)
def set_by_pass_configuration_numberOfSpanwisePoints(value):
    return a5_setNozzleParameters("numberOfSpanwisePoints",value)
def set_by_pass_configuration_numberOfStreamwisePoints(value):
    return a5_setNozzleParameters("numberOfStreamwisePoints",value)
def set_by_pass_configuration_relativeControlDistance(value):
    return a5_setNozzleParameters("relativeControlDistance",value)
def set_by_pass_configuration_nup(value):
    return a5_setNozzleParameters("nozzleUp",value)
def set_by_pass_configuration_ndown(value):
    return a5_setNozzleParameters("nozzleDown",value)
def set_by_pass_configuration_relax_inlet_distribution(value):
    return a5_setNozzleParameters("relaxInletDistribution",value)

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#---------------------- CHT & COOLING MODULE ----------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
#---------------------- BLADE COOLING HOLE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class Hole(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteHole(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl)
        self.impl = 0
    def getName(self):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getEndWallHolesName(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl)
    def setName(self,value):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_setEndWallHolesName(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl,value)
############################
####### Hole control
############################

####### Hole location
####    parametric mode (all hole type excepted grooves)
    def get_spanwise_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocation")
    def set_spanwise_location(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocation",value,highlight,draw)
#       parent lines defined in % of arc length from leading edge
    def get_streamwise_location_from_leading_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocation2")
    def set_streamwise_location_from_leading_edge(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocation2",value,highlight,draw)
#       parent lines defined in % of arc length from trailing edge
    def get_streamwise_location_from_trailing_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocation3")
    def set_streamwise_location_from_trailing_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocation3",value,highlight)
#       parent lines defined in % of meridional chord
    def get_streamwise_location_on_chord_length(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocation1")
    def set_streamwise_location_on_chord_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocation1",value,highlight)
#       xyz mode  (p1 for te grooves)
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       xyz mode only for te groove: p2
    def get_x2_location(self):
        return a5_getHolesProperties(self.impl,"locationX2")
    def set_x2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX2",value,highlight)
    def get_y2_location(self):
        return a5_getHolesProperties(self.impl,"locationY2")
    def set_y2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY2",value,highlight)
    def get_z2_location(self):
        return a5_getHolesProperties(self.impl,"locationZ2")
    def set_z2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ2",value,highlight)
#       rthz mode  (p1 for grooves)
    def get_r_location(self):
        return a5_getHolesProperties(self.impl,"locationR")
    def set_r_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationR",value,highlight)
    def get_theta_location(self):
        return a5_getHolesProperties(self.impl,"locationTH")
    def set_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       rthz mode only for te groove: p2
    def get_r2_location(self):
        return a5_getHolesProperties(self.impl,"locationR2")
    def set_r2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationR2",value,highlight)
    def get_theta2_location(self):
        return a5_getHolesProperties(self.impl,"locationTH2")
    def set_theta2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH2",value,highlight)
    def get_z2_location(self):
        return a5_getHolesProperties(self.impl,"locationZ2")
    def set_z2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ2",value,highlight)

####### Hole axis (not for te groove)
#       parametric mode
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)
#       rthz mode
    def get_r_axis(self):
        return a5_getHolesProperties(self.impl,"axisR")
    def set_r_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisR",value,highlight)
    def get_theta_axis(self):
        return a5_getHolesProperties(self.impl,"axisTH")
    def set_theta_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisTH",value,highlight)
##      def get_z_axis(self):
##              return a5_getHolesProperties(self.impl,"axisZ")
##      def set_z_axis(self,value,highlight=1):
##              return a5_setHolesProperties(self.impl,"axisZ",value,highlight)

####### Holes dimension
    def get_depth(self):
        return a5_getHolesProperties(self.impl,"width")
    def set_depth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"width",value,highlight)
#       circular shape
    def get_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_diameter(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight)

#       rectangular and rounded shape (height also for te groove in parametric mode)
    def get_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)
#               also for te groove  in parametric mode
    def get_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation (not effect for circular and te groove shape)
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)


#------------------------------------------------------------------------------------------------
#---------------------- BLADE HOLES LINE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class HolesLine(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteHoles(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0
    def number_of_holes(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfHolesInLine(parent_row.impl,parent_blade.impl, self.impl)
    def hole(self,i):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return Hole(a5_getHolePointer(parent_row.impl,parent_blade.impl,self.impl,a5_getHoleNameByIndex(parent_row.impl,parent_blade.impl,self.impl,i-1)))
    def getName(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getHolesName(parent_row.impl,parent_blade.impl,self.impl)
    def setName(self,value):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_setHolesName(parent_row.impl,parent_blade.impl,self.impl,value)

    def preview3D(self):
        return a5_viewHolesProperties(self.impl,0)
    def hide2D(self):
        return a5_hideHolesProperties(self.impl)
##################################
####### external file control
##################################
    def exportGeometry(self):
        return exportHolesLine(self.impl,0)
    def exportDefinition(self):
        return exportHolesLine(self.impl,1)
    def defineGeometry(self,fileName):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return setholesGeometryFromFile(parent_row.impl,parent_blade.impl,self.impl,fileName)
##################################
####### Hole line geometry control
##################################
####### Holes number
    def get_holes_number(self):
        return a5_getHolesProperties(self.impl,"number")
    def set_holes_number(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"number",value,highlight,draw)

####### Hole shape
#       shape: circular, oval, rectangular, quadrilateral, circular at TE and groove at TE

    def set_circular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",0,highlight)
    def set_rectangular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",1,highlight)
    def set_oval_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",2,highlight)
    def set_trailing_edge_groove_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",3,highlight)
    def set_trailing_edge_circular_hole_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",4,highlight)
    def set_quadrilateral_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",5,highlight)
    def get_shape(self,highlight=1):
        return a5_getHolesProperties(self.impl,"shape",highlight)

####### Hole location
    def set_location_to_blade_upper_side(self,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"side",0,highlight,draw)
    def set_location_to_blade_lower_side(self,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"side",1,highlight,draw)
#       parametric mode
    def enable_parametric_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",1)
    def get_first_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationStart")
    def set_first_spanwise_parametric_location(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationStart",value,highlight,draw)
    def get_last_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationEnd")
    def set_last_spanwise_parametric_location(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationEnd",value,highlight,draw)
#       all shapes excepted for te groove
    def set_streamwise_location_on_meridional_chord(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationBoth1",value,highlight)
    def set_streamwise_location_from_leading_edge(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationBoth2",value,highlight,draw)
    def set_streamwise_location_from_trailing_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationBoth3",value,highlight)

    def get_first_streamwise_location_on_meridional_chord(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart1")
    def set_first_streamwise_location_on_meridional_chord(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart1",value,highlight)
    def get_first_streamwise_location_from_leading_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart2")
    def set_first_streamwise_location_from_leading_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart2",value,highlight)
    def get_first_streamwise_location_from_trailing_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart3")
    def set_first_streamwise_location_from_trailing_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart3",value,highlight)
    def get_last_streamwise_location_on_meridional_chord(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationEnd1")
    def set_last_streamwise_location_on_meridional_chord(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationEnd1",value,highlight)
    def get_last_streamwise_location_from_leading_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationEnd2")
    def set_last_streamwise_location_from_leading_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationEnd2",value,highlight)
    def get_last_streamwise_location_from_trailing_edge(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationEnd3")
    def set_last_streamwise_location_from_trailing_edge(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationEnd3",value,highlight)
#       xyz mode
    def enable_xyz_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",0)
#           xyz mode  (p1 for te grooves)
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#           xyz mode only for te groove: p2
    def get_x2_location(self):
        return a5_getHolesProperties(self.impl,"locationX2")
    def set_x2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX2",value,highlight)
    def get_y2_location(self):
        return a5_getHolesProperties(self.impl,"locationY2")
    def set_y2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY2",value,highlight)
    def get_z2_location(self):
        return a5_getHolesProperties(self.impl,"locationZ2")
    def set_z2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ2",value,highlight)
#       rthz mode  (
    def enable_mtheta_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",2)
#            rthz mode  (p1 for grooves)
    def get_r_location(self):
        return a5_getHolesProperties(self.impl,"locationR")
    def set_r_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationR",value,highlight)
    def get_theta_location(self):
        return a5_getHolesProperties(self.impl,"locationTH")
    def set_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#            rthz mode only for te groove: p2
    def get_r2_location(self):
        return a5_getHolesProperties(self.impl,"locationR2")
    def set_r2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationR2",value,highlight)
    def get_theta2_location(self):
        return a5_getHolesProperties(self.impl,"locationTH2")
    def set_theta2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH2",value,highlight)
    def get_z2_location(self):
        return a5_getHolesProperties(self.impl,"locationZ2")
    def set_z2_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ2",value,highlight)

####### Hole axis
#       parametric mode
    def enable_parametric_holes_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",1)
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight,draw)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def enable_xyz_holes_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",0)
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)
#       rthz mode
    def enable_rthz_holes_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",2)
    def get_r_axis(self):
        return a5_getHolesProperties(self.impl,"axisR")
    def set_r_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisR",value,highlight)
    def get_theta_axis(self):
        return a5_getHolesProperties(self.impl,"axisTH")
    def set_theta_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisTH",value,highlight)

####### Holes dimension
    def get_depth(self):
        return a5_getHolesProperties(self.impl,"width")
    def set_depth(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"width",value,highlight,draw)
#       circular shape
    def get_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_diameter(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight,draw)

#       rectangular and rounded shape (height also for te groove in parametric mode)
    def get_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)
#               also for te groove  in parametric mode
    def get_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation (not effect for circular and te groove shape)
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)

##################################
####### Hole line mesh control
##################################
####### In Holes grid points numbers
#       circular and rounded shape only
    def get_number_of_points_in_boundary_layer(self):
        return a5_getHolesProperties(self.impl,"numberOfPointAlongHoleRadius1")
    def set_number_of_points_in_boundary_layer(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointAlongHoleRadius1",value,highlight)
#       all shapes
    def get_number_of_points_streamwise(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideStreamwise")
    def set_number_of_points_streamwise(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideStreamwise",value,highlight)
    def get_number_of_points_spanwise(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideSpanwise")
    def set_number_of_points_spanwise(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideSpanwise",value,highlight)
####### Holes's surrounding area grid points numbers
    def get_number_of_points_streamwise_left(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideLeft")
    def set_number_of_points_streamwise_left(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideLeft",value,highlight)
    def get_number_of_points_streamwise_right(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideRight")
    def set_number_of_points_streamwise_right(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideRight",value,highlight)
    def get_number_of_points_spanwise_up(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideUp")
    def set_number_of_points_spanwise_up(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideUp",value,highlight)
    def get_number_of_points_spanwise_down(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideDown")
    def set_number_of_points_spanwise_down(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideDown",value,highlight)
####### In Holes optimization
    def get_number_of_optimization_steps_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingStepsHoles")
    def set_number_of_optimization_steps_inside_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingStepsHoles",value,highlight)
    def get_skewness_control_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingTypeHoles")
    def enable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",1)
    def disable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",0)
####### Surrounding Holes area optimization
    def get_number_of_optimization_steps_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingSteps")
    def set_number_of_optimization_steps_arround_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingSteps",value,highlight)
    def get_skewness_control_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingType")
    def enable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",1)
    def disable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",0)
####### upstream and downstream hole mesh normalized length (>0)
    def get_upstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_upstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio1",value,highlight)
    def get_downstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_downstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio2",value,highlight)
####### hole mesh line shape link to next hole line shape
    def get_hole_line_shape_link_to_next_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToNext")
    def set_hole_line_shape_link_to_next_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToNext",value,highlight)
####### hole mesh line shape link to previous hole line shape
    def get_hole_line_shape_link_to_previous_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToPrevious")
    def set_hole_line_shape_link_to_previous_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToPrevious",value,highlight)
##################################
####### global mesh control
##################################
####### preserved blade to blade bnd layer
    def get_preserved_layers_on_lower_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerHub")
    def set_preserved_layers_on_lower_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerHub",value,highlight)
    def get_preserved_layers_on_upper_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerShroud")
    def set_preserved_layers_on_upper_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerShroud",value,highlight)
####### intersection tolerance
    def get_intersection_tolerance(self):
        return a5_getHolesProperties(self.impl,"holesTolerance")
    def set_intersection_tolerance(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"holesTolerance",value,highlight)

#------------------------------------------------------------------------------------------------
#---------------------- BASIN HOLES LINE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class BasinHole(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteBassinHoles(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0

#       global parameters (apply to all holes)
    def reset_parametrization_up(self):
        return a5_setBassinHolesProperties(self.impl,"parameterAreInitialized_up",0)
    def reset_parametrization_down(self):
        return a5_setBassinHolesProperties(self.impl,"parameterAreInitialized_down",0)
    def get_optimization_steps(self):
        return a5_getBassinHolesProperties(self.impl,"optsmoothingSteps")
    def set_optimization_steps(self,value):
        return a5_setBassinHolesProperties(self.impl,"optsmoothingSteps",value)
    def get_streamwise_mesh_resolution(self):
        return a5_getBassinHolesProperties(self.impl,"basinMeshWithHolesResolution")
    def set_streamwise_mesh_resolution(self,value):
        return a5_setBassinHolesProperties(self.impl,"basinMeshWithHolesResolution",value)
#       hole parameters
    def get_boundary_optimization_steps(self):
        return a5_getBassinHolesProperties(self.impl,"smoothingSteps")
    def set_boundary_optimization_steps(self,value):
        return a5_setBassinHolesProperties(self.impl,"smoothingSteps",value)
    def enable_parametric_location(self):
        return a5_setBassinHolesProperties(self.impl,"locationType",1)
    def enable_XYZ_location(self):
        return a5_setBassinHolesProperties(self.impl,"locationType",0)
    def get_parametric_streamwise_location(self):
        return a5_getBassinHolesProperties(self.impl,"streamwiseLocation1")
    def set_parametric_streamwise_location(self,value):
        return a5_setBassinHolesProperties(self.impl,"streamwiseLocation1",value)
    def get_anchor_points_x_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"locationx")
    def set_anchor_points_x_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"locationx",value)
    def get_anchor_points_y_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"locationy")
    def set_anchor_points_y_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"locationy",value)
    def get_anchor_points_z_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"locationz")
    def set_anchor_points_z_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"locationz",value)
    def get_axis_x_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"axisx")
    def set_axis_x_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"axisx",value)
    def get_axis_y_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"axisx")
    def set_axis_y_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"axisy",value)
    def get_axis_z_coordinate(self):
        return a5_getBassinHolesProperties(self.impl,"axisy")
    def set_axis_z_coordinate(self,value):
        return a5_setBassinHolesProperties(self.impl,"axisz",value)
    def get_number_of_points_on_hole_side(self):
        return a5_getBassinHolesProperties(self.impl,"numberOfPointAlongsize1")
    def set_number_of_points_on_hole_side(self,value):
        return a5_setBassinHolesProperties(self.impl,"numberOfPointAlongsize1",value)
    # for penny and basin hole only
    def get_diameter(self):
        return a5_getBassinHolesProperties(self.impl,"diameter")
    def set_diameter(self,value):
        return a5_setBassinHolesProperties(self.impl,"diameter",value)
    def get_number_of_points_in_bnd_layer(self):
        return a5_getBassinHolesProperties(self.impl,"numberOfPointAlongHoleRadius1")
    def set_number_of_points_in_bnd_layer(self,value):
        return a5_setBassinHolesProperties(self.impl,"numberOfPointAlongHoleRadius1",value)
    def get_parametric_azimutal_deviation(self):
        return a5_getBassinHolesProperties(self.impl,"streamwiseLocation2")
    def set_parametric_azimutal_deviation(self,value):
        return a5_setBassinHolesProperties(self.impl,"streamwiseLocation2",value)
    # for separator only
    def get_width(self):
        return a5_getBassinHolesProperties(self.impl,"size1")
    def set_width(self,value):
        return a5_setBassinHolesProperties(self.impl,"size1",value)
    # for penny only
    def get_rotation_angle(self):
        return a5_getBassinHolesProperties(self.impl,"rotationAngle")
    def set_rotation_angle(self,value):
        return a5_setBassinHolesProperties(self.impl,"rotationAngle",value)


#------------------------------------------------------------------------------------------------
#---------------------- END WALL COOLING HOLE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class EndWallHole(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteEndWallHole(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl)
        self.impl = 0
    def getName(self):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getEndWallHoleName(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl)
    def setName(self,value):
        parent_hole = self.parent()
        if parent_hole == 0 : return 0
        parent_blade = parent_hole.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_setEndWallHoleName(parent_row.impl,parent_blade.impl,parent_hole.impl,self.impl,value)
############################
####### Hole control
############################

####### Hole location
#       xyz mode
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       mtheta mode
    def get_m_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_m_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
    def get_theta_location(self):
        return a5_getHolesProperties(self.impl,"locationTH")
    def set_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH",value,highlight)

####### Hole axis
#       parametric mode
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1,draw=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight,draw)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)

####### Holes sizes
#       circular shape
    def get_holes_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_holes_diameter(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight)

#       rectangular and rounded shape
    def get_holes_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_holes_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)

    def get_holes_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_holes_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)


#------------------------------------------------------------------------------------------------
#---------------------- END WALL COOLING HOLES LINE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class EndWallHolesLine(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteEndWallHoles(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0
    def number_of_holes(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfEndWallHolesInLine(parent_row.impl,parent_blade.impl, self.impl)
    def hole(self,i):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return EndWallHole(a5_getEndWallHolePointer(parent_row.impl,parent_blade.impl,self.impl,a5_getEndWallHoleNameByIndex(parent_row.impl,parent_blade.impl,self.impl,i-1)))
    def getName(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getEndWallHolesName(parent_row.impl,parent_blade.impl,self.impl)
    def setName(self,value):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_setEndWallHolesName(parent_row.impl,parent_blade.impl,self.impl,value)
##################################
####### external file control
##################################
    def exportGeometry(self):
        return exportHolesLine(self.impl,0)
    def exportDefinition(self):
        return exportHolesLine(self.impl,1)
    def defineGeometry(self,fileName):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return setendwallholesGeometryFromFile(parent_row.impl,parent_blade.impl,self.impl,fileName)
#
##################################
####### Hole line geometry control
##################################
####### Holes number
    def get_holes_number(self):
        return a5_getHolesProperties(self.impl,"number")
    def set_holes_number(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"number",value,highlight)

####### Hole shape
#       shape: circular, oval, rectangular or quadrilateral

    def set_circular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",0,highlight)
    def set_rectangular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",1,highlight)
    def set_oval_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",2,highlight)
    def set_quadrilateral_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",5,highlight)
    def get_shape(self,highlight=1):
        return a5_getHolesProperties(self.impl,"shape",highlight)

####### Hole location
#       parametric mode
    def enable_parametric_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",1)
    def get_first_theta_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationStart")
    def set_first_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationStart",value,highlight)
    def get_last_theta_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationEnd")
    def set_last_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationEnd",value,highlight)
    def get_streamwise_location(self):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart1")
    def set_streamwise_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart1",value,highlight)
#       xyz mode
    def enable_xyz_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",0)
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       mtheta mode
    def enable_mtheta_holes_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",2)
    def get_m_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_m_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
    def get_theta_location(self):
        return a5_getHolesProperties(self.impl,"locationTH")
    def set_theta_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationTH",value,highlight)

####### Hole axis
#       parametric mode
    def enable_parametric_holes_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",1)
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def enable_xyz_holes_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",0)
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)

####### Holes sizes
#       circular shape
    def get_holes_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_holes_diameter(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight)

#       rectangular and rounded shape
    def get_holes_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_holes_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)

    def get_holes_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_holes_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)

##################################
####### Hole line mesh control
##################################
#       up and down clsutering relaxation (0: uniform. value>0: clustering*value)
    def get_up_clustering_relaxation(self):
        return a5_getHolesProperties(self.impl,"upClustering")
    def set_up_clustering_relaxation(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"upClustering",value,highlight)
    def get_down_clustering_relaxation(self):
        return a5_getHolesProperties(self.impl,"downClustering")
    def set_down_clustering_relaxation(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"downClustering",value,highlight)
####### In Holes grid points numbers
#       circular and rounded shape only
    def get_number_of_points_in_boundary_layer(self):
        return a5_getHolesProperties(self.impl,"numberOfPointAlongHoleRadius1")
    def set_number_of_points_in_boundary_layer(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointAlongHoleRadius1",value,highlight)
#       all shapes
    def get_number_of_points_streamwise(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideStreamwise")
    def set_number_of_points_streamwise(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideStreamwise",value,highlight)
    def get_number_of_points_azimutal(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideSpanwise")
    def set_number_of_points_azimutal(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideSpanwise",value,highlight)
####### Holes's surrounding area grid points numbers
    def get_number_of_points_streamwise_left(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideLeft")
    def set_number_of_points_streamwise_left(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideLeft",value,highlight)
    def get_number_of_points_streamwise_right(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideRight")
    def set_number_of_points_streamwise_right(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideRight",value,highlight)
    def get_number_of_points_spanwise_up(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideUp")
    def set_number_of_points_spanwise_up(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideUp",value,highlight)
    def get_number_of_points_spanwise_down(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideDown")
    def set_number_of_points_spanwise_down(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideDown",value,highlight)
####### In Holes optimization
    def get_number_of_optimization_steps_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingStepsHoles")
    def set_number_of_optimization_steps_inside_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingStepsHoles",value,highlight)
    def get_skewness_control_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingTypeHoles")
    def enable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",1)
    def disable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",0)
####### Surrounding Holes area optimization
    def get_number_of_optimization_steps_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingSteps")
    def set_number_of_optimization_steps_arround_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingSteps",value,highlight)
    def get_skewness_control_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingType")
    def enable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",1)
    def disable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",0)
####### upstream and downstream hole mesh normalized length (>0)
    def get_upstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_upstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio1",value,highlight)
    def get_downstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_downstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio2",value,highlight)
####### hole mesh line shape link to next hole line shape
    def get_hole_line_shape_link_to_next_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToNext")
    def set_hole_line_shape_link_to_next_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToNext",value,highlight)
####### hole mesh line shape link to previous hole line shape
    def get_hole_line_shape_link_to_previous_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToPrevious")
    def set_hole_line_shape_link_to_previous_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToPrevious",value,highlight)
##################################
####### global mesh control
##################################
####### preserved blade to blade bnd layer
    def get_preserved_layers_on_lower_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerHub")
    def set_preserved_layers_on_lower_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerHub",value,highlight)
    def get_preserved_layers_on_upper_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerShroud")
    def set_preserved_layers_on_upper_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerShroud",value,highlight)
####### intersection tolerance
    def get_intersection_tolerance(self):
        return a5_getHolesProperties(self.impl,"holesTolerance")
    def set_intersection_tolerance(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"holesTolerance",value,highlight)

#------------------------------------------------------------------------------------------------
#---------------------- End Wall Body -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class EndWall(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_deleteRowWall(parent_row.impl,self.impl)
        self.impl = 0

# end wall generation control

    def generate(self):
        a5_generateRowEndWall(self.impl)
    def generate_holes(self):
        a5_generateRowEndWallHoles(self.impl)

# end wall parameters control

    def get_width(self):
        return a5_getEndWallParameters(self.impl,"width")
    def set_width(self,value):
        return a5_setEndWallParameters(self.impl,"width",value)
    def get_number_of_spanwise_points(self):
        return a5_getEndWallParameters(self.impl,"numberOfSpanwisePoints")
    def set_number_of_spanwise_points(self,value):
        return a5_setEndWallParameters(self.impl,"numberOfSpanwisePoints",value)
    def get_number_of_connected_layers(self):
        return a5_getEndWallParameters(self.impl,"numberOfConnectedLayer")
    def set_number_of_connected_layers(self,value):
        return a5_setEndWallParameters(self.impl,"numberOfConnectedLayer",value)
    def get_number_of_optimization_steps(self):
        return a5_getEndWallParameters(self.impl,"optimizationStepsEndWall")
    def set_number_of_optimization_steps(self,value):
        return a5_setEndWallParameters(self.impl,"optimizationStepsEndWall",value)
    def get_multigrid_optimization_status(self):
        return a5_getEndWallParameters(self.impl,"multigridSpeedUpEndWall")
    def enable_multigrid_optimization(self,value):
        return a5_setEndWallParameters(self.impl,"multigridSpeedUpEndWall",1)
    def disable_multigrid_optimization(self,value):
        return a5_setEndWallParameters(self.impl,"multigridSpeedUpEndWall",0)
    def get_generation_type(self):
        return a5_getEndWallParameters(self.impl,"projectionType")
    def set_generation_type(self,value):
        return a5_setEndWallParameters(self.impl,"projectionType",value)

    def number_of_holes_lines(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfEndWallHoles(parent_row.impl, self.impl)
    def add_holes_line(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return EndWallHolesLine(a5_addEndWallHoles(parent_row.impl, self.impl))
    def holes_line(self,i):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        return EndWallHolesLine(a5_getEndWallHolesPointer(parent_row.impl,self.impl,a5_getEndWallHolesNameByIndex(parent_row.impl,self.impl,i-1)))

#------------------------------------------------------------------------------------------------
#---------------------- Cooling Channel  -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class CoolingChannel(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def pinFinsChannel(self,i):
        parent_solid_body = self.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return PinFinsChannel(a5_getInnerPinFinsChannelPointer(parent_row.impl,parent_blade.impl,a5_getInnerPinFinsChannelNameByIndex(parent_row.impl,parent_blade.impl,i-1)))

#------------------------------------------------------------------------------------------------
#---------------------- Pin Fin Channel  -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class PinFinsChannel(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteInnerPinFinsChannel(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0
    def box(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getPinFinsChannelBox(parent_row.impl,parent_blade.impl,self.impl)
    # pinfins type = 0, 1 (grid), 2 (solid) 3 (both)
    # box type 0, 1,2,3
    # box side 0, 1 || 2
    def view_mesh  (self,pinfinstype,boxtype,boxside,clear=1):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_viewPinFinsChannel(parent_row.impl,parent_blade.impl,self.impl,pinfinstype,boxtype,boxside,clear)
    def viewbox(self,side,rep):
        a5_view_pin_fins_box(self.impl,side,rep)
    def hidebox(self):
        a5_hide_pin_fins_box(self.impl)
    def link_geometry(self,curve_names, surface_names):
        curve_pointers = []
        surface_pointers = []
        for i in range(len(curve_names)):
            curve_pointers.append(get_curve_by_name_(AutoGrid_Import_get_geom_(), curve_names[i]))
        for i in range(len(surface_names)):
            surface_pointers.append(get_surf_by_name_(AutoGrid_Import_get_geom_(), surface_names[i]))
        AutoGrid_link_3D_entity_(self.box(), curve_pointers, surface_pointers)
    def edit(self):
        effect3d = TechnologicalEffect3D(self.box())
        technoEffect3d_generate_(effect3d.impl)
        effect3d.start_editing()
    def stop_edit(self):
        effect3d = TechnologicalEffect3D(self.box())
        effect3d.stop_editing()
    def generate(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_generateInnerPinFinsChannel(parent_row.impl,parent_blade.impl,self.impl)
#
    def number_of_pinFins_line(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfInnerPinFins(parent_row.impl,parent_blade.impl,self.impl)
    def add_pinFins_line(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_addInnerPinFins(parent_row.impl,parent_blade.impl,self.impl)
    def pinFins_line(self,i):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_solid_body = parent_channel.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return PinFinsLine(a5_getInnerPinFinsPointer(parent_row.impl,parent_blade.impl,self.impl,a5_getInnerPinFinsNameByIndex(parent_row.impl,parent_blade.impl,self.impl,i-1)))


#------------------------------------------------------------------------------------------------
#---------------------- Pin Fins Line  -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class PinFins(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_pinfinsline = self.parent()
        if parent_pinfinsline == 0 : return 0
        parent_channel = parent_pinfinsline.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteInnerPinFins(parent_row.impl,parent_blade.impl,parent_pinfinsline.impl,self.impl)
        self.impl = 0
    def getName(self):
        parent_pinfinsline = self.parent()
        if parent_pinfinsline == 0 : return 0
        parent_channel = parent_pinfinsline.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getInnerPinFinsName(parent_row.impl,parent_blade.impl,self.impl)
############################
####### Pin fins control
############################

####### pin fins location
#       parametric mode
    def get_first_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationStart")
    def set_first_spanwise_parametric_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationStart",value,highlight)
    def get_last_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationEnd")
    def set_last_spanwise_parametric_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationEnd",value,highlight)
#
    def set_streamwise_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart1",value,highlight)
    def get_streamwise_location(self,highlight=1):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart1")

#       xyz mode
#           xyz mode
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       U,V mode
    def get_U_location(self):
        return a5_getHolesProperties(self.impl,"locationU")
    def set_U_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationU",value,highlight)
    def get_V_location(self):
        return a5_getHolesProperties(self.impl,"locationV")
    def set_V_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationV",value,highlight)

####### pin fins axis
#       parametric mode
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)

####### Holes dimension
    def get_depth(self):
        return a5_getHolesProperties(self.impl,"width")
    def set_depth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"width",value,highlight)
#       circular shape
    def get_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_diameter(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight)
    def get_diameter2(self):
        return a5_getHolesProperties(self.impl,"diameter2")
    def set_diameter2(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter2",value,highlight)

#       rectangular and rounded shape (height also for te groove in parametric mode)
    def get_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)
#               also for te groove  in parametric mode
    def get_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation (not effect for circular and te groove shape)
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)



#------------------------------------------------------------------------------------------------
#---------------------- Pin Fins LINE -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class PinFinsLine(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a5_deleteInnerPinFins(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0
    def number_of_pinFins(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getNumberOfPinFinsInLine(parent_row.impl,parent_blade.impl,parent_channel.impl,self.impl)
    def pinFin(self,i):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        a = PinFins(a5_getPinFinPointer(parent_row.impl,parent_blade.impl,parent_channel.impl,self.impl,a5_getPinFinNameByIndex(parent_row.impl,parent_blade.impl,parent_channel.impl,self.impl,i-1)))
        return a
    def getName(self):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_getInnerPinFinsName(parent_row.impl,parent_blade.impl,self.impl)

    def preview3D(self):
        return a5_viewHolesProperties(self.impl,0)
    def hide3D(self):
        return a5_hideHolesProperties(self.impl)
##################################
####### external file control
##################################
    def exportGeometry(self):
        return exportHolesLine(self.impl,0)
    def exportDefinition(self):
        return exportHolesLine(self.impl,1)
    def defineGeometry(self,fileName):
        parent_channel = self.parent()
        if parent_channel == 0 : return 0
        parent_channel2 = parent_channel.parent()
        if parent_channel2 == 0 : return 0
        parent_solid_body = parent_channel2.parent()
        if parent_solid_body == 0 : return 0
        parent_blade = Blade(get_parent_blade(parent_solid_body.impl))
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        return a5_setpinfinsGeometryFromFile(parent_row.impl,parent_blade.impl,parent_channel.impl,self.impl)
##################################
####### pin fins line geometry control
##################################
####### pin fins number
    def get_pinfins_number(self):
        return a5_getHolesProperties(self.impl,"number")
    def set_pinfins_number(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"number",value,highlight)

####### pin fins shape
#       shape: circular, oval, rectangular, quadrilateral

    def set_circular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",0,highlight)
    def set_rectangular_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",1,highlight)
    def set_oval_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",2,highlight)
    def set_quadrilateral_shape(self,highlight=1):
        return a5_setHolesProperties(self.impl,"shape",5,highlight)
    def get_shape(self,highlight=1):
        return a5_getHolesProperties(self.impl,"shape",highlight)

####### pin fins location
#       parametric mode
    def enable_parametric_pinfins_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",1)
    def get_first_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationStart")
    def set_first_spanwise_parametric_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationStart",value,highlight)
    def get_last_spanwise_parametric_location(self):
        return a5_getHolesProperties(self.impl,"spanwiseLocationEnd")
    def set_last_spanwise_parametric_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseLocationEnd",value,highlight)
#
    def set_streamwise_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseLocationStart1",value,highlight)
    def get_streamwise_location(self,highlight=1):
        return a5_getHolesProperties(self.impl,"streamwiseLocationStart1")

#       xyz mode
    def enable_xyz_pinfins_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",0)
#           xyz mode
    def get_x_location(self):
        return a5_getHolesProperties(self.impl,"locationX")
    def set_x_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationX",value,highlight)
    def get_y_location(self):
        return a5_getHolesProperties(self.impl,"locationY")
    def set_y_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationY",value,highlight)
    def get_z_location(self):
        return a5_getHolesProperties(self.impl,"locationZ")
    def set_z_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationZ",value,highlight)
#       U,V mode
    def enable_UV_pinfins_location(self,highlight=1):
        return a5_setHolesProperties(self.impl,"locationCoordinates",2)
    def get_U_location(self):
        return a5_getHolesProperties(self.impl,"locationU")
    def set_U_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationU",value,highlight)
    def get_V_location(self):
        return a5_getHolesProperties(self.impl,"locationV")
    def set_V_location(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"locationV",value,highlight)

####### pin fins axis
#       parametric mode
    def enable_parametric_pinfins_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",1)
    def get_streamwise_angle(self):
        return a5_getHolesProperties(self.impl,"streamwiseAngle")
    def set_streamwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"streamwiseAngle",value,highlight)
    def get_spanwise_angle(self):
        return a5_getHolesProperties(self.impl,"spanwiseAngle")
    def set_spanwise_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"spanwiseAngle",value,highlight)
#       xyz mode
    def enable_xyz_pinfins_axis(self,highlight=1):
        return a5_setHolesProperties(self.impl,"axisCoordinates",0)
    def get_x_axis(self):
        return a5_getHolesProperties(self.impl,"axisX")
    def set_x_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisX",value,highlight)
    def get_y_axis(self):
        return a5_getHolesProperties(self.impl,"axisY")
    def set_y_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisY",value,highlight)
    def get_z_axis(self):
        return a5_getHolesProperties(self.impl,"axisZ")
    def set_z_axis(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"axisZ",value,highlight)

####### Holes dimension
    def get_depth(self):
        return a5_getHolesProperties(self.impl,"width")
    def set_depth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"width",value,highlight)
#       circular shape
    def get_diameter(self):
        return a5_getHolesProperties(self.impl,"diameter")
    def set_diameter(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter",value,highlight)
    def get_diameter2(self):
        return a5_getHolesProperties(self.impl,"diameter2")
    def set_diameter2(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"diameter2",value,highlight)

#       rectangular and rounded shape (height also for te groove in parametric mode)
    def get_width(self):
        return a5_getHolesProperties(self.impl,"size1")
    def set_width(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size1",value,highlight)
#               also for te groove  in parametric mode
    def get_heigth(self):
        return a5_getHolesProperties(self.impl,"size2")
    def set_heigth(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"size2",value,highlight)

#       quadrilateral shape
    def get_holes_p1x(self):
        return a5_getHolesProperties(self.impl,"p1x")
    def set_holes_p1x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1x",value,highlight)
    def get_holes_p2x(self):
        return a5_getHolesProperties(self.impl,"p2x")
    def set_holes_p2x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2x",value,highlight)
    def get_holes_p3x(self):
        return a5_getHolesProperties(self.impl,"p3x")
    def set_holes_p3x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3x",value,highlight)
    def get_holes_p4x(self):
        return a5_getHolesProperties(self.impl,"p4x")
    def set_holes_p4x(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4x",value,highlight)
    def get_holes_p1y(self):
        return a5_getHolesProperties(self.impl,"p1y")
    def set_holes_p1y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p1y",value,highlight)
    def get_holes_p2y(self):
        return a5_getHolesProperties(self.impl,"p2y")
    def set_holes_p2y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p2y",value,highlight)
    def get_holes_p3y(self):
        return a5_getHolesProperties(self.impl,"p3y")
    def set_holes_p3y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p3y",value,highlight)
    def get_holes_p4y(self):
        return a5_getHolesProperties(self.impl,"p4y")
    def set_holes_p4y(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"p4y",value,highlight)
####### Hole orientation (not effect for circular and te groove shape)
    def get_orientation_angle(self):
        return a5_getHolesProperties(self.impl,"rectangleAngle")
    def set_orientation_angle(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"rectangleAngle",value,highlight)

##################################
####### pin fins line mesh control
##################################
####### In pin fins grid points numbers
#       circular and rounded shape only
    def get_number_of_points_in_boundary_layer(self):
        return a5_getHolesProperties(self.impl,"numberOfPointAlongHoleRadius1")
    def set_number_of_points_in_boundary_layer(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointAlongHoleRadius1",value,highlight)
#       all shapes
    def get_number_of_points_streamwise(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideStreamwise")
    def set_number_of_points_streamwise(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideStreamwise",value,highlight)
    def get_number_of_points_spanwise(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideSpanwise")
    def set_number_of_points_spanwise(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideSpanwise",value,highlight)
####### pin fins's surrounding area grid points numbers
    def get_number_of_points_streamwise_left(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideLeft")
    def set_number_of_points_streamwise_left(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideLeft",value,highlight)
    def get_number_of_points_streamwise_right(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideRight")
    def set_number_of_points_streamwise_right(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideRight",value,highlight)
    def get_number_of_points_spanwise_up(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideUp")
    def set_number_of_points_spanwise_up(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideUp",value,highlight)
    def get_number_of_points_spanwise_down(self):
        return a5_getHolesProperties(self.impl,"numberOfPointSideDown")
    def set_number_of_points_spanwise_down(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"numberOfPointSideDown",value,highlight)
####### In pin fins optimization
    def get_number_of_optimization_steps_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingStepsHoles")
    def set_number_of_optimization_steps_inside_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingStepsHoles",value,highlight)
    def get_skewness_control_inside_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingTypeHoles")
    def enable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",1)
    def disable_skewness_control_inside_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingTypeHoles",0)
####### Surrounding pin fins area optimization
    def get_number_of_optimization_steps_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingSteps")
    def set_number_of_optimization_steps_arround_holes(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"smoothingSteps",value,highlight)
    def get_skewness_control_arround_holes(self):
        return a5_getHolesProperties(self.impl,"smoothingType")
    def enable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",1)
    def disable_skewness_control_arround_holes(self):
        return a5_setHolesProperties(self.impl,"smoothingType",0)
####### upstream and downstream pin fins mesh normalized length (>0)
    def get_upstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_upstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio1",value,highlight)
    def get_downstream_wake_length(self):
        return a5_getHolesProperties(self.impl,"wakeRatio1")
    def set_downstream_wake_length(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"wakeRatio2",value,highlight)
####### pin fins mesh line shape link to next pin fins line shape
    def get_hole_line_shape_link_to_next_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToNext")
    def set_hole_line_shape_link_to_next_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToNext",value,highlight)
####### hole mesh line shape link to previous hole line shape
    def get_hole_line_shape_link_to_previous_hole_line_shape(self):
        return a5_getHolesProperties(self.impl,"lineShapeLinkToPrevious")
    def set_hole_line_shape_link_to_previous_hole_line_shape(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"lineShapeLinkToPrevious",value,highlight)
##################################
####### global mesh control
##################################
####### preserved blade to blade bnd layer
    def get_preserved_layers_on_lower_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerHub")
    def set_preserved_layers_on_lower_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerHub",value,highlight)
    def get_preserved_layers_on_upper_side(self):
        return a5_getHolesProperties(self.impl,"untouchedLayerShroud")
    def set_preserved_layers_on_upper_side(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"untouchedLayerShroud",value,highlight)
####### intersection tolerance
    def get_intersection_tolerance(self):
        return a5_getHolesProperties(self.impl,"holesTolerance")
    def set_intersection_tolerance(self,value,highlight=1):
        return a5_setHolesProperties(self.impl,"holesTolerance",value,highlight)

#------------------------------------------------------------------------------------------------
#---------------------- ROW WIZARD -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class RowWizard(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer

# row wizard initialization: 4 args given
# machine_type:         generic type of the machine
#                       1: wind turbine
#                       2: axial turbine
#                       3: francis turbine
#                       4: kaplan turbine
#                       5: inducer
#                       6: axial compressor
#                       7: centrifugal impeller
#                       8: centrifugal diffuser
#                       9: return channel
#                       10: contra rotating fan
#                       11: shf pump
#                       12: axial fan
#                       13: marine propeller
#                       14: xxx (under specific licence)
# row_type:             stator:0, rotor:1
# rotationSpeed
# periodicity
# backward wind turbine wizard initialization, should not be used anymore, should use initializeChannel instead:
# 7 args given, shroudRmax,hubRmin,Zmin,Zmax,RFarField,flowPathNumberFarField,cstCellFarField
    def initialize(self, *args):
        if len(args) == 4:
            parent_row = self.parent()
            if parent_row == 0 : return 0

            machine_type, row_type, rotationSpeed, periodicity = args[0], args[1], args[2], args[3]
            setRowWizardType(parent_row.impl,machine_type,row_type,rotationSpeed,periodicity)
        elif len(args) == 7:
            self.initializeChannel(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
            
# shroudRmax:           relative shroud distance to the real tip of the blade (default 1)
# hubRmin:              relative hub distance to the real hub of the blade (default 0)
# Zmin:                 relative inlet length (in blade height unit)
# Zmax:                 relative outlet length (in blade height unit)
# RFarField:            relative far field height (in blade height unit)
# flowPathNumberFarField: number of points in far field
# cstCellFarField:      % of constant cell number in far field
    def initializeChannel(self,shroudRmax,hubRmin,Zmin,Zmax,RFarField,flowPathNumberFarField,cstCellFarField):
        setRowWizardParameters_py(self.impl,"shroudRmax",shroudRmax)
        setRowWizardParameters_py(self.impl,"hubRmin",hubRmin)
        setRowWizardParameters_py(self.impl,"Zmin",Zmin)
        setRowWizardParameters_py(self.impl,"Zmax",Zmax)
        setRowWizardParameters_py(self.impl,"RFarField",RFarField)
        setRowWizardParameters_py(self.impl,"flowPathNumberFarField",flowPathNumberFarField)
        setRowWizardParameters_py(self.impl,"cstCellFarField",cstCellFarField)
        
    def copy(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        a5_copy_topology_(parent_row.impl,"0")
    def paste(self,switchOffOpti=0):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        unselect_all()
        parent_row.select()
        a5_pasteRowWizard(parent_row.impl,switchOffOpti)
    def generate(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        unselect_all()
        parent_row.select()
        a5_generateRowWizard(parent_row.impl)
        a5_tclCommand("cursor_arrow")
    def get_wizard_type(self):
        return getRowWizardParameters_py(self.impl,"wizardType")
    def get_blade_tip_rounded_topology(self):
        return getRowWizardParameters_py(self.impl,"bladeTipRoundedTopology")
    def set_blade_tip_rounded_topology(self,value):
        setRowWizardParameters_py(self.impl,"bladeTipRoundedTopology",value)
    def get_reset_hub_shroud(self):
        return getRowWizardParameters_py(self.impl,"resetHubShroud")
    def set_reset_hub_shroud(self,value):
        setRowWizardParameters_py(self.impl,"resetHubShroud",value)
    def get_R_hub(self):
        return getRowWizardParameters_py(self.impl,"hubRmin")
    def set_R_hub(self,value):
        setRowWizardParameters_py(self.impl,"hubRmin",value)
    def get_R_shroud(self):
        return getRowWizardParameters_py(self.impl,"shroudRmax")
    def set_R_shroud(self,value):
        setRowWizardParameters_py(self.impl,"shroudRmax",value)
    def get_R_far_field(self):
        return getRowWizardParameters_py(self.impl,"RFarField")
    def set_R_far_field(self,value):
        setRowWizardParameters_py(self.impl,"RFarField",value)
    def set_R_far_field_demo(self,value):
        setGlobalRowWizardParameters(self.impl,"RFarField",value)
    def get_hub_location(self):
        return getRowWizardParameters_py(self.impl,"hubRmin")
    def set_hub_location(self,value):
        setRowWizardParameters_py(self.impl,"hubRmin",value)
    def get_shroud_location(self):
        return getRowWizardParameters_py(self.impl,"shroudRmax")
    def set_shroud_location(self,value):
        setRowWizardParameters_py(self.impl,"shroudRmax",value)
    def get_upstream_channel_location(self):
        return getRowWizardParameters_py(self.impl,"Zmin")
    def set_upstream_channel_location(self,value):
        setRowWizardParameters_py(self.impl,"Zmin",value)
    def get_downstream_channel_location(self):
        return getRowWizardParameters_py(self.impl,"Zmax")
    def set_downstream_channel_location(self,value):
        setRowWizardParameters_py(self.impl,"Zmax",value)
    
    def get_grid_level(self):
        return getRowWizardParameters_py(self.impl,"gridLevel")
    def set_grid_level(self,value):
        setRowWizardParameters_py(self.impl,"gridLevel",value)
    def get_flow_path_number_far_field(self):
        return getRowWizardParameters_py(self.impl,"flowPathNumberFarField")
    def set_flow_path_number_far_field(self,value):
        setRowWizardParameters_py(self.impl,"flowPathNumberFarField",value)
    def set_flow_path_number_far_field_demo(self,value):
        setGlobalRowWizardParameters(self.impl,"flowPathNumberFarField",value)
    def get_cst_cell_number_far_field(self):
        return getRowWizardParameters_py(self.impl,"cstCellFarField")
    def set_cst_cell_number_far_field(self,value):
        setRowWizardParameters_py(self.impl,"cstCellFarField",value)
    def set_cst_cell_number_far_field_demo(self,value):
        setGlobalRowWizardParameters(self.impl,"cstCellFarField",value)
    def get_flow_path_number(self):
        return getRowWizardParameters_py(self.impl,"flowPathNumber")
    def set_flow_path_number(self,value):
        setRowWizardParameters_py(self.impl,"flowPathNumber",value)
    def set_flow_path_number_demo(self,value):
        setGlobalRowWizardParameters(self.impl,"radialPointNumber",value)
    def get_number_of_points(self):
        return rowWizard_getNpts(self.impl)
    def get_full_matching_topology(self):
        return getRowWizardParameters_py(self.impl,"fullMatching")
    def set_full_matching_topology(self,value):
        setRowWizardParameters_py(self.impl,"fullMatching",value)
    def set_full_matching_topology_demo(self,value):
        setRowWizardParameters(self.impl,"fullMatching",value)
    def get_row_cell_width_at_wall(self):
        return getRowWizardParameters_py(self.impl,"rowClustering")
    def set_row_cell_width_at_wall(self,value):
        setRowWizardParameters_py(self.impl,"rowClustering",value)
    def set_row_cell_width_at_wall_demo(self,value):
        setRowWizardParameters(self.impl,"rowClustering",value)
    def is_hub_gap_asked(self):
        return getRowWizardParameters_py(self.impl,"hubGap")
    def hub_gap_is_asked(self,value):
        setRowWizardParameters_py(self.impl,"hubGap",value)
    def hub_gap_is_asked_demo(self,value):
        setRowWizardParameters(self.impl,"hubGap",value)
    def is_tip_gap_asked(self):
        return getRowWizardParameters_py(self.impl,"tipGap")
    def tip_gap_is_asked(self,value):
        setRowWizardParameters_py(self.impl,"tipGap",value)
    def tip_gap_is_asked_demo(self,value):
        setRowWizardParameters(self.impl,"tipGap",value)
    def is_hub_fillet_asked(self):
        return getRowWizardParameters_py(self.impl,"hubFillet")
    def hub_fillet_is_asked(self,value):
        setRowWizardParameters_py(self.impl,"hubFillet",value)
    def hub_fillet_is_asked_demo(self,value):
        setRowWizardParameters(self.impl,"hubFillet",value)
    def is_tip_fillet_asked(self):
        return getRowWizardParameters_py(self.impl,"tipFillet")
    def tip_fillet_is_asked(self,value):
        setRowWizardParameters_py(self.impl,"tipFillet",value)
    def tip_fillet_is_asked_demo(self,value):
        setRowWizardParameters(self.impl,"tipFillet",value)
    def get_hub_gap_width_at_leading_edge(self):
        return getRowWizardParameters_py(self.impl,"hubControlWidthAtLeadingEdge")
    def set_hub_gap_width_at_leading_edge(self,value):
        setRowWizardParameters_py(self.impl,"hubControlWidthAtLeadingEdge",value)
    def set_hub_gap_width_at_leading_edge_demo(self,value):
        setRowWizardParameters(self.impl,"hubControlWidthAtLeadingEdge",value)
    def get_hub_gap_width_at_trailing_edge(self):
        return getRowWizardParameters_py(self.impl,"hubControlWidthAtTrailingEdge")
    def set_hub_gap_width_at_trailing_edge(self,value):
        setRowWizardParameters_py(self.impl,"hubControlWidthAtTrailingEdge",value)
    def set_hub_gap_width_at_trailing_edge_demo(self,value):
        setRowWizardParameters(self.impl,"hubControlWidthAtTrailingEdge",value)
    def get_tip_gap_width_at_leading_edge(self):
        return getRowWizardParameters_py(self.impl,"tipControlWidthAtLeadingEdge")
    def set_tip_gap_width_at_leading_edge(self,value):
        setRowWizardParameters_py(self.impl,"tipControlWidthAtLeadingEdge",value)
    def set_tip_gap_width_at_leading_edge_demo(self,value):
        setRowWizardParameters(self.impl,"tipControlWidthAtLeadingEdge",value)
    def get_tip_gap_width_at_trailing_edge(self):
        return getRowWizardParameters_py(self.impl,"tipControlWidthAtTrailingEdge")
    def set_tip_gap_width_at_trailing_edge(self,value):
        setRowWizardParameters_py(self.impl,"tipControlWidthAtTrailingEdge",value)
    def set_tip_gap_width_at_trailing_edge_demo(self,value):
        setRowWizardParameters(self.impl,"tipControlWidthAtTrailingEdge",value)

# kept for wind turbine wizard backward. Should not be used anymore
    def delete(self):
        parent_row = self.parent()
        if parent_row == 0 : return 0
        wizardType = self.get_wizard_type()

        if wizardType == 1 or wizardType == 13:
            deleteWindTurbineWizard(parent_row.impl,self.impl)
    def get_hub_cut_relative_value(self):
        return self.get_R_hub()
    def set_hub_cut_relative_value(self,value):
        self.set_R_hub(value)
    def get_tip_cut_relative_value(self):
        return self.get_R_shroud()
    def set_tip_cut_relative_value(self,value):
        self.set_R_shroud(value)
    def get_inlet_width(self):
        return self.get_upstream_channel_location()
    def set_inlet_width(self,value):
        self.set_upstream_channel_location(value)
    def get_outlet_width(self):
        return self.get_downstream_channel_location()
    def set_outlet_width(self,value):
        self.set_downstream_channel_location(value)
    def get_expansion_cst_cell_percentage_number(self):
        return self.get_cst_cell_number_far_field()
    def set_expansion_cst_cell_percentage_number(self,value):
        self.set_cst_cell_number_far_field(value)
    def get_expansion_number_of_layer(self):
        return self.get_flow_path_number_far_field()
    def set_expansion_number_of_layer(self,value):
        self.set_flow_path_number_far_field(value)
    def get_expansion_height(self):
        return self.get_R_far_field()
    def set_expansion_height(self,value):
        self.set_R_far_field(value)
    def get_number_of_layer(self):
        return self.get_flow_path_number()
    def set_number_of_layer(self,value):
        self.set_flow_path_number(value)
    # percentage of constant cells is not a wizard parameter anymore
    def get_cst_cell_percentage_number(self):
        return 0
    def set_cst_cell_percentage_number(self,value):
        # do nothing
        return
        
# for demo purpose only. Should not be used externally
    def start(self):
        self.select()
        a5_start_row_wizard(self.impl)
    def finish(self):
        self.select()
        GlobalRowWizard_finish(self.impl)
    def cancel(self):
        self.select()
        GlobalRowWizard_cancel(self.impl)
    def ok(self):
        self.select()
        GlobalRowWizard_ok(self.impl)
    def selectType(self):
        self.select()
        rowWizard_next(self.impl)
    def next(self):
        self.select()
        GlobalRowWizard_next(self.impl)
    def back(self):
        self.select()
        GlobalRowWizard_back(self.impl)
    def previewB2B(self):
        self.select()
        rowWizard_previewB2B_wizard(self.impl)
    def previewB2B_quick(self,opti=0):
        self.select()
        rowWizard_previewB2B_fast_wizard(self.impl,opti)
       

#------------------------------------------------------------------------------------------------
#---------------------- LETE WIZARD -----------------------------------------------------
#------------------------------------------------------------------------------------------------

class WizardLETE(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def select(self):
        select_(self.impl)
    def delete(self):
        parent_blade = self.parent()
        if parent_blade == 0 : return 0
        parent_row = parent_blade.parent()
        if parent_row == 0 : return 0
        deleteWizardLETE(parent_row.impl,parent_blade.impl,self.impl)
        self.impl = 0
    def generate(self,replace_le=1,replace_te=1):
        WizardLETE_initialize(self.impl)
        WizardLETE_initLayers(self.impl)
        WizardLETE_previewLayers(self.impl)
        WizardLETE_initLETE(self.impl)
        WizardLETE_previewLETE(self.impl)
        WizardLETE_finish(self.impl,replace_le,replace_te)
        WizardLETE_clean(self.impl)

# layerUpstreamLocation: 0->1
# layerDownstreamLocation: 0->1
    def get_layer_upstream_hub_location(self):
        return getWizardLETEParameters_py(self.impl,"layerUpstreamLocationHub")
    def set_layer_upstream_hub_location(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerUpstreamLocationHub",value,update)
    def get_layer_downstream_hub_location(self):
        return getWizardLETEParameters_py(self.impl,"layerDownstreamLocationHub")
    def set_layer_downstream_hub_location(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerDownstreamLocationHub",value,update)
    def get_layer_upstream_shroud_location(self):
        return getWizardLETEParameters_py(self.impl,"layerUpstreamLocationShroud")
    def set_layer_upstream_shroud_location(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerUpstreamLocationShroud",value,update)
    def get_layer_downstream_shroud_location(self):
        return getWizardLETEParameters_py(self.impl,"layerDownstreamLocationShroud")
    def set_layer_downstream_shroud_location(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerDownstreamLocationShroud",value,update)
    def get_layer_hub_clustering(self):
        return getWizardLETEParameters_py(self.impl,"layerHubClustering")
    def set_layer_hub_clustering(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerHubClustering",value,update)
    def get_layer_shroud_clustering(self):
        return getWizardLETEParameters_py(self.impl,"layerShroudClustering")
    def set_layer_shroud_clustering(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerShroudClustering",value,update)
    def get_layer_number(self):
        return getWizardLETEParameters_py(self.impl,"layerNumber")
    def set_layer_number(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerNumber",value,update)
    def get_layer_number_of_control_points(self):
        return getWizardLETEParameters_py(self.impl,"layerNpts")
    def set_layer_number_of_control_points(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerNpts",value,update)
    def get_layer_number_of_constant_cells(self):
        return getWizardLETEParameters_py(self.impl,"layerNcst")
    def set_layer_number_of_constant_cells(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"layerNcst",value,update)
    def is_last_section_used(self):
        return getWizardLETEParameters_py(self.impl,"useLastSection")
    def last_section_is_used(self):
        setWizardLETEParameters_py(self.impl,"useLastSection",1)
    def last_section_is_not_used(self):
        setWizardLETEParameters_py(self.impl,"useLastSection",0)
    def is_first_section_used(self):
        return getWizardLETEParameters_py(self.impl,"useFirstSection")
    def first_section_is_used(self):
        setWizardLETEParameters_py(self.impl,"useFirstSection",1)
    def first_section_is_not_used(self):
        setWizardLETEParameters_py(self.impl,"useFirstSection",0)
    def get_blade_type(self):
        return getWizardLETEParameters_py(self.impl,"highstaggered")
    def set_blade_normal_type(self):
        setWizardLETEParameters_py(self.impl,"highstaggered",0)
    def set_blade_very_low_angle_type(self):
        setWizardLETEParameters_py(self.impl,"highstaggered",1)
    def set_blade_very_high_angle_type(self):
        setWizardLETEParameters_py(self.impl,"highstaggered",2)
    def get_hub_expansion(self):
        return getWizardLETEParameters_py(self.impl,"leadingEdgeHubExtension")
    def set_hub_expansion(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"leadingEdgeHubExtension",value,update)
    def get_shroud_expansion(self):
        return getWizardLETEParameters_py(self.impl,"leadingEdgeShroudExtension")
    def set_shroud_expansion(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"leadingEdgeShroudExtension",value,update)
    def get_leading_edge_location(self,layer):
        return getWizardLETEParameters_py(self.impl,"leadingEdgeLocation",layer)
    def set_leading_edge_location(self,layer,value,update=0):
        setWizardLETEParameters_py(self.impl,"leadingEdgeLocation",layer,value,update)
    def get_trailing_edge_location(self,layer):
        return getWizardLETEParameters_py(self.impl,"trailingEdgeLocation",layer)
    def set_trailing_edge_location(self,layer,value,update=0):
        setWizardLETEParameters_py(self.impl,"trailingEdgeLocation",layer,value,update)
    def get_chord_tolerance_at_le(self):
        return getWizardLETEParameters_py(self.impl,"chordToleranceLE")
    def set_chord_tolerance_at_le(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"chordToleranceLE",value,update)
    def get_chord_tolerance_at_te(self):
        return getWizardLETEParameters_py(self.impl,"chordToleranceTE")
    def set_chord_tolerance_at_te(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"chordToleranceTE",value,update)
    def get_iteration_steps(self):
        return getWizardLETEParameters_py(self.impl,"iterationSteps")
    def set_iteration_steps(self,value,update=0):
        setWizardLETEParameters_py(self.impl,"iterationSteps",value,update)


    def set_active_layer(self,index):
        setWizardLETEParameters_py(self.impl,"layer",index)
    def get_number_of_control_point(self):
        return getWizardLETEParameters_py(self.impl,"numberOfControlPoints")
    def get_point_leading_edge_xyz (self,index)     :
        list = getWizardLETEParameters_py(self.impl,"le_xyz",index)
        return Point(list[0],list[1],list[2])
    def get_point_trailing_edge_xyz (self,index)    :
        list = getWizardLETEParameters_py(self.impl,"te_xyz",index)
        return Point(list[0],list[1],list[2])
    def get_point_leading_edge_mt (self,index)      :
        list = getWizardLETEParameters_py(self.impl,"le_mt",index)
        return Point(list[0],list[1],list[2])
    def get_point_trailing_edge_mt (self,index)     :
        list = getWizardLETEParameters_py(self.impl,"te_mt",index)
        return Point(list[0],list[1],list[2])

    def start(self):
        self.select()
        WizardLETE_start(self.impl)
    def cancel(self):
        self.select()
        WizardLETE_cancel(self.impl)
    def ok(self):
        self.select()
        WizardLETE_ok(self.impl)
    def next(self):
        self.select()
        WizardLETE_next(self.impl)
    def back(self):
        self.select()
        WizardLETE_back(self.impl)
    def finish(self):
        self.select()
        WizardLETE_finish(self.impl)

#------------------------------------------------------------------------------------------------
#---------------------- ACOUSTIC WIZARD -----------------------------------------------------
#------------------------------------------------------------------------------------------------
# This class is just an API and does not hold a specific object pointer, self is the row itself

class RowAcousticWizard(NIConfigurationEntities):
    def __init__(self,pointer):
        self.impl = pointer
    def set_max_span_cell_size(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "maxSpanCellSize", value)
    def set_max_span_cell_size_in_far_field(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "maxSpanCellSizeInFarField", value)
    def set_max_B2B_cell_size(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "maxB2BCellSize", value)
    def set_max_stream_cell_size_upstream_downstream(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "maxStreamCellSizeUpstreamDownstream", value)
    def set_max_stream_cell_size_in_bulb(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "maxStreamCellSizeInBulb", value)
    def set_far_field_reference_layer(self, value):
        a5_set_acoustic_wizard_parameters_(self.impl, "farFieldReferenceLayer", value)

    def get_max_span_cell_size(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[0]
    def get_max_span_cell_size_in_far_field(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[1]
    def get_max_B2B_cell_size(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[2]
    def get_max_stream_cell_size_upstream_downstream(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[3]
    def get_max_stream_cell_size_in_bulb(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[4]
    def get_far_field_reference_layer(self):
        param_list = a5_get_acoustic_wizard_parameters_(self.impl)
        return param_list[5]

    def compute_number_of_points(self):
        error_message = a5_apply_acoustic_wizard_(self.impl)
        return error_message
    def compute_spanwise_number_of_points(self):
        error_message = a5_compute_spanwise_npts_to_respect_max_cell_size_(self.impl)
        return error_message
    def compute_spanwise_farfield_number_of_points(self):
        error_message = a5_compute_spanwise_farfield_npts_to_respect_max_cell_size_(self.impl)
        return error_message
    def compute_B2B_number_of_points(self):
        error_message = a5_compute_B2B_npts_to_respect_max_cell_size_(self.impl)
        return error_message
    def compute_streamwise_bulb_number_of_points(self):
        error_message = a5_compute_streamwise_bulb_npts_to_respect_max_cell_size_(self.impl)
        return error_message
    
