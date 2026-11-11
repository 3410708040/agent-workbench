import { type BaseResponse } from '@/models/base'

// 自定义模型提供商（模型管理界面）
export type CustomModelItem = {
  id: string
  name: string
  label: string
  api_key: string
  base_url: string
  model_type: string
  model_names: string[]
  features: string[]
  context_window: number
  max_output_tokens: number
  is_active: boolean
  created_at?: number
  updated_at?: number
}

// 创建/更新自定义模型请求
export type CreateCustomModelRequest = {
  name: string
  label?: string
  api_key: string
  base_url: string
  model_type?: string
  models: Array<{ name: string; label?: string }>
  features?: string[]
  context_window?: number
  max_output_tokens?: number
  is_active?: boolean
}

// 测试连接响应
export type TestCustomModelResponse = BaseResponse<{
  ok: boolean
  model?: string
  message: string
  response?: string
}>
