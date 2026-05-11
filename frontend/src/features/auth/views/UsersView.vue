<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import PageHeader from '@/components/shared/PageHeader.vue';
import EmptyState from '@/components/shared/EmptyState.vue';
import { userApi } from '../api/user.api';
import type { User } from '../types/user.types';
import UserFormDialog from '../components/UserFormDialog.vue';
import PermissionOverridesDialog from '../components/PermissionOverridesDialog.vue';
import { usePermission } from '@/features/auth/composables/usePermission';

const { hasPermission } = usePermission();
const canEdit = hasPermission('auth.users.edit');
const canCreate = hasPermission('auth.users.create');
const canDelete = hasPermission('auth.users.delete');

const users = ref<User[]>([]);
const loading = ref(false);
const searchQuery = ref('');
const dialogVisible = ref(false);
const editingUser = ref<User | null>(null);
const overridesVisible = ref(false);
const overridesUser = ref<User | null>(null);

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value;
  const q = searchQuery.value.toLowerCase();
  return users.value.filter(u =>
    u.email.toLowerCase().includes(q) ||
    (u.full_name?.toLowerCase().includes(q)) ||
    (u.username?.toLowerCase().includes(q))
  );
});

const fetchUsers = async () => {
  loading.value = true;
  try {
    const res = await userApi.getUsers(1, 100);
    users.value = res.data.data?.items ?? [];
  } catch (e) { console.error(e); } finally { loading.value = false; }
};

onMounted(() => fetchUsers());

const openNew = () => { editingUser.value = null; dialogVisible.value = true; };
const edit = (data: User) => { editingUser.value = data; dialogVisible.value = true; };
const openOverrides = (data: User) => { overridesUser.value = data; overridesVisible.value = true; };

const remove = async (id: number) => {
  if (!confirm('Delete this user?')) return;
  try { await userApi.deleteUser(id); fetchUsers(); } catch (e) { console.error(e); }
};
</script>

<template>
  <div>
    <PageHeader title="Users" subtitle="Manage user accounts and access" icon="pi pi-users">
      <template #actions>
        <Button v-if="canCreate" label="Add User" icon="pi pi-plus" @click="openNew" />
      </template>
    </PageHeader>

    <div class="ems-card">
      <div class="mb-4">
        <span class="p-input-icon-left w-full md:w-auto">
          <i class="pi pi-search" />
          <InputText v-model="searchQuery" placeholder="Search by email, name, username..." class="w-full md:w-20rem" />
        </span>
      </div>

      <DataTable v-if="filteredUsers.length" :value="filteredUsers" :loading="loading" stripedRows responsiveLayout="scroll">
        <Column field="email" header="Email" sortable></Column>
        <Column field="full_name" header="Full Name" sortable>
          <template #body="{ data }">{{ data.full_name || '—' }}</template>
        </Column>
        <Column field="username" header="Username" sortable>
          <template #body="{ data }">{{ data.username || '—' }}</template>
        </Column>
        <Column header="Roles" style="min-width:10rem">
          <template #body="{ data }">
            <div class="flex flex-wrap gap-1">
              <Tag v-for="role in data.roles" :key="role.id" :value="role.name" severity="info" class="text-xs" />
              <span v-if="!data.roles.length" class="text-surface-400 text-sm">—</span>
            </div>
          </template>
        </Column>
        <Column header="Status" style="width:7rem">
          <template #body="{ data }">
            <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
          </template>
        </Column>
        <Column v-if="canEdit || canDelete" :exportable="false" style="min-width:12rem">
          <template #body="{ data }">
            <Button v-if="canEdit" icon="pi pi-pencil" text rounded severity="success" class="mr-1" @click="edit(data)" />
            <Button v-if="canEdit" icon="pi pi-shield" text rounded severity="info" class="mr-1" @click="openOverrides(data)" v-tooltip="'Permission Overrides'" />
            <Button v-if="canDelete" icon="pi pi-trash" text rounded severity="danger" @click="remove(data.id)" />
          </template>
        </Column>
      </DataTable>
      <EmptyState v-else icon="pi pi-users" title="No users found" description="Create your first user to get started" />
    </div>

    <UserFormDialog v-model:visible="dialogVisible" :edit-data="editingUser" @saved="fetchUsers" />
    <PermissionOverridesDialog v-model:visible="overridesVisible" :user="overridesUser" />
  </div>
</template>
