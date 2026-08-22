import os
import requests
import json
import subprocess
import time
import urllib.parse

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
    return float(''.join(c for c in metric_str if c.isdigit() or c == '.'))

def get_last_24h_accepted_submissions():
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
        question { 
            questionFrontendId 
            title 
            difficulty 
        }
      }
    }
    """
    payload = {'query': query, 'variables': {'submissionId': sub_id}}
    res = requests.post(graphql_url, json=payload, headers=headers).json()
    return res['data'].get('submissionDetails')

def update_readme(master_meta):
    """Generates a beautiful README.md with a static chart and a summary table."""
    total_unique_problems = len(master_meta)
    diff_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    table_rows = []

    for q_id, data in master_meta.items():
        title = data['title']
        difficulty = data.get('difficulty', 'Unknown')
        
        if difficulty in diff_counts:
            diff_counts[difficulty] += 1
            
        solutions = data['solutions']
        
        # Prepare lists to handle multiple languages beautifully in one cell
        langs = []
        runtimes = []
        memories = []
        
        for lang_ext, details in solutions.items():
            langs.append(f"`{details['language']}`")
            runtimes.append(details['runtime_formatted'])
            memories.append(details['memory_formatted'])
            
        # Join with <br> to stack them vertically in the table cell
        lang_str = "<br>".join(langs)
        runtime_str = "<br>".join(runtimes)
        memory_str = "<br>".join(memories)
        
        # Add a colored circle next to difficulty in the table
        diff_emoji = "🟢" if difficulty == "Easy" else "🟠" if difficulty == "Medium" else "🔴" if difficulty == "Hard" else "⚪"
        
        folder_path = urllib.parse.quote(f"solutions/{q_id} - {title}")
        table_rows.append(f"| {q_id} | [{title}](./{folder_path}) | {diff_emoji} {difficulty} | {lang_str} | {runtime_str} | {memory_str} |")

    # Filter out empty difficulties so they don't show up in the chart legend
    chart_labels = []
    chart_data = []
    chart_colors = []
    
    if diff_counts["Easy"] > 0:
        chart_labels.append("Easy")
        chart_data.append(diff_counts["Easy"])
        chart_colors.append("#2cba42") # LeetCode Green
    if diff_counts["Medium"] > 0:
        chart_labels.append("Medium")
        chart_data.append(diff_counts["Medium"])
        chart_colors.append("#ffa116") # LeetCode Orange
    if diff_counts["Hard"] > 0:
        chart_labels.append("Hard")
        chart_data.append(diff_counts["Hard"])
        chart_colors.append("#ef4743") # LeetCode Red
        
    # Generate static chart image URL
    chart_config = {
        "type": "pie",
        "data": {
            "labels": chart_labels,
            "datasets": [{
                "data": chart_data,
                "backgroundColor": chart_colors
            }]
        }
    }
    encoded_config = urllib.parse.quote(json.dumps(chart_config))
    chart_url = f"https://quickchart.io/chart?c={encoded_config}&w=400&h=250"

    # Assemble Markdown content
    readme_content = f"""# Leet Code Statistics 📊

## Problem Difficulty Distribution
<img src="{chart_url}" width="400" />

### Summary
* **Total Unique Problems Solved:** {total_unique_problems}

## 📝 Solutions
| ID | Problem | Difficulty | Languages | Runtime | Memory |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    readme_content += "\n".join(table_rows)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Generated beautiful README.md summary.")

def push_to_github(commit_message):
    try:
        subprocess.run(["git", "add", "solutions/", "master_meta.json", "README.md"], check=True)
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
    
    master_meta_path = "master_meta.json"
    master_meta = {}
    if os.path.exists(master_meta_path):
        with open(master_meta_path, 'r', encoding='utf-8') as f:
            master_meta = json.load(f)

    for sub in reversed(accepted_subs):
        sub_id = sub['id']
        
        raw_runtime = sub.get('runtime', '0 ms').replace('\u00a0', ' ')
        raw_memory = sub.get('memory', '0 MB').replace('\u00a0', ' ')
        
        runtime_val = parse_metric(raw_runtime)
        memory_val = parse_metric(raw_memory)
        lang_ext = ext_map.get(sub['lang'], 'txt')

        details = get_submission_details(sub_id)
        if not details or not details['question']:
            continue
            
        q_id = details['question']['questionFrontendId']
        q_id_padded = str(q_id).zfill(4)
        q_title = details['question']['title']
        q_difficulty = details['question']['difficulty']
        code = details['code']

        folder_name = f"solutions/{q_id_padded} - {q_title}"
        os.makedirs(folder_name, exist_ok=True)
        code_path = os.path.join(folder_name, f"solution.{lang_ext}")

        is_better = False
        
        if q_id_padded in master_meta:
            if "solutions" not in master_meta[q_id_padded]:
                master_meta[q_id_padded] = {"title": q_title, "difficulty": q_difficulty, "solutions": {}}
                
            # Update difficulty in case it was missing
            master_meta[q_id_padded]["difficulty"] = q_difficulty
                
            if lang_ext in master_meta[q_id_padded]["solutions"]:
                prev_runtime = master_meta[q_id_padded]["solutions"][lang_ext].get('runtime', float('inf'))
                prev_memory = master_meta[q_id_padded]["solutions"][lang_ext].get('memory', float('inf'))

                if runtime_val < prev_runtime:
                    is_better = True
                elif runtime_val == prev_runtime:
                    if memory_val <= prev_memory: 
                        is_better = True
            else:
                is_better = True 
        else:
            is_better = True 
            master_meta[q_id_padded] = {"title": q_title, "difficulty": q_difficulty, "solutions": {}}

        if is_better:
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            master_meta[q_id_padded]["solutions"][lang_ext] = {
                "language": sub['lang'],
                "runtime": runtime_val,
                "runtime_formatted": raw_runtime,
                "memory": memory_val,
                "memory_formatted": raw_memory,
                "submission_id": sub_id
            }
            
            print(f"Updated {q_id_padded} - {q_title} ({lang_ext}): {raw_runtime}, {raw_memory}")
            updates_made += 1
            
        time.sleep(1) 

    if updates_made > 0:
        ordered_meta = {}
        for key in sorted(master_meta.keys()):
            ordered_meta[key] = {
                "title": master_meta[key]["title"],
                "difficulty": master_meta[key].get("difficulty", "Unknown"),
                "solutions": master_meta[key]["solutions"]
            }

        with open(master_meta_path, "w", encoding="utf-8") as f:
            json.dump(ordered_meta, f, indent=4, ensure_ascii=False)
            
        # Build the README before committing
        update_readme(ordered_meta)
            
        push_to_github(f"Daily Sync: Updated {updates_made} solutions")
    else:
        print("All submissions evaluated, but none were better than existing solutions.")

if __name__ == "__main__":
    run_sync()
