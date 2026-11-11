<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Form, Message, type ValidatedError } from '@arco-design/web-vue'
import { useI18n } from 'vue-i18n'
import { getErrorMessage } from '@/utils/error'
import {
  createCustomModel,
  updateCustomModel,
  testCustomModel,
  testCustomModelPayload,
  getCustomModels,
} from '@/services/custom-model'
import type { CustomModelItem } from '@/models/custom-model'

type ModelRow = { name: string; label: string }

const props = defineProps({
  model_provider_id: { type: String, default: '', required: false },
  visible: { type: Boolean, required: true },
  callback: { type: Function, required: false },
})

const emits = defineEmits(['update:visible', 'update:model_provider_id'])
const { t } = useI18n()

const formRef = ref<InstanceType<typeof Form>>()
const submitLoading = ref(false)
const testing = ref(false)
const testResult = ref<{ ok: boolean; message: string } | null>(null)

const defaultForm = () => ({
  name: '',
  label: '',
  api_key: '',
  base_url: '',
  model_type: 'chat',
  models: [{ name: '', label: '' }] as ModelRow[],
  features: ['tool_call'] as string[],
  context_window: 0,
  max_output_tokens: 0,
  is_active: true,
})

const form = ref(defaultForm())

const isEditMode = computed(() => Boolean(props.model_provider_id))

const hideModal = () => emits('update:visible', false)

const buildPayload = () => ({
  name: form.value.name.trim(),
  label: form.value.label.trim(),
  api_key: form.value.api_key.trim(),
  base_url: form.value.base_url.trim(),
  model_type: form.value.model_type,
  models: form.value.models
    .map((row) => ({ name: row.name.trim(), label: row.label.trim() || row.name.trim() }))
    .filter((row) => row.name),
  features: form.value.features,
  context_window: Number(form.value.context_window || 0),
  max_output_tokens: Number(form.value.max_output_tokens || 0),
  is_active: form.value.is_active,
})

const validateBeforeTest = () => {
  if (!form.value.name.trim()) {
    Message.warning(t('space.models.nameRequired'))
    return false
  }
  if (!form.value.api_key.trim()) {
    Message.warning(t('space.models.apiKeyRequired'))
    return false
  }
  if (!form.value.base_url.trim()) {
    Message.warning(t('space.models.baseUrlRequired'))
    return false
  }
  const modelNames = form.value.models
    .map((row) => row.name.trim())
    .filter(Boolean)
  if (modelNames.length === 0) {
    Message.warning(t('space.models.modelListRequired'))
    return false
  }
  return true
}

const handleTest = async () => {
  if (!validateBeforeTest()) return
  testing.value = true
  testResult.value = null
  try {
    const payload = buildPayload()
    const firstModel = payload.models[0]?.name || ''
    const res = isEditMode.value
      ? await testCustomModel(props.model_provider_id, firstModel)
      : await testCustomModelPayload(payload)
    const data = res.data || { ok: false, message: '' }
    testResult.value = { ok: Boolean(data.ok), message: String(data.message || '') }
    if (data.ok) {
      Message.success(t('space.models.testSuccess'))
    } else {
      Message.error(t('space.models.testFailed'))
    }
  } catch (error: unknown) {
    testResult.value = { ok: false, message: getErrorMessage(error, t('space.models.testFailed')) }
    Message.error(testResult.value.message)
  } finally {
    testing.value = false
  }
}

const applyProvider = (item: CustomModelItem) => {
  const savedModels: ModelRow[] = (item.model_names || []).map((name) => ({ name, label: name }))
  form.value = {
    name: item.name || '',
    label: item.label || '',
    api_key: item.api_key || '',
    base_url: item.base_url || '',
    model_type: item.model_type || 'chat',
    models: savedModels.length ? savedModels : [{ name: '', label: '' }],
    features: (item.features && item.features.length ? item.features : ['tool_call']) as string[],
    context_window: Number(item.context_window || 0),
    max_output_tokens: Number(item.max_output_tokens || 0),
    is_active: item.is_active !== false,
  }
}

const loadProvider = async (providerId: string) => {
  if (!providerId) return
  try {
    const res = await getCustomModels()
    const target = (res.data || []).find((item) => item.id === providerId)
    if (target) applyProvider(target)
  } catch (error: unknown) {
    Message.error(getErrorMessage(error, t('space.models.loadFailed')))
  }
}

const handleSubmit = async ({ errors }: { errors: Record<string, ValidatedError> | undefined }) => {
  if (errors) return
  submitLoading.value = true
  try {
    const payload = buildPayload()
    if (payload.models.length === 0) {
      Message.warning(t('space.models.modelListRequired'))
      return
    }
    if (isEditMode.value) {
      const resp = await updateCustomModel(props.model_provider_id, payload)
      Message.success(resp.message)
    } else {
      const resp = await createCustomModel(payload)
      Message.success(resp.message)
    }
    emits('update:visible', false)
    emits('update:model_provider_id', '')
    props.callback && props.callback()
  } catch (error: unknown) {
    Message.error(getErrorMessage(error, t('space.models.loadFailed')))
  } finally {
    submitLoading.value = false
  }
}

const removeModelRow = (index: number) => {
  if (form.value.models.length <= 1) {
    form.value.models = [{ name: '', label: '' }]
    return
  }
  form.value.models.splice(index, 1)
}

const addModelRow = () => {
  form.value.models.push({ name: '', label: '' })
}

watch(
  () => props.visible,
  async (visible) => {
    formRef.value?.resetFields()
    testResult.value = null
    if (!visible) {
      form.value = defaultForm()
      emits('update:model_provider_id', '')
      return
    }
    if (props.model_provider_id) {
      await loadProvider(props.model_provider_id)
    } else {
      form.value = defaultForm()
    }
  },
)
</script>

<template>
  <a-modal
    :visible="props.visible"
    :title="isEditMode ? t('space.models.updateTitle') : t('space.models.createTitle')"
    :width="680"
    :footer="false"
    modal-class="custom-model-modal-shell"
    @cancel="hideModal"
  >
    <a-form ref="formRef" :model="form" layout="vertical" class="custom-model-form" @submit="handleSubmit">
      <a-form-item
        field="name"
        :label="t('space.models.name')"
        asterisk-position="end"
        :rules="[{ required: true, message: t('space.models.nameRequired') }]"
      >
        <a-input v-model:model-value="form.name" :placeholder="t('space.models.namePlaceholder')" />
      </a-form-item>

      <a-form-item field="label" :label="t('space.models.label')">
        <a-input v-model:model-value="form.label" :placeholder="t('space.models.labelPlaceholder')" />
      </a-form-item>

      <a-form-item
        field="api_key"
        :label="t('space.models.apiKey')"
        asterisk-position="end"
        :rules="[{ required: true, message: t('space.models.apiKeyRequired') }]"
      >
        <a-input-password
          v-model:model-value="form.api_key"
          :placeholder="t('space.models.apiKeyPlaceholder')"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="base_url"
        :label="t('space.models.baseUrl')"
        asterisk-position="end"
        :rules="[{ required: true, message: t('space.models.baseUrlRequired') }]"
      >
        <a-input v-model:model-value="form.base_url" :placeholder="t('space.models.baseUrlPlaceholder')" />
      </a-form-item>

      <a-form-item field="model_list" :label="t('space.models.modelList')" asterisk-position="end">
        <div class="w-full space-y-2">
          <div
            v-for="(row, index) in form.models"
            :key="index"
            class="flex items-center gap-2"
          >
            <a-input
              v-model:model-value="row.name"
              :placeholder="t('space.models.modelPlaceholder')"
              class="flex-1"
            />
            <a-input
              v-model:model-value="row.label"
              :placeholder="t('space.models.label')"
              class="w-[160px]"
            />
            <a-button type="text" class="!text-red-600" size="small" @click="removeModelRow(index)">
              <template #icon><icon-delete :size="16" /></template>
            </a-button>
          </div>
          <a-button size="small" class="rounded-lg" @click="addModelRow">
            <template #icon><icon-plus :size="14" /></template>
            {{ t('space.models.addModel') }}
          </a-button>
        </div>
      </a-form-item>

      <a-form-item field="features" :label="t('space.models.features')">
        <a-checkbox-group v-model:model-value="form.features">
          <a-checkbox value="tool_call">{{ t('space.models.featureToolCall') }}</a-checkbox>
          <a-checkbox value="agent_thought">{{ t('space.models.featureAgentThought') }}</a-checkbox>
          <a-checkbox value="image_input">{{ t('space.models.featureImageInput') }}</a-checkbox>
        </a-checkbox-group>
      </a-form-item>

      <div class="grid grid-cols-2 gap-4">
        <a-form-item field="context_window" :label="t('space.models.contextWindow')">
          <a-input-number v-model:model-value="form.context_window" :min="0" :step="1024" class="w-full" />
        </a-form-item>
        <a-form-item field="max_output_tokens" :label="t('space.models.maxOutputTokens')">
          <a-input-number v-model:model-value="form.max_output_tokens" :min="0" :step="256" class="w-full" />
        </a-form-item>
      </div>

      <a-form-item field="is_active" :label="t('space.models.isActive')">
        <a-switch v-model:model-value="form.is_active" />
      </a-form-item>

      <div v-if="testResult" class="mb-4 rounded-lg border p-3 text-xs leading-5" :class="testResult.ok ? 'border-green-200 bg-green-50 text-green-800' : 'border-red-200 bg-red-50 text-red-800'">
        {{ testResult.message }}
      </div>

      <div class="flex items-center justify-between gap-3 pt-2">
        <a-button size="large" class="rounded-lg" :loading="testing" @click="handleTest">
          {{ testing ? t('space.models.testing') : t('space.models.testConnection') }}
        </a-button>
        <div class="flex items-center gap-3">
          <a-button size="large" html-type="button" class="rounded-lg px-6" @click="hideModal">
            {{ t('common.actions.cancel') }}
          </a-button>
          <a-button :loading="submitLoading" type="primary" html-type="submit" size="large" class="rounded-lg px-6">
            {{ t('common.actions.save') }}
          </a-button>
        </div>
      </div>
    </a-form>
  </a-modal>
</template>

<style scoped>
.custom-model-form :deep(.arco-form-item-label) {
  font-weight: 500;
}

.custom-model-modal-shell {
  width: min(96vw, 680px);
}
</style>
