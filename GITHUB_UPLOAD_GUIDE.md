# 上传到 GitHub 的方法

本文档说明如何把本项目上传到 GitHub（适用于新仓库或已有仓库）。

## 前置条件

- 已安装 `git`
- 已有 GitHub 账号
- 已创建 GitHub 仓库（例如：`https://github.com/<用户名>/<仓库名>.git`）

## 方式一：HTTPS + Personal Access Token (PAT)

> 说明：GitHub 已不再支持账号密码方式登录，需要用 PAT 作为密码。

### 1) 生成 PAT

在 GitHub 设置中创建一个新 token，勾选 `repo` 权限（私有/公共仓库均需要）。

### 2) 初始化本地仓库

```bash
git init
git branch -m main
```

### 3) 添加远程仓库

```bash
git remote add origin https://github.com/<用户名>/<仓库名>.git
```

### 4) 提交并推送

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

执行推送时会提示输入用户名与密码：
- 用户名：你的 GitHub 用户名
- 密码：你的 PAT

## 方式二：SSH（推荐长期使用）

### 1) 生成并添加 SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

将 `~/.ssh/id_ed25519.pub` 内容添加到 GitHub 的 SSH Keys。

### 2) 添加远程并推送

```bash
git remote add origin git@github.com:<用户名>/<仓库名>.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

## 常见问题

### 1) 推送被拒绝（non-fast-forward）

远程分支已有提交时，先拉取并合并/变基：

```bash
git pull --rebase origin main
git push -u origin main
```

### 2) 远程仓库地址写错

```bash
git remote -v
git remote set-url origin <正确的仓库地址>
```

### 3) 认证失败（HTTP 403）

- 确认 PAT 有 `repo` 权限
- 确认仓库 URL 正确
- 确认账号对仓库有写权限

