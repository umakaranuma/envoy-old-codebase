import os
import ast
import json

def analyze_directory(root_dir):
    modules = ['core', 'crm', 'customer', 'finance', 'policy']
    results = {m: {'backend': {}, 'frontend': {}} for m in modules}

    for module in modules:
        module_path = os.path.join(root_dir, module)
        if not os.path.exists(module_path):
            continue

        for root, dirs, files in os.walk(module_path):
            # Check if we are inside a 'services' or 'utils' or 'helpers' folder
            path_parts = root.split(os.sep)
            
            is_interesting_dir = any(d.lower() in ['services', 'utils', 'helpers', 'utils'] for d in path_parts)
            
            # Simple heuristic for backend vs frontend
            is_backend = '-api' in root or 'backend' in root
            is_frontend = '-ui' in root or 'frontend' in root
            target = 'backend' if is_backend else 'frontend'

            if is_interesting_dir:
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                tree = ast.parse(f.read())
                                funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                                if funcs or classes:
                                    rel_path = os.path.relpath(file_path, module_path)
                                    results[module][target][rel_path] = {'functions': funcs, 'classes': classes}
                        except Exception as e:
                            pass
                    elif file.endswith(('.js', '.ts', '.tsx', '.jsx')):
                        # Simple regex or parsing for JS/TS is harder, just count files for now or use regex
                        import re
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                funcs = re.findall(r'(?:function\s+|const\s+)(\w+)\s*(?:=|:\s*function|\([^)]*\)\s*=>)', content)
                                if funcs:
                                    rel_path = os.path.relpath(file_path, module_path)
                                    results[module][target][rel_path] = {'functions': list(set(funcs))}
                        except Exception:
                            pass

    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    analyze_directory(r"f:\apptimus\envoy\agentic_coding")
