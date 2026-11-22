import csv, gzip, random, argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
START = datetime(2025, 1, 1, tzinfo=timezone.utc)
CHANNELS = ['paid_social','paid_search','organic_search','direct','referral','email']
EVENTS = ['page_view','session_start','view_pricing','sign_up','login','trial_started']
PRODUCT_EVENTS = ['page_view','feature_view','feature_used','project_created','integration_connected','invite_sent','export_completed','error']


def write(name, fields, count, rows):
    path = BASE / (name + '.csv.gz')
    with gzip.open(path, 'wt', newline='', encoding='utf-8', compresslevel=3) as f:
        w=csv.writer(f); w.writerow(fields)
        for i,row in enumerate(rows, 1):
            w.writerow(row)
            if i % 1000000 == 0: print(f'{name}: {i:,}/{count:,}', flush=True)
    print(f'{name}: DONE {count:,} rows -> {path.name}', flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--scale', type=float, default=1.0, help='1.0 = 8.75 million rows total; 0.001 = sample')
    a=p.parse_args(); rng=random.Random(20261112)
    n_ga4=max(1,int(1500000*a.scale)); n_prod=max(1,int(7000000*a.scale))
    n_meta=max(1,int(200000*a.scale)); n_sub=max(1,int(50000*a.scale))
    users=100000; campaigns=300; days=365
    def ts(day, second): return (START+timedelta(days=day, seconds=second)).isoformat(timespec='seconds')
    def ga4():
        for i in range(n_ga4):
            uid=rng.randrange(users); day=rng.randrange(days); sec=rng.randrange(86400)
            channel=rng.choices(CHANNELS,weights=[20,15,30,20,5,10])[0]
            campaign=f'C{rng.randrange(campaigns):04d}' if channel in ('paid_social','paid_search','email') else ''
            event=rng.choices(EVENTS, weights=[55,16,10,8,8,3])[0]
            yield [f'ga4_{i:09d}',ts(day,sec),f'user_{uid:06d}',f'session_{uid:06d}_{day:03d}_{sec//1800:02d}',event,channel,campaign,rng.choice(['desktop','mobile','tablet']),rng.choice(['ES','FR','DE','GB','US']),rng.randrange(100,120000) if event=='page_view' else '']
    if not (BASE/'ga4_events.csv.gz').exists(): write('ga4_events',['event_id','event_timestamp','user_id','session_id','event_name','traffic_source','campaign_id','device_category','country','engagement_time_msec'],n_ga4,ga4())
    def product():
        for i in range(n_prod):
            uid=rng.randrange(users); day=rng.randrange(days); sec=rng.randrange(86400)
            event=rng.choices(PRODUCT_EVENTS,weights=[22,19,30,9,5,5,6,4])[0]
            yield [f'pe_{i:010d}',ts(day,sec),f'user_{uid:06d}',f'account_{uid//5:05d}',f'session_{uid:06d}_{day:03d}_{sec//1800:02d}',event,rng.choice(['web','ios','android']),rng.choice(['free','trial','pro','business']),rng.randrange(50,5000) if event=='feature_used' else '',rng.choice(['dashboard','reports','integrations','billing','projects'])]
    write('product_events',['event_id','event_timestamp','user_id','account_id','session_id','event_name','platform','plan_at_event','duration_ms','feature_area'],n_prod,product())
    def meta():
        for i in range(n_meta):
            day=i%days; campaign=i%campaigns; impressions=rng.randrange(500,15000)
            clicks=int(impressions*rng.uniform(.005,.065)); spend=round(clicks*rng.uniform(.3,2.9),2)
            yield [(START+timedelta(days=day)).date().isoformat(),f'C{campaign:04d}',f'meta_ad_{i%1200:05d}',rng.choice(['facebook','instagram']),impressions,clicks,spend,rng.randrange(0,max(1,clicks//8+1)), 'EUR']
    write('meta_ads_daily',['date','campaign_id','ad_id','placement','impressions','clicks','spend','platform_conversions','currency'],n_meta,meta())
    def subscriptions():
        for i in range(n_sub):
            uid=i%users; day=rng.randrange(300); plan=rng.choices(['starter','pro','business'],[55,35,10])[0]
            price={'starter':19,'pro':59,'business':199}[plan]; billing=rng.choices(['monthly','annual'],[80,20])[0]
            status=rng.choices(['active','cancelled','past_due','trialing'],[60,22,8,10])[0]
            start=START+timedelta(days=day)
            end=(start+timedelta(days=rng.randrange(7,180))).date().isoformat() if status=='cancelled' else ''
            yield [f'sub_{i:08d}',f'user_{uid:06d}',f'account_{uid//5:05d}',plan,billing,status,start.date().isoformat(),end,price,'EUR']
    write('subscriptions',['subscription_id','user_id','account_id','plan','billing_interval','status','started_at','cancelled_at','monthly_price_eur','currency'],n_sub,subscriptions())
    print(f'TOTAL: {n_ga4+n_prod+n_meta+n_sub:,} records',flush=True)

if __name__=='__main__': main()
