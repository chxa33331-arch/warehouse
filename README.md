# 🌧️ 雨云自动签到工具

基于 Selenium + ddddocr 的雨云自动签到工具，支持 GitHub Actions 自动执行。

## ✨ 功能特性

- 🔐 自动登录雨云账号
- 🖼️ 自动识别验证码（基于 ddddocr）
- 📅 每日自动签到赚取积分
- 👥 支持多账号
- 🤖 GitHub Actions 自动执行
- 📸 失败时自动保存截图

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）

1. **Fork 本仓库**

2. **配置 Secrets**
   
   进入仓库 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   
   添加以下密钥：
   
   | Name | Value |
   |------|-------|
   | `RAINYUN_USERNAME` | 你的雨云用户名/邮箱/手机号 |
   | `RAINYUN_PASSWORD` | 你的雨云密码 |

3. **启用 Actions**
   
   进入 `Actions` 标签页，启用 Workflows

4. **手动测试**
   
   点击 `Run workflow` 手动触发测试

### 方式二：本地运行

```bash
# 克隆仓库
git clone https://github.com/yourusername/rainyun-auto-signin.git
cd rainyun-auto-signin

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export RAINYUN_USERNAME="your_username"
export RAINYUN_PASSWORD="your_password"

# 运行
python main.py