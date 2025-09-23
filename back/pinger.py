import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

class Pinger:
    error_patterns = {
        "100% packet loss": "100% perda de pacotes",
        "Destination Host Unreachable": "Host inacessível",
        "Network is unreachable": "Network inacessível"
    }

    def analyzePingErrors(lines, devices, ip):
        for line in lines:
            for pattern, error_msg in Pinger.error_patterns.items():
                if pattern in line:
                    device_name = devices.get(ip, "Nome desconhecido")
                    return {
                        "name": device_name,
                        "ip": ip,
                        "error": error_msg
                    }
                
        return None
    
    def check_devices(devices: dict):
        errors = []

        for ip in devices.keys():
            lines = Pinger.run_ping(ip)
            error = Pinger.analyzePingErrors(lines, devices, ip)
            if error:
                errors.append(error)

        if errors:
            return {
                "code": 500,
                "message": "Erros encontrados.",
                "errors": errors
            }
        else:
            return {
                "code": 200,
                "message": "Rede OK!"
            }
    
    def run_ping(ip: str, count: int = 2):
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            return result.stdout.splitlines()
        except Exception as e:
            return [f"Erro ao pingar o endereço: {ip}: {e}"]
        
    def ping_device(ip, devices):
        lines = Pinger.run_ping(ip)
        return Pinger.analyzePingErrors(lines, devices, ip)
    
    def check_devices(devices: dict, max_workers: int = 10):
        errors = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(Pinger.ping_device, ip, devices): ip for ip in devices.keys()}
            for future in as_completed(future_to_ip):
                error = future.result()
                if error:
                    errors.append(error)
        
        if errors:
            return {
                "code": 500,
                "message": "Erros encontrados.",
                "errors": errors
            }
        else: 
            return {
                "code": 200,
                "message": "Rede OK!"
            }