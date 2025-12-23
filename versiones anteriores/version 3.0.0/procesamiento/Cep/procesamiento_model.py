
import ezdxf
#from ezdxf.math.construct2d import is_point_in_polygon_2d, Vec2
from ezdxf.math import is_point_in_polygon_2d, Vec2
from pandas import DataFrame, read_excel, read_csv
from procesamiento.General.catastroBox import rumbo, medidaLadoPol, sup_polilinea, discretizar_curva, polig_dentro_polig, invasiones
import re
import difflib
from json import loads
from requests import get
from geopandas import GeoSeries
from shapely import Polygon, union, difference, area, geometry, Point
from tkinter import*
from tkinter import messagebox, filedialog, ttk
import math

#--- 2.5 INICIO Validación de elementos del model --#

def chequeo_model(doc,nom_layers_dxf,colores):

    validaciones_model = DataFrame()

    global parcelas_poly
    global manzana_poly

    global medidas_dxf
    global nom_parc_list
    global band_parc_arc_1
    global sup_arc_parc
    global band_text_style
    #--- 2.5.1 INICIO Validación de Parcela--#
    parcelas = doc.modelspace().query('*[layer=="09-M-PARCELA"]')#  Busca las polylineas en el layer PARCELA
    parcelas_poly=list()
    parcelas_poly_close=list()
    band_poly_parc=list()   #lista de banderas para validar todas las entidades del layer parcela sean polilineas
    band_poly_cer_parc=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_parc=list()
    band_poly_color_parc=list()
    band_parc_arc_1 = list()
    medidas_dxf = list()
    sup_arc_parc = list()
    band_num_layer = list()
    band_text_style = list()
    manzana_poly = list()
    
    
##    Calcular la cantidad de lados que tiene la parcela

    if len(parcelas): #si hay entindades en el layer patrcela comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for parcela in parcelas:
            if parcela.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline
                if parcela.dxftype()!= "INSERT":
                    band_poly_parc.append('-1')
                else:
                    if parcela.dxf.name != "PARCELA_SURGENTE":
                        #band_poly_parc.append('-1') ver que vandera usar para uando hay un bloque inserto en parcela y no es el bloque de parcela surgente
                        band_poly_parc.append('-1')
                    else:
                        band_poly_parc.append('0')
            else:
                band_poly_parc.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline
                parcelas_poly.append(parcela)

        if "-1" in band_poly_parc: # si hay un -1 en la bandera arroja error 
            validaciones_model.loc[0,'Resultado']=-1
            validaciones_model.loc[0,'Observacion']="ERROR: Existen entidades distintas de Polylineas y Bloque de nomenclatura en el Layer 09-M-PARCELA"
            validaciones_model.loc[0,'Cetegoría']='Parcela/s'  
        else:
            for parcela in parcelas_poly:
                if parcela.has_arc:
                    band_parc_arc_1.append("1")
                else:
                    band_parc_arc_1.append("0")
                if parcela.closed:
                    band_poly_cer_parc.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                    parcelas_poly_close.append(parcela)
                else:
                    band_poly_cer_parc.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta

            if len(parcelas_poly)>0:
                lados = parcelas_poly[0].virtual_entities()
                for lado in  lados:
                    if lado.dxftype() == "ARC":

                        medidas_dxf.append({"rumbo":rumbo(parcelas_poly[0],lado),"medida":medidaLadoPol(lado)})
                    else:
                        # if lado.dxf.start == lado.dxf.end:
                        #     pass
                        if math.sqrt(((lado.dxf.end[0]-lado.dxf.start[0])**2)+((lado.dxf.end[1]-lado.dxf.start[1])**2))<=0.001:
                            pass
                        else:

                            medidas_dxf.append({"rumbo":rumbo(parcelas_poly[0],lado),"medida":medidaLadoPol(lado)})
            else:
                pass

            if '-1' in band_poly_cer_parc:
                validaciones_model.loc[0,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[0,'Observacion']="ERROR: Se dibujaron polylineas Abiertas en el layer 09-M-PARCELA"
                validaciones_model.loc[0,'Cetegoría']='Parcela/s'  

            else:# si no hay un -1 en la bandera sigue validando color y grosor de polylineas.

                validaciones_model.loc[0,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[0,'Observacion']="OK: Se dibujaron polylineas Cerradass en el layer 09-M-PARCELA"
                validaciones_model.loc[0,'Cetegoría']='Parcela/s'

        if len(parcelas_poly) > 1:
                validaciones_model.loc[1,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[1,'Observacion']="ERROR: Se dibujaron más de una polylineas en el layer 09-M-PARCELA"
                validaciones_model.loc[1,'Cetegoría']='Parcela/s'

        elif len(parcelas_poly) == 1:
                validaciones_model.loc[1,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[1,'Observacion']="OK: Se dibujó una unica polylinea en el layer 09-M-PARCELA"
                validaciones_model.loc[1,'Cetegoría']='Parcela/s'

        elif len(parcelas_poly) == 0:
                validaciones_model.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[1,'Observacion']="ERROR: No se dibujaron polylineas en el layer 09-M-PARCELA"
                validaciones_model.loc[1,'Cetegoría']='Parcela/s'       

        for parcela in parcelas:
            if parcela.dxf.color==colores.at[0,'Parcela']:   
                band_poly_color_parc.append('0')
            else:
                band_poly_color_parc.append('-1')

            if parcela.dxf.lineweight==-3:
                band_poly_gro_parc.append('0')
            else:
                band_poly_gro_parc.append('-1')

                
        if '0' in band_poly_color_parc and '0' in band_poly_gro_parc:
            validaciones_model.loc[2,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[2,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en el layer 09-M-PARCELA"
            validaciones_model.loc[2,'Cetegoría']='Parcela/s'  

        elif '0' in band_poly_color_parc and '-1' in band_poly_gro_parc:
            validaciones_model.loc[2,'Resultado']=-5 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[2,'Observacion']="ERROR: Grosor de polylineas erroneo en layer 09-M-PARCELA debe ser 'Default'"

        elif '-1' in band_poly_color_parc and '0' in band_poly_gro_parc:
            validaciones_model.loc[2,'Resultado']=-4 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[2,'Observacion']="ERROR: Color de polylineas erroneo en layer 09-M-PARCELA debe ser Azul"
            validaciones_model.loc[2,'Cetegoría']='Parcela/s'  

        elif '-1' in band_poly_color_parc and '-1' in band_poly_gro_parc:
            validaciones_model.loc[2,'Resultado']=-3 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[2,'Observacion']="ERROR: Color y grosor de polylineas erroneo en layer 09-M-PARCELA"
            validaciones_model.loc[2,'Cetegoría']='Parcela/s'
        
    else:
        
        validaciones_model.loc[0,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones_model.loc[0,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones_model.loc[0,'Cetegoría']='Parcela/s'

        validaciones_model.loc[1,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones_model.loc[1,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones_model.loc[1,'Cetegoría']='Parcela/s'

        validaciones_model.loc[2,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones_model.loc[2,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones_model.loc[2,'Cetegoría']='Parcela/s'

    #--- 2.5.1 FIN Validación de Parcela --#

    #--- 2.5.2 INICIO Validación de Antecedentes--#
    m_manzana = doc.modelspace().query('*[layer=="07-M-MANZANA"]')
    m_calles = doc.modelspace().query('*[layer=="05-M-NOMBRE-DE-CALLE"]')
    numeros_puerta = doc.modelspace().query("MTEXT").filter(lambda e: "N°" in e.text or "n°" in e.dxf.text) | doc.modelspace().query("TEXT").filter(lambda e: "N°" in e.dxf.text or "n°" in e.dxf.text)
    
    textos_model = doc.modelspace().query("TEXT")|doc.modelspace().query("MTEXT")
    
    band_ant_manzana = list()
    band_ant_text = list()
    band_calles_text = list()

    estilos = doc.styles
    for text in textos_model:
        if text.dxf.style in estilos:
            style = estilos.get(text.dxf.style)
            if style.dxf.font != "arial.ttf":
                band_text_style.append("-1")

            else:
                band_text_style.append("0")
        else:
            pass
    
    if len(numeros_puerta)>0:
        for n in numeros_puerta:
            if len(n.dxf.text)<15 and n.dxf.layer != "06-M-NUMERO-DE-PUERTA":
                band_num_layer.append("-1")
            else:
                band_num_layer.append("0")
    else:
        pass

    if len(m_manzana)>0:
        for element in m_manzana:
            if element.dxftype()== "LWPOLYLINE":
                band_ant_manzana.append("0")
                manzana_poly.append(element)
            else:
                band_ant_manzana.append("-1")
                if element.dxftype()== "TEXT":
                    band_ant_text.append("0")
    else:
        
            validaciones_model.loc[3,'Resultado']=-1
            validaciones_model.loc[3,'Observacion']="ERROR: Verifique que haya pegado con coordenadas originales los elementos del dxf de la manzana correspondiente en el layer 07-M-MANZANA"
            validaciones_model.loc[3,'Cetegoría']='Antecedente'

    if "0" in band_ant_manzana:
            validaciones_model.loc[3,'Resultado']=0
            validaciones_model.loc[3,'Observacion']="OK: El layer 07-M-MANZANA no se encuentra vacío"
            validaciones_model.loc[3,'Cetegoría']='Antecedente'  

    else:
        
        validaciones_model.loc[3,'Resultado']=-1
        validaciones_model.loc[3,'Observacion']="ERROR: Verifique que haya pegado con coordenadas originales los elementos del dxf de la manzana correspondiente en el layer 07-M-MANZANA"
        validaciones_model.loc[3,'Cetegoría']='Antecedente'


    if len(m_calles)>0:
        for element in m_calles:
            if element.dxftype()== "TEXT":
                band_calles_text.append("0")
            else:
                band_calles_text.append("-1")

        if "-1" in band_calles_text:
            validaciones_model.loc[4,'Resultado']=-1
            validaciones_model.loc[4,'Observacion']="ERROR:En el layer 05-M-NOMBRES-DE-CALLE deben indicarse los nombres de calle del DXF de la manzana correspondiente con entidad 'TEXT'"
            validaciones_model.loc[4,'Cetegoría']='Antecedente'

        else:
            validaciones_model.loc[4,'Resultado']=0
            validaciones_model.loc[4,'Observacion']="OK: En el layer 05-M-NOMBRES-DE-CALLE se encuentran indicadas solo entidades de 'TEXT'"
            validaciones_model.loc[4,'Cetegoría']='Antecedente'
                
    else:
        validaciones_model.loc[4,'Resultado']=-1
        validaciones_model.loc[4,'Observacion']="ERROR: El layer 05-M-NOMBRES-DE-CALLE está vacío, debe copiarse con coord. originales los elementos del DXF de la manzana correspondiente"
        validaciones_model.loc[4,'Cetegoría']='Antecedente'

    if "-1" in band_num_layer:
        validaciones_model.loc[5,'Resultado']=-1
        validaciones_model.loc[5,'Observacion']="ERROR: Existen N° de puerta en layer distinto a '06-M-NUMERO-DE-PUERTA'"
        validaciones_model.loc[5,'Cetegoría']='Antecedente'
    else:
        validaciones_model.loc[5,'Resultado']=0
        validaciones_model.loc[5,'Observacion']="Ok: Se indicaron los N° de puerta en el layer correspondiente"
        validaciones_model.loc[5,'Cetegoría']='Antecedente'

 
    #--- 2.5.2 INICIO Validación de Antecedentes--#
    #--- 2.5.3 INICIO Validación de Excedente--#
    excedentes = doc.modelspace().query('*[layer=="11-M-EXCEDENTE"]')#  Busca las polylineas en el layer EXCEDENTE

    band_poly_exc=list()   #lista de banderas para validar todas las entidades del layer excedente sean polilineas
    band_poly_cer_exc=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_exc=list()
    band_poly_color_exc=list()

    global excedentes_poly
    global excedentes_poly_close

    excedentes_poly = list()
    excedentes_poly_close = list()

    if len(excedentes): #si hay entindades en el layer patrcela comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for excedente in excedentes:
            if excedente.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline
                band_poly_exc.append('-1')
            else:
                band_poly_exc.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline

        if "-1" in band_poly_exc: # si hay un -1 en la bandera arroja error 
            validaciones_model.loc[6,'Resultado']=-1
            validaciones_model.loc[6,'Observacion']="ERROR: Existen entidades distintas de Polylineas en el Layer EXCEDENTE"
            validaciones_model.loc[6,'Cetegoría']='Parcela/s'  
        else:

            for excedente in excedentes:
                if excedente.dxftype()== "LWPOLYLINE":
                    if excedente.closed:
                        band_poly_cer_exc.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                        excedentes_poly_close.append(excedente)
                    else:
                        band_poly_cer_exc.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta
                else:
                    pass
                
            if '-1' in band_poly_cer_exc:
                    validaciones_model.loc[6,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                    validaciones_model.loc[6,'Observacion']="ERROR: Se dibujaron polylineas Abiertas en el layer EXCEDENTE"
                    validaciones_model.loc[6,'Cetegoría']='Parcela/s'
            else:
                validaciones_model.loc[6,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones_model.loc[6,'Observacion']="OK: Se dibujaron polylineas Cerradas en el layer EXCEDENTE"
                validaciones_model.loc[6,'Cetegoría']='Parcela/s'#si la polylinea es cerrada sigue validando que tengan el color y grosor bylayer

        #excedente.dxf.color==colores.at[0,'Excedente']:
        for excedente in excedentes: 
            if excedente.dxf.color==7:   
                band_poly_color_exc.append('0')
            else:
                band_poly_color_exc.append('-1')

            if excedente.dxf.lineweight==-3:
                        band_poly_gro_exc.append('0')
            else:
                band_poly_gro_exc.append('-1')

        if '0' in band_poly_color_exc and '0' in band_poly_gro_exc:
            validaciones_model.loc[7,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[7,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en el layer EXCEDENTE"
            validaciones_model.loc[7,'Cetegoría']='Parcela/s'
            
        elif '0' in band_poly_color_exc and '-1' in band_poly_gro_exc:
            validaciones_model.loc[7,'Resultado']=-5 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[7,'Observacion']="ERROR: Grosor de polylineas erroneo en layer EXCEDENTE"
            validaciones_model.loc[7,'Cetegoría']='Parcela/s'
            
        elif '-1' in band_poly_color_exc and '0' in band_poly_gro_exc:
            validaciones_model.loc[7,'Resultado']=-4 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[7,'Observacion']="ERROR: Color de polylineas erroneo en layer EXCEDENTE"
            validaciones_model.loc[7,'Cetegoría']='Parcela/s'
            
        elif '-1' in band_poly_color_exc and '-1' in band_poly_gro_exc:
            validaciones_model.loc[7,'Resultado']=-3 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[7,'Observacion']="ERROR: Color y grosor de polylineas erroneo en layer EXCEDENTE"
            validaciones_model.loc[7,'Cetegoría']='Parcela/s'
        ## INICIO VERIFICACIÓN EXCEDENTE ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.

        excedentes_poly= excedentes.query('LWPOLYLINE')
        parcelas_poly= parcelas.query('LWPOLYLINE')
        band_exc_dentro=list() #inicia bandera de control si cada uno de los excedentes estan dentro de una parcela
        for excedente in excedentes_poly: #reccorre poligonos de excedentes
            vertices_e1 = excedente.get_points('xy') #para cada excedente obtiene los vertices y los prepara para la función de control
            vertices_e2 = Vec2.list(vertices_e1)
            band_parc_dentro=list() #bandera que controla si el excedente x esta dentro de laguna de las parcelas
            for parcela in parcelas_poly: #fijado un excedente reccorre poligonos de parcelas para comparar vertices
                #Para que la funcion offset no tire error por vectores nulos al haber vertices repetidos se recorre la polilinea y solo se guardan en la lista vertices_p1 si ya esta repetido
                # vert_unicos_parc = set()
                # vertices_p1 = list()
                # for vert in parcela.vertices():
                #     if vert in vertices_p1:
                #         pass
                #     else:
                #         vertices_p1.append(vert)
                # #vertices_p1 = parcela.get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control
                # vertices_p2 = Vec2.list(vertices_p1)
                # vertices_p3 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=-0.01, closed=True))
                # vertices_p4 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=0.01, closed=True))
                # band_vert_dentro=list() #inicia bandera que valida si los vertices del excedente caen dentro de el polig. de parcela

                # for i in range (0,len(vertices_e2)): 
                    
                #     if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p3,abs_tol=1e-3)==-1: #validación de vertices arroja -1 si cae fuera, 0 si cae en los limites y 1 si cae dentro
                #         if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p4,abs_tol=1e-3)==-1:
                #             band_vert_dentro.append('-1')
                #         else:
                #             band_vert_dentro.append('0')
                #     else:
                #         band_vert_dentro.append('0')

                if polig_dentro_polig(parcela, excedente, 0.01):
                    band_parc_dentro.append('0')
                else:
                    band_parc_dentro.append('-1')
                
                # if '-1' in band_vert_dentro:
                #     band_parc_dentro.append('-1')
                # else:
                #     band_parc_dentro.append('0')
                # del band_vert_dentro
                    
            if '0' in band_parc_dentro:
                band_exc_dentro.append('0')
                
            else:
                band_exc_dentro.append('-1')

            del band_parc_dentro

        if '-1' in band_exc_dentro:
            validaciones_model.loc[8,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color blayer
            validaciones_model.loc[8,'Observacion']="ERROR: Existe al menos un excedente fuera de la o las Parcelas mensuradas"
            validaciones_model.loc[8,'Cetegoría']='Parcela/s'
        else:
            validaciones_model.loc[8,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones_model.loc[8,'Observacion']="OK: El o los excedentes se encuentran completamente dentro de la/las Parcelas Mensuradas"
            validaciones_model.loc[8,'Cetegoría']='Parcela/s'

            ## FIN VERIFICACIÓN EXCEDENTE ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.
    else:
        
        validaciones_model.loc[6,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[6,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones_model.loc[6,'Cetegoría']='Parcela/s'

        validaciones_model.loc[7,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[7,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones_model.loc[7,'Cetegoría']='Parcela/s'

        validaciones_model.loc[8,'Resultado']=99 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
        validaciones_model.loc[8,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones_model.loc[8,'Cetegoría']='Parcela/s'
     
    #--- 2.5.2 FIN Validación de Excedente --#

    #--- 2.5.3 INICIO Validación de Bloque NOmenclatura Parcela --#

    #Validar que se encuentre inserto y completo el bloque "PARCELA_VIGENTE" tantas veces como poligonos cerrados de parcela haya. 

    bloque_PARCELA_SURGENTE = doc.modelspace().query('INSERT[name=="PARCELA_SURGENTE"]')
    patron_parc = re.compile('(^([0-9]{3})|([0-9]{3}[a-z]{1})|([0-9]{3}[ñ]{1})|([0-9]{2}[l]{2})|(000[A-Z]{1}))$') #patron para validar el formato de la parcela escrito en el bloque mensura
    nom_parc_list=list()
    
    #valida que haya la misma cantidad de bloques de parcela insertos en el dxf que la cantidad de parcelas del layer parcelas.    

    if len(bloque_PARCELA_SURGENTE)==1:
            validaciones_model.loc[9,'Resultado']=0
            validaciones_model.loc[9,'Observacion']='OK: Exite inserto un unico bloque "PARCELA_SURGENTE"'
            validaciones_model.loc[9,'Cetegoría']='Bloques'

            ban_bparc_comp=list()
            band_nom_parc = list()
                
            for bloque in (bloque_PARCELA_SURGENTE):
                    for attrib in bloque.attribs:
                        if attrib.dxf.tag=="NPARC":

                            if attrib.dxf.text == None:
                                ban_bparc_comp.append(-1)
                                nom_parc_list.append("0")
                            else:
                                ban_bparc_comp.append(0)
                                nom_parc_list.append(attrib.dxf.text)
                        else:
                            ban_bparc_comp.append(-2)
                            nom_parc_list.append("0")

                    if -1 in ban_bparc_comp:
                        validaciones_model.loc[10,'Resultado']=-1
                        validaciones_model.loc[10,'Observacion']='ERROR: El o los bloques "PARCELA_SURGENTE" estan vacíos'
                        validaciones_model.loc[10,'Cetegoría']='Bloques' 
                    elif -2 in ban_bparc_comp:
                        validaciones_model.loc[10,'Resultado']=-1
                        validaciones_model.loc[10,'Observacion']='ERROR: Se modificó el bloque PARCELA_SURGENTE, utilice el de la plantilla.'
                        validaciones_model.loc[10,'Cetegoría']='Bloques' 

                    else:
                            #validar que la nomenclatura del bloque Parc_vig tegnga elformato correcto 000a#

                        for i in nom_parc_list:
                            band_nom_parc.append(patron_parc.match(i))                                            
                    
                        if None in band_nom_parc:
                            validaciones_model.loc[10,'Resultado']=-1
                            validaciones_model.loc[10,'Observacion']='ERROR: La nomenclatura indicada en el de los bloque "PARCELA_SURGENTE" no respeta el formato 000a'
                            validaciones_model.loc[10,'Cetegoría']='Bloques'
                        else:
                            validaciones_model.loc[10,'Resultado']=0
                            validaciones_model.loc[10,'Observacion']='OK: La nomenclatura indicada el bloque "PARCELA_SURGENTE" respeta el formato 000a'
                            validaciones_model.loc[10,'Cetegoría']='Bloques'

    elif len(bloque_PARCELA_SURGENTE)>1:
            validaciones_model.loc[9,'Resultado']=-2
            validaciones_model.loc[9,'Observacion']='ERROR: Exite más de un boque "PARCELA_SURGENTE" inserto'
            validaciones_model.loc[9,'Cetegoría']='Bloques'

            validaciones_model.loc[10,'Resultado']=-1
            validaciones_model.loc[10,'Observacion']='ERROR: Exite más de un boque "PARCELA_SURGENTE" inserto'
            validaciones_model.loc[10,'Cetegoría']='Bloques'

            nom_parc_list.append("0")

    elif len(bloque_PARCELA_SURGENTE)==0:
            validaciones_model.loc[9,'Resultado']=-1
            validaciones_model.loc[9,'Observacion']='ERROR: No se ha insertado el bloque "PARCELA_SURGENTE"'
            validaciones_model.loc[9,'Cetegoría']='Bloques'

            validaciones_model.loc[10,'Resultado']=-1
            validaciones_model.loc[10,'Observacion']='ERROR: No se ha insertado el bloque "PARCELA_SURGENTE"'
            validaciones_model.loc[10,'Cetegoría']='Bloques'

            nom_parc_list.append("0")
 #valida que haya la misma cantidad de bloques de parcela insertos en el dxf que la cantidad de parcelas del layer parcelas

        #Validar que el bloque de nomenclatura este en el model y adentro de una parcela#   

    else:
        validaciones_model.loc[9,'Resultado']=-1
        validaciones_model.loc[9,'Observacion']='Error: No se encuentra inserto el bloque "PARCELA_SURGENTE" por cada una de las parcelas que surgen o se mantienen vigentes con este plano'
        validaciones_model.loc[9,'Cetegoría']='Bloques'

        validaciones_model.loc[10,'Resultado']=99
        validaciones_model.loc[10,'Observacion']='ERROR: No se puede validar el bloque "PARCELA_SURGENTE" dado que no se encuentra inserto'
        validaciones_model.loc[10,'Cetegoría']='Bloques'

            
    #--- 2.5.3 FIN Validación de Bloque Nomenclatura Parcela --#  


    #--- 2.5.4 INICIO Validación de MEJORAS--#
    global mejoras_poly

    global forms
    global forms_empadronados
    global forms_descubiertos
    global forms_vacios
    global layers_mejoras
    global layers_mejoras_1

    global piso_con_mejoras
    global band_form_polig

    global info_form_nuevo
    global info_form_emp
    global info_form_sin_info
    global info_form_desc
    global info_form_vacio
    global info_form_muchos_form

    global sup_cub_dxf
    global sup_semicub_dxf
    global sup_descub_dxf
    global sup_descont_dxf
    global sup_pileta_dxf
    global sup_invasion_dxf
    global mejora_piso

    global band_mejora_cub_arc_0
    global band_mejora_semi_arc_0
    global band_mejora_desc_arc_0
    global band_mejora_emp_arc_0
    global band_mejora_nueva_arc_0
    
    info_form_nuevo = list()
    info_form_emp = list()
    info_form_sin_info = list()
    info_form_desc = list()
    info_form_vacio = list()
    info_form_muchos_form = list()
    #info_form = list()
    mejoras = doc.modelspace().query('*[layer ? ".*-SUP"]') #  Busca las polylineas en los layers que finalizan con -SUP
    band_poly_mej=list()   #lista de banderas para validar todas las entidades del layer excedente sean polilineas
    band_poly_cer_mej=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_mej=list()
    band_poly_color_mej=list()
    forms = list()
    forms_empadronados = list()
    forms_descubiertos = list()
    forms_vacios = list()
    mejoras_poly = list()
    layers_mejoras_0 = list()
    layers_mejoras_1 = list()
    layers_mejoras = list()
    band_mej_form_piso = list() #bandera que captura la validacion de cntidad de polilineas y formularios por piso
    piso_con_mejoras_0 = list()
    piso_con_mejoras = list()
    patron_polig = re.compile('^[0-9]*$')
    band_letra_form = list()
    band_form_polig = list()
    mejora_piso = list()
    mejora_piso_0 = list()

    forms_polig = list()
    forms_polig_sorted = list()
    forms_N_forms =list()
    forms_T_forms =list()
    band_T_forms = list()
    band_N_forms = list()
    band_1_polig = list() #bandera que guarda si el primer numero d elos poligonos es 1
    band_correl_polig = list() #bandera que guarda si los valores de numero d epoligonos son correlativos
    band_correl_polig_2 = list() #bandera que guarda lo mismo que la nterior pero sin el primer valor
    #patron_polig = re.compile('^[0-9]*$')
    #band_letra_form = list()
    sup_cub_dxf = list()
    sup_semicub_dxf = list()
    sup_descub_dxf = list()
    sup_descont_dxf = list()
    sup_pileta_dxf = list()
    sup_invasion_dxf = list()

    for layer in nom_layers_dxf:  #recorre todos los layers del dxf y si tiene la leyenda -sup en el nombre lo guarda en una lista d enombres de layers de superficie
        if "-SUP" in layer:
            layers_mejoras_0.append(layer)
            if "M-M-PB-SUP" in layer:
                pass
            else:
                layers_mejoras_1.append(layer)
        else:
            pass

    layers_mejoras = list(set(layers_mejoras_0)) #Arma una lista de valores unicos con los nombres de los layers de superficie

    layers_mejoras_spb = list(set(layers_mejoras_1)) #Arma una lista de valores unicos con los nombres de los layers de superficie sin el de planta baja
    
    #inicializacion de banderas para determinar si los distintos tipos de superficies tienen arco
    band_mejora_cub_arc_0 = list()
    band_mejora_semi_arc_0 = list()
    band_mejora_desc_arc_0 = list()
    band_mejora_emp_arc_0 = list()
    band_mejora_nueva_arc_0 = list()
    band_mejora_vacio_arc_0 = list()
    
    for layer in layers_mejoras: #recorre cada piso
        consulta = f'layer=="{layer}"'
        mejora_piso_0 = doc.modelspace().query(f'LWPOLYLINE[{consulta}]') #renombrar por mejora_piso_0
        form_piso = doc.modelspace().query(f'INSERT[{consulta}]')
        mejora_piso = list()
        for mejora in mejora_piso_0:
            if mejora.closed:
                mejora_piso.append(mejora)
            else:
                pass

        if len(mejora_piso)>0:
            piso_con_mejoras_0.append(layer)
        else:
            pass

        band_mejora_arc = list()
        #codigo para verificar que un form este inserto dentro de un poligono

        band_form_dentro = list()
    
        # form_piso_sueltos = form_piso[:]

        for i in range (len(mejora_piso)): #recorre cada poligono dentro del piso
            form_dentro_mejora = list()
            form_dentro_mejora_2 = list()
            form_dentro_mejora_3 = list()
            mejora_piso_comp = mejora_piso[:]
            mejora_piso_comp.pop(i)
            vert_pol_madre = list()
            vert_pol_agujero = list()
            vert_pol_madre_unico = list()
            vert_pol_agujero_unico = list()

            vertices_mp0 = mejora_piso[i].get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
            vertices_mp1 = Vec2.list(vertices_mp0)
            # vertices_mp12 = list(ezdxf.math.offset_vertices_2d(vertices_mp1,offset=-0.01, closed=True))
            # vertices_mp13 = list(ezdxf.math.offset_vertices_2d(vertices_mp1,offset=0.01, closed=True))

            mejora_adentro_2 =list ()
            band_mej_mej_dentro_2 = list()

            band_mejora_arc = list()
            band_mejora_adentro_arc = list()

            # Inicio Calcula la superficie del poligono de la mejora dependiendo si tiene arco o no
            sup_mejora_0 = round(sup_polilinea(mejora_piso[i]),2)

            if mejora_piso[i].has_arc:
                band_mejora_arc.append("1")

            
            # FIN Calcula la superficie del poligono de la mejora dependiendo si tiene arco o no

            # INICIO detecta las mejoras que se encuentran dibujadas dentro de la mejora madre
            
            for mejora in mejora_piso_comp:
        
                if polig_dentro_polig(mejora_piso[i],mejora,0.01):
                    band_mej_mej_dentro_2.append("0")
                    mejora_adentro_2.append(mejora)
                else:
                    band_mej_mej_dentro_2.append("-1")
            
            # FIN detecta las mejoras que se encuentran dibujadas dentro de la mejora madre


            # INICIO Calcula la superficie de las mejoras Hijas dependiendo si tienen arco o no
            # Además de los formularios dentro de la mejora madre detecta los que estan en las hijas, para identificar cual es el formulario de la mejora madre

            
            if len(mejora_adentro_2)>0:
                #genera poligono de mejora madre
                    
                for lado in mejora_piso[i].virtual_entities():  
                    
                    if lado.dxftype() == "ARC":
                        arco_discretizado = discretizar_curva(lado,0.01)
                        #dar vuelta el arco para que coincida con los vertices

                        if len(vert_pol_madre):

                            if vert_pol_madre[-1] == arco_discretizado[0]:
                                
                                vert_pol_madre = vert_pol_madre + arco_discretizado
                                
                            elif vert_pol_madre[-1] == arco_discretizado[-1]:
                                
                                vert_pol_madre = vert_pol_madre + list(reversed(arco_discretizado))
                            else:
                                if vert_pol_madre[0] == arco_discretizado[0]:
                                
                                    vert_pol_madre = list(reversed(vert_pol_madre)) + arco_discretizado
                                    
                                elif vert_pol_madre[0] == arco_discretizado[-1]:
                                    vert_pol_madre = list(reversed(vert_pol_madre)) + list(reversed(arco_discretizado))
                                
                                else:
                                    pass
                        else:
                            vert_pol_madre = vert_pol_madre + arco_discretizado

                    else:
                        lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]

                        if len(vert_pol_madre):

                            if vert_pol_madre[-1] == lado_recto[0]:
                                
                                vert_pol_madre = vert_pol_madre + lado_recto
                                
                            elif vert_pol_madre[-1] == lado_recto[-1]:
                                
                                vert_pol_madre = vert_pol_madre + list(reversed(lado_recto))
                            else:
                                if vert_pol_madre[0] == lado_recto[0]:
                                
                                    vert_pol_madre = list(reversed(vert_pol_madre)) + lado_recto
                                    
                                elif vert_pol_madre[0] == lado_recto[-1]:
                                    vert_pol_madre = list(reversed(vert_pol_madre)) + list(reversed(lado_recto))
                                
                                else:
                                    pass

                        else:

                            vert_pol_madre = vert_pol_madre + lado_recto
                
                for lado in mejora_adentro_2[0].virtual_entities():

                    if lado.dxftype() == "ARC":
                        arco_discretizado = discretizar_curva(lado,0.01)
                        #dar vuelta el arco para que coincida con los vertices
                        
                        if len(vert_pol_agujero):

                            if vert_pol_agujero[-1] == arco_discretizado[0]:
                                
                                vert_pol_agujero = vert_pol_agujero + arco_discretizado
                            elif vert_pol_agujero[-1] == arco_discretizado[-1]:
                                
                                vert_pol_agujero = vert_pol_agujero + list(reversed(arco_discretizado))
                            else:
                                if vert_pol_agujero[0] == arco_discretizado[0]:
                                    vert_pol_agujero = list(reversed(vert_pol_agujero)) + arco_discretizado

                                elif vert_pol_agujero[0] == arco_discretizado[-1]:
                                    vert_pol_agujero = list(reversed(vert_pol_agujero)) + list(reversed(arco_discretizado))

                                else:
                                    pass
                        else:
                            vert_pol_agujero = vert_pol_agujero + arco_discretizado

                    else:
                    
                        lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]

                        if len(vert_pol_agujero):
                         
                            if vert_pol_agujero[-1] == lado_recto[0]:
                                
                                vert_pol_agujero = vert_pol_agujero + lado_recto
                            

                            #vert_pol_agujero[-1]
                            elif vert_pol_agujero[-1] == lado_recto[-1]:
                                
                                vert_pol_agujero = vert_pol_agujero + list(reversed(lado_recto))
                            else: #comparar si vert_mejora_pol[0] == lado_recto[0]
                                if vert_pol_agujero[0] == lado_recto[0]:
                                    vert_pol_agujero = list(reversed(vert_pol_agujero)) + lado_recto
                                elif vert_pol_agujero[0] == lado_recto[-1]:
                                    vert_pol_agujero = list(reversed(vert_pol_agujero)) + list(reversed(lado_recto))
                                else:
                                    pass

                        else:

                            vert_pol_agujero = vert_pol_agujero + lado_recto

                        
                        


                
                
                poligono_madre = Polygon(vert_pol_madre)
                poligono_agujero = Polygon(vert_pol_agujero)
                
                 #genera poligono de mejora hija 1 para iniciar la union de mejoras hijas para luego restar a la madre

                for mejora in mejora_adentro_2:
                    vert_mejora_pol = list()

                    #va uniendo los poligonos de las mejoras hijas
                    for lado in mejora.virtual_entities():

                        if lado.dxftype() == "ARC":
                            arco_discretizado = discretizar_curva(lado,0.01)
                            #dar vuelta el arco para que coincida con los vertices

                            #vert_pol_agujero
                            if len(vert_mejora_pol):

                                #vert_pol_agujero[-1]
                                if vert_mejora_pol[-1] == arco_discretizado[0]:
                                    
                                    vert_mejora_pol = vert_mejora_pol + arco_discretizado
                                

                                #vert_pol_agujero[-1]
                                elif vert_mejora_pol[-1] == arco_discretizado[-1]:
                                    
                                    vert_mejora_pol = vert_mejora_pol + list(reversed(arco_discretizado))
                                else:
                                    if vert_mejora_pol[0] == arco_discretizado[0]:
                                        vert_mejora_pol = list(reversed(vert_mejora_pol)) + arco_discretizado
                                        
                                    elif vert_mejora_pol[0] == arco_discretizado[-1]:
                                        vert_mejora_pol = list(reversed(vert_mejora_pol)) + list(reversed(arco_discretizado))
                                        
                                    else:
                                        pass
                                    
                            else:
                                vert_mejora_pol = vert_mejora_pol + arco_discretizado

                        else:
                           

                            lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]


                            if len(vert_mejora_pol):
                            
                                if vert_mejora_pol[-1] == lado_recto[0]:
                                    
                                    vert_mejora_pol = vert_mejora_pol + lado_recto
                                

                                #vert_pol_agujero[-1]
                                elif vert_mejora_pol[-1] == lado_recto[-1]:
                                    
                                    vert_mejora_pol = vert_mejora_pol + list(reversed(lado_recto))
                                else: #comparar si vert_mejora_pol[0] == lado_recto[0]
                                    if vert_mejora_pol[0] == lado_recto[0]:
                                        vert_mejora_pol = list(reversed(vert_mejora_pol)) + lado_recto
                                    elif vert_mejora_pol[0] == lado_recto[-1]:
                                        vert_mejora_pol = list(reversed(vert_mejora_pol)) + list(reversed(lado_recto))
                                    else:
                                        pass

                            else:
                            #lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]

                                vert_mejora_pol = vert_mejora_pol + lado_recto

                    mejora_poligon = Polygon(vert_mejora_pol)

                    # mejora_poligon = Polygon(list(mejora.get_points('xy')))
                    poligono_agujero = union(poligono_agujero,mejora_poligon)

                    
                    if mejora.has_arc:
                        band_mejora_adentro_arc.append("1")

                #resta a la mejora madre el agujero de las mejoras hijas
                poligono_diference = difference(poligono_madre,poligono_agujero)
                sup_mejora_descont_2 = area(poligono_diference) #calcula superficie del poligono despues de todas las restas

                    
                for form in form_piso: #detecta todos los formularios que caen dentro del poligono de mejora madre
                    vertice_k = Vec2(form.dxf.insert.x,form.dxf.insert.y)
                    if ezdxf.math.is_point_in_polygon_2d(vertice_k,vertices_mp1,abs_tol=1e-3)==-1:
                        pass
                    else:
                        form_dentro_mejora_2.append(form)
                
                if len(form_dentro_mejora_2)>0:
                    for form1 in form_dentro_mejora_2:
                        band_form_polig_dentro = list()
                        vertice_f = Vec2(form1.dxf.insert.x,form1.dxf.insert.y)
                        for mejora in mejora_adentro_2:
                            vertices_md0 = mejora.get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
                            vertices_md1 = Vec2.list(vertices_md0)

                            if ezdxf.math.is_point_in_polygon_2d(vertice_f,vertices_md1,abs_tol=1e-3)==-1:
                                if ezdxf.math.is_point_in_polygon_2d(vertice_f,vertices_md1,abs_tol=1e-3)==-1:
                                    band_form_polig_dentro.append("0")
                                else:
                                    band_form_polig_dentro.append("-1")
                            else:
                                band_form_polig_dentro.append("0")
                        
                        if "-1" in band_form_polig_dentro:
                            pass
                        else:
                            form_dentro_mejora_3.append(form1) #formularios que caen fuera de todas las mejoras hijas pero dentro de la madre

                    if len(form_dentro_mejora_3) == 1:
                        if form_dentro_mejora_3[0].dxf.name == "form":
                            for attrib in form_dentro_mejora_3[0].attribs:
                                if attrib.dxf.tag=="Nº_POLIG.":
                                    if len(attrib.dxf.text)==0:
                                        band_form_polig.append('-1')
                                    else:
                                        band_form_polig.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_polig = (int(attrib.dxf.text))
                                        else:
                                            pass
                        
                                elif attrib.dxf.tag=="TIPO_FORM":
                                    if len(attrib.dxf.text)==0:
                                        band_T_forms.append('-1')
                                    else:
                                        band_T_forms.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_tipo = (int(attrib.dxf.text))
                                        else:
                                            pass
                    
                                elif attrib.dxf.tag=="Nº_FORM":
                                    if len(attrib.dxf.text)==0:
                                        band_N_forms.append('-1')
                                    else:
                                        band_N_forms.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_numero = (int(attrib.dxf.text))
                                        else:
                                            pass
                                else:
                                    form_tipo = 0
                                    form_numero = 0
                                    form_polig = 0

                            info_form_nuevo.append({"form":f"{form_tipo}/{form_numero}","polig":f"{form_polig}","sup":f"{sup_mejora_descont_2}"})
                            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                band_mejora_nueva_arc_0.append("1")
                            else:
                                pass
                        elif form_dentro_mejora_3[0].dxf.name == "form_empadronado":
                            info_form_emp.append(sup_mejora_descont_2)
                            if  len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                band_mejora_emp_arc_0.append("1")
                            else:
                                pass
                        
                        elif form_dentro_mejora_3[0].dxf.name == "form_descubierto":
                            info_form_desc.append(sup_mejora_descont_2)


                        elif form_dentro_mejora_3[0].dxf.name == "form_vacio":
                            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                info_form_vacio.append(sup_mejora_descont_2)
                                band_mejora_vacio_arc_0.append("1")
                            else:
                                pass
                        else:
                            pass
                    
                    elif len(form_dentro_mejora_3) == 0:
                        info_form_sin_info.append(sup_mejora_descont_2)
                    
                    else:
                        info_form_muchos_form.append(sup_mejora_descont_2)
                else:
                    pass

            else:
                sup_mejora_descont_2 = sup_mejora_0
                
                for form in form_piso:
                    vertice_i = Vec2(form.dxf.insert.x,form.dxf.insert.y)
                    for attrib in form.attribs:
                        if attrib.dxf.tag=="Nº_POLIG.":
                            if len(attrib.dxf.text)==0:
                                band_form_polig.append('-1')
                            else:
                                band_form_polig.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_polig = (int(attrib.dxf.text))
                                else:
                                    pass
                
                        elif attrib.dxf.tag=="TIPO_FORM":
                            if len(attrib.dxf.text)==0:
                                band_T_forms.append('-1')
                            else:
                                band_T_forms.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_tipo = (int(attrib.dxf.text))
                                else:
                                    pass
            
                        elif attrib.dxf.tag=="Nº_FORM":
                            if len(attrib.dxf.text)==0:
                                band_N_forms.append('-1')
                            else:
                                band_N_forms.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_numero = (int(attrib.dxf.text))
                                else:
                                    pass
                        else:
                            form_tipo = 0
                            form_numero = 0
                            form_polig = 0

                    if ezdxf.math.is_point_in_polygon_2d(vertice_i,vertices_mp1,abs_tol=1e-3)==-1:
                        pass
                    else:
                        form_dentro_mejora.append(form)
                
                if len(form_dentro_mejora) == 1:
                    if form_dentro_mejora[0].dxf.name == "form":
                        info_form_nuevo.append({"form":f"{form_tipo}/{form_numero}","polig":f"{form_polig}","sup":f"{sup_mejora_descont_2}"})
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_nueva_arc_0.append("1") #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)
                        else:
                            pass
                    elif form_dentro_mejora[0].dxf.name == "form_empadronado":
                        info_form_emp.append(sup_mejora_descont_2)
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_emp_arc_0.append("1") #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)
                        else:
                            pass
                             #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)

                    elif form_dentro_mejora[0].dxf.name == "form_descubierto":
                        info_form_desc.append(sup_mejora_descont_2)

                    elif form_dentro_mejora[0].dxf.name == "form_vacio":
                        info_form_vacio.append(sup_mejora_descont_2)
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_vacio_arc_0.append("1")
                        else:
                            pass
                    else:
                        pass
                elif len(form_dentro_mejora) == 0:
                    info_form_sin_info.append(sup_mejora_descont_2)

                else:
                    info_form_muchos_form.append(sup_mejora_descont_2)

            #sup_mejora_descont_2 = round(ezdxf.math.area(Vec2.list(mejora_piso[i].get_points('xy'))),2) - sup_mejora_dentro_2

            if mejora_piso[i].dxf.color==1 or mejora_piso[i].dxf.color==216:
                sup_cub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==2 or mejora_piso[i].dxf.color==4:
                sup_semicub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==3 or mejora_piso[i].dxf.color==5:
                sup_descub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==32:
                sup_descont_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==150:
                sup_pileta_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==155:
                sup_invasion_dxf.append(sup_mejora_descont_2)
            else:
                pass

            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                if mejora_piso[i].dxf.color==1 or mejora_piso[i].dxf.color==216:
                    band_mejora_cub_arc_0.append("1")
                elif mejora_piso[i].dxf.color==2 or mejora_piso[i].dxf.color==4:
                    band_mejora_semi_arc_0.append("1")
                elif mejora_piso[i].dxf.color==3 or mejora_piso[i].dxf.color==5:
                    band_mejora_desc_arc_0.append("1")
                elif mejora_piso[i].dxf.color==32:
                    band_mejora_vacio_arc_0.append("1")
                else:
                    pass
            else:
                pass
        
    if '-1' in band_form_dentro:
        validaciones_model.loc[11,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_model.loc[11,'Observacion']="Error: Algun bloque de formulario no se encuentra inserto dentro del poligono de superficie al que pertenece"
        validaciones_model.loc[11,'Cetegoría']='Mejoras'
        
        
    else:
        validaciones_model.loc[11,'Resultado']=0 
        validaciones_model.loc[11,'Observacion']="Ok: Los bloques de formularios se encuentran insertos dentro de los poligono de superficie a los que pertenecen"
        validaciones_model.loc[11,'Cetegoría']='Mejoras'
        
    del band_form_dentro

    if len(mejora_piso)==len(form_piso): #evalua por piso que haya la misma cantidad de polilineas de mejoras que bloques de fomrularios
        band_mej_form_piso.append("0")
    else:
        band_mej_form_piso.append("-1")

    piso_con_mejoras = list(set(piso_con_mejoras_0))

    if "-1" in band_mej_form_piso:
        validaciones_model.loc[12,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_model.loc[12,'Observacion']="Error: En alguno de los pisos difiere la cantidad de polilineas cerradas que bloques de formulario insertos"
        validaciones_model.loc[12,'Cetegoría']='Mejoras'
        
    else:
        validaciones_model.loc[12,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones_model.loc[12,'Observacion']="Ok: En todos los pisos existe la misma cantidad de polilineas cerradas de superficies que bloques de formulario insertos"
        validaciones_model.loc[12,'Cetegoría']='Mejoras'

    patron_layer_sup = re.compile('^M-M-((PB-SUP)|([0-9]{2}(E|P|S)-SUP))$')

    band_layer_sup = list()

    for layer in layers_mejoras:

        if (patron_layer_sup.match(layer)):
            band_layer_sup.append('0')
        else:
            band_layer_sup.append('-1')

    if "-1" in band_layer_sup:
        validaciones_model.loc[13,'Resultado']=-1
        validaciones_model.loc[13,'Observacion']="Error: Alguno de los Layers de Superficies no se ha creado con el nombre correcto"
        validaciones_model.loc[13,'Cetegoría']='Mejoras'
    else:
        validaciones_model.loc[13,'Resultado']=0
        validaciones_model.loc[13,'Observacion']="Ok: Los layers de superficies poseen el formato correcto en el nombre"
        validaciones_model.loc[13,'Cetegoría']='Mejoras'
        
    if len(mejoras): #si hay entindades en el layer mejoras comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for mejora in mejoras:
            if mejora.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline

                if mejora.dxftype()!= "INSERT":
                    band_poly_mej.append('-1')
                    
                else:
                    if mejora.dxf.name == "form":
                        band_poly_mej.append('0')
                        forms.append(mejora)
                        
                    elif mejora.dxf.name == "form_empadronado":
                        band_poly_mej.append('0')
                        forms_empadronados.append(mejora)

                    elif mejora.dxf.name == "form_descubierto":
                        band_poly_mej.append('0')
                        forms_descubiertos.append(mejora)
                    
                    elif mejora.dxf.name == "form_vacio":
                        band_poly_mej.append('0')
                        forms_vacios.append(mejora)
                        
                    elif mejora.dxf.name != "form" or mejora.dxf.name != "form_empadronado" or mejora.dxf.name != "form_descubierto" or mejora.dxf.name != "form_vacio":
                        band_poly_mej.append('-2')

            else:
                band_poly_mej.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline
                mejoras_poly.append(mejora)

        if "-1" in band_poly_mej or "-2" in band_poly_mej: # si hay un -1 en la bandera arroja error 
            validaciones_model.loc[14,'Resultado']=-1
            validaciones_model.loc[14,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones_model.loc[14,'Cetegoría']='Mejoras'

            validaciones_model.loc[15,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[15,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de  "-SUP"'
            validaciones_model.loc[15,'Cetegoría']='Mejoras'

            validaciones_model.loc[16,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[16,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones_model.loc[16,'Cetegoría']='Mejoras'

            validaciones_model.loc[17,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[17,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones_model.loc[17,'Cetegoría']='Mejoras'
            
            resultado_inv = "ok"
        else:           
                
            for mejora in mejoras_poly:
                if mejora.closed:
                    band_poly_cer_mej.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                    
                else:
                    band_poly_cer_mej.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta
            
            if '-1' in band_poly_cer_mej:
                validaciones_model.loc[14,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[14,'Observacion']="Error: Se dibujaron polylineas Abiertas en alguno de los layers de '-SUP', deben ser Cerradas"
                validaciones_model.loc[14,'Cetegoría']='Mejoras'
            else:
                validaciones_model.loc[14,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones_model.loc[14,'Observacion']="OK: Se dibujaron polylineas Cerradas en los layers de '-SUP'"
                validaciones_model.loc[14,'Cetegoría']='Mejoras'

                #si la polylinea es cerrada sigue validando que tengan el color y grosor bylayer                    
            for mejora in mejoras_poly:
                if mejora.dxf.color == 1 or mejora.dxf.color == 2 or mejora.dxf.color == 3 or mejora.dxf.color == 4 or mejora.dxf.color == 5 or mejora.dxf.color == 32 or mejora.dxf.color == 150 or mejora.dxf.color == 155 or mejora.dxf.color == 216 or mejora.dxf.color == 200:   
                    band_poly_color_mej.append('0')
                else:
                    band_poly_color_mej.append('-1')

                if mejora.dxf.lineweight==-3:
                    band_poly_gro_mej.append('0')
                else:
                    band_poly_gro_mej.append('-1')

            if '-1' in band_poly_color_mej:
                validaciones_model.loc[15,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones_model.loc[15,'Observacion']="Error: Color de polylineas erroneo en los layers de '-SUP' (colores admitidos rojo, amarillo, verde, cian, azul)"
                validaciones_model.loc[15,'Cetegoría']='Mejoras'
            
            else:
                validaciones_model.loc[15,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones_model.loc[15,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en los layers de '-SUP'"
                validaciones_model.loc[15,'Cetegoría']='Mejoras'
                

            if len(mejoras_poly) == (len(forms) + len(forms_empadronados) + len(forms_descubiertos) + len(forms_vacios)):
                validaciones_model.loc[16,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones_model.loc[16,'Observacion']="OK: Coinciden la cantidad de polilineas cerradas con la de bloques de formularios"
                validaciones_model.loc[16,'Cetegoría']='Mejoras'

            else:
                validaciones_model.loc[16,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones_model.loc[16,'Observacion']="ERROR: No Coinciden la cantidad de polilineas cerradas con la de bloques de formularios (form / form_emparonado / form_descubierto)"
                validaciones_model.loc[16,'Cetegoría']='Mejoras'
                
                        
            ## INICIO VERIFICACIÓN MEJORA ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.

            
            mejoras_poly= mejoras.query('LWPOLYLINE')
            parcelas_poly= parcelas.query('LWPOLYLINE')
            band_mej_dentro=list() #inicia bandera de control si cada uno de las mejoras estan dentro de una parcela
            band_inv_publica = list()
            band_inv_lind = list()

            
            #que la mejora que consulte en la funcion invasiones, sea una mejora de PB o de un subsuelo
            

            mejoras_poly_PB_SUB = []

            for layer in layers_mejoras: #recorre cada piso
                if layer == "M-M-PB-SUP" or "S-SUP" in layer:
                    consulta = f'layer=="{layer}"'
                    mejora_consultada =  doc.modelspace().query(f'LWPOLYLINE[{consulta}]')
                    for mejora in mejora_consultada:
                        mejoras_poly_PB_SUB.append(mejora)
                else:
                    pass
            if len(mejoras_poly_PB_SUB)>0:
            
                for mejora in mejoras_poly_PB_SUB: #reccorre poligonos de mejoras

                    if len(manzana_poly)>0:

                        resultado_inv  = invasiones(manzana_poly[0], parcelas_poly[0], mejora ,0.01)
                    else:
                        resultado_inv = "ok"
            else:
                resultado_inv = "ok"

            ## FIN VERIFICACIÓN MEJORA ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.
    else:

        validaciones_model.loc[14,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[14,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"
        validaciones_model.loc[14,'Cetegoría']='Mejoras'

        validaciones_model.loc[15,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[15,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"        
        validaciones_model.loc[15,'Cetegoría']='Mejoras'

        validaciones_model.loc[16,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[16,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"
        validaciones_model.loc[16,'Cetegoría']='Mejoras'

        validaciones_model.loc[17,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[17,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"        
        validaciones_model.loc[17,'Cetegoría']='Mejoras'

        resultado_inv = "ok"

    #--- 2.5.4.1 INICIO Validación de Bloque Formularios--#

    if (len(forms)>0 or len(forms_empadronados)>0):
        
        for form in forms:
            for attrib in form.attribs:
                if attrib.dxf.tag=="Nº_POLIG.":
                    if len(attrib.dxf.text)==0:
                        band_form_polig.append('-1')
                    else:
                        band_form_polig.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_polig = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')
                        
                elif attrib.dxf.tag=="TIPO_FORM":
                    if len(attrib.dxf.text)==0:
                        band_T_forms.append('-1')
                    else:
                        band_T_forms.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_tipo = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')

                    
                elif attrib.dxf.tag=="Nº_FORM":
                    if len(attrib.dxf.text)==0:
                        band_N_forms.append('-1')
                    else:
                        band_N_forms.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_numero = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')
                else:
                    form_tipo = 0
                    form_numero = 0
                    form_polig = 0
                
        if ("-1" in band_form_polig) or ("-1" in band_T_forms) or ("-1" in band_N_forms):

            validaciones_model.loc[18,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[18,'Observacion']="Error: En el bloque form no se ha completado algun campo"
            validaciones_model.loc[18,'Cetegoría']='Formularios'

        else:
            validaciones_model.loc[18,'Resultado']=0 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[18,'Observacion']="OK: Se han completado los campos del bloque form"
            validaciones_model.loc[18,'Cetegoría']='Formularios'

        if "-1" in band_letra_form:
            validaciones_model.loc[19,'Resultado']=-1
            validaciones_model.loc[19,'Observacion']="Error: Los campos 'Nº_POLIG.','TIPO_FORM', y 'Nº_FORM' deben completarse unicamente con números enteros"
            validaciones_model.loc[19,'Cetegoría']='Mejoras'
        else:
            validaciones_model.loc[19,'Resultado']=0
            validaciones_model.loc[19,'Observacion']="Ok: Los campos 'Nº_POLIG.','TIPO_FORM', y 'Nº_FORM' se completaron unicamente con números entero"
            validaciones_model.loc[19,'Cetegoría']='Mejoras'


        #--- 2.5.4.1 INICIO Validación de Nº de poligono en bloque FOrmularios--#
        if len(forms_polig)>0:

            forms_polig_sorted = sorted(forms_polig)

            if forms_polig_sorted[0] == 1:
                band_1_polig = "0"
            else:
                band_1_polig = "-1"
          
                       
            for i in range (0,len(forms_polig_sorted)):
                if (forms_polig_sorted[i] == (int(forms_polig_sorted[i-1]) + 1)):
                    band_correl_polig.append("0")
                else:
                    band_correl_polig.append("-1")

            band_correl_polig_2 = band_correl_polig.pop(0)

            if band_1_polig == "-1":

                validaciones_model.loc[20,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
                validaciones_model.loc[20,'Observacion']="Error: El primer Poligono indicado en el bloque form debe ser el Nº '1'"
                validaciones_model.loc[20,'Cetegoría']='Formularios'

            else:
                if "-1" in band_correl_polig:
                    validaciones_model.loc[20,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
                    validaciones_model.loc[20,'Observacion']="Error: Los poligonos deben numerarse en forma correlativa a partir del Nº '1'"
                    validaciones_model.loc[20,'Cetegoría']='Formularios'

                else:
                    validaciones_model.loc[20,'Resultado']=0 # si no hay un -1 en la bandera indica que la validación es correcta.
                    validaciones_model.loc[20,'Observacion']="OK: Numeros de poligonos en los bloques forms indicados correctamente"
                    validaciones_model.loc[20,'Cetegoría']='Formularios'
        else:

            validaciones_model.loc[20,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones_model.loc[20,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
            validaciones_model.loc[20,'Cetegoría']='Formularios'

            
    else:
        validaciones_model.loc[18,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[18,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones_model.loc[18,'Cetegoría']='Formularios'

        validaciones_model.loc[19,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[19,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones_model.loc[19,'Cetegoría']='Formularios'

        validaciones_model.loc[20,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones_model.loc[20,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones_model.loc[20,'Cetegoría']='Formularios'


    band_dict = {"band_mejora_cub_arc":band_mejora_cub_arc_0, "band_mejora_semi_arc":band_mejora_semi_arc_0, "band_mejora_desc_arc":band_mejora_desc_arc_0, "band_mejora_emp_arc":band_mejora_emp_arc_0, "band_mejora_nueva_arc":band_mejora_nueva_arc_0, "band_text_style":band_text_style,"band_parc_arc":band_parc_arc_1}

    mejoras_dict = {"piso_con_mejoras":piso_con_mejoras,"info_form_emp":info_form_emp,"info_form_nuevo" :info_form_nuevo,"layers_mejoras_spb":layers_mejoras_spb,"sup_cub_dxf":sup_cub_dxf, "sup_semicub_dxf":sup_semicub_dxf, "sup_descub_dxf":sup_descub_dxf,"sup_descont_dxf": sup_descont_dxf}

    return validaciones_model, medidas_dxf, parcelas_poly_close, parcelas_poly, excedentes_poly,mejoras_dict, band_dict, nom_parc_list, manzana_poly, resultado_inv 

# debe retornar   parcelas_poly_close_f,excedentes_poly_f, layouts, 
    #--- 2.5.4.1 FIN Validación de Nº de poligono en bloque FOrmularios--#
    #--- 2.5.5.1 INICIO Validación de restricciones--#
    #--- 2.5.5.1 FIN Validación de restricciones--#
      
#--- 2.5 FIN Validación de elementos del model --#

#--- INICIO Validación Layout-----#
