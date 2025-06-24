
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

      
#--- 2.1 INICIO  Validación de layers --#
        
def chequeo_layers(doc):

    validaciones_layers = DataFrame()
    
    # global nom_layers_dxf
    
    #inicio Carga Info de layers de archivo y de plantilla
    Layers_DXF = DataFrame() #crea data frame para almacenar los layers del archivo con su configuración
    nombre_layers,color_layers,linea_layers, grosor_layers = list(), list(), list(), list() #crea listas que tendran datos de los layers del dxf y pasaran al data frame

    for layer in doc.layers:                 ##-- Guarda la configuración de los layers en listas
        nombre_layers.append(layer.dxf.name) ##-- guarda nombre de los layers en una lista
        color_layers.append(layer.dxf.color) ##-- guarda nombre de los layers en una lista
        linea_layers.append(layer.dxf.linetype) ##-- guarda nombre de los layers en una lista
        grosor_layers.append(layer.dxf.lineweight) ##-- guarda nombre de los layers en una lista

    Layers_DXF = DataFrame(list(zip(nombre_layers,color_layers,linea_layers, grosor_layers)), columns = ['Nombre','Color','Tipo_Linea','Grosor_Linea']) #arma data frame con los layers y su configuracion
    
    Layers_DXF = Layers_DXF.sort_values('Nombre', ascending=True) #ordena la tabla de layers del DXF en forma ascdenete para poder comparar con la de la plantilla
    Layers_DXF.reset_index(inplace=True, drop=True) #resetea el indice de la tabla ordenada para poder comparar con la de la plantilla
    plantilla_2 = read_csv('configuracion/Config_Layers.csv') #data frame con archivo de ocnfiguración de layers csv
    del  nombre_layers,color_layers,linea_layers, grosor_layers ##-- Borra las listas de layers que ya no se usan

    # layer_count_DXF = len(doc.layers) ##-- Cuenta el total de layers del archivo DXF
    # layer_count_plantilla = len(plantilla_2) ##-- Cuenta el total de layers del archivo DXF

    elim_nom_layer = list()
    nom_layers_dxf = Layers_DXF["Nombre"].tolist()
    nom_layers_plant = plantilla_2["Nombre"].tolist()
    band_dxf_plant = list()


    for i in range (0,len(nom_layers_dxf)):      # Elimina los elementos que no son bloques del dxf y correconden al layout, model, etc.
       if '@' in nom_layers_dxf[i]:
            elim_nom_layer.append(nom_layers_dxf[i]) 

    for i in range (0,len(elim_nom_layer)):
        nom_layers_dxf.remove(elim_nom_layer[i])
    
    #FIN Carga Info de layers de archivo y de plantilla

    #Inicio Validar Layers

    for layer in nom_layers_plant:
        if layer in nom_layers_dxf:
            band_dxf_plant.append('0')
        else:
            band_dxf_plant.append('-1')

    if '-1' in band_dxf_plant:
        validaciones_layers.loc[0,'Resultado']=-1
        validaciones_layers.loc[0,'Observacion']='ERROR: Faltan Layers de la plantilla'

    else:

        validaciones_layers.loc[0,'Resultado']=0
        validaciones_layers.loc[0,'Observacion']='OK: Se han detectado todos los layers de la palantilla en el archivo DXF'

    return validaciones_layers, nom_layers_dxf
    #validar que el layer muro este como no imprimible
          
#--- 2.1 FIN Validación de layers --#         

#--- 2.2 INICIO Validación de bloques --#

