<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const visible = ref(true)
const expanded = ref(false)
const position = ref({ x: window.innerWidth - 100, y: window.innerHeight - 100 })
const dragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

// 模拟数据 - 实际应该从后端或对话状态获取
const tokenStats = ref({
  totalTokens: 1250,
  inputTokens: 850,
  outputTokens: 400,
  todayRequests: 23,
  modelName: '豆包 Pro',
})

const handleMouseDown = (e: MouseEvent) => {
  dragging.value = true
  dragOffset.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y,
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!dragging.value) return
  position.value = {
    x: e.clientX - dragOffset.value.x,
    y: e.clientY - dragOffset.value.y,
  }
}

const handleMouseUp = () => {
  dragging.value = false
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
})
</script>

<template>
  <div
    v-if="visible"
    class="fixed z-50 select-none"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @mousedown="handleMouseDown"
  >
    <!-- 展开状态 -->
    <div
      v-if="expanded"
      class="bg-white rounded-2xl shadow-xl border border-gray-200 p-4 w-64 cursor-move"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm">
            🤖
          </div>
          <span class="font-semibold text-gray-900">用量统计</span>
        </div>
        <button
          class="text-gray-400 hover:text-gray-600 text-lg leading-none"
          @click.stop="expanded = false"
        >
          ×
        </button>
      </div>

      <!-- 统计内容 -->
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">当前模型</span>
          <span class="font-medium text-gray-900">{{ tokenStats.modelName }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">总 Token</span>
          <span class="font-medium text-blue-600">{{ tokenStats.totalTokens }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">输入 Token</span>
          <span class="text-gray-700">{{ tokenStats.inputTokens }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">输出 Token</span>
          <span class="text-gray-700">{{ tokenStats.outputTokens }}</span>
        </div>
        <div class="flex justify-between border-t pt-2">
          <span class="text-gray-500">今日对话</span>
          <span class="font-medium text-green-600">{{ tokenStats.todayRequests }} 次</span>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="mt-3 text-xs text-gray-400 text-center">
        拖动我可以移动位置
      </div>
    </div>

    <!-- 收起状态 - 只显示一个小圆点 -->
    <div
      v-else
      class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full shadow-lg flex items-center justify-center text-white text-xl cursor-pointer hover:scale-110 transition-transform"
      @click.stop="expanded = true"
    >
      🤖
    </div>
  </div>
</template>

<style scoped>
/* 拖动时禁止选中文本 */
:host {
  user-select: none;
}
</style>
