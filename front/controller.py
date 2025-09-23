from back.pinger import Pinger

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
    
    def update_status(self, devices, selected_devices):
        active = {d.ip: d.name for d in devices if selected_devices[d.ip]}
        results = [Pinger.check_devices(active)]
        return results
    
    def stop_monitoring(self):
        print("Cessando monitoramento...")
    
    def ping_device(self, ip, devices):
        error = Pinger.analyzePingErrors(Pinger.run_ping(ip), devices, ip)
        if error:
            return {
                "code": 500, 
                "message": "Erro encontrado", 
                "name": error["name"],
                "ip": error["ip"],
                "error": error["error"]
            }
        else:
            return {"code": 200, "message": "Rede OK!"}