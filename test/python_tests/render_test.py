import sys, os
import tempfile
import mapnik
import pytest
from .utilities import execution_path, images_almost_equal

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

def test_simplest_render(setup):
    m = mapnik.Map(256, 256)
    im = mapnik.Image(m.width, m.height)
    assert not im.painted()
    assert im.is_solid()
    mapnik.render(m, im)
    assert not im.painted()
    assert im.is_solid()
    s = im.to_string()
    assert s ==  256 * 256 * b'\x00\x00\x00\x00'


def test_render_image_to_string():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('black'))
    assert not im.painted()
    assert im.is_solid()
    s = im.to_string()
    assert s ==  256 * 256 * b'\x00\x00\x00\xff'


def test_non_solid_image():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('black'))
    assert not im.painted()
    assert im.is_solid()
    # set one pixel to a different color
    im.set_pixel(0, 0, mapnik.Color('white'))
    assert not im.painted()
    assert not im.is_solid()


def test_non_solid_image_view():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('black'))
    view = im.view(0, 0, 256, 256)
    assert view.is_solid()
    # set one pixel to a different color
    im.set_pixel(0, 0, mapnik.Color('white'))
    assert not im.is_solid()
    # view, since it is the exact dimensions of the image
    # should also be non-solid
    assert not view.is_solid()
    # but not a view that excludes the single diff pixel
    view2 = im.view(1, 1, 256, 256)
    assert view2.is_solid()


def test_setting_alpha():
    w, h = 256, 256
    im1 = mapnik.Image(w, h)
    # white, half transparent
    c1 = mapnik.Color('rgba(255,255,255,.5)')
    im1.fill(c1)
    assert not im1.painted()
    assert im1.is_solid()
    # pure white
    im2 = mapnik.Image(w, h)
    c2 = mapnik.Color('rgba(255,255,255,1)')
    im2.fill(c2)
    im2.apply_opacity(c1.a / 255.0)
    assert not im2.painted()
    assert im2.is_solid()
    assert len(im1.to_string('png32')) ==  len(im2.to_string('png32'))


def test_render_image_to_file():
    im = mapnik.Image(256, 256)
    im.fill(mapnik.Color('black'))
    if mapnik.has_jpeg():
        im.save('test.jpg')
    im.save('test.png', 'png')
    if os.path.exists('test.jpg'):
        os.remove('test.jpg')
    else:
        return False
    if os.path.exists('test.png'):
        os.remove('test.png')
    else:
        return False


def get_paired_images(w, h, mapfile):
    tmp_map = 'tmp_map.xml'
    m = mapnik.Map(w, h)
    mapnik.load_map(m, mapfile)
    im = mapnik.Image(w, h)
    m.zoom_all()
    mapnik.render(m, im)
    mapnik.save_map(m, tmp_map)
    m2 = mapnik.Map(w, h)
    mapnik.load_map(m2, tmp_map)
    im2 = mapnik.Image(w, h)
    m2.zoom_all()
    mapnik.render(m2, im2)
    os.remove(tmp_map)
    return im, im2


def test_render_from_serialization():
    try:
        im, im2 = get_paired_images(
            100, 100, '../data/good_maps/building_symbolizer.xml')
        assert im.to_string('png32') ==  im2.to_string('png32')

        im, im2 = get_paired_images(
            100, 100, '../data/good_maps/polygon_symbolizer.xml')
        assert im.to_string('png32') ==  im2.to_string('png32')
    except RuntimeError as e:
        # only test datasources that we have installed
        if not 'Could not create datasource' in str(e):
            raise RuntimeError(e)


def test_render_points():
    if not mapnik.has_cairo():
        return
    # create and populate point datasource (WGS84 lat-lon coordinates)
    ds = mapnik.MemoryDatasource()
    context = mapnik.Context()
    context.push('Name')
    f = mapnik.Feature(context, 1)
    f['Name'] = 'Westernmost Point'
    f.geometry = mapnik.Geometry.from_wkt('POINT (142.48 -38.38)')
    ds.add_feature(f)

    f = mapnik.Feature(context, 2)
    f['Name'] = 'Southernmost Point'
    f.geometry = mapnik.Geometry.from_wkt('POINT (143.10 -38.60)')
    ds.add_feature(f)

    # create layer/rule/style
    s = mapnik.Style()
    r = mapnik.Rule()
    symb = mapnik.PointSymbolizer()
    symb.allow_overlap = True
    r.symbolizers.append(symb)
    s.rules.append(r)
    lyr = mapnik.Layer(
        'Places',
        'epsg:4326')
    lyr.datasource = ds
    lyr.styles.append('places_labels')
    # latlon bounding box corners
    ul_lonlat = mapnik.Coord(142.30, -38.20)
    lr_lonlat = mapnik.Coord(143.40, -38.80)
    # render for different projections
    projs = {
        'google': 'epsg:3857',
        'latlon': 'epsg:4326',
        'merc': '+proj=merc +datum=WGS84 +k=1.0 +units=m +over +no_defs',
        'utm': '+proj=utm +zone=54 +datum=WGS84'
    }
    for projdescr in projs:
        m = mapnik.Map(1000, 500, projs[projdescr])
        m.append_style('places_labels', s)
        m.layers.append(lyr)
        dest_proj = mapnik.Projection(projs[projdescr])
        src_proj = mapnik.Projection('epsg:4326')
        tr = mapnik.ProjTransform(src_proj, dest_proj)
        m.zoom_to_box(tr.forward(mapnik.Box2d(ul_lonlat, lr_lonlat)))
        # Render to SVG so that it can be checked how many points are there
        # with string comparison
        svg_file = os.path.join(
            tempfile.gettempdir(),
            'mapnik-render-points-%s.svg' %
            projdescr)
        mapnik.render_to_file(m, svg_file)
        num_points_present = len(list(iter(ds)))
        with open(svg_file, 'r') as f:
            svg = f.read()
        num_points_rendered = svg.count('<image ')
        assert  num_points_present == num_points_rendered, "Not all points were rendered (%d instead of %d) at projection %s" % (num_points_rendered, num_points_present, projdescr)


def test_render_with_scale_factor_zero_throws():
    with pytest.raises(RuntimeError):
        m = mapnik.Map(256, 256)
        im = mapnik.Image(256, 256)
        mapnik.render(m, im, 0.0) #should throw

def test_render_with_detector():
    ds = mapnik.MemoryDatasource()
    context = mapnik.Context()
    geojson = '{ "type": "Feature", "geometry": { "type": "Point", "coordinates": [ 0, 0 ] } }'
    ds.add_feature(mapnik.Feature.from_geojson(geojson, context))
    s = mapnik.Style()
    r = mapnik.Rule()
    lyr = mapnik.Layer('point')
    lyr.datasource = ds
    lyr.styles.append('point')
    symb = mapnik.MarkersSymbolizer()
    symb.allow_overlap = False
    r.symbolizers.append(symb)
    s.rules.append(r)
    m = mapnik.Map(256, 256)
    m.append_style('point', s)
    m.layers.append(lyr)
    m.zoom_to_box(mapnik.Box2d(-180, -85, 180, 85))
    im = mapnik.Image(256, 256)
    mapnik.render(m, im)
    expected_file = 'images/support/marker-in-center.png'
    actual_file = '/tmp/' + os.path.basename(expected_file)
    # im.save(expected_file,'png8')
    im.save(actual_file, 'png8')
    actual = mapnik.Image.open(expected_file)
    expected = mapnik.Image.open(expected_file)
    assert actual.to_string('png32') == expected.to_string('png32'), 'failed comparing actual (%s) and expected (%s)' % (actual_file, expected_file)
    # now render will a collision detector that should
    # block out the placement of this point
    detector = mapnik.LabelCollisionDetector(m)
    assert detector.extent(), mapnik.Box2d(-0.0, -0.0, m.width ==  m.height)
    assert detector.extent(), mapnik.Box2d(-0.0, -0.0, 256.0 ==  256.0)
    assert detector.boxes() ==  []
    detector.insert(detector.extent())
    assert detector.boxes() ==  [detector.extent()]
    im2 = mapnik.Image(256, 256)
    mapnik.render_with_detector(m, im2, detector)
    expected_file_collision = 'images/support/marker-in-center-not-placed.png'
    # im2.save(expected_file_collision,'png8')
    actual_file = '/tmp/' + os.path.basename(expected_file_collision)
    im2.save(actual_file, 'png8')


if 'shape' in mapnik.DatasourceCache.plugin_names():

    def test_render_with_scale_factor():
        m = mapnik.Map(256, 256)
        mapnik.load_map(m, '../data/good_maps/marker-text-line.xml')
        m.zoom_all()
        sizes = [.00001, .005, .1, .899, 1, 1.5, 2, 5, 10, 100]
        for size in sizes:
            im = mapnik.Image(256, 256)
            mapnik.render(m, im, size)
            expected_file = 'images/support/marker-text-line-scale-factor-%s.png' % size
            actual_file = '/tmp/' + os.path.basename(expected_file)
            im.save(actual_file, 'png32')
            if os.environ.get('UPDATE'):
                im.save(expected_file, 'png32')
            # we save and re-open here so both png8 images are ready as full
            # color png
            actual = mapnik.Image.open(actual_file)
            expected = mapnik.Image.open(expected_file)
            images_almost_equal(actual, expected)
