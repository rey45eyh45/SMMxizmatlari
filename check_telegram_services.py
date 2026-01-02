# -*- coding: utf-8 -*-
"""
Telegram xizmatlarini tekshirish
"""
from smm_api import MultiPanel

api = MultiPanel()

print("=" * 80)
print("PEAKERR API - TELEGRAM XIZMATLARI")
print("=" * 80)

if 'peakerr' in api.panels:
    services = api.panels['peakerr'].get_services(use_cache=False)
    telegram = [s for s in services if 'telegram' in s.get('name','').lower()]
    print(f"\nJami Telegram xizmatlari: {len(telegram)} ta\n")
    
    # Kategoriyalar bo'yicha
    members = [s for s in telegram if 'member' in s.get('name','').lower() or 'subscriber' in s.get('name','').lower()]
    views = [s for s in telegram if 'view' in s.get('name','').lower()]
    reactions = [s for s in telegram if 'reaction' in s.get('name','').lower() or 'emoji' in s.get('name','').lower()]
    shares = [s for s in telegram if 'share' in s.get('name','').lower() or 'forward' in s.get('name','').lower()]
    comments = [s for s in telegram if 'comment' in s.get('name','').lower()]
    votes = [s for s in telegram if 'vote' in s.get('name','').lower() or 'poll' in s.get('name','').lower()]
    
    print(f"👥 MEMBERS/SUBSCRIBERS: {len(members)} ta")
    for s in members[:15]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    
    print(f"\n👁 VIEWS: {len(views)} ta")
    for s in views[:15]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    
    print(f"\n👍 REACTIONS: {len(reactions)} ta")
    for s in reactions[:15]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    
    print(f"\n🔄 SHARES/FORWARDS: {len(shares)} ta")
    for s in shares[:10]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    
    print(f"\n💬 COMMENTS: {len(comments)} ta")
    for s in comments[:10]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    
    print(f"\n📊 VOTES/POLLS: {len(votes)} ta")
    for s in votes[:10]:
        print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")

print("\n" + "=" * 80)
print("SMMMAIN API - TELEGRAM XIZMATLARI")
print("=" * 80)

if 'smmmain' in api.panels:
    services = api.panels['smmmain'].get_services(use_cache=False)
    if isinstance(services, list):
        telegram = [s for s in services if 'telegram' in s.get('name','').lower()]
        print(f"\nJami Telegram xizmatlari: {len(telegram)} ta\n")
        
        members = [s for s in telegram if 'member' in s.get('name','').lower() or 'subscriber' in s.get('name','').lower()]
        views = [s for s in telegram if 'view' in s.get('name','').lower()]
        reactions = [s for s in telegram if 'reaction' in s.get('name','').lower() or 'emoji' in s.get('name','').lower()]
        
        print(f"👥 MEMBERS/SUBSCRIBERS: {len(members)} ta")
        for s in members[:15]:
            print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
        
        print(f"\n👁 VIEWS: {len(views)} ta")
        for s in views[:15]:
            print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
        
        print(f"\n👍 REACTIONS: {len(reactions)} ta")
        for s in reactions[:15]:
            print(f"  ID:{s['service']} | ${s['rate']}/1K | {s['name'][:50]}")
    else:
        print(f"Xato: {services}")
else:
    print("SMMMain API mavjud emas")
