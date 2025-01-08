import { Controller, Get, HttpException, HttpStatus, Param } from '@nestjs/common';
import { ConversionService } from './conversion.service';

@Controller('convert')
export class ConversionController {
  constructor(
    private readonly conversionService: ConversionService,
  ) {}

  @Get(':url')
  async convertToMarkdown(@Param('url') url: string) {
    try {
      const decodedUrl = decodeURIComponent(url);
      
      try {
        const markdown = await this.conversionService.convertUrlToMarkdown(decodedUrl);
        
        return {
          success: true,
          url: decodedUrl,
          markdown
        };
      } catch (error) {
        return {
          success: false,
          url: decodedUrl,
          error: error.message
        };
      }
      
    } catch (error) {
      console.error('Conversion error:', {
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