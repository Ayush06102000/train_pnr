from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb+srv://ayushkumar:Ayush%40123@cluster0.ruhlgi4.mongodb.net/')
db = client['pnr_database']
collection = db['pnr_collection']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pnr = request.form['pnr']
        url = f"https://www.confirmtkt.com/pnr-status/{pnr}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad response status
            soup = BeautifulSoup(response.content, 'html.parser')
            a = str(soup.find_all('script')[13]).split(";")
            data = a[3]
            data = str(data)
            finaldata = data[11:]
            data_dict = json.loads(finaldata)

            passenger_booking_status = [passenger['BookingStatus'] for passenger in data_dict['PassengerStatus']]
            passenger_current_status = [passenger['CurrentStatus'] for passenger in data_dict['PassengerStatus']]
            train_source = data_dict['To']
            train_destination = data_dict['From']
            train_name = data_dict['TrainName']
            classs = data_dict['Class']

            # Store data in MongoDB
            pnr_data = {
                'PNR': pnr,
                'BookingStatus': passenger_booking_status,
                'CurrentStatus': passenger_current_status,
                'TrainSource': train_source,
                'TrainDestination': train_destination,
                'TrainName': train_name,
                'Class': classs
            }
            collection.insert_one(pnr_data)

            return render_template('index.html', booking_status=passenger_booking_status, current_status=passenger_current_status,
                                   train_source=train_source, train_destination=train_destination, train_name=train_name, classes=classs)
        
        except Exception as e:
            error_message = "Invalid PNR number or an error occurred. Please try again."
            return render_template('index.html', error_message=error_message)

    return render_template('index.html', booking_status=None, current_status=None, train_source=None, train_destination=None, train_name=None)

if __name__ == '__main__':
    app.run(debug=True,port=8000)
