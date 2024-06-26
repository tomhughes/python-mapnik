import os
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield

if mapnik.has_png():
    tmp_dir = '/tmp/mapnik-png/'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    opts = [
        'png32',
        'png32:t=0',
        'png8:m=o',
        'png8:m=o:c=1',
        'png8:m=o:t=0',
        'png8:m=o:c=1:t=0',
        'png8:m=o:t=1',
        'png8:m=o:t=2',
        'png8:m=h',
        'png8:m=h:c=1',
        'png8:m=h:t=0',
        'png8:m=h:c=1:t=0',
        'png8:m=h:t=1',
        'png8:m=h:t=2'
    ]

    # Todo - use itertools.product
    #z_opts = range(1,9+1)
    #t_opts = range(0,2+1)

    def gen_filepath(name, format):
        return os.path.join('images/support/encoding-opts',
                            name + '-' + format.replace(":", "+") + '.png')

    generate = os.environ.get('UPDATE')

    def test_expected_encodings(setup):
        # blank image
        im = mapnik.Image(256, 256)
        for opt in opts:
            expected = gen_filepath('solid', opt)
            actual = os.path.join(tmp_dir, os.path.basename(expected))
            if generate or not os.path.exists(expected):
                print('generating expected image %s' % expected)
                im.save(expected, opt)
            else:
                im.save(actual, opt)
                assert mapnik.Image.open(actual).to_string('png32') == mapnik.Image.open(expected).to_string('png32'), '%s (actual) not == to %s (expected)' % (actual, expected)

        # solid image
        im.fill(mapnik.Color('green'))
        for opt in opts:
            expected = gen_filepath('blank', opt)
            actual = os.path.join(tmp_dir, os.path.basename(expected))
            if generate or not os.path.exists(expected):
                print('generating expected image %s' % expected)
                im.save(expected, opt)
            else:
                im.save(actual, opt)
                assert mapnik.Image.open(actual).to_string('png32') == mapnik.Image.open(expected).to_string('png32'), '%s (actual) not == to %s (expected)' % (actual, expected)

        # aerial
        im = mapnik.Image.open('./images/support/transparency/aerial_rgba.png')
        for opt in opts:
            expected = gen_filepath('aerial_rgba', opt)
            actual = os.path.join(tmp_dir, os.path.basename(expected))
            if generate or not os.path.exists(expected):
                print('generating expected image %s' % expected)
                im.save(expected, opt)
            else:
                im.save(actual, opt)
                assert mapnik.Image.open(actual).to_string('png32') == mapnik.Image.open(expected).to_string('png32'), '%s (actual) not == to %s (expected)' % (actual, expected)

    def test_transparency_levels():
        # create partial transparency image
        im = mapnik.Image(256, 256)
        im.fill(mapnik.Color('rgba(255,255,255,.5)'))
        c2 = mapnik.Color('rgba(255,255,0,.2)')
        c3 = mapnik.Color('rgb(0,255,255)')
        for y in range(0, int(im.height() / 2)):
            for x in range(0, int(im.width() / 2)):
                im.set_pixel(x, y, c2)
        for y in range(int(im.height() / 2), im.height()):
            for x in range(int(im.width() / 2), im.width()):
                im.set_pixel(x, y, c3)

        t0 = tmp_dir + 'white0.png'
        t2 = tmp_dir + 'white2.png'
        t1 = tmp_dir + 'white1.png'

        # octree
        format = 'png8:m=o:t=0'
        im.save(t0, format)
        im_in = mapnik.Image.open(t0)
        t0_len = len(im_in.to_string(format))
        assert t0_len == len(mapnik.Image.open('images/support/transparency/white0.png').to_string(format))
        format = 'png8:m=o:t=1'
        im.save(t1, format)
        im_in = mapnik.Image.open(t1)
        t1_len = len(im_in.to_string(format))
        assert len(im.to_string(format)) == len(mapnik.Image.open('images/support/transparency/white1.png').to_string(format))
        format = 'png8:m=o:t=2'
        im.save(t2, format)
        im_in = mapnik.Image.open(t2)
        t2_len = len(im_in.to_string(format))
        assert len(im.to_string(format)) == len(mapnik.Image.open('images/support/transparency/white2.png').to_string(format))
        assert t0_len < t1_len < t2_len

        # hextree
        format = 'png8:m=h:t=0'
        im.save(t0, format)
        im_in = mapnik.Image.open(t0)
        t0_len = len(im_in.to_string(format))
        assert t0_len == len(mapnik.Image.open('images/support/transparency/white0.png').to_string(format))
        format = 'png8:m=h:t=1'
        im.save(t1, format)
        im_in = mapnik.Image.open(t1)
        t1_len = len(im_in.to_string(format))
        assert len(im.to_string(format)) == len(mapnik.Image.open('images/support/transparency/white1.png').to_string(format))
        format = 'png8:m=h:t=2'
        im.save(t2, format)
        im_in = mapnik.Image.open(t2)
        t2_len = len(im_in.to_string(format))
        assert len(im.to_string(format)) == len(mapnik.Image.open('images/support/transparency/white2.png').to_string(format))
        assert t0_len < t1_len < t2_len

    def test_transparency_levels_aerial():
        im = mapnik.Image.open('../data/images/12_654_1580.png')
        im_in = mapnik.Image.open(
            './images/support/transparency/aerial_rgba.png')
        assert len(im.to_string('png8')) == len(im_in.to_string('png8'))
        assert len(im.to_string('png32')) == len(im_in.to_string('png32'))

        im_in = mapnik.Image.open(
            './images/support/transparency/aerial_rgb.png')
        assert len(im.to_string('png32')) == len(im_in.to_string('png32'))
        assert len(im.to_string('png32:t=0')) == len(im_in.to_string('png32:t=0'))
        assert not len(im.to_string('png32:t=0')) == len(im_in.to_string('png32'))
        assert len(im.to_string('png8')) == len(im_in.to_string('png8'))
        assert len(im.to_string('png8:t=0')) == len(im_in.to_string('png8:t=0'))
        # unlike png32 paletted images without alpha will look the same even if
        # no alpha is forced
        assert len(im.to_string('png8:t=0')) == len(im_in.to_string('png8'))
        assert len(im.to_string('png8:t=0:m=o')) == len(im_in.to_string('png8:m=o'))

    def test_9_colors_hextree():
        expected = './images/support/encoding-opts/png8-9cols.png'
        im = mapnik.Image.open(expected)
        t0 = tmp_dir + 'png-encoding-9-colors.result-hextree.png'
        im.save(t0, 'png8:m=h')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)

    def test_9_colors_octree():
        expected = './images/support/encoding-opts/png8-9cols.png'
        im = mapnik.Image.open(expected)
        t0 = tmp_dir + 'png-encoding-9-colors.result-octree.png'
        im.save(t0, 'png8:m=o')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)

    def test_17_colors_hextree():
        expected = './images/support/encoding-opts/png8-17cols.png'
        im = mapnik.Image.open(expected)
        t0 = tmp_dir + 'png-encoding-17-colors.result-hextree.png'
        im.save(t0, 'png8:m=h')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)

    def test_17_colors_octree():
        expected = './images/support/encoding-opts/png8-17cols.png'
        im = mapnik.Image.open(expected)
        t0 = tmp_dir + 'png-encoding-17-colors.result-octree.png'
        im.save(t0, 'png8:m=o')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)

    def test_2px_regression_hextree():
        im = mapnik.Image.open('./images/support/encoding-opts/png8-2px.A.png')
        expected = './images/support/encoding-opts/png8-2px.png'

        t0 = tmp_dir + 'png-encoding-2px.result-hextree.png'
        im.save(t0, 'png8:m=h')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)

    def test_2px_regression_octree():
        im = mapnik.Image.open('./images/support/encoding-opts/png8-2px.A.png')
        expected = './images/support/encoding-opts/png8-2px.png'
        t0 = tmp_dir + 'png-encoding-2px.result-octree.png'
        im.save(t0, 'png8:m=o')
        assert mapnik.Image.open(t0).to_string() == mapnik.Image.open(expected).to_string(), '%s (actual) not == to %s (expected)' % (t0, expected)
