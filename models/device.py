class Device:
    def __init__ (self, name: str, ip: str):
        self.name = name
        self.ip = ip
        self.status = "Unknown"

    def __repr__ (self):
        return f"<Device {self.name} ({self.ip} - {self.status})>"