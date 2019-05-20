import pymel.core as pm
import logging
import os
import maya.mel as mel
import maya.cmds as mc
from PySide2 import QtWidgets


ATTRIBUTEPROJECT = 'EZSurfacing_project'
ATTRIBUTETEXTUREOBJECT = 'EZSurfacing_object'

def EZSurfacingInit():
    ''' Initializes the scene by creating the EZSurfacing root
    an EZSurfacing object, and runs the validation to create and
    connect the partition'''
    root = create_project_root()
    if not root.members:
        EZProject = create_project ('project')
        EZObject = create_object(EZProject, 'default_object')
    validate_scene()

def create_project_root_node():
    '''create projects root node'''
    EZSurfacing_root = pm.createNode('objectSet', name='EZSurfacing_root')
    EZSurfacing_root.setAttr('EZSurfacing_root','', force=True)
    return EZSurfacing_root


def create_project_root():
    '''create projects root if it doesnt exist'''
    if not get_project_root():
        EZSurfacing_root = create_project_root_node()
        return EZSurfacing_root
    else:
        return get_project_root()

def create_project(name=None):
    '''Creates a EZSurfacing project'''
    if not name:
        name= 'project'
    EZSurfacing_project = pm.createNode('objectSet', name=name)
    EZSurfacing_project.setAttr(ATTRIBUTEPROJECT,'', force=True)
    create_object(EZSurfacing_project)
    get_project_root().add(EZSurfacing_project)
    update_partition()
    return EZSurfacing_project

def create_object(project, name=None):
    '''Creates a EZSurfacing Object under a given project'''
    if get_project_root() and is_project(project):
        if not name:
            name='object'
        EZSurfacing_set = pm.createNode('objectSet', name=name)
        EZSurfacing_set.setAttr(ATTRIBUTETEXTUREOBJECT,'', force=True)
        project.add(EZSurfacing_set)
    else:
        raise Exception('No project root, or project given is not valid')

def update_partition():
    '''Recreates the partition node, and reconnects to all the EZSurfacing nodes'''
    partitions = [item for item in pm.ls(type='partition') if item.hasAttr('EZSurfacing_partition')]
    for each in partitions:
        logging.info('disconnecting existing partition: %s' % each)
        each.sets.disconnect() 
        pm.delete(each)
        logging.info('deleted partition')
    EZSurfacing_partition = pm.createNode('partition', name='EZSurfacing_partition')
    logging.info('partition created: %s' % EZSurfacing_partition)
    EZSurfacing_partition.setAttr('EZSurfacing_partition','', force=True)
    for project in get_projects():
        for object in get_objects(project):
            pm.connectAttr('%s.partition'%object, EZSurfacing_partition.sets, na=True)
            logging.info('partition connected: %s ' % object)
    pass

def get_project_root():
    '''Gets the project root node''' 
    objSetLs = [item for item in pm.ls(type='objectSet') if item.hasAttr('EZSurfacing_root')]
    if len(objSetLs) == 0:
        logging.info('EZSurfacing_root node found, creating one')
        return create_project_root_node()
    elif len(objSetLs) > 1:
        raise Exception('more than 1 EZSurfacing_root node found')
    return objSetLs[0]

def get_projects():
    '''Gets all EZSurfacing Projects under the root'''
    objSetLs = [item for item in pm.ls(type='objectSet') if item.hasAttr(ATTRIBUTEPROJECT)]
    return objSetLs

def get_objects(project):
    '''Gets all EZSurfacing Objects under the given project'''
    if is_project(project):
        return project.members()
    else:
        return []

def is_project(project):
    '''Returns is project is of the type EZSurfacing project'''
    if project.hasAttr(ATTRIBUTEPROJECT):
        return True
    else:
        return False

def is_texture_object(texture_object):
    '''Returns is project is of the type EZSurfacing Object'''
    if texture_object.hasAttr(ATTRIBUTETEXTUREOBJECT):
        return True
    else:
        return False

def remove_invalid_members():
    '''pops all not-allowd member types
    Allowed:
     objectSets inside the project_root
     objectSets inside each texture_project
     transforms (that have a mesh) inside texture_objects'''
    project_root = get_project_root()
    for project in project_root.members():
        if not project.type() == 'objectSet': #add check for attr
            project_root.removeMembers([project])
    for project in get_projects():
        for object in get_objects(project): #add check for attr
            if not object.type() == 'objectSet':
                project.removeMembers([object])
            else:
                for member in object.members():
                    if not member.type() == 'transform':
                        logging.info('removing invalid member: %s' % member)
                        object.removeMembers([member])
                    elif not member.listRelatives(type='mesh'):
                        logging.info('removing invalid member: %s' % member)
                        object.removeMembers([member])


def get_mesh_transforms(object_list):
    '''Gets all the mesh shape transforms'''
    shapes_in_hierarchy = pm.listRelatives(object_list, allDescendents=True, path= True,f=True, type='mesh')
    shapes_transforms = pm.listRelatives(shapes_in_hierarchy, p=True,path=True,f=True)
    return shapes_transforms

def add_member(texture_object, transform):
    '''Adds the transform to the EZSurfacing Object'''
    pm.sets( texture_object, transform, fe=True)

def add_mesh_transforms_to_object(texture_object, object_list):
    '''Adds all mesh shape transforms from the object list to a EZSurfacing Object'''
    pm.select()
    if texture_object and object_list:
        if is_texture_object(texture_object):
            for item in object_list:
                for transform in get_mesh_transforms(item):
                    pm.select(transform)
                    add_member(texture_object, transform)

def validate_scene():
    '''Removes not allowed or invalid members, updates the partition
    and the meshes attributes'''
    if get_project_root:
        remove_invalid_members()
        update_partition()
        update_mesh_attributes()
    #check all object sets of type texture_object contain only shapes
    pass


def export_project(project, subdiv= 1, single_export=True):
    '''Export EZSurfacing Project'''
    current_file = pm.sceneName()
    if single_export:
        check_scene_state()
    root = get_project_root()
    path = root.EZSurfacing_root.get()
    if os.path.exists(path) and os.path.isdir(path):
        project_geo_list = []
        if is_project(project): #add check isDirectory
            for each in get_objects(project):
                merged_geo = merge_texture_object(each)
                if merged_geo:
                    project_geo_list.append(merged_geo)
            #AbcExport -j '-frameRange 0 0 -uvWrite -dataFormat ogawa -root |cabin|Geom|armchair|Chair|Geom|back -file /home/ezequielm/Desktop/adsdas.abc';
            if project_geo_list:
                export_roots = ' -root |' +' -root |'.join([ str(x) for x in project_geo_list ])
                if subdiv:
                    for geo in project_geo_list:
                        logging.info('subdivision level: %s' % subdiv)
                        logging.info('subdividing merged members: %s' % geo)
                        #-mth 0 -sdt 2 -ovb 1 -ofb 3 -ofc 0 -ost 0 -ocr 0 -dv 3 -bnr 1 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 1 -peh 0 -sl 1 -dpe 1 -ps 0.1 -ro 1 -ch 1
                        pm.polySmooth(geo, mth=0,sdt=2, ovb=1, dv= subdiv)
                export_file_path = os.path.join(path, str(project) + ".abc")
                mel_cmd = 'AbcExport -j "-frameRange 0 0 -uvWrite -dataFormat ogawa -attrPrefix EZ ' + export_roots + " -file " + (export_file_path + '"')
                mel.eval(mel_cmd)
                logging.info('Succesful export to: %s' % export_file_path)
    if single_export:
        pm.openFile(current_file, force=True)
    #pm.undo()

def merge_texture_object(texture_object):
    '''Merges all the meshs assigned to a EZSurfacing Object for export'''
    try:
        members = texture_object.members()
        logging.info('Merging members: %s' % members)
        geo_name = '%s_geo' % str(texture_object)
        if len(members) > 1:
            geo = pm.polyUnite(*members, n=geo_name)
            return geo [0]
        else:
            logging.info('single object found, skipping merge: %s' % members[0])
            members[0].rename(geo_name)
            pm.parent(members[0], world=True)
            return members[0]
    except:
        logging.error('Could not merge members of: %s' % texture_object)
        return False

def export_all_projects(subdiv=1):
    '''Export all EZSurfacing Projects'''
    check_scene_state()
    current_file = pm.sceneName()
    for project in get_projects():
        export_project(project, subdiv=subdiv,single_export=False)
    pm.openFile(current_file, force=True)
    return True

def check_scene_state():
    if unsaved_scene():
        if save_scene_dialog():
            pm.saveFile(force=True)
        else:
            raise ValueError('Unsaved changes')

def update_mesh_attributes():
    '''Adds the attributes to all the shapes transforms assigned to EZSurfacing Objects
    This will be used later for quick shader/material creation and assignment'''
    for project in get_projects():
        project.setAttr(ATTRIBUTEPROJECT, project)
        logging.info('Updating attributes for project: %s' % project)
        for texture_object_set in get_objects(project):
            logging.info('----Updating attributes for object texture set: %s' % texture_object_set)
            texture_object_set.setAttr(ATTRIBUTETEXTUREOBJECT, texture_object_set)
            members = texture_object_set.members()
            logging.info('--------Updating mesh for meshes:')
            logging.info('--------%s' % members)
            for member in members:
                member.setAttr(ATTRIBUTEPROJECT,project.name(),force=True)
                member.setAttr(ATTRIBUTETEXTUREOBJECT,texture_object_set.name(),force=True)

def unsaved_scene():
    import maya.cmds as cmds
    return cmds.file(q=True, modified=True)

def save_scene_dialog():
    """
    If the scene has unsaved changes, it will ask the user to go ahead save or cancel
    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)

    msg.setText("Your scene has unsaved changes")
    msg.setInformativeText("")
    msg.setWindowTitle("Warning")
    msg.setDetailedText("This tool will do undoable changes. It requires you to save your scene, and reopen it after its finished")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    retval = msg.exec_()
    if retval == QtWidgets.QMessageBox.Ok:
        return True
    else:
        return False