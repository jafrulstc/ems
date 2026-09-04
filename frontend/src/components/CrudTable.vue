<script setup lang="ts">
import { ref, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import ConfirmDialog from 'primevue/confirmdialog';
import { useConfirm } from 'primevue/useconfirm';

interface ColDef {
  field: string;
  header: string;
  displayField?: string; // Optional field name for rendering in table column (e.g. department_name)
  type?: 'text' | 'date' | 'time' | 'number' | 'select' | 'password' | 'boolean';
  options?: { label: string; value: any }[] | ((data: any) => { label: string; value: any }[]);
  required?: boolean;
  hideInTable?: boolean;
  defaultValue?: any;
}

const props = defineProps<{
  title: string;
  rows: any[];
  columns: ColDef[];
  loading?: boolean;
  createFn: (data: any) => Promise<any>;
  updateFn: (id: string, data: any) => Promise<any>;
  deleteFn: (id: string) => Promise<any>;
  afterCreate?: (created: any) => string; // optional: return a custom success message string
}>();

const emit = defineEmits<{ refresh: [] }>();

const toast = useToast();
const confirm = useConfirm();

const dialogVisible = ref(false);
const editingRow = ref<any>(null);
const form = ref<any>({});
const saving = ref(false);

const filters = ref({
    global: { value: null, matchMode: 'contains' },
});

const dialogTitle = computed(() => editingRow.value ? `Edit ${props.title.slice(0, -1)}` : `New ${props.title.slice(0, -1)}`);

function openCreate() {
  editingRow.value = null;
  form.value = {};
  for (const col of props.columns) {
    if (col.defaultValue !== undefined) {
      form.value[col.field] = col.defaultValue;
    }
  }
  dialogVisible.value = true;
}

function openEdit(row: any) {
  editingRow.value = row;
  form.value = { ...row };
  dialogVisible.value = true;
}

async function save() {
  saving.value = true;
  try {
    if (editingRow.value) {
      await props.updateFn(editingRow.value.id, form.value);
      toast.add({ severity: 'success', summary: 'Updated', life: 2000 });
    } else {
      const created = await props.createFn(form.value);
      const msg = props.afterCreate ? props.afterCreate(created) : 'Created';
      toast.add({ severity: 'success', summary: msg, life: 3000 });
    }
    dialogVisible.value = false;
    emit('refresh');
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'Failed', life: 3000 });
  } finally {
    saving.value = false;
  }
}

function confirmDelete(row: any) {
  confirm.require({
    message: 'Are you sure you want to delete this record?',
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await props.deleteFn(row.id);
        toast.add({ severity: 'success', summary: 'Deleted', life: 2000 });
        emit('refresh');
      } catch (e: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Delete failed', life: 3000 });
      }
    }
  });
}
</script>

<template>
  <Toast />
  <ConfirmDialog />
  
  <div class="crud-table">
    <div class="table-header">
      <div class="table-title">
        <h3>{{ title }}</h3>
        <span class="p-input-icon-left search-input">
          <i class="pi pi-search" />
          <InputText v-model="filters['global'].value" placeholder="Search..." />
        </span>
      </div>
      <Button :label="`Add ${title.slice(0,-1)}`" icon="pi pi-plus" size="small" @click="openCreate" />
    </div>

    <DataTable :value="rows" :loading="loading" scrollable stripedRows size="small" :filters="filters" :globalFilterFields="columns.map(c => c.displayField || c.field)">
      <Column v-for="col in columns.filter(c => !c.hideInTable)" :key="col.field" :field="col.displayField || col.field" :header="col.header" sortable>
        <template #body="{ data }">
          <span v-if="col.type === 'boolean'">
            <i class="pi" :class="data[col.field] ? 'pi-check-circle' : 'pi-times-circle'" :style="{ color: data[col.field] ? '#22c55e' : '#ef4444' }"></i>
          </span>
          <span v-else-if="col.type === 'select' && col.options">
            {{ (typeof col.options === 'function' ? col.options(data) : col.options).find(o => o.value === data[col.field])?.label || data[col.displayField || col.field] }}
          </span>
          <span v-else>{{ data[col.displayField || col.field] }}</span>
        </template>
      </Column>
      <Column header="Actions" style="width: 120px">
        <template #body="{ data }">
          <div class="action-btns">
            <Button icon="pi pi-pencil" text rounded size="small" severity="info" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="confirmDelete(data)" />
          </div>
        </template>
      </Column>
    </DataTable>
  </div>

  <Dialog v-model:visible="dialogVisible" :header="dialogTitle" modal :style="{ width: '90vw', maxWidth: '440px' }">
    <div class="dialog-form">
      <div v-for="col in columns" :key="col.field" class="field" :class="{ 'row-field': col.type === 'boolean' }">
        <label v-if="col.type !== 'boolean'">
          {{ col.header }}
          <span v-if="col.required" style="color: #ef4444; margin-left: 2px;">*</span>
        </label>
        
        <!-- Dropdown / Select Input -->
        <Dropdown 
          v-if="col.type === 'select'" 
          v-model="form[col.field]" 
          :options="typeof col.options === 'function' ? col.options(form) : col.options" 
          optionLabel="label" 
          optionValue="value" 
          :placeholder="`-- Select ${col.header} --`" 
          filter 
          class="w-full custom-dropdown" 
        />
        
        <!-- Boolean Input -->
        <div v-else-if="col.type === 'boolean'" style="display: flex; align-items: center; gap: 8px;">
          <input type="checkbox" :id="col.field" v-model="form[col.field]" style="width: 18px; height: 18px; accent-color: #3b82f6;" />
          <label :for="col.field" style="margin: 0; font-size: 0.9rem; font-weight: 500;">
            {{ col.header }}
            <span v-if="col.required" style="color: #ef4444; margin-left: 2px;">*</span>
          </label>
        </div>
        
        <!-- Standard Input -->
        <InputText v-else v-model="form[col.field]" :type="col.type === 'number' ? 'number' : col.type === 'date' ? 'date' : col.type === 'time' ? 'time' : col.type === 'password' ? 'password' : 'text'" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" text @click="dialogVisible = false" />
      <Button label="Save" :loading="saving" @click="save" />
    </template>
  </Dialog>
</template>

<style scoped>
.crud-table {
  background: white;
  border-radius: 12px;
  border: 1px solid #f0f4f8;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  overflow: hidden;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f0f4f8;
  gap: 1rem;
}
.table-title {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}
.table-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #334e68;
  white-space: nowrap;
}
.search-input {
  max-width: 300px;
  width: 100%;
}
.search-input :deep(.p-inputtext) {
  padding: 0.4rem 0.5rem 0.4rem 2.25rem;
  border-radius: 6px;
  font-size: 0.85rem;
  width: 100%;
}
.action-btns { display: flex; gap: 4px; }
.dialog-form { display: flex; flex-direction: column; gap: 1rem; padding: 0.5rem 0; }
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field.row-field { flex-direction: row; align-items: center; }
.field label { font-size: 0.85rem; font-weight: 600; color: #486581; }
:deep(.p-inputtext), .custom-select {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  background: #fff;
  color: #1e293b;
  outline: none;
  transition: border-color 0.2s ease;
}
.custom-select:focus, :deep(.p-inputtext:focus), :deep(.p-dropdown.p-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
:deep(.p-dropdown) {
  border-radius: 6px;
  border-color: #cbd5e1;
}

/* Responsive adjustments for CrudTable */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }
  .table-title {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  .search-input {
    max-width: 100%;
  }
}
</style>
