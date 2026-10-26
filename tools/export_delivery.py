"""Export a clean snapshot for the expressly requested empty delivery repository."""
from pathlib import Path
import subprocess,shutil,re

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'tmp/github-entrega'
tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
paths=sorted(set(tracked+untracked))

def permitted(path):
    p=Path(path);parts=p.parts
    if any(part in {'.git','.venv','venv','node_modules','__pycache__','.pytest_cache','tmp','data','dist'} for part in parts):return False
    if p.suffix.lower() in {'.db','.sqlite','.sqlite3','.log','.pem','.key','.pyc','.pyo'}:return False
    if p.name.startswith('.env') and not p.name.endswith('.example'):return False
    if 'credentials' in p.name.lower():return False
    if p.parts[0]=='output' and p.suffix.lower()!='.pdf':return False
    return True

paths=[p for p in paths if permitted(p) and (ROOT/p).is_file()]
secrets={}
env=ROOT/'.env'
if env.exists():
    for line in env.read_text(encoding='utf-8-sig').splitlines():
        if '=' not in line or line.lstrip().startswith('#'):continue
        key,value=line.split('=',1);value=value.strip().strip('\"\'')
        if any(k in key.upper() for k in ('SECRET','PASSWORD','KEY','TOKEN')) and len(value)>=16 and not value.startswith(('change-','your_','tu_')):secrets[key.strip()]=value
leaks=[]
patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9_]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
for rel in paths:
    blob=(ROOT/rel).read_bytes()
    for name,value in secrets.items():
        if value.encode() in blob:leaks.append((rel,name))
    if Path(rel).suffix.lower() in {'.py','.js','.jsx','.json','.md','.yml','.yaml','.txt','.ps1','.html','.example'}:
        text=blob.decode('utf-8',errors='replace')
        for i,pattern in enumerate(patterns):
            # This utility contains the detection patterns, never credentials.
            if pattern.search(text):leaks.append((rel,f'credential_pattern_{i}'))
if leaks:raise SystemExit('Publicación detenida: '+repr(leaks))
DEST.mkdir(parents=True,exist_ok=True)
if (DEST/'.git').exists():raise SystemExit('Exportación ya inicializada: revisar antes de reemplazar')
for rel in paths:
    target=DEST/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
print(f'Exportación: {len(paths)} archivos. Secretos locales contrastados: {len(secrets)}. Sin coincidencias.')
print(DEST)
