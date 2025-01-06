import { Controller, Post, Body, HttpException, HttpStatus, Get } from '@nestjs/common';
import { ConversionService } from './conversion.service';

@Controller('convert')
export class ConversionController {
  constructor(private readonly conversionService: ConversionService) {}

  @Post('/')
  async convertToMarkdown(@Body('url') url: string) {
    if (!url) {
      throw new HttpException('URL is required', HttpStatus.BAD_REQUEST);
    }

    try {
      const markdown = await this.conversionService.convertUrlToMarkdown(url);
      return { markdown };
    } catch (error) {
      console.error('Conversion error:', {
        url,
        error: error.message,
        stack: error.stack
      });
      
      throw new HttpException(
        `Error converting URL to markdown: ${error.message}`,
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
} 