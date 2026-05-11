<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import Dropdown from 'primevue/dropdown';
import { coreApi } from '@/features/core/api/core.api';
import type { GeoDivision, GeoDistrict, GeoUpazila, GeoPostOffice, GeoVillage } from '@/types/core.types';

const props = defineProps<{
  modelValue?: number | null; // village_id
}>();

const emit = defineEmits<{
  'update:modelValue': [val: number | null];
}>();

const loading = ref(false);

const divisions = ref<GeoDivision[]>([]);
const districts = ref<GeoDistrict[]>([]);
const upazilas = ref<GeoUpazila[]>([]);
const postOffices = ref<GeoPostOffice[]>([]);
const villages = ref<GeoVillage[]>([]);

const selectedDivision = ref<number | null>(null);
const selectedDistrict = ref<number | null>(null);
const selectedUpazila = ref<number | null>(null);
const selectedPostOffice = ref<number | null>(null);
const selectedVillage = ref<number | null>(props.modelValue || null);

onMounted(async () => {
  loading.value = true;
  try {
    const res = await coreApi.getDivisions();
    divisions.value = res.data.data ?? [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

const onDivisionChange = async () => {
  selectedDistrict.value = null;
  selectedUpazila.value = null;
  selectedPostOffice.value = null;
  selectedVillage.value = null;
  emit('update:modelValue', null);
  
  if (selectedDivision.value) {
    const res = await coreApi.getDistricts(selectedDivision.value);
    districts.value = res.data.data ?? [];
  } else {
    districts.value = [];
  }
};

const onDistrictChange = async () => {
  selectedUpazila.value = null;
  selectedPostOffice.value = null;
  selectedVillage.value = null;
  emit('update:modelValue', null);
  
  if (selectedDistrict.value) {
    const res = await coreApi.getUpazilas(selectedDistrict.value);
    upazilas.value = res.data.data ?? [];
  } else {
    upazilas.value = [];
  }
};

const onUpazilaChange = async () => {
  selectedPostOffice.value = null;
  selectedVillage.value = null;
  emit('update:modelValue', null);
  
  if (selectedUpazila.value) {
    const res = await coreApi.getPostOffices(selectedUpazila.value);
    postOffices.value = res.data.data ?? [];
  } else {
    postOffices.value = [];
  }
};

const onPostOfficeChange = async () => {
  selectedVillage.value = null;
  emit('update:modelValue', null);
  
  if (selectedPostOffice.value) {
    const res = await coreApi.getVillages(selectedPostOffice.value);
    villages.value = res.data.data ?? [];
  } else {
    villages.value = [];
  }
};

const onVillageChange = () => {
  emit('update:modelValue', selectedVillage.value);
};
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Division</label>
      <Dropdown
        v-model="selectedDivision"
        :options="divisions"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Division"
        @change="onDivisionChange"
        :loading="loading"
        class="w-full text-sm"
      />
    </div>

    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-500 dark:text-slate-400">District</label>
      <Dropdown
        v-model="selectedDistrict"
        :options="districts"
        optionLabel="name"
        optionValue="id"
        placeholder="Select District"
        @change="onDistrictChange"
        :disabled="!selectedDivision"
        class="w-full text-sm"
      />
    </div>

    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Upazila</label>
      <Dropdown
        v-model="selectedUpazila"
        :options="upazilas"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Upazila"
        @change="onUpazilaChange"
        :disabled="!selectedDistrict"
        class="w-full text-sm"
      />
    </div>

    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Post Office</label>
      <Dropdown
        v-model="selectedPostOffice"
        :options="postOffices"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Post Office"
        @change="onPostOfficeChange"
        :disabled="!selectedUpazila"
        class="w-full text-sm"
      />
    </div>

    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Village</label>
      <Dropdown
        v-model="selectedVillage"
        :options="villages"
        optionLabel="name"
        optionValue="id"
        placeholder="Select Village"
        @change="onVillageChange"
        :disabled="!selectedPostOffice"
        class="w-full text-sm"
      />
    </div>
  </div>
</template>
