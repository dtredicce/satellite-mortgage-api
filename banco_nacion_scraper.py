import asyncio
from playwright.sync_api import sync_playwright
import time

def simulate_banco_nacion(data):
    valor_vivienda = data.get("valor_vivienda")
    monto_credito = data.get("monto_credito")
    plazo = data.get("plazo")
    uso = data.get("uso")

    print(">>> Simulación Banco Nación")
    print(f"    - valor_vivienda: {valor_vivienda}")
    print(f"    - monto_credito: {monto_credito}")
    print(f"    - plazo: {plazo}")
    print(f"    - uso: {uso}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            print(">>> Abriendo página Banco Nación...")
            page.goto("https://www.bna.com.ar/Personas/SimuladorPrestamoUVACuotas", timeout=30000)

            # Completando campos
            print(">>> Completando formulario...")
            page.fill("#valorVivienda", str(valor_vivienda))
            page.fill("#montoCredito", str(monto_credito))
            page.fill("#plazo", str(plazo))

            if uso == "permanente":
                page.check("#tipoDestino1")
            else:
                page.check("#tipoDestino2")

            page.click("#btnSimular", timeout=10000)

            # Esperar resultado
            print(">>> Esperando resultado...")
            page.wait_for_selector(".resSimu", timeout=10000)

            cuotas = page.locator(".resSimu tbody tr")

            results = []
            for row in cuotas.all():
                tds = row.locator("td").all_inner_texts()
                results.append({
                    "linea": tds[0],
                    "cuota_inicial": tds[1],
                    "tna": tds[2],
                    "cftea": tds[3],
                    "ingreso_minimo": tds[4],
                    "monto_maximo": tds[5],
                })

            print(">>> Resultado extraído correctamente")
            return results

        except Exception as e:
            print(">>> ERROR durante simulación:", e)
            return {"error": str(e)}
        finally:
            try:
                browser.close()
            except:
                pass
