import { createApp } from 'vue'
import Kanban from './Kanban.vue'
import GeoCascade from './GeoCascade.vue'

const k = document.getElementById('kanban-app')
if (k) createApp(Kanban, { projectId: Number(k.dataset.project) }).mount(k)

const g = document.getElementById('geo-app')
if (g) createApp(GeoCascade).mount(g)
