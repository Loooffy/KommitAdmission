import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ConversionController } from './conversion.controller';
import { ConversionService } from './conversion.service';
import { HealthCheckController } from './health.controller';
import { HealthCheckService } from './healthCheck.service';
import { MongooseModule } from '@nestjs/mongoose';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
  ],
  controllers: [
    ConversionController,
    HealthCheckController],
  providers: [
    ConversionService,
    HealthCheckService,
  ],
})
export class AppModule {} 