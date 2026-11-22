#!/usr/bin/env python3
"""Generate reproducible, cross-source FlowPilot synthetic datasets.

Run from flowpilot-data-pipeline after extract_hubspot.py:
  python3 generate_flowpilot_sources.py --scale 0.001
  python3 generate_flowpilot_sources.py

No external Python dependencies required. Outputs CSVs to data/synthetic/.
All cross-source identities and CRM links are SYNTHETIC, not actual HubSpot associations.
"""
import argparse
import csv
import json
import random
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20261106
START = date(2025, 1, 1)
END = date(2026, 10, 31)
DAYS = (END - START).days + 1
PLANS = {"Free": 0, "Pro": 12, "Business": 25, "Enterprise": 80}


def writer(path, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open('w', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    return f, w


def load_json(path):
    if not path.exists():
        raise SystemExit(f"Missing {path}. Run python3 extract_hubspot.py first, from your project folder.")
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def day_for(i, mul=17):
    return START + timedelta(days=(i * mul + 31) % DAYS)


def timestamp(d, i):
    return f'{d.isoformat()}T{(i * 7) % 24:02d}:{(i * 13) % 60:02d}:00Z'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--scale', type=float, default=1.0, help='0.001 for ~9,500 rows; 1 for ~9.5M')
    p.add_argument('--output', default='data/synthetic')
    args = p.parse_args()
    if not 0 < args.scale <= 1:
        p.error('--scale must be greater than 0 and at most 1')
    rng = random.Random(SEED)
    out = Path(args.output)
    hub = Path('data/raw')
    contacts = load_json(hub / 'contacts.json')
    companies = load_json(hub / 'companies.json')
    deals = load_json(hub / 'deals.json')
    if not contacts or not companies:
        raise SystemExit('HubSpot contacts and companies JSON must contain records.')

    # Every synthetic user has one stable identity. First users are mapped to
    # actual HubSpot record IDs; associations are generated, not extracted.
    n_users = max(len(contacts), round(50000 * args.scale))
    n_campaigns = 60
    campaign_ids = [f'G-{i:03d}' for i in range(1, 31)] + [f'M-{i:03d}' for i in range(1, 31)]
    company_ids = [str(c['id']) for c in companies]
    contact_ids = [str(c['id']) for c in contacts]
    user_map = {}
    f, w = writer(out / 'identity_map.csv', ['user_id','anonymous_id','hubspot_contact_id','hubspot_company_id','acquisition_source','campaign_id','signup_date','synthetic_association'])
    for i in range(n_users):
        uid = f'U{i+1:07d}'
        source = ('google_ads', 'meta_ads', 'organic', 'direct', 'referral')[i % 5]
        campaigns = campaign_ids[:30] if source == 'google_ads' else campaign_ids[30:] if source == 'meta_ads' else []
        campaign = campaigns[(i // 5) % len(campaigns)] if campaigns else ''
        signup = day_for(i, 11)
        row = dict(user_id=uid, anonymous_id=f'A{i+1:07d}',
                   hubspot_contact_id=contact_ids[i] if i < len(contact_ids) else '',
                   hubspot_company_id=company_ids[i % len(company_ids)] if i < len(contact_ids) else '',
                   acquisition_source=source, campaign_id=campaign, signup_date=signup.isoformat(),
                   synthetic_association='true')
        w.writerow(row)
        user_map[uid] = row
    f.close()

    # All campaigns are defined once; both ads and web events reference them.
    f, w = writer(out / 'campaigns.csv', ['campaign_id','platform','campaign_name','start_date','end_date'])
    for j, cid in enumerate(campaign_ids):
        platform = 'google_ads' if cid.startswith('G') else 'meta_ads'
        w.writerow(dict(campaign_id=cid, platform=platform, campaign_name=f'FlowPilot {platform} campaign {j+1}', start_date=START, end_date=END))
    f.close()

    # Daily campaign performance (aggregate grains); all IDs are valid.
    for platform, name, target in [('google_ads','google_ads_daily.csv',300000),('meta_ads','meta_ads_daily.csv',200000)]:
        n = max(1, round(target * args.scale))
        ids = campaign_ids[:30] if platform == 'google_ads' else campaign_ids[30:]
        f, w = writer(out / name, ['row_id','date','campaign_id','platform','impressions','clicks','spend_eur'])
        for i in range(n):
            imp = rng.randint(100, 5000)
            clicks = rng.randint(1, max(1, imp // 8))
            w.writerow(dict(row_id=f'{platform}-{i+1}',date=day_for(i, 7),campaign_id=ids[i % len(ids)],platform=platform,
                            impressions=imp,clicks=clicks,spend_eur=f'{clicks * rng.uniform(0.35, 3.4):.2f}'))
        f.close()
        print(f'{name}: {n:,} rows')

    # Each GA4 event references a stable user and its acquisition campaign.
    n = max(1, round(1500000 * args.scale))
    f, w = writer(out / 'ga4_events.csv', ['event_id','event_timestamp','anonymous_id','user_id','session_id','event_name','source','campaign_id','page_path'])
    ga_events = ['page_view','session_start','scroll','signup_click','pricing_view']
    for i in range(n):
        u = user_map[f'U{(i % n_users)+1:07d}']
        event_day = date.fromisoformat(u['signup_date']) + timedelta(days=(i // n_users) % 90)
        if event_day > END: event_day = END
        w.writerow(dict(event_id=f'WEB{i+1:09d}',event_timestamp=timestamp(event_day,i),anonymous_id=u['anonymous_id'],
                        user_id=u['user_id'],session_id=f'WS{(i // 5)+1:09d}',event_name=ga_events[i % len(ga_events)],
                        source=u['acquisition_source'],campaign_id=u['campaign_id'],page_path=['/','/pricing','/features','/signup'][i%4]))
    f.close()
    print(f'ga4_events.csv: {n:,} rows')

    # Product event timestamps never precede signup; user IDs are shared.
    n = max(1, round(7000000 * args.scale))
    f, w = writer(out / 'product_events.csv', ['event_id','event_timestamp','user_id','company_id','session_id','event_name','feature'])
    product_events = ['signup','login','workspace_created','task_created','automation_run','integration_connected','dashboard_viewed']
    for i in range(n):
        u = user_map[f'U{(i % n_users)+1:07d}']
        signup = date.fromisoformat(u['signup_date'])
        event_day = min(END, signup + timedelta(days=(i // n_users) % 120))
        event = product_events[(i // n_users + i % n_users) % len(product_events)]
        w.writerow(dict(event_id=f'PE{i+1:010d}',event_timestamp=timestamp(event_day,i),user_id=u['user_id'],
                        company_id=u['hubspot_company_id'] or f'SYNCO{(i%n_users)+1:07d}',
                        session_id=f'PS{(i // 8)+1:09d}',event_name=event,
                        feature={'automation_run':'automations','task_created':'tasks','integration_connected':'integrations'}.get(event,'core')))
    f.close()
    print(f'product_events.csv: {n:,} rows')

    # Subscription dimension: one subscription per paying synthetic user.
    # Billing rows reference only these subscriptions and are paid after start.
    paying_users = [f'U{i+1:07d}' for i in range(n_users) if i % 4 != 0]
    f, w = writer(out / 'subscriptions.csv', ['subscription_id','user_id','company_id','plan','seats','monthly_amount_eur','start_date','status'])
    subscriptions = []
    for i, uid in enumerate(paying_users):
        u = user_map[uid]
        plan = ['Pro','Business','Enterprise'][i % 3]
        seats = [1,5,15][i % 3]
        sid = f'SUB{i+1:07d}'
        start = min(END, date.fromisoformat(u['signup_date']) + timedelta(days=7))
        subscriptions.append((sid,uid,u['hubspot_company_id'] or f'SYNCO{i+1:07d}',plan,seats,PLANS[plan]*seats,start))
        w.writerow(dict(subscription_id=sid,user_id=uid,company_id=subscriptions[-1][2],plan=plan,seats=seats,
                        monthly_amount_eur=PLANS[plan]*seats,start_date=start,status='active' if i%10 else 'canceled'))
    f.close()
    print(f'subscriptions.csv: {len(subscriptions):,} rows')

    n = max(1, round(500000 * args.scale))
    f, w = writer(out / 'billing_invoices.csv', ['invoice_id','subscription_id','user_id','invoice_date','amount_eur','currency','payment_status'])
    for i in range(n):
        sid,uid,_,_,_,amount,start = subscriptions[i % len(subscriptions)]
        invoice_day = min(END, start + timedelta(days=30*(i // len(subscriptions))))
        w.writerow(dict(invoice_id=f'INV{i+1:09d}',subscription_id=sid,user_id=uid,invoice_date=invoice_day,
                        amount_eur=f'{amount:.2f}',currency='EUR',payment_status='paid' if i%20 else 'failed'))
    f.close()
    print(f'billing_invoices.csv: {n:,} rows')

    # Keep a separate audit of original HubSpot deal IDs, never claim a
    # relationship to companies or users that HubSpot did not provide.
    f, w = writer(out / 'hubspot_deal_reference.csv', ['hubspot_deal_id','deal_name','hubspot_pipeline','hubspot_dealstage'])
    for deal in deals:
        props = deal.get('properties', {})
        w.writerow(dict(hubspot_deal_id=deal['id'],deal_name=props.get('dealname',''),
                        hubspot_pipeline=props.get('pipeline',''),hubspot_dealstage=props.get('dealstage','')))
    f.close()
    manifest = {'synthetic':True,'seed':SEED,'scale':args.scale,'hubspot_records':{'companies':len(companies),'contacts':len(contacts),'deals':len(deals)},
                'important':'CRM identity associations are synthetic; no HubSpot record associations were fetched.',
                'caution':'Ad performance rows are generated aggregate observations; they do not reconcile to GA4 clicks or guarantee realistic unique campaign-day grain.'}
    (out / 'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Finished. Files: {out.resolve()}')

if __name__ == '__main__':
    main()
