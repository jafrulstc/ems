<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';

const authStore = useAuthStore();
const router = useRouter();
const isSidebarCollapsed = ref(false);
const isMobile = ref(false);

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
  if (isMobile.value) {
    isSidebarCollapsed.value = true;
  }
};

onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});

const handleLogout = () => {
  authStore.logout();
  router.push({ name: 'login' });
};

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const closeSidebarOnMobile = () => {
  if (isMobile.value) {
    isSidebarCollapsed.value = true;
  }
};

const menuItems = [
  { label: 'Dashboard', icon: 'pi pi-home', route: 'dashboard' },
  { label: 'Academics', icon: 'pi pi-book', route: 'academic-setup' },
  { label: 'Students', icon: 'pi pi-users', route: 'students' },
  { label: 'Examinations', icon: 'pi pi-file-edit', route: 'exam-setup' },
  { label: 'Administration', icon: 'pi pi-server', route: 'tenant-setup' },
];
</script>

<template>
  <div class="layout-container">
    <!-- Mobile Overlay -->
    <div 
      class="mobile-overlay" 
      :class="{ 'active': !isSidebarCollapsed && isMobile }" 
      @click="toggleSidebar"
    ></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo-box">EMS</div>
        <h2 v-if="!isSidebarCollapsed || isMobile">EduManage</h2>
      </div>
      
      <nav class="sidebar-nav">
        <router-link 
          v-for="item in menuItems" 
          :key="item.label" 
          :to="{ name: item.route }" 
          class="nav-item"
          active-class="active"
          @click="closeSidebarOnMobile"
        >
          <i :class="item.icon"></i>
          <span v-if="!isSidebarCollapsed || isMobile">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper">
      <!-- Topbar -->
      <header class="topbar">
        <div class="topbar-left">
          <Button icon="pi pi-bars" text rounded @click="toggleSidebar" class="toggle-btn" />
          <h3 class="tenant-badge">{{ authStore.tenantSlug?.toUpperCase() }}</h3>
        </div>
        
        <div class="topbar-right">
          <Avatar image="https://i.pravatar.cc/150?u=a042581f4e29026024d" shape="circle" class="avatar" />
          <Button icon="pi pi-sign-out" text rounded severity="danger" @click="handleLogout" title="Logout" />
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background-color: #f4f6f8;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

/* Sidebar Styles */
.sidebar {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e4e7eb;
  transition: width 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 1.25rem;
  gap: 1rem;
  border-bottom: 1px solid #f0f4f8;
}

.logo-box {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3e82f7 0%, #2b6cb0 100%);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #102a43;
  margin: 0;
  white-space: nowrap;
}

.sidebar-nav {
  padding: 1.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  color: #486581;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-item i {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.nav-item:hover {
  background: #f0f4f8;
  color: #102a43;
}

.nav-item.active {
  background: #ebf4ff;
  color: #3e82f7;
}

/* Mobile Overlay */
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 90;
  backdrop-filter: blur(2px);
}

/* Main Content Styles */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 70px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e4e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  z-index: 5;
}

.topbar-left, .topbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.toggle-btn {
  color: #486581 !important;
}

.tenant-badge {
  background: #e2e8f0;
  color: #334e68;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin: 0;
  white-space: nowrap;
}

.avatar {
  border: 2px solid #ebf4ff;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    left: 0;
    top: 0;
    transform: translateX(0);
    width: 260px;
    box-shadow: 2px 0 12px rgba(0,0,0,0.1);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 260px; /* Keep full width, just hide it */
  }

  .mobile-overlay.active {
    display: block;
  }

  .topbar {
    padding: 0 1rem;
  }
  
  .tenant-badge {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .page-content {
    padding: 1rem;
  }
}
</style>
