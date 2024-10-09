
import ezdxf
from ezdxf.math.construct2d import is_point_in_polygon_2d, Vec2
from pandas import DataFrame, read_excel, read_csv
from procesamiento.catastroBox import rumbo, medidaLadoPol, sup_polilinea, discretizar_curva, polig_dentro_polig
import re
import difflib
from json import loads
from requests import get
from geopandas import GeoSeries
from shapely import Polygon, union, difference, area, geometry, Point
from tkinter import*
from tkinter import messagebox, filedialog, ttk

def chequeo_archivo(doc):
    
    validaciones_archivo = DataFrame()
    version_arch = doc.header['$ACADVER']
    version_num = int(version_arch.replace("AC",""))
    version_no = ['AC1009','AC1012','AC1014','AC1015']

    if (version_num >= 1032) or (version_num <= 1015):
        validaciones_archivo.loc[0,'Resultado']=-1
        validaciones_archivo.loc[0,'Observacion']='ERROR: Las Versiones de DXF admitidas son 2004, 2007, 2010 y 2013'
    else:
        validaciones_archivo.loc[0,'Resultado']=0
        validaciones_archivo.loc[0,'Observacion']='OK: Versión de Archivo DXF correcta'
    return validaciones_archivo  
#--- 2.1 FIN  Validación de versión de archivo --#
        
