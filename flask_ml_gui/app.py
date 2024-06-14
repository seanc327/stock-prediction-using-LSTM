from flask import Flask, render_template, request
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# Load your pre-trained machine learning model
model = load_model('lstm-2.h5')

# Function to preprocess the input data
def preprocess_data(filepath):
    data = pd.read_csv(filepath)
    data.drop(["volume", "avg_vol_20d"], inplace=True, axis=1)
    data.fillna(0.57, inplace=True)
    try:
        data["date"] = pd.to_datetime(data["date"], format='%Y%m%d')
    except ValueError:
        data["date"] = pd.to_datetime(data["date"], infer_datetime_format=True)
    data["date_str"] = data["date"].dt.strftime("%Y-%m-%d")
    
    # Scaling the necessary columns for LSTM
    scaler = MinMaxScaler()
    scaler.fit(data[['close', 'change_percent', 'open']])
    scaled_data = scaler.transform(data[['close', 'change_percent', 'open']])
    
    return scaled_data, data["date_str"], scaler

# Function to create features for the LSTM model
def create_features(data, time_steps):
    X = []
    for i in range(len(data) - time_steps + 1):
        X.append(data[i:i+time_steps])
    return np.array(X)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = 'uploaded_data.csv'
            file.save(filepath)
            try:
                # Preprocess data and create features
                scaled_data, date_str, scaler = preprocess_data(filepath)
                time_steps = 24
                features = create_features(scaled_data, time_steps)

                features = features.astype('float32')

                # Reshape features to match expected input shape
                features = features.reshape(-1, time_steps, 3)
                
                # Predict market crash
                predictions = model.predict(features)
                
                # Inverse transform predictions
                shapematch = np.repeat(predictions, scaled_data.shape[1], axis=-1)
                y_pred = scaler.inverse_transform(shapematch)[:, 0]

                # Use the last date in the dataset as the start date for predictions
                last_date = pd.to_datetime(date_str.iloc[-1])
                prediction_dates = pd.date_range(start=last_date, periods=len(predictions), freq='D')

                # Create a DataFrame for forecasted data
                df_forecast = pd.DataFrame({'date': prediction_dates, 'close': y_pred})
                
                # Plot the predicted values
                plt.figure(figsize=(10, 5))
                sns.lineplot(x='date', y='close', data=df_forecast, label='Prediction', color='orange')
                plt.title('S&P 500 Prediction Graph')
                plt.xlabel('Date')
                plt.ylabel('Close Price')
                plt.legend()
                plt.grid(True)
                
                # Convert plot to a base64-encoded image
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plot_data = base64.b64encode(buffer.getvalue()).decode()
                plt.close()  # Close the plot to prevent it from being displayed in the browser
                
                # Pass predictions and plot data to the result.html template
                return render_template('result.html', predictions=predictions, plot_data=plot_data)
            
            except Exception as e:
                return str(e), 500
        return render_template('upload.html')

    else:
        return "Something went wrong. Please try again."



if __name__ == "__main__":
    app.run(debug=True)