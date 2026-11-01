from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import docker
import uuid
import random
import re

app = FastAPI(title="PiCloud API")
client = docker.from_env()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InstanceRequest(BaseModel):
    name: str  # Het nieuwe naam-veld
    os_choice: str
    memory_mb: int
    cpu_cores: float

@app.get("/instances")
def list_instances():
    # We filteren nu op het label 'managed_by=picloud' voor veiligheid
    containers = client.containers.list(all=True, filters={"label": "managed_by=picloud"})
    instances = []
    for c in containers:
        networks = c.attrs.get('NetworkSettings', {}).get('Networks', {})
        ip_adres = "Geen IP"
        if networks:
            netwerk_naam = list(networks.keys())[0]
            ip_adres = networks[netwerk_naam].get('IPAddress', "Geen IP")

        ports = c.attrs.get('NetworkSettings', {}).get('Ports', {})
        ssh_port = "Geen"
        if ports and '22/tcp' in ports and ports['22/tcp'] is not None:
            ssh_port = ports['22/tcp'][0]['HostPort']

        status = c.status
        if status == 'running':
            exit_code, _ = c.exec_run("pgrep sshd")
            if exit_code != 0:
                status = 'provisioning'

        # Haal de onzichtbare prefix weg voor een cleane weergave in het dashboard
        display_name = c.name.replace("picloud-", "")

        instances.append({
            "id": c.short_id,
            "name": display_name,
            "status": status,
            "ip": ip_adres,
            "ssh_port": ssh_port,
            "image": c.image.tags[0] if c.image.tags else "unknown",
            "cores": c.attrs['HostConfig']['NanoCpus'] / 1e9,
            "ram": f"{c.attrs['HostConfig']['Memory'] / (1024*1024)} MB"
        })
    return {"instances": instances}

@app.post("/instances")
def create_instance(req: InstanceRequest):
    # Maak de naam Docker-safe (vervang spaties door streepjes, verwijder vreemde tekens)
    safe_name = re.sub(r'[^a-zA-Z0-9-]', '', req.name.replace(' ', '-').lower())
    if not safe_name:
        safe_name = f"instance-{str(uuid.uuid4())[:6]}"
        
    # We prefixen intern met picloud- om botsingen met je andere projecten te voorkomen
    container_name = f"picloud-{safe_name}"
    host_ssh_port = random.randint(2200, 9000)
    
    if req.os_choice == "rocky":
        image_tag = "rockylinux:9"
        startup_cmd = "bash -c 'dnf install -y openssh-server procps-ng && ssh-keygen -A && echo \"root:picloud\" | chpasswd && echo \"PermitRootLogin yes\" >> /etc/ssh/sshd_config && echo \"PasswordAuthentication yes\" >> /etc/ssh/sshd_config && /usr/sbin/sshd -D'"
    else:
        image_tag = "ubuntu:latest"
        startup_cmd = "bash -c 'apt-get update && apt-get install -y openssh-server procps && mkdir -p /var/run/sshd && echo \"root:picloud\" | chpasswd && echo \"PermitRootLogin yes\" >> /etc/ssh/sshd_config && echo \"PasswordAuthentication yes\" >> /etc/ssh/sshd_config && /usr/sbin/sshd -D'"
    
    mem_limit = f"{req.memory_mb}m"
    nano_cpus = int(req.cpu_cores * 1e9)
    
    client.containers.run(
        image_tag, 
        command=startup_cmd,
        detach=True, 
        name=container_name,
        labels={"managed_by": "picloud"}, # Markeer hem als een PiCloud instance
        mem_limit=mem_limit,
        nano_cpus=nano_cpus,
        ports={'22/tcp': host_ssh_port}
    )
    return {"message": "Instance gestart!"}

@app.post("/instances/{instance_id}/stop")
def stop_instance(instance_id: str):
    try:
        client.containers.get(instance_id).stop()
        return {"message": "Instance gestopt"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Instance niet gevonden")

@app.post("/instances/{instance_id}/start")
def start_instance(instance_id: str):
    client.containers.get(instance_id).start()
    return {"message": "Instance gestart"}

@app.delete("/instances/{instance_id}")
def delete_instance(instance_id: str):
    client.containers.get(instance_id).remove(force=True)
    return {"message": "Instance verwijderd"}