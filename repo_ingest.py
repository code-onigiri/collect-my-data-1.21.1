import os
import subprocess
import shutil

# ================= 設定エリア =================

# 1. 読み込みたいリポジトリURL
REPO_URL = "https://github.com/Creators-of-Create/Create"

# 2. ブランチ (Noneならデフォルト)
BRANCH = "mc1.21.1/dev"

# 3. 中身を読み込むテキストファイルの拡張子
TEXT_EXTENSIONS = {
    '.java', '.json', '.toml', '.xml', '.mcmeta', 
    '.gradle', '.properties', '.md', '.txt'
}

# 4. リスト表示だけにするアセット/バイナリの拡張子
ASSET_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tga',
    '.ogg', '.mp3', '.wav',
    '.jar', '.zip', '.nbt', '.class', '.ico'
}

# 5. 無視するディレクトリ
IGNORE_DIRS = {
    '.git', '.idea', '.vscode', 'build', 'run', 'bin', 'out', '.gradle', 'eclipse'
}

# ============================================

def run_command(command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)

def get_repo_name(url):
    return url.rstrip('/').split('/')[-1].replace('.git', '')

def generate_output_filename(repo_name, branch):
    b_name = branch if branch else "default"
    # ファイル名に使えない文字を置換
    b_name = b_name.replace('/', '_').replace('\\', '_')
    return f"{repo_name}_{b_name}_summary.md"

def main():
    repo_name = get_repo_name(REPO_URL)
    output_file = generate_output_filename(repo_name, BRANCH)
    
    # 1. リポジトリのクローン/更新
    if os.path.exists(repo_name):
        print(f"🔄 リポジトリ '{repo_name}' を更新中...")
        run_command(["git", "fetch", "--all"], cwd=repo_name)
        if BRANCH:
            run_command(["git", "checkout", f"origin/{BRANCH}"], cwd=repo_name)
    else:
        print(f"📥 クローン中: {REPO_URL} ...")
        cmd = ["git", "clone", REPO_URL]
        if BRANCH:
            cmd.extend(["-b", BRANCH])
        run_command(cmd)

    print(f"📝 出力ファイル: {output_file}")
    
    code_count = 0
    asset_count = 0

    with open(output_file, "w", encoding="utf-8") as out:
        # ヘッダー
        out.write(f"# Repository Summary: {repo_name}\n")
        out.write(f"- URL: {REPO_URL}\n")
        out.write(f"- Branch: {BRANCH}\n")
        out.write(f"- Created: {output_file}\n\n")
        out.write("---\n\n")

        # ディレクトリ探索
        for root, dirs, files in os.walk(repo_name):
            # 無視フォルダを除外
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            # ファイルを分類
            text_files = []
            asset_files = []

            for f in files:
                _, ext = os.path.splitext(f)
                ext = ext.lower()
                if ext in TEXT_EXTENSIONS:
                    text_files.append(f)
                elif ext in ASSET_EXTENSIONS:
                    asset_files.append(f)

            rel_root = os.path.relpath(root, repo_name)
            if rel_root == ".": rel_root = "(Root)"

            # 1. テキストファイルは中身を書き出し
            for f in text_files:
                path = os.path.join(root, f)
                rel_path = os.path.join(rel_root, f)
                
                # 言語判定
                lang = ""
                if f.endswith('.java'): lang = 'java'
                elif f.endswith('.json'): lang = 'json'
                elif f.endswith('.toml'): lang = 'toml'
                elif f.endswith('.gradle'): lang = 'groovy'

                out.write(f"## 📄 File: {rel_path}\n")
                out.write(f"```{lang}\n")
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as tf:
                        out.write(tf.read())
                except Exception as e:
                    out.write(f"(Error reading file: {e})")
                out.write("\n```\n\n")
                code_count += 1

            # 2. アセットファイルはディレクトリ単位でまとめてリスト表示
            if asset_files:
                out.write(f"### 📦 Assets in: {rel_root}\n")
                out.write("```text\n")
                # ソートして見やすく
                asset_files.sort()
                for asset in asset_files:
                    out.write(f"{asset}\n")
                out.write("```\n\n")
                out.write("---\n\n")
                asset_count += len(asset_files)
                
            # 処理状況の表示 (ディレクトリごと)
            if text_files or asset_files:
                print(f"Processed: {rel_root}")

    print(f"\n✅ 完了しました！")
    print(f"出力ファイル: {output_file}")
    print(f"コードファイル数: {code_count}, アセットファイル数: {asset_count}")

if __name__ == "__main__":
    main()