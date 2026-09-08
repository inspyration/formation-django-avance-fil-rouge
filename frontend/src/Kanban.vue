<template>
  <div class="d-flex gap-3 overflow-auto">
    <div v-for="s in statuses" :key="s.id" class="border rounded p-2" style="min-width:220px"
         @dragover.prevent @drop="onDrop(s.id)">
      <div class="fw-bold mb-2" :style="{ color: s.color }">{{ s.name }}</div>
      <div v-for="t in tasksByStatus(s.id)" :key="t.id"
           class="card p-2 mb-2" draggable="true" @dragstart="dragId = t.id">
        {{ t.name }}
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const props = defineProps({ projectId: Number })
const statuses = ref([]); const tasks = ref([]); let dragId = null; let timer = null
function cookie(n) { const m = document.cookie.match('(^|;)\\s*' + n + '\\s*=\\s*([^;]+)'); return m ? m.pop() : '' }
async function load() {
  const r = await fetch(`/api/projects/${props.projectId}/board`)
  const d = await r.json(); statuses.value = d.statuses; tasks.value = d.tasks
}
const tasksByStatus = (sid) => tasks.value.filter(t => t.status_id === sid)
async function onDrop(sid) {
  if (!dragId) return
  await fetch(`/api/tasks/${dragId}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cookie('csrftoken') },
    body: JSON.stringify({ status_id: sid }),
  })
  dragId = null; load()
}
let ws = null
onMounted(() => {
  load()
  timer = setInterval(load, 15000)  // repli
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}/ws/board/${props.projectId}/`)
  ws.onmessage = () => load()  // temps réel : un autre client a bougé une carte
})
onUnmounted(() => { clearInterval(timer); if (ws) ws.close() })
</script>
