class Controller:
    def list_devices(self, devices, selected_devices):
        print("\nDevices: ")
        for d in devices:
            enabled = "ON" if selected_devices[d.ip] else "OFF"
            print(f"- {d.name} ({d.ip}) | Status: {d.status} | Monitoring: {enabled}")

    def start_monitoring(self, selected_devices):
        print("Monitorando...")
        for ip, enabled in selected_devices.items():
            if enabled:
                print(f"- {ip}")

    def update_statuses(self, devices, selected_devices):
        results = []
        errors = []

        for d in devices:
            if selected_devices[d.ip]:
                if d.status == "Offline":
                    errors.append({"name": d.name, "ip": d.ip})
                else:
                    d.status = "Online"

        if errors:
            results.append({
                "status": "500",
                "message": "Encontrado erros.",
                "errors": errors
            })
        else:
            results.append({
                "status": "200",
                "message": "Rede OK!"
            })

        return results


    def stop_monitoring(self):
        print("Cessando monitoramento...")
        