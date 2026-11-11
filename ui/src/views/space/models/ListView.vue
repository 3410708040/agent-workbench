<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { useI18n } from 'vue-i18n'
import CardGridSkeleton from '@/components/skeletons/CardGridSkeleton.vue'
import { getErrorMessage } from '@/utils/error'
import { formatTimestampShort } from '@/utils/time-formatter'
import { deleteCustomModel, getCustomModels } from '@/services/custom-model'
import type { CustomModelItem } from '@/models/custom-model'
import CreateOrUpdateCustomModelModal from './components/CreateOrUpdateCustomModelModal.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const loading = ref(false)
const providers = ref<CustomModelItem[]>([])
const showCreateOrUpdateModelModalVisible = ref(false)
const updateModelProviderId = ref('')

const clearCreateTypeQuery = async () => {
  const nextQuery = { ...route.query }
  delete nextQuery.create_type
  await router.replace({
    path: route.path,
    query: nextQuery,
  })
}

const loadProviders = async () => {
  loading.value = true
  try {
    const res = await getCustomModels()
    providers.value = res.data || []
  } catch (error: unknown) {
    Message.error(getErrorMessage(error, t('space.models.loadFailed')))
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  updateModelProviderId.value = ''
  showCreateOrUpdateModelModalVisible.value = true
}

const openEditModal = (provider: CustomModelItem) => {
  updateModelProviderId.value = provider.id
  showCreateOrUpdateModelModalVisible.value = true
}

const handleCardClick = (provider: CustomModelItem) => {
  openEditModal(provider)
}

const handleDelete = (provider: CustomModelItem) => {
  Modal.warning({
    title: t('space.models.deleteConfirmTitle'),
    content: t('space.models.deleteConfirmContent'),
    hideCancel: false,
    onOk: async () => {
      try {
        const resp = await deleteCustomModel(provider.id)
        Message.success(resp.message)
        await loadProviders()
      } catch (error: unknown) {
        Message.error(getErrorMessage(error, t('space.models.deleteFailed')))
      }
    },
  })
}

const featureLabel = (feature: string) => {
  const map: Record<string, string> = {
    tool_call: t('space.models.featureToolCall'),
    agent_thought: t('space.models.featureAgentThought'),
    image_input: t('space.models.featureImageInput'),
  }
  return map[feature] || feature
}

watch(
  () => route.query?.create_type,
  (newValue) => {
    if (newValue !== 'model') return
    openCreateModal()
    void clearCreateTypeQuery()
  },
  { immediate: true },
)

onMounted(async () => {
  await loadProviders()
})
</script>

<template>
  <a-spin :loading="loading" class="block h-full w-full scrollbar-w-none overflow-y-scroll overflow-x-hidden">
    <div class="p-6 flex flex-col h-full min-h-0">
      <card-grid-skeleton v-if="loading && providers.length === 0" :count="8" />
      <a-row v-else :gutter="[20, 20]" class="flex-1 min-h-0 overflow-hidden">
        <a-col
          v-for="provider in providers"
          :key="provider.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="6"
        >
          <a-card hoverable class="cursor-pointer rounded-lg h-full" @click="handleCardClick(provider)">
            <div class="flex items-start gap-3 mb-3">
              <a-avatar :size="40" shape="square" :style="{ backgroundColor: '#4F6BF6' }">
                <span class="text-white font-semibold">
                  {{ (provider.label || provider.name || 'M')[0].toUpperCase() }}
                </span>
              </a-avatar>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 min-w-0">
                  <div class="text-base font-bold text-gray-900 truncate">{{ provider.label || provider.name }}</div>
                  <a-tag size="small" :color="provider.is_active ? 'green' : 'gray'">
                    {{ provider.is_active ? t('space.models.isActive') : t('space.models.unavailable') }}
                  </a-tag>
                </div>
                <div class="text-xs text-gray-500 line-clamp-1">{{ provider.name }}</div>
              </div>
            </div>

            <div class="flex items-center gap-2 flex-wrap mt-3">
              <a-tag size="small" color="arcoblue">{{ provider.base_url }}</a-tag>
            </div>

            <div class="mt-3 flex items-center gap-2 flex-wrap">
              <a-tag v-for="modelName in provider.model_names || []" :key="modelName" size="small" color="gray">
                {{ modelName }}
              </a-tag>
            </div>

            <div class="mt-3 flex items-center gap-2 flex-wrap">
              <a-tag
                v-for="feature in provider.features || []"
                :key="feature"
                size="small"
                :color="feature === 'tool_call' ? 'green' : 'orange'"
              >
                {{ featureLabel(feature) }}
              </a-tag>
            </div>

            <div class="flex items-center gap-1.5 mt-3">
              <div class="text-xs text-gray-400">
                {{ t('space.models.recentEdited', { time: formatTimestampShort(provider.updated_at || provider.created_at) }) }}
              </div>
            </div>

            <div class="flex items-center justify-between gap-2 mt-4" @click.stop>
              <a-dropdown position="br" @click.stop>
                <a-button size="small" type="text" class="rounded-lg !text-gray-700">
                  <template #icon>
                    <icon-more />
                  </template>
                </a-button>
                <template #content>
                  <a-doption @click="() => openEditModal(provider)">
                    {{ t('space.models.edit') }}
                  </a-doption>
                  <a-doption class="text-red-700" @click="() => handleDelete(provider)">
                    {{ t('common.actions.delete') }}
                  </a-doption>
                </template>
              </a-dropdown>

              <a-button size="small" type="primary" class="rounded-lg" @click.stop="openEditModal(provider)">
                {{ t('space.models.edit') }}
              </a-button>
            </div>
          </a-card>
        </a-col>

        <a-col v-if="providers.length === 0" :span="24">
          <a-empty :description="t('space.models.empty')" class="py-20" />
        </a-col>
      </a-row>
    </div>

    <create-or-update-custom-model-modal
      v-model:visible="showCreateOrUpdateModelModalVisible"
      v-model:model_provider_id="updateModelProviderId"
      :callback="async () => await loadProviders()"
    />
  </a-spin>
</template>

<style scoped>
.scrollbar-w-none {
  scrollbar-width: none;
}

.scrollbar-w-none::-webkit-scrollbar {
  display: none;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
