// Renders the HTML report to PDF with a real "Page X of Y" footer.
// Usage: node render_report_pdf.js <input.html> <output.pdf>
const path = require('path');
const puppeteer = require(path.join(process.env.APPDATA, 'npm', 'node_modules', 'puppeteer'));

(async () => {
  const [input, output] = process.argv.slice(2);
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(input).replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  await page.pdf({
    path: output,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate:
      '<div style="width:100%;font-size:8.5px;font-family:Arial,Helvetica,sans-serif;color:#888;padding:0 13mm;display:flex;justify-content:space-between;">' +
      '<span>JPS Sales Analysis \u2014 Attribution &amp; Requirements Review</span>' +
      '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
    margin: { top: '16mm', bottom: '18mm', left: '13mm', right: '13mm' },
  });
  await browser.close();
})();
