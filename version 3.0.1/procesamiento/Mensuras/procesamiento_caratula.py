import pandas as pd
from pandas import DataFrame, read_excel, read_csv
import ezdxf
import re
from procesamiento.General.catastroBox import sup_polilinea

def chequeo_caratula(doc,opcion_mens,parcelas_poly_close, excedentes_poly, cesion_poly_close):
                
    global layouts
    global objetos_planos
    global validaciones_caratula
    
    validaciones_caratula = pd.DataFrame()
    sup_mens_poly = 0
    
    for i in parcelas_poly_close:
        sup_mens_poly = sup_mens_poly + sup_polilinea(i)

    for j in cesion_poly_close:
        sup_mens_poly = sup_mens_poly + sup_polilinea(j)

    caratulas=doc.query('INSERT[name=="CARATULA-CABA"]') #consulta el bloque caratula (todas las veces que se inserto)
    caratulas_s_balance = doc.query('INSERT[name=="CARATULA-CABA-MODIF_COMP_PRESC-UF"]')
    
    model_1 = list()
    point_model = list()
    model = doc.modelspace()
    bloque_caratula_model = doc.modelspace().query('INSERT[name=="CARATULA-CABA"]') | doc.modelspace().query('INSERT[name=="CARATULA-CABA-MODIF_COMP_PRESC-UF"]')
            
    bandera_layer=list()
    bandera_model=list()

    objetos_planos = read_excel('configuracion/objetos.xls')


    # INICIO Validar que este inserto el bloque caratula, en el/los layouts, en el layer correcto 


    if len(caratulas)>0: #Valida si se está inserto el bloque caratula

    
        validaciones_caratula.loc[0,'Resultado']=0
        validaciones_caratula.loc[0,'Observacion']='OK: Se encuentra inserto el Bloque Caratula'
        validaciones_caratula.loc[0,'Cetegoría']='Caratula'
        

        for caratula in caratulas:              

            #Inicio validar que la caratula este inserta en layer que corresponde
            if caratula.dxf.layer=="01-P-PLANO-CARATULA": 
                bandera_layer.append('0')
            else:
                bandera_layer.append('-1')
            #Fin validar que la caratula este inserta en layer que corresponde

            #Inicio validar que la caratula este inserta en los Layouts

                
            #Fin validar que la caratula este inserta en los Layouts

        if len(bloque_caratula_model)>0:
            bandera_model.append('-1')
        else:
            bandera_model.append('0')

                
        if '-1' in bandera_layer:

            validaciones_caratula.loc[1,'Resultado']=-1
            validaciones_caratula.loc[1,'Observacion']='ERROR: La caratula se encuentra inserta en el Layer Incorrecto'
            validaciones_caratula.loc[1,'Cetegoría']='Caratula'
        else:

            validaciones_caratula.loc[1,'Resultado']=0
            validaciones_caratula.loc[1,'Observacion']='OK: La caratula se encuentra inserta en el Layer correcto'
            validaciones_caratula.loc[1,'Cetegoría']='Caratula'

        if '-1' in bandera_model:

            validaciones_caratula.loc[2,'Resultado']=-1
            validaciones_caratula.loc[2,'Observacion']='ERROR: Existe caratula inserta en el espacio modelo'
            validaciones_caratula.loc[2,'Cetegoría']='Caratula'
        else:

            validaciones_caratula.loc[2,'Resultado']=0
            validaciones_caratula.loc[2,'Observacion']='OK: La o las caratulas se encuentran insertas en el/los Layout/s'
            validaciones_caratula.loc[2,'Cetegoría']='Caratula'
    else:

        validaciones_caratula.loc[0,'Resultado']=-1
        validaciones_caratula.loc[0,'Observacion']='ERROR: No se encuentra inserto el Bloque Caratula'
        validaciones_caratula.loc[0,'Cetegoría']='Caratula'
        
        validaciones_caratula.loc[1,'Resultado']=-2
        validaciones_caratula.loc[1,'Observacion']='ERROR: No es posible validar la caratula dado que no se encuentra inserto el bloque caratula'
        validaciones_caratula.loc[1,'Cetegoría']='Caratula'

        validaciones_caratula.loc[2,'Resultado']=-2
        validaciones_caratula.loc[2,'Observacion']='ERROR: No es posible validar la caratula dado que no se encuentra inserto el bloque caratula'
        validaciones_caratula.loc[2,'Cetegoría']='Caratula'
    # FIN Validar que este inserto el bloque caratula, en el/los layouts, en el layer correcto 

    #INICIO validar que la caratula tenga los atributos completos y que sean coherentes excepto el balance que se valida mas adelante

    atributos_tag = list()
    caratulas_valores = pd.DataFrame() #ver como cargar los atributos de la lista en las columnas del dataframe
    bloque_caratula = doc.query('INSERT[name=="CARATULA-CABA"]')

    #variables que leen las distintas caratulas y guardan un dato especifico para cada caratula

    #recolectores de atributos de varias caratulas ára comparar que sean iguales y que no esten vacios#

    global car_manz
    global car_parc
    global car_manz_lower
    global car_parc_lower

    car_circ,car_sec,car_manz,car_manz_lower,car_parc,car_parc_lower,car_direc,car_prop,car_dominio,car_fecha_mens,car_cur,car_partida,car_num_plano,car_tipo_plano,car_año_plano,car_hoja,car_objeto,car_agrim,car_cuit,car_mens,car_tit, car_dif, car_tipo_dif, car_hojas= list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list() ,list () ,list() ,list() ,list() ,list() ,list() ,list(), list(), list()
    
    #recolectores de atributos de varias caratulas#

    #Banderas de igualdad de atributos en varias caratulas#
    
    band_circ,band_sec, band_manz,band_parc,band_direc,band_prop,band_dominio,band_fecha_mens,band_cur,band_partida, band_num_plano ,band_tipo_plano,band_año_plano,band_hoja,band_objeto,band_agrim,band_cuit,band_mens,band_tit,band_dif,band_tipo_dif = list() ,list(), list() ,list() ,list() ,list(),list(), list(), list(), list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list()

    #Banderas de igualdad de atributos en varias caratulas#

    #Banderas de vacio de atributos#
    
    band_vac_circ, band_vac_sec,band_vac_manz,band_vac_parc,band_vac_direc,band_vac_prop,band_vac_dominio,band_vac_fecha_mens,band_vac_cur,band_vac_partida ,band_vac_num_plano,band_vac_tipo_plano,band_vac_año_plano,band_vac_tipo_plano,band_vac_año_plano,band_vac_hoja,band_vac_objeto,band_vac_agrim ,band_vac_cuit,band_vac_mens,band_vac_tit,band_vac_dif,band_vac_tipo_dif = list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list(),list()

    #Banderas de vacio de atributos#
    
    #variables que leen las distintas caratulas y guardan un dato especifico para cada caratula

    for caratula in bloque_caratula:

        for attribs in caratula.attribs:
        
            if attribs.dxf.tag == "0201-CIRC.":
                
                car_circ.append(attribs.dxf.text)
                
            elif attribs.dxf.tag == "0202-SECC.":
                
                car_sec.append(attribs.dxf.text)
            
            elif attribs.dxf.tag == "0203-MANZ.":
                
                car_manz.append(attribs.dxf.text.lower())
                car_manz_lower.append(attribs.dxf.text.lower())
                
            elif attribs.dxf.tag == "0204-PARC.":
                
                car_parc.append(attribs.dxf.text)
                car_parc_lower.append(attribs.dxf.text.lower())
                
            elif attribs.dxf.tag == "0205-CALLE":
                
                car_direc.append(attribs.dxf.text)
                
            elif attribs.dxf.tag == "0206-PROPIETARIOS":
                
                car_prop.append(attribs.dxf.text)
                
            elif attribs.dxf.tag == "0208-RPI":

                car_dominio.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0801-FECHA":

                car_fecha_mens.append(attribs.dxf.text)
            
            elif attribs.dxf.tag == "0302-C.U.R":

                car_cur.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0207-PARTIDA":

                car_partida.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0901-TIPO":

                car_tipo_plano.append(attribs.dxf.text)

            elif attribs.dxf.tag =="0902-NUM":
                car_num_plano.append(attribs.dxf.text)

            elif attribs.dxf.tag =="0903-AÑO":
                car_año_plano.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0102-HOJA":

                car_hojas.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0103-PLANO":

                car_objeto.append(attribs.dxf.text)            

            elif attribs.dxf.tag == "0802-AGRIMENSOR":

                car_agrim.append(attribs.dxf.text)

            elif attribs.dxf.tag == "0807-CUIT-AGRIM.":

                car_cuit.append(attribs.dxf.text)
                
            elif attribs.dxf.tag =="SUPS/M":
                
                car_mens.append(attribs.dxf.text)

            elif attribs.dxf.tag =="SUPS/T-P":
                
                car_tit.append(attribs.dxf.text)

            elif attribs.dxf.tag =="DIFBALANCE":
                
                car_dif.append(attribs.dxf.text)

            elif attribs.dxf.tag =="TIPODIF":
                car_tipo_dif.append(attribs.dxf.text)

            else: 
                pass


    #si tiene mas de una caratula verifica que se hayan puesto los mismos datos para el mismo campo en todas las caratulas#

    if len(bloque_caratula)>1:

        for i in range (len(bloque_caratula)):
            if car_circ[i-1] == car_circ[i]: #Evalua que todos los valores de circunscripción, sean iguales
                band_circ.append('0')
            else:
                band_circ.append('-1')

            if car_sec[i-1] == car_sec[i]: #Evalua que todos los valores de sección, sean iguales
                band_sec.append('0')
            else:
                band_sec.append('-1')

            if car_manz[i-1] == car_manz[i]: #Evalua que todos los valores de manzana, sean iguales
                band_manz.append('0')
            else:
                band_manz.append('-1')

            if car_parc[i-1] == car_parc[i]: #Evalua que todos los valores de parcela, sean iguales
                band_parc.append('0')
            else:
                band_parc.append('-1')

            if car_fecha_mens[i-1] == car_fecha_mens[i]: #Evalua que todos los valores de fecha de mensura, sean iguales
                band_fecha_mens.append('0')
            else:
                band_fecha_mens.append('-1')

            if car_partida[i-1] == car_partida[i]: #Evalua que todos los valores de partida , sean iguales
                band_partida.append('0')
            else:
                band_partida.append('-1')

            if car_num_plano[i-1] == car_num_plano[i]: #Evalua que todos los valores de numero de plano, sean iguales
                band_num_plano.append('0')
            else:
                band_num_plano.append('-1')

            if car_tipo_plano[i-1] == car_tipo_plano[i]: #Evalua que todos los valores de numero de plano, sean iguales
                band_tipo_plano.append('0')
            else:
                band_tipo_plano.append('-1')

            if car_año_plano[i-1] == car_año_plano[i]: #Evalua que todos los valores de numero de plano, sean iguales
                band_año_plano.append('0')
            else:
                band_año_plano.append('-1')               

            if car_dif[i-1] == car_dif[i]: #Evalua que todos los valores de numero de plano, sean iguales
                band_dif.append('0')
            else:
                band_dif.append('-1')

            if car_objeto[i-1] == car_objeto[i]: #Evalua que todos los valores de dobjeto de plano, sean iguales
                band_objeto.append('0')
            else:
                band_objeto.append('-1')

            if car_mens[i-1] == car_mens[i]: #Evalua que todos los valores de Sup s/m, sean iguales
                band_mens.append('0')
            else:
                band_mens.append('-1')

            if car_tit[i-1] == car_tit[i]: #Evalua que todos los valores de Sup s/t, sean iguales
                band_tit.append('0')
            else:
                band_tit.append('-1')

            if car_tipo_dif[i-1] == car_tipo_dif[i]: #Evalua que todos los valores de dif balance, sean iguales
                band_tipo_dif.append('0')
            else:
                band_tipo_dif.append('-1')

        #consulta las banderas de os distintos valores buscando que se haya detectado una diferencia. Si hay diferencia tirra erroro sino se fija que los campos no esten vacios

        if (("-1" in band_circ) or ("-1" in band_sec) or ("-1" in  band_manz) or ("-1" in  band_parc) or
                ("-1" in band_fecha_mens) or ("-1" in  band_partida) or ("-1" in band_tipo_dif)or ("-1" in  band_num_plano) or ("-1" in band_objeto) or ("-1" in band_mens) or ("-1" in band_tit) or ("-1" in band_dif)):
            
            validaciones_caratula.loc[3,'Resultado']=-1
            validaciones_caratula.loc[3,'Observacion']="ERROR: No se ingresaron los mismos datos en las caratulas insertas"
            validaciones_caratula.loc[3,'Cetegoría']='Caratula'
            
        else:

            for i in range (len(bloque_caratula)):

                if car_circ[i]==None:
                    band_vac_circ.append("-1")
                else:
                    band_vac_circ.append("0")

                if car_sec[i]==None:
                    band_vac_sec.append("-1")
                else:
                    band_vac_sec.append("0")

                if car_manz[i]==None:
                    band_vac_manz.append("-1")
                else:
                    band_vac_manz.append("0")

                if car_parc[i]==None:
                    band_vac_parc.append("-1")
                else:
                    band_vac_parc.append("0")

                if car_fecha_mens[i]==None:
                    band_vac_fecha_mens.append("-1")
                else:
                    band_vac_fecha_mens.append("0")

                if car_partida[i]==None:
                    band_vac_partida.append("-1")
                else:
                    band_vac_partida.append("0")

                if car_num_plano[i]==None:
                    band_vac_num_plano.append("-1")
                else:
                    band_vac_num_plano.append("0")

                if car_tipo_plano[i]==None:
                    band_vac_tipo_plano.append("-1")
                else:
                    band_vac_tipo_plano.append("0")

                if car_año_plano[i]==None:
                    band_vac_año_plano.append("-1")
                else:
                    band_vac_año_plano.append("0")

                if car_mens[i]==None:
                    band_vac_mens.append("-1")
                else:
                    band_vac_mens.append("0")

                if car_tit[i]==None:
                    band_vac_tit.append("-1")
                else:
                    band_vac_tit.append("0")

                if car_dif[i]==None:
                    band_vac_dif.append("-1")
                else:
                    band_vac_dif.append("0")

                if car_tipo_dif[i]==None:
                    band_vac_tipo_dif.append("-1")
                else:
                    band_vac_tipo_dif.append("0") 

            if (("-1" in band_vac_circ) or ("-1" in band_vac_sec) or ("-1" in band_vac_manz) or ("-1" in band_vac_parc) or ("-1" in band_vac_fecha_mens) or ("-1" in band_vac_tipo_dif) 
                or ("-1" in band_vac_partida) or ("-1" in band_vac_mens) or ("-1" in band_vac_tit) or ("-1" in band_vac_dif) or ("-1" in band_vac_num_plano)):

                
                validaciones_caratula.loc[3,'Resultado']=-1
                validaciones_caratula.loc[3,'Observacion']="ERROR: Existen campos vacios en las caratulas insertas"
                validaciones_caratula.loc[3,'Cetegoría']='Caratula'

            else:
                validaciones_caratula.loc[3,'Resultado']=0
                validaciones_caratula.loc[3,'Observacion']="OK: Los campos de las caratulas se encuentran completos"
                validaciones_caratula.loc[3,'Cetegoría']='Caratula'


                patron_circ = re.compile('^[0-9]{1,3}$')
                patron_sec = re.compile('^[0-9]{3}$')
                patron_maz_parc = re.compile(r'(^([0-9]{3})|([0-9]{3}[a-z]{1}))|(\D{3,}(\.)*(Plano|PLANO|plano)\D{0,})$')
                # patron_fecha_mens = re.compile('^([0-9]{2}/[0-9]{2}/[0-9]{4})|([0-9]{2}-[0-9]{2}-[0-9]{4})$')
                patron_fecha_mens = re.compile('^([0-9]{2}/[0-9]{4})|([0-9]{2}-[0-9]{4})$')
                patron_balance = re.compile(r'^[0-9]{1,}\.[0-9]{1,}$')
                # patron_plano = re.compile('^(MH-|M-|MS-)[0-9]{4}-[0-9]{4}$')
                patron_plano = re.compile('^[0-9]{4}$')

                band_pat_circ = list()
                band_pat_sec = list()
                band_pat_manz = list()
                band_pat_parc = list()
                band_pat_fecha_mens = list()
                band_pat_plano = list()

                band_pat_mens = list()
                band_pat_tit = list()
                band_pat_dif = list()

                for i in range(len(bloque_caratula)):
                    band_pat_circ.append(patron_circ.match(car_circ[i]))#recolecta como salio la validacion en las distintas caratulas para el campo circunscripión
                    band_pat_sec.append(patron_sec.match(car_sec[i]))#recolecta como salio la validacion en las distintas caratulas para el campo sección
                    band_pat_manz.append(patron_maz_parc.match(car_manz[i]))#recolecta como salio la validacion en las distintas caratulas para el campo manzana
                    band_pat_parc.append(patron_maz_parc.match(car_parc[i]))          #recolecta como salio la validacion en las distintas caratulas para el campo parcela
                    band_pat_fecha_mens.append(patron_fecha_mens.match(car_fecha_mens[i])) #recolecta como salio la validacion en las distintas caratulas para el campo feha mensura 
                    band_pat_plano.append(patron_plano.match(car_num_plano[i]))
                    band_pat_mens.append(patron_balance.match(car_mens[i]))
                    band_pat_tit.append(patron_balance.match(car_tit[i]))
                    band_pat_dif.append(patron_balance.match(car_dif[i]))


                                            
                if None in (band_pat_circ) or (None in band_pat_sec) or (None in band_pat_manz) or (None in band_pat_parc) or (None in band_pat_fecha_mens) or (None in band_pat_plano):
                    validaciones_caratula.loc[4,'Resultado']=-1
                    validaciones_caratula.loc[4,'Observacion']="ERROR: Alguno de los campos Circ, Sec, Manz, Parc, fecha de mensura no se han completado correctamente"
                    validaciones_caratula.loc[4,'Cetegoría']='Caratula'
                else:
                    validaciones_caratula.loc[4,'Resultado']=0
                    validaciones_caratula.loc[4,'Observacion']="OK: Los campos Circ, Sec, Manz, Parc, fecha de mensura se han completado correctamente"
                    validaciones_caratula.loc[4,'Cetegoría']='Caratula'

                if None in (band_pat_mens) or (None in band_pat_tit) or (None in band_pat_dif):
                    validaciones_caratula.loc[5,'Resultado']=-1
                    validaciones_caratula.loc[5,'Observacion']='ERROR: Alguno de los valores de superficies del balance no son numericos o se utilizó un separador distinto de "."'
                    validaciones_caratula.loc[5,'Cetegoría']='Caratula'
                else:
                    validaciones_caratula.loc[5,'Resultado']=0
                    validaciones_caratula.loc[5,'Observacion']="OK: Los campos del Balance de superficie se completaron correctamente"
                    validaciones_caratula.loc[5,'Cetegoría']='Caratula'

                    band_dif_sup=list()
                    band_men_tit = list()


                    for i in range (len(car_mens)):
                        sup_men = car_mens[i]
                        
                        if abs(float(sup_mens_poly) - float(sup_men)) <= 0.01: #evalua que la supericie que puso como sup. de mensura en el balance de la primer caratula no difiera mas de 1cm2 de la suma de todos los poligonos de parcela y cesiones
                            band_dif_sup.append('0')
                        else:
                            band_dif_sup.append('-1')

                    if '-1' in band_dif_sup:
                        validaciones_caratula.loc[6,'Resultado']=-1
                        validaciones_caratula.loc[6,'Observacion']='ERROR: La superficie según mensura del balance de alguna de las caratulas no coincide con la suma de las supercicies de los poligonos Parcelas y Cesiones o no se ha podido validar por no ser un número'
                        validaciones_caratula.loc[6,'Cetegoría']='Caratula'
                    else:
                        validaciones_caratula.loc[6,'Resultado']=0
                        validaciones_caratula.loc[6,'Observacion']='OK: La superficie según mensura del balance coincide con la superficie de los polignos los poligonos Parcelas y Cesiones'
                        validaciones_caratula.loc[6,'Cetegoría']='Caratula'

                    for i in range (len(car_dif)):

                        if abs(float(car_dif[i]) - abs((float(car_mens[i]) - float(car_tit[i])))) <= 0.01:
                            band_men_tit.append("0")
                        else:
                            band_men_tit.append("-1")
                        
                    
                    if "-1" in band_men_tit:
                        validaciones_caratula.loc[7,'Resultado']=-3
                        validaciones_caratula.loc[7,'Observacion']="ERROR: En la o alguna de las caratulas no coincide el valor indicado con la diferencia real entre las superficies según Mensura y título/plano"
                        validaciones_caratula.loc[7,'Cetegoría']='Caratula'
                    else:
                        validaciones_caratula.loc[7,'Resultado']=0
                        validaciones_caratula.loc[7,'Observacion']="OK: El valor de la diferencia de superficie entre mensura y titulo se indicó correctamente en los valances de la/s caratula/s"
                        validaciones_caratula.loc[7,'Cetegoría']='Caratula'


                    #<----- Valida que se haya colocado Diferenci en Menos Más o Excedente según corresponda------>#

                    band_excedente = list()
                    band_dif_mas = list()
                    band_dif_menos = list()
                    band_dif = list()

                    for i in range (len(car_mens)):
                        if (len(car_mens[i])>0) and (len(car_tit[i])>0):
                            if (float(car_mens[i]) - float(car_tit[i])) >= (0.05 * float(car_tit[i])):
                                if ("EXCEDENTE" in car_tipo_dif[i]) or ("Excedente" in car_tipo_dif[i]) or ("excedente" in car_tipo_dif[i]):
                                    band_excedente.append("0")
                                else:
                                    band_excedente.append("-1")
                            elif ((float(car_mens[i]) - float(car_tit[i])>0)) and ((float(car_mens[i]) - float(car_tit[i]))<(0.05 * float(car_tit[i]))):
                                if ("MAS" in car_tipo_dif[i]) or ("Más" in car_tipo_dif[i]) or ("Mas" in car_tipo_dif[i]) or ("mas" in car_tipo_dif[i]):
                                    band_dif_mas.append("0")
                                else:
                                    band_dif_mas.append("-1")
                            elif (float(car_mens[i]) - float(car_tit[i])<0):
                                if ("Menos" in car_tipo_dif[i]) or ("menos" in car_tipo_dif[i]) or ("MENOS" in car_tipo_dif[i]):
                                    band_dif_menos.append("0")
                                else:
                                    band_dif_menos.append("-1")
                            elif ((float(car_mens[i]) - float(car_tit[i])==0)):
                                if ("Dif." in car_tipo_dif[i]) or ("Diferencia" in car_tipo_dif[i]) or ("DIFERENCIA" in car_tipo_dif[i]) or ("DIF." in car_tipo_dif[i]):
                                    band_dif.append("0")
                                else:
                                    band_dif.append("-1")
                        else:
                            validaciones_caratula.loc[8,'Resultado']=-1
                            validaciones_caratula.loc[8,'Observacion']="ERROR: Se han consignado valores negativos en la Sup. S/ Mensura o Sup S/ Tit."
                            validaciones_caratula.loc[8,'Cetegoría']='Caratula'
                        
                    if ("-1" in band_excedente) or ("-1" in band_dif_menos) or ("-1" in band_dif_mas) or ("-1" in band_dif):
                        validaciones_caratula.loc[8,'Resultado']=-1
                        validaciones_caratula.loc[8,'Observacion']="ERROR: No coincide el Tipo de diferencia del balance (Diferencia, Diferencia en más, Diferencia en Menos, Excedente), con el valor de la dif. entre titulo y mensura del balance"
                        validaciones_caratula.loc[8,'Cetegoría']='Caratula'
                    else:
                        validaciones_caratula.loc[8,'Resultado']=0
                        validaciones_caratula.loc[8,'Observacion']="OK: El tipo de diferencia declarada en el balance coincide con la diferencia de valor entre Mensura y Título"
                        validaciones_caratula.loc[8,'Cetegoría']='Caratula'

        
        
                     #VALIDAR QUE LA SUPERF DEL BALANCE SEA IGUAL A LAS DE MENSURAS

        hojas = list()
        band_hojas = list()
        band_hojas_totales = list()

        
        for i in range (len(car_hojas)):
            hoja_de_hojas = car_hojas[i].split(" DE ")
            hojas.append(int(hoja_de_hojas[0])) 

            if int(hoja_de_hojas[1]) == len(bloque_caratula):
                band_hojas_totales.append("0")
            else:
                band_hojas_totales.append("-1")

        #chequea que el primer numero de hoja sea 1, que el ultimo numero de hoja sea igual al total de caratulas insertas y 

        if len(hojas)>0:
            if 1 in hojas:
                band_hojas.append("0")
            else:
                band_hojas.append("-1")

            if max(hojas) == len(bloque_caratula):
                band_hojas.append("0")
            else:
                band_hojas.append("-1")


            #chequear que sean correlativos y no haya repetidos
            if len(set(hojas)) == len(hojas) and (max(hojas) - min(hojas) + 1) == len(hojas):
                band_hojas.append("0")
            else:   
                band_hojas.append("-1")

        else:
            band_hojas.append("-1")


        if ("-1" in band_hojas) or ("-1" in band_hojas_totales):
            validaciones_caratula.loc[9,'Resultado']=-1
            validaciones_caratula.loc[9,'Observacion']="ERROR: El/Los número/s de hoja/s de las caratulas deben ser correlativos, comenzar en 1 y coincidir con el total de caratulas insertas"
            validaciones_caratula.loc[9,'Cetegoría']='Caratula'
        else:
            validaciones_caratula.loc[9,'Resultado']=0
            validaciones_caratula.loc[9,'Observacion']="OK: El/Los número/s de hoja/s de las caratulas se completó correctamente"
            validaciones_caratula.loc[9,'Cetegoría']='Caratula'

               #guarda la primer parte del texto de la hoja, que es el numero de hoja

    #verificar que los datos de los distintos atributos no esten vacios si estan vacios hacer alerta sino seguir verificando que los datos sean coherentes

    #verificar que los datos de los distintos atributos no esten vacios si estan vacios hacer alerta sino seguir verificando que los datos sean coherentes                
    elif len(bloque_caratula)==1:
        for i in range (len(bloque_caratula)):

            if car_circ[i]==None:
                band_vac_circ.append("-1")
            else:
                band_vac_circ.append("0")

            if car_sec[i]==None:
                band_vac_sec.append("-1")
            else:
                band_vac_sec.append("0")

            if car_manz[i]==None:
                band_vac_manz.append("-1")
            else:
                band_vac_manz.append("0")

            if car_parc[i]==None:
                band_vac_parc.append("-1")
            else:
                band_vac_parc.append("0")

            if car_fecha_mens[i]==None:
                band_vac_fecha_mens.append("-1")
            else:
                band_vac_fecha_mens.append("0")

            if car_partida[i]==None:
                band_vac_partida.append("-1")
            else:
                band_vac_partida.append("0")

            if car_num_plano[i]==None:
                band_vac_num_plano.append("-1")
            else:
                band_vac_num_plano.append("0")

            if car_tipo_plano[i]==None:
                band_vac_tipo_plano.append("-1")
            else:
                band_vac_tipo_plano.append("0")

            if car_año_plano[i]==None:
                band_vac_año_plano.append("-1")
            else:
                band_vac_año_plano.append("0")

            if car_mens[i]==None:
                band_vac_mens.append("-1")
            else:
                band_vac_mens.append("0")

            if car_tit[i]==None:
                band_vac_tit.append("-1")
            else:
                band_vac_tit.append("0")

            if car_dif[i]==None:
                band_vac_dif.append("-1")
            else:
                band_vac_dif.append("0")

            if car_tipo_dif[i]==None:
                band_vac_tipo_dif.append("-1")
            else:
                band_vac_tipo_dif.append("0") 

        if (("-1" in band_vac_circ) or ("-1" in band_vac_sec) or ("-1" in band_vac_manz) or ("-1" in band_vac_parc) or ("-1" in band_vac_fecha_mens) or ("-1" in band_vac_mens) or ("-1" in band_vac_tipo_dif) or ("-1" in band_vac_tit) or ("-1" in band_vac_dif) or ("-1" in band_vac_partida) or ("-1" in band_vac_num_plano)):
            
            validaciones_caratula.loc[3,'Resultado']=-1
            validaciones_caratula.loc[3,'Observacion']="ERROR: Existen campos vacios en las caratulas insertas"
            validaciones_caratula.loc[3,'Cetegoría']='Caratula'

        else:
            validaciones_caratula.loc[3,'Resultado']=0
            validaciones_caratula.loc[3,'Observacion']="OK: Los campos de las caratulas se encuentran completos"
            validaciones_caratula.loc[3,'Cetegoría']='Caratula'

            #Genrea los patrones para comparar los campos cargados con lo que se espera#

            patron_circ = re.compile('^[0-9]{1,3}$')
            patron_sec = re.compile('^[0-9]{3}$')
            patron_maz_parc = re.compile(r'(^([0-9]{3})|([0-9]{3}[a-z]{1}))|(\D{3,}(\.)*(Plano|PLANO|plano)\D{0,})$')
            patron_fecha_mens = re.compile('^([0-9]{2}/[0-9]{4})|([0-9]{2}-[0-9]{4})$')
            patron_balance = re.compile(r'^[0-9]{1,}\.[0-9]{1,}$')
            patron_plano = re.compile('^[0-9]{4}$')

            #Genrea los patrones para comparar los campos cargados con lo que se espera#

            #Genera las banderas para guardar el resultado de la validacion de los patrones#

            band_pat_circ,band_pat_sec,band_pat_manz,band_pat_parc,band_pat_fecha_mens,band_pat_plano,band_pat_mens,band_pat_tit,band_pat_dif = list(),list(),list(),list(),list(),list(),list(),list(),list()

            #Genera las banderas para guardar el resultado de la validacion de los patrones#

            for i in range (len(bloque_caratula)):
                band_pat_circ.append(patron_circ.match(car_circ[i]))#recolecta como salio la validacion en las distintas caratulas para el campo circunscripión
                band_pat_sec.append(patron_sec.match(car_sec[i]))#recolecta como salio la validacion en las distintas caratulas para el campo sección
                band_pat_manz.append(patron_maz_parc.match(car_manz[i]))#recolecta como salio la validacion en las distintas caratulas para el campo manzana
                band_pat_parc.append(patron_maz_parc.match(car_parc[i]))          #recolecta como salio la validacion en las distintas caratulas para el campo parcela
                band_pat_fecha_mens.append(patron_fecha_mens.match(car_fecha_mens[i])) #recolecta como salio la validacion en las distintas caratulas para el campo feha mensura 
                band_pat_plano.append(patron_plano.match(car_num_plano[i]))
                band_pat_mens.append(patron_balance.match(car_mens[i]))
                band_pat_tit.append(patron_balance.match(car_tit[i]))
                band_pat_dif.append(patron_balance.match(car_dif[i]))


            
            if None in (band_pat_circ) or (None in band_pat_sec) or (None in band_pat_manz) or (None in band_pat_parc) or (None in band_pat_fecha_mens):
    ##                or (None in band_pat_plano)
                validaciones_caratula.loc[4,'Resultado']=-1
                validaciones_caratula.loc[4,'Observacion']="ERROR: Alguno de los campos Circ, Sec, Manz, Parc, fecha de mensura no se han completado correctamente"
                validaciones_caratula.loc[4,'Cetegoría']='Caratula'
            else:
                validaciones_caratula.loc[4,'Resultado']=0
                validaciones_caratula.loc[4,'Observacion']="OK: Los campos Circ, Sec, Manz, Parc, fecha de mensura se han completado correctamente"
                validaciones_caratula.loc[4,'Cetegoría']='Caratula'

            if None in (band_pat_mens) or (None in band_pat_tit) or (None in band_pat_dif):
                validaciones_caratula.loc[5,'Resultado']=-1
                validaciones_caratula.loc[5,'Observacion']='ERROR: Alguno de los campos del balance de superficie no son numericos o se utilizó un separador distinto de "."'
                validaciones_caratula.loc[5,'Cetegoría']='Caratula'

                validaciones_caratula.loc[6,'Resultado']=99
                validaciones_caratula.loc[6,'Observacion']='ERROR: No se puede validar el balance porque los campos completados no son numericos o se utilizó un separador distinto de "."'
                validaciones_caratula.loc[6,'Cetegoría']='Caratula'

                validaciones_caratula.loc[7,'Resultado']=99
                validaciones_caratula.loc[7,'Observacion']='ERROR: No se puede validar el balance porque los campos completados no son numericos o se utilizó un separador distinto de "."'
                validaciones_caratula.loc[7,'Cetegoría']='Caratula'

                validaciones_caratula.loc[8,'Resultado']=99
                validaciones_caratula.loc[8,'Observacion']='ERROR: No se puede validar el balance porque los campos completados no son numericos o se utilizó un separador distinto de "."'
                validaciones_caratula.loc[8,'Cetegoría']='Caratula'
            
            else:
                validaciones_caratula.loc[5,'Resultado']=0
                validaciones_caratula.loc[5,'Observacion']="OK: Los campos del Balance de superficie se completaron correctamente"
                validaciones_caratula.loc[5,'Cetegoría']='Caratula'

                band_dif_sup=list()
                band_men_tit = list()


                for i in range (len(car_mens)):
                    sup_men = car_mens[i]
                        
                    if abs(float(sup_mens_poly) - float(sup_men)) <= 0.01: #evalua que la supericie que puso como sup. de mensura en el balance de la primer caratula no difiera mas de 1cm2 de la suma de todos los poligonos de parcela y cesiones
                        band_dif_sup.append('0')
                    else:
                        band_dif_sup.append('-1')

                        

                if '-1' in band_dif_sup:
                    validaciones_caratula.loc[6,'Resultado']=-1
                    validaciones_caratula.loc[6,'Observacion']='ERROR: La superficie según mensura del balance de alguna de las caratulas no coincide con la suma de las supercicies de los poligonos Parcelas y Cesiones o no se ha podido validar por no ser un nmero'
                    validaciones_caratula.loc[6,'Cetegoría']='Caratula'
                else:
                    validaciones_caratula.loc[6,'Resultado']=0
                    validaciones_caratula.loc[6,'Observacion']='OK: La superficie según mensura del balance coincide con la superficie de los polignos los poligonos Parcelas y Cesiones'
                    validaciones_caratula.loc[6,'Cetegoría']='Caratula'

                for i in range (len(car_dif)):
                    
                    if abs(float(car_dif[i]) - abs((float(car_mens[i]) - float(car_tit[i]))))<=0.01:
                        band_men_tit.append("0")
                    else:
                        band_men_tit.append("-1")
                
                if "-1" in band_men_tit:
                    validaciones_caratula.loc[7,'Resultado']=-3
                    validaciones_caratula.loc[7,'Observacion']="ERROR: En la o alguna de las caratulas no coincide el valor indicado con la diferencia real entre las superficies según Mensura y título/plano"
                    validaciones_caratula.loc[7,'Cetegoría']='Caratula'
                else:
                    validaciones_caratula.loc[7,'Resultado']=0
                    validaciones_caratula.loc[7,'Observacion']="OK: El valor de la diferencia de superficie entre mensura y titulo se indicó correctamente en los valances de la/s caratula/s"
                    validaciones_caratula.loc[7,'Cetegoría']='Caratula'


                #<----- Valida que se haya colocado Diferenci en Menos Más o Excedente segúh corresponda------>#

                band_excedente,band_dif_mas,band_dif_menos, band_dif = list(),list(),list(),list()

                for i in range (len(car_mens)):
                    if (len(car_mens[i])>0) and (len(car_tit[i])>0):
                        if (float(car_mens[i]) - float(car_tit[i])) >= (0.05 * float(car_tit[i])):
                            if ("EXCEDENTE" in car_tipo_dif[i]) or ("Excedente" in car_tipo_dif[i]) or ("excedente" in car_tipo_dif[i]):
                                band_excedente.append("0")
                            else:
                                band_excedente.append("-1")
                        elif ((float(car_mens[i]) - float(car_tit[i])>=0)) and ((float(car_mens[i]) - float(car_tit[i]))<(0.05 * float(car_tit[i]))):
                            if ("MAS" in car_tipo_dif[i]) or ("Más" in car_tipo_dif[i]) or ("Mas" in car_tipo_dif[i]) or ("mas" in car_tipo_dif[i]):
                                band_dif_mas.append("0")
                            else:
                                band_dif_mas.append("-1")
                        elif (float(car_mens[i]) - float(car_tit[i])<0):
                            if ("Menos" in car_tipo_dif[i]) or ("menos" in car_tipo_dif[i]) or ("MENOS" in car_tipo_dif[i]):
                                band_dif_menos.append("0")
                            else:
                                band_dif_menos.append("-1")
                        elif ((float(car_mens[i]) - float(car_tit[i])==0)):
                            if ("Dif." in car_tipo_dif[i]) or ("Diferencia" in car_tipo_dif[i]) or ("DIFERENCIA" in car_tipo_dif[i]) or ("DIF." in car_tipo_dif[i]):
                                band_dif.append("0")
                            else:
                                band_dif.append("-1")
                    else:
                        validaciones_caratula.loc[8,'Resultado']=-1
                        validaciones_caratula.loc[8,'Observacion']="ERROR: Se han consignado valores negativos en la Sup. S/ Mensura o Sup S/ Tit."
                        validaciones_caratula.loc[8,'Cetegoría']='Caratula'
                    
                if ("-1" in band_excedente) or ("-1" in band_dif_menos) or ("-1" in band_dif_mas):
                    validaciones_caratula.loc[8,'Resultado']=-1
                    validaciones_caratula.loc[8,'Observacion']="ERROR: No coincide el Tipo de diferencia del balance (Diferencia, Diferencia en más, Diferencia en Menos, Excedente), con el valor de la dif. entre titulo y mensura del balance"
                    validaciones_caratula.loc[8,'Cetegoría']='Caratula'
                else:
                    validaciones_caratula.loc[8,'Resultado']=0
                    validaciones_caratula.loc[8,'Observacion']="OK: El tipo de diferencia declarada en el balance coincide con la diferencia de valor entre Mensura y Título"
                    validaciones_caratula.loc[8,'Cetegoría']='Caratula'

            if "1 DE 1" in car_hojas[0].upper():
                validaciones_caratula.loc[9,'Resultado']=0
                validaciones_caratula.loc[9,'Observacion']="OK: El/Los número/s de hoja/s de las caratulas se completó correctamente"
                validaciones_caratula.loc[9,'Cetegoría']='Caratula'
            else:
                validaciones_caratula.loc[9,'Resultado']=-1
                validaciones_caratula.loc[9,'Observacion']="ERROR: El/Los número/s de hoja/s de las caratulas deben ser correlativos, comenzar en 1 y coincidir con el total de caratulas insertas"
                validaciones_caratula.loc[9,'Cetegoría']='Caratula'
                    
                #<----- Valida que se haya colocado Diferenci en Menos Más o Excedente segúh corresponda------>#

        #verificar que los datos de los distintos atributos no esten vacios si estan vacios hacer alerta sino seguir verificando que los datos sean coherentes
    else:
        validaciones_caratula.loc[3,'Resultado']=-1
        validaciones_caratula.loc[3,'Observacion']="ERROR: No se han detectado caratulas en el plano"
        validaciones_caratula.loc[3,'Cetegoría']='Caratula'
        
        #FIN validar que la caratula tenga los atributos completos y que que sean coherentes excepto el balance que se valida mas adelante
    band_objeto_1 = list()
    band_objeto_2 = list()
    
    if len(bloque_caratula):
        for i in range(0,len(bloque_caratula)):
            for j in range(0,len(objetos_planos)):   
                if objetos_planos.loc[j,"Objetos"].lower() in car_objeto[i].lower():
                    band_objeto_1.append("0")
                else:
                    band_objeto_1.append("-1")
        if "0" in band_objeto_1:
            band_objeto_2.append("0")
        else:
            band_objeto_2.append("-1")
    else:
        pass

    if "-1" in band_objeto_2:
        validaciones_caratula.loc[10,'Resultado']=-1
        validaciones_caratula.loc[10,'Observacion']="ERROR: El Objeto del plano de la/s caratula/s no se corresponde con un objeto de plano aprobado por los reglamentos técnicos"
        validaciones_caratula.loc[10,'Cetegoría']='Caratula'
    else:
        validaciones_caratula.loc[10,'Resultado']=0
        validaciones_caratula.loc[10,'Observacion']="OK: Objeto de plano Correcto en la/s caratulas"
        validaciones_caratula.loc[10,'Cetegoría']='Caratula'
    
    return validaciones_caratula, bloque_caratula