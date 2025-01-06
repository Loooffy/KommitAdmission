import { Injectable } from '@nestjs/common';

@Injectable()
export class HealthCheckService {
  async checkHealth(): Promise<{ status: string; timestamp: string }> {
    return {
      status: 'ok',
      timestamp: new Date().toISOString()
    };
  }
} 