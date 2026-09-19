from interpretation_engine import interpret_chart
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
from vedic_engine import build_report
from interpretation import generate_interpretation
from timing import timing_signals

app = Flask(__name__)

# Starter place directory: deliberately bundled so the first version needs no paid
# geocoding API. More places can be added later or replaced with an open geocoder.
PLACES = [
('Udaipur, Rajasthan, India',24.5854,73.7125,'Asia/Kolkata'),('Jaipur, Rajasthan, India',26.9124,75.7873,'Asia/Kolkata'),
('Jodhpur, Rajasthan, India',26.2389,73.0243,'Asia/Kolkata'),('Kota, Rajasthan, India',25.2138,75.8648,'Asia/Kolkata'),('Ajmer, Rajasthan, India',26.4499,74.6399,'Asia/Kolkata'),
('Delhi, India',28.6139,77.2090,'Asia/Kolkata'),('Mumbai, Maharashtra, India',19.0760,72.8777,'Asia/Kolkata'),('Pune, Maharashtra, India',18.5204,73.8567,'Asia/Kolkata'),('Nagpur, Maharashtra, India',21.1458,79.0882,'Asia/Kolkata'),
('Bengaluru, Karnataka, India',12.9716,77.5946,'Asia/Kolkata'),('Hyderabad, Telangana, India',17.3850,78.4867,'Asia/Kolkata'),('Chennai, Tamil Nadu, India',13.0827,80.2707,'Asia/Kolkata'),('Kolkata, West Bengal, India',22.5726,88.3639,'Asia/Kolkata'),
('Ahmedabad, Gujarat, India',23.0225,72.5714,'Asia/Kolkata'),('Surat, Gujarat, India',21.1702,72.8311,'Asia/Kolkata'),('Lucknow, Uttar Pradesh, India',26.8467,80.9462,'Asia/Kolkata'),
('Kanpur, Uttar Pradesh, India',26.4499,80.3319,'Asia/Kolkata'),('Varanasi, Uttar Pradesh, India',25.3176,82.9739,'Asia/Kolkata'),('Patna, Bihar, India',25.5941,85.1376,'Asia/Kolkata'),
('Bhopal, Madhya Pradesh, India',23.2599,77.4126,'Asia/Kolkata'),('Indore, Madhya Pradesh, India',22.7196,75.8577,'Asia/Kolkata'),('Chandigarh, India',30.7333,76.7794,'Asia/Kolkata'),
('Dehradun, Uttarakhand, India',30.3165,78.0322,'Asia/Kolkata'),('Guwahati, Assam, India',26.1445,91.7362,'Asia/Kolkata'),('Bhubaneswar, Odisha, India',20.2961,85.8245,'Asia/Kolkata'),
('Ranchi, Jharkhand, India',23.3441,85.3096,'Asia/Kolkata'),('Raipur, Chhattisgarh, India',21.2514,81.6296,'Asia/Kolkata'),('Srinagar, Jammu and Kashmir, India',34.0837,74.7973,'Asia/Kolkata'),
('Amritsar, Punjab, India',31.6340,74.8723,'Asia/Kolkata'),('Shimla, Himachal Pradesh, India',31.1048,77.1734,'Asia/Kolkata'),('Goa, India',15.2993,74.1240,'Asia/Kolkata'),
('Kathmandu, Nepal',27.7172,85.3240,'Asia/Kathmandu'),('Dubai, UAE',25.2048,55.2708,'Asia/Dubai'),('Singapore, Singapore',1.3521,103.8198,'Asia/Singapore'),
('London, United Kingdom',51.5074,-0.1278,'Europe/London'),('New York, USA',40.7128,-74.0060,'America/New_York'),('Los Angeles, USA',34.0522,-118.2437,'America/Los_Angeles'),
('Toronto, Canada',43.6532,-79.3832,'America/Toronto'),('Sydney, Australia',-33.8688,151.2093,'Australia/Sydney'),('Melbourne, Australia',-37.8136,144.9631,'Australia/Melbourne'),
('Doha, Qatar',25.2854,51.5310,'Asia/Qatar'),('Abu Dhabi, UAE',24.4539,54.3773,'Asia/Dubai'),('Kuala Lumpur, Malaysia',3.1390,101.6869,'Asia/Kuala_Lumpur'),
('Auckland, New Zealand',-36.8509,174.7645,'Pacific/Auckland'),('San Francisco, USA',37.7749,-122.4194,'America/Los_Angeles'),('Chicago, USA',41.8781,-87.6298,'America/Chicago')
]
PLACE_MAP = {p[0]: {'name':p[0],'latitude':p[1],'longitude':p[2],'timezone':p[3]} for p in PLACES}



def enrich_chart(chart):
    try:
        chart["interpretation"] = interpret_chart(chart)
    except Exception as exc:
        chart["interpretation_error"] = str(exc)
    return chart
@app.get('/')
def home(): return render_template('index.html')

@app.get('/api/places')
def api_places():
    q=request.args.get('q','').strip().lower()
    if len(q)<1: return jsonify([])
    out=[p for p in PLACES if q in p[0].lower()][:12]
    return jsonify([{'name':p[0],'latitude':p[1],'longitude':p[2],'timezone':p[3]} for p in out])

@app.post('/api/chart')
def api_chart():
    try:
        data=request.get_json(force=True)
        if not all(k in data for k in ['date','time']): return jsonify({'error':'Date and time are required.'}),400
        place=data.get('place')
        if place and place in PLACE_MAP:
            p=PLACE_MAP[place]; lat,lon,tz=p['latitude'],p['longitude'],p['timezone']
            dt=datetime.fromisoformat(f"{data['date']}T{data['time']}").replace(tzinfo=ZoneInfo(tz))
            offset=dt.utcoffset().total_seconds()/3600
            result=build_report(data['date'],data['time'],lat,lon,offset)
            result['meta'].update({'place':p['name'],'timezone':tz,'utc_offset_hours':offset})
        else:
            required=['latitude','longitude','utc_offset']
            if any(k not in data for k in required): return jsonify({'error':'Select a birth place or provide coordinates.'}),400
            result=build_report(data['date'],data['time'],float(data['latitude']),float(data['longitude']),float(data['utc_offset']))
        result['interpretation']=generate_interpretation(result, data.get('language','hinglish'))
        result['timing']=timing_signals(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error':str(e)}),400

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=True)
