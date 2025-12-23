
import ezdxf
from ezdxf.math import is_point_in_polygon_2d, Vec2
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
    band_bloque = list()

    #chequeo que todos los bloques del dxf esten en el archivo de configuracion
    for bloque in Bloques_DXF:
        if bloque in Plant_Bloques:
            band_bloque_nombre.append('0')
        else:
            band_bloque_nombre.append('-1')

    #chequeo que todos los bloques del archivo de configuracion esten en el dxf
    for bloque in Plant_Bloques:
        if bloque in Bloques_DXF:
            band_bloque.append('0')
        else:
            band_bloque.append('-1')
    
    bloque_PARCELA_SURGENTE = doc.modelspace().query('INSERT[name=="PARCELA_SURGENTE"]')
    bloque_form = doc.modelspace().query('INSERT[name=="form"]')
    

    band_parc_surg = list()

    band_form_1 = list()
    band_form_2 = list()
    
    if len(bloque_PARCELA_SURGENTE)>0:
        for attrib in bloque_PARCELA_SURGENTE[0].attribs:
            if attrib.dxf.tag=="NPARC":
                band_parc_surg.append("0")
            else:
                band_parc_surg.append("-1")
    else:
        band_parc_surg.append("-2")
    
    if len(bloque_form)>0:
        for bloque in bloque_form:
            band_form_polig_atrib = list()
            band_form_tipo_atrib = list()
            band_form_N_atrib = list()
            band_form_0 = list()
            for attrib in bloque.attribs:

                if attrib.dxf.tag=="Nº_POLIG.":
                    band_form_polig_atrib.append("0")
                else:
                    band_form_polig_atrib.append("-1")
                
                if attrib.dxf.tag=="TIPO_FORM":
                    band_form_tipo_atrib.append("0")
                else:
                    band_form_tipo_atrib.append("-1")

                if attrib.dxf.tag=="Nº_FORM":
                    band_form_N_atrib.append("0")
                else:
                    band_form_N_atrib.append("-1")
            
            if "0" in band_form_polig_atrib:
                band_form_0.append(0)
            else:
                band_form_0.append(-1)
            
            if "0" in band_form_tipo_atrib:
                band_form_0.append(0)
            else:
                band_form_0.append(-1)

            if "0" in band_form_N_atrib:
                band_form_0.append(0)
            else:
                band_form_0.append(-1)
            
            band_form_1.append(band_form_0)

        for band in band_form_1:
            if "-1" in band:
                band_form_2.append("-1")
            else:
                band_form_2.append("0")
        
        if "-1" in band_form_2:
            band_form = "-1"
        else:
            band_form = "0"
    else:
        band_form = "-2"

    if '-1' in band_bloque_nombre:
            validaciones_bloques.loc[0,'Resultado']=-1
            validaciones_bloques.loc[0,'Observacion']='ERROR: Existen más Bloques en el archivo dxf que los admitidos en la plantilla'
            validaciones_bloques.loc[0,'Cetegoría']='Bloques' 
    else:
        if "-1" in band_bloque:
            validaciones_bloques.loc[0,'Resultado']=-1
            validaciones_bloques.loc[0,'Observacion']='ERROR: No se han detectado todos los bloques de la plantilla en el archivo dxf'
            validaciones_bloques.loc[0,'Cetegoría']='Bloques'
        else:
            validaciones_bloques.loc[0,'Resultado']=0
            validaciones_bloques.loc[0,'Observacion']='OK: Se han detectado todos los Bloques de la palantilla en el archivo DXF'
            validaciones_bloques.loc[0,'Cetegoría']='Bloques'

    if "-1" in band_form:
        validaciones_bloques.loc[1,'Resultado']=-1
        validaciones_bloques.loc[1,'Observacion']='ERROR: El bloque "form" tiene atributos modificados respecto a la plantilla aprobada'
        validaciones_bloques.loc[1,'Cetegoría']='Bloques'
    else:
        validaciones_bloques.loc[1,'Resultado']=0
        validaciones_bloques.loc[1,'Observacion']='OK: El bloque "form" tiene atributos sin modificación respecto a la plantilla aprobada'
        validaciones_bloques.loc[1,'Cetegoría']='Bloques'

    if "-1" in band_parc_surg:
        validaciones_bloques.loc[2,'Resultado']=-1
        validaciones_bloques.loc[2,'Observacion']='ERROR: El bloque "PARCELA_SURGENTE" tiene atributos modificados respecto a la plantilla aprobada'
        validaciones_bloques.loc[2,'Cetegoría']='Bloques'
    else:
        validaciones_bloques.loc[2,'Resultado']=0
        validaciones_bloques.loc[2,'Observacion']='OK: El bloque "PARCELA_SURGENTE" tiene atributos sin modificación respecto a la plantilla aprobada'
        validaciones_bloques.loc[2,'Cetegoría']='Bloques'

    return validaciones_bloques
    #------>
#--- 2.2 FIN Validación de bloques --#

#--- 2.4 INICIO Validación de elementos de Layout --#
    
    #--- 2.4.3 INICIO Validación de Cotas --#
