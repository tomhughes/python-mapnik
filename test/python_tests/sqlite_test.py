import os
import mapnik
import pytest
from .utilities import execution_path

@pytest.fixture(scope="module")
def setup_and_teardown():
    # All of the paths used are relative, if we run the tests
    # from another directory we need to chdir()
    os.chdir(execution_path('.'))
    yield
    index = '../data/sqlite/world.sqlite.index'
    if os.path.exists(index):
        os.unlink(index)

if 'sqlite' in mapnik.DatasourceCache.plugin_names():

    def test_attachdb_with_relative_file(setup_and_teardown):
        # The point table and index is in the qgis_spatiallite.sqlite
        # database.  If either is not found, then this fails
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='point',
                           attachdb='scratch@qgis_spatiallite.sqlite'
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['pkuid'] == 1

    test_attachdb_with_relative_file.requires_data = True

    def test_attachdb_with_multiple_files():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='attachedtest',
                           attachdb='scratch1@:memory:,scratch2@:memory:',
                           initdb='''
                create table scratch1.attachedtest (the_geom);
                create virtual table scratch2.idx_attachedtest_the_geom using rtree(pkid,xmin,xmax,ymin,ymax);
                insert into scratch2.idx_attachedtest_the_geom values (1,-7799225.5,-7778571.0,1393264.125,1417719.375);
                '''
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        # the above should not throw but will result in no features
        assert feature == None

    test_attachdb_with_multiple_files.requires_data = True

    def test_attachdb_with_absolute_file():
        # The point table and index is in the qgis_spatiallite.sqlite
        # database.  If either is not found, then this fails
        ds = mapnik.SQLite(file=os.getcwd() + '/../data/sqlite/world.sqlite',
                           table='point',
                           attachdb='scratch@qgis_spatiallite.sqlite'
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['pkuid'] ==  1

    test_attachdb_with_absolute_file.requires_data = True

    def test_attachdb_with_index():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='attachedtest',
                           attachdb='scratch@:memory:',
                           initdb='''
                create table scratch.attachedtest (the_geom);
                create virtual table scratch.idx_attachedtest_the_geom using rtree(pkid,xmin,xmax,ymin,ymax);
                insert into scratch.idx_attachedtest_the_geom values (1,-7799225.5,-7778571.0,1393264.125,1417719.375);
                '''
                           )

        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_attachdb_with_index.requires_data = True

    def test_attachdb_with_explicit_index():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='attachedtest',
                           index_table='myindex',
                           attachdb='scratch@:memory:',
                           initdb='''
                create table scratch.attachedtest (the_geom);
                create virtual table scratch.myindex using rtree(pkid,xmin,xmax,ymin,ymax);
                insert into scratch.myindex values (1,-7799225.5,-7778571.0,1393264.125,1417719.375);
                '''
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_attachdb_with_explicit_index.requires_data = True

    def test_attachdb_with_sql_join():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from world_merc INNER JOIN business on world_merc.iso3 = business.ISO3 limit 100)',
                           attachdb='busines@business.sqlite'
                           )
        assert len(ds.fields()) ==  29
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat',
                               'ISO3:1',
                               '1995',
                               '1996',
                               '1997',
                               '1998',
                               '1999',
                               '2000',
                               '2001',
                               '2002',
                               '2003',
                               '2004',
                               '2005',
                               '2006',
                               '2007',
                               '2008',
                               '2009',
                               '2010']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int']
        fs = iter(ds)
        feature = next(fs)
        assert feature.id() ==  1
        expected = {
            1995: 0,
            1996: 0,
            1997: 0,
            1998: 0,
            1999: 0,
            2000: 0,
            2001: 0,
            2002: 0,
            2003: 0,
            2004: 0,
            2005: 0,
            2006: 0,
            2007: 0,
            2008: 0,
            2009: 0,
            2010: 0,
            # this appears to be sqlites way of
            # automatically handling clashing column names
            'ISO3:1': 'ATG',
            'OGC_FID': 1,
            'area': 44,
            'fips': u'AC',
            'iso2': u'AG',
            'iso3': u'ATG',
            'lat': 17.078,
            'lon': -61.783,
            'name': u'Antigua and Barbuda',
            'pop2005': 83039,
            'region': 19,
            'subregion': 29,
            'un': 28
        }
        for k, v in expected.items():
            try:
                assert feature[str(k)] ==  v
            except:
                #import pdb;pdb.set_trace()
                print('invalid key/v %s/%s for: %s' % (k, v, feature))

    test_attachdb_with_sql_join.requires_data = True

    def test_attachdb_with_sql_join_count():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from world_merc INNER JOIN business on world_merc.iso3 = business.ISO3 limit 100)',
                           attachdb='busines@business.sqlite'
                           )
        assert len(ds.fields()) ==  29
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat',
                               'ISO3:1',
                               '1995',
                               '1996',
                               '1997',
                               '1998',
                               '1999',
                               '2000',
                               '2001',
                               '2002',
                               '2003',
                               '2004',
                               '2005',
                               '2006',
                               '2007',
                               '2008',
                               '2009',
                               '2010']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int']
        assert len(list(iter(ds))) ==  100

    test_attachdb_with_sql_join_count.requires_data = True

    def test_attachdb_with_sql_join_count2():
        '''
        sqlite3 world.sqlite
        attach database 'business.sqlite' as business;
        select count(*) from world_merc INNER JOIN business on world_merc.iso3 = business.ISO3;
        '''
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from world_merc INNER JOIN business on world_merc.iso3 = business.ISO3)',
                           attachdb='busines@business.sqlite'
                           )
        assert len(ds.fields()) ==  29
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat',
                               'ISO3:1',
                               '1995',
                               '1996',
                               '1997',
                               '1998',
                               '1999',
                               '2000',
                               '2001',
                               '2002',
                               '2003',
                               '2004',
                               '2005',
                               '2006',
                               '2007',
                               '2008',
                               '2009',
                               '2010']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int']
        assert len(list(iter(ds))) ==  192

    test_attachdb_with_sql_join_count2.requires_data = True

    def test_attachdb_with_sql_join_count3():
        '''
        select count(*) from (select * from world_merc where 1=1) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3;
        '''
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from (select * from world_merc where !intersects!) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3)',
                           attachdb='busines@business.sqlite'
                           )
        assert len(ds.fields()) ==  29
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat',
                               'ISO3:1',
                               '1995',
                               '1996',
                               '1997',
                               '1998',
                               '1999',
                               '2000',
                               '2001',
                               '2002',
                               '2003',
                               '2004',
                               '2005',
                               '2006',
                               '2007',
                               '2008',
                               '2009',
                               '2010']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int']
        assert len(list(iter(ds))) ==  192

    test_attachdb_with_sql_join_count3.requires_data = True

    def test_attachdb_with_sql_join_count4():
        '''
        select count(*) from (select * from world_merc where 1=1) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3;
        '''
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from (select * from world_merc where !intersects! limit 1) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3)',
                           attachdb='busines@business.sqlite'
                           )
        assert len(ds.fields()) ==  29
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat',
                               'ISO3:1',
                               '1995',
                               '1996',
                               '1997',
                               '1998',
                               '1999',
                               '2000',
                               '2001',
                               '2002',
                               '2003',
                               '2004',
                               '2005',
                               '2006',
                               '2007',
                               '2008',
                               '2009',
                               '2010']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'int']
        assert len(list(iter(ds))) ==  1

    test_attachdb_with_sql_join_count4.requires_data = True

    def test_attachdb_with_sql_join_count5():
        '''
        select count(*) from (select * from world_merc where 1=1) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3;
        '''
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from (select * from world_merc where !intersects! and 1=2) as world_merc INNER JOIN business on world_merc.iso3 = business.ISO3)',
                           attachdb='busines@business.sqlite'
                           )
        # nothing is able to join to business so we don't pick up business
        # schema
        assert len(ds.fields()) ==  12
        assert ds.fields() == ['OGC_FID',
                               'fips',
                               'iso2',
                               'iso3',
                               'un',
                               'name',
                               'area',
                               'pop2005',
                               'region',
                               'subregion',
                               'lon',
                               'lat']
        assert ds.field_types() == ['int',
                                    'str',
                                    'str',
                                    'str',
                                    'int',
                                    'str',
                                    'int',
                                    'int',
                                    'int',
                                    'int',
                                    'float',
                                    'float']
        assert len(list(iter(ds))) ==  0

    test_attachdb_with_sql_join_count5.requires_data = True

    def test_subqueries():
        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='world_merc',
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['OGC_FID'] ==  1
        assert feature['fips'] ==  u'AC'
        assert feature['iso2'] ==  u'AG'
        assert feature['iso3'] ==  u'ATG'
        assert feature['un'] ==  28
        assert feature['name'] ==  u'Antigua and Barbuda'
        assert feature['area'] ==  44
        assert feature['pop2005'] ==  83039
        assert feature['region'] ==  19
        assert feature['subregion'] ==  29
        assert feature['lon'] ==  -61.783
        assert feature['lat'] ==  17.078

        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select * from world_merc)',
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['OGC_FID'] ==  1
        assert feature['fips'] ==  u'AC'
        assert feature['iso2'] ==  u'AG'
        assert feature['iso3'] ==  u'ATG'
        assert feature['un'] ==  28
        assert feature['name'] ==  u'Antigua and Barbuda'
        assert feature['area'] ==  44
        assert feature['pop2005'] ==  83039
        assert feature['region'] ==  19
        assert feature['subregion'] ==  29
        assert feature['lon'] ==  -61.783
        assert feature['lat'] ==  17.078

        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select OGC_FID,GEOMETRY from world_merc)',
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['OGC_FID'] ==  1
        assert len(feature) ==  1

        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select GEOMETRY,OGC_FID,fips from world_merc)',
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['OGC_FID'] ==  1
        assert feature['fips'] ==  u'AC'

        # same as above, except with alias like postgres requires
        # TODO - should we try to make this work?
        # ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
        #    table='(select GEOMETRY,rowid as aliased_id,fips from world_merc) as table',
        #    key_field='aliased_id'
        #    )
        #fs = iter(ds)
        #feature = next(fs)
        # assert feature['aliased_id'] == 1
        # assert feature['fips'] == u'AC'

        ds = mapnik.SQLite(file='../data/sqlite/world.sqlite',
                           table='(select GEOMETRY,OGC_FID,OGC_FID as rowid,fips from world_merc)',
                           )
        fs = iter(ds)
        feature = next(fs)
        assert feature['rowid'] ==  1
        assert feature['fips'] ==  u'AC'

    test_subqueries.requires_data = True

    def test_empty_db():
        ds = mapnik.SQLite(file='../data/sqlite/empty.db',
                           table='empty',
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_empty_db.requires_data = True


    def test_that_nonexistant_query_field_throws(**kwargs):
        ds = mapnik.SQLite(file='../data/sqlite/empty.db',
                           table='empty',
                           )
        assert len(ds.fields()) ==  25
        assert ds.fields() == ['OGC_FID',
                               'scalerank',
                               'labelrank',
                               'featurecla',
                               'sovereignt',
                               'sov_a3',
                               'adm0_dif',
                               'level',
                               'type',
                               'admin',
                               'adm0_a3',
                               'geou_dif',
                               'name',
                               'abbrev',
                               'postal',
                               'name_forma',
                               'terr_',
                               'name_sort',
                               'map_color',
                               'pop_est',
                               'gdp_md_est',
                               'fips_10_',
                               'iso_a2',
                               'iso_a3',
                               'iso_n3']
        assert ds.field_types() ==  ['int',
                                     'int',
                                     'int',
                                     'str',
                                     'str',
                                     'str',
                                     'float',
                                     'float',
                                     'str',
                                     'str',
                                     'str',
                                     'float',
                                     'str',
                                     'str',
                                     'str',
                                     'str',
                                     'str',
                                     'str',
                                     'float',
                                     'float',
                                     'float',
                                     'float',
                                     'str',
                                     'str',
                                     'float']
        query = mapnik.Query(ds.envelope())
        for fld in ds.fields():
            query.add_property_name(fld)
        # also add an invalid one, triggering throw
        query.add_property_name('bogus')
        with pytest.raises(RuntimeError):
            ds.features(query)

    test_that_nonexistant_query_field_throws.requires_data = True

    def test_intersects_token1():
        ds = mapnik.SQLite(file='../data/sqlite/empty.db',
                           table='(select * from empty where !intersects!)',
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_intersects_token1.requires_data = True

    def test_intersects_token2():
        ds = mapnik.SQLite(file='../data/sqlite/empty.db',
                           table='(select * from empty where "a"!="b" and !intersects!)',
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_intersects_token2.requires_data = True

    def test_intersects_token3():
        ds = mapnik.SQLite(file='../data/sqlite/empty.db',
                           table='(select * from empty where "a"!="b" and !intersects!)',
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None

    test_intersects_token3.requires_data = True

    # https://github.com/mapnik/mapnik/issues/1537
    # this works because key_field is manually set
    def test_db_with_one_text_column():
        # form up an in-memory test db
        wkb = '010100000000000000000000000000000000000000'
        ds = mapnik.SQLite(file=':memory:',
                           table='test1',
                           initdb='''
                create table test1 (alias TEXT,geometry BLOB);
                insert into test1 values ("test",x'%s');
                ''' % wkb,
                           extent='-180,-60,180,60',
                           use_spatial_index=False,
                           key_field='alias'
                           )
        assert len(ds.fields()) ==  1
        assert ds.fields() ==  ['alias']
        assert ds.field_types() ==  ['str']
        fs = list(iter(ds))
        assert len(fs) ==  1
        feat = fs[0]
        assert feat.id() ==  0  # should be 1?
        assert feat['alias'] ==  'test'
        assert feat.geometry.to_wkt() ==  'POINT(0 0)'

    def test_db_with_one_untyped_column():
        # form up an in-memory test db
        wkb = '010100000000000000000000000000000000000000'
        ds = mapnik.SQLite(file=':memory:',
                           table='test1',
                           initdb='''
                create table test1 (geometry BLOB, untyped);
                insert into test1 values (x'%s', 'untyped');
            ''' % wkb,
                           extent='-180,-60,180,60',
                           use_spatial_index=False,
                           key_field='rowid'
                           )

        # ensure the untyped column is found
        assert len(ds.fields()) ==  2
        assert ds.fields(), ['rowid' ==  'untyped']
        assert ds.field_types(), ['int' ==  'str']

    def test_db_with_one_untyped_column_using_subquery():
        # form up an in-memory test db
        wkb = '010100000000000000000000000000000000000000'
        ds = mapnik.SQLite(file=':memory:',
                           table='(SELECT rowid, geometry, untyped FROM test1)',
                           initdb='''
                create table test1 (geometry BLOB, untyped);
                insert into test1 values (x'%s', 'untyped');
            ''' % wkb,
                           extent='-180,-60,180,60',
                           use_spatial_index=False,
                           key_field='rowid'
                           )

        # ensure the untyped column is found
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['rowid', 'untyped' ==  'rowid']
        assert ds.field_types(), ['int', 'str' ==  'int']

    def test_that_64bit_int_fields_work():
        ds = mapnik.SQLite(file='../data/sqlite/64bit_int.sqlite',
                           table='int_table',
                           use_spatial_index=False
                           )
        assert len(ds.fields()) ==  3
        assert ds.fields(), ['OGC_FID', 'id' ==  'bigint']
        assert ds.field_types(), ['int', 'int' ==  'int']
        fs = iter(ds)
        feat = next(fs)
        assert feat.id() ==  1
        assert feat['OGC_FID'] ==  1
        assert feat['bigint'] ==  2147483648
        feat = next(fs)
        assert feat.id() ==  2
        assert feat['OGC_FID'] ==  2
        assert feat['bigint'] ==  922337203685477580

    test_that_64bit_int_fields_work.requires_data = True

    def test_null_id_field():
        # silence null key warning:
        # https://github.com/mapnik/mapnik/issues/1889
        default_logging_severity = mapnik.logger.get_severity()
        mapnik.logger.set_severity(getattr(mapnik.severity_type, "None"))
        # form up an in-memory test db
        wkb = '010100000000000000000000000000000000000000'
        # note: the osm_id should be declared INTEGER PRIMARY KEY
        # but in this case we intentionally do not make this a valid pkey
        # otherwise sqlite would turn the null into a valid, serial id
        ds = mapnik.SQLite(file=':memory:',
                           table='test1',
                           initdb='''
                create table test1 (osm_id INTEGER,geometry BLOB);
                insert into test1 values (null,x'%s');
                ''' % wkb,
                           extent='-180,-60,180,60',
                           use_spatial_index=False,
                           key_field='osm_id'
                           )
        fs = iter(ds)
        feature = None
        try:
            feature = next(fs)
        except StopIteration:
            pass
        assert feature ==  None
        mapnik.logger.set_severity(default_logging_severity)
