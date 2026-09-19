import swisseph as swe
from datetime import datetime, timezone, timedelta

SIGNS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
SIGN_HI = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]
GRAHAS = {"Surya": swe.SUN, "Chandra": swe.MOON, "Mangala": swe.MARS, "Budha": swe.MERCURY, "Guru": swe.JUPITER, "Shukra": swe.VENUS, "Shani": swe.SATURN, "Rahu": swe.TRUE_NODE}
NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Shukra","Surya","Chandra","Mangala","Rahu","Guru","Shani","Budha"] * 3
VIM_ORDER = ["Ketu","Shukra","Surya","Chandra","Mangala","Rahu","Guru","Shani","Budha"]
VIM_YEARS = {"Ketu":7,"Shukra":20,"Surya":6,"Chandra":10,"Mangala":7,"Rahu":18,"Guru":16,"Shani":19,"Budha":17}
PLANET_HI = {"Surya":"सूर्य","Chandra":"चंद्र","Mangala":"मंगल","Budha":"बुध","Guru":"गुरु","Shukra":"शुक्र","Shani":"शनि","Rahu":"राहु","Ketu":"केतु"}


def norm(x): return x % 360.0
def sign_index(lon): return int(norm(lon) // 30)

def nakshatra(lon):
    x = norm(lon); span = 360/27
    n = min(26, int(x/span)); within = x - n*span
    pada = min(4, int(within/(span/4))+1)
    return NAKSHATRAS[n], pada, NAK_LORDS[n]

def navamsa_sign(lon):
    r = sign_index(lon); part = min(8, int((norm(lon)%30)/(30/9)))
    # Movable starts same sign; fixed starts 9th from sign; dual starts 5th.
    if r in (0,3,6,9): start = r
    elif r in (1,4,7,10): start = (r + 8) % 12
    else: start = (r + 4) % 12
    return (start + part) % 12

def _planet_obj(name, lon, speed):
    nk,pada,nlord = nakshatra(lon)
    return {"longitude":round(norm(lon),6), "rashi":SIGNS[sign_index(lon)], "rashi_hi":SIGN_HI[sign_index(lon)],
            "degree_in_rashi":round(norm(lon)%30,6), "retrograde":bool(speed < 0),
            "nakshatra":nk, "pada":pada, "nakshatra_lord":nlord,
            "navamsa_rashi":SIGNS[navamsa_sign(lon)], "navamsa_rashi_hi":SIGN_HI[navamsa_sign(lon)]}

def calc(jd_ut, lat, lon):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {"ayanamsha":"Lahiri / Chitrapaksha", "grahas":{}}
    for name,pid in GRAHAS.items():
        xx,_ = swe.calc_ut(jd_ut,pid,flags)
        out["grahas"][name] = _planet_obj(name,xx[0],xx[3])
    r = out["grahas"]["Rahu"]["longitude"]; out["grahas"]["Ketu"] = _planet_obj("Ketu",r+180,0)
    # Use Swiss Ephemeris ascendant; whole-sign house assignment is then derived from Lagna sign.
    _, ascmc = swe.houses_ex(jd_ut,float(lat),float(lon),b'P',swe.FLG_SIDEREAL)
    asc = norm(ascmc[0]); asc_sign = sign_index(asc)
    out["lagna"] = {"longitude":round(asc,6),"rashi":SIGNS[asc_sign],"rashi_hi":SIGN_HI[asc_sign],"degree_in_rashi":round(asc%30,6),"navamsa_rashi":SIGNS[navamsa_sign(asc)],"navamsa_rashi_hi":SIGN_HI[navamsa_sign(asc)]}
    out["houses"] = [{"house":h,"rashi":SIGNS[(asc_sign+h-1)%12],"rashi_hi":SIGN_HI[(asc_sign+h-1)%12]} for h in range(1,13)]
    for v in out["grahas"].values(): v["house"]=(sign_index(v["longitude"])-asc_sign)%12+1
    out["ayanamsha_degrees"] = round(swe.get_ayanamsa_ut(jd_ut),8)
    return out

def birth_chart(date_str,time_str,lat,lon,utc_offset_hours=5.5):
    local = datetime.fromisoformat(f"{date_str}T{time_str}")
    utc = local - timedelta(hours=float(utc_offset_hours)); utc = utc.replace(tzinfo=timezone.utc)
    jd = swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60+utc.second/3600+utc.microsecond/3.6e9)
    return calc(jd,float(lat),float(lon))

def dasha_timeline(date_str,time_str,utc_offset_hours,moon_lon,years=9):
    local = datetime.fromisoformat(f"{date_str}T{time_str}"); birth_utc=(local-timedelta(hours=float(utc_offset_hours))).replace(tzinfo=timezone.utc)
    nk,pada,lord=nakshatra(moon_lon); span=360/27; frac=(norm(moon_lon)%span)/span; balance=VIM_YEARS[lord]*(1-frac)
    start_idx=VIM_ORDER.index(lord); events=[]; cursor=birth_utc
    for i in range(9):
        maha=VIM_ORDER[(start_idx+i)%9]; dur=balance if i==0 else VIM_YEARS[maha]
        end=cursor+timedelta(days=dur*365.2425)
        events.append({"lord":maha,"lord_hi":PLANET_HI[maha],"start":cursor.date().isoformat(),"end":end.date().isoformat(),"years":round(dur,4)})
        cursor=end
    # Antardasha schedule for current/first mahadasha, useful for V1 detail page.
    ad=[]; maha=lord; maha_years=balance; ad_cursor=birth_utc
    maha_days=maha_years*365.2425
    maha_idx=VIM_ORDER.index(maha)
    for j in range(9):
        sub=VIM_ORDER[(maha_idx+j)%9]; days=maha_days*VIM_YEARS[sub]/120
        ad_end=ad_cursor+timedelta(days=days)
        ad.append({"lord":sub,"lord_hi":PLANET_HI[sub],"start":ad_cursor.date().isoformat(),"end":ad_end.date().isoformat()}); ad_cursor=ad_end
    return {"birth_nakshatra":nk,"pada":pada,"starting_lord":lord,"starting_lord_hi":PLANET_HI[lord],"balance_years":round(balance,4),"mahadasha":events,"antardasha_first_mahadasha":ad}

def build_report(date_str,time_str,lat,lon,utc_offset_hours=5.5):
    chart=birth_chart(date_str,time_str,lat,lon,utc_offset_hours)
    moon=chart["grahas"]["Chandra"]["longitude"]
    chart["dasha"]=dasha_timeline(date_str,time_str,utc_offset_hours,moon)
    chart["meta"]={"date":date_str,"time":time_str,"latitude":float(lat),"longitude":float(lon),"utc_offset_hours":float(utc_offset_hours)}
    return chart
