import type { PredictionRequest, PredictionResponse } from '../types/prediction'
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
export async function predictHousePrice(payload: PredictionRequest): Promise<PredictionResponse> {
  const response = await fetch(`${baseUrl}/predict`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) })
  if (!response.ok) throw new Error('The prediction service could not process your request. Please try again.')
  return response.json()
}
