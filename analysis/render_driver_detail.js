// Renders the detailed Driver Report HTML to A4 PDF with a Page X of Y footer. Usage: node render_driver_detail.js <input.html> <output.pdf>
const path = require('path');
const puppeteer = require(path.join(process.env.APPDATA, 'npm', 'node_modules', 'puppeteer'));
(async () => {
  const [input, output] = process.argv.slice(2);
  const browser = await puppeteer.launch({ executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless: true });
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(input).split(path.sep).join('/'), { waitUntil: 'networkidle0' });
  await page.pdf({
    path: output, format: 'A4', printBackground: true,
    preferCSSPageSize: true,
  });
  await browser.close();
})();
