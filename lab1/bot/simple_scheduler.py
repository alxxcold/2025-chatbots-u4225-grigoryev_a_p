#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой планировщик задач для Telegram-бота
Альтернатива JobQueue для Python 3.13
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
import pytz
from typing import Callable, Any

logger = logging.getLogger(__name__)

class SimpleScheduler:
    """Простой планировщик задач"""
    
    def __init__(self, bot, timezone):
        self.bot = bot
        self.timezone = timezone
        self.tasks = []
        self.running = False
        
    async def start(self):
        """Запуск планировщика"""
        self.running = True
        logger.info("Простой планировщик запущен")
        
        # Запускаем все задачи
        for task_func, schedule_time, days, name in self.tasks:
            asyncio.create_task(self._run_scheduled_task(task_func, schedule_time, days, name))
    
    async def stop(self):
        """Остановка планировщика"""
        self.running = False
        logger.info("Простой планировщик остановлен")
    
    def add_daily_task(self, task_func: Callable, schedule_time: time, days: tuple = None, name: str = None):
        """Добавить ежедневную задачу"""
        self.tasks.append((task_func, schedule_time, days, name))
        logger.info(f"Добавлена задача '{name}' на {schedule_time.strftime('%H:%M')} МСК")
    
    def add_one_time_task(self, task_func: Callable, when: datetime, name: str = None):
        """Добавить разовую задачу"""
        self.tasks.append((task_func, when.time(), None, name))
        logger.info(f"Добавлена разовая задача '{name}' на {when.strftime('%H:%M:%S %d.%m.%Y')} МСК")
    
    async def _run_scheduled_task(self, task_func: Callable, schedule_time: time, days: tuple, name: str):
        """Запуск запланированной задачи"""
        while self.running:
            try:
                now = datetime.now(self.timezone)
                current_time = now.time()
                current_weekday = now.weekday()
                
                # Проверяем, нужно ли выполнять задачу сегодня
                should_run = True
                if days is not None:
                    should_run = current_weekday in days
                
                # Проверяем время
                if should_run and current_time >= schedule_time:
                    # Проверяем, не выполняли ли мы уже эту задачу сегодня
                    last_run_key = f"{name}_{now.date()}"
                    if not hasattr(self, '_last_runs'):
                        self._last_runs = set()
                    
                    if last_run_key not in self._last_runs:
                        logger.info(f"Выполнение задачи '{name}' в {current_time.strftime('%H:%M:%S')}")
                        try:
                            await task_func(self.bot)
                            self._last_runs.add(last_run_key)
                            logger.info(f"Задача '{name}' выполнена успешно")
                        except Exception as e:
                            logger.error(f"Ошибка выполнения задачи '{name}': {e}")
                
                # Ждем до следующей минуты
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Ошибка в планировщике задачи '{name}': {e}")
                await asyncio.sleep(60)
