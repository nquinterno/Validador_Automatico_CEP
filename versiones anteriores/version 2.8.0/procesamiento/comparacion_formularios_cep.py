
import ezdxf
from pandas import DataFrame, read_excel, read_csv, eval
from procesamiento.catastroBox import medidaLadoPol, rumbo, sup_polilinea, polig_dentro_polig, discretizar_curva
from procesamiento.procesamiento_formularios import analisis_FOMUBI, analisis_IFDOM, analisis_IFFVN, analisis_IFTAM
from procesamiento.procesamiento_cur import cur_parcela
import difflib
from ezdxf.math.construct2d import is_point_in_polygon_2d, Vec2

def resumen(smp, pages_IFTAM_text, pages_IFFVN_text, pages_IFDOM_text,pages_FOMUBI_text,parcelas_poly,excedentes_poly,piso_con_mejoras, info_form_emp,info_form_nuevo,exp_layout, band_parc_arc, medidas_dxf, sup_cub_dxf, sup_semicub_dxf, sup_descub_dxf, sup_descont_dxf, band_mejora_cub_arc_0, band_mejora_semi_arc_0, band_mejora_desc_arc_0, band_mejora_emp_arc_0, band_mejora_nueva_arc_0, nom_parc_list):

    global validaciones_comparacion
    global validaciones
    global comparacion

    global resultado_final
    global filas_con_error
    global band_filas_error

    global sup_arc_parc

    validaciones_comparacion = DataFrame()

    formul_0 = list()
    info_form_nuevo_1 = list()
    notas_2 = list()
    band_notas = list()

    lados_iftam = list()
    smp_fomubi, exp_fomubi, mensura_3,plantas_3,cubierta_3,semi_3,des_3, cont_3 = "", "", "", "", "", "", "", "",

    cubierta_dxf = round(sum(sup_cub_dxf),2)
    semicubierta_dxf = round(sum(sup_semicub_dxf),2)
    descubierta_dxf = round(sum(sup_descub_dxf),2)
    
    sup_emp_dxf = 0
    sup_nueva_dxf = 0
    band_2 = list()
    band_agip_dxf = list()
    band_medida = list()

    #calcular superficie de parcela, sup excedente, sup total construida, sup no empadronada, sup empadronada.
    if len(parcelas_poly)>0:
        area_parc_dxf = sup_polilinea(parcelas_poly[0])
    else:
        area_parc_dxf = 0
 
    if len(excedentes_poly):
        #hacer lo mismo que con las construcciones
      area_excedente_dxf = round(ezdxf.math.area(Vec2.list(excedentes_poly[0].get_points('xy'))),2)
    else:
        area_excedente_dxf = round(0,2)

    for i in range (len(info_form_emp)): #calcula la superficie empadronada del archivo dxf
        sup_emp_dxf = sup_emp_dxf + info_form_emp[i]
    
    sup_emp_dxf = round(sup_emp_dxf,2)


    for i in range (len(info_form_nuevo)):
       formul_0.append((info_form_nuevo[i])['form'])

    formul = list(set(formul_0))

    for i in formul:

        lista = [indice for indice, dato in enumerate(info_form_nuevo) if dato['form'] == i]
        poligonos = ""
        sumar_sup = 0
        for k in range (len(lista)):
            poligonos = poligonos + "," + (info_form_nuevo[k])["polig"] #comprimir poligonos de los k
            sumar_sup = sumar_sup + float((info_form_nuevo[k])["sup"])

        poligonos = poligonos[1:]
        info_form_nuevo_1.append({"form":i,"polig":f"{poligonos}","sup":sumar_sup}) #comprime todas las superficies de un mismo formulario en un unico campo
        
        for i in range(len(info_form_nuevo_1)):
            sup_nueva_dxf = sup_nueva_dxf + info_form_nuevo_1[i]["sup"]

        sup_nueva_dxf = round(sup_nueva_dxf,2)

    plantas_dxf = len(piso_con_mejoras)

    #generar una lista de diccionarios en la cual este comprimida la suma de las superficies que corresponden al mismo formulario
        
    if len(pages_IFTAM_text)>0 and len(pages_IFFVN_text)>0 and len(pages_IFDOM_text)>0 and len(pages_FOMUBI_text)>0:
        
        resultado_iftam = analisis_IFTAM(pages_IFTAM_text)
        
        dif_agip, supdemo_3, agip_supnueva, agip_supexis = analisis_IFFVN(pages_IFFVN_text)
        
        dom_insc, dom_desc_1, dom_rest_1, dom_desig, dom_obs,sup_tit, dom_sup = analisis_IFDOM(pages_IFDOM_text)
        
        smp_fomubi, parc_fomubi, exp_fomubi, band_exp_fomubi = analisis_FOMUBI(pages_FOMUBI_text)

        #variables del form de mensura
        mensura_3 = resultado_iftam["sup_parc"]
        lados_iftam = resultado_iftam["deslinde"]
        cubierta_3 = resultado_iftam["sup_cub"]
        plantas_3 = resultado_iftam["cant_plantas"]
        semi_3 = resultado_iftam["sup_semicub"]
        des_3 = resultado_iftam["sup_desc"]
        notas_1 = resultado_iftam["notas"]
        particularidades = resultado_iftam["particularidades"]
        prec_3 = resultado_iftam["sup_prec"]
        cont_3 = resultado_iftam["sup_cont"]
        obs = resultado_iftam["obs"]
        tipo_ant = resultado_iftam["tipo_ant"]
        numero_ant = resultado_iftam["numero_ant"]

        zonificacion, cur_afectaciones, aph, band_cur_parcela = cur_parcela(smp)

        #variables del form de agip
        global agip_fechaconst


        #variables del form de dominio
        global band_text_style


        dif_mensura_dxf = round(area_parc_dxf - mensura_3,2)
        dif_plantas_dxf = plantas_dxf - plantas_3

        sup_cub_dxf_0 = cubierta_dxf
        sup_semicub_dxf_0 = semicubierta_dxf 
        sup_descub_dxf_0 = descubierta_dxf
        
        dif_cubierta_dxf = round(sup_cub_dxf_0,0) - round(cubierta_3,0)
        dif_semi_dxf = round(sup_semicub_dxf_0,0) - round(semi_3,0)
        dif_desc_dxf  = round(sup_descub_dxf_0,0) - round(des_3,0)

        
        notas_df = read_excel('configuracion/notas.xls')

        notas_comparar = dict(zip(notas_df.iloc[:, 0], notas_df.iloc[:, 1]))

        caracteres_eliminar = [",",".",";"]

        for char in caracteres_eliminar:
            for nota in notas_1:
                notas_2.append(nota.replace(char, "")) #elimina ".", "," y ";" de las notas cargadas por el prof y las guarda nota por nota en una lista

        for nota in notas_1:
            words1 = nota.split()
            for clave, valor in notas_comparar.items():
                words2 = valor.split()
                seq = difflib.SequenceMatcher(None, words1, words2)
                similarity = seq.ratio()
                if similarity >0.5:
                    band_notas.append(clave)
                else:
                    pass
                del words2
            del words1
       

        #validar que smp_fomubi sea igual a smp en el 33, si es igual validar que p del bloque parcela sea igual a parc_fomubi
        
        #validar que el exp_fomubi sea igual a exp del layout en el 34
        if len(smp)>0:

            if smp_fomubi == smp[0]:
                if parc_fomubi == nom_parc_list[0]: # completar con parcela del atributo de bloque de la parc
                    validaciones_comparacion.loc[0,'Resultado']=0
                    validaciones_comparacion.loc[0,'Observacion']="Ok: Coinciden las nomenclaturas de Caratula del Exp, Layout y bloque parc. surg"
                else:
                    validaciones_comparacion.loc[0,'Resultado']=-1
                    validaciones_comparacion.loc[0,'Observacion']="Error: No Coinciden las nomenclaturas de Caratula del Exp y del Layout"
            else:
                validaciones_comparacion.loc[0,'Resultado']=-1
                validaciones_comparacion.loc[0,'Observacion']="Error: No coincide la parcela del Layout y La caratula del Exp"
        else:
            validaciones_comparacion.loc[0,'Resultado']=-1
            validaciones_comparacion.loc[0,'Observacion']="Error: No se indico SMP en el layout de ficha catastral o no tiene el formato correcto ej: '003-134A-001b'"

        if band_exp_fomubi =="0":
            if exp_fomubi[:16] == exp_layout[:16]: # completar con la variable que tenga el numero de exp tomado del layout
                validaciones_comparacion.loc[1,'Resultado']=0
                validaciones_comparacion.loc[1,'Observacion']="Ok: Coinciden las nomenclaturas de Caratula del Exp, Layout y bloque parc. surg"
            else:
                validaciones_comparacion.loc[1,'Resultado']=-1
                validaciones_comparacion.loc[1,'Observacion']="Error: No Coincide el Expediente del tramite con el declarado en el layout"
        else:
            validaciones_comparacion.loc[1,'Resultado']=50
            validaciones_comparacion.loc[1,'Observacion']="Verificar: No se pudo Leer el número de Exp del Form. de ubic., verifique manualmente el exp del croquis de parcela"

        if abs(dif_mensura_dxf) > 0.01:
            if not("1" in band_parc_arc):
                validaciones_comparacion.loc[2,'Resultado']=-1
                validaciones_comparacion.loc[2,'Observacion']="Error: No coincide la Superficie de la Parcela en el dxf con la declarada en el formulario de Mensura"
            else:
                validaciones_comparacion.loc[2,'Resultado']=50
                validaciones_comparacion.loc[2,'Observacion']="Verificar: La parcela tiene lado curvo, verif. la sup. del form de mensura y la del dxf manualmente" 
        else:
            validaciones_comparacion.loc[2,'Resultado']=0
            validaciones_comparacion.loc[2,'Observacion']="Ok: Coinciden la Superficie de la Parcela en el dxf con la declarada en el formulario de Mensura"

        if dif_plantas_dxf != 0:
            validaciones_comparacion.loc[3,'Resultado']=-1
            validaciones_comparacion.loc[3,'Observacion']="Error: No coincide la N° de Plantas en las que se dibujó en el dxf con el N° de plantas declaradas en el form de mensura"
        else:
            validaciones_comparacion.loc[3,'Resultado']=0
            validaciones_comparacion.loc[3,'Observacion']="Ok: Coincide la N° de Plantas en las que se dibujó en el dxf con el N° de plantas declaradas en el form de mensura"

        if abs(dif_cubierta_dxf) > 0.01 and len(band_mejora_cub_arc_0)==0:
            validaciones_comparacion.loc[4,'Resultado']=-1
            validaciones_comparacion.loc[4,'Observacion']="Error: No coincide la Sup. Cubierta dibujada en el dxf con la superficie cubierta declarada en el form de mensura"
        
        elif abs(dif_cubierta_dxf) > 0.01 and len(band_mejora_cub_arc_0)!=0:
            validaciones_comparacion.loc[4,'Resultado']=50
            validaciones_comparacion.loc[4,'Observacion']="Verificar: Algun poligono cubierto o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        else:
            validaciones_comparacion.loc[4,'Resultado']=0
            validaciones_comparacion.loc[4,'Observacion']="Ok:Coincide la Sup. Cubierta dibujada en el dxf con la superficie cubierta declarada en el form de mensura"

        if abs(dif_semi_dxf) > 0.01 and len(band_mejora_semi_arc_0)==0:
            validaciones_comparacion.loc[5,'Resultado']=-1
            validaciones_comparacion.loc[5,'Observacion']="Error: No coincide la Sup. semicubierta dibujada en el dxf con la superficie semicubierta declarada en el form de mensura"
        
        elif abs(dif_semi_dxf) > 0.01 and len(band_mejora_semi_arc_0)!=0:
            validaciones_comparacion.loc[5,'Resultado']=50
            validaciones_comparacion.loc[5,'Observacion']="Verificar: Algun poligono semicub o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        
        else:
            validaciones_comparacion.loc[5,'Resultado']=0
            validaciones_comparacion.loc[5,'Observacion']="Ok: Coincide la Sup. Semicubierta dibujada en el dxf con la superficie semicubierta declarada en el form de mensura"

        if abs(dif_desc_dxf) > 0.01 and len(band_mejora_desc_arc_0)==0:
            validaciones_comparacion.loc[6,'Resultado']=-1
            validaciones_comparacion.loc[6,'Observacion']="Error: No coincide la Sup. descubierta dibujada en el dxf con la superficie descubierta declarada en el form de mensura"
        
        elif abs(dif_desc_dxf) > 0.01 and len(band_mejora_desc_arc_0)!=0:
            validaciones_comparacion.loc[6,'Resultado']=50
            validaciones_comparacion.loc[6,'Observacion']="Verificar: Algun poligono descub o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        
        else:
            validaciones_comparacion.loc[6,'Resultado']=0
            validaciones_comparacion.loc[6,'Observacion']="Ok: Coincide la Sup. descubierta dibujada en el dxf con la superficie descubierta declarada en el form de mensura"

        #Calcula cantidad de lados de la parcela, medidas de cada lado y contrastarlo con las medidas y cantidad de lados indicadas en el formulario de mensura

        if len(medidas_dxf) == len(lados_iftam):
            validaciones_comparacion.loc[7,'Resultado']=0
            validaciones_comparacion.loc[7,'Observacion']="Ok: Coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

            for lado in lados_iftam:
                for lado_dxf in medidas_dxf:
                    if (lado["medida"] == lado_dxf["medida"]) and (lado["rumbo"] == lado_dxf["rumbo"]):
                        band_medida.append('0')
                        break
                else:
                    pass

            if len(band_medida) == len(medidas_dxf):
                validaciones_comparacion.loc[8,'Resultado']=0
                validaciones_comparacion.loc[8,'Observacion']="Ok: Coinciden las medidas y/o rumbos de lados declarados en form de mensura con las de los lados de parcela dxf"
                
            else:
                validaciones_comparacion.loc[8,'Resultado']=-1
                validaciones_comparacion.loc[8,'Observacion']="Error: No coinciden las medidas y/o rumbos de lados declarados en form de mensura con las de los lados de parcela dxf"

            
        else:
            validaciones_comparacion.loc[7,'Resultado']=-1
            validaciones_comparacion.loc[7,'Observacion']="Error: No coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

            validaciones_comparacion.loc[8,'Resultado']=-1
            validaciones_comparacion.loc[8,'Observacion']="Error: No coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

        if cont_3 > 0:

            if ("contravencion" in band_notas):
                validaciones_comparacion.loc[9,'Resultado']=0
                validaciones_comparacion.loc[9,'Observacion']="Ok: Se detectó nota de Superficie en contravención de los RT en el Campo 'Notas' del Form. de Mensura"
            else:
                if "no_plano" in  band_notas:
                    validaciones_comparacion.loc[9,'Resultado']=-1
                    validaciones_comparacion.loc[9,'Observacion']="Error: Se detectó nota de inexistencia de plano en antecedentes y se declaro sup. en contravención > 0"
                else:
                    validaciones_comparacion.loc[9,'Resultado']=-1
                    validaciones_comparacion.loc[9,'Observacion']="Error: No se detectó nota de Superficie en contravención de los RT en el Campo 'Notas' del Form. de Mensura"
        else:
            if ("contravencion" in band_notas):
                validaciones_comparacion.loc[9,'Resultado']=-1
                validaciones_comparacion.loc[9,'Observacion']="Error: Se detectó nota de Superficie en contravención en el Campo 'Notas' del Form. de Mensura y si declaró valor '0'"
            else:
                validaciones_comparacion.loc[9,'Resultado']=99
                validaciones_comparacion.loc[9,'Observacion']="Ok: No corresponde validar nota de Superficie en contravención por no haberse declarado la misma"

        if (mensura_3 - sup_tit) >0:
            if (mensura_3 - sup_tit) > (0.05 * sup_tit):

                if ("excedente" in band_notas) and not(len(excedentes_poly)>0): 

                    validaciones_comparacion.loc[10,'Resultado']=-1
                    validaciones_comparacion.loc[10,'Observacion']="Error: Se ha detectado nota de Excedente de los en 'Notas' del form. de Mensura y NO se dibujo el excedente"
                
                elif ("excedente" in band_notas) and (len(excedentes_poly)>0):
                    validaciones_comparacion.loc[10,'Resultado']=0
                    validaciones_comparacion.loc[10,'Observacion']="Ok: Se ha detectado nota de Excedente de los en 'Notas' del form. de Mensura y se dibujo el excedente"
                
                elif ("tolerancia_mas" in band_notas) and (len(excedentes_poly)>0):
                    validaciones_comparacion.loc[10,'Resultado']=-1
                    validaciones_comparacion.loc[10,'Observacion']="Error: Se detecto nota de tolerancia en más  en 'Notas' del form. de Mensura y se dibujo el excedente"
                
                elif ("tolerancia_mas" in band_notas) and not(len(excedentes_poly)>0):
                    validaciones_comparacion.loc[10,'Resultado']=0
                    validaciones_comparacion.loc[10,'Observacion']="Ok: Se detecto nota de tolerancia en más en 'Notas' del form. de Mensura y No se dibujo el excedente"
                else:
                    validaciones_comparacion.loc[10,'Resultado']=-1
                    validaciones_comparacion.loc[10,'Observacion']="Error: No se ha detectado nota de Excedente ni superficie que supera la tolerancia en el campo 'Notas' del form.de Mensura"
            else:
                validaciones_comparacion.loc[10,'Resultado']=99
                validaciones_comparacion.loc[10,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"

        elif (mensura_3 - sup_tit) == 0:
            if ("excedente" in band_notas):
                validaciones_comparacion.loc[10,'Resultado']=-1
                validaciones_comparacion.loc[10,'Observacion']="Error: Mensura - Titulo = 0 y se declaro notas nota de excedente"
            elif ("tolerancia_mas" in band_notas):
                validaciones_comparacion.loc[10,'Resultado']=-1
                validaciones_comparacion.loc[10,'Observacion']="Error: Mensura - Titulo = 0 y se declaro  en notas, nota de tolerancia en más"
            else:
                validaciones_comparacion.loc[10,'Resultado']=99
                validaciones_comparacion.loc[10,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente ni sup. en menos"

        elif ((mensura_3 - sup_tit) < 0):

            if (abs((mensura_3 - sup_tit)) > (0.05 * sup_tit)):
                if "tolerancia_menos" in band_notas:
                    validaciones_comparacion.loc[10,'Resultado']=0
                    validaciones_comparacion.loc[10,'Observacion']="Ok: Se detectó nota de sup. en menos"
                else:
                    validaciones_comparacion.loc[10,'Resultado']=50
                    validaciones_comparacion.loc[10,'Observacion']="Verificar: Sup. s/título de form de dominio es mayor a sup en form de mensura (> al 5%) y no hay nota de sup en menos verifique que sup. s/titulo o notas"

            else:
                validaciones_comparacion.loc[10,'Resultado']=99
                validaciones_comparacion.loc[10,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"
        
        else:
            validaciones_comparacion.loc[10,'Resultado']=99
            validaciones_comparacion.loc[10,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"
            
        if "excedente" in (particularidades[0].lower().replace(" ","")):

            if "excedente_2" in band_notas:
                validaciones_comparacion.loc[11,'Resultado']=0
                validaciones_comparacion.loc[11,'Observacion']="Ok: En particularidades se declaró excedente y se indico nota del mismo en el campo 'Notas' del form. tecnico de Mensura"
            else:
                validaciones_comparacion.loc[11,'Resultado']=0
                validaciones_comparacion.loc[11,'Observacion']="Error: En particularidades se declaró excedente y no se indico nota del mismo en el campo 'Notas' del form. tecnico de Mensura"
        else:
            validaciones_comparacion.loc[11,'Resultado']=99
            validaciones_comparacion.loc[11,'Observacion']="Ok: En particularidades no se declaró excedente, no corresponde validar nota de excedente en form. técnico de Mensura"

        if dif_agip =="no":

            if "agip_nodif" in band_notas:
                validaciones_comparacion.loc[12,'Resultado']=0
                validaciones_comparacion.loc[12,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                
                validaciones_comparacion.loc[13,'Resultado']=0
                validaciones_comparacion.loc[13,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
            
            else:
                if "cep_demolicion" in band_notas:
                    validaciones_comparacion.loc[12,'Resultado']=0
                    validaciones_comparacion.loc[12,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota de Cep demolicion en el campo notas del form. tecnico de mensura"

                    validaciones_comparacion.loc[13,'Resultado']=0
                    validaciones_comparacion.loc[13,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota de Cep demolicion en el campo notas del form. tecnico de mensura"
                else:
                    validaciones_comparacion.loc[12,'Resultado']=-1
                    validaciones_comparacion.loc[12,'Observacion']="Error: se declaró que no difiere con agip y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"

                    validaciones_comparacion.loc[13,'Resultado']=-1
                    validaciones_comparacion.loc[13,'Observacion']="Error: se declaró que no difiere con agip y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
        elif dif_agip =="si":

            if supdemo_3>0:
                if "agip_dif_menos" in band_notas:
                    validaciones_comparacion.loc[12,'Resultado']=0
                    validaciones_comparacion.loc[12,'Observacion']="Ok: se declaró que difiere con agip, superficie demolida y se detectó la nota correspondiente en el campo notas del form. tecnico de mensura"
                else:
                    validaciones_comparacion.loc[12,'Resultado']=-1
                    validaciones_comparacion.loc[12,'Observacion']="Error: se declaró que difiere con agip, superficie demolida y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
            else:
                validaciones_comparacion.loc[12,'Resultado']=99
                validaciones_comparacion.loc[12,'Observacion']="Ok: No corresponde validar nota de demolicion por no haberse declarado la misma en el form resumen"

            if len(agip_supnueva)>0:

                if sum(agip_supnueva)>0:
                    if "agip_dif_mas" in band_notas:
                        validaciones_comparacion.loc[13,'Resultado']=0
                        validaciones_comparacion.loc[13,'Observacion']="Ok: se declaró que difiere con agip, superficie nueva y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                    else:
                        validaciones_comparacion.loc[13,'Resultado']=-1
                        validaciones_comparacion.loc[13,'Observacion']="Error: se declaró que difiere con agip, superficie nueva y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                else:
                    validaciones_comparacion.loc[13,'Resultado']=99
                    validaciones_comparacion.loc[13,'Observacion']="Ok: No corresponde validar nota de superficie a empadronar por no haberse declarado superficie nueva en el from resumen"

            else:
                validaciones_comparacion.loc[13,'Resultado']=99
                validaciones_comparacion.loc[13,'Observacion']="Ok: se declaró que difiere con agip, y no se indicó ningun valor en el campo sup. nueva en el form. resumen"  
      
        else:
            validaciones_comparacion.loc[12,'Resultado']=-1
            validaciones_comparacion.loc[12,'Observacion']="Error: no se puede validar nota de agip por no haberse completado si difere o no con agip las construcciones relevadas"
            
            validaciones_comparacion.loc[13,'Resultado']=-1
            validaciones_comparacion.loc[13,'Observacion']="Error: no se puede validar nota de agip por no haberse completado si difere o no con agip las construcciones relevadas"
        
        if "-1" in band_cur_parcela:
            validaciones_comparacion.loc[14,'Resultado']=-1
            validaciones_comparacion.loc[14,'Observacion']="Error: No se puede comprobar APH y afectaciones de la parcela por no poder conectarse con Ciudad 3d, verifique conexión de internet"
        else:
            if "cep_demolicion" in band_notas:
                if aph != "No":
                    validaciones_comparacion.loc[14,'Resultado']=-1
                    validaciones_comparacion.loc[14,'Observacion']="Error: Se ha declarado CEP Demolición y la parcela esta afectada a APH"

                else:
                    validaciones_comparacion.loc[14,'Resultado']=0
                    validaciones_comparacion.loc[14,'Observacion']="Ok: Se ha declarado CEP Demolición y la parcela no esta afectada a APH"

            else:
                validaciones_comparacion.loc[14,'Resultado']=0
                validaciones_comparacion.loc[14,'Observacion']="Ok: No se ha declarado CEP Demolición"

            if aph != "No":
                if "aph" in band_notas:
                    validaciones_comparacion.loc[15,'Resultado']=0
                    validaciones_comparacion.loc[15,'Observacion']="Ok: Se ha indicado la Nota de Aph en formulario de Mensura"
                else:
                    validaciones_comparacion.loc[15,'Resultado']=-1
                    validaciones_comparacion.loc[15,'Observacion']="Error: No se ha indicado la Nota de Aph en formulario de Mensura y la parcela se encuentra catalogada"
            else:
                if "aph" in band_notas:
                    validaciones_comparacion.loc[15,'Resultado']=-1
                    validaciones_comparacion.loc[15,'Observacion']="Error: Se ha indicado la Nota de Aph en formulario de Mensura, y la parcela no está catalogada"
                else:
                    validaciones_comparacion.loc[15,'Resultado']=99
                    validaciones_comparacion.loc[15,'Observacion']="Ok: No corresponde validar nota de Aph"
            
            if "Cinturon Digital" in cur_afectaciones:
                if "cinturón digital" in particularidades.lower():
                    #if "Cinturon Digital".lower().replace(" ","") in (notas_0[0].lower()):
                    if "cinturon_digital" in band_notas:
                        validaciones_comparacion.loc[16,'Resultado']=0
                        validaciones_comparacion.loc[16,'Observacion']="Ok: Se indicó nota de 'Cinturon Digital' en Notas del formulario de Mensura"
                    else:
                        validaciones_comparacion.loc[16,'Resultado']=-1
                        validaciones_comparacion.loc[16,'Observacion']="Error: No se indicó nota de 'Cinturon Digital' en Notas del formulario de Mensura"
                else:
                    validaciones_comparacion.loc[16,'Resultado']=-1
                    validaciones_comparacion.loc[16,'Observacion']="Error: No se indicó nota de 'Cinturon Digital' en Particularidades del formulario de Mensura"
            else:
                validaciones_comparacion.loc[16,'Resultado']=99
                validaciones_comparacion.loc[16,'Observacion']="Ok: No corresponde validar nota de 'Cinturon Digital'"

            if "Afectación por Apertura" in cur_afectaciones:
                if "afectación por apertura" in particularidades.lower():
                    #if "Afectación por Apertura".lower().replace(" ","") in (notas_0[0].lower()):
                    if "apertura" in band_notas:  
                        validaciones_comparacion.loc[17,'Resultado']=0
                        validaciones_comparacion.loc[17,'Observacion']="Ok: Se indicó nota de 'Afectación por Apertura' en Notas del formulario de Mensura"
                    else:
                        validaciones_comparacion.loc[17,'Resultado']=-1
                        validaciones_comparacion.loc[17,'Observacion']="Error: No se indicó nota de 'Afectación por Apertura' en Notas del formulario de Mensura"
                else:
                    validaciones_comparacion.loc[17,'Resultado']=-1
                    validaciones_comparacion.loc[17,'Observacion']="Error: No se indicó nota de 'Afectación por Apertura' en Particularidades del formulario de Mensura"
            else:
                validaciones_comparacion.loc[17,'Resultado']=99
                validaciones_comparacion.loc[17,'Observacion']="Ok: No corresponde validar nota 'Afectación por Apertura'"


            if "Afectación por Ensanche" in cur_afectaciones:
                if "afectación por ensanche" in particularidades.lower():
                    #if "Afectación por Ensanche".lower().replace(" ","") in (notas_0[0].lower()):
                    if "ensanche" in band_notas:
                        validaciones_comparacion.loc[18,'Resultado']=0
                        validaciones_comparacion.loc[18,'Observacion']="Ok: Se indicó nota de 'Afectación por Ensanche' en Notas del formulario de Mensura"
                    else:
                        validaciones_comparacion.loc[18,'Resultado']=-1
                        validaciones_comparacion.loc[18,'Observacion']="Error: No se indicó nota de 'Afectación por Ensanche' en Notas del formulario de Mensura"
                else:
                    validaciones_comparacion.loc[18,'Resultado']=-1
                    validaciones_comparacion.loc[18,'Observacion']="Error: No se indicó nota de 'Afectación por Ensanche' en Particularidades del formulario de Mensura"
            else:
                validaciones_comparacion.loc[18,'Resultado']=99
                validaciones_comparacion.loc[18,'Observacion']="Ok: No corresponde validar nota 'Afectación por Ensanche'"

            if "Linea de Edificacion Particularizada" in cur_afectaciones:
                if "linea de edificación particularizada" in particularidades.lower():
                    #if "Linea de Edificacion Particularizada".lower().replace(" ","") in (notas_0[0].lower()):
                    if "particularizada" in band_notas:
                        validaciones_comparacion.loc[19,'Resultado']=0
                        validaciones_comparacion.loc[19,'Observacion']="Ok: Se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Notas del formulario de Mensura"
                    else:
                        validaciones_comparacion.loc[19,'Resultado']=-1
                        validaciones_comparacion.loc[19,'Observacion']="Error: No se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Notas del formulario de Mensura"
                else:
                    validaciones_comparacion.loc[19,'Resultado']=-1
                    validaciones_comparacion.loc[19,'Observacion']="Error: No se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Particularidades del formulario de Mensura"
            else:
                validaciones_comparacion.loc[19,'Resultado']=99
                validaciones_comparacion.loc[19,'Observacion']="Ok: No corresponde validar nota 'Afectación por Linea de Edificacion Particularizada'"
            
            if "cep_demolicion" in band_notas:
                if  cubierta_3 != 0:
                    validaciones_comparacion.loc[20,'Resultado']=-1
                    validaciones_comparacion.loc[20,'Observacion']="Error: Se declaró CEP Demolición y se declaró Superficie cubierta distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[20,'Resultado']=0
                    validaciones_comparacion.loc[20,'Observacion']="Ok: Se declaró CEP Demolición y se declaró Superficie cubierta igual a 0 en el form de Mensura'"

                if semi_3 !=0:
                    validaciones_comparacion.loc[21,'Resultado']=-1
                    validaciones_comparacion.loc[21,'Observacion']="Error: Se declaró CEP Demolición y se declaró Superficie semicubierta distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[21,'Resultado']=0
                    validaciones_comparacion.loc[21,'Observacion']="Ok: Se declaró CEP Demolición y se declaró Superficie semicubierta igual a 0 en el form de Mensura'"

                if des_3 !=0:
                    validaciones_comparacion.loc[22,'Resultado']=-1
                    validaciones_comparacion.loc[22,'Observacion']="Error: Se declaró CEP Demolición y se declaró Superficie descubierta distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[22,'Resultado']=0
                    validaciones_comparacion.loc[22,'Observacion']="Ok: Se declaró CEP Demolición y se declaró Superficie descubierta igual a 0 en el form de Mensura'"

                if plantas_3 !=0:
                    validaciones_comparacion.loc[23,'Resultado']=-1
                    validaciones_comparacion.loc[23,'Observacion']="Error: Se declaró CEP Demolición y se declaró cantidad de plantas edificadas distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[23,'Resultado']=0
                    validaciones_comparacion.loc[23,'Observacion']="Ok: Se declaró CEP Demolición y se declaró cantidad de plantas edificadas igual a 0 en el form de Mensura'"
                
                if prec_3 !=0:
                    validaciones_comparacion.loc[24,'Resultado']=-1
                    validaciones_comparacion.loc[24,'Observacion']="Error: Se declaró CEP Demolición y se declaró sup. precaria distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[24,'Resultado']=0
                    validaciones_comparacion.loc[24,'Observacion']="Ok: Se declaró CEP Demolición y se declaró sup. precaria igual a 0 en el form de Mensura'"

                if cont_3 !=0:
                    validaciones_comparacion.loc[25,'Resultado']=-1
                    validaciones_comparacion.loc[25,'Observacion']="Error: Se declaró CEP Demolición y se declaró sup. en contravención distinta de 0 en el form de Mensura'"
                else:
                    validaciones_comparacion.loc[25,'Resultado']=0
                    validaciones_comparacion.loc[25,'Observacion']="Ok: Se declaró CEP Demolición y se declaró sup. en contravención igual a 0 en el form de Mensura'"
            else:
                    validaciones_comparacion.loc[20,'Resultado']=99
                    validaciones_comparacion.loc[20,'Observacion']="Ok: No corresponde validar sup cub = 0 dado que no se declaró CEP Demolición"
                    
                    validaciones_comparacion.loc[21,'Resultado']=99
                    validaciones_comparacion.loc[21,'Observacion']="Ok: No corresponde validar sup semicub = 0 dado que no se declaró CEP Demolición"

                    validaciones_comparacion.loc[22,'Resultado']=99
                    validaciones_comparacion.loc[22,'Observacion']="Ok: No corresponde validar sup descub = 0 dado que no se declaró CEP Demolición"

                    validaciones_comparacion.loc[23,'Resultado']=99
                    validaciones_comparacion.loc[23,'Observacion']="Ok: No corresponde validar cantidad de plantas = 0 dado que no se declaró CEP Demolición"

                    validaciones_comparacion.loc[24,'Resultado']=99
                    validaciones_comparacion.loc[24,'Observacion']="Ok: No corresponde validar sup precaria = 0 dado que no se declaró CEP Demolición"

                    validaciones_comparacion.loc[25,'Resultado']=99
                    validaciones_comparacion.loc[25,'Observacion']="Ok: No corresponde validar sup en contravencion = 0 dado que no se declaró CEP Demolición"

    else:
        validaciones_comparacion.loc[0,'Resultado']=-1
        validaciones_comparacion.loc[0,'Observacion']="Error: No es posible validar los formularios por no haberse cargado los mismos"

    ## Detección de que filas tienen error para poder saber si la admisibilidad da o no.
    filas_con_error = list()
    band_filas_error = list()


    return validaciones_comparacion,  lados_iftam, smp_fomubi, exp_fomubi,area_parc_dxf, area_excedente_dxf , sup_emp_dxf, sup_nueva_dxf, plantas_dxf,mensura_3,plantas_3,cubierta_3,semi_3,des_3, cont_3

