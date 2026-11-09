# -*- coding: utf-8 -*-
# Weather and EV chargers are in the base: forecast workbook text.
p = '_fy27_workbook.py'; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("'Weather. Whether the zero-kWh premises return (worth about 8 GWh if they all do by mid-year). Net billing growth.'),",
    "'Weather: the base carries a warm 2027 (about +7 GWh), so a normal year takes it out. Whether the zero-kWh premises return (worth about 8 GWh if they all do by mid-year). Net billing growth. EV chargers keep growing at the 2026 pace.'),")
rep("Drags are 7,742 more zero-kWh premises", "Weather and the EV44 charging accounts are in the base. Drags are 7,742 more zero-kWh premises")
rep("      ('Hotel recovery', '19% of the gap",
    "      ('Weather', 'Anomaly of 0.07 to 0.37C a month over the 2023-2025 mean in 2027, flat 0.09C in 2028, at 1.93% of residential load per degree', 'The 7 September engine profile. The WMO expects a very strong El Nino through February 2027. About +7 GWh in FY2027 and +3.5 in FY2028, RT10 and RT20 residential.'),\n      ('EV chargers (EV44)', 'August to October level in the base plus the 2026 monthly trend of about 4.6 MWh a month', 'Charging accounts in the name of JPS. The billing report flags them not billed in error, so they are now counted in sales from January 2025. About 1.3 GWh in FY2027.'),\n      ('Hotel recovery', '19% of the gap")
rep("('Not in the base (upside)', 'Zero-kWh premises returning, El Nino, new hospitals', '')]", "('Not in the base (upside)', 'Zero-kWh premises returning, new hospitals', '')]")
open(p, 'w', encoding='utf-8').write(s); print('workbook text patched')
