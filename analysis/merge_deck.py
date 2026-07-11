import json
D=json.load(open('app_data2.json'))
tariff=json.load(open('tariff_app_data.json'))
yoy=json.load(open('yoy_verify.json'))
anc=json.load(open('anchors_deck.json'))
mov=json.load(open('movers_deck.json'))
accj=json.load(open('accts_joined.json'))
yi={n:i for i,n in enumerate(yoy['leg'])}
G=['RT10','RT20','RT40','RT50','RT60','RT70']
deck=dict(
 momKwh=tariff['momKwh'], momRev=tariff['momRev'],
 total=tariff['total'], byClass=tariff['byClass'], carib=tariff['carib'],
 cases=dict(alcoa=anc['alcoa'], windalco=anc['windalco'], carib=anc['carib']),
 wow=anc['wow'],
 movers={k:{'top':mov[k]['top'],'bot':mov[k]['bot'],'dRev':mov[k]['dRev'],'dDem':mov[k]['dDem'],'n':mov[k]['n'],'dilut':mov[k]['dilut']} for k in ['RT40','RT50','RT70']},
 yoyComp={k:round((yoy['T26'][yi[k]]-yoy['T25'][yi[k]])/1e6,1) for k in ['energy','demand','fuel','ipp','cust_chg']},
 yoyTot=[round(yoy['T25'][yi['net_rev']]/1e9,2), round(yoy['T26'][yi['net_rev']]/1e9,2)],
 yoyKwh=[round(yoy['T25'][yi['net_kwh']]/1e6,0), round(yoy['T26'][yi['net_kwh']]/1e6,0)],
 yoyByClass={g:{'r25':yoy['G25'][g][yi['net_rev']],'r26':yoy['G26'][g][yi['net_rev']],'d25':yoy['G25'][g][yi['demand']],'d26':yoy['G26'][g][yi['demand']],'k25':yoy['G25'][g][yi['net_kwh']],'k26':yoy['G26'][g][yi['net_kwh']]} for g in G},
 accts=[{'n':a['name'],'c':a['cls'],'dR':round(a['dRev']),'dK':round(a['dKwh']),'dD':round(a['dDem'])} for a in accj if (a['k25'] or a['k26'])],
 trend17=tariff['trend'],
)
D['deck']=deck
json.dump(D, open('app_data2.json','w'))
print('merged. deck accts',len(deck['accts']),'| yoyComp',deck['yoyComp'],'| momRev',round(deck['momRev'],1),'momKwh',round(deck['momKwh'],1))
