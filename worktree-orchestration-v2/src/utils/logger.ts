/**
 * Structured logging utility using pino
 */

import pino from 'pino';

let rootLogger: pino.Logger | null = null;

export function createLogger(name: string): pino.Logger {
  if (!rootLogger) {
    rootLogger = pino({
      level: process.env.LOG_LEVEL || 'info',
      transport: process.env.NODE_ENV === 'development' ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'HH:MM:ss.l',
          ignore: 'pid,hostname',
        },
      } : undefined,
    });
  }

  return rootLogger.child({ component: name });
}

export function setLogLevel(level: string): void {
  if (rootLogger) {
    rootLogger.level = level;
  }
}
