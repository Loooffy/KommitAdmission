const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const Tesseract = require('tesseract.js');

// Create an interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Ask the user for the website URL
rl.question('Enter the website URL: ', async (url) => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Capture screenshot of the full page
    const screenshotPath = path.join(__dirname, 'page.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });

    console.log(`Screenshot saved at ${screenshotPath}`);

    try {
      // Perform OCR on the screenshot using tesseract.js
      const result = await Tesseract.recognize(
        screenshotPath,
        'eng',
        { logger: m => console.log(m) }
      );

      const text = result.data.text;
      console.log('OCR Text:', text);

      // Write to markdown file
      const markdownPath = path.join(__dirname, 'output.md');
      fs.writeFileSync(markdownPath, text, 'utf8');

      console.log(`Markdown saved at ${markdownPath}`);
    } catch (ocrError) {
      console.error('Error during OCR:', ocrError);
    }

  } catch (error) {
    console.error('Error navigating to the URL:', error);
  } finally {
    await browser.close();
    rl.close();
  }
});