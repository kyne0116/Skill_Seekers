#!/usr/bin/env python3
"""
GitHub Token 诊断工具
验证 GITHUB_TOKEN 是否被正确读取和使用
"""
import os
import sys

def test_token():
    """测试 GitHub token 配置"""
    print("=" * 60)
    print("GitHub Token 诊断")
    print("=" * 60)

    # 1. 检查环境变量
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print(f"✅ GITHUB_TOKEN 环境变量已设置")
        print(f"   Token 前缀: {token[:8]}...")
        print(f"   Token 长度: {len(token)} 字符")
    else:
        print("❌ GITHUB_TOKEN 环境变量未设置")
        print("   请运行: set GITHUB_TOKEN=your_token_here")
        return False

    # 2. 测试 PyGithub 连接
    try:
        from github import Github, Auth
        print("\n正在测试 GitHub API 连接...")

        # 使用新版 API 创建客户端
        auth = Auth.Token(token)
        g = Github(auth=auth)

        # 获取当前用户信息（验证 token 有效性）
        user = g.get_user()
        print(f"✅ Token 有效！")
        print(f"   用户名: {user.login}")
        print(f"   类型: {user.type}")

        # 检查 rate limit（兼容新旧版本）
        try:
            rate_limit = g.get_rate_limit()

            # 尝试不同的 API 访问方式
            if hasattr(rate_limit, 'core'):
                # PyGithub < 2.0
                core = rate_limit.core
                remaining = core.remaining
                limit = core.limit
                reset = core.reset
            elif hasattr(rate_limit, 'resources'):
                # PyGithub >= 2.0 (可能的新结构)
                core = rate_limit.resources.core
                remaining = core.remaining
                limit = core.limit
                reset = core.reset
            else:
                # 直接访问属性
                remaining = getattr(rate_limit, 'remaining', None)
                limit = getattr(rate_limit, 'limit', None)
                reset = getattr(rate_limit, 'reset', None)

                if remaining is None:
                    # 如果还是不行，直接打印对象看结构
                    print(f"\n⚠️  无法解析 rate limit 对象")
                    print(f"   对象类型: {type(rate_limit)}")
                    print(f"   可用属性: {dir(rate_limit)}")
                    # 尝试调用 _rawData 或其他内部属性
                    if hasattr(rate_limit, '_rawData'):
                        print(f"   原始数据: {rate_limit._rawData}")
                    remaining = "未知"
                    limit = "未知"

            print(f"\n📊 API 配额状态:")
            print(f"   剩余请求: {remaining}/{limit}")
            if reset:
                print(f"   重置时间: {reset}")

            if isinstance(remaining, int) and remaining < 100:
                print(f"\n⚠️  警告: 剩余配额较低 ({remaining})")
                print(f"   建议等待配额重置或使用新 token")
            elif isinstance(remaining, int):
                print(f"\n✅ 配额充足，可以开始抓取")

        except Exception as e:
            print(f"\n⚠️  无法获取 rate limit: {e}")
            print(f"   Token 仍然有效，可以继续使用")

        return True

    except ImportError:
        print("❌ PyGithub 未安装")
        print("   运行: pip install PyGithub")
        return False
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        if "401" in str(e):
            print("   Token 无效或已过期")
        elif "403" in str(e):
            print("   Token 权限不足或 rate limit 已用尽")
        return False

def test_repo_access():
    """测试目标仓库访问"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return

    print("\n" + "=" * 60)
    print("测试目标仓库访问")
    print("=" * 60)

    try:
        from github import Github, Auth
        auth = Auth.Token(token)
        g = Github(auth=auth)

        # 测试目标仓库
        repo_name = "spring-ai-alibaba/examples"
        print(f"正在访问: {repo_name}")

        repo = g.get_repo(repo_name)
        print(f"✅ 仓库访问成功")
        print(f"   名称: {repo.full_name}")
        print(f"   描述: {repo.description}")
        print(f"   主分支: {repo.default_branch}")
        print(f"   文件数: ~{repo.size} KB")

        # 统计文件类型
        print(f"\n正在分析仓库结构...")
        contents = repo.get_contents("")
        file_count = 0
        dir_count = 0

        for content in contents:
            if content.type == "dir":
                dir_count += 1
            else:
                file_count += 1

        print(f"   根目录文件: {file_count}")
        print(f"   根目录文件夹: {dir_count}")

        # 检查当前配额消耗
        rate_limit = g.get_rate_limit()
        print(f"\n   本次测试消耗: ~3 个 API 请求")
        print(f"   剩余配额: {rate_limit.core.remaining}")

    except Exception as e:
        print(f"❌ 仓库访问失败: {e}")

if __name__ == '__main__':
    print("\n🔍 开始诊断...\n")

    if test_token():
        test_repo_access()
        print("\n" + "=" * 60)
        print("诊断完成！")
        print("=" * 60)
        print("\n如果以上测试通过，unified scraper 应该能正常使用 token")
        print("如果抓取仍然很慢，可能是仓库太大或网络问题\n")
    else:
        print("\n❌ 诊断失败，请修复以上问题后重试\n")
