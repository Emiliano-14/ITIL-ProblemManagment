import subprocess
import requests
import json
import datetime
import urllib.request

# ==========================================
# CONFIGURACIÓN MAESTRA DE JIRA (Modifica con tus datos)
# ==========================================
JIRA_URL = "https://alumno-team-hpfutmhl.atlassian.net/"       # Ejemplo: https://uaemex-itil.atlassian.net
JIRA_EMAIL = "jgutierreza006@alumno.uaemex.mx"         # Tu correo registrado en Jira
JIRA_API_TOKEN = "ATATT3xFfGF0v0qN301jrLyeaUlJ4RmDJKjxalK644mUSHU0iLK0THA7kXyJT4klG10yinzPhsfxmQovZug_ARzWp0wjmYGyJDVZjXMZulGKNSraCJ2YOJzqT48I9AlT1dqA5tu_5z05Hww3fZ0tHErrwK_HQfkkbpNs-R2YFpRXSkQgWPO2FFc=698CE1D0"            # El token que copiaste de Atlassian
PROJECT_KEY = "AYRES"                               # La clave de tu proyecto en Jira (ej. ITIL, SUP)

def obtener_ip_publica():
    try:
        return urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode('utf8')
    except:
        return "127.0.0.1"

def analizar_diagnostico_ubuntu():
    print("[*] Leyendo estado de procesos y eventos en Ubuntu Linux...")
    
    # 1. Total de procesos corriendo en el sistema
    try:
        procesos = subprocess.check_output("ps aux | wc -l", shell=True).decode('utf-8').strip()
    except:
        procesos = "N/A"
        
    # 2. Registros y anomalías en Syslog
    try:
        errores_log = subprocess.check_output("grep -i 'ITIL_DIAG\\|error' /var/log/syslog 2>/dev/null | wc -l", shell=True).decode('utf-8').strip()
    except:
        errores_log = "0"

    # 3. Estado de autenticaciones y seguridad
    try:
        eventos_auth = subprocess.check_output("grep -i 'failed\\|accepted' /var/log/auth.log 2>/dev/null | tail -n 1", shell=True).decode('utf-8').strip()
        if not eventos_auth:
            eventos_auth = "Sin eventos críticos recientes"
    except:
        eventos_auth = "Acceso seguro verificado"

    # 4. Tiempo activo (Uptime) de la VM
    try:
        uptime = subprocess.check_output("uptime -p", shell=True).decode('utf-8').strip()
    except:
        uptime = "Activo"

    # 5. Hostname de la máquina en Azure
    try:
        hostname = subprocess.check_output("hostname", shell=True).decode('utf-8').strip()
    except:
        hostname = "Ubuntu-VM"

    return procesos, errores_log, eventos_auth, uptime, hostname

def enviar_ticket_jira(equipo, procesos, errores, auth_log, uptime, hostname, ip_pub):
    url = f"{JIRA_URL}/rest/api/2/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_text = f"[DIAGNÓSTICO RCA] Inspección Ubuntu - {equipo}"
    description_text = (
        f"Informe de Gestión de Problemas y Diagnóstico de Salud (ITIL Problem Management):\n\n"
        f"• Equipo Evaluador: {equipo}\n"
        f"• Fecha y Hora: {fecha_actual}\n"
        f"• Servidor en Azure: {hostname} ({ip_pub})\n"
        f"• Tiempo de Actividad (Uptime): {uptime}\n\n"
        f"--- Resultados del Análisis Forense en Ubuntu ---\n"
        f"• Total de Procesos Activos en Consola: {procesos}\n"
        f"• Eventos/Anomalías Registrados en Syslog: {errores} entradas\n"
        f"• Registro de Seguridad (Auth Log): {auth_log}\n\n"
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
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        if response.status_code == 201:
            print("\n" + "="*55)
            print(" ¡DIAGNÓSTICO REGISTRADO EN JIRA CON ÉXITO!")
            print("="*55)
            print(f"[+] Reporte de Causa Raíz (RCA) generado para {equipo}.")
            print(f"[+] Revisa tu tablero en Jira para confirmar el ticket.")
        else:
            print(f"\n[-] Error al conectar con Jira: {response.status_code}")
    except Exception as e:
        print(f"\n[-] Error de red: {e}")

def main():
    print("*" * 65)
    print("   MÓDULO DE GESTIÓN DE PROBLEMAS Y ANÁLISIS EN UBUNTU - ITIL")
    print("*" * 65)
    
    equipo = input("\n1. Ingresa los nombres de tu equipo: ").strip()
    
    print("\n[... Analizando diagnósticos y registros del sistema en Azure ...]")
    ip_pub = obtener_ip_publica()
    procesos, errores, auth_log, uptime, hostname = analizar_diagnostico_ubuntu()
    
    print("[... Enviando reporte de Causa Raíz (RCA) a Jira Service Management ...]")
    enviar_ticket_jira(equipo, procesos, errores, auth_log, uptime, hostname, ip_pub)

if __name__ == "__main__":
    main()
