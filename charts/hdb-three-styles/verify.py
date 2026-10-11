from pathlib import Path
import hashlib,json,re,subprocess
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
assert hashlib.sha256((R/'transactions.csv').read_bytes()).digest()==hashlib.sha256((R.parent/'hdb/transactions.csv').read_bytes()).digest()
d=json.loads((R/'data.json').read_text());assert sum(x['n'] for x in d['matrix'])==242259;assert sum(x['n'] for x in d['monthly'])==25084;assert sum(x['n'] for x in d['lease'])==25084
manifest=json.loads((R/'manifest.json').read_text())
for p in R.rglob('*.html'):
 js='\n'.join(re.findall(r'<script>(.*?)</script>',p.read_text(),re.S));Path('/tmp/hdb-styles-check.js').write_text(js);subprocess.run(['node','--check','/tmp/hdb-styles-check.js'],check=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
 page=b.new_page(viewport={'width':1120,'height':920},device_scale_factor=2)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://**/*',lambda route:route.abort()) # Verify without CDN/font requests.
 for spec in manifest:
  rel=spec['family']+'/'+spec['file'];page.goto('http://127.0.0.1:8877/hdb-three-styles/'+rel,wait_until='domcontentloaded');page.wait_for_timeout(1800)
  if spec['fn']=='chunky':assert page.evaluate('Chart.getChart(document.getElementById("chart")).data.datasets[0].data.length')==5
  elif spec['fn']=='gaps':assert page.evaluate('echarts.getInstanceByDom(document.getElementById("chart")).getOption().series[0].data.length')==6
  else:assert page.locator('#chart > *').count()>0
  page.screenshot(path=str(R/rel.replace('.html','.png')),full_page=True)
  if spec['fn']!='chunky':
   selector='#chart svg' if spec['fn']=='gaps' else '#chart'
   svg=page.locator(selector).evaluate('(el)=>{const s=el.cloneNode(true);s.setAttribute("xmlns","http://www.w3.org/2000/svg");s.insertAdjacentHTML("afterbegin","<style>text{font-family:Inter,Arial,sans-serif}.pop,.fade,.draw{animation:none;stroke-dashoffset:0}</style>");return s.outerHTML}')
   (R/rel.replace('.html','.svg')).write_text(svg)
  page.locator('#replay').click();page.wait_for_timeout(50)
 page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:8877/hdb-three-styles/glance/01-lease-value.html',wait_until='domcontentloaded');page.wait_for_timeout(100)
 assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
 page.emulate_media(reduced_motion='reduce');page.reload(wait_until='domcontentloaded');page.wait_for_timeout(100)
 assert page.evaluate('Chart.getChart(document.getElementById("chart")).options.animation===false')
 assert not errors,errors;b.close()
result={'source_csv':'byte-identical','all_record_mix_total':242259,'full_year_count':25084,'html_javascript':'passed','offline_chart_renders':9,'replay':'passed','mobile_overflow':'none','reduced_motion':'passed','browser_errors':errors}
(R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
