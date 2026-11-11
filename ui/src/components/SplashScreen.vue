<script setup lang="ts">
import { ref, onMounted } from 'vue'

const visible = ref(true)
const progress = ref(0)

onMounted(() => {
  // 模拟加载进度
  const timer = setInterval(() => {
    progress.value += Math.random() * 15
    if (progress.value >= 100) {
      progress.value = 100
      clearInterval(timer)
      // 进度完成后延迟一点再消失
      setTimeout(() => {
        visible.value = false
      }, 300)
    }
  }, 150)
})
</script>

<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white transition-opacity duration-500"
  >
    <!-- Logo 区域 -->
    <div class="mb-8">
      <div class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        我的智能体工作台
      </div>
    </div>

    <!-- 加载动画 -->
    <div class="relative w-16 h-16 mb-8">
      <div class="absolute inset-0 rounded-full border-4 border-gray-200"></div>
      <div
        class="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-600 animate-spin"
      ></div>
    </div>

    <!-- 进度条 -->
    <div class="w-64 h-1 bg-gray-200 rounded-full overflow-hidden">
      <div
        class="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300 ease-out"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>

    <!-- 提示文字 -->
    <div class="mt-4 text-sm text-gray-500">正在加载工作台...</div>
  </div>
</template>

<style scoped></style>
