import docker

client = docker.from_env()

print("Starten van instance...")
container = client.containers.run(
    "ubuntu:latest", 
    command="sleep infinity",
    detach=True, 
    name="pi-instance-01"
)

# Wacht tot de container netwerkgegevens heeft
container.reload()

# Nieuwe, veiligere manier om het IP-adres uit te lezen
networks = container.attrs['NetworkSettings']['Networks']
# Pak de naam van het eerste netwerk (meestal 'bridge') en lees daar het IP uit
netwerk_naam = list(networks.keys())[0]
ip_adres = networks[netwerk_naam]['IPAddress']

print(f"Instance '{container.name}' draait succesvol!")
print(f"Toegewezen IP-adres: {ip_adres}")