# Requirements Checklist

| Requirement | Implementation | Verification | Status |
| --- | --- | --- | --- |
| Load actual CSV and inspect columns | `notebooks/house_price_model.ipynb`, `src/training.py` | CSV read: 187,531 x 21 | PASS |
| Price, area, floor, numeric parsing | `src/training.py` | Training completed on real CSV | PASS |
| Group top locations and remove ratio outliers | `src/training.py` | 176,293 cleaned rows | PASS |
| Four EDA plots with interpretation | notebook | Executed notebook has four labelled chart outputs | PASS |
| Pipeline with imputation and one-hot encoding | `src/training.py` | Exported pipeline reload prediction succeeded | PASS |
| Linear Regression and Random Forest metrics | `models/model_metrics.csv` | Held-out MAE/RMSE/R² recorded | PASS |
| Export pipeline and location list | `models/` | `.pkl` reload and JSON written | PASS |
| FastAPI health and prediction endpoints | `backend/app/` | Pytest TestClient coverage | PASS |
| Valid and invalid backend tests | `backend/tests/test_prediction.py` | `2 passed` | PASS |
| React form, validation, routes, result, 404 | `frontend/src/` | Typechecked production build | PASS |
| Frontend production build | `frontend/` | `npm run build` succeeded | PASS |
| End-to-end API flow | Backend + frontend contract | Started FastAPI and made real HTTP health/prediction requests | PASS |
| Professional README | `README.md` | Manual review | PASS |
| No Git/GitHub operation performed | N/A | No Git commands run | PASS |
