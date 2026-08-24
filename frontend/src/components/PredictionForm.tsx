import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import locations from '../data/locations.json'
import { predictHousePrice } from '../api/predictionClient'
import type { PredictionRequest } from '../types/prediction'

const options = { furnishing: ['Furnished', 'Semi-Furnished', 'Unfurnished'], transaction: ['New Property', 'Resale'], ownership: ['Freehold', 'Co-operative Society', 'Leasehold', 'Power Of Attorney'], facing: ['East', 'West', 'North', 'South', 'North - East', 'North - West', 'South - East', 'South - West'] }
const initial: PredictionRequest = { location: '', carpet_area_sqft: 0, floor_num: 0, bathroom: 0, balcony: 0, car_parking: 0, furnishing: '', transaction: '', ownership: '', facing: '' }
const labels: Record<keyof PredictionRequest, string> = { location: 'Location', carpet_area_sqft: 'Carpet area', floor_num: 'Floor', bathroom: 'Bathrooms', balcony: 'Balconies', car_parking: 'Car parking', furnishing: 'Furnishing', transaction: 'Transaction', ownership: 'Ownership', facing: 'Facing' }
const numericFields: Array<keyof PredictionRequest> = ['carpet_area_sqft', 'floor_num', 'bathroom', 'balcony', 'car_parking']

export function PredictionForm() {
  const [form, setForm] = useState(initial); const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const navigate = useNavigate()
  const update = (name: keyof PredictionRequest, value: string) => setForm(current => ({ ...current, [name]: numericFields.includes(name) ? Number(value) : value }))
  function validate(): string {
    for (const field of Object.keys(labels) as Array<keyof PredictionRequest>) {
      if (field === 'carpet_area_sqft') continue
      if (typeof form[field] === 'string' && !form[field]) return `Please select ${labels[field].toLowerCase()}.`
    }
    if (form.carpet_area_sqft <= 0) return 'Carpet area must be greater than zero.'
    if (form.bathroom < 0 || form.balcony < 0 || form.car_parking < 0) return 'Bathrooms, balconies, and car parking cannot be negative.'
    return ''
  }
  async function submit(event: FormEvent) { event.preventDefault(); const validationError = validate(); if (validationError) { setError(validationError); return }; setLoading(true); setError(''); try { const result = await predictHousePrice(form); navigate('/result', { state: result }) } catch (err) { setError(err instanceof Error ? err.message : 'An unexpected error occurred.') } finally { setLoading(false) } }
  return <form onSubmit={submit} className="form" noValidate>{error && <p role="alert" className="error">{error}</p>}<label>Location<select value={form.location} onChange={e => update('location', e.target.value)}><option value="">Choose a location</option>{locations.map(location => <option key={location}>{location}</option>)}</select></label><label>Carpet area (sq ft)<input min="0.01" step="any" type="number" value={form.carpet_area_sqft || ''} onChange={e => update('carpet_area_sqft', e.target.value)} /></label><label>Floor<input type="number" value={form.floor_num} onChange={e => update('floor_num', e.target.value)} /></label><label>Bathrooms<input min="0" type="number" value={form.bathroom} onChange={e => update('bathroom', e.target.value)} /></label><label>Balconies<input min="0" type="number" value={form.balcony} onChange={e => update('balcony', e.target.value)} /></label><label>Car parking<input min="0" type="number" value={form.car_parking} onChange={e => update('car_parking', e.target.value)} /></label>{(Object.keys(options) as Array<keyof typeof options>).map(key => <label key={key}>{labels[key]}<select value={form[key]} onChange={e => update(key, e.target.value)}><option value="">Choose {labels[key].toLowerCase()}</option>{options[key].map(value => <option key={value}>{value}</option>)}</select></label>)}<button disabled={loading}>{loading ? 'Calculating…' : 'Predict price'}</button></form>
}
