
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


#--- 2.2 INICIO Validación de bloques --#

def chequeo_bloques (doc):

    nombre_bloque = list()
    validaciones_bloques = DataFrame()

    for block in doc.blocks:                 ##-- Guarda información de los bloques en una lista
            nombre_bloque.append(block.dxf.name) ##-- guarda nombre de los bloques en una lista
    elim_bloque=list()

    for i in range (0,len(nombre_bloque)):      # Elimina los elementos que no son bloques del dxf y correconden al layout, model, etc.
       if '*' in nombre_bloque[i]:
            elim_bloque.append(nombre_bloque[i]) 

    for i in range (0,len(elim_bloque)):
        nombre_bloque.remove(elim_bloque[i])

    Plant_Bloques = read_csv('configuracion/Config_Bloques.csv') #data frame con archivo de configuración de bloques csv
    Bloques_DXF = DataFrame(list(zip(nombre_bloque)), columns = ['Nombre']) #,'Color','Tipo_Linea','Grosor_Linea']), bloques del archivo dxf

    band_bloque_nombre = list()

    for bloque in Bloques_DXF:
        if bloque in Plant_Bloques:
            band_bloque_nombre.append('0')
        else:
            band_bloque_nombre.append('-1')

    if '-1' in band_bloque_nombre:
            validaciones_bloques.loc[0,'Resultado']=-1
            validaciones_bloques.loc[0,'Observacion']='ERROR: Existen más Bloques en el archivo dxf que los admitidos en la plantilla'
            validaciones_bloques.loc[0,'Cetegoría']='Bloques' 
    else:
            validaciones_bloques.loc[0,'Resultado']=0
            validaciones_bloques.loc[0,'Observacion']='OK: Se han detectado todos los Bloques de la palantilla en el archivo DXF'
            validaciones_bloques.loc[0,'Cetegoría']='Bloques' 

    return validaciones_bloques
    #------>
#--- 2.2 FIN Validación de bloques --#

#--- 2.4 INICIO Validación de elementos de Layout --#
    
    #--- 2.4.3 INICIO Validación de Cotas --#
