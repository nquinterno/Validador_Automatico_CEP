
import requests
import time
import json
from json import loads

def cur_parcela(smp):


    url = f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp[0]}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0",
        "Accept": "*/*",
        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://ciudad3d.buenosaires.gob.ar/",
        "Origin": "https://ciudad3d.buenosaires.gob.ar",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=4"
    }

    max_intentos = 5
    tiempo_espera = 3
    timeout_segundos = 20

    print(f"Consultando CUR parcela para SMP {smp}...")

    # Inicialización para el return final
    zonificacion = ""
    cur_afectaciones = ""
    aph = ""
    band_cur_parcela = []

    for intento in range(1, max_intentos + 1):

        print(f"\n➡ Intento {intento}/{max_intentos}")

        try:
            # 1) REQUEST
            resp = requests.get(url, headers=headers, timeout=timeout_segundos)

            print(f"HTTP Status: {resp.status_code}")

            resp.raise_for_status()


            resp_parc_datos = loads(resp.text)

            print("resp_parc_datos:", resp_parc_datos)
            
            band_cur_parcela.append("0")

            cur_aph = resp_parc_datos["catalogacion"]
            cur_dist_esp = resp_parc_datos["distrito_especial"]
            cur_unidad_edif = resp_parc_datos["unidad_edificabilidad"]
            cur_afectaciones_0 = resp_parc_datos["afectaciones"]

            # --------------------
            # DISTRITO ESPECIFICO
            # --------------------
            for cur in cur_dist_esp:
                if len(cur["distrito_especifico"]) > 0:
                    zonificacion.append(cur["distrito_especifico"])

            # --------------------
            # UNIDADES DE EDIFICABILIDAD
            # --------------------
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

            # --------------------
            # AFECTACIONES
            # --------------------
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

            # --------------------
            # APH
            # --------------------
            if cur_aph["proteccion"] not in [None, "", " ", "DESESTIMADO"]:
                aph = cur_aph["proteccion"]
            else:
                aph = "No"

            print("✔ Servicio respondido correctamente.")

            return zonificacion, cur_afectaciones, aph, band_cur_parcela


        except Exception as e:
            print(f"❌ ERROR EN INTENTO {intento}")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Detalle: {e}")

            if intento < max_intentos:
                print(f"⏳ Reintentando en {tiempo_espera} segundos...")
                time.sleep(tiempo_espera)
            else:
                print("❌ Se agotaron todos los intentos. No hubo respuesta del servicio.\n")
                return "", "", "", ["-1"]