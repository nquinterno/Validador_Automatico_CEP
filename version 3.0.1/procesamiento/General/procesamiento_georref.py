from json import loads
from requests import get
from geopandas import GeoSeries
from shapely import Polygon, union, difference, area, geometry, Point
import ezdxf
from ezdxf.math import is_point_in_polygon_2d, Vec2
from pandas import DataFrame
import math
from procesamiento.General.catastroBox import correlacion_poligonos

def georref(smp,parcelas_poly_close, manzana_poly):
    
    validaciones_georref = DataFrame()
    
    global diferencia_coord
    global diferencia_coord_2
    global diferencia_coord_3
    global diferencia_coord
    global dif_max
    global parc_ant_posgba_2
    global manz_ant_posgba_2

    tol_verif_p = 0.51
    tol_error_p = 2.01
    
    tol_verif_m = 0.51
    tol_error_m = 1.01

    sm_0=list()
    sm = list()

    parc_ant_posgba = list()
    parc_ant_posgba_2 = list()

    manz_ant_posgba = list()
    manz_ant_posgba_2 = list()

    band_tol_p_error = list()
    band_tol_p_verif = list()
    band_tol_m_error = list()
    band_tol_m_verif = list()
    parametros = [-0.839549316178051,0.311003700314302,1.0000045988987,-0.000000917727150057199] #parametros de transformación obtenidos para llevar las coordenadas api ciudad3d convertidad a posgar bsas a las coordenadas oficiales de catatsro de las manzanas en posgar bs as
    resp_parc = ""
    resp_manz = ""
    respuesta_parc = ""
    respuesta_manz = ""
    diferencia_coord = list()
    diferencia_coord_2 = list()
    diferencia_coord_3 = list()
    dif_max=0
    parc_ant_posgba_0 = list()
    manz_ant_posgba_0 = list()
    manz_ant_wgs84_0 = list()
    parc_ant_wgs84_0 = list()
    parc_ant_wgs84_1 = list()
    manz_ant_wgs84_1 = list()

    for i in range(len(smp)):
        sm_0=(smp[i].split("-"))
        sm.append(f"{sm_0[0]}-{sm_0[1]}")

    if len(smp)==1:

        validaciones_georref.loc[0,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[0,'Observacion']="Ok: Existe un unico Layout de Ficha catastral con nomenclatura en su nombre SSS-MMMM-PPPP"
        validaciones_georref.loc[0,'Cetegoría']='Layout'
   
        try:
            resp_parc = get(f"https://epok.buenosaires.gob.ar/catastro/geometria/?smp={smp[0]}") #consulta a la api de ciudad 3d para pedir las coordenadas de la parcela
            resp_manz = get(f"https://epok.buenosaires.gob.ar/catastro/geometria/?sm={sm[0]}") #consulta a la api de ciudad 3d para pedir las coordenadas de la manzana
            respuesta_parc = loads(resp_parc.text)
            respuesta_manz = loads(resp_manz.text)

        except:  
            validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_georref.loc[1,'Observacion']="Error: No se puede validar la georref., verifique su conexión, que la parcela se encuentre en Ciudad3d, o la nomenclatura del layout"
            validaciones_georref.loc[1,'Cetegoría']='Tolerancias'

            validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_georref.loc[2,'Observacion']="Error: No se puede validar la georref., verifique su conexión, que la parcela se encuentre en Ciudad3d, o la nomenclatura del layout"
            validaciones_georref.loc[2,'Cetegoría']='Tolerancias'

        if len(respuesta_parc)>0 and len(respuesta_manz)>0: #si ciudad 3d responde con coordenadas se hace la validacion
            
            dic_p2=respuesta_parc.get("features") #la respuesta de cudad3d son listas anidadas, se accede hasta la ultima lista con las coordenadas y se guarda en parc_ant_wgs84
            dic_p3= dic_p2[0].get("geometry")
            dic_p4 = dic_p3.get("coordinates")
            dic_p5 = dic_p4[0]
            parc_ant_wgs84_0 = dic_p5[0] ## dic6 es una lista de listas de coordenadas de los vertices de la parcela consultada.

            dic_m2=respuesta_manz.get("features") #la respuesta de cudad3d son listas anidadas, se accede hasta la ultima lista con las coordenadas y se guarda en parc_ant_wgs84
            dic_m3= dic_m2[0].get("geometry")
            dic_m4 = dic_m3.get("coordinates")
            dic_m5 = dic_m4[0]
            manz_ant_wgs84_0 = dic_m5[0] ## dic6 es una lista de listas de coordenadas de los vertices de la parcela consultada.

            for m in manz_ant_wgs84_0:
                
                manz_ant_wgs84_1.append(GeoSeries(geometry.Point(m[0],m[1]),crs="EPSG:4326",))
            for p in parc_ant_wgs84_0:
            
                parc_ant_wgs84_1.append(GeoSeries(geometry.Point(p[0],p[1]),crs="EPSG:4326",))

            for m in manz_ant_wgs84_1:
                manz_ant_posgba_0.append(m.to_crs(9498))

            for p in parc_ant_wgs84_1:
                parc_ant_posgba_0.append(p.to_crs(9498))

            z = list()
            for m in manz_ant_posgba_0:
                x = (m.x)
                y = (m.y)
                z.append(x)
                z.append(y)
                manz_ant_posgba.append(z)
                z = list()

            z = list()
            for p in parc_ant_posgba_0:
                x = (p.x)
                y = (p.y)
                z.append(x)
                z.append(y)
                parc_ant_posgba.append(z)
                z = list()   

            for i in range (len(parc_ant_posgba)): # se aplica los parametros de transfoormación para la parcela antecedente de ciudad3d asi cae correstamente con las coordenadas de catastro y se guarda en parc_ant_posgba_2
                a = parc_ant_posgba[i]
                c_correg = list()
                a_correg = parametros[0]+(parametros[2]*a[0])-(parametros[3]*a[1])
                b_correg = parametros[1]+(parametros[2]*a[1])-(parametros[3]*a[0])
                c_correg.append(a_correg)
                c_correg.append(b_correg)
                parc_ant_posgba_2.append(c_correg)
 
            for i in range (len(manz_ant_posgba)): # se aplica los parametros de transfoormación para la parcela antecedente de ciudad3d asi cae correstamente con las coordenadas de catastro y se guarda en parc_ant_posgba_2
            
                a = manz_ant_posgba[i]
                c_correg = list()
                a_correg = parametros[0]+(parametros[2]*a[0])-(parametros[3]*a[1])
                b_correg = parametros[1]+(parametros[2]*a[1])-(parametros[3]*a[0])
                c_correg.append(a_correg)
                c_correg.append(b_correg)
                manz_ant_posgba_2.append(c_correg)

            if len(parcelas_poly_close):
            
                ver_cep_p1 = parcelas_poly_close[0].get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control
                ver_cep_p2 = Vec2.list(ver_cep_p1) #arma el vector necesariopara la funcion que verifica que cada vertice este dentro del poligono

                ver_ant_p1 = parc_ant_posgba_2 #prepara la parcela antecedente transformada para compararla con la medida
                ver_ant_p2 = Vec2.list(ver_ant_p1)
                ver_ant_p3 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset= tol_verif_p, closed=True)) #arma ofsets de 0,5m para afuera y para adentro de la parcela antecedente y la parcela medida debe caer dentro de esos dos poligonos
                ver_ant_p4 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset=-tol_verif_p, closed=True))

                ver_ant_p5 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset=tol_error_p, closed=True))
                ver_ant_p6 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset=-tol_error_p, closed=True))
                
                ver_ant_m1 = manz_ant_posgba_2 #prepara la parcela antecedente transformada para compararla con la medida
                ver_ant_m2 = Vec2.list(ver_ant_m1)
                ver_ant_m3 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=tol_verif_m, closed=True)) #arma ofsets de 0,5m para afuera y para adentro de la parcela antecedente y la parcela medida debe caer dentro de esos dos poligonos
                ver_ant_m3 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=0.51, closed=True)) 
                ver_ant_m4 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=-tol_verif_m, closed=True))

                ver_ant_m5 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=tol_error_m, closed=True))
                ver_ant_m6 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=-tol_error_m, closed=True)) 
    
    ### INICIO DE EN PREPARACION ALGORITMO DE GEORREFEENCIACIÓN 2.0             
                #calcula todas las distancias de los vertices de la parcela a los vertices antecedentes
                # correlacion_p = correlacion_poligonos(ver_cep_p2,ver_ant_p2,0.8)
                
                # print("correlacion_parcela")
                # print(correlacion_p)

                # correlacion_m = correlacion_poligonos(manzana_poly,ver_ant_m2,0.8)
                # print("correlacion_parcela")
                # print(correlacion_m)

    ### FIN DE EN PREPARACION ALGORITMO DE GEORREFEENCIACIÓN 2.0

                for vert in ver_cep_p2:
                    if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m5,abs_tol=1e-4)==-1:
                        if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m6,abs_tol=1e-4)==-1:
                            band_tol_m_error.append("-1")
                        else:
                            band_tol_m_error.append("0")
                            if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m3,abs_tol=1e-4)==-1:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m4,abs_tol=1e-4)==-1:
                                    band_tol_m_verif.append("-1")
                                else:
                                    band_tol_m_verif.append("0")
                            else:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m4,abs_tol=1e-4)==0:
                                    band_tol_m_verif.append("-1")
                                else:
                                    band_tol_m_verif.append("0")

                    else:
                        if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m6,abs_tol=1e-4)==0:
                            band_tol_m_error.append("-1")
                        else:
                            band_tol_m_error.append("0")
                            if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m3,abs_tol=1e-4)==-1:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m4,abs_tol=1e-4)==-1:
                                    band_tol_m_verif.append("-1")
                                else:
                                    band_tol_m_verif.append("0")
                            else:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m4,abs_tol=1e-4)==0:
                                    band_tol_m_verif.append("-1")
                                else:
                                    band_tol_m_verif.append("0")
                

                    if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p5,abs_tol=1e-4)==-1:
                        if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p6,abs_tol=1e-4)==-1:
                            band_tol_p_error.append("-1") #OK
                        else:
                            band_tol_p_error.append("0")
                            if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p3,abs_tol=1e-4)==-1:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p4,abs_tol=1e-4)==-1:
                                    band_tol_p_verif.append("-1")
                                else:
                                    band_tol_p_verif.append("0")
                            else:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p4,abs_tol=1e-4)==0:
                                    band_tol_p_verif.append("-1")
                                else:
                                     band_tol_p_verif.append("0")     
                    else:
                        if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p6,abs_tol=1e-4)==0:
                            band_tol_p_error.append("-1") #OK
                        else:
                            band_tol_p_error.append("0")
                            if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p3,abs_tol=1e-4)==-1:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p4,abs_tol=1e-4)==-1:
                                    band_tol_p_verif.append("-1")
                                else:
                                    band_tol_p_verif.append("0")
                            else:
                                if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p4,abs_tol=1e-4)==0:
                                    band_tol_p_verif.append("-1")
                                else:
                                    band_tol_p_verif.append("0")
                    
                if "-1" in band_tol_m_error:

                    validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                    validaciones_georref.loc[1,'Observacion']="Error: No se ha georreferenciado Correctamente"
                    validaciones_georref.loc[1,'Cetegoría']='Tolerancias'
                else:
                    if "-1" in band_tol_m_verif:
                        validaciones_georref.loc[1,'Resultado']=50# si hay un -1 en la bandera arroja error 
                        validaciones_georref.loc[1,'Observacion']=f"Verificar: La parcela medida excede la tolerancia de {tol_verif_m}m respecto a la manzana antecedente de Ciudad 3d, verificar georreferenciación"
                        validaciones_georref.loc[1,'Cetegoría']='Tolerancias'
                    else:
                        validaciones_georref.loc[1,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                        validaciones_georref.loc[1,'Observacion']="Ok: La parcela se encuentra dentro de la manzana a la que pertenece"
                        validaciones_georref.loc[1,'Cetegoría']='Tolerancias'
                
                if "-1" in  band_tol_p_error:
                        validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                        validaciones_georref.loc[2,'Observacion']=f"Error: La parcela medida excede la tolerancia de {tol_error_p} respecto a la parcela antecedente, no se ha georreferenciado correctamente"
                        validaciones_georref.loc[2,'Cetegoría']='Tolerancias'
                else:
                    if "-1" in band_tol_p_verif:
                        validaciones_georref.loc[2,'Resultado']=50 # si hay un -1 en la bandera arroja error 
                        validaciones_georref.loc[2,'Observacion']=f"Verificar: La parcela medida excede la tolerancia de {tol_verif_p}m respecto a la parcela antecedente de Ciudad 3d, verificar medidas con ficha parcelaria"
                        validaciones_georref.loc[2,'Cetegoría']='Tolerancias'
                    else:
                        validaciones_georref.loc[2,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                        validaciones_georref.loc[2,'Observacion']="Ok: La parcela se encuentra en tolerancia con respecto a la parcela antecedente de Ciudad 3d"
                        validaciones_georref.loc[2,'Cetegoría']='Tolerancias'

                for vert in ver_cep_p1:

                    diferencia_coord = list()

                    for vert1 in ver_ant_p1:
                      
                        diferencia_coord.append(math.sqrt(((vert[0]-vert1[0])**2)+((vert[1]-vert1[1])**2)))

                    diferencia_coord_2.append(min(diferencia_coord))
                    
                diferencia_coord_3 = sorted(diferencia_coord_2, reverse = False)

                dif_max = round(max(diferencia_coord_3),2)
                
            else:
                validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_georref.loc[1,'Observacion']="Error: No se puede validar la georreferenciación porque no se encuen5ra dubujada la parcela como polilinea cerrada en el layer 09-M-PARCELA"
                validaciones_georref.loc[1,'Cetegoría']='Tolerancias'

                validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_georref.loc[2,'Observacion']="Error: No se puede validar la georreferenciación porque no se encuen6ra dubujada la parcela como polilinea cerrada en el layer 09-M-PARCELA"
                validaciones_georref.loc[2,'Cetegoría']='Tolerancias'
        else:

                validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_georref.loc[1,'Observacion']="Error: No puede validarse la georref., no se encuentra en Ciudad3d la parcela indicada en el layout o no se puede conectarse con Ciudad3d"
                validaciones_georref.loc[1,'Cetegoría']='Tolerancias'

                validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones_georref.loc[2,'Observacion']="Error: No puede validarse la georref., no se encuentra en Ciudad3d la parcela indicada en el layout o no se puede conectarse con Ciudad3d"
                validaciones_georref.loc[2,'Cetegoría']='Tolerancias'
   
    
    elif len(smp)>1:

        validaciones_georref.loc[0,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[0,'Observacion']="Error: Existen mas de un Layout de Ficha catastral con nomenclatura en su nombre SSS-MMMM-PPPP"
        validaciones_georref.loc[0,'Cetegoría']='Layout'

        validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[1,'Observacion']="Error: Existen más de un Layout con nombre SSS-MMMM-PPPP, con lo que no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones_georref.loc[1,'Cetegoría']='Layout'

        validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[2,'Observacion']="Error: Existen más de un Layout con nombre SSS-MMMM-PPPP, con lo que no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones_georref.loc[2,'Cetegoría']='Layout'

    else:

        validaciones_georref.loc[0,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[0,'Observacion']="Error: No existe layout cuyo nombre tenga formato de nomenclatura catastral SSS-MMMM-PPPP"
        validaciones_georref.loc[0,'Cetegoría']='Layout'

        validaciones_georref.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[1,'Observacion']="Error: No existe layout cuyo nombre tenga formato ‘SSS-MMMM-PPPP’, no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones_georref.loc[1,'Cetegoría']='Layout'

        validaciones_georref.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_georref.loc[2,'Observacion']="Error: No existe layout cuyo nombre tenga formato ‘SSS-MMMM-PPPP’, no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones_georref.loc[2,'Cetegoría']='Layout'
    
    return validaciones_georref, dif_max, parc_ant_posgba_2, manz_ant_posgba_2