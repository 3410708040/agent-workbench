<script setup lang="ts">
import { computed } from 'vue'
import { useAccountStore } from '@/stores/account'

const accountStore = useAccountStore()

const userName = computed(() => {
  return accountStore.account?.name || '朋友'
})

const quickActions = [
  {
    title: '新建对话',
    description: '开始一个新的 AI 对话',
    icon: '💬',
    path: '/home',
    color: 'from-blue-500 to-blue-600',
  },
  {
    title: '模型管理',
    description: '配置和管理你的 AI 模型',
    icon: '🤖',
    path: '/space/models',
    color: 'from-purple-500 to-purple-600',
  },
  {
    title: '我的应用',
    description: '管理你的智能体应用',
    icon: '📱',
    path: '/space/apps',
    color: 'from-green-500 to-green-600',
  },
  {
    title: '插件中心',
    description: '扩展工作台能力',
    icon: '🧩',
    path: '/space/tools',
    color: 'from-orange-500 to-orange-600',
  },
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-[#F8FBFF] via-[#F6FAFF] to-[#F9FAFB] p-6 lg:p-8">
    <div class="max-w-6xl mx-auto">
      <!-- 欢迎区 -->
      <div class="mb-8 animate-fade-in-down">
        <h1 class="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
          你好，{{ userName }} 👋
        </h1>
        <p class="text-gray-500 text-lg">
          欢迎回到我的智能体工作台，今天想做点什么？
        </p>
      </div>

      <!-- 快捷操作卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div
          v-for="action in quickActions"
          :key="action.title"
          class="group cursor-pointer bg-white rounded-2xl p-5 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
          @click="$router.push(action.path)"
        >
          <div
            class="w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform"
            :class="action.color"
          >
            {{ action.icon }}
          </div>
          <div class="text-base font-semibold text-gray-900 mb-1">{{ action.title }}</div>
          <div class="text-sm text-gray-500">{{ action.description }}</div>
        </div>
      </div>

      <!-- 快速开始输入框 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <div class="text-base font-semibold text-gray-900 mb-4">快速开始</div>
        <div class="flex gap-3">
          <input
            type="text"
            placeholder="输入你的问题，开始和 AI 对话..."
            class="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
          />
          <button class="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-200 transition-all">
            发送
          </button>
        </div>
      </div>

      <!-- 最近对话区域 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div class="text-base font-semibold text-gray-900">最近对话</div>
          <button class="text-sm text-blue-600 hover:text-blue-700">查看全部 →</button>
        </div>
        <div class="text-sm text-gray-400 text-center py-8">
          还没有对话记录，点击上方"新建对话"开始吧
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-down {
  animation: fade-in-down 0.5s ease-out;
}
</style>
