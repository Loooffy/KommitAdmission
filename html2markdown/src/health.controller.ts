import { Controller, Get } from '@nestjs/common';
import { HealthCheckService } from './healthCheck.service';

@Controller('ok')
export class HealthCheckController {
  constructor(private readonly healthCheckService: HealthCheckService) {}

  @Get('/')
  async healthCheck() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString()
    };
  }
} 