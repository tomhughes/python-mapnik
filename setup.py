#! /usr/bin/env python3

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import sys
import subprocess
import os

lib_path = '/usr/lib64'
linkflags = [
    '-lmapnik',
    '-lmapnikwkt',
    '-lmapnikjson',
    '-licui18n',
    '-licuuc',
    '-licudata',
    '-lharfbuzz',
    '-lfreetype',
    '-lxml2',
    '-lpng16',
    '-ljpeg',
    '-ltiff',
    '-lwebp',
    '-lcairo',
    '-lproj'
]

# Dynamically make the mapnik/paths.py file
f_paths = open('packaging/mapnik/paths.py', 'w')
f_paths.write('import os\n')
f_paths.write('\n')

input_plugin_path = '/usr/lib64/mapnik/input'
font_path = '/usr/share/fonts'

if os.environ.get('LIB_DIR_NAME'):
    mapnik_lib_path = lib_path + os.environ.get('LIB_DIR_NAME')
else:
    mapnik_lib_path = lib_path + "/mapnik"
    f_paths.write("mapniklibpath = '{path}'\n".format(path=mapnik_lib_path))
    f_paths.write(
        "inputpluginspath = '{path}'\n".format(path=input_plugin_path))
    f_paths.write(
        "fontscollectionpath = '{path}'\n".format(path=font_path))
    f_paths.write(
        "__all__ = [mapniklibpath,inputpluginspath,fontscollectionpath]\n")
    f_paths.close()

extra_comp_args = [
    '-I/usr/include/mapnik',
    '-I/usr/include/mapnik/agg',
    '-DMAPNIK_THREADSAFE',
    '-DBOOST_REGEX_HAS_ICU',
    '-DBIGINT',
    '-DMAPNIK_MEMORY_MAPPED_FILE',
    '-DHAVE_LIBXML2',
    '-DHAVE_PNG',
    '-DHAVE_JPEG',
    '-DHAVE_TIFF',
    '-DHAVE_WEBP',
    '-DHAVE_CAIRO',
    '-DMAPNIK_USE_PROJ',
    '-DMAPNIK_PROJ_VERSION=90401',
    '-DGRID_RENDERER',
    '-DSVG_RENDERER',
    '-DMAPNIK_HAS_DLCFN',
    '-I/usr/include/harfbuzz',
    '-I/usr/include/cairo',
    '-I/usr/include/libpng16',
    '-I/usr/include/libxml2',
    '-I/usr/include/freetype2',
    '-I/usr/include/glib-2.0',
    '-I/usr/lib64/glib-2.0/include',
    '-I/usr/include/sysprof-6',
    '-pthread',
    '-I/usr/include/webp',
    '-DWITH_GZFILEOP',
    '-I/usr/include/pixman-1'
]

if sys.platform == 'darwin':
     pass
else:
     linkflags.append('-lrt')


ext_modules = [
     Pybind11Extension(
          "mapnik._mapnik",
          [
               "src/mapnik_python.cpp",
               "src/mapnik_layer.cpp",
               "src/mapnik_query.cpp",
               "src/mapnik_map.cpp",
               "src/mapnik_color.cpp",
               "src/mapnik_composite_modes.cpp",
               "src/mapnik_coord.cpp",
               "src/mapnik_envelope.cpp",
               "src/mapnik_expression.cpp",
               "src/mapnik_datasource.cpp",
               "src/mapnik_datasource_cache.cpp",
               "src/mapnik_gamma_method.cpp",
               "src/mapnik_geometry.cpp",
               "src/mapnik_feature.cpp",
               "src/mapnik_featureset.cpp",
               "src/mapnik_font_engine.cpp",
               "src/mapnik_fontset.cpp",
               "src/mapnik_grid.cpp",
               "src/mapnik_grid_view.cpp",
               "src/mapnik_image.cpp",
               "src/mapnik_image_view.cpp",
               "src/mapnik_projection.cpp",
               "src/mapnik_proj_transform.cpp",
               "src/mapnik_rule.cpp",
               "src/mapnik_symbolizer.cpp",
               "src/mapnik_debug_symbolizer.cpp",
               "src/mapnik_markers_symbolizer.cpp",
               "src/mapnik_polygon_symbolizer.cpp",
               "src/mapnik_polygon_pattern_symbolizer.cpp",
               "src/mapnik_line_symbolizer.cpp",
               "src/mapnik_line_pattern_symbolizer.cpp",
               "src/mapnik_point_symbolizer.cpp",
               "src/mapnik_raster_symbolizer.cpp",
               "src/mapnik_scaling_method.cpp",
               "src/mapnik_style.cpp",
               "src/mapnik_logger.cpp",
               "src/mapnik_placement_finder.cpp",
               "src/mapnik_text_symbolizer.cpp",
               "src/mapnik_palette.cpp",
               "src/mapnik_parameters.cpp",
               "src/python_grid_utils.cpp",
               "src/mapnik_raster_colorizer.cpp",
               "src/mapnik_label_collision_detector.cpp",
               "src/mapnik_dot_symbolizer.cpp",
               "src/mapnik_building_symbolizer.cpp",
               "src/mapnik_shield_symbolizer.cpp",
               "src/mapnik_group_symbolizer.cpp"
          ],
          extra_compile_args=extra_comp_args,
          extra_link_args=linkflags,
     )
]

if os.environ.get("CC", False) == False:
    os.environ["CC"] = 'c++'
if os.environ.get("CXX", False) == False:
    os.environ["CXX"] = 'c++'

setup(
     name="mapnik",
     version="4.0.0.dev",
     packages=find_packages(where="packaging"),
     package_dir={"": "packaging"},
     package_data={
          'mapnik': ['lib/*.*', 'lib/*/*/*', 'share/*/*'],
     },
     ext_modules=ext_modules,
     #extras_require={"test": "pytest"},
     cmdclass={"build_ext": build_ext},
     #zip_safe=False,
     python_requires=">=3.7",
)
