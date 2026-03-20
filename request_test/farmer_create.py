import requests
from datetime import datetime, UTC

def test_create_farmer():
    url = "http://localhost:8000/farmer_auth/create"
    payload = {
        "first_name": "Nelly",
        "last_name": "Isimbi Assoumpta",
        "email": "i.assoumpta@alustudent.com",
        "phone_number": "0782658179",
        "password": "Pilau",
        "role": "farmer"
    }

    response = requests.post(url=url, json=payload)
    response.raise_for_status()
    print(response.json())

def test_create_buyer():
    url = "http://localhost:8000/buyers_auth/create"
    payload = {
  "first_name": "Bode",
  "last_name": "Murairi",
  "email": "bodemurairi2@gmail.com",
  "phone_number": "250795020998",
  "password": "bodemurairi2",
  "role": "buyer",
  "country": "Rwanda",
  "city": "Kigali City",
  "location": "KG 11 AV 128 Kimironko"
}
    response = requests.post(url=url, json=payload)
    response.raise_for_status()
    print(response.json())



if __name__ == "__main__":
    #test_create_farmer()
    test_create_buyer()
