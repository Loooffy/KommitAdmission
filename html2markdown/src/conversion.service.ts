import { Injectable } from '@nestjs/common';
import * as puppeteer from 'puppeteer';
import * as fs from 'fs';
import * as path from 'path';
import { ocr } from 'llama-ocr';

@Injectable()
export class ConversionService {
  async convertUrlToMarkdown(url: string): Promise<string> {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    try {
      await page.goto(url, { waitUntil: 'networkidle2' });

      const screenshotPath = path.join(__dirname, '..', 'temp', 'page.png');
      
      const tempDir = path.join(__dirname, '..', 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      await page.screenshot({ path: screenshotPath, fullPage: true });

      const markdown = await ocr({
        filePath: screenshotPath,
        apiKey: process.env.TOGETHER_API_KEY,
      });
      
      console.log('Conversion complete');
      
      try {
        fs.unlinkSync(screenshotPath);
      } catch (error) {
        console.error(`Error deleting screenshot: ${error}`);
      }
      
      return markdown;

    } catch (error) {
      console.error('Error during conversion:', error);
      throw error;
    } finally {
      await browser.close();
    }
  }
} 