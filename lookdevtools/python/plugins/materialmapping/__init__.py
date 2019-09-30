"""
.. module:: Material Mapping
   :synopsis: Import textures to surfacing projects and surfacing objects.

.. moduleauthor:: Ezequiel Mastrasso

"""
import logging
from functools import partial
from yapsy.IPlugin import IPlugin
from lookdevtools.ui.libs import *
from lookdevtools.ui import qtutils
from lookdevtools.common import utils
from lookdevtools.common import templates
from lookdevtools.common.constants import TEXTURESET_ELEMENT_PATTERN
from lookdevtools.common.constants import ATTR_SURFACING_PROJECT
from lookdevtools.common.constants import ATTR_SURFACING_OBJECT

logger = logging.getLogger(__name__)

DCC_CONTEXT = None

try:
    import pymel.core as pm
    from lookdevtools.maya import maya
    from lookdevtools.maya import surfacing_projects
    from lookdevtools.maya.surfacing_projects import viewport
    reload(surfacing_projects)
    DCC_CONTEXT = True
except:
    logger.warning('PLUGIN: Maya packages not loaded, not this dcc')


class MaterialMapping(IPlugin):
    """Plug-in to Import textures to surfacing projects and surfacing objects."""

    name = "MaterialMapping Plugin"

    plugin_layout = None

    def __init__(self):
        """Check dcc context, and build the ui if context is correct."""
        logger.info('PLUGIN: MaterialMapping loaded')
        # Load dcc python packages inside a try, to catch the application
        # environment, this will be replaced by IPlugin Categories
        if not DCC_CONTEXT:
            logger.warning(
                'PLUGIN: MaterialMapping  not loaded, dcc libs not found')
            self.plugin_layout = QtWidgets.QWidget()
            self.label_ui = QtWidgets.QLabel(self.plugin_layout)
            self.label_ui.setText(
                'MaterialMapping\nPlugin not available in this application')
        else:
            self.build_ui()

    def build_ui(self):
        """Build the Plug-in UI and append it to the main ui as a tab."""
        self.plugin_layout = QtWidgets.QWidget()
        self.lbl_custom_template = QtWidgets.QLabel('File load template')
        self.ln_custom_template = QtWidgets.QLineEdit(
            TEXTURESET_ELEMENT_PATTERN)
        self.lbl_extension = QtWidgets.QLabel('Find files with extension')
        self.ln_extension = QtWidgets.QLineEdit('tif')
        self.import_layout = QtWidgets.QHBoxLayout()
        self.lbl_import = QtWidgets.QLabel('Import textures')
        self.btn_search_files = QtWidgets.QPushButton(
            "Search files in folder"
        )
        self.btn_import_textures_surfacing_project = QtWidgets.QPushButton(
            "by surfacing_project"
        )
        self.btn_import_textures_surfacing_object = QtWidgets.QPushButton(
            "by surfacing_object"
        )
        self.form_widget = QtWidgets.QTableWidget(0, 8)
        col_headers = ['filepath', 'surfacing_project', 'surfacing_object',
                       'textureset_element', 'colorspace', 'shader_plug', 'maya_prj', 'maya_obj']
        self.form_widget.setHorizontalHeaderLabels(col_headers)
        main_layout = QtWidgets.QVBoxLayout()

        # Attach widgets to the main layout
        main_layout.addWidget(self.lbl_custom_template)
        main_layout.addWidget(self.ln_custom_template)
        main_layout.addWidget(self.lbl_extension)
        main_layout.addWidget(self.ln_extension)

        main_layout.addWidget(self.btn_search_files)
        main_layout.addWidget(self.form_widget)
        main_layout.addLayout(self.import_layout)
        self.import_layout.addWidget(self.lbl_import)
        self.import_layout.addWidget(
            self.btn_import_textures_surfacing_project)
        self.import_layout.addWidget(self.btn_import_textures_surfacing_object)

        # Set main layout
        self.plugin_layout.setLayout(main_layout)

        self.btn_search_files.clicked.connect(
            self.load_textures
        )
        self.btn_import_textures_surfacing_project.clicked.connect(
            self.import_textures_surfacing_project
        )
        self.btn_import_textures_surfacing_object.clicked.connect(
            self.import_textures_surfacing_object
        )

    def load_textures(self):
        """Load textures."""
        config = utils.get_config_materials()
        search_folder = qtutils.get_folder_path()
        if search_folder:
            self.form_widget.setRowCount(0)
            logger.info('Search folder: %s' % search_folder)
            file_list = utils.get_files_in_folder(
                search_folder, recursive=True, pattern=self.ln_extension.text())
            custom_template = self.ln_custom_template.text()
            logger.info('Using template: %s' % custom_template)
            file_template_object = templates.custom_texture_file_template(
                custom_template)
            file_templates = []
            for file_path in file_list:
                try:
                    file_template = file_template_object.parse(file_path)
                    file_template['file_path'] = file_path
                    try:
                        file_template['shader_plug'] = config['material_mapping']['PxrSurface'][file_template['textureset_element']]
                    except:
                        file_template['shader_plug'] = ''
                    file_templates.append(file_template)
                except BaseException:
                    logger.warning('File pattern not matched: %s' % file)

            # not grouped by udims
            # self.form_widget.setRowCount(len(file_templates))
            # self.populate_form(file_templates)

            # group by udims
            grouped_templates = utils.get_udim_file_templates(file_templates)
            self.form_widget.setRowCount(len(grouped_templates))
            self.populate_form(grouped_templates)

    def populate_form(self, file_templates):
        """
        Populate form with texture lucidity parsed files.

        Args:
            file_templates (list): A list of lucidity parsed files, with file_path key added.

        """
        for num, file_template in enumerate(file_templates):
            try:
                item = QtWidgets.QTableWidgetItem(file_template['file_path'])
                self.form_widget.setItem(num, 0, item)
            except BaseException:
                logger.error('file_path not in file_template dict.')
            try:
                item = QtWidgets.QTableWidgetItem(
                    file_template['surfacing_project'])
                self.form_widget.setItem(num, 1, item)
            except BaseException:
                logger.error('surfacing_project not in file_template dict.')
            try:
                item = QtWidgets.QTableWidgetItem(
                    file_template['surfacing_object'])
                self.form_widget.setItem(num, 2, item)
            except BaseException:
                logger.error('surfacing_object not in file_template dict.')
            try:
                item = QtWidgets.QTableWidgetItem(
                    file_template['textureset_element'])
                self.form_widget.setItem(num, 3, item)
            except BaseException:
                logger.error('textureset_element not in file_template dict.')
            try:
                item = QtWidgets.QTableWidgetItem(file_template['colorspace'])
                self.form_widget.setItem(num, 4, item)
            except:
                logger.warning('colorspace not in file_template dict.')
            try:
                search_plug = utils.search_material_mapping(
                    file_template['textureset_element'])
                item = QtWidgets.QTableWidgetItem(search_plug)
                if search_plug == None:
                    logger.warning('textureset_element could not be mappend to a shader plug: %s' %
                                   file_template['textureset_element'])
                self.form_widget.setItem(num, 5, item)
            except:
                pass
            try:
                # Match parsed surfacing projects and objects to the open maya file
                local_surfacing_projects = surfacing_projects.get_projects()
                logger.info('Searching for "%s" in local projects %s' % (
                    file_template['surfacing_object'], local_surfacing_projects))
                for project in local_surfacing_projects:
                    project_name = project.getAttr(ATTR_SURFACING_PROJECT)
                    if project_name == file_template['surfacing_project']:
                        item = QtWidgets.QTableWidgetItem(project_name)
                        self.form_widget.setItem(num, 6, item)
                    local_surfacing_objects = surfacing_projects.get_objects(
                        project)
                    logger.info(
                        'Searching objects in project: %s', project_name)
                    for local_surfacing_object in local_surfacing_objects:
                        object_name = local_surfacing_object.getAttr(
                            ATTR_SURFACING_OBJECT)
                        if object_name == file_template['surfacing_object']:
                            logger.info(
                                'Found matching local surfacing object: %s' % file_template['surfacing_object'])
                            item = QtWidgets.QTableWidgetItem(object_name)
                            self.form_widget.setItem(num, 7, item)
            except:
                pass

    def get_form_data(self):
        """Get the form_widget data."""
        file_templates = []
        form_column_count = self.form_widget.columnCount()
        logger.info('Form column count: %s' % form_column_count)
        form_row_count = self.form_widget.rowCount()
        logger.info('Form row count: %s' % form_row_count)
        logger.info('Retrieving form data')
        row = 0
        while row < form_row_count:
            column = 0
            file_templates.append({})
            while column < form_column_count:
                logger.info('Form Coords %s,%s' % (row, column))
                try:
                    item_text = self.form_widget.item(row, column).text()
                except:
                    item_text = ''
                column_name = self.form_widget.horizontalHeaderItem(
                    column).text()
                logger.info('Data pair %s,%s' % (column_name, item_text))
                logger.info('Appending to data index %s' % column)
                file_templates[row][column_name] = item_text
                column = column + 1
            row = row + 1
        return file_templates

    def import_textures_surfacing_project(self):
        """Import textures to surfacing projects."""
        parsed_files = self.get_form_data()
        shaders = surfacing_projects.create_surfacing_shaders(
            parsed_files=parsed_files, key='maya_prj')
        surfacing_projects.import_textures(
            parsed_files=parsed_files, key='maya_prj', shaders=shaders)

    def import_textures_surfacing_object(self):
        """Import textures to surfacing objects."""
        parsed_files = self.get_form_data()
        shaders = surfacing_projects.create_surfacing_shaders(
            parsed_files=parsed_files, key='maya_obj')
        surfacing_projects.import_textures(
            parsed_files=parsed_files, key='maya_obj', shaders=shaders)