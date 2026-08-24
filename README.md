# ITI House Price Prediction

An end-to-end machine-learning web application that estimates Indian property prices from listing details. It cleans the supplied Kaggle dataset, trains and exports a scikit-learn pipeline, serves it through FastAPI, and presents a React + TypeScript form.

## Architecture

`CSV -> notebook/training pipeline -> models/house_price.pkl -> FastAPI /predict -> React form -> result page`

## Tech stack

Python 3.11, Pandas, scikit-learn, Jupyter, FastAPI, Pydantic, React, TypeScript, and Vite.

## Dataset

Source: [House Price by Juhi Bhojani](https://www.kaggle.com/datasets/juhibhojani/house-price). Download `house_prices.csv` and put it in `data/house_prices.csv`. The raw CSV is deliberately excluded from version control because it is large.

## Project structure

```
data/                         raw CSV (local only)
notebooks/house_price_model.ipynb
src/training.py               shared cleaning/training workflow
models/                       exported pipeline, locations, metrics
backend/                      FastAPI application and tests
frontend/                     React + TypeScript + Vite application
```

## Measured model result

The supplied CSV contains 187,531 rows and 21 columns. After target parsing and outlier filtering, 176,293 rows remained. The model uses carpet area, floor, bathroom, balcony, grouped location, furnishing, transaction, ownership, and facing.

| Model | Test MAE | Test RMSE | Test R² |
| --- | ---: | ---: | ---: |
| RandomForestRegressor | 1,405,683 INR | 5,563,194 INR | 0.8346 |
| LinearRegression | 4,715,094 INR | 8,788,544 INR | 0.5872 |

Selected model: **RandomForestRegressor**, because it achieved the lowest held-out-test RMSE and the highest R². Exact machine-readable metrics are in `models/model_metrics.csv`.

## Run locally

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the notebook from the project root, or rebuild the model directly:

```powershell
python -c "from src.training import train_and_export; train_and_export('data/house_prices.csv', 'models')"
Copy-Item models\house_price.pkl,models\locations.json backend\models\
Copy-Item models\locations.json frontend\src\data\locations.json
```

Start the backend:

```powershell
cd backend
..\.venv\Scripts\uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Environment variables

| File | Variable | Value |
| --- | --- | --- |
| `backend/.env` | `MODEL_PATH` | `models/house_price.pkl` |
| `backend/.env` | `ALLOWED_ORIGIN` | `http://localhost:5173` |
| `frontend/.env` | `VITE_API_BASE_URL` | `http://localhost:8000` |

Copy the included `.env.example` files before changing any values.

## API

`GET /health` returns `{ "status": "ok" }`.

`POST /predict` accepts property details and returns `{ "predicted_price": <float> }`.

```powershell
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"location":"other","carpet_area_sqft":800,"floor_num":3,"bathroom":2,"balcony":1,"furnishing":"Semi-Furnished","transaction":"Resale","ownership":"Freehold","facing":"East"}'
```

## Checks

```powershell
$env:PYTHONPATH = (Resolve-Path backend).Path
python -m pytest backend/tests -q
cd frontend; npm run build
```

## Screenshots

The application includes a React frontend for entering property details and displaying the predicted house price, with a FastAPI backend serving the machine-learning model.
