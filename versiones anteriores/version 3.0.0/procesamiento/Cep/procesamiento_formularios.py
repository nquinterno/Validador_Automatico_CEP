import re

def analisis_IFTAM(pages_IFTAM_text_0):

    global band_iftam_mensura
    global band_iftam_plantas
    global band_iftam_cubierta
    global band_iftam_semi
    global band_iftam_desc
    global band_iftam_prec
    global band_iftam_cont

    pages_IFTAM_text = (pages_IFTAM_text_0.replace("\n","")).replace("\xa0","")
    lados_iftam = list()
    notas_0 = list()

    if (re.search(r'Superficie Mts de la Parcela:\s*(\d+\,\d+)', pages_IFTAM_text))!=None:
        superficie_parcela = re.search(r'Superficie Mts de la Parcela:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif (re.search(r'Superficie Mts de la Parcela:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text))!=None:
        superficie_parcela = (re.search(r'Superficie Mts de la Parcela:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text)).group(1)
    else:
        pass


    deslinde = re.search(r'Descripción de la Parcela\s*(.*?)Particularidades', pages_IFTAM_text, re.DOTALL)
    

    if (re.search(r'Particularidades: (.*?)Cantidad de plantas: ', pages_IFTAM_text))!=None:
        particularidades_0 =  ((re.search(r'Particularidades: (.*?)Cantidad de plantas: ', pages_IFTAM_text)).group(1)).replace("\n", "")
    
    elif re.search(r'Particularidades\s*(.*?)\s*Cantidad de plantas:', pages_IFTAM_text) != None:

        particularidades_0 = (re.search(r'Particularidades\s*(.*?)\s*Cantidad de plantas:', pages_IFTAM_text).group(1)).replace("Particularidades: ","").replace("\n", "")
    
    else:
        particularidades_0 = "Error: No se pudo detectar"
    
    particularidades = (particularidades_0.replace("Particularidades: ","")).replace("Particularidades:","")
    
    if particularidades == "":
        particularidades = " "
    else:
        pass
        
    cantidad_de_plantas = re.search(r'Cantidad de plantas:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)


    if re.search(r'Superficie cubierta:\s*(\d+\,\d+)', pages_IFTAM_text)!=None:
        superficie_cubierta = re.search(r'Superficie cubierta:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif re.search(r'Superficie cubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text)!= None:
        superficie_cubierta = re.search(r'Superficie cubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text).group(1)
    else:
        pass

    if re.search(r'Superficie semicubierta:\s*(\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_semicubierta = re.search(r'Superficie semicubierta:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif re.search(r'Superficie semicubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_semicubierta = re.search(r'Superficie semicubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text).group(1)
    else:
        pass
    
    if re.search(r'Superficie descubierta:\s*(\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_descubierta = re.search(r'Superficie descubierta:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif re.search(r'Superficie descubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_descubierta = re.search(r'Superficie descubierta:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text).group(1)
    else:
        pass

    if re.search(r'Superficie en contravención:\s*(\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_contravencion = re.search(r'Superficie en contravención:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif re.search(r'Superficie en contravención:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text) != None:
        superficie_contravencion = re.search(r'Superficie en contravención:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text).group(1)
    else:
        pass
    if re.search(r'Superficie Precaria:\s*(\d+\,\d+)', pages_IFTAM_text) !=None:
        superficie_precaria = re.search(r'Superficie Precaria:\s*(\d+\,\d+)', pages_IFTAM_text).group(1)
    elif re.search(r'Superficie Precaria:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text) !=None:
        superficie_precaria = re.search(r'Superficie Precaria:\s*(\d+\.\d+\,\d+)', pages_IFTAM_text)
    else:
        pass
    tipo_ant = re.search(r'Tipo de antecedente:\s*(\S+)', pages_IFTAM_text).group(1)
    numero_ant = re.search(r'Numero de actuacion:\s*(\S+)', pages_IFTAM_text).group(1)
    notas = re.search(r'Notas:\s*(.*?)$', pages_IFTAM_text, re.DOTALL).group(1)
    obs  = re.search(r"Observaciones:\s*(.*?)\s*Notas", pages_IFTAM_text, re.DOTALL).group(1)

    #INICIO Capturar texto de superficie de la parcela

    mensura_1 = superficie_parcela.replace("\n","")
    mensura_2 = mensura_1.replace(".","")
    if len(mensura_2)>0:
        mensura_3 = float(mensura_2.replace(",","."))
    else:
        mensura_3 = 0
        band_iftam_mensura = "-1"

    #INICIO Capturar texto de superficie de la parcela

    #INICIO Capturar texto de Cantidad de plantas:

    plantas_1 = (cantidad_de_plantas.replace("\n","")).replace(" ","")
    plantas_2 = plantas_1.replace(",",".")
    if len(plantas_2)>0:
        plantas_3 = float(plantas_2)
    else:
        plantas_3 = 0
        band_iftam_plantas = "-1"

    #FIN Capturar texto de Cantidad de plantas:

    #INICIO Capturar texto de Superficie cubierta:

    cubierta_1 = superficie_cubierta.replace("\n","")
    cubierta_2 = cubierta_1.replace(".","")
    if len(cubierta_2) > 0:
        cubierta_3 = float(cubierta_2.replace(",","."))
    else:
        cubierta_3 = 0
        band_iftam_cubierta = "-1"

    #FIN Capturar texto de Superficie cubierta:

    #INICIO Capturar texto de superficie semicubierta

    semi_1 = superficie_semicubierta.replace("\n","")
    semi_2 = semi_1.replace(".","")
    if len(semi_2)>0:
        semi_3 = float(semi_2.replace(",","."))
    else:
        semi_3 = 0
        band_iftam_semi = "-1"

    # FIN Capturar texto de superficie semicubierta

    #INICIO Capturar texto de superficie Descubierta

    des_1 = superficie_descubierta.replace("\n","")
    des_2 = des_1.replace(".","")
    if len(des_2)>0:
        des_3 = float(des_2.replace(",","."))
    else:
        des_3 = 0
        band_iftam_desc = "-1"

    # FIN Capturar texto de superficie Descubierta

    #INICIO Capturar texto de superficie Precaria

    prec_1 = superficie_precaria.replace("\n","")
    prec_2 = prec_1.replace(".","")
    if len(prec_2)>0:
        prec_3 = float(prec_2.replace(",","."))
    else:
        prec_3 = 0
        band_iftam_prec= "-1"

    # FIN Capturar texto de superficie Precaria

    #INICIO Capturar texto de superficie en contravención

    cont_1 = superficie_contravencion.replace("\n","")
    cont_2 = cont_1.replace(".","")
    if len(cont_2)>0:
        cont_3 = float(cont_2.replace(",","."))
    else:
        cont_3 = 0
        band_iftam_cont= "-1"

    
    patron = r"Rumbo:.*?(?=(?:Rumbo:|Particularidades:))"
    lineas_deslinde = re.findall(patron, pages_IFTAM_text, re.DOTALL)

    #captura las medidas de la descripcion de la parcela en una lista
    regex = r"Medida:\s*([\d(,|.)]+)\s+Tipo de Lado"
    medidas_0 = re.findall(regex, pages_IFTAM_text)
    if len(medidas_0)>0:
        medidas = [float(medida.replace(",", ".")) for medida in medidas_0]
    else:
        pass
    
    if len(lineas_deslinde)>0:
        for linea in lineas_deslinde:
            medida_lado = ((re.findall(r"Medida:(.*?)Tipo de Lado:",linea,re.DOTALL)[0]).replace(" ","")).replace(",",".").replace("\xa0","")
            tipo_lado = (re.findall(r"Tipo de Lado:(.*?)Lindero:",linea,re.DOTALL)[0]).replace(" ","").replace("\xa0","")
            rumbo_lado = (re.findall(r"Rumbo:(.*?)Medida:",linea,re.DOTALL)[0]).replace(" ","").replace("\xa0","")
            lindero_lado = (re.findall(r"Lindero:(.*?)",linea,re.DOTALL)[0]).replace(" ","").replace("\xa0","")
            lados_iftam.append({"rumbo":rumbo_lado,"medida":float(medida_lado)})
    else:
        lados_iftam.append({})

    #capturar observaciones
    #capturar antededente tiopo y actuacion
    
    # for nota in notas:
    notas_0 = ((notas.replace("\n","")).replace("\xa0","")).lower()
    
    notas_1 = notas_0.split("notas:")
    
    resultado_iftam = {"sup_parc":mensura_3,"deslinde":lados_iftam,"particularidades":particularidades,"cant_plantas":plantas_3,"sup_cub":cubierta_3,"sup_semicub":semi_3,"sup_desc":des_3,"sup_prec":prec_3,"sup_cont":cont_3,"tipo_ant":tipo_ant,"numero_ant":numero_ant,"obs":obs,"notas":notas_1}

    return resultado_iftam
    # FIN Capturar texto de superficie en contravención

def analisis_IFFVN(pages_IFFVN_text_0):

    global agip_fechaconst
    global fechdemo

    agip_supnueva = list()
    agip_supexis = list()
    agip_sup_nueva_exis = list()
    supdemo_3 = 0
    fechdemo = ""
    agip_supexis_2 = list()
    agip_supnueva_2 = list()

    pages_IFFVN_text = pages_IFFVN_text_0.replace("\n","")

    #CAPTURAR SI DIFIERE CON AGIP

    dif_agip_0 = re.findall(r'¿Difiere con AGIP\?:\s*(.{2}\s*)',pages_IFFVN_text, re.DOTALL)[0]


    if "no" in dif_agip_0.lower():
        dif_agip = "no"
    
    elif "si" in dif_agip_0.lower(): 
        dif_agip = "si"
        
        #supdemo_2 = re.findall(r"Superficie Demolida:\s*(\d+,\d+)", pages_IFFVN_text)
        
        if (re.search(r'Superficie Demolida:\s*(\d+\,\d+)', pages_IFFVN_text))!=None:
            supdemo_2 = re.search(r'Superficie Demolida:\s*(\d+\,\d+)', pages_IFFVN_text).group(1)
        elif (re.search(r'Superficie Demolida:\s*(\d+\.\d+\,\d+)', pages_IFFVN_text))!=None:
            supdemo_2 = (re.search(r'Superficie Demolida:\s*(\d+\.\d+\,\d+)', pages_IFFVN_text)).group(1)
        else:
            supdemo_2 = "Error"
        
        if len(supdemo_2)>0 and supdemo_2 != "Error": 
            supdemo_3 = float((supdemo_2.replace(".","")).replace(",", "."))
        else:
            supdemo_3
        
        fechdemo = re.findall(r"Fecha de Demolición:\s*(\d{2}/\d{2}/\d{4})\s*", pages_IFFVN_text)[0]
        
        baldio_0 = re.findall(r'¿Es Terreno Baldío\?:\s*(.{2}\s*)',pages_IFFVN_text, re.DOTALL)[0]
        
        if "si" in baldio_0.lower():
            baldio = 'si'
            
            #supdemo_3 = float(re.findall(r"Superficie Demolida:\s*(\d+,\d+)", pages_IFFVN_text)[0].replace(",", "."))
            
            #fechdemo = re.findall(r"Fecha de Demolición:\s*(\d{2}/\d{2}/\d{4})\s*", pages_IFFVN_text)[0]
       
        elif "no" in baldio_0.lower():

            #captura toda la informcacion de los distintos for,ularios declarados y los alacena en una lista por cada campo capturado
            baldio = 'no'
            agip_polig_0 =  re.findall(r'Polígonos dentro del formulario:\s*(.*?)\s*Destino: ', pages_IFFVN_text)
            agip_destinos_0 = re.findall(r'Destino:\s*(.*?)\s*Superficie Exitente Destino:', pages_IFFVN_text)
            agip_supexis_0 = re.findall(r'Superficie Exitente Destino:\s*(.*?)\s*Superficie Nueva / Ampliada:', pages_IFFVN_text)
        

            agip_supnueva_0 = re.findall(r'Superficie Nueva / Ampliada:\s*(.*?)\s*Fecha de Construcción de Superficie nueva:', pages_IFFVN_text)
            agip_fechaconst = re.findall(r'Fecha de Construcción de Superficie nueva:\s*(.*?)\s*Refacción del Destino:', pages_IFFVN_text)

            for i in range (len(agip_supexis_0)):
                agip_supexis_1 = agip_supexis_0[i].replace(".","")
                agip_supexis_2.append(agip_supexis_1.replace(",","."))
                for i in range (len(agip_supexis_2)):
                    if len(agip_supexis_2[i])>0:
                        agip_supexis.append(float(agip_supexis_2[i]))
                    else:
                        agip_supexis.append(0)
                

                agip_supnueva_1 = agip_supnueva_0[i].replace(".","")
                agip_supnueva_2.append(agip_supnueva_1.replace(",","."))
                for i in range (len(agip_supnueva_2)):
                    if len(agip_supnueva_2[i])>0:
                        agip_supnueva.append(float(agip_supnueva_2[i]))
                    else:
                        agip_supnueva.append(0)
                agip_sup_nueva_exis.append({"sup_exist":agip_supexis,"sup_nueva":agip_supnueva})
        else:
            pass       
    else:
        pass
    
    return dif_agip, supdemo_3,agip_supnueva, agip_supexis
    
def analisis_IFDOM(pages_IFDOM_text):

    global sup_tit
    global inscripcion
    global dom_desc_0
    global dom_rest_0
    global dom_obs_0
    global dom_insc_0
    global dom_desig_0
    dom_sup = list()

    dom_insc_0 = list()
    dom_insc_1 = list()
    dom_insc = list()
    sup_tit = 0
    dom_desc_1 = list()
    dom_rest_1 = list()
    dom_desig = list()
    dom_obs = list()
    
    # print("pages_IFDOM_text 1",pages_IFDOM_text)
    # print("-------------------------------------------------")
    pages_IFDOM_text = pages_IFDOM_text.replace("\n","")

    # print("pages_IFDOM_text 2",pages_IFDOM_text)
    # print("-------------------------------------------------")


    # if len(re.findall(r'Superficie en mts 2: (.*?)Descripción según título:', pages_IFDOM_text)) !=0:
    #     dom_sup_0 =  re.findall(r'Superficie en mts 2: (.*?)Descripción según título:', pages_IFDOM_text)
    # elif len(re.findall(r'Superficie en mts 2:\s*(\d+\,\d+)', pages_IFDOM_text)) != 0:
    #     dom_sup_0 = re.findall(r'Superficie en mts 2:\s*(\d+\,\d+)', pages_IFDOM_text)
    # elif len(re.findall(r'Superficie en mts 2:\s*(\d+\.\d+\,\d+)', pages_IFDOM_text)) != 0:
    #     dom_sup_0 = re.findall(r'Superficie en mts 2:\s*(\d+\.\d+\,\d+)', pages_IFDOM_text)
    # else:
    #     dom_sup_0 = 0

    dom_sup_0 = re.findall(r'Superficie en mts 2:\s*([\d\.,]+)', pages_IFDOM_text)
                               
    # print ("dom_sup_0_raw",dom_sup_0)
    # print("-------------------------------------------------")

    # print ("dom_sup_0",dom_sup_0)
    # # dom_sup_0 =  re.findall(r'Superficie en mts 2: (.*?)Descripción según título:', pages_IFDOM_text)

    if len(re.findall(r'Descripción según título: (.*)Restiricciones y Afectaciones Inscriptas:', pages_IFDOM_text))!=0:
       dom_desc_0 = re.findall(r'Descripción según título: (.*)Restiricciones y Afectaciones Inscriptas:', pages_IFDOM_text)

    elif len(re.findall(r'Descripción según título:\s*(.*?)Restiricciones',pages_IFDOM_text))!=0:
        dom_desc_0 = re.findall(r'Descripción según título:\s*(.*?)Restiricciones',pages_IFDOM_text)

    else:
        dom_desc_0 = "Error: no se detecto"
    #dom_desc_0 = re.findall(r'Descripción según título: (.*)Restiricciones y Afectaciones Inscriptas:', pages_IFDOM_text)

    dom_rest_0 = re.findall(r'Restiricciones y Afectaciones Inscriptas:\s*(.*?)Observaciones:', pages_IFDOM_text)

    dom_obs_0 = re.findall(r'Observaciones:\s*(.*)\s*\¿Desea agregar otros datos de Dominio\?:', pages_IFDOM_text)

    #dom_insc_0 = re.findall(r'Descripción Folio protocolizado\n(.*?)\n\nDatos', pages_IFDOM_text)
    dom_insc_0 = re.findall(r'Detalle matrícula(.*?)Datos|Descripción Folio protocolizado(.*?)Datos', pages_IFDOM_text, re.DOTALL)

    dom_desig_0 = re.findall(r'Designación del bien según titulo:\s*(.*?)\s*Tipo de superficie de título:', pages_IFDOM_text)

    for i in range(len(dom_insc_0)): #limpia la lista de valores de dominio porque al leer el pdf se genera una lista de tuplas con valores basura ademas de la matricula o el tomo
        for dom in dom_insc_0[i]:
            if ("Matrícula:" in dom) or ("Tomo:" in dom):
                dom_insc_1.append(dom)
            else:
                pass

    for dom in dom_insc_1:
        dom_insc_2 = dom.replace("\n","")
        dom_insc.append(((dom_insc_2.replace(" ","")).replace("Matrícula:","")).replace("\xa0",""))

    for dom in dom_desc_0:
        dom_desc_1.append(dom)

    for dom in dom_rest_0:
        dom_rest_1.append(dom)
    
    for dom in dom_desig_0:
        dom_desig.append(dom)

    for dom in dom_obs_0:
        dom_obs.append(dom)
    


    for i in range(len(dom_sup_0)): #convierte los valores numericos en números y ajusta los campos de inscripcion (elimina comas y saltos de linea leidos)
        dom_sup_1 = (dom_sup_0[i].replace(".",""))
        if len(dom_sup_1)>0:
            dom_sup.append(float(dom_sup_1.replace(",",".")))
            sup_tit = sup_tit  + float(dom_sup_1.replace(",","."))
        else:
            sup_tit = 0
    print("sup_tit",sup_tit)
    return dom_insc, dom_desc_1, dom_rest_1, dom_desig, dom_obs,sup_tit, dom_sup 

def analisis_FOMUBI(pages_FOMUBI_text):

    exp_fomubi_0 = re.findall(r'EX-(.*?)- -GCABA-DGROC', pages_FOMUBI_text)

    seccion_0 = re.search(r'Sección:\s*(\d+)', pages_FOMUBI_text)
    manzana_0 = re.search(r'Manzana:\s*([\w\d]+)', pages_FOMUBI_text)
    parcela_0 = re.search(r'Parcela:\s*([\w\d]+)', pages_FOMUBI_text)

    if seccion_0:
        sec_fomubi = seccion_0.group(1)
    else:
        sec_fomubi = None

    if manzana_0:
        manz_fomubi = manzana_0.group(1)
    else:
        manz_fomubi = None

    if parcela_0:
        parc_fomubi_0 = parcela_0.group(1)
    else:
        parc_fomubi_0 = None

    
    if len(exp_fomubi_0):
        exp_fomubi = "EX-" + exp_fomubi_0[0] + "- -GCABA-DGROC"
        band_exp_fomubi = "0"
    else:
        exp_fomubi = "EX-" + "" + "- -GCABA-DGROC"
        band_exp_fomubi = "-1"

    smp_fomubi = sec_fomubi.replace("Manzana","") + "-" + manz_fomubi.replace("Parcela","") + "-" + parc_fomubi_0.replace("Unidad","")
    
    parc_fomubi = parc_fomubi_0.replace("Unidad","")
    
    return smp_fomubi, parc_fomubi, exp_fomubi, band_exp_fomubi
