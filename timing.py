from datetime import datetime, timezone, timedelta
import swisseph as swe
from app.vedic_engine import VIM_ORDER, VIM_YEARS, PLANET_HI, norm, nakshatra

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
TRANSIT_PLANETS = {'Surya': swe.SUN, 'Chandra': swe.MOON, 'Mangala': swe.MARS, 'Budha': swe.MERCURY, 'Guru': swe.JUPITER, 'Shukra': swe.VENUS, 'Shani': swe.SATURN, 'Rahu': swe.TRUE_NODE}

def _utc(date_str, time_str='12:00', offset=0):
    local=datetime.fromisoformat(f'{date_str}T{time_str}')
    return (local-timedelta(hours=float(offset))).replace(tzinfo=timezone.utc)

def _jd(dt):
    return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600)

def transit_positions(date_str, utc_offset=0):
    dt=_utc(date_str,'12:00',utc_offset); jd=_jd(dt); swe.set_sid_mode(swe.SIDM_LAHIRI)
    out={}
    for name,pid in TRANSIT_PLANETS.items():
        xx,_=swe.calc_ut(jd,pid,FLAGS); lon=norm(xx[0]); nk,pada,lord=nakshatra(lon)
        out[name]={'longitude':round(lon,5),'rashi':int(lon//30),'nakshatra':nk,'pada':pada,'retrograde':bool(xx[3]<0)}
    rahu=out['Rahu']['longitude']; klon=norm(rahu+180); nk,pada,lord=nakshatra(klon)
    out['Ketu']={'longitude':round(klon,5),'rashi':int(klon//30),'nakshatra':nk,'pada':pada,'retrograde':True}
    return out

def _parse(d): return datetime.fromisoformat(d).replace(tzinfo=timezone.utc)

def current_dasha(chart, as_of=None):
    meta=chart['meta']; birth=_utc(meta['date'],meta['time'],meta.get('utc_offset_hours',0))
    moon=chart['grahas']['Chandra']['longitude']; nk,pada,lord=nakshatra(moon)
    span=360/27; frac=(norm(moon)%span)/span; balance=VIM_YEARS[lord]*(1-frac)
    target=as_of or datetime.now(timezone.utc)
    cursor=birth; start_idx=VIM_ORDER.index(lord)
    mah=None
    for i in range(9):
        mlord=VIM_ORDER[(start_idx+i)%9]; years=balance if i==0 else VIM_YEARS[mlord]
        end=cursor+timedelta(days=years*365.2425)
        if cursor <= target < end:
            mah=(mlord,cursor,end,years); break
        cursor=end
    if not mah: return None
    mlord,mstart,mend,myears=mah; total_days=(mend-mstart).total_seconds()/86400
    elapsed=(target-mstart).total_seconds()/86400
    m_idx=VIM_ORDER.index(mlord); ad_cursor=mstart; ad=None
    for j in range(9):
        alord=VIM_ORDER[(m_idx+j)%9]; ad_days=total_days*VIM_YEARS[alord]/120; ad_end=ad_cursor+timedelta(days=ad_days)
        if ad_cursor <= target < ad_end: ad=(alord,ad_cursor,ad_end); break
        ad_cursor=ad_end
    return {'mahadasha':mlord,'mahadasha_hi':PLANET_HI[mlord],'mahadasha_start':mstart.date().isoformat(),'mahadasha_end':mend.date().isoformat(),'antardasha':ad[0] if ad else None,'antardasha_hi':PLANET_HI[ad[0]] if ad else None,'antardasha_start':ad[1].date().isoformat() if ad else None,'antardasha_end':ad[2].date().isoformat() if ad else None,'elapsed_days':round(elapsed,2)}

def timing_signals(chart, as_of=None):
    target=as_of or datetime.now(timezone.utc); date=target.date().isoformat(); offset=chart['meta'].get('utc_offset_hours',0)
    trans=transit_positions(date,offset); cd=current_dasha(chart,target); signals=[]
    if not cd: return {'as_of':date,'current_dasha':None,'transits':trans,'signals':signals}
    for lord in [cd['mahadasha'],cd['antardasha']]:
        if lord in chart['grahas']:
            natal=chart['grahas'][lord]
            signals.append({'type':'dasha','planet':lord,'planet_hi':PLANET_HI[lord],'house':natal['house'],'rashi':natal['rashi'],'meaning':'A dasha period places traditional interpretive emphasis on the planet and the houses it signifies.'})
    lagna_sign=next(h['rashi'] for h in chart['houses'] if h['house']==1)
    lagna_idx=['Mesha','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrishchika','Dhanu','Makara','Kumbha','Meena'].index(lagna_sign)
    for p in ['Guru','Shani']:
        tr=trans[p]['rashi']; houses=((tr-lagna_idx)%12)+1
        signals.append({'type':'transit','planet':p,'planet_hi':PLANET_HI[p],'house_from_lagna':houses,'rashi_index':tr,'meaning':f'{PLANET_HI[p]} transit is shown from the Lagna as a traditional timing input; interpretation should be combined with dasha and natal placements.'})
    return {'as_of':date,'current_dasha':cd,'transits':trans,'signals':signals}
