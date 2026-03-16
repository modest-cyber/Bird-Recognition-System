<template>
  <div class="layout">
    <NavBar />
    <el-main class="main-content">
      <slot></slot>
    </el-main>
    <Footer />
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue'
import Footer from './Footer.vue'
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
}
</style>
