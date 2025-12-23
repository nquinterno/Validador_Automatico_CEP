from procesamiento.catastroBox import frente_parcela

def chequeo_ochava(doc, parcelas_poly_close, manzana_poly, titulo_poly):

    param_ochava = list()
    lado_ochava_parc = list()
    ochava_cur = list()
    frentes = list()
    
    #completar la lista de param ochava con el valor del angulo y la suma de los anchos de calle asociados a esa esquina, es una lista de diccionacios con los parametros s y ang. Donde s es la suma de los anchos de calle en esa esquina y ang es el angulo

    for lado in parcelas_poly_close[0].virtual_entities():
        if frente_parcela(lado,manzana_poly,0.20):
            frentes.append(lado)
        else:
            frentes.append("no")
            
    

    for i in range(len(param_ochava)):
        if (param_ochava[i])['s']<= 24:
            if (param_ochava[i])['ang'] < 75:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] <= 105:
                (param_ochava[i])['ochava'] = 7
            elif (param_ochava[i])['ang'] <= 135:
                (param_ochava[i])['ochava'] = 5
            elif (param_ochava[i])['ang'] > 135:

                (param_ochava[i])['ochava'] = 0
            else:
                pass
        elif (param_ochava[i])['s'] > 24 and (param_ochava[i])['s'] <= 42:
            
            if (param_ochava[i])['ang'] < 75:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] <= 105:
                (param_ochava[i])['ochava'] = 6
            elif (param_ochava[i])['ang'] <= 135:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] > 135:
                (param_ochava[i])['ochava'] = 0
            else:
                pass

        elif (param_ochava[i])['s'] > 42 and (param_ochava[i])['s'] <= 70:
            
            if (param_ochava[i])['ang'] < 75:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] <= 105:
                (param_ochava[i])['ochava'] = 5
            elif (param_ochava[i])['ang'] <= 135:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] > 135:
                (param_ochava[i])['ochava'] = 0
            else:
                pass

        elif (param_ochava[i])['s'] > 70:
            
            if (param_ochava[i])['ang'] < 75:
                (param_ochava[i])['ochava'] = 4
            elif (param_ochava[i])['ang'] <= 105:
                (param_ochava[i])['ochava'] = 0
            elif (param_ochava[i])['ang'] <= 135:
                (param_ochava[i])['ochava'] = 0
            elif (param_ochava[i])['ang'] > 135:
                (param_ochava[i])['ochava'] = 0
            else:
                pass


    return lado_ochava_parc, ochava_cur