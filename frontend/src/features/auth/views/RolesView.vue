<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { roleApi } from '../api/role.api';
import type { RoleWithPermissions } from '../types/role.types';
import RoleFormDialog from '../components/RoleFormDialog.vue';
import RolePermissionsDialog from '../components/RolePermissionsDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('auth.roles.edit');
const canCreate = hasPermission('auth.roles.create');
const canDelete = hasPermission('auth.roles.delete');

const roles = ref<RoleWithPermissions[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const dialogVisible = ref(false);
const editingRole = ref<RoleWithPermissions | null>(null);
const permsVisible = ref(false);
const permsRole = ref<RoleWithPermissions | null>(null);

const filteredRoles = computed(() => {
  if (!searchQuery.value) return roles.value;
  const q = searchQuery.value.toLowerCase();
  return roles.value.filter(r => r.name.toLowerCase().includes(q) || (r.description?.toLowerCase().includes(q)));
});

const fetchRoles = async () => {
  loading.value = true;
  try {
    const res = await roleApi.getRoles();
    roles.value = res.data.data ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => fetchRoles());

const openNew = () => { editingRole.value = null; dialogVisible.value = true; };
const edit = (data: RoleWithPermissions) => { editingRole.value = data; dialogVisible.value = true; };
const openPerms = (data: RoleWithPermissions) => { permsRole.value = data; permsVisible.value = true; };

const remove = async (id: number) => {
  if (!confirm('Delete this role?')) return;
  try { await roleApi.deleteRole(id); fetchRoles(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Roles" subtitle="Manage roles and their permissions" icon="pi pi-shield">
      <template #actions>
        <Button v-if="canCreate" label="Add Role" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="card bg-surface-0 dark:bg-surface-900 p-4 rounded-xl shadow-sm border border-surface-200 dark:border-surface-800">
      <div class="mb-4">
        <span class="p-input-icon-left w-full md:w-auto">
          <i class="pi pi-search" />
          <InputText v-model="searchQuery" placeholder="Search roles..." class="w-full md:w-20rem" />
        </span>
      </div>

      <DataTable v-if="filteredRoles.length" :value="filteredRoles" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="name" header="Name" sortable></Column>
        <Column field="description" header="Description" sortable>
          <template #body="{ data }">{{ data.description || '—' }}</template>
        </Column>
        <Column header="Permissions" style="min-width:12rem">
          <template #body="{ data }">
            <div class="flex flex-wrap gap-1">
              <Tag v-for="p in data.permissions.slice(0, 3)" :key="p.id" :value="p.label" severity="info" class="text-xs" />
              <Tag v-if="data.permissions.length > 3" :value="`+${data.permissions.length - 3} more`" severity="warn" class="text-xs" />
              <span v-if="!data.permissions.length" class="text-surface-400 text-sm">None</span>
            </div>
          </template>
        </Column>
        <Column v-if="canEdit || canDelete" :exportable="false" style="min-width:12rem">
          <template #body="{ data }">
            <Button v-if="canEdit" icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button v-if="canEdit" icon="pi pi-key" text rounded severity="info" class="mr-1" @click="openPerms(data)" v-tooltip="'Assign Permissions'" />
            <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-shield" title="No roles found" description="Create your first role to get started" />
    </div>

    <RoleFormDialog v-model:visible="dialogVisible" :edit-data="editingRole" @saved="fetchRoles" />
    <RolePermissionsDialog v-model:visible="permsVisible" :role="permsRole" @saved="fetchRoles" />
  </div>
</template>
