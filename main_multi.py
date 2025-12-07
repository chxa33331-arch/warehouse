#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨云自动签到工具 - 多账号版本
"""

import os
import sys
import json
import time
from main import RainyunSignin


def parse_accounts():
    """
    解析多账号配置
    支持格式:
    1. JSON格式: [{"username": "xxx", "password": "xxx"}, ...]
    2. 简单格式: username1----password1\nusername2----password2
    """
    accounts_str = os.environ.get("RAINYUN_ACCOUNTS", "")
    
    if not accounts_str:
        # 使用单账号配置
        username = os.environ.get("RAINYUN_USERNAME", "")
        password = os.environ.get("RAINYUN_PASSWORD", "")
        if username and password:
            return [{"username": username, "password": password}]
        return []
    
    accounts = []
    
    # 尝试JSON格式解析
    try:
        accounts = json.loads(accounts_str)
        return accounts
    except json.JSONDecodeError:
        pass
    
    # 尝试简单格式解析
    for line in accounts_str.strip().split("\n"):
        line = line.strip()
        if "----" in line:
            parts = line.split("----")
            if len(parts) >= 2:
                accounts.append({
                    "username": parts[0].strip(),
                    "password": parts[1].strip()
                })
    
    return accounts


def main():
    """主函数"""
    accounts = parse_accounts()
    
    if not accounts:
        print("❌ 未配置任何账号")
        sys.exit(1)
    
    print("=" * 50)
    print("🌧️ 雨云自动签到工具 - 多账号版本")
    print(f"📊 共 {len(accounts)} 个账号")
    print("=" * 50)
    
    results = []
    
    for i, account in enumerate(accounts, 1):
        username = account.get("username", "")
        password = account.get("password", "")
        
        print(f"\n{'='*50}")
        print(f"📧 账号 {i}/{len(accounts)}: {username[:3]}***")
        print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        try:
            signin = RainyunSignin(username, password, headless=True)
            success = signin.run()
            results.append({
                "username": username,
                "success": success
            })
        except Exception as e:
            print(f"❌ 账号 {username} 签到出错: {e}")
            results.append({
                "username": username,
                "success": False,
                "error": str(e)
            })
        
        # 账号间间隔
        if i < len(accounts):
            print("\n⏳ 等待 10 秒后处理下一个账号...")
            time.sleep(10)
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 签到结果汇总")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    
    for r in results:
        status = "✅ 成功" if r["success"] else "❌ 失败"
        print(f"  {r['username'][:3]}***: {status}")
    
    print("=" * 50)
    print(f"✅ 成功: {success_count} | ❌ 失败: {fail_count}")
    print("=" * 50)
    
    # 如果全部失败则退出码为1
    if fail_count == len(results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()