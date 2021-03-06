"""

This module defines the :class:`GenericFunction` class, which is the base for
the implementation of spatial functions in GeoAlchemy.  This module is also
where actual spatial functions are defined. Spatial functions supported by
GeoAlchemy are defined in this module. See :class:`GenericFunction` to know how
to create new spatial functions.

.. note::

    By convention the names of spatial functions are prefixed by ``ST_``.  This
    is to be consistent with PostGIS', which itself is based on the ``SQL-MM``
    standard.

Functions created by subclassing :class:`GenericFunction` can be called
in several ways:

* By using the ``func`` object, which is the SQLAlchemy standard way of calling
  a function. For example, without the ORM::

      select([func.ST_Area(lake_table.c.geom)])

  and with the ORM::

      Session.query(func.ST_Area(Lake.geom))

* By applying the function to a geometry column. For example, without the
  ORM::

      select([lake_table.c.geom.ST_Area()])

  and with the ORM::

      Session.query(Lake.geom.ST_Area())

* By applying the function to a :class:`geoalchemy2.elements.WKBElement`
  object (:class:`geoalchemy2.elements.WKBElement` is the type into
  which GeoAlchemy converts geometry values read from the database), or
  to a :class:`geoalchemy2.elements.WKTElement` object. For example,
  without the ORM::

      conn.scalar(lake['geom'].ST_Area())

  and with the ORM::

      session.scalar(lake.geom.ST_Area())

Reference
---------

"""

from sqlalchemy.sql import functions

from . import types


class GenericFunction(functions.GenericFunction):
    """
    The base class for GeoAlchemy functions.

    This class inherits from ``sqlalchemy.sql.functions.GenericFunction``, so
    functions defined by subclassing this class can be given a fixed return
    type. For example, functions like :class:`ST_Buffer` and
    :class:`ST_Envelope` have their ``type`` attributes set to
    :class:`geoalchemy2.types.Geometry`.

    This class allows constructs like ``Lake.geom.ST_Buffer(2)``. In that
    case the ``Function`` instance is bound to an expression (``Lake.geom``
    here), and that expression is passed to the function when the function
    is actually called.

    If you need to use a function that GeoAlchemy does not provide you will
    certainly want to subclass this class. For example, if you need the
    ``ST_TransScale`` spatial function, which isn't (currently) natively
    supported by GeoAlchemy, you will write this::

        from geoalchemy2 import Geometry
        from geoalchemy2.functions import GenericFunction

        class ST_TransScale(GenericFunction):
            name = 'ST_TransScale'
            type = Geometry
    """

    def __init__(self, *args, **kwargs):
        expr = kwargs.pop('expr', None)
        if expr is not None:
            args = (expr,) + args
        functions.GenericFunction.__init__(self, *args, **kwargs)


# Functions are classified as in the PostGIS doc.
# <http://www.postgis.org/documentation/manual-svn/reference.html>


_FUNCTIONS = [
    #
    # Geometry Accessors
    #

    ('ST_Envelope', types.Geometry,
     'Returns a geometry representing the double precision (float8) bounding'
     'box of the supplied geometry.'),

    ('ST_GeometryN', None,
     'Return the 1-based Nth geometry if the geometry is a '
     '``GEOMETRYCOLLECTION``, ``(MULTI)POINT``, ``(MULTI)LINESTRING``, '
     '``MULTICURVE`` or ``(MULTI)POLYGON``, ``POLYHEDRALSURFACE`` Otherwise, '
     'return ``NULL``.'),

    ('ST_GeometryType', None,
     'Return the geometry type of the ``ST_Geometry`` value.'),

    ('ST_IsValid', None,
     'Returns ``true`` if the ``ST_Geometry`` is well formed.'),

    ('ST_NPoints', None,
     'Return the number of points (vertexes) in a geometry.'),

    ('ST_SRID', None,
     'Returns the spatial reference identifier for the ``ST_Geometry`` as '
     'defined in ``spatial_ref_sys`` table.'),

    ('ST_X', None,
     'Return the X coordinate of the point, or ``NULL`` if not available. '
     'Input must be a point.'),

    ('ST_Y', None,
     'Return the Y coordinate of the point, or ``NULL`` if not available. '
     'Input must be a point.'),

    #
    # Geometry Editors
    #

    ('ST_Transform', types.Geometry,
     'Returns a new geometry with its coordinates transformed to the SRID '
     'referenced by the integer parameter.'),

    #
    # Geometry Outputs
    #

    ('ST_AsBinary', None,
     'Return the Well-Known Binary (WKB) representation of the geometry/'
     'geography without SRID meta data.'),

    ('ST_AsGeoJSON', None, 'Return the geometry as a GeoJSON element.'),

    ('ST_AsGML', None, 'Return the geometry as a GML version 2 or 3 element.'),

    ('ST_AsKML', None,
     'Return the geometry as a KML element. Several variants. Default '
     'version=2, default precision=15'),

    ('ST_AsSVG', None,
     'Returns a Geometry in SVG path data given a geometry or geography '
     'object.'),

    ('ST_AsText', None,
     'Return the Well-Known Text (WKT) representation of the geometry/'
     'geography without SRID metadata.'),

    #
    # Spatial Relationships and Measurements
    #

    ('ST_Area', None,
     'Returns the area of the surface if it is a polygon or multi-polygon. '
     'For ``geometry`` type area is in SRID units. For ``geography`` area is '
     'in square meters.'),

    ('ST_Centroid', types.Geometry,
     'Returns the geometric center of a geometry.'),

    ('ST_Contains', None,
     'Returns true if and only if no points of B lie in the exterior of A, '
     'and at least one point of the interior of B lies in the interior of A.'),

    ('ST_ContainsProperly', None,
     'Returns true if B intersects the interior of A but not the boundary '
     '(or exterior). A does not contain properly itself, but does contain '
     'itself.'),

    ('ST_Covers', None,
     'Returns 1 (TRUE) if no point in Geometry B is outside Geometry A'),

    ('ST_CoveredBy', None,
     'Returns 1 (TRUE) if no point in Geometry/Geography A is outside Geometry'
     '/Geography B'),

    ('ST_Crosses', None,
     'Returns TRUE if the supplied geometries have some, but not all, '
     'interior points in common.'),

    ('ST_Disjoint', None,
     ' Returns TRUE if the Geometries do not "spatially intersect" - if they '
     'do not share any space together.'),

    ('ST_Distance', None,
     'For geometry type Returns the 2-dimensional cartesian minimum distance '
     '(based on spatial ref) between two geometries in projected units. For '
     'geography type defaults to return spheroidal minimum distance between '
     'two geographies in meters.'),

    ('ST_Distance_Sphere', None,
     'Returns minimum distance in meters between two lon/lat geometries. Uses '
     'a spherical earth and radius of 6370986 meters. Faster than '
     '``ST_Distance_Spheroid``, but less accurate. PostGIS versions '
     'prior to 1.5 only implemented for points.'),

    ('ST_DFullyWithin', None,
     'Returns true if all of the geometries are within the specified distance '
     'of one another'),

    ('ST_DWithin', None,
     'Returns true if the geometries are within the specified distance of one '
     'another. For geometry units are in those of spatial reference and For '
     'geography units are in meters and measurement is defaulted to '
     '``use_spheroid=true`` (measure around spheroid), for faster check, '
     '``use_spheroid=false`` to measure along sphere.'),

    ('ST_Equals', None,
     'Returns true if the given geometries represent the same geometry. '
     'Directionality is ignored.'),

    ('ST_Intersects', None,
     'Returns ``TRUE`` if the Geometries/Geography "spatially intersect in '
     '2D" - (share any portion of space) and ``FALSE`` if they don\'t (they '
     'are Disjoint). For geography -- tolerance is 0.00001 meters (so any '
     'points that close are considered to intersect)'),

    ('ST_Length', None,
     'Returns the 2d length of the geometry if it is a linestring or '
     'multilinestring. geometry are in units of spatial reference and '
     'geography are in meters (default spheroid)'),

    ('ST_OrderingEquals', None,
     'Returns true if the given geometries represent the same geometry and '
     'points are in the same directional order.'),

    ('ST_Overlaps', None,
     'Returns TRUE if the Geometries share space, are of the same dimension, '
     'but are not completely contained by each other.'),

    ('ST_Perimeter', None,
     'Return the length measurement of the boundary of an ST_Surface or '
     'ST_MultiSurface geometry or geography. (Polygon, Multipolygon). '
     'geometry measurement is in units of spatial reference and geography is '
     'in meters.'),

    ('ST_Project', types.Geography,
     'Returns a ``POINT`` projected from a start point using a distance in '
     'meters and bearing (azimuth) in radians.'),

    ('ST_Relate', None,
     'Returns ``TRUE`` if this Geometry is spatially related to '
     'anotherGeometry, by testing for intersections between the Interior, '
     'Boundary and Exterior of the two geometries as specified by the values '
     'in the intersectionMatrixPattern. If no intersectionMatrixPattern is '
     'passed in, then returns the maximum intersectionMatrixPattern that '
     'relates the 2 geometries.'),

    ('ST_Touches', None,
     'Returns ``TRUE`` if the geometries have at least one point in common, '
     'but their interiors do not intersect.'),

    ('ST_Within', None,
     'Returns ``TRUE`` if the geometry A is completely inside geometry B'),

    #
    # Geometry Processing
    #

    ('ST_Buffer', types.Geometry,
     'For geometry: Returns a geometry that represents all points whose '
     'distance from this Geometry is less than or equal to distance. '
     'Calculations are in the Spatial Reference System of this Geometry.\n\n'
     'For geography: Uses a planar transform wrapper. Introduced in 1.5 '
     'support for different end cap and mitre settings to control shape.'),

    ('ST_Difference', types.Geometry,
     'Returns a geometry that represents that part of geometry A that does '
     'not intersect with geometry B.'),

    ('ST_Intersection', types.Geometry,
     'Returns a geometry that represents the shared portion of geomA and '
     'geomB. The geography implementation does a transform to geometry to do '
     'the intersection and then transform back to WGS84.'),

    ('ST_Union', types.Geometry,
     'Returns a geometry that represents the point set union of the '
     'Geometries.'),
]

# Iterate through _FUNCTION and create GenericFunction classes dynamically
for name, type_, doc in _FUNCTIONS:
    attributes = {'name': name}
    docs = []

    if doc is not None:
        docs.append(doc)
        docs.append('see http://postgis.net/docs/{0}.html'.format(name))

    if type_ is not None:
        attributes['type'] = type_

        type_str = '{0}.{1}'.format(type_.__module__, type_.__name__)
        docs.append('Return type: :class:`{0}`.'.format(type_str))

    if len(docs) != 0:
        attributes['__doc__'] = '\n\n'.join(docs)

    globals()[name] = type(name, (GenericFunction,), attributes)
