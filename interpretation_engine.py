
"""BhawishyaWani Stage 8 - deterministic Vedic interpretation layer.

This module interprets already-calculated chart facts. It does not calculate
astronomical positions itself and does not use an LLM to invent placements.
"""
SIGNS = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
LORDS = {"Mesha":"Mangala","Vrishabha":"Shukra","Mithuna":"Budha","Karka":"Chandra",
         "Simha":"Surya","Kanya":"Budha","Tula":"Shukra","Vrishchika":"Mangala",
         "Dhanu":"Guru","Makara":"Shani","Kumbha":"Shani","Meena":"Guru"}
NATURAL_FRIENDS = {
    "Surya":{"Surya","Chandra","Mangala","Guru"},
    "Chandra":{"Surya","Chandra","Budha"},
    "Mangala":{"Surya","Chandra","Guru"},
    "Budha":{"Surya","Shukra"},
    "Guru":{"Surya","Chandra","Mangala"},
    "Shukra":{"Budha","Shani"},
    "Shani":{"Budha","Shukra"},
}
EXALT = {"Surya":"Mesha","Chandra":"Vrishabha","Mangala":"Makara","Budha":"Kanya",
         "Guru":"Karka","Shukra":"Meena","Shani":"Tula"}
DEBIL = {"Surya":"Tula","Chandra":"Vrishchika","Mangala":"Karka","Budha":"Meena",
         "Guru":"Makara","Shukra":"Kanya","Shani":"Mesha"}

def _sign_i(name): return SIGNS.index(name)

def _house_signs(lagna):
    i=_sign_i(lagna)
    return {h:SIGNS[(i+h-1)%12] for h in range(1,13)}

def _lord_house(lagna, house):
    return _house_signs(lagna)[house]

def _find_planet(chart, name):
    return (chart.get("grahas") or {}).get(name, {})

def _planet_house(chart, name):
    return _find_planet(chart,name).get("house")

def _dignity(name, sign):
    if name in EXALT and EXALT[name]==sign: return "Exalted"
    if name in DEBIL and DEBIL[name]==sign: return "Debilitated"
    if LORDS.get(sign)==name: return "Own sign"
    return "Neutral"

def _aspects(planet_house, target_house):
    # Classical Parashari graha drishti: all planets 7th; Mars 4/8,
    # Jupiter 5/9, Saturn 3/10. Nodes are not assigned special aspects here.
    if planet_house is None: return False
    d=((target_house-planet_house)%12)+1
    if d==7: return True
    if planet_house=="Mangala": return d in (4,8)
    return False

def interpret_chart(chart):
    lagna=chart.get("lagna",{}).get("rashi")
    if lagna not in SIGNS: return {}
    houses=_house_signs(lagna)
    g=chart.get("grahas",{})
    result={"engine_note":"Rule-based interpretation of calculated Vedic chart facts.",
            "lagna":lagna,"life_areas":{},"signals":[],"planet_notes":[]}

    # Planetary dignity facts.
    for name,p in g.items():
        sign=p.get("rashi")
        if sign:
            result["planet_notes"].append({
                "graha":name,"rashi":sign,"house":p.get("house"),
                "dignity":_dignity(name,sign),
                "nakshatra":p.get("nakshatra"),"pada":p.get("pada")
            })

    # House-lord placement framework.
    for area,house in [("Personality",1),("Wealth & Earnings",2),
                       ("Education & Skills",5),("Relationships & Marriage",7),
                       ("Career & Work",10),("Gains",11),("Dharma & Spirituality",9)]:
        sign=houses[house]
        lord=LORDS[sign]
        lord_house=_planet_house(chart,lord)
        text=f"{area}: {house}th house is {sign}; its lord is {lord}"
        if lord_house: text += f", placed in house {lord_house}."
        result["life_areas"][area]={
            "house":house,"house_sign":sign,"lord":lord,"lord_house":lord_house,
            "text":text
        }

    # Traditional, non-deterministic labels are phrased as indicators.
    # Gaja-Kesari: Jupiter in a kendra from Moon (1/4/7/10).
    moon_h=_planet_house(chart,"Chandra"); jup_h=_planet_house(chart,"Guru")
    if moon_h and jup_h and ((jup_h-moon_h)%12)+1 in (1,4,7,10):
        result["signals"].append({"name":"Gaja-Kesari indicator","status":True,
            "basis":"Jupiter is in a kendra from the Moon."})

    # Budha-Aditya: Sun and Mercury in same sign/house.
    if g.get("Surya",{}).get("rashi") and g.get("Surya",{}).get("rashi")==g.get("Budha",{}).get("rashi"):
        result["signals"].append({"name":"Budha-Aditya indicator","status":True,
            "basis":"Sun and Mercury occupy the same sign."})

    # Manglik indicator: Mars in 1,4,7,8,12 from Lagna.
    mh=_planet_house(chart,"Mangala")
    if mh in (1,4,7,8,12):
        result["signals"].append({"name":"Manglik indicator","status":True,
            "basis":f"Mars is placed in house {mh} from Lagna."})

    # Mahapurusha indicators: Mars/Jupiter/Venus/Saturn in own or exalted sign and kendra.
    for pl in ("Mangala","Guru","Shukra","Shani"):
        p=g.get(pl,{})
        if p.get("house") in (1,4,7,10):
            dig=_dignity(pl,p.get("rashi"))
            if dig in ("Own sign","Exalted"):
                result["signals"].append({"name":f"{pl} Mahapurusha indicator","status":True,
                    "basis":f"{pl} is {dig.lower()} and placed in a kendra."})

    # Current dasha labels if Stage 6 supplied them.
    d=chart.get("dasha") or chart.get("vimshottari") or {}
    result["timing"]={
        "starting_dasha_lord":d.get("starting_dasha_lord"),
        "balance_years":d.get("balance_years"),
        "current_mahadasha":chart.get("current_mahadasha") or d.get("current_mahadasha"),
        "current_antardasha":chart.get("current_antardasha") or d.get("current_antardasha")
    }
    return result
