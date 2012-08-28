import unittest
import re

from nose.tools import eq_, raises


def eq_sql(a, b, msg=None):
    a = re.sub(r'[\n\t]', '', str(a))
    eq_(a, b, msg)


class TestGeometry(unittest.TestCase):

    def _create_table(self):
        from sqlalchemy import Table, MetaData, Column
        from geoalchemy2.types import Geometry
        table = Table('table', MetaData(), Column('geom', Geometry))
        return table

    def test_column_expression(self):
        from sqlalchemy.sql import select
        table = self._create_table()
        s = select([table.c.geom])
        eq_sql(s, 'SELECT ST_AsBinary("table".geom) AS geom_1 FROM "table"')

    def test_select_bind_expression(self):
        from sqlalchemy.sql import select
        table = self._create_table()
        s = select(['foo']).where(table.c.geom == 'POINT(1 2)')
        eq_sql(s, 'SELECT foo FROM "table" WHERE '
                  '"table".geom = ST_GeomFromText(:geom_1)')
        eq_(s.compile().params, {'geom_1': 'POINT(1 2)'})

    def test_insert_bind_expression(self):
        from sqlalchemy.sql import insert
        table = self._create_table()
        i = insert(table).values(geom='POINT(1 2)')
        eq_sql(i, 'INSERT INTO "table" (geom) VALUES (ST_GeomFromText(:geom))')
        eq_(i.compile().params, {'geom': 'POINT(1 2)'})

    def test_function_call(self):
        from sqlalchemy.sql import select
        table = self._create_table()
        s = select([table.c.geom.ST_Buffer(2)])
        eq_sql(s,
               'SELECT ST_AsBinary(ST_Buffer("table".geom, :param_1)) '
               'AS "ST_Buffer_1" FROM "table"')

    @raises(AttributeError)
    def test_non_ST_function_call(self):
        table = self._create_table()
        table.c.geom.Buffer(2)


class TestOperator(unittest.TestCase):

    def _create_table(self):
        from sqlalchemy import Table, MetaData, Column
        from geoalchemy2.types import Geometry
        table = Table('table', MetaData(), Column('geom', Geometry))
        return table

    def test_eq(self):
        table = self._create_table()
        expr = table.c.geom == 'POINT(1 2)'
        eq_sql(expr, '"table".geom = ST_GeomFromText(:geom_1)')

    def test_eq_with_None(self):
        table = self._create_table()
        expr = table.c.geom == None
        eq_sql(expr, '"table".geom IS NULL')

    def test_ne(self):
        table = self._create_table()
        expr = table.c.geom != 'POINT(1 2)'
        eq_sql(expr, '"table".geom != ST_GeomFromText(:geom_1)')

    def test_ne_with_None(self):
        table = self._create_table()
        expr = table.c.geom != None
        eq_sql(expr, '"table".geom IS NOT NULL')

    def test_intersects(self):
        table = self._create_table()
        expr = table.c.geom.intersects('POINT(1 2')
        eq_sql(expr, '"table".geom && ST_GeomFromText(:geom_1)')

    def test_overlaps_or_left(self):
        table = self._create_table()
        expr = table.c.geom.overlaps_or_left('POINT(1 2')
        eq_sql(expr, '"table".geom &< ST_GeomFromText(:geom_1)')


class TestWKBElement(unittest.TestCase):

    def test_desc(self):
        from geoalchemy2.types import WKBElement
        e = WKBElement('\x01\x02')
        eq_(e.desc, '0102')

    def test_function_call(self):
        from geoalchemy2.types import WKBElement
        e = WKBElement('\x01\x02')
        f = e.ST_Buffer(2)
        eq_sql(f,
               'ST_Buffer(ST_GeomFromWKB(:ST_GeomFromWKB_1), :param_1)')
        eq_(f.compile().params,
            {u'ST_GeomFromWKB_1': '\x01\x02', u'param_1': 2})

    @raises(AttributeError)
    def test_non_ST_function_call(self):
        from geoalchemy2.types import WKBElement
        e = WKBElement('\x01\x02')
        e.Buffer(2)