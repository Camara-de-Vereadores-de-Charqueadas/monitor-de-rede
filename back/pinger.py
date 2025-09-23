import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

class Pinger:
    def analyzePingErrors(lines, devices, ip):
        full_output = ' '.join(lines).lower()
        
        error_patterns = {
            "100% packet loss": "100% perda de pacotes",
            "destination host unreachable": "Host inacessível", 
            "network is unreachable": "Rede inacessível",
            "request timeout": "Timeout",
            "no route to host": "Sem rota para o host"
        }
        
        for pattern, error_msg in error_patterns.items():
            if pattern in full_output:
                device_name = devices.get(ip, "Nome desconhecido") if isinstance(devices, dict) else "Nome desconhecido"
                return {
                    "name": device_name,
                    "ip": ip,
                    "error": error_msg
                }
        
        if "0 received" in full_output and "100%" in full_output:
            device_name = devices.get(ip, "Nome desconhecido") if isinstance(devices, dict) else "Nome desconhecido"
            return {
                "name": device_name,
                "ip": ip,
                "error": "100% perda de pacotes"
            }
        
        if "bytes from" not in full_output and len(lines) > 2:
            device_name = devices.get(ip, "Nome desconhecido") if isinstance(devices, dict) else "Nome desconhecido"
            return {
                "name": device_name,
                "ip": ip,
                "error": "Sem resposta do host"
            }
        
        return None
    
    def run_ping(ip: str, count: int = 1):
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), "-W", "5", ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10
            )
            return result.stdout.splitlines()
        except subprocess.TimeoutExpired:
            return ["Ping timeout"]
        except Exception as e:
            return [f"Erro ao pingar o endereço: {ip}: {e}"]
        
    def ping_device(ip, devices):
        lines = Pinger.run_ping(ip)
        return Pinger.analyzePingErrors(lines, devices, ip)
    
    def check_devices(devices: dict, max_workers: int = 10):
        errors = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(Pinger.ping_device, ip, devices): ip for ip in devices.keys()}

            for future in as_completed(futures):
                err = future.result()
                if err:
                    errors.append(err)

        if errors:
            return {"code": 500, "message": "Erros encontrados", "errors": errors}
        return {"code": 200, "message": "Rede OK!"}