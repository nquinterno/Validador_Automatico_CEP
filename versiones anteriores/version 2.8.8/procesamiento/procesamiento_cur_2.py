from json import loads
import requests

def cur_parcela(smp):
    global resp_parc_datos_0
    global resp_parc_datos
    global band_cur_parcela


    band_cur_parcela = list()
    zonificacion = list()
    cur_afectaciones = list()


    # try:
    #     resp_parc_datos_0 = get(f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp[0]}",timeout=30)                            
    #     resp_parc_datos = loads(resp_parc_datos_0.text)
    #     band_cur_parcela.append("0")

    #     cur_aph = resp_parc_datos["catalogacion"]

    #     cur_dist_esp = resp_parc_datos["distrito_especial"]
    #     cur_unidad_edif = resp_parc_datos["unidad_edificabilidad"]
    #     cur_afectaciones_0 = resp_parc_datos["afectaciones"]

    #     for cur in cur_dist_esp:
    #         if len(cur["distrito_especifico"])>0:
    #             zonificacion.append(cur["distrito_especifico"])
    #         else:
    #             pass
        
    #     for edif in cur_unidad_edif:
    #         if edif == 38.0:
    #             zonificacion.append("C.A")
            
    #         elif edif == 31.2:
    #             zonificacion.append("C.M")
            
    #         elif edif == 22.8:
    #             zonificacion.append("U.S.A.A")
            
    #         elif edif == 17.2:
    #             zonificacion.append("U.S.A.M")

    #         elif edif == 11.6:
    #             zonificacion.append("U.S.A.B.2")

    #         elif edif == 9.0:
    #             zonificacion.append("U.S.A.B.1")
            
    #         else:
    #             pass
            
    #     if cur_afectaciones_0["riesgo_hidrico"]>0:
    #         cur_afectaciones.append("Riesgo Hídrico")
    #     else:
    #         pass
        
    #     if cur_afectaciones_0["lep"]>0:
    #         cur_afectaciones.append("Linea de Edificacion Particularizada")
    #     else:
    #         pass

    #     if cur_afectaciones_0["ensanche"]>0:
    #         cur_afectaciones.append("Afectación por Ensanche")
    #     else:
    #         pass
        
    #     if cur_afectaciones_0["apertura"]>0:
    #         cur_afectaciones.append("Afectación por Apertura")
    #     else:
    #         pass

    #     if cur_afectaciones_0["ci_digital"]>0:
    #         cur_afectaciones.append("Cinturon Digital")
    #     else:
    #         pass

    #     if (cur_aph["proteccion"] != None) and (cur_aph["proteccion"] != "DESESTIMADO") and cur_aph["proteccion"] !="" and cur_aph["proteccion"] !=" ": 
    #         aph = cur_aph["proteccion"]
    #     else:
    #         aph = "No"
        
    #     return zonificacion, cur_afectaciones, aph, band_cur_parcela

    # except:

    #     band_cur_parcela.append("-1")
    #     zonificacion = ""
    #     cur_afectaciones = ""
    #     aph = ""
    #     return zonificacion, cur_afectaciones, aph, band_cur_parcela
    


    try:
        # Aumentá el timeout (por ejemplo a 30 segundos)
        resp_parc_datos_0 = requests.get(
            f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp[0]}",
            timeout=30
        )

        resp_parc_datos = loads(resp_parc_datos_0.text)
        band_cur_parcela.append("0")

        cur_aph = resp_parc_datos["catalogacion"]
        cur_dist_esp = resp_parc_datos["distrito_especial"]
        cur_unidad_edif = resp_parc_datos["unidad_edificabilidad"]
        cur_afectaciones_0 = resp_parc_datos["afectaciones"]

        for cur in cur_dist_esp:
            if len(cur["distrito_especifico"]) > 0:
                zonificacion.append(cur["distrito_especifico"])

        for edif in cur_unidad_edif:
            if edif == 38.0:
                zonificacion.append("C.A")
            elif edif == 31.2:
                zonificacion.append("C.M")
            elif edif == 22.8:
                zonificacion.append("U.S.A.A")
            elif edif == 17.2:
                zonificacion.append("U.S.A.M")
            elif edif == 11.6:
                zonificacion.append("U.S.A.B.2")
            elif edif == 9.0:
                zonificacion.append("U.S.A.B.1")

        if cur_afectaciones_0["riesgo_hidrico"] > 0:
            cur_afectaciones.append("Riesgo Hídrico")

        if cur_afectaciones_0["lep"] > 0:
            cur_afectaciones.append("Linea de Edificacion Particularizada")

        if cur_afectaciones_0["ensanche"] > 0:
            cur_afectaciones.append("Afectación por Ensanche")

        if cur_afectaciones_0["apertura"] > 0:
            cur_afectaciones.append("Afectación por Apertura")

        if cur_afectaciones_0["ci_digital"] > 0:
            cur_afectaciones.append("Cinturon Digital")

        if (
            cur_aph["proteccion"] not in [None, "", " ", "DESESTIMADO"]
        ):
            aph = cur_aph["proteccion"]
        else:
            aph = "No"

        return zonificacion, cur_afectaciones, aph, band_cur_parcela

    except requests.exceptions.Timeout:
        # Caso específico: el servicio no respondió a tiempo
        print("no responde CUR parcela")
        band_cur_parcela.append("-1")

        zonificacion = ""
        cur_afectaciones = ""
        aph = ""
        return zonificacion, cur_afectaciones, aph, band_cur_parcela


    except Exception as e:
        # Cualquier otro error
        print("Error en la request:", e)
        band_cur_parcela.append("-1")
        zonificacion = ""
        cur_afectaciones = ""
        aph = ""
        return zonificacion, cur_afectaciones, aph, band_cur_parcela
    


#FIN CONSULTA CUR PARCELA