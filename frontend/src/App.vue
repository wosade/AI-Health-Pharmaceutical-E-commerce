<template>
  <router-view v-if="$route.meta.noAuth" />
  <div v-else class="app-layout">
    <Sidebar />
    <div class="main-area">
      <Header />
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
</script>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
}
</style>