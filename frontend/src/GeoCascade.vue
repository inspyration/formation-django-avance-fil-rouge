<template>
  <div class="row g-2" style="max-width:760px">
    <div class="col"><select class="form-select" v-model="country" @change="onCountry">
      <option value="">— pays —</option>
      <option v-for="c in countries" :key="c.id" :value="c.id">{{ c.name }}</option>
    </select></div>
    <div class="col" v-if="country"><select class="form-select" v-model="region" @change="onRegion">
      <option value="">— {{ labels.region }} —</option>
      <option v-for="r in regions" :key="r.id" :value="r.id">{{ r.name }}</option>
    </select></div>
    <div class="col" v-if="region"><select class="form-select" v-model="subregion" @change="onSub">
      <option value="">— {{ labels.subregion }} —</option>
      <option v-for="s in subregions" :key="s.id" :value="s.id">{{ s.name }}</option>
    </select></div>
    <div class="col" v-if="subregion"><select class="form-select" v-model="city">
      <option value="">— ville —</option>
      <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.label }}</option>
    </select></div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
const countries = ref([]), regions = ref([]), subregions = ref([]), cities = ref([])
const country = ref(''), region = ref(''), subregion = ref(''), city = ref('')
const codeById = ref({})
const LABELS = { FR: { region: 'région', subregion: 'département' }, US: { region: 'état', subregion: 'comté' } }
const labels = computed(() => LABELS[codeById.value[country.value]] || { region: 'région', subregion: 'sous-région' })
const j = async (u) => (await fetch(u)).json()
onMounted(async () => { const cs = await j('/api/countries'); countries.value = cs; cs.forEach(c => codeById.value[c.id] = c.code2) })
async function onCountry() { region.value = subregion.value = city.value = ''; regions.value = subregions.value = cities.value = []; if (country.value) regions.value = await j('/api/regions?country=' + country.value) }
async function onRegion() { subregion.value = city.value = ''; subregions.value = cities.value = []; if (region.value) subregions.value = await j('/api/subregions?region=' + region.value) }
async function onSub() { city.value = ''; cities.value = []; if (subregion.value) cities.value = await j('/api/cities?subregion=' + subregion.value) }
</script>
