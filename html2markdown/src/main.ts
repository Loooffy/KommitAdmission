import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { connect } from 'mongoose';
import * as dotenv from 'dotenv';

async function bootstrap() {
  dotenv.config();
  
  // Connect to MongoDB
  const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/html-to-markdown';
  try {
    await connect(MONGODB_URI);
    console.log('Connected to MongoDB successfully');
  } catch (error) {
    console.error('MongoDB connection error:', error);
  }

  const app = await NestFactory.create(AppModule);
  await app.listen(3000, '0.0.0.0');
  console.log('Server running on http://localhost:3000');
}
bootstrap(); 