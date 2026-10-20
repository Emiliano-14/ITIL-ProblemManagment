import subprocess
import requests
import json
import datetime
import urllib.request

# ===================================================
# CONFIGURACIÓN MAESTRA DE JIRA (Modifica con tus datos)
# ===================================================
JIRA_URL = "https://alumno-team-hpfutmhl.atlassian.net/"
JIRA_EMAIL = "jgutierreza006@alumno.uaemex.mx"
JIRA_API_TOKEN = "ATATT3xFfGF0v0qN301jrLyeaUlJ4RmDJKjxalK644mUSHU0iLK0THA7kXyJT4klG10yinzPhsfxmQovZug_ARzWp0wjmYGyJDVZjXMZulGKNSraCJ2YOJzqT48I9AlT1dqA5tu_5z05Hww3fZ0tHErrwK_HQfkkbpNs-R2YFpRXSkQgWPO2FFc=698CE1D0"
PROJECT_KEY = "AYRES"

def obtener_ip_publica():
    try:
        return urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode('utf8')
    except:
        return "127.0.0.1"

def analizar_diagnostico_ubuntu():
    print("[*] Leyendo estado de procesos y eventos en Ubuntu Linux...")
    try:
        procesos = subprocess.check_output("ps aux --sort=-%mem | head -n 6", shell=True).decode('utf-8').strip()
    except:
        procesos = "No disponible"

    try:
        errores_log = subprocess.check_output("grep -i 'error' /var/log/syslog | tail -n 5", shell=True).decode('utf-8').strip()
    except:
        errores_log = "Sin errores recientes en syslog"

    try:
        eventos_auth = subprocess.check_output("grep -i 'Failed' /var/log/auth.log | tail -n 5", shell=True).decode('utf-8').strip()
    except:
        eventos_auth = "Sin registros de fallos de autenticación"

    try:
        uptime = subprocess.check_output("uptime -p", shell=True).decode('utf-8').strip()
    except:
        uptime = "Desconocido"

    try:
        hostname = subprocess.check_output("hostname", shell=True).decode('utf-8').strip()
    except:
        hostname = "Ubuntu-VM"

    return procesos, errores_log, eventos_auth, uptime, hostname

def enviar_ticket_jira(equipo, procesos, errores, auth_log, uptime, hostname, ip_pub):
    url = f"{JIRA_URL}/rest/api/2/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    fecha_actual = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")

    summary_text = f"[DIAGNÓSTICO RCA] Inspección Ubuntu - {equipo}"
    description_text = (
        f"Informe de Gestión de Problemas y Diagnóstico de Salud (ITIL Problem Management):\n\n"
        f"• Equipo Evaluador: {equipo}\n"
        f"• Fecha y Hora: {fecha_actual}\n"
        f"• Servidor en Azure: {hostname} ({ip_pub})\n"
        f"• Tiempo de Actividad (Uptime): {uptime}\n\n"
        f"--- Resultados del Análisis Forense en Ubuntu ---\n"
        f"• Total de Procesos Activos en Consola:\n{procesos}\n\n"
        f"• Eventos/Anomalías Registrados en Syslog:\n{errores}\n\n"
        f"• Registro de Seguridad (Auth Log):\n{auth_log}\n\n"
        f"Diagnóstico ITIL: Inspección completada exitosamente. Se registra la causa raíz para prevención de problemas."
    )

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary_text,
            "description": description_text,
            "issuetype": {"name": "Task"}
        }
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code == 201:
        print("\n¡Ticket de RCA creado exitosamente en Jira!")
        print(f"Clave del Ticket: {response.json().get('key')}")
    else:
        print(f"\nError al crear el ticket en Jira: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("=== INICIANDO ANÁLISIS FORENSE E ITIL ===")
    equipo = input("1. Ingresa los nombres de tu equipo: ")

    print("Recopilando información del sistema...")
    ip_pub = obtener_ip_publica()
    procesos, errores, auth_log, uptime, hostname = analizar_diagnostico_ubuntu()

    print("Enviando reporte a Jira...")
    enviar_ticket_jira(equipo, procesos, errores, auth_log, uptime, hostname, ip_pub)
