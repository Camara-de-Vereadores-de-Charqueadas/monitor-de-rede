import re
import socket
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dei uma mexida pra ficar mais modularizado o código.
# Facilita na hora de tirar ou adicionar módulos

def getNetworkDevices():
    return {
        "192.168.1.11": "Camara3 - PC",
        "192.168.1.12": "Camara5 - Gilvan",
        "192.168.1.15": "SERVIDOR",
        "192.168.1.20": "Camara03 - Chines",
        "192.168.1.22": "Camara2 - Paula",
        "192.168.1.34": "Camara10 - Administração",
        "192.168.1.35": "Camara005 - Tatiana",
        "192.168.1.58": "Camara006 - Rose",    
        "192.168.1.81": "Camara2 - Giovane",
        "192.168.1.87": "Camara01 - Wilson",
        "192.168.1.93": "Camara007 - Patrick",
        "192.168.1.94": "Camara09 - Adriano",
        "192.168.1.101": "Romeira",
        "192.168.1.105": "Camara003 - Secretaria", 
        "192.168.1.106": "Camara001 - Comissoes",
        "192.168.1.107": "Camara004 - Financeiro",
        "192.168.1.113": "Impressora - Wilson",
        "192.168.1.208": "Impressora - Giovane",
        "192.168.1.214": "Impressora - Administração",
        "192.168.1.217": "Impressora - Comissoes",
        "192.168.1.218": "Impressora - Claudio",
        "192.168.1.222": "Impressora - Rose",
        "192.168.1.223": "Impressora - Tatiana",
        "192.168.1.224": "Impressora - Patrick",
        "192.168.1.225": "Impressora - Gilvan",
        "192.168.1.226": "Impressora - Esporinha",
        "192.168.1.228": "Impressora - Wagner",
        "192.168.1.232": "Impressora - Recepção",
        "192.168.1.234": "Impressora - Secretaria",
        "192.168.1.235": "Impressora - Adriano",
        "192.168.1.236": "Impressora - PC",
        "192.168.1.237": "Impressora - Rogerio",
        "192.168.1.239": "Impressora - Financeiro",
        "192.168.1.240": "Impressora - Paula",
        "8.8.8.8": "Internet"
    }

def readLogFile(arquivo):
    try:
        with open(arquivo, 'r') as file :
            return file.readlines()
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado, verifique se o arquivo monitorarede.bat esta executando!!!")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return None

def findIpInPreviousLines(lines, current_index, max_lookback=5):
    # Usado para determinar o IP do dispositivo que causou o output.
    for j in range(current_index - 1, max(0, current_index - max_lookback - 1), -1):
        match = re.search(r"PING (\d{1,3}(?:\.\d{1,3}){3})", lines[j])
        if match:
            return match.group(1)
    return None

def analyzePingErrors(lines, network_devices):
    # Analisa as linhas e retorna os erros que foram encontrados.
    error_patterns = ["100% packet loss", "Network is unreachable", "Destination Host Unreachable"] # Erros comuns do bash
    errors_found = [] # Evita repetição
    processed_ips = set()
    
    for i, line in enumerate(lines):
        if any(error in line for error in error_patterns):
            ip = findIpInPreviousLines(lines, i)

            if ip and ip in processed_ips:
                continue

            device_name = network_devices.get(ip, "Nome desconhecido") if ip else "IP não identificado"
            
            timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            error_details = line.strip()
            if "100% packet loss" in line:
                error_details = f"100% perda de pacotes - {device_name}"
            elif "Destination Host Unreachable" in line:
                error_details = f"Host inacessível - {device_name}"
            elif "Network is unreachable" in line:
                error_details = f"Network inacessível - {device_name}"

            errors_found.append({
                'timestamp': timestamp,
                'device_name': device_name,
                'ip': ip,
                'error_details': line.strip()
            })
            
            if ip:
                processed_ips.add(ip)
            
            print(f"\nERRO: {device_name} ({ip if ip else 'N/A'})")
            print(f"Detalhes: {line.strip()}")
    
    return errors_found

def saveErrorsToFile(errors, arquivo="momento_erro.txt"):
    if not errors:
        return
    
    try:
        with open(arquivo, "a") as file:
            for error in errors:
                file.write(f"{error['timestamp']}\n")
                file.write(f"{error['device_name']}\n")
                file.write(f"Erro: {error['error_details']}\n")
                file.write("-------------------\n")
    except Exception as e:
        print(f"Erro ao salvar no arquivo {arquivo}: {e}")

def sendToEmail(device_name, error_details):
    email_sender = 'rafaelbarth856@gmail.com'
    email_password = 'gjti ypao msws uibw'
    email_recipient = 'rafaelchina856@gmail.com'
    subject = 'Erro de Rede'
    
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(f"Erro detectado em: {device_name}\nDetalhes: {error_details}", 'plain'))
    
    try:
        # with smtplib.SMTP('smtp.gmail.com', 587) as server:
        #     server.starttls()
        #     server.login(email_sender, email_password)
        #     server.send_message(msg)
        print(f'Email enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar email: {e}')

def cleanupLogFile(arquivo):
    try:
        if os.path.exists(arquivo):
            os.remove(arquivo)
            print(f"Arquivo {arquivo} removido após processamento.")
    except Exception as e:
        print(f"Erro ao remover arquivo {arquivo}: {e}")

def main():
    # Orquestra a lógica do monitor

    log_arquivo = "log_ping.txt"
    network_devices = getNetworkDevices()
    
    lines = readLogFile(log_arquivo)
    if lines is None:
        return
    
    errors_found = analyzePingErrors(lines, network_devices)
    
    if errors_found:
        saveErrorsToFile(errors_found)
        
        for error in errors_found:
            sendToEmail(error['device_name'], error['error_details'])
    else:
        print("\nRede OK!")
    
    cleanupLogFile(log_arquivo)

if __name__ == "__main__":
    main()