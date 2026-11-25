#!/usr/bin/env python3
import base64
import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

FLOWABLE_UI_BASE = "http://localhost:8080/flowable-ui"
PROCESS_API = f"{FLOWABLE_UI_BASE}/process-api"
IDM_API = f"{FLOWABLE_UI_BASE}/api/idm"
PROCESS_DEF_KEY = "curso5"


class FlowableClient:
    def __init__(self, username: str, password: str):
        self.username = username
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        self.auth_header = f"Basic {token}"

    def request(self, method: str, url: str, body=None):
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
        }
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8").strip()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace").strip()
            try:
                err_json = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                err_json = {"message": raw}
            return e.code, err_json
        except urllib.error.URLError as e:
            return 0, {"message": f"Error de conexión: {e.reason}"}


def autenticar() -> FlowableClient:
    print("=== 4.2.2 - Simulador de Comunicaciones de Empresa (API REST) ===")
    while True:
        user = input("Usuario Flowable [admin]: ").strip() or "admin"
        pwd = getpass.getpass("Clave: ").strip()
        if not pwd:
            print("Ingresá una clave válida.\n")
            continue

        client = FlowableClient(user, pwd)
        status, data = client.request("GET", f"{IDM_API}/users/{urllib.parse.quote(user)}")
        if status == 200:
            nombre = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip() or user
            print(f"\n[OK] Autenticado como {nombre} ({user}).\n")
            return client
        elif status == 401:
            print("[ERROR] Credenciales inválidas (401 Unauthorized).\n")
        elif status == 403:
            print("[ERROR] Usuario sin privilegio 'access-rest-api' (403 Forbidden).\n")
        else:
            print(f"[ERROR] HTTP {status}: {data.get('message', data)}\n")


def obtener_tareas_instancia(client: FlowableClient, proc_id: str) -> list:
    url = f"{PROCESS_API}/runtime/tasks?processInstanceId={urllib.parse.quote(proc_id)}&size=100"
    status, data = client.request("GET", url)
    if status == 200:
        return data.get("data", [])
    return []


def listar_solicitudes(client: FlowableClient) -> list:
    url = f"{PROCESS_API}/runtime/process-instances?processDefinitionKey={PROCESS_DEF_KEY}&size=100"
    status, data = client.request("GET", url)
    if status != 200:
        print(f"[ERROR] No se pudieron obtener las instancias (HTTP {status}): {data}")
        return []
    return data.get("data", [])


def listar_timer_jobs(client: FlowableClient, proc_id: str) -> list:
    url = f"{PROCESS_API}/management/timer-jobs?processInstanceId={urllib.parse.quote(proc_id)}&size=100"
    status, data = client.request("GET", url)
    if status == 200:
        return data.get("data", [])
    print(f"    [ERROR] No se pudieron consultar los timer jobs (HTTP {status}): {data}")
    return []


def normalizar_fecha_iso(fecha: str) -> str:
    limpia = fecha.strip().strip('"').strip("'")
    if re.search(r"(Z|[+-]\d{2}:\d{2})$", limpia):
        return limpia
    return f"{limpia}-03:00"


def simular_vencimiento_timer(client: FlowableClient, proc_id: str):
    timers = listar_timer_jobs(client, proc_id)
    if not timers:
        print("    [AVISO] No hay timer jobs activos para esta instancia.")
        return

    print("    Timer jobs activos:")
    for idx, t in enumerate(timers, start=1):
        print(f"      {idx}. ID: {t.get('id')} | Elemento: {t.get('elementName') or t.get('elementId')} | Vence: {t.get('dueDate')}")

    elegido = timers[0]
    job_id = elegido.get("id")
    url = f"{PROCESS_API}/management/timer-jobs/{urllib.parse.quote(job_id)}"
    status, resp = client.request("POST", url, {"action": "move"})

    if 200 <= status < 300:
        print(f"\n    [OK] Timer job {job_id} movido/disparado correctamente.\n")
    else:
        print(f"\n    [ERROR] No se pudo mover el timer job (HTTP {status}): {resp}\n")


def detectar_comunicaciones_habilitadas(client: FlowableClient, proc_id: str) -> list:
    url = f"{PROCESS_API}/runtime/executions?processInstanceId={urllib.parse.quote(proc_id)}&size=100"
    status, data = client.request("GET", url)
    if status != 200:
        print(f"[ERROR] No se pudieron consultar las ejecuciones (HTTP {status}): {data}")
        return []

    ejecuciones = data.get("data", [])
    habilitadas = []
    ya_agregadas = set()

    for ej in ejecuciones:
        exec_id = ej.get("id")
        act_id = ej.get("activityId") or ""

        if act_id == "Aceptar" and "ACEPTAR" not in ya_agregadas:
            ya_agregadas.add("ACEPTAR")
            habilitadas.append({
                "codigo": "ACEPTAR",
                "titulo": "Aceptación de la propuesta (incluyendo fecha acordada)",
                "executionId": exec_id,
                "messageName": "Aceptación",
            })
        elif act_id == "Rechazar" and "RECHAZAR" not in ya_agregadas:
            ya_agregadas.add("RECHAZAR")
            habilitadas.append({
                "codigo": "RECHAZAR",
                "titulo": "Rechazo de la propuesta",
                "executionId": exec_id,
                "messageName": "Rechazo",
            })
        elif act_id == "Modificar" and "MODIFICAR" not in ya_agregadas:
            ya_agregadas.add("MODIFICAR")
            habilitadas.append({
                "codigo": "MODIFICAR",
                "titulo": "Solicitud de modificaciones (incluyendo observaciones)",
                "executionId": exec_id,
                "messageName": "Solicitud de modificaciones",
            })
        elif act_id == "sid-9A2B39EC-DF21-46DF-9CF1-D622AB6187C4" and "NOMINA" not in ya_agregadas:
            ya_agregadas.add("NOMINA")
            habilitadas.append({
                "codigo": "NOMINA",
                "titulo": "Envío de la nómina de participantes",
                "executionId": exec_id,
                "messageName": "Nómina de participantes",
            })
        elif act_id == "Event_1g4xmqo" and "CANCELAR" not in ya_agregadas:
            ya_agregadas.add("CANCELAR")
            habilitadas.append({
                "codigo": "CANCELAR",
                "titulo": "Cancelación durante la preparación",
                "executionId": exec_id,
                "messageName": "Cancelación",
            })

    # Si el subproceso de evento Event_1g4xmqo no aparece como activityId explícito,
    # revisamos suscripciones de mensajes en las ejecuciones activas
    if "CANCELAR" not in ya_agregadas:
        for ej in ejecuciones:
            exec_id = ej.get("id")
            st_sub, sub_data = client.request("GET", f"{PROCESS_API}/runtime/executions/{exec_id}/subscriptions")
            if st_sub == 200 and isinstance(sub_data, list):
                for s in sub_data:
                    if s.get("eventType") == "message" and s.get("eventName") == "Cancelación":
                        ya_agregadas.add("CANCELAR")
                        habilitadas.append({
                            "codigo": "CANCELAR",
                            "titulo": "Cancelación durante la preparación",
                            "executionId": exec_id,
                            "messageName": "Cancelación",
                        })
                        break
            if "CANCELAR" in ya_agregadas:
                break

    return habilitadas


def ejecutar_comunicacion(client: FlowableClient, accion: dict):
    codigo = accion["codigo"]
    exec_id = accion["executionId"]
    msg_name = accion["messageName"]
    variables = []

    if codigo == "ACEPTAR":
        fecha_raw = input("Ingresá la fecha acordada (formato YYYY-MM-DDTHH:MM:SS[-03:00], ej: 2026-11-26T10:00:00-03:00): ").strip()
        if not fecha_raw:
            print("[AVISO] La fecha acordada es obligatoria.\n")
            return
        fecha = normalizar_fecha_iso(fecha_raw)
        variables = [
            {"name": "fechaInicioCurso", "type": "string", "value": fecha},
            {"name": "fechaInicio", "type": "string", "value": fecha},
            {"name": "respuestaEmpresa", "type": "string", "value": "aceptada"},
        ]

    elif codigo == "RECHAZAR":
        motivo = input("Motivo del rechazo (opcional): ").strip()
        variables = [
            {"name": "respuestaEmpresa", "type": "string", "value": "rechazada"},
        ]
        if motivo:
            variables.append({"name": "motivoRechazo", "type": "string", "value": motivo})

    elif codigo == "MODIFICAR":
        obs = input("Ingresá las observaciones para la modificación: ").strip()
        if not obs:
            print("[AVISO] Las observaciones son obligatorias para solicitar modificaciones.\n")
            return
        variables = [
            {"name": "respuestaEmpresa", "type": "string", "value": "modificaciones"},
            {"name": "observacionesModificacion", "type": "string", "value": obs},
        ]

    elif codigo == "NOMINA":
        nomina = input("Ingresá la nómina de participantes (ej: Juan Perez - 30111222, Ana Gomez - 32333444): ").strip()
        if not nomina:
            print("[AVISO] Debe ingresar al menos un participante en la nómina.\n")
            return
        variables = [
            {"name": "nominaParticipantes", "type": "string", "value": nomina},
            {"name": "nominaRecibida", "type": "boolean", "value": True},
        ]

    elif codigo == "CANCELAR":
        motivo = input("Motivo de cancelación durante la preparación (opcional): ").strip()
        variables = [
            {"name": "cursoCancelado", "type": "boolean", "value": True},
        ]
        if motivo:
            variables.append({"name": "motivoCancelacion", "type": "string", "value": motivo})

    payload = {
        "action": "messageEventReceived",
        "messageName": msg_name,
        "variables": variables,
    }

    url = f"{PROCESS_API}/runtime/executions/{urllib.parse.quote(exec_id)}"
    status, resp = client.request("PUT", url, payload)

    if 200 <= status < 300:
        print(f"\n[OK] Comunicación '{msg_name}' enviada correctamente sobre ejecución {exec_id}.\n")
    else:
        print(f"\n[ERROR] Flowable rechazó la comunicación (HTTP {status}): {resp}\n")


def main():
    client = autenticar()

    while True:
        solicitudes = listar_solicitudes(client)
        if not solicitudes:
            print("No hay solicitudes (instancias activas de curso5) en ejecución.")
            op = input("Presioná Enter para refrescar o 'q' para salir: ").strip().lower()
            if op == "q":
                break
            continue

        print("------------------------------------------------------------")
        print("Solicitudes activas (instancias de curso5):")
        for idx, s in enumerate(solicitudes, start=1):
            proc_id = s.get("id")
            bkey = s.get("businessKey") or "(sin businessKey)"
            tareas = obtener_tareas_instancia(client, proc_id)
            nombres_tareas = ", ".join(t.get("name") or t.get("taskDefinitionKey") for t in tareas) or "Esperando evento/timer"
            print(f"  {idx}. Instancia: {proc_id} | Ref: {bkey} | Estado actual: [{nombres_tareas}]")
        print("  0. Salir")
        print("------------------------------------------------------------")

        sel = input("Seleccioná una solicitud por número: ").strip()
        if sel == "0" or sel.lower() == "q":
            break
        if not sel.isdigit() or not (1 <= int(sel) <= len(solicitudes)):
            print("[AVISO] Opción inválida.\n")
            continue

        elegida = solicitudes[int(sel) - 1]
        proc_id = elegida.get("id")

        while True:
            habilitadas = detectar_comunicaciones_habilitadas(client, proc_id)
            timers = listar_timer_jobs(client, proc_id)
            tareas = obtener_tareas_instancia(client, proc_id)
            nombres_tareas = ", ".join(t.get("name") or t.get("taskDefinitionKey") for t in tareas) or "Sin tareas de usuario activas"

            print(f"\n>>> Solicitud seleccionada: {proc_id} (Ref: {elegida.get('businessKey') or '-'})")
            print(f"    Tareas activas ahora: {nombres_tareas}")

            if not habilitadas and not timers:
                print("    No hay comunicaciones de empresa ni timer jobs activos en el estado actual de esta instancia.")
                input("    Presioná Enter para volver al listado de solicitudes...")
                break

            if habilitadas:
                print("    Comunicaciones habilitadas en este estado:")
                for i, acc in enumerate(habilitadas, start=1):
                    print(f"      {i}. {acc['titulo']}")
            if timers:
                print("    Eventos de tiempo (timers) habilitados:")
                print("      9. Simular vencimiento de timer (mover timer job)")
            print("      0. Volver a seleccionar otra solicitud")

            op_acc = input("    Elegí la opción a simular: ").strip()
            if op_acc == "0":
                break
            if op_acc == "9" and timers:
                simular_vencimiento_timer(client, proc_id)
                break
            if op_acc.isdigit() and 1 <= int(op_acc) <= len(habilitadas):
                ejecutar_comunicacion(client, habilitadas[int(op_acc) - 1])
                break
            print("    [AVISO] Opción inválida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo...")
        sys.exit(0)
