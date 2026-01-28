import schedule
import time
import threading
import logging
from .controller import controller

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("调度器已停止")
    
    def schedule_daily(self, hour, minute):
        """设置每日定时任务"""
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._run_pipeline)
        logger.info(f"已设置每日 {hour:02d}:{minute:02d} 执行任务")
    
    def schedule_weekly(self, day_of_week, hour, minute):
        """设置每周定时任务"""
        days = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }
        if day_of_week.lower() in days:
            days[day_of_week.lower()].at(f"{hour:02d}:{minute:02d}").do(self._run_pipeline)
            logger.info(f"已设置每周 {day_of_week} {hour:02d}:{minute:02d} 执行任务")
    
    def _run_pipeline(self):
        """执行工作流程"""
        logger.info("调度器触发工作流程执行")
        try:
            controller.run_pipeline()
        except Exception as e:
            logger.error(f"调度器执行任务失败: {str(e)}")
    
    def _run_scheduler(self):
        """运行调度器主循环"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

# 创建全局调度器实例
scheduler = Scheduler()
