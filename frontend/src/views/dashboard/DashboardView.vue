<script setup lang="ts">
import Card from 'primevue/card';
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="page-header">
      <h1>Overview</h1>
      <p>Welcome back to your school management dashboard.</p>
    </header>

    <div class="stats-grid">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Total Students</span>
              <h2 class="stat-value">1,248</h2>
            </div>
            <div class="stat-icon bg-blue">
              <i class="pi pi-users"></i>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Active Classes</span>
              <h2 class="stat-value">42</h2>
            </div>
            <div class="stat-icon bg-green">
              <i class="pi pi-book"></i>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Revenue (Month)</span>
              <h2 class="stat-value">$14,500</h2>
            </div>
            <div class="stat-icon bg-purple">
              <i class="pi pi-wallet"></i>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #102a43;
  margin: 0 0 0.5rem 0;
}

.page-header p {
  color: #627d98;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #f0f4f8;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}

:deep(.p-card-body) {
  padding: 1.5rem;
}

:deep(.p-card-content) {
  padding: 0;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #829ab1;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #102a43;
  margin: 0.5rem 0 0 0;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.bg-blue { background: linear-gradient(135deg, #3e82f7 0%, #2b6cb0 100%); }
.bg-green { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.bg-purple { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }
</style>
