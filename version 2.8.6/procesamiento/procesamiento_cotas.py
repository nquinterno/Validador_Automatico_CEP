
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

#--- 2.4.3 INICIO Validación de Cotas --#

def chequeo_cotas(doc, parcelas_poly_close, medidas_dxf):
##  global layer_cotas_parc_1
    
    validaciones_cotas = DataFrame()
    lados_parcelas_l = list()
    
    cotas = doc.query('DIMENSION')
    cotas_parc= doc.query('DIMENSION[layer=="03-P-MEDIDAS-PARCELA"]') | doc.query('ARC_DIMENSION[layer=="03-P-MEDIDAS-PARCELA"]')
    band_cparc_model = list() #ok
    band_cparc_med = list() #ok
    band_cota_lineal = list() #ver si lo usa otra funcion
    band_parc_arc = list() #ok

    lados_parcelas=0

    cotas_parc_lado = list() #ok
    cotas_parc_ang = list() #ok
    valores_cotas_lado = list() #ok
    band_valores_cotas = list() #ok

    if len(parcelas_poly_close)>0:
        for parcela in parcelas_poly_close:
            if parcela.has_arc:
                band_parc_arc.append("1")
            else:
                band_parc_arc.append("0")

            lados_parcelas_l.append(len(parcela))
    else:
        lados_parcelas_l.append(0)
    

    if len (cotas_parc)>0:

        #verifica que tipo de acotaciones se utilizo para la parcela 162 = angular, 32 = lineal, 33 = alineado,

        for cota in cotas_parc:

            if cota.dxf.dimtype == 162:
                cotas_parc_ang.append(cota)

            elif (cota.dxf.dimtype == 33) or (cota.dxf.dimtype == 8) or (cota.dxf.dimtype == 37) or (cota.dxf.dimtype == 165) or (cota.dxf.dimtype == 161):
                cotas_parc_lado.append(cota)
                valores_cotas_lado.append(round(cota.dxf.actual_measurement,2))

            elif (cota.dxf.dimtype == 32):
                band_cota_lineal.append('-1')
                
            else:
                pass

            for i in range (len(lados_parcelas_l)):         #Para todas las parcelas suma la cantidad de lados que tiene para comparar con la cantidad de cotas realizadas 
                lados_parcelas=lados_parcelas+lados_parcelas_l[i]

           
        for cota in cotas_parc:        
            if cota.dxf.paperspace==0:
                band_cparc_model.append('-1')
            else:
                band_cparc_model.append('0')

            if len(cota.dxf.text)==0:
                band_cparc_med.append('0')
            else:
                band_cparc_med.append('-1') 

        for valor in valores_cotas_lado:
            for medida in medidas_dxf:
                if abs(valor - medida["medida"]) <= 0.01:
                    band_valores_cotas.append("0")
                else:
                    pass

        if '-1' in  band_cparc_model:
            validaciones_cotas.loc[0,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[0,'Observacion']="ERROR: Se acotó en el model"
            validaciones_cotas.loc[0,'Cetegoría']='Acotaciones'
        else:
            validaciones_cotas.loc[0,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[0,'Observacion']="OK: Se acoto en el Layout"
            validaciones_cotas.loc[0,'Cetegoría']='Acotaciones'
            
        if '-1' in  band_cparc_med:
            validaciones_cotas.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[1,'Observacion']="ERROR: Se modificó el valor real de alguna de las cotas de parcelas"
            validaciones_cotas.loc[1,'Cetegoría']='Acotaciones'
        else:
            if len(band_valores_cotas) >= len (medidas_dxf):
                validaciones_cotas.loc[1,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones_cotas.loc[1,'Observacion']="OK: No se han modificado los valores reales de las cotas de parcelas"
                validaciones_cotas.loc[1,'Cetegoría']='Acotaciones'
        
            else:
                validaciones_cotas.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_cotas.loc[1,'Observacion']="ERROR: No coinciden los valores de las acotaciones con las medidas reales de los lados de la parcelas"
                validaciones_cotas.loc[1,'Cetegoría']='Acotaciones'

        if (lados_parcelas_l[0] == len(cotas_parc)):
            validaciones_cotas.loc[2,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[2,'Observacion']="OK: Se acotó correctamente"
            validaciones_cotas.loc[2,'Cetegoría']='Acotaciones'            
        else:
            if "1" in band_parc_arc:
                validaciones_cotas.loc[2,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones_cotas.loc[2,'Observacion']="OK: Se acotó correctamente"
                validaciones_cotas.loc[2,'Cetegoría']='Acotaciones'   
            else:
                validaciones_cotas.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_cotas.loc[2,'Observacion']="ERROR:No coinciden el N° de lados de la parcela con el N° de acotaciones aligned realizadas, o no están en el layer '03-P-MEDIDAS-PARCELA'"
                validaciones_cotas.loc[2,'Cetegoría']='Acotaciones'
    else:

        if len(cotas)==0:
            validaciones_cotas.loc[0,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[0,'Observacion']="ERROR: No se uso un Dimensionado para acotar"
            validaciones_cotas.loc[0,'Cetegoría']='Acotaciones'

            validaciones_cotas.loc[1,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[1,'Observacion']="ERROR: No se uso un Dimensionado para acotar"
            validaciones_cotas.loc[1,'Cetegoría']='Acotaciones'

            validaciones_cotas.loc[2,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[2,'Observacion']="ERROR: No se uso un Dimensionado 'Alineado' o 'de arco' para acotar"
            validaciones_cotas.loc[2,'Cetegoría']='Acotaciones'
        else:

            validaciones_cotas.loc[0,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[0,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones_cotas.loc[0,'Cetegoría']='Acotaciones'

            validaciones_cotas.loc[1,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[1,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones_cotas.loc[1,'Cetegoría']='Acotaciones'

            validaciones_cotas.loc[2,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones_cotas.loc[2,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones_cotas.loc[2,'Cetegoría']='Acotaciones'
    
    return validaciones_cotas, lados_parcelas_l
              


