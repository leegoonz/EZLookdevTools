import logging
import pymel.core as pm
from PySide2 import QtGui, QtWidgets, QtWidgets, QtUiTools
from maya_toolkit.app.general.mayaMixin import MayaQWidgetDockableMixin
import os

import maya_toolkit.maya_main as maya_main

logger = logging.getLogger(__name__)


class MainWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        # Main widget
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        project_btns_layout = QtWidgets.QHBoxLayout()
        object_btns_layout = QtWidgets.QHBoxLayout()
        selection_layout = QtWidgets.QHBoxLayout()
        self.setWindowTitle("maya_main")

        main_widget.closeEvent = self.close
        # Create UI widgets
        self.refresh = QtWidgets.QPushButton("refresh")
        self.btn_set_path = QtWidgets.QPushButton("set path")
        self.lbl_path = QtWidgets.QLabel("export path")
        self.path = QtWidgets.QLabel("")
        self.sync_selection = QtWidgets.QCheckBox("Sync object set selection")
        self.expand_selection = QtWidgets.QCheckBox("expand selection to members")
        self.project_new_btn = QtWidgets.QPushButton("new texture project")
        self.project_delete_btn = QtWidgets.QPushButton("delete texture project")
        self.list_projects = QtWidgets.QListWidget(self)
        self.list_projects.setSortingEnabled(True)
        self.btn_new_texture_object = QtWidgets.QPushButton("new texture object")
        self.btn_delete_texture_object = QtWidgets.QPushButton("delete texture object")
        self.btn_add_to_texture_object = QtWidgets.QPushButton(
            "add selected to texture object"
        )
        self.list_texture_objects = QtWidgets.QListWidget(self)
        self.list_texture_objects.setSortingEnabled(True)
        self.lbl_validate_scene = QtWidgets.QLabel("validation")
        self.btn_validate_scene = QtWidgets.QPushButton("validate scene")
        self.lbl_wireframe = QtWidgets.QLabel("wireframe colors")
        self.btn_wireframe_color_projects = QtWidgets.QPushButton(
            "per Surfacing Project"
        )
        self.btn_wireframe_color_objects = QtWidgets.QPushButton("per Surfacing Object")
        self.lbl_materials = QtWidgets.QLabel("material colors")
        self.btn_material_color_objects = QtWidgets.QPushButton("per Surfacing Object")
        self.btn_wireframe_color_none = QtWidgets.QPushButton("Remove")
        self.lbl_export = QtWidgets.QLabel("Project Export")
        self.btn_export_project = QtWidgets.QPushButton("Selected")
        self.btn_export_all = QtWidgets.QPushButton("All")

        maya_main.EZSurfacingInit()
        self.update_ui_projects()

        # TODO
        # To remove the manually refesh button
        # Need to add this to maya as selection changed callback to
        # update the UI avoiding validating the scene
        # import maya.OpenMaya as OpenMaya
        # idx = OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.update_ui_projects
        # OpenMaya.MMessage.removeCallback(idx)

        # Attach widgets to the main layout
        main_layout.addWidget(self.refresh)
        main_layout.addWidget(self.lbl_path)
        main_layout.addWidget(self.btn_set_path)
        main_layout.addWidget(self.path)
        main_layout.addLayout(selection_layout)
        selection_layout.addWidget(self.sync_selection)
        selection_layout.addWidget(self.expand_selection)
        main_layout.addLayout(project_btns_layout)
        project_btns_layout.addWidget(self.project_new_btn)
        project_btns_layout.addWidget(self.project_delete_btn)
        main_layout.addWidget(self.list_projects)
        main_layout.addLayout(object_btns_layout)
        object_btns_layout.addWidget(self.btn_new_texture_object)
        object_btns_layout.addWidget(self.btn_delete_texture_object)
        main_layout.addWidget(self.list_texture_objects)
        main_layout.addWidget(self.btn_add_to_texture_object)
        main_layout.addWidget(self.lbl_wireframe)
        main_layout.addWidget(self.btn_wireframe_color_projects)
        main_layout.addWidget(self.btn_wireframe_color_objects)
        main_layout.addWidget(self.btn_wireframe_color_none)
        main_layout.addWidget(self.lbl_materials)
        main_layout.addWidget(self.btn_material_color_objects)
        main_layout.addWidget(self.lbl_validate_scene)
        main_layout.addWidget(self.btn_validate_scene)
        main_layout.addWidget(self.lbl_export)
        main_layout.addWidget(self.btn_export_project)
        main_layout.addWidget(self.btn_export_all)

        # Set main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect buttons signals
        self.refresh.clicked.connect(self.update_ui_projects)
        self.btn_set_path.clicked.connect(self.set_path)
        self.project_new_btn.clicked.connect(self.create_project)
        self.project_delete_btn.clicked.connect(self.delete_project)
        self.list_projects.itemClicked.connect(self.update_ui_texture_objects)
        self.list_projects.itemDoubleClicked.connect(self.editItem)
        self.btn_new_texture_object.clicked.connect(self.create_texture_object)
        self.btn_delete_texture_object.clicked.connect(self.delete_texture_object)
        self.btn_add_to_texture_object.clicked.connect(self.add_to_texture_object)
        self.btn_validate_scene.clicked.connect(self.validate_scene)
        self.btn_wireframe_color_projects.clicked.connect(
            maya_main.set_wireframe_colors_per_project
        )
        self.btn_wireframe_color_objects.clicked.connect(
            maya_main.set_wireframe_colors_per_object
        )
        self.btn_wireframe_color_none.clicked.connect(
            maya_main.set_wifreframe_color_none
        )
        self.btn_material_color_objects.clicked.connect(
            maya_main.set_materials_per_object
        )
        self.list_texture_objects.itemClicked.connect(self.select_texture_object)
        self.list_texture_objects.itemDoubleClicked.connect(self.editItem)

        self.btn_export_project.clicked.connect(self.export_project)
        self.btn_export_all.clicked.connect(self.export_all_projects)

    def close(self):
        """Function to call on panel close"""
        pass

    def editItem(self, item):
        item_object_set = pm.PyNode(str(item.text()))
        text, okPressed = QtWidgets.QInputDialog.getText(
            self, "", "rename to:", QtWidgets.QLineEdit.Normal, str(item.text())
        )
        if okPressed and text != "":
            logging.info("renaming objsetSet %s to %s" % (item.text(), text))
            try:
                pm.rename(item_object_set, text)
            except:
                pass
            finally:
                self.update_ui_projects()

    def delete_project(self):
        selected_project = pm.PyNode(self.list_projects.currentItem().text())
        maya_main.delete_project(selected_project)
        self.update_ui_projects()

    def select_texture_object(self, item):
        """selects the texture object on the scene"""
        selected_texture_object = pm.PyNode(str(item.text()))
        if self.sync_selection.isChecked():
            pm.select(selected_texture_object, ne=True)
            if self.expand_selection.isChecked():
                pm.select(selected_texture_object)

    def set_path(self):
        """sets the EZTool texture root path attribute to where to export"""
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        if file_dialog.exec_():
            root = maya_main.get_project_root()
            path = str(file_dialog.selectedFiles()[0])
            pm.setAttr("%s.EZSurfacing_root" % root, path)
            self.path.setText(os.path.basename(path))

    def create_project(self):
        """Initializes the scene with the required nodes"""
        root = maya_main.create_project()
        self.update_ui_projects()

    def create_texture_object(self):
        """Creates a new texture object set"""
        if self.list_projects.currentItem():
            selected_project = pm.PyNode(self.list_projects.currentItem().text())
            pm.select(selected_project)
            maya_main.create_object(selected_project)
            self.update_ui_texture_objects(self.list_projects.currentItem())

    def delete_texture_object(self):
        if self.list_texture_objects.currentItem():
            selected_object = pm.PyNode(self.list_texture_objects.currentItem().text())
            if selected_object and maya_main.is_texture_object(selected_object):
                pm.delete(selected_object)
                self.update_ui_projects()

    def update_ui_projects(self):
        """updates the list of texture projects"""
        root = maya_main.get_project_root()
        self.path.setText(
            "Export path: %s"
            % os.path.basename(pm.getAttr("%s.EZSurfacing_root" % root))
        )
        # update_lists
        projects = maya_main.get_projects()
        self.list_projects.clear()
        for each in projects:
            self.list_projects.addItem(str(each))
        self.list_texture_objects.clear()

    def update_ui_texture_objects(self, item):
        """updates the list of texture objects in the selected texture project"""
        selected_project = pm.PyNode(str(item.text()))
        texture_objects = maya_main.get_objects(selected_project)
        self.list_texture_objects.clear()
        for each in texture_objects:
            self.list_texture_objects.addItem(str(each))
        if self.sync_selection.isChecked():
            pm.select(selected_project, ne=True)

    def add_to_texture_object(self):
        """add maya selection to currently selected texture object"""
        selected_texture_object = pm.PyNode(
            str(self.list_texture_objects.currentItem().text())
        )
        if selected_texture_object:
            maya_main.add_mesh_transforms_to_object(
                pm.PyNode(selected_texture_object), pm.ls(sl=True)
            )

    def validate_scene(self):
        """scene validation and update"""
        maya_main.validate_scene()

    def export_project(self):
        selected_project = pm.PyNode(str(self.list_projects.currentItem().text()))
        if selected_project:
            maya_main.export_project(selected_project)

    def export_all_projects(self):
        maya_main.export_all_projects()


def show():
    w = MainWindow()
    w.show(dockable=True, floating=False, area="left")