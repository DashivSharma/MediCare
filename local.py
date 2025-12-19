import os
import requests
import re
import time
from typing import List, Dict, Any, Optional


class StandaloneDoctorFinder:
    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.overpass_base_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DoctorFinderBot/1.0 (Educational Project)'
        })
        # Your contact details (CHANGE THESE)
        self.partner_phone = "+91-9466140838"
        self.partner_email = "dashivsharma@gmail.com"


    # -------------------- NER for specialty & location --------------------
    def extract_doctor_info(self, user_input: str) -> Dict[str, str]:
        user_input_lower = user_input.lower()

        specialties = {
            "cardiologist": "cardiologist",
            "cardiac": "cardiologist",
            "heart": "cardiologist",
            "dermatologist": "dermatologist",
            "skin": "dermatologist",
            "orthopedic": "orthopedic surgeon",
            "bone": "orthopedic surgeon",
            "joint": "orthopedic surgeon",
            "neurologist": "neurologist",
            "brain": "neurologist",
            "nerve": "neurologist",
            "pediatrician": "pediatrician",
            "child": "pediatrician",
            "gynecologist": "gynecologist",
            "women": "gynecologist",
            "psychiatrist": "psychiatrist",
            "mental": "psychiatrist",
            "dentist": "dentist",
            "teeth": "dentist",
            "eye": "ophthalmologist",
            "vision": "ophthalmologist",
            "ent": "ENT specialist",
            "ear": "ENT specialist",
            "nose": "ENT specialist",
            "throat": "ENT specialist",
            "general": "general physician",
            "physician": "general physician",
            "oncologist": "oncologist",
            "cancer": "oncologist",
            "urologist": "urologist",
            "kidney": "urologist",
            "endocrinologist": "endocrinologist",
            "diabetes": "endocrinologist",
            "pulmonologist": "pulmonologist",
            "lung": "pulmonologist",
            "gastroenterologist": "gastroenterologist",
            "stomach": "gastroenterologist",
        }

        specialty = "general physician"
        for keyword, spec in specialties.items():
            if keyword in user_input_lower:
                specialty = spec
                break

        location_patterns = [
            r"in\s+([a-zA-Z\s]+?)(?:\s|$|,)",
            r"near\s+([a-zA-Z\s]+?)(?:\s|$|,)",
            r"at\s+([a-zA-Z\s]+?)(?:\s|$|,)",
            r"around\s+([a-zA-Z\s]+?)(?:\s|$|,)",
        ]

        location = "Delhi"
        for pattern in location_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                potential = match.group(1).strip()
                if len(potential) > 2:
                    location = potential.title()
                    break

        return {"specialty": specialty, "location": location}

    # -------------------- Mock fallback --------------------
    def get_mock_doctors(self, specialty: str, location: str) -> List[Dict[str, Any]]:
        doctor_names = [
            "Dr. Rajesh Sharma", "Dr. Priya Gupta", "Dr. Amit Kumar",
            "Dr. Sneha Patel", "Dr. Vikram Singh", "Dr. Anita Verma"
        ]
        hospitals = [
            "City Hospital", "Medical Center", "Healthcare Clinic",
            "Super Specialty Hospital", "Prime Healthcare", "Metro Hospital"
        ]
        doctors = []
        for i in range(6):
            doctors.append({
                "name": doctor_names[i],
                "specialty": specialty,
                "address": f"{hospitals[i]}, {location}",
                "rating": round(3.8 + i * 0.15, 1),
                "phone": f"+91-987654{3210 + i}",
                "availability": "Mon-Fri 9AM-6PM",
                "distance": f"{1.5 + (i * 0.4):.1f} km",
                "experience": f"{8 + (i * 2)} years",
                "consultation_fee": f"₹{300 + (i * 50)}-{400 + (i * 50)}",
                "source": "Mock Data"
            })
        doctors.insert(3, self.get_partner_clinic(specialty, location))
        return doctors


    # -------------------- Nominatim + Overpass --------------------
    def geocode_location(self, location: str) -> Optional[Dict[str, float]]:
        try:
            import requests

            # Create a clean, isolated session to avoid LangChain interference
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'DoctorFinderBot/1.0 (Standalone)',
                'Accept': 'application/json'
            })

            url = f"{self.nominatim_base_url}/search"
            params = {"q": f"{location}, India", "format": "json", "limit": 1}
            res = session.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data:
                return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
            else:
                print("⚠ Empty geocoding response.")
        except Exception as e:
            print(f"⚠️ Geocoding error: {e}")
        return None

    def find_doctors_overpass(self, specialty: str, lat: float, lng: float) -> List[Dict[str, Any]]:
        try:
            radius_m = 5000
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="hospital"](around:{radius_m},{lat},{lng});
              node["amenity"="clinic"](around:{radius_m},{lat},{lng});
              node["healthcare"="doctor"](around:{radius_m},{lat},{lng});
            );
            out center;
            """
            res = self.session.post(self.overpass_base_url, data=query, timeout=30)
            res.raise_for_status()
            data = res.json()
            doctors = []
            for el in data.get("elements", [])[:10]:
                tags = el.get("tags", {})
                name = tags.get("name", "Healthcare Facility")
                address = tags.get("addr:city", "Address not available")
                doctors.append({
                    "name": name,
                    "specialty": specialty,
                    "address": address,
                    "rating": 4.0,
                    "phone": tags.get("phone", "Contact facility"),
                    "availability": "Mon-Sat 10AM-6PM",
                    "distance": "Nearby",
                    "facility_type": tags.get("amenity", "Clinic"),
                    "source": "OpenStreetMap"
                })
            doctors.insert(3, self.get_partner_clinic(specialty, "Nearby"))
            return doctors

        except Exception as e:
            print(f"⚠️ Overpass API error: {e}")
            return []

    # -------------------- Main Search --------------------
    def find_doctors(self, specialty: str, location: str) -> List[Dict[str, Any]]:
        print(f"🔍 Searching for {specialty} in {location}...")
        coords = self.geocode_location(location)
        if coords:
            print(f"📍 Location: {coords['lat']:.4f}, {coords['lng']:.4f}")
            doctors = self.find_doctors_overpass(specialty, coords["lat"], coords["lng"])
            if doctors:
                print(f"✅ Found {len(doctors)} facilities (OpenStreetMap)")
                return doctors
            else:
                print("⚠ No real facilities found, using mock data.")
        else:
            print("⚠ Could not geocode location, using mock data.")
        return self.get_mock_doctors(specialty, location)

    # -------------------- Display --------------------
    def display_doctors(self, doctors: List[Dict[str, Any]], specialty: str, location: str):
        if not doctors:
            print(f"\n❌ No {specialty} doctors found near {location}")
            return
        print(f"\n✅ Found {len(doctors)} {specialty} doctors near {location}")
        print("=" * 60)
        for i, d in enumerate(doctors, 1):
            print(f"{i}. 👨‍⚕ {d['name']}  ({d['specialty']})")
            print(f"   🏥 {d['address']}")
            print(f"   ⭐ {d['rating']} / 5   📞 {d['phone']}")
            print(f"   🕐 {d['availability']}   📏 {d['distance']}")
            print(f"   Source: {d['source']}")
            print("-" * 60)

    # -------------------- Chatbot Interface --------------------
    def run(self):
        print("=" * 60)
        print("🏥 OFFLINE DOCTOR FINDER CHATBOT (Free APIs only)")
        print("=" * 60)
        while True:
            user_input = input("\n💬 You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("👋 Stay healthy! Exiting...")
                break
            info = self.extract_doctor_info(user_input)
            docs = self.find_doctors(info["specialty"], info["location"])
            self.display_doctors(docs, info["specialty"], info["location"])


    #Partner Clinic
    def get_partner_clinic(self, specialty: str, location: str):
        return {
            "name": "MediCare AI Partner Clinic",
            "specialty": specialty,
            "address": "Online Appointment Assistance",
            "rating": 4.9,
            "phone": self.partner_phone,
            "email": self.partner_email,
            "availability": "24/7 Online",
            "distance": "Virtual",
            "source": "MediCare AI (Partner)",
            "is_partner": True
        }



if __name__ == "__main__":
    finder = StandaloneDoctorFinder()
    finder.run()
