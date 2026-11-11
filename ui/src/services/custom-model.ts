import { get, post, put, del } from '@/utils/request'
import type { BaseResponse } from '@/models/base'
import type {
  CreateCustomModelRequest,
  CustomModelItem,
  TestCustomModelResponse,
} from '@/models/custom-model'

// 获取全部自定义模型提供商
export const getCustomModels = () => {
  return get<BaseResponse<CustomModelItem[]>>('/language-model-providers')
}

// 添加自定义模型提供商
export const createCustomModel = (req: CreateCustomModelRequest) => {
  return post<BaseResponse<unknown>>('/language-model-providers', { body: req })
}

// 更新自定义模型提供商
export const updateCustomModel = (provider_id: string, req: CreateCustomModelRequest) => {
  return put<BaseResponse<unknown>>(`/language-model-providers/${provider_id}`, { body: req })
}

// 删除自定义模型提供商
export const deleteCustomModel = (provider_id: string) => {
  return del<BaseResponse<unknown>>(`/language-model-providers/${provider_id}`)
}

// 测试自定义模型连接
export const testCustomModel = (provider_id: string, model_name?: string) => {
  return post<TestCustomModelResponse>(`/language-model-providers/${provider_id}/test`, {
    body: { model_name: model_name || '' },
  })
}

// 根据未保存的表单内容测试连接（添加时直接测试，不落库）
export const testCustomModelPayload = (req: CreateCustomModelRequest) => {
  return post<TestCustomModelResponse>('/language-model-providers/test', { body: req })
}
