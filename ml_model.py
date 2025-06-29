# ml_model.py
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_next_month_from_csv(csv_file='exp.csv'):
    try:
        df = pd.read_csv(csv_file)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month

        monthly_totals = df.groupby(['year', 'month'])['amount'].sum().reset_index()

        if len(monthly_totals) < 2:
            return None, None, 0.0

        X = monthly_totals[['year', 'month']]
        y = monthly_totals['amount']

        model = LinearRegression()
        model.fit(X, y)

        last_year = monthly_totals.iloc[-1]['year']
        last_month = monthly_totals.iloc[-1]['month']

        if last_month == 12:
            next_month = 1
            next_year = last_year + 1
        else:
            next_month = last_month + 1
            next_year = last_year

        prediction = model.predict([[next_year, next_month]])[0]
        return next_year, next_month, round(max(prediction, 0), 2)

    except Exception as e:
        print("Prediction Error:", e)
        return None, None, 0.0

