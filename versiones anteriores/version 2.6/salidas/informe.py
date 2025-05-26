from pandas import DataFrame, eval
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt
from tkinter import messagebox, filedialog, ttk

def salida_pdf(validaciones2,parcelas_poly,parc_ant_posgba_2,manz_ant_posgba_2,smp,smp_fomubi,exp_layout,exp_fomubi, medidas_dxf, lados_iftam, cubierta_3, mensura_3, plantas_3, semi_3, des_3, cont_3,     area_parc_dxf, area_excedente_dxf, plantas_dxf, cubierta_dxf, semicubierta_dxf, descubierta_dxf, sup_emp_dxf, sup_nueva_dxf,version,resultado_final):

    validaciones3 = DataFrame(columns=['N°','Observacion'])
    enc = pdfencrypt.StandardEncryption(userPassword='',ownerPassword=None,canPrint=0, canModify=0, canAnnotate=0)

    for i in range(len(validaciones2)):
        validaciones3.loc[i,"N°"] = i
        validaciones3.loc[i,"Observacion"] = validaciones2.loc[i,"Observacion"]
        

    if len(validaciones3)>35:

        directorio = filedialog.askdirectory()
        if len(smp):
            c = canvas.Canvas(directorio + f"/validacion_dxf_{smp[0]}.pdf",pagesize=A4, encrypt = enc)
            smp_hoja = smp[0]
        else:
            c = canvas.Canvas(directorio + "/validacion_dxf_sinSMP.pdf",pagesize=A4, encrypt = enc)
            smp_hoja = "Sin SMP declarada"
        c.setFont("Times-Roman", 12)
        #Datos que se imprimiran en el pdf
        texto_encabezado=["Subgerencia Operativa de Registro de Mensura",
                          "Gerencia Operativa de Catastro Físico",
                          "Dirección General de Registro de Obras y Catastro"]

        #Impresión en canvas
        c.drawString(175, 800,  texto_encabezado[0])
        c.drawString(175, 780,  texto_encabezado[1])
        c.drawString(175, 760,  texto_encabezado[2])

        #Linea Separadora
        c.line(50, 740, 550, 740)

        c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela: {smp_hoja}")
        c.drawString(175, 700,  f"Validador Automatico Cep Versión {version}")

        
        if "Error:" in resultado_final:
            c.setFillColorRGB(1,0.62,0.62)
        else:
            c.setFillColorRGB(0.68,1,0.62)
        #dibuja rectangulo del fondo del texto de la validacion
        c.rect(190,675,250,20,stroke=1,fill=1)
        #cambia color a negro para el texto
        c.setFillColorRGB(0,0,0)
        c.setFont("Times-Roman", 10)
        c.drawString(200, 680,  f"{resultado_final}")

        #Encabezados de tabla
        c.drawString(20, 660, 'N°')
        c.drawString(50, 660, 'Observacion')

        #Filas de tabla
        i=int(640)
        c.setFont("Times-Roman", 9)
        c.setFillColorRGB(1,1,1)
        # for index, row in validaciones3.iterrows():
        for k in range (len(validaciones3)):
            if "Error:" in validaciones3.loc[k,'Observacion'] or "ERROR:" in validaciones3.loc[k,'Observacion'] or "error:" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(1,0.62,0.62)
            elif "Verificar:" in validaciones3.loc[k,'Observacion'] or "VERIFICAR:" in validaciones3.loc[k,'Observacion'] or "verificar" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(1,0.74,0.45)
            elif "OK" in validaciones3.loc[k,'Observacion'] or "Ok" in validaciones3.loc[k,'Observacion'] or "ok" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(0.68,1,0.62)
            else:
                c.setFillColorRGB(1,1,1)
            #dibuja rectangulo del fondo del texto de la validacion
            c.rect(18,i-5,565,20,stroke=1,fill=1)
            #cambia color a negro para el texto
            c.setFillColorRGB(0,0,0)
            #inserta el texto
            c.drawString(20, i, str(validaciones3.loc[k,'N°']))
            c.drawString(50, i, str(validaciones3.loc[k,'Observacion']))
            i-=20

            if i <= 20:
                c.showPage()
                i=int(660)

                #Impresión en canvas
                c.setFont("Times-Roman", 12)
                c.drawString(175, 800,  texto_encabezado[0])
                c.drawString(175, 780,  texto_encabezado[1])
                c.drawString(175, 760,  texto_encabezado[2])

                #Linea Separadora
                c.line(50, 740, 550, 740)
                
                c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela:{smp_hoja}")
                c.drawString(175, 700,  f"Validador Automatico Cep Versión {version}")
                if "Error:" in resultado_final:
                    c.setFillColorRGB(1,0.62,0.62)
                else:
                    c.setFillColorRGB(0.68,1,0.62)

                c.rect(190,675,250,20,stroke=1,fill=1)
                #cambia color a negro para el texto
                c.setFillColorRGB(0,0,0)
                c.setFont("Times-Roman", 10)
                c.drawString(200, 680,  f"{resultado_final}")

                #Encabezados de tabla
                c.drawString(20, 660, 'N°')
                c.drawString(50, 660, 'Observacion')

                #Filas de tabla
                i=640
                c.setFont("Times-Roman", 9)
                c.setFillColorRGB(1,1,1)
            else:
                pass
        
        c.showPage()
        #Impresión en canvas
        c.setFont("Times-Roman", 12)
        c.drawString(175, 800,  texto_encabezado[0])
        c.drawString(175, 780,  texto_encabezado[1])
        c.drawString(175, 760,  texto_encabezado[2])

        #Linea Separadora
        c.line(50, 740, 550, 740)
        
        c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela:{smp_hoja}")
        c.drawString(175, 700,  f"Validador Automatico Cep Versión {version}")
        #dibuja el rectangulo donde se dibujaran la mz y las parcelas
        c.setFillColorRGB(0,1,0)
        c.drawString(20,680, "Mz. Ciudad3D")

        c.setFillColorRGB(1,0,0)
        c.drawString(225, 680, "Parcela Ciudad3D")

        c.setFillColorRGB(0,0,1)
        c.drawString(450, 680,  "Parcela Medida")

        c.rect(10,20,570,650,stroke=1,fill=0)
        c.setFont("Times-Roman", 12)
        centroide_area_pdf = (290,335)
        #calcular y dibujar parcelas y manzana en el pdf
        if manz_ant_posgba_2 and parc_ant_posgba_2 and parcelas_poly:
            #inicia los valores minimos y maximos de x e y en la primer coordenada
            
            #Convierte los poligonos de manzana y parcela traidos de cur3d y transformado en listas de coordenadas que s epuedan manejar
            manz_ant_posgba_5 = eval(manz_ant_posgba_2)
            parc_ant_posgba_5 = eval(parc_ant_posgba_2)
            manz_ant_posgba_6 = list()
            parc_ant_posgba_6 = list()
            for x in manz_ant_posgba_5:
               manz_ant_posgba_6.append((x[0][0],x[1][0]))
            
            for x in parc_ant_posgba_5:
                parc_ant_posgba_6.append((x[0][0],x[1][0]))

            parcela_points = parcelas_poly[0].get_points('xy')

            max_x = float(0)
            max_y = float(0)
            min_x = float(1000000000)
            min_y = float(1000000000)
            
            #compara todos los puntos y saca las valosres maximos y minimos de las coordendas x e y
            for point in manz_ant_posgba_6:
                max_x = max(max_x, point[0])
                max_y = max(max_y, point[1])
                min_x = min(min_x,point[0])
                min_y = min(min_y,point[1])
            
            #el espacio dispobible para dibujar es: 570 de ancho por 670 de alto 
            rect_manz = (max_x - min_x, max_y - min_y)

            rect_pdf = (550,630)

            #convierto el rectangulo que envuelve la manzana en unidades de puntos del pdf para poder calcular el factor de escala necesario para que entre completo

            # 1mm = 2.8346456692 ptos
            # 1m = 2834.6456692913 ptos
            # 1pto = 0.3527777777 mm
            conv = 2834.6456692913 #conversion de mtros a puntos
            rect_manz_convert = (rect_manz[0]*conv, rect_manz[1]*conv)
            
            #calcula el factor de escalado necesario para que el dibujo engre en "x" y el factor para que entre en "y"
            scale_x = rect_manz_convert[0]/rect_pdf[0]
            scale_y = rect_manz_convert[1]/rect_pdf[1]
            
            #setea el factor de escala como el mayor de los calculados, para asegurarnos de que la manzana entre completa en el pdf
            scale = max(scale_x, scale_y)*1.10

            rect_manz_2 = ((((max_x + min_x)/2)*conv/scale),(((max_y + min_y)/2)*conv/scale))

            #escalando las polilineas a unidades de pto
            mz_escalada = list()
            parc_ant_escalada = list()
            parc_medida_escalda = list()
            
            for point in manz_ant_posgba_6:
                mz_escalada.append(((point[0]*conv)/scale, (point[1]*conv)/scale))
                
            for point in parc_ant_posgba_6:
                parc_ant_escalada.append(((point[0]*conv)/scale, (point[1]*conv)/scale))
                            
            for point in parcela_points:
                parc_medida_escalda.append(((point[0]*conv)/scale, (point[1]*conv)/scale))
            
            # calculando centroide de la mz_escalada 
            sum_x = 0
            sum_y = 0
            for point in mz_escalada:
                sum_x = sum_x + point[0]
                sum_y = sum_y + point[1]
            puntos = len(mz_escalada)

            centroide_mz_escalada = (sum_x/puntos, sum_y/puntos)


            mover = (rect_manz_2[0]- centroide_area_pdf[0],rect_manz_2[1] - centroide_area_pdf[1]) 

            #calculando factor de traslado de polilineas escaladas para que se vean en el pdf en base al centroide de mz_escalada y del recuadro del pdf
            
            #aplicando factor de traslado a las polilineas
            mz_pdf = list()
            parc_ant_pdf = list()

            parc_medida_pdf = list()
            for point in mz_escalada:
                x = (point[0] - mover[0] , point[1] - mover[1])
                mz_pdf.append(x)

            for point in parc_ant_escalada:
                x = (point[0] - mover[0] , point[1] - mover[1])
                parc_ant_pdf.append(x)
                            
            for point in parc_medida_escalda:
                x = (point[0] - mover[0] , point[1] - mover[1])
                parc_medida_pdf.append(x)

            
            # dibujar poligonos en el pdf en colores distintos con las coordenadas calculadas
            
            c.setStrokeColorRGB(0,1,0)
            for i in range(0,len(mz_pdf)-1):
                c.line((mz_pdf[i])[0], (mz_pdf[i])[1], (mz_pdf[i+1])[0], (mz_pdf[i+1])[1])
            
            c.line((parc_ant_pdf[len(parc_ant_pdf)-1])[0], (parc_ant_pdf[len(parc_ant_pdf)-1])[1], (parc_ant_pdf[0])[0], (parc_ant_pdf[0])[1])
            
            c.setStrokeColorRGB(1,0,0)
            for i in range(0,len(parc_ant_pdf)-1):
                c.line((parc_ant_pdf[i])[0], (parc_ant_pdf[i])[1], (parc_ant_pdf[i+1])[0], (parc_ant_pdf[i+1])[1])
            c.line((parc_ant_pdf[len(parc_ant_pdf)-1])[0], (parc_ant_pdf[len(parc_ant_pdf)-1])[1], (parc_ant_pdf[0])[0], (parc_ant_pdf[0])[1])

            c.setStrokeColorRGB(0,0,1)
            for i in range(0,len(parc_medida_pdf)-1):
                c.line((parc_medida_pdf[i])[0], (parc_medida_pdf[i])[1], (parc_medida_pdf[i+1])[0], (parc_medida_pdf[i+1])[1])
            c.line((parc_medida_pdf[len(parc_medida_pdf)-1])[0], (parc_medida_pdf[len(parc_medida_pdf)-1])[1], (parc_medida_pdf[0])[0], (parc_medida_pdf[0])[1])

        else:
            c.drawString(20,centroide_area_pdf[1], "No es posible representar la geometría de la Manzana y parcela por no haberse encontrado la misma")
            c.drawString(20,centroide_area_pdf[1]-20,"en Ciudad 3D y/o no haberse representado la parcela mensurada en el layer M-M-PARCELA")
        
        c.showPage()
        #Impresión en canvas
        c.setFont("Times-Roman", 12)
        c.drawString(175, 800,  texto_encabezado[0])
        c.drawString(175, 780,  texto_encabezado[1])
        c.drawString(175, 760,  texto_encabezado[2])

        #Linea Separadora
        c.line(50, 740, 550, 740)
        
        c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela:{smp_hoja}")
        c.drawString(175, 700,  f"Validador Automatico Cep Versión {version}")

        try: 
            mensura_3
        except:
            mensura_3 = "No se cargo Form Mensura"
        
        try:
            plantas_3
        except:
            plantas_3 = "No se cargo Form Mensura"

        try:
            cubierta_3
        except:
            cubierta_3 = "No se cargo Form Mensura"

        try:
            semi_3
        except:
            semi_3 = "No se cargo Form Mensura"

        try: 
            des_3
        except:
            des_3 = "No se cargo Form Mensura"

        try:
            cont_3
        except:
            cont_3 = "No se cargo Form Mensura"

        c.setStrokeColorRGB(0,0,0)

        k1 = 10
        a1 = 130
        b1 = a1+k1
        c1 = 215
        d1 = b1 + c1

        c.rect(k1,675,a1,20,stroke=1,fill=0)
        c.rect(b1,675,c1,20,stroke=1,fill=0)
        c.rect(d1,675,c1,20,stroke=1,fill=0) 
        
        c.drawString(k1+10, 680, 'Variable')
        c.drawString(b1+10, 680, 'Valor Según DXF')
        c.drawString(d1+10, 680, 'Valor Según Formulario')

        c.rect(k1,655,a1,20,stroke=1,fill=0)
        c.rect(b1,655,c1,20,stroke=1,fill=0)
        c.rect(d1,655,c1,20,stroke=1,fill=0)        
        
        c.drawString(k1+10, 660, 'SMP')
        c.drawString(b1+10, 660, f'{smp_hoja}')
        try:
            c.drawString(d1+10, 660, f'{smp_fomubi}')
        except:
            c.drawString(d1+10, 660, f'No se cargo form. de ubic.')

        c.rect(k1,635,a1,20,stroke=1,fill=0)
        c.rect(b1,635,c1,20,stroke=1,fill=0)
        c.rect(d1,635,c1,20,stroke=1,fill=0)           
        
        c.drawString(k1+10, 640, 'Expediente')
        c.drawString(b1+10, 640, f'{exp_layout}')
        try:
            c.drawString(d1+10, 640, f'{exp_fomubi}')
        except:
            c.drawString(d1+10, 640, f'No se cargo form. de ubic.')
        
        c.rect(k1,615,a1,20,stroke=1,fill=0)
        c.rect(b1,615,c1,20,stroke=1,fill=0)
        c.rect(d1,615,c1,20,stroke=1,fill=0)          
        
        c.drawString(k1+10, 620, 'Superficie Parcela')
        c.drawString(b1+10, 620, f'{area_parc_dxf}')
        c.drawString(d1+10, 620, f'{mensura_3}')

        c.rect(k1,595,a1,20,stroke=1,fill=0)
        c.rect(b1,595,c1,20,stroke=1,fill=0)
        c.rect(d1,595,c1,20,stroke=1,fill=0)    
        
        c.drawString(k1+10, 600, 'Superficie Excedente')
        c.drawString(b1+10, 600, f'{area_excedente_dxf}')
        c.drawString(d1+10, 600, f'-')

        
        c.rect(k1,575,a1,20,stroke=1,fill=0)
        c.rect(b1,575,c1,20,stroke=1,fill=0)
        c.rect(d1,575,c1,20,stroke=1,fill=0)  
        
        c.drawString(k1+10, 580, 'Cantidad de Plantas')
        c.drawString(b1+10, 580, f'{len(plantas_dxf)}')
        c.drawString(d1+10, 580, f'{plantas_3}')

        c.rect(k1,555,a1,20,stroke=1,fill=0)
        c.rect(b1,555,c1,20,stroke=1,fill=0)
        c.rect(d1,555,c1,20,stroke=1,fill=0)  
        
        c.drawString(k1+10, 560, 'Superficie cubierta')
        c.drawString(b1+10, 560, f'{round(sum(cubierta_dxf),2)}')
        c.drawString(d1+10, 560, f'{cubierta_3}')
        
        c.rect(k1,535,a1,20,stroke=1,fill=0)
        c.rect(b1,535,c1,20,stroke=1,fill=0)
        c.rect(d1,535,c1,20,stroke=1,fill=0)  
        
        c.drawString(k1+10, 540, 'Superficie Semicubierta')
        c.drawString(b1+10, 540, f'{round(sum(semicubierta_dxf),2)}')
        c.drawString(d1+10, 540, f'{semi_3}')
       
        c.rect(k1,515,a1,20,stroke=1,fill=0)
        c.rect(b1,515,c1,20,stroke=1,fill=0)
        c.rect(d1,515,c1,20,stroke=1,fill=0)  
        
        c.drawString(k1+10, 520, 'Superficie Descubierta')
        c.drawString(b1+10, 520, f'{round(sum(descubierta_dxf),2)}')
        c.drawString(d1+10, 520, f'{des_3}')
        
        c.rect(k1,495,a1,20,stroke=1,fill=0)
        c.rect(b1,495,c1,20,stroke=1,fill=0)
        c.rect(d1,495,c1,20,stroke=1,fill=0)  
        
        c.drawString(k1+10, 500, 'Superficie en Cont.')
        c.drawString(b1+10, 500, f'-')
        c.drawString(d1+10, 500, f'{cont_3}')

        
        c.rect(k1,475,a1,20,stroke=1,fill=0)
        c.rect(b1,475,c1,20,stroke=1,fill=0)
        c.rect(d1,475,c1,20,stroke=1,fill=0) 
        
        c.drawString(k1+10, 480, 'Superficie Empadronada')
        c.drawString(b1+10, 480, f'{sup_emp_dxf}')
        c.drawString(d1+10, 480, f'-')

        
        c.rect(k1,455,a1,20,stroke=1,fill=0)
        c.rect(b1,455,c1,20,stroke=1,fill=0)
        c.rect(d1,455,c1,20,stroke=1,fill=0) 
        
        c.drawString(k1+10, 460, 'Superficie a Empadronar')
        c.drawString(b1+10, 460, f'{sup_nueva_dxf}')
        c.drawString(d1+10, 460, f'-')

        c.rect(k1,245,a1,200,stroke=1,fill=0)
        c.rect(b1,245,c1,200,stroke=1,fill=0)
        c.rect(d1,245,c1,200,stroke=1,fill=0) 

        c.drawString(k1+10, 420, 'Medidas y Rumbos')
        for i in range (0, len(medidas_dxf), 2):
            c.drawString(b1+10, 440-(20*((i/2)+1)), f'{(medidas_dxf[i])["rumbo"]} - {(medidas_dxf[i])["medida"]}')
            
            try:
                c.drawString(b1+125, 440-(20*((i/2)+1)), f'{(medidas_dxf[i+1])["rumbo"]} - {(medidas_dxf[i+1])["medida"]}')
            
            except:
                pass
        try:
            for i in range (0,len(lados_iftam),2):
                c.drawString(d1+10, 440-(20*((i/2)+1)), f'{(lados_iftam[i])["rumbo"]} - {(lados_iftam[i])["medida"]}')
                
                try:
                    c.drawString(d1+125, 440-(20*((i/2)+1)), f'{(lados_iftam[i+1])["rumbo"]} - {(lados_iftam[i+1])["medida"]}')
                
                except:
                    pass
        except:
            c.drawString(d1+10, 420, f'No se cargo form de mensura')
            
        c.save() 
        print("Archivo PDF generado exitosamente en " + directorio)
                          
    else:
        print(messagebox.showerror(message="1° cargar dxf, 2° cargar formularios 3° procesar, 4° descargar pdf", title="Error"))

#funciones auxiliares