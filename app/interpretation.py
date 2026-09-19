SIGN_LORDS = {0:'Mangala',1:'Shukra',2:'Budha',3:'Chandra',4:'Surya',5:'Budha',6:'Shukra',7:'Mangala',8:'Guru',9:'Shani',10:'Shani',11:'Guru'}
SIGN_NAMES = ['Mesha','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrishchika','Dhanu','Makara','Kumbha','Meena']
PLANET_HI = {'Surya':'सूर्य','Chandra':'चंद्र','Mangala':'मंगल','Budha':'बुध','Guru':'गुरु','Shukra':'शुक्र','Shani':'शनि','Rahu':'राहु','Ketu':'केतु'}
EXALTATION = {'Surya':0,'Chandra':1,'Mangala':9,'Budha':5,'Guru':3,'Shukra':11,'Shani':6}
DEBILITATION = {'Surya':6,'Chandra':7,'Mangala':3,'Budha':11,'Guru':9,'Shukra':5,'Shani':0}
OWN_SIGNS = {'Surya':{4},'Chandra':{3},'Mangala':{0,7},'Budha':{2,5},'Guru':{8,11},'Shukra':{1,6},'Shani':{9,10}}
NATURAL_FRIENDS = {'Surya':{'Chandra','Mangala','Guru'},'Chandra':{'Surya','Budha'},'Mangala':{'Surya','Chandra','Guru'},'Budha':{'Surya','Shukra'},'Guru':{'Surya','Chandra','Mangala'},'Shukra':{'Budha','Shani'},'Shani':{'Budha','Shukra'}}
NATURAL_ENEMIES = {'Surya':{'Shukra','Shani'},'Chandra':set(),'Mangala':{'Budha'},'Budha':{'Chandra'},'Guru':{'Budha','Shukra'},'Shukra':{'Surya','Chandra'},'Shani':{'Surya','Chandra','Mangala'}}

def _idx(sign): return SIGN_NAMES.index(sign)
def _house_sign(chart, h): return next(x['rashi'] for x in chart['houses'] if x['house']==h)
def _lord_for_sign(sign): return SIGN_LORDS[_idx(sign)]

def dignity(planet, sign):
    idx=_idx(sign)
    if planet in EXALTATION and idx==EXALTATION[planet]: return 'Exalted'
    if planet in DEBILITATION and idx==DEBILITATION[planet]: return 'Debilitated'
    if planet in OWN_SIGNS and idx in OWN_SIGNS[planet]: return 'Own sign'
    lord=SIGN_LORDS[idx]
    if planet in NATURAL_FRIENDS and lord in NATURAL_FRIENDS[planet]: return 'Friendly sign'
    if planet in NATURAL_ENEMIES and lord in NATURAL_ENEMIES[planet]: return 'Enemy sign'
    return 'Neutral sign'

def conjunctions(chart):
    by_sign={}
    for p,v in chart['grahas'].items(): by_sign.setdefault(v['rashi'],[]).append(p)
    return [ps for ps in by_sign.values() if len(ps)>=2]

def yoga_flags(chart):
    g=chart['grahas']; flags=[]
    for p in ['Mangala','Budha','Guru','Shukra','Shani']:
        if g[p]['house'] in {1,4,7,10} and dignity(p,g[p]['rashi']) in {'Exalted','Own sign'}:
            flags.append({'name':f'{p} Mahapurusha Yoga','planet':p,'basis':f'{p} is {dignity(p,g[p]["rashi"])} and placed in Kendra house {g[p]["house"]}.'})
    # From the Moon, not the Lagna: calculate sign-distance.
    moon_sign=_idx(g['Chandra']['rashi']); guru_sign=_idx(g['Guru']['rashi'])
    if (guru_sign-moon_sign)%12 in {0,3,6,9}:
        flags.append({'name':'Gaja-Kesari Yoga','planet':'Guru','basis':'Jupiter is in a Kendra from the Moon by sign.'})
    if g['Surya']['rashi']==g['Budha']['rashi']:
        flags.append({'name':'Budha-Aditya Yoga','planet':'Budha','basis':'Sun and Mercury occupy the same sign.'})
    ninth_lord=_lord_for_sign(_house_sign(chart,9)); tenth_lord=_lord_for_sign(_house_sign(chart,10))
    if ninth_lord!=tenth_lord and g[ninth_lord]['rashi']==g[tenth_lord]['rashi']:
        flags.append({'name':'Dharma-Karma Adhipati Link','planet':f'{ninth_lord}/{tenth_lord}','basis':'9th and 10th house lords are in the same sign.'})
    return flags

def dosha_indicators(chart):
    g=chart['grahas']
    manglik_houses={1,4,7,8,12}
    return [{'name':'Manglik indicator (Lagna-based)','present':g['Mangala']['house'] in manglik_houses,'basis':f'Mars is in house {g["Mangala"]["house"]}; this V1 flag uses the Lagna-based 1/4/7/8/12 rule.','note':'Traditional schools use different rules and cancellation conditions; this is an indicator, not a final dosha judgement.'}]

def life_areas(chart):
    g=chart['grahas']; lagna=_idx(chart['lagna']['rashi']); ll=_lord_for_sign(chart['lagna']['rashi'])
    tenth=_house_sign(chart,10); seventh=_house_sign(chart,7); second=_house_sign(chart,2); eleventh=_house_sign(chart,11)
    return [
      {'key':'personality','title':'Personality & Self','icon':'ॐ','summary':f'Lagna: {chart["lagna"]["rashi"]}; Lagna lord {ll} in house {g[ll]["house"]}.','details':'The Lagna, its lord, Moon and their condition form the primary Vedic framework for temperament and self-expression.'},
      {'key':'career','title':'Career & Work','icon':'☀','summary':f'10th house: {tenth}; 10th lord: {_lord_for_sign(tenth)}.','details':'Assess the 10th house/lord together with Sun, Saturn, relevant conjunctions and dasha activation. This chart is a structured indicator, not a deterministic career forecast.'},
      {'key':'relationships','title':'Relationships & Marriage','icon':'♡','summary':f'7th house: {seventh}; 7th lord: {_lord_for_sign(seventh)}.','details':'Relationship analysis should combine the 7th house/lord, Venus, Moon and Navamsa (D9). Timing should be tied to dashas and, in a future stage, transits.'},
      {'key':'wealth','title':'Wealth & Earnings','icon':'₹','summary':f'2nd: {second}; 11th: {eleventh}.','details':'The 2nd and 11th houses, their lords, occupants and dasha activation are core Vedic financial indicators. They do not guarantee financial outcomes.'},
      {'key':'education','title':'Education & Skills','icon':'✦','summary':f'5th house: {_house_sign(chart,5)}; 5th lord: {_lord_for_sign(_house_sign(chart,5))}.','details':'The 4th/5th houses, Mercury and Jupiter are useful starting points for education, learning style and intellectual development.'},
      {'key':'spirituality','title':'Dharma & Spirituality','icon':'◉','summary':f'9th house: {_house_sign(chart,9)}; 12th house: {_house_sign(chart,12)}.','details':'The 9th and 12th houses, Jupiter, Ketu and their lords provide a classical framework for dharma, pilgrimage and inward-oriented interests.'}
    ]

def localized(language):
    if language=='hi':
        return {'career':'करियर और काम','relationships':'रिश्ते और विवाह','wealth':'धन और आय','personality':'व्यक्तित्व','education':'शिक्षा और कौशल','spirituality':'धर्म और आध्यात्मिकता'}
    if language=='en':
        return {'career':'Career & Work','relationships':'Relationships & Marriage','wealth':'Wealth & Earnings','personality':'Personality & Self','education':'Education & Skills','spirituality':'Dharma & Spirituality'}
    return {'career':'Career & Work / करियर','relationships':'Relationships / रिश्ते','wealth':'Wealth & Earnings / धन','personality':'Personality / व्यक्तित्व','education':'Education / शिक्षा','spirituality':'Dharma / अध्यात्म'}

def generate_interpretation(chart, language='hinglish'):
    g=chart['grahas']; ll=_lord_for_sign(chart['lagna']['rashi']); labels=localized(language)
    areas=life_areas(chart)
    for a in areas: a['display_title']=labels[a['key']]
    return {
      'language':language,
      'lagna_lord':ll,
      'lagna_lord_hi':PLANET_HI[ll],
      'dignities':{p:dignity(p,v['rashi']) for p,v in g.items() if p not in {'Rahu','Ketu'}},
      'yogas':yoga_flags(chart),
      'doshas':dosha_indicators(chart),
      'conjunctions':conjunctions(chart),
      'life_areas':areas,
      'note':'These are rule-based Vedic-astrology indicators. They are not guaranteed predictions. Different Jyotisha traditions may apply different rules, especially for yogas and doshas.'
    }
