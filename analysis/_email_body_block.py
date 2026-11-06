body = f'''<p style="font-size:14px;font-weight:bold;margin:0 0 8px">See key highlights for the month. The one-page analysis is attached.</p>
{mt}
{h('Anomalies')}
{ul(b('Petrojam:', '1.8 GWh, against 0.9 GWh in September. The refinery was shut down for about two weeks in September after a fire, which accounts for the lower volume. October is back to its usual 1.5–1.7 GWh.'),
    b('Caribbean Broilers:', '2.5 GWh, after 4.2 GWh in August and 0.8 GWh in September. The August over-bill and the September correction have cleared. The three months together are about 0.4 GWh above normal (2.2–2.4 a month).'),
    b('Caribbean Cement:', f'9.1 GWh, the same as September and more than double last October (4.3). September was down 16% on last year because last September was strong (10.8). It has billed 8.5 to 9.1 GWh for three months and is up 22% year to date (91.4 vs 75.2 GWh).'),
    b('National Water Commission:', '18.4 GWh, up 1.7 GWh (10%) on September and 0.6 GWh (3.5%) on last October. St. Elizabeth (+0.6) and St. Catherine (+0.3) make up half of the rise on September. St. Elizabeth was low in September and is back at last October’s level. St. James adds 0.2, and KSAN, St. Ann, Manchester and Clarendon about 0.1 each. Against last October the increases are in Clarendon and St. Catherine (+0.2 each). All water supply accounts together are up 1.2 GWh (6.4%) on last October. Dry weather and the water restrictions in St. Catherine are the likely cause. We do not have pump-level data to confirm.'))}
{h('Insights')}
{ul(b('Residential and commercial.', 'Residential-side sales were up 4.9% year over year (126.2 to 132.4 GWh) and commercial was down 0.6% (163.0 to 161.9 GWh). Alcoa explains 6.8 GWh of the commercial decline. Excluding Alcoa, commercial is up 3.7%. October 2025 had fewer billing days because billing ran a few days early after Hurricane Melissa, so the year-over-year growth is overstated.'),
    b('Alcoa.', '0.26 GWh in October, from 1.2 in August and 0.6 in September. A year ago it was 7.0.'),
    b('Hotels.', f'Hotels are down 18.8% year over year in October ({M}19.1% in September) and 24.5% year to date ({M}25.2%): 17.3 GWh against 21.3. Royalton Negril and Royalton Blue Waters (about 1,150 rooms) reopened in late August and mid-September and are not in the October bills yet. About 1,900 more rooms are expected in December.'),
    b('Month on month.', f'Sales were flat on September ({M}0.2%) with one more day, so per day volume fell 3.4%. The budget assumes {M}4.7% per day. Billing cycles do not map exactly to calendar days, and there was one holiday (National Heroes Day, 19 October), so treat this as approximate.'),
    b('RT10 customers.', 'RT10 added 449 accounts and zero-consumption accounts fell by 153, so active RT10 customers rose by about 600 after falling in September. Zero-consumption accounts are still 15% above last October (58,886 vs 51,144).'),
    b('RT20 accounts.', 'RT20 commercial accounts are down 3.2% over a year (24,170 to 23,393) and lost 89 in October.'))}
{h('October against September')}
<p style="margin:0 0 8px;font-size:14px">Sales fell {abs(t25):.1f} GWh from September to October last year and {abs(t26):.1f} GWh this year. Caribbean Cement (down last October), Caribbean Broilers and Petrojam (both low in September) account for 9.3 GWh of the {t26 - t25:.1f} GWh difference. October 2025 also had fewer billing days, which adds to last year’s drop. With the September Broilers and Petrojam volumes at their normal levels, sales fell about 1.0% from September to October this year, against 2.1% last year excluding Cement.</p>
{bt}
<p style="margin:10px 0 4px;font-size:12px;color:{GREY}">Change in GWh from September to October. Each bar starts where the previous one ended.</p>
{wf}
<p style="margin:8px 0 0;font-size:13px">Residential fell more than last year; prepaid usage per customer was 151 kWh against 167 in September. The rest of the commercial gain is spread over 7,600 accounts and none is above 0.7 GWh.</p>
{h('Prepaid')}
{ul(b('Customers:', '18,090, up 10.5% year over year (16,371) and 66 on the month.'),
    b('Volume:', '2.7 GWh, up 18% year over year and 9% below September. Usage per customer was 151 kWh against 167 in September and 141 a year ago. Including RT20 prepaid, the total is 2.8 GWh and 18,591 customers.'))}
{h('Market context')}
{ul(b('Tourism:', 'Stayover arrivals were down 27.5% in the first quarter and arrivals at Sangster were down 23.7% in August. Hotel volume is 19% below last year. About 1,900 rooms are expected back in December and Hyatt’s seven resorts have moved to the first half of 2027.'),
    b('Economy:', 'The PIOJ expects July to September to contract by 0.5% to 1.5%, after a 2.9% fall in April to June, with output back at pre-Melissa levels from April to June 2027.'),
    b('Water:', 'Prohibition orders took effect on 17 August for Kingston, St. Andrew, St. Thomas, St. Mary, Portland, St. Ann and St. Catherine. On 2 October the minister reported 10 systems in St. Catherine and Clarendon under severe drought.'),
    b('Alcoa:', 'Century says the new Jamalco turbine came online in early August and the refinery now runs on its own power.'),
    b('Cement:', 'Caribbean Cement reported record second-quarter volumes (110,647 tonnes). Its 2025 output was held back by an extended planned shutdown, kiln stoppages and the storm. Third-quarter results are not out yet.'),
    b('Petrojam:', 'The gasoline unit was out for 23 days from April (about US$3.6M). A review of the refinery’s operating options is due this quarter.'),
    b('Weather:', 'The WMO expects El Niño to strengthen into early 2027 and the Met Service expects warmer, drier weather. June rainfall was the lowest in 30 years in 11 parishes, and JPS set its 2026 demand high on 1 July. The official October summary is not out yet.'))}
<p style="margin:12px 0 2px;font-size:11px;font-weight:bold;color:{GREY}">Sources</p>
<p style="margin:0;font-size:11px;line-height:1.5;color:{GREY}">
''' + '<br>'.join(f'<a href="{u}" style="color:{GREY}">{u}</a>' for u in [
    'https://www.caribjournal.com/2026/07/13/jamaica-tourism-arrivals-down-27/', 'https://www.riotimesonline.com/jamaica-arrivals-fall-montego-bay-hurricane-melissa-2026/',
    'https://www.travelpulse.com/news/hotels-and-resorts/royalton-negril-reopens-as-jamaica-tourism-recovery-gains-steam', 'https://www.travelpulse.com/news/hotels-and-resorts/jamaica-resorts-update-reopen-timelines-for-sandals-hyatt-princess-and-more',
    'https://www.caribjournal.com/2026/04/12/jamaica-hyatt-all-inclusive-resorts-delays/', 'https://www.jamaicaobserver.com/2026/08/19/recovery-ahead-schedule/',
    'https://www.jamaicaobserver.com/2026/08/21/water-prohibitions-coming-parishes/', 'https://jis.gov.jm/stricter-water-restrictions-coming-for-kingston-and-st-andrew/',
    'https://jamaica-gleaner.com/article/business/20260809/jamalco-unplugs-grid-power-turbine-set-save-us28m-year', 'https://jamaica-gleaner.com/article/business/20260730/cement-production-hits-record-2nd-quarter-profit-surges-fivefold',
    'https://jamaica-gleaner.com/article/business/20260703/petrojam-absorbs-us156000-day-loss-after-gas-unit-shuts-down-april', 'https://wmo.int/node/39136',
    'https://jis.gov.jm/met-service-says-11-parishes-recorded-30-year-low-rainfall-in-june/', 'https://www.jamaicaobserver.com/2026/07/08/heat-sends-power-demand-2026-high/']) + '</p>'

