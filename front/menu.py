import json
import time
import os
import sys
import select
import questionary
import termios
import tty

from models.device import Device

class MonitorUI:
    def __init__(self, device_file: str = "devices.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.device_file = os.path.join(base_dir, "..", device_file)

        self.devices = self.load_devices()
        self.selected_devices = {d.ip: True for d in self.devices}

    def load_devices(self):
        with open(self.device_file, "r") as f:
            data = json.load(f)
        return [Device(d["name"], d["ip"]) for d in data]
    
    def main_menu(self, controller):
        while True:
            self.flush_stdin()

            os.system("clear" if os.name == "posix" else "cls")
            choice = questionary.select(
                "=== MONITOR DE REDE === ",
                choices= [
                    "Listar dispositivos",
                    "Iniciar monitoramento",
                    "Config dispositivos",
                    "Sair"
                ]
            ).ask()
            
            if choice == "Listar dispositivos":
                self.list_devices(controller)

            elif choice == "Iniciar monitoramento":
                self.monitoring_mode(controller)
            
            elif choice == "Config dispositivos":
                self.config_devices()
            
            elif choice == "Sair":
                print("Encerrando.")
                sys.exit(0)

    def config_devices(self):
        choices = [
            questionary.Choice(
                title = f"{d.name} ({d.ip})",
                value = d.ip,
                checked = self.selected_devices.get(d.ip, True)
            )
            for d in self.devices
        ]
        
        selected = questionary.checkbox(
            "Selecione dispositivos para monitorar",
            choices=choices
        ).ask()

        self.selected_devices = {d.ip: (d.ip in selected) for d in self.devices}

    def monitoring_mode(self, controller):
        print("Monitoramento iniciado. Pressione 'q' para encerrar.")
        time.sleep(1)

        selected_ips = [d.ip for d in self.devices if self.selected_devices[d.ip]]
        total = len(selected_ips)
        ping_counter = 0
        
        CYCLE_INTERVAL = 30
        history = []

        while True:
            current_errors = [] 
            
            for idx, ip in enumerate(selected_ips, 1):
                if self.key_pressed("q"):
                    return
                
                res = controller.ping_device(ip, {d.ip: d.name for d in self.devices})
                
                if res.get("code") == 500:
                    current_errors.append(res)

                os.system("clear" if os.name == "posix" else "cls")
                print("=== MONITORANDO REDE ===")
                print(f"Progresso: {idx}/{total} dispositivos")
                print(f"Ciclos completados: {ping_counter}\n")
                print("Testando dispositivos...")
                time.sleep(0.1)
            
            if current_errors:
                history.extend(current_errors)
            else:
                history.append({"code": 200, "message": "Rede OK!"})
            
            os.system("clear" if os.name == "posix" else "cls")
            print("=== MONITORANDO REDE ===")
            print(f"Progresso: {total}/{total} dispositivos")
            print(f"Ciclos completados: {ping_counter + 1}\n")

            for entry in history:
                if entry.get("code") == 500:
                    print(f" - {entry.get('name', 'Unknown')} ({entry.get('ip', 'Unknown')}) | {entry.get('error', 'Unknown error')}")
                elif entry.get("code") == 200:
                    print(f"[{entry.get('code')}] {entry.get('message', '')}")
            
            ping_counter += 1
            print("Pressione 'q' para sair.\n")
                        
            for remaining in range(CYCLE_INTERVAL, 0, -1):
                if self.key_pressed("q"):
                    return
                print(f"\rPróximo ciclo em {remaining} segundos...", end="", flush=True)
                time.sleep(1)
            print()

        
    def list_devices(self, controller):
        controller.list_devices(self.devices, self.selected_devices)
        input("\nPressione ENTER para voltar ao menu...")

    def key_pressed(self, target_key: str) -> bool:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            key = sys.stdin.read(1)
            return key.lower() == target_key.lower()
        return False
    
    def flush_stdin(self):
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        while dr:
            os.read(sys.stdin.fileno(), 1024)
            dr, _, _ = select.select([sys.stdin], [], [], 0)