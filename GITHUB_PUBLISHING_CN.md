# CamBatch GitHub 上线指南

## 准备内容

正式发布需要上传两部分：

- 源代码仓库：当前文件夹中的源码和文档。
- 安装包：由 Blender 验证过的 `cam_batch-1.0.0.zip`。

不要让用户安装 GitHub 自动生成的 `Source code (zip)`，它不是 Blender 扩展安装包。

## 创建仓库

1. 登录 GitHub，点击 **New repository**。
2. Repository name 填写 `CamBatch`。
3. Description 填写：`Multi-camera Final and Viewport batch rendering for Blender 4.5 LTS and 5.x.`
4. 选择 **Public**。
5. 不要勾选自动创建 README、License 或 `.gitignore`。
6. 点击 **Create repository**。

## 上传源码

在 CamBatch 源码文件夹中运行：

```powershell
git init
git add .
git commit -m "Release CamBatch 1.0.0"
git branch -M main
git remote add origin https://github.com/你的用户名/CamBatch.git
git push -u origin main
```

把命令中的 `你的用户名` 替换为实际 GitHub 用户名。

## 发布安装包

1. 打开 GitHub 仓库的 **Releases** 页面。
2. 点击 **Create a new release**。
3. 新建 Tag：`v1.0.0`。
4. Release title 填写 `CamBatch 1.0.0`。
5. 将 `CHANGELOG.md` 中 1.0.0 的内容复制到说明中。
6. 上传 `cam_batch-1.0.0.zip`。
7. 点击 **Publish release**。

## 推荐设置

- 开启 Issues。
- 添加 Topics：`blender`、`blender-addon`、`blender-extension`、`camera`、`rendering`、`batch-render`。
- 在 About 区域写明支持 Blender 4.5 LTS 和 5.x。
- 发布后在一台干净环境的 Blender 中，从 GitHub Release 重新下载并安装一次。

## 后续更新

每次发布新版本时：

1. 同步修改 `blender_manifest.toml` 中的 `version` 和 `__init__.py` 中的 `ADDON_VERSION`。
2. 更新 `CHANGELOG.md`。
3. 使用 Blender 构建并验证新的 ZIP。
4. 在 Blender 4.5 LTS 和最新 Blender 5.x 中测试。
5. 提交并推送源码。
6. 创建相同版本号的新 Tag 和 GitHub Release。
7. 将新的验证版 ZIP 作为 Release 附件上传。
