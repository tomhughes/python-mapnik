#!/usr/bin/env python
# -*- coding: utf-8 -*-

from binascii import unhexlify

from nose.tools import eq_, raises

import mapnik

from .utilities import run_all


def test_default_constructor():
    f = mapnik.Feature(mapnik.Context(), 1)
    eq_(f is not None, True)


def test_feature_geo_interface():
    ctx = mapnik.Context()
    feat = mapnik.Feature(ctx, 1)
    feat.geometry = mapnik.Geometry.from_wkt('Point (0 0)')
    eq_(feat.__geo_interface__['geometry'], {
        u'type': u'Point', u'coordinates': [0, 0]})


def test_python_extended_constructor():
    context = mapnik.Context()
    context.push('foo')
    context.push('foo')
    f = mapnik.Feature(context, 1)
    wkt = 'POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),(20 30, 35 35, 30 20, 20 30))'
    f.geometry = mapnik.Geometry.from_wkt(wkt)
    f['foo'] = 'bar'
    eq_(f['foo'], 'bar')
    eq_(f.envelope(), mapnik.Box2d(10.0, 10.0, 45.0, 45.0))
    # reset
    f['foo'] = u"avión"
    eq_(f['foo'], u"avión")
    f['foo'] = 1.4
    eq_(f['foo'], 1.4)
    f['foo'] = True
    eq_(f['foo'], True)


def test_add_geom_wkb():
    # POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))
    wkb = '010300000001000000050000000000000000003e4000000000000024400000000000002440000000000000344000000000000034400000000000004440000000000000444000000000000044400000000000003e400000000000002440'
    geometry = mapnik.Geometry.from_wkb(unhexlify(wkb))
    if hasattr(geometry, 'is_valid'):
        # Those are only available when python-mapnik has been built with
        # boost >= 1.56.
        eq_(geometry.is_valid(), True)
        eq_(geometry.is_simple(), True)
    eq_(geometry.envelope(), mapnik.Box2d(10.0, 10.0, 40.0, 40.0))
    geometry.correct()
    if hasattr(geometry, 'is_valid'):
        # valid after calling correct
        eq_(geometry.is_valid(), True)


def test_feature_expression_evaluation():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 1)
    f['name'] = 'a'
    eq_(f['name'], u'a')
    expr = mapnik.Expression("[name]='a'")
    evaluated = expr.evaluate(f)
    eq_(evaluated, True)
    num_attributes = len(f)
    eq_(num_attributes, 1)
    eq_(f.id(), 1)

# https://github.com/mapnik/mapnik/issues/933


def test_feature_expression_evaluation_missing_attr():
    context = mapnik.Context()
    context.push('name')
    f = mapnik.Feature(context, 1)
    f['name'] = u'a'
    eq_(f['name'], u'a')
    expr = mapnik.Expression("[fielddoesnotexist]='a'")
    eq_('fielddoesnotexist' in f, False)
    try:
        expr.evaluate(f)
    except Exception as e:
        eq_("Key does not exist" in str(e), True)
    num_attributes = len(f)
    eq_(num_attributes, 1)
    eq_(f.id(), 1)

# https://github.com/mapnik/mapnik/issues/934


def test_feature_expression_evaluation_attr_with_spaces():
    context = mapnik.Context()
    context.push('name with space')
    f = mapnik.Feature(context, 1)
    f['name with space'] = u'a'
    eq_(f['name with space'], u'a')
    expr = mapnik.Expression("[name with space]='a'")
    eq_(str(expr), "([name with space]='a')")
    eq_(expr.evaluate(f), True)

# https://github.com/mapnik/mapnik/issues/2390


@raises(RuntimeError)
def test_feature_from_geojson():
    ctx = mapnik.Context()
    inline_string = """
    {
         "geometry" : {
            "coordinates" : [ 0,0 ]
            "type" : "Point"
         },
         "type" : "Feature",
         "properties" : {
            "this":"that"
            "known":"nope because missing comma"
         }
    }
    """
    mapnik.Feature.from_geojson(inline_string, ctx)

if __name__ == "__main__":
    exit(run_all(eval(x) for x in dir() if x.startswith("test_")))
