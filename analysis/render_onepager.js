// Renders a one-page HTML to A4 PDF. Usage: node render_onepager.js <input.html> <output.pdf>
const path = require('path');
const puppeteer = require(path.join(process.env.APPDATA, 'npm', 'node_modules', 'puppeteer'));
(async () => {
  const [input, output] = process.argv.slice(2);
  const browser = await puppeteer.launch({ executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless: true });
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(input).split(path.sep).join('/'), { waitUntil: 'networkidle0' });
  await page.pdf({ path: output, format: 'A4', printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 }, preferCSSPageSize: true });
  await browser.close();
})();
