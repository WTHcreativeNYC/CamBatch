# Publishing CamBatch on GitHub

## 1. Create the repository

1. Sign in to GitHub and choose **New repository**.
2. Use `CamBatch` as the repository name.
3. Add the description: `Multi-camera Final and Viewport batch rendering for Blender 4.5 LTS and 5.x.`
4. Choose **Public**.
5. Do not initialize the repository with a README, license, or `.gitignore`; these files are already included.

## 2. Prepare the local repository

Run these commands from the folder containing the source files:

```powershell
git init
git add .
git commit -m "Release CamBatch 1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/CamBatch.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with the actual GitHub account name.

## 3. Create the first release

1. Open the repository on GitHub.
2. Choose **Releases > Create a new release**.
3. Create the tag `v1.0.0` targeting `main`.
4. Set the title to `CamBatch 1.0.0`.
5. Copy the `1.0.0` section from `CHANGELOG.md` into the release notes.
6. Attach `cam_batch-1.0.0.zip` as the downloadable installation file.
7. Publish the release.

Users should install the attached release ZIP. GitHub's automatically generated **Source code (zip)** archive is not the Blender installation package.

## 4. Recommended repository settings

- Enable **Issues** for bug reports and feature requests.
- Add the topics `blender`, `blender-addon`, `blender-extension`, `camera`, `rendering`, and `batch-render`.
- Set the website field later if a documentation or portfolio page is created.
- Protect the `main` branch if additional contributors join.

## 5. Publishing an update

1. Update `version` in `blender_manifest.toml`.
2. Update `ADDON_VERSION` in `__init__.py` to the same value.
3. Add release notes to `CHANGELOG.md`.
4. Build and validate the extension with Blender:

```powershell
blender --command extension build --source-dir . --output-dir ..
blender --command extension validate ..\cam_batch-VERSION.zip
```

5. Test installation in both Blender 4.5 LTS and the current Blender 5.x release.
6. Commit, push, create a matching Git tag, and attach the validated ZIP to a new GitHub Release.
