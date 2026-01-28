#!/usr/bin/env python3
import sys
import argparse
import logging
from src.core.controller import controller
from src.core.config import config_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('run.log')
    ]
)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Run the dinhui-range-search system')
    parser.add_argument('--domain', type=str, help='Research domain')
    parser.add_argument('--start-year', type=int, help='Start year')
    parser.add_argument('--end-year', type=int, help='End year')
    parser.add_argument('--keywords', type=str, nargs='+', help='Keywords for search')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # 更新配置
    if args.domain:
        config_manager.set('research.domain', args.domain)
    if args.start_year:
        config_manager.set('research.start_year', args.start_year)
    if args.end_year:
        config_manager.set('research.end_year', args.end_year)
    if args.keywords:
        config_manager.set('research.keywords', args.keywords)
    
    # 如果启用详细输出，设置日志级别为DEBUG
    if args.verbose:
        for handler in logging.root.handlers:
            handler.setLevel(logging.DEBUG)
    
    # 运行工作流程
    print(f"开始执行工作流程...")
    print(f"研究领域: {config_manager.get_research_domain()}")
    start_year, end_year = config_manager.get_time_range()
    print(f"时间范围: {start_year}-{end_year}")
    
    success = controller.run_pipeline()
    
    if success:
        print("\n工作流程执行完成！")
        print("生成的报告保存在 data/reports/ 目录中")
    else:
        print("\n工作流程执行失败，请查看日志获取详细信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()
