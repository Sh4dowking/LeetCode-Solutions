import os
import requests
import json
import subprocess
import time

# --- CONFIGURATION ---
LEETCODE_SESSION = os.environ.get('LEETCODE_SESSION')
CSRF_TOKEN = os.environ.get('CSRF_TOKEN')

headers = {
    'Cookie': f'LEETCODE_SESSION={LEETCODE_SESSION}; csrftoken={CSRF_TOKEN}',
    'X-CSRFToken': CSRF_TOKEN,
    'Content-Type': 'application/json',
    'Referer': 'https://leetcode.com'
}

ext_map = {'python3': 'py', 'python': 'py', 'cpp': 'cpp', 'java': 'java', 
           'javascript': 'js', 'typescript': 'ts', 'golang': 'go', 'rust': 'rs',
           'c': 'c', 'csharp': 'cs', 'ruby': 'rb', 'swift': 'swift'}

def parse_metric(metric_str):
    """Converts '45 ms' to 45.0 or '16.4 MB' to 16.4 for comparison."""
    return float(''.join(c for c in metric_str if c.isdigit() or c == '.'))

def get_last_24h_accepted_submissions():
    """Paginates through submissions until it hits one older than 24 hours."""
    cutoff_time = time.time() - (24 * 60 * 60)
    offset = 0
    limit = 20
    accepted_subs = []
    
    print("Fetching submissions from the last 24 hours...")
    
    while True:
        url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}"
        res = requests.get(url, headers=headers).json()
        submissions = res.get('submissions_dump', [])
        
        if not submissions:
            break
            
        for sub in submissions:
            if sub['timestamp'] < cutoff_time:
                return accepted_subs
            
            if sub['status_display'] == 'Accepted':
                accepted_subs.append(sub)
                
        if not res.get('has_next'):
            break 
            
        offset += limit
        time.sleep(1)
        
    return accepted_subs

def get_submission_details(sub_id):
    graphql_url = "https://leetcode.com/graphql/"
    query = """
    query submissionDetails($submissionId: Int!) {
      submissionDetails(submissionId: $submissionId) { 
        code 
        question { questionFrontendId title }
      }
    }
    """
    payload = {'query': query, 'variables': {'submissionId': sub_id}}
    res = requests.post(graphql_url, json=payload, headers=headers).json()
    return res['data'].get('submissionDetails')

def push_to_github(commit_message):
    try:
        # We now add the master_meta.json file to the commit as well
        subprocess.run(["git", "add", "solutions/", "master_meta.json"], check=True)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("No new file changes to push.")
            return 
        
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"Successfully pushed to GitHub: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")

def run_sync():
    accepted_subs = get_last_24h_accepted_submissions()
    if not accepted_subs:
        print("No accepted submissions found in the last 24 hours.")
        return

    print(f"Found {len(accepted_subs)} accepted submissions to evaluate.")
    updates_made = 0
    
    # Load the master meta file if it exists
    master_meta_path = "master_meta.json"
    master_meta = {}
    if os.path.exists(master_meta_path):
        with open(master_meta_path, 'r', encoding='utf-8') as f:
            master_meta = json.load(f)

    for sub in reversed(accepted_subs):
        sub_id = sub['id']
        runtime_val = parse_metric(sub['time'])
        memory_val = parse_metric(sub['memory'])
        lang_ext = ext_map.get(sub['lang'], 'txt')

        details = get_submission_details(sub_id)
        if not details or not details['question']:
            continue
            
        q_id = details['question']['questionFrontendId']
        q_id_padded = str(q_id).zfill(4)
        q_title = details['question']['title']
        code = details['code']

        folder_name = f"solutions/{q_id_padded} - {q_title}"
        os.makedirs(folder_name, exist_ok=True)
        code_path = os.path.join(folder_name, f"solution.{lang_ext}")

        is_better = False
        
        # Check if problem exists in master meta
        if q_id_padded in master_meta:
            prev_runtime = master_meta[q_id_padded].get('runtime', float('inf'))
            prev_memory = master_meta[q_id_padded].get('memory', float('inf'))

            if runtime_val < prev_runtime:
                is_better = True
            elif runtime_val == prev_runtime:
                if memory_val <= prev_memory: 
                    is_better = True
        else:
            is_better = True 

        if is_better:
            # Save new source code
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Update the dictionary in memory with a beautifully structured entry
            master_meta[q_id_padded] = {
                "title": q_title,
                "language": sub['lang'],
                "runtime": runtime_val,
                "runtime_formatted": sub['time'],
                "memory": memory_val,
                "memory_formatted": sub['memory'],
                "submission_id": sub_id
            }
            
            print(f"Updated {q_id_padded} - {q_title}: {sub['time']}, {sub['memory']}")
            updates_made += 1
            
        time.sleep(1) 

    if updates_made > 0:
        # Save the updated dictionary to master_meta.json with formatting
        with open(master_meta_path, "w", encoding="utf-8") as f:
            json.dump(master_meta, f, indent=4, sort_keys=True)
            
        push_to_github(f"Daily Sync: Updated {updates_made} solutions")
    else:
        print("All submissions evaluated, but none were better than existing solutions.")

if __name__ == "__main__":
    run_sync()
