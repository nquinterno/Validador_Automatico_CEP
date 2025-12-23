import requests
import time


def cur_parcela(smp):
    """
    Consulta el servicio CUR 3D para una parcela (SMP)
    Devuelve:
        zonificacion: list[str]
        cur_afectaciones: list[str]
        aph: str
        band_cur_parcela: list[str]
    """

    url = f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp[0]}"

    max_intentos = 5
    tiempo_espera = 3
    timeout_segundos = 30

    print(f"Consultando CUR parcela para SMP {smp}...")

    # -----------------------------
    # Inicialización de salidas
    # -----------------------------
    zonificacion = []
    cur_afectaciones = []
    aph = "No"
    band_cur_parcela = []

    for intento in range(1, max_intentos + 1):
        try:
            # -----------------------------
            # REQUEST
            # -----------------------------
            resp = requests.get(url, timeout=timeout_segundos)
            print(f"HTTP Status: {resp.status_code}")
            resp.raise_for_status()

            # -----------------------------
            # PARSEO JSON
            # -----------------------------
            resp_parc_datos = resp.json()
            print("✔ Servicio respondió correctamente")

            band_cur_parcela.append("0")

            # -----------------------------
            # DATOS PRINCIPALES
            # -----------------------------
            cur_aph = resp_parc_datos.get("catalogacion", {})
            cur_dist_esp = resp_parc_datos.get("distrito_especial", [])
            cur_unidad_edif = resp_parc_datos.get("unidad_edificabilidad", [])
            cur_afectaciones_0 = resp_parc_datos.get("afectaciones", {})

            # -----------------------------
            # DISTRITO ESPECÍFICO
            # -----------------------------
            for cur in cur_dist_esp:
                distrito = cur.get("distrito_especifico")
                if distrito:
                    zonificacion.append(distrito)

            # -----------------------------
            # UNIDAD DE EDIFICABILIDAD
            # -----------------------------
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

            # Eliminar duplicados manteniendo orden
            zonificacion = list(dict.fromkeys(zonificacion))

            # -----------------------------
            # AFECTACIONES
            # -----------------------------
            if cur_afectaciones_0.get("riesgo_hidrico", 0) > 0:
                cur_afectaciones.append("Riesgo Hídrico")

            if cur_afectaciones_0.get("lep", 0) > 0:
                cur_afectaciones.append("Línea de Edificación Particularizada")

            if cur_afectaciones_0.get("ensanche", 0) > 0:
                cur_afectaciones.append("Afectación por Ensanche")

            if cur_afectaciones_0.get("apertura", 0) > 0:
                cur_afectaciones.append("Afectación por Apertura")

            if cur_afectaciones_0.get("ci_digital", 0) > 0:
                cur_afectaciones.append("Cinturón Digital")

            # -----------------------------
            # APH
            # -----------------------------
            proteccion = cur_aph.get("proteccion")
            if proteccion and proteccion not in ["", " ", "DESESTIMADO"]:
                aph = proteccion
            else:
                aph = "No"

            # -----------------------------
            # RETORNO EXITOSO
            # -----------------------------
            return zonificacion, cur_afectaciones, aph, band_cur_parcela

        # -----------------------------
        # ERRORES DE RED (REINTENTA)
        # -----------------------------
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red en intento {intento}/{max_intentos}")
            print(f"   Detalle: {e}")

            if intento < max_intentos:
                print(f"⏳ Reintentando en {tiempo_espera} segundos...")
                time.sleep(tiempo_espera)
            else:
                print("❌ Se agotaron los intentos por error de red")
                return [], [], "No", ["-1"]

        # -----------------------------
        # ERRORES DE LÓGICA / DATOS
        # -----------------------------
        except Exception as e:
            print("❌ Error procesando la respuesta del servicio")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Detalle: {e}")

            # No tiene sentido reintentar
            raise