1. PostGIS is used to handle location fields which requires:
    A. Postgis installed on the system
    B. Postgresql extension: postgis32_15
    C. Commands CREATE EXTENSION postgis; and CREATE EXTENSION postgis_topology; must be enabled in postgres
    D. Change of database engine: django.contrib.gis.db.backends.postgis