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
            
            elif choice == "Saindo":
                print("Encerrando.")
                break

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

        ping_interval = 30
        ping_counter = 0
        countdown = ping_interval

        while True:
            if countdown <= 0:
                results = controller.update_statuses(self.devices, self.selected_devices)
                ping_counter += 1
                countdown = ping_interval
            else:
                results = []

            os.system("clear" if os.name == "posix" else "cls")

            print("=== MONITORANDO REDE ===")
            print(f"Próximo ping em: {countdown} segundos")
            print(f"Pings realizados: {ping_counter}\n")

            for r in results:
                print(f"[{r['status']}] {r['message']}")
                if r.get("errors"):
                    for e in r["errors"]:
                        print(f" - {e['nme']} ({e['ip']})")
            
            print("\nPressione 'q' para sair do monitoramento.")

            if self.key_pressed("q"):
                return

            time.sleep(1)
            countdown -= 1
        
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
