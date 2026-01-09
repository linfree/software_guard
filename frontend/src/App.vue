<template>
  <a-config-provider :locale="zhCN">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import '@/styles/design-system.css'
</script>

<style>
/* 全局样式已迁移至 design-system.css */
</style>
