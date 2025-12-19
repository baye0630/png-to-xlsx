# 连接 GitHub 仓库指南

## 第一步：安装 Git（如果尚未安装）

1. 访问 https://git-scm.com/download/win 下载 Git for Windows
2. 运行安装程序，使用默认设置即可
3. 安装完成后，重新打开终端

## 第二步：配置 Git（首次使用）

```bash
git config --global user.name "您的用户名"
git config --global user.email "您的邮箱"
```

## 第三步：连接 GitHub 仓库

### 方式一：克隆现有仓库（推荐用于获取已有项目）

```bash
# 使用 HTTPS（需要个人访问令牌）
git clone https://github.com/用户名/仓库名.git

# 或使用 SSH（需要先配置 SSH 密钥）
git clone git@github.com:用户名/仓库名.git
```

### 方式二：将本地项目连接到 GitHub 仓库

如果您的项目已经在本地，想要连接到 GitHub：

```bash
# 1. 初始化 Git 仓库（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交文件
git commit -m "Initial commit"

# 4. 添加远程仓库
git remote add origin https://github.com/用户名/仓库名.git

# 5. 推送到 GitHub
git push -u origin main
```

### 方式三：添加远程仓库到现有项目

如果项目已经有 Git 仓库，只需要添加远程：

```bash
# 查看现有远程仓库
git remote -v

# 添加 GitHub 远程仓库
git remote add origin https://github.com/用户名/仓库名.git

# 或如果已存在 origin，可以修改
git remote set-url origin https://github.com/用户名/仓库名.git
```

## 第四步：身份验证

### HTTPS 方式（需要个人访问令牌）

1. 访问 GitHub：Settings > Developer settings > Personal access tokens > Tokens (classic)
2. 生成新令牌，选择 `repo` 权限
3. 复制令牌，在 Git 要求输入密码时使用此令牌

### SSH 方式（推荐）

1. 生成 SSH 密钥：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. 复制公钥内容：
```bash
# Windows PowerShell
cat ~/.ssh/id_ed25519.pub

# 或 Windows CMD
type %USERPROFILE%\.ssh\id_ed25519.pub
```

3. 在 GitHub 上添加 SSH 密钥：
   - 访问 GitHub：Settings > SSH and GPG keys
   - 点击 "New SSH key"
   - 粘贴公钥内容并保存

4. 测试连接：
```bash
ssh -T git@github.com
```

## 常用命令

```bash
# 查看远程仓库
git remote -v

# 拉取最新代码
git pull origin main

# 推送代码
git push origin main

# 查看状态
git status

# 查看提交历史
git log
```


