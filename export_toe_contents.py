# ============================================================
# EXPORT: dump everything readable out of the open .toe file
#
# Run from Textport (Alt+T) with missJiba_Original.toe open:
#   exec(open(r'C:/Users/kroge/Dropbox/Documents/Postdoc/Fun/Jibo Performance/export_toe_contents.py').read())
#
# Creates a folder "toe_export" next to the .toe with:
#   - every script / table inside the project as a text file
#   - file_references.txt: every file on disk the project points to
# It only READS the project. Nothing in the .toe is changed.
# ============================================================
import os

OUT = os.path.join(project.folder, 'toe_export')
os.makedirs(OUT, exist_ok=True)
SKIP = ('/sys', '/ui', '/local')

def safe(path):
    return path.strip('/').replace('/', '__') or 'root'

n_dats, refs = 0, []
for o in root.findChildren(depth=None):
    if o.path.startswith(SKIP):
        continue
    # 1) scripts and tables
    if o.isDAT:
        try:
            txt = o.text
        except Exception:
            txt = ''
        if txt and txt.strip():
            ext = '.tsv' if getattr(o, 'isTable', False) else '.txt'
            with open(os.path.join(OUT, safe(o.path) + ext), 'w', encoding='utf-8') as f:
                f.write(txt)
            n_dats += 1
    # 2) any parameter that points at a file or folder
    for p in o.pars():
        try:
            if p.style in ('File', 'Folder', 'FileSave'):
                v = str(p.eval()).strip()
                if v:
                    refs.append('%s  .%s  =  %s' % (o.path, p.name, v))
        except Exception:
            pass

with open(os.path.join(OUT, 'file_references.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(sorted(set(refs))) + '\n')

print('=== export done ===')
print('%d scripts/tables written, %d file references found' % (n_dats, len(set(refs))))
print('Folder: ' + OUT)
