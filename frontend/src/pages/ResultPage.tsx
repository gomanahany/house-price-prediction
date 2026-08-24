import { Link, useLocation } from 'react-router-dom'
import type { PredictionResponse } from '../types/prediction'
function formatPrice(value: number) { return value >= 10_000_000 ? `₹ ${(value / 10_000_000).toFixed(2)} Cr` : `₹ ${(value / 100_000).toFixed(2)} Lac` }
export function ResultPage() { const result = useLocation().state as PredictionResponse | null; if (!result) return <main><h1>No prediction yet</h1><Link to="/">Return to the form</Link></main>; return <main><h1>Your estimated price</h1><p className="price">{formatPrice(result.predicted_price)}</p><p>Exact estimate: ₹ {result.predicted_price.toLocaleString('en-IN', {maximumFractionDigits: 0})}</p><Link to="/">Estimate another property</Link></main> }
