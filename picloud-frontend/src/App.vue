<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const instances = ref([])
const currentView = ref('instances')
const loading = ref(false)
let pollingInterval = null

// PAS DIT IP AAN NAAR HET IP VAN JE RASPBERRY PI
const apiBase = 'http://192.168.1.254:8000' 

const form = ref({
  os_choice: 'ubuntu',
  memory_mb: 512,
  cpu_cores: 1
})

const fetchInstances = async () => {
  try {
    const res = await axios.get(`${apiBase}/instances`)
    instances.value = res.data.instances
  } catch (error) {
    console.error(error)
  }
}

const createInstance = async () => {
  loading.value = true
  try {
    await axios.post(`${apiBase}/instances`, form.value)
    currentView.value = 'instances'
    await fetchInstances()
  } catch (error) {
    console.error(error)
  }
  loading.value = false
}

const stopInstance = async (id) => { await axios.post(`${apiBase}/instances/${id}/stop`); fetchInstances(); }
const startInstance = async (id) => { await axios.post(`${apiBase}/instances/${id}/start`); fetchInstances(); }
const deleteInstance = async (id) => {
  if(confirm("Weet je zeker dat je deze instance wilt verwijderen?")) {
    await axios.delete(`${apiBase}/instances/${id}`);
    fetchInstances();
  }
}

onMounted(() => {
  fetchInstances()
  pollingInterval = setInterval(fetchInstances, 3000)
})

onUnmounted(() => { clearInterval(pollingInterval) })
</script>

<template>
  <div class="layout">
    <!-- Topbar (Volledige breedte) -->
    <header class="site-header">
      <div class="nav-wrap">
        <div class="brand">
          <div class="brand-mark">Pi<span>Cloud</span></div>
          <div class="brand-name">Control Panel</div>
        </div>
        <div class="main-nav">
          <a href="#">admin@picloud.local</a>
          <button class="nav-cta">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main Container (Neemt de rest van het scherm in) -->
    <div class="main-container">
      
      <!-- Zijbalk -->
      <aside class="sidebar">
        <ul class="nav-list">
          <li :class="['nav-item', { active: currentView === 'instances' }]" @click="currentView = 'instances'">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
            Instances
          </li>
          <li :class="['nav-item', { active: currentView === 'create' }]" @click="currentView = 'create'">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Nieuwe Instance
          </li>
          <li :class="['nav-item', { active: currentView === 'storage' }]" @click="currentView = 'storage'">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
            Storage (NAS)
          </li>
          <li :class="['nav-item', { active: currentView === 'network' }]" @click="currentView = 'network'">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/></svg>
            Virtual Networks
          </li>
        </ul>
      </aside>

      <!-- Content Area -->
      <main class="content">
        <div class="eyebrow">
          <div class="eyebrow-line"></div>
          <span>PICLOUD / {{ currentView.toUpperCase() }}</span>
        </div>

        <div class="heading-row">
          <h2>
            <span v-if="currentView === 'instances'"><em>Instances</em></span>
            <span v-if="currentView === 'create'">Deploy <em>Instance</em></span>
            <span v-if="currentView === 'storage'">Storage <em>Pools</em></span>
            <span v-if="currentView === 'network'">Network <em>Topology</em></span>
          </h2>
          <button v-if="currentView === 'instances'" class="nav-cta" @click="fetchInstances">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.85.84 6.72 2.27L21 8"/><path d="M21 3v5h-5"/></svg>
            Refresh
          </button>
        </div>

        <!-- INSTANCE LIJST -->
        <div v-if="currentView === 'instances'" class="card">
          <div class="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Naam</th>
                  <th>State</th>
                  <th>IP Address</th>
                  <th>Cores</th>
                  <th>RAM</th>
                  <th>Connectie (SSH)</th>
                  <th>Acties</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inst in instances" :key="inst.id">
                  <td class="font-bold">{{ inst.name }}</td>
                  <td>
                    <div class="status-indicator">
                      <span v-if="inst.status === 'running'" class="orb orb-green"></span>
                      <span v-else-if="inst.status === 'provisioning'" class="orb orb-yellow"></span>
                      <span v-else class="orb orb-red"></span>
                      <span class="mono-status">{{ inst.status }}</span>
                    </div>
                  </td>
                  <td class="mono-text">{{ inst.ip }}</td>
                  <td class="mono-text">{{ inst.cores || 'Standaard' }}</td>
                  <td class="mono-text">{{ inst.ram === '0.0 MB' ? 'Standaard' : inst.ram }}</td>
                  <td>
                    <code v-if="inst.status === 'running' && inst.ssh_port !== 'Geen'" class="ssh-code">
                      ssh root@192.168.1.254 -p {{ inst.ssh_port }}
                    </code>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="actions-cell">
                    <button v-if="inst.status === 'exited'" @click="startInstance(inst.id)" class="btn-icon" title="Start">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="6 3 20 12 6 21 6 3"/></svg>
                    </button>
                    <button v-if="inst.status === 'running'" @click="stopInstance(inst.id)" class="btn-icon" title="Stop">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                    </button>
                    <button @click="deleteInstance(inst.id)" class="btn-icon text-danger" title="Delete">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- NIEUWE INSTANCE FORMULIER -->
        <div v-if="currentView === 'create'" class="card form-card">
          <div class="form-container">
            <div class="form-group">
              <label>Instance Naam</label>
              <input type="text" v-model="form.name" placeholder="bijv. webserver-productie" required>
            </div>
            <div class="form-group">
              <label>Besturingssysteem Image</label>
              <select v-model="form.os_choice">
                <option value="ubuntu">Ubuntu 22.04 LTS (Latest)</option>
                <option value="rocky">Rocky Linux 9 (RHEL Compatible)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Toegekend Geheugen (RAM in MB)</label>
              <input type="number" v-model="form.memory_mb" step="256" min="256" max="6144">
            </div>
            <div class="form-group">
              <label>Toegewezen CPU Cores</label>
              <input type="number" v-model="form.cpu_cores" step="0.5" min="0.5" max="4">
            </div>
            <button class="nav-cta btn-deploy" @click="createInstance" :disabled="loading">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              {{ loading ? 'Provisioning bezig...' : 'Deploy Instance' }}
            </button>
          </div>
        </div>

        <!-- STORAGE MOCKUP -->
        <div v-if="currentView === 'storage'" class="card storage-card">
          <div class="storage-visual">
            <div class="storage-header">
              <strong>Raspberry Pi Hoofdopslag (SD Kaart)</strong>
              <span class="mono-text">128 GB Totaal</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 35%;"></div>
            </div>
            <div class="storage-footer">
              <span class="text-muted">44.8 GB Gebruikt (35%)</span>
              <span class="text-teal">83.2 GB Vrij</span>
            </div>
          </div>
          <div class="table-responsive" style="margin-top: 30px;">
            <table>
              <thead>
                <tr><th>Volume ID</th><th>Type</th><th>Gekoppeld aan</th><th>Grootte</th></tr>
              </thead>
              <tbody>
                <tr><td class="mono-text">vol-local-1</td><td>Local LVM</td><td>Host (Raspberry Pi)</td><td class="mono-text">30 GB</td></tr>
                <tr><td class="mono-text">vol-docker-data</td><td>Overlay2</td><td>Docker Engine</td><td class="mono-text">14.8 GB</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- NETWORK MOCKUP -->
        <div v-if="currentView === 'network'" class="card">
          <div class="table-responsive">
            <table>
              <thead>
                <tr><th>Netwerk Naam</th><th>Subnet CIDR</th><th>Gateway</th><th>Driver</th><th>DHCP</th></tr>
              </thead>
              <tbody>
                <tr><td class="font-bold">picloud-bridge (Standaard)</td><td class="mono-text">172.17.0.0/16</td><td class="mono-text">172.17.0.1</td><td>bridge</td><td><span class="orb orb-green"></span> Aan</td></tr>
                <tr><td class="font-bold">host-network</td><td class="mono-text">-</td><td class="mono-text">-</td><td>host</td><td><span class="orb orb-red"></span> Uit</td></tr>
                <tr><td class="font-bold">docker-internal</td><td class="mono-text">10.0.0.0/24</td><td class="mono-text">10.0.0.1</td><td>bridge</td><td><span class="orb orb-green"></span> Aan</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

:root {
  --paper: #f6f3ed;
  --paper-light: #fcfbf8;
  --ink: #1d2d3b;
  --ink-soft: #45545d;
  --muted: #77817e;
  --line: #deded6;
  --teal: #64877f;
  --teal-light: #dce7e1;
  --mono: "DM Mono", monospace;
  --sans: "DM Sans", Arial, sans-serif;
  --serif: "Playfair Display", Georgia, serif;
}

* { box-sizing: border-box; }
body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); font-family: var(--sans); -webkit-font-smoothing: antialiased; overflow-x: hidden; }

/* Forceer het framework over het hele scherm */
.layout { display: flex; flex-direction: column; height: 100vh; width: 100vw; max-width: 100%; }

/* Header neemt perfect 100% in */
.site-header { height: 82px; display: flex; align-items: center; border-bottom: 1px solid var(--line); background: rgba(246,243,237,.93); width: 100%; padding: 0 40px; }
.nav-wrap { width: 100%; display: flex; align-items: center; justify-content: space-between; }
.brand { display: inline-flex; align-items: center; gap: 11px; }
.brand-mark { font-size: 24px; letter-spacing: -2px; font-weight: 700; }
.brand-mark span { color: var(--teal); }
.brand-name { font-size: 15px; font-weight: 600; letter-spacing: .01em; }
.main-nav { display: flex; align-items: center; gap: 34px; font-size: 14px; font-weight: 500; color: var(--ink-soft); }
.nav-cta { display: inline-flex; gap: 10px; align-items: center; padding: 12px 16px; background: var(--ink); color: white; border: none; border-radius: 3px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background .2s, transform .2s; font-family: var(--sans); }
.nav-cta:hover:not(:disabled) { background: #355267; transform: translateY(-2px); }
.nav-cta:disabled { background: var(--muted); cursor: not-allowed; }

/* Main Container gebruikt resterende ruimte */
.main-container { display: flex; flex: 1; overflow: hidden; width: 100%; }

/* Sidebar breedte staat vast */
.sidebar { width: 260px; flex-shrink: 0; background: var(--paper-light); border-right: 1px solid var(--line); padding: 30px 20px; overflow-y: auto; }
.nav-list { list-style: none; padding: 0; margin: 0; }
.nav-item { padding: 14px 16px; color: var(--ink-soft); font-size: 15px; font-weight: 500; cursor: pointer; border-radius: 4px; display: flex; align-items: center; gap: 12px; margin-bottom: 8px; transition: background .2s, color .2s; }
.nav-item:hover { background: var(--paper); color: var(--teal); }
.nav-item.active { background: var(--ink); color: var(--paper-light); }

/* Content vult flexibel aan tot de rand */
.content { flex: 1; min-width: 0; padding: 40px; overflow-y: auto; overflow-x: hidden; background: var(--paper); }

.eyebrow { display: flex; align-items: center; gap: 12px; font-size: 11px; letter-spacing: .13em; color: var(--teal); font-family: var(--mono); margin-bottom: 10px; }
.eyebrow-line { width: 29px; height: 1px; background: var(--teal); }
.heading-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
h2 { font-size: clamp(28px, 4vw, 42px); line-height: 1.12; letter-spacing: -.055em; font-weight: 500; margin: 0; }
h2 em { font-family: var(--serif); font-weight: 500; color: var(--teal); letter-spacing: -.045em; }

/* Cards & Tables */
.card { background: var(--paper-light); border: 1px solid var(--line); border-radius: 4px; padding: 25px; width: 100%; box-shadow: 0 10px 30px rgba(29,45,59,.03); }
.table-responsive { width: 100%; overflow-x: auto; }
table { width: 100%; min-width: 850px; border-collapse: collapse; font-size: 14px; text-align: left; }
th, td { padding: 16px; border-bottom: 1px solid var(--line); white-space: nowrap; }
th { font-family: var(--mono); font-size: 11px; letter-spacing: .08em; color: var(--muted); text-transform: uppercase; border-bottom: 2px solid var(--line); }
tr:last-child td { border-bottom: none; }
.font-bold { font-weight: 600; color: var(--ink); }
.mono-text { font-family: var(--mono); font-size: 13px; color: var(--ink-soft); }

/* Actieknoppen */
.actions-cell { display: flex; gap: 8px; }
.btn-icon { background: var(--paper); border: 1px solid var(--line); color: var(--ink-soft); padding: 8px; cursor: pointer; border-radius: 3px; display: grid; place-items: center; transition: all .2s; }
.btn-icon:hover { background: var(--line); color: var(--ink); }
.text-danger { color: #b94a4a; }
.text-danger:hover { background: #faeaea; border-color: #eababa; color: #9c3030; }

/* Status Indicators */
.status-indicator { display: flex; align-items: center; gap: 10px; }
.orb { width: 10px; height: 10px; border-radius: 50%; display: inline-block; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); }
.orb-green { background: #6c9c80; }
.orb-red { background: #b94a4a; }
.orb-yellow { background: #cca652; animation: pulse 1.5s infinite; }
.mono-status { font-family: var(--mono); font-size: 11px; letter-spacing: .05em; color: var(--ink-soft); text-transform: uppercase; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

/* Code Blocks */
.ssh-code { background: var(--teal-light); color: var(--ink); font-family: var(--mono); font-size: 12px; padding: 6px 10px; border-radius: 3px; border: 1px solid #c9d8d1; display: inline-block; }
.text-muted { color: var(--muted); }
.text-teal { color: var(--teal); font-weight: 600; }

/* Formulier */
.form-card { max-width: 700px; }
.form-group { margin-bottom: 24px; }
.form-group label { display: block; font-family: var(--mono); font-size: 11px; letter-spacing: .08em; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }
.form-group input, .form-group select { width: 100%; padding: 12px 14px; border: 1px solid var(--line); background: var(--paper); border-radius: 3px; font-family: var(--sans); font-size: 15px; color: var(--ink); transition: border-color .2s; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: var(--teal); }
.btn-deploy { width: 100%; justify-content: center; padding: 14px; font-size: 14px; margin-top: 10px; }

/* Storage Mockup Specials */
.storage-visual { background: var(--paper); border: 1px solid var(--line); padding: 20px; border-radius: 4px; }
.storage-header, .storage-footer { display: flex; justify-content: space-between; font-size: 13px; }
.storage-header { margin-bottom: 15px; }
.storage-footer { margin-top: 15px; }
.progress-bar { height: 12px; background: var(--line); border-radius: 6px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--teal); border-radius: 6px; }
</style>