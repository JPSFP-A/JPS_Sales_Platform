// Renders the Driver Report HTML to A4 PDF with a page footer. Usage: node render_driver_report.js <input.html> <output.pdf>
const path = require('path');
const puppeteer = require(path.join(process.env.APPDATA, 'npm', 'node_modules', 'puppeteer'));
(async () => {
  const [input, output] = process.argv.slice(2);
  const browser = await puppeteer.launch({ executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless: true });
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(input).split(path.sep).join('/'), { waitUntil: 'networkidle0' });
  await page.pdf({
    path: output, format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: false, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:7.5px;font-family:Arial,Helvetica,sans-serif;color:#66788A;padding:0 13mm;display:flex;justify-content:space-between;">' +
      '<span><b style="color:#062552">Jamaica Public Service</b> | Sales Forecast Driver Report | November 2026</span>' +
      '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
    margin: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  await browser.close();
})();
