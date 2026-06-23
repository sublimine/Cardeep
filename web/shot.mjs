import puppeteer from 'puppeteer';

const OUT = 'C:/Users/elias/AppData/Local/Temp/claude/C--Users-elias/3593f77d-a524-4eeb-82e6-5ab4a8b1bbb0/scratchpad';
const routes = [
  ['/', 'cx-landing'],
  ['/dashboard', 'cx-dashboard'],
  ['/terminal', 'cx-terminal'],
  ['/market', 'cx-market'],
];

const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
for (const [route, name] of routes) {
  try {
    await page.goto('http://localhost:5173' + route, { waitUntil: 'networkidle2', timeout: 45000 });
    await new Promise((r) => setTimeout(r, 4000)); // settle preloader/shader/animations
    await page.screenshot({ path: `${OUT}/${name}.jpg`, type: 'jpeg', quality: 85 });
    console.log('OK', name, '->', page.url());
  } catch (e) {
    console.log('FAIL', name, String(e).slice(0, 120));
  }
}
await browser.close();
console.log('DONE');
