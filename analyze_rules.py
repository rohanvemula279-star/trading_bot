import json, os

for task in ['easy', 'medium', 'hard']:
    with open(f'test_data/{task}_cases.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"\nTask: {task.upper()} ({len(data)} cases)")
    
    unique_cases = {}
    for c in data:
        mo = c['model_output'].strip()
        if mo not in unique_cases:
            unique_cases[mo] = c['ground_truth']
            
    for mo, gt in unique_cases.items():
        print(f"[{gt['decision']:8} | {str(gt.get('violation_type')):15} | {str(gt.get('severity')):8}] {mo[:100]}")
