import os

req_dir = r'f:\apptimus\agentic_coding\agentic-code-envoy-1\.docs\requirements'
ui_dir = r'f:\apptimus\agentic_coding\agentic-code-envoy-1\.docs\tasks\ui'
api_dir = r'f:\apptimus\agentic_coding\agentic-code-envoy-1\.docs\tasks\api'

os.makedirs(ui_dir, exist_ok=True)
os.makedirs(api_dir, exist_ok=True)

for filename in os.listdir(req_dir):
    if not filename.endswith('.md'):
        continue
        
    with open(os.path.join(req_dir, filename), 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    title = filename.replace('.md', '').replace('-', ' ').title()
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break
            
    ui_tasks = [f'# UI Tasks: {title}\n']
    api_tasks = [f'# API Tasks: {title}\n']
    
    current_section = ""
    
    for line in lines:
        if line.startswith('### '):
            current_section = line.replace('###', '').strip()
            ui_tasks.append(f'## {current_section}')
            api_tasks.append(f'## {current_section}')
            
            action_lower = current_section.lower()
            if 'create' in action_lower or 'add' in action_lower:
                ui_tasks.append('- [ ] Build form component for creating record.')
                ui_tasks.append('- [ ] Implement form validation rules.')
                ui_tasks.append('- [ ] Integrate POST API and handle success/error states.\n')
                api_tasks.append('- [ ] Define database model/schema.')
                api_tasks.append('- [ ] Create POST endpoint with validation.')
                api_tasks.append('- [ ] Implement permission checks.\n')
            elif 'view' in action_lower or 'list' in action_lower:
                ui_tasks.append('- [ ] Build data table/list view component.')
                ui_tasks.append('- [ ] Implement search/filtering/pagination UI.')
                ui_tasks.append('- [ ] fetch data from GET API.\n')
                api_tasks.append('- [ ] Create GET endpoint (list) with filters.')
                api_tasks.append('- [ ] Implement permission checks for viewing.\n')
            elif 'edit' in action_lower or 'update' in action_lower:
                ui_tasks.append('- [ ] Build edit form component.')
                ui_tasks.append('- [ ] Integrate PUT/PATCH API and handle success/error states.\n')
                api_tasks.append('- [ ] Create PUT/PATCH endpoint with validation.')
                api_tasks.append('- [ ] Implement permission checks for editing.\n')
            elif 'delete' in action_lower or 'remove' in action_lower:
                ui_tasks.append('- [ ] Build deletion confirmation modal.')
                ui_tasks.append('- [ ] Integrate DELETE API and handle success/error states.\n')
                api_tasks.append('- [ ] Create DELETE endpoint.')
                api_tasks.append('- [ ] Implement permission checks for deletion.\n')
            else:
                ui_tasks.append(f'- [ ] Implement UI for {current_section}.\n')
                api_tasks.append(f'- [ ] Implement API logic for {current_section}.\n')
                
        elif line.strip().startswith('|') and '---|---' not in line and '| #' not in line and '| Permission Key |' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2 and parts[0].replace('.', '').isdigit():
                req_text = parts[1]
                ui_tasks.append(f'- [ ] Ensure UI supports: {req_text}')
                api_tasks.append(f'- [ ] Ensure API supports: {req_text}')
            elif len(parts) >= 2 and '`' in parts[0]:
                perm = parts[0].replace('`', '')
                desc = parts[1]
                api_tasks.append(f'- [ ] Register permission: `{perm}` ({desc})')

    status_table = '''
---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
'''
    ui_tasks.append(status_table)
    api_tasks.append(status_table)
    
    ui_name = filename.replace('.md', '') + '-ui-task.md'
    api_name = filename.replace('.md', '') + '-api-task.md'
    
    ui_file = os.path.join(ui_dir, ui_name)
    api_file = os.path.join(api_dir, api_name)
    
    with open(ui_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ui_tasks))
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(api_tasks))

print('Task files generated successfully.')
