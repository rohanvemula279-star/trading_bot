import requests, json

# Reset
r = requests.post('http://localhost:8000/reset', json={})
print('RESET:', r.status_code)

# Step through entire episode
for i in range(10):
    r = requests.post('http://localhost:8000/step', json={'action': {'reasoning': 'Buy and hold', 'orders': [{'ticker': 'SPY', 'side': 'BUY', 'amount_usd': 2000}]}})
    data = r.json()
    obs = data['observation']
    pv = obs["portfolio_value_usd"]
    rw = data["reward"]
    dn = data["done"]
    print(f"Step {obs['step']}: portfolio={pv}, reward={rw:.2f}, done={dn}")
    if data.get('done'):
        print('METADATA:', obs.get('metadata', {}))
        break
