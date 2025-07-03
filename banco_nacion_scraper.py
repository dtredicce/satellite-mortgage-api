from playwright.sync_api import sync_playwright

def simulate_banco_nacion(data):
    valor_vivienda = data.get("valor_vivienda")
    monto_credito = data.get("monto_credito")
    plazo = data.get("plazo")
    uso = data.get("uso")

    destino_value = "adq_unica" if uso == "permanente" else "adq_segunda"

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for cobra_haberes in ["Si", "No"]:
            page.goto("https://bna.com.ar/Personas/SimuladorHipotecariosUva")

            page.wait_for_selector("#Destino", timeout=10000)
            page.select_option("#Destino", destino_value)
            page.fill("#ValorVivienda", str(valor_vivienda))
            page.select_option("#Plazo", str(plazo))
            page.fill("#Monto", str(monto_credito))
            page.select_option("#CobraHaberesBNA", cobra_haberes)
            page.select_option("#AdhiereOpcionTopeCVS", "No")

            page.get_by_role("button", name="Calcular").click()

            # Esperar a que aparezca el resultado o el mensaje de error
            page.wait_for_timeout(2000)  # Breve pausa para que se procese el cálculo

            error_element = page.query_selector('[data-valmsg-for="Monto"]')
            if error_element and error_element.inner_text().strip():
                error_msg = error_element.inner_text().strip()
                results.append({
                    "con_sueldo_en_banco": cobra_haberes == "Si",
                    "error": error_msg
                })
            else:
                # Esperar que los resultados estén visibles
                page.wait_for_selector("#cuota_pesos", timeout=10000)

                cuota = page.query_selector("#cuota_pesos").inner_text()
                tna = page.query_selector("#valor_tna").inner_text()
                cft = page.query_selector("#cft_tea").inner_text()
                ingresos = page.query_selector("#ingresos_necesarios_tit_cod").inner_text()

                results.append({
                    "con_sueldo_en_banco": cobra_haberes == "Si",
                    "cuota_pesos": cuota,
                    "tna": tna,
                    "cft_tea": cft,
                    "sueldo_requerido": ingresos,
                    "plazo_meses": int(plazo) * 12,
                    "monto_credito": monto_credito
                })

        browser.close()

    return results
