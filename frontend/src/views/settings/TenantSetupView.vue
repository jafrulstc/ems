<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { TenantService } from '../../services/tenant.service';
import CrudTable from '../../components/CrudTable.vue';
import Toast from 'primevue/toast';

const toast = useToast();
const activeTab = ref('branches');

const institutes = ref<any[]>([]);
const branches = ref<any[]>([]);
const users = ref<any[]>([]);
const loading = ref(true);

const load = async () => {
  loading.value = true;
  try {
    [institutes.value, branches.value, users.value] = await Promise.all([
      TenantService.getInstitutes(),
      TenantService.getBranches(),
      TenantService.getUsers(),
    ]);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Load failed', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(load);

const tabs = [
  { id: 'institutes', label: 'Institutes (Super Admin)', icon: 'pi pi-globe' },
  { id: 'branches', label: 'Branches', icon: 'pi pi-sitemap' },
  { id: 'users', label: 'Users', icon: 'pi pi-users' },
];

const instituteCols = [
  { field: 'name', header: 'Institute Name' },
  { field: 'slug', header: 'Slug/Subdomain' },
  { field: 'address', header: 'Address' },
  { field: 'contact_email', header: 'Contact Email' },
  { field: 'admin_email', header: 'Admin Email', hideInTable: true, required: true },
  { field: 'admin_password', header: 'Admin Password', hideInTable: true, type: 'password' as const, required: true },
];

const branchCols = [
  { field: 'name', header: 'Branch Name', required: true },
  { field: 'address', header: 'Address' },
];

const userCols = [
  { field: 'full_name', header: 'Full Name', required: true },
  { field: 'email', header: 'Email', required: true },
  { 
    field: 'user_type', 
    header: 'Role / Type', 
    type: 'select' as const, 
    options: [
      { label: 'Branch Admin', value: 'branch_admin' },
      { label: 'Teacher', value: 'teacher' },
      { label: 'Staff', value: 'staff' },
      { label: 'Student', value: 'student' }
    ],
    required: true
  },
  { 
    field: 'branch_id', 
    header: 'Branch', 
    type: 'select' as const, 
    options: () => branches.value.map(b => ({ label: b.name, value: b.id })), 
    required: true 
  },
  { field: 'password', header: 'Password', type: 'password' as const, hideInTable: true, required: true },
  { field: 'is_active', header: 'Active', type: 'boolean' as const, defaultValue: true }
];
</script>

<template>
  <div class="page-container">
    <Toast />
    
    <div class="page-header">
      <div>
        <h1>Administration & Settings</h1>
        <p>Manage institutes, branches, and system settings.</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-header">
      <button 
        v-for="t in tabs" 
        :key="t.id" 
        class="tab-btn" 
        :class="{ active: activeTab === t.id }" 
        @click="activeTab = t.id"
      >
        <i :class="t.icon"></i>
        <span>{{ t.label }}</span>
      </button>
    </div>

    <!-- Tab Content Panels -->
    <div class="tab-content">
      <div v-if="activeTab === 'institutes'">
        <CrudTable 
          title="Institutes" 
          :rows="institutes" 
          :columns="instituteCols" 
          :loading="loading"
          :createFn="TenantService.createInstitute"
          :updateFn="TenantService.updateInstitute"
          :deleteFn="TenantService.deleteInstitute"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'branches'">
        <CrudTable 
          title="Branches" 
          :rows="branches" 
          :columns="branchCols" 
          :loading="loading"
          :createFn="TenantService.createBranch"
          :updateFn="TenantService.updateBranch"
          :deleteFn="TenantService.deleteBranch"
          @refresh="load" 
        />
      </div>

      <div v-if="activeTab === 'users'">
        <CrudTable 
          title="Users" 
          :rows="users" 
          :columns="userCols" 
          :loading="loading"
          :createFn="TenantService.createUser"
          :updateFn="TenantService.updateUser"
          :deleteFn="TenantService.deleteUser"
          @refresh="load" 
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container { 
  display: flex; 
  flex-direction: column; 
  gap: 1.5rem; 
}
.page-header h1 { 
  font-size: 1.75rem; 
  font-weight: 700; 
  color: #102a43; 
  margin: 0 0 .25rem; 
}
.page-header p { 
  color: #627d98; 
  margin: 0; 
}

/* Tabs Styling */
.tabs-header {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 2px;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
}
.tab-btn:hover {
  color: #1e293b;
  background: #f8fafc;
}
.tab-btn.active {
  color: #2563eb;
  background: #eff6ff;
  border-bottom-color: #2563eb;
}
.tab-content {
  margin-top: 0.5rem;
}
</style>
