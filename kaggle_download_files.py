import requests
import os
from zipfile import ZipFile
from IPython.display import FileLink, display

# 创建下载目录（可选）
download_dir = 'downloaded_files'
os.makedirs(download_dir, exist_ok=True)

# 要下载的多个文件URL列表
urls = [
    'https://jaist.dl.sourceforge.net/project/tortoisesvn/1.14.5/Application/TortoiseSVN-1.14.5.29465-x64-svn-1.14.2.msi',
    'https://jaist.dl.sourceforge.net/project/tortoisesvn/1.14.6/Application/TortoiseSVN-1.14.6.29673-x64-svn-1.14.3.msi',
    'https://jaist.dl.sourceforge.net/project/tortoisesvn/1.14.7/Application/TortoiseSVN-1.14.7.29687-x64-svn-1.14.3.msi'
]

# 下载每个文件到本地目录
for url in urls:
    filename = os.path.join(download_dir, os.path.basename(url))
    print(f"Downloading {url} to {filename}")
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

# 打包所有文件为 zip
zip_filename = 'downloaded_files.zip'
with ZipFile(zip_filename, 'w') as zipf:
    for root, dirs, files in os.walk(download_dir):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=file)

print(f"All files zipped into {zip_filename}")

# 显示下载链接
display(FileLink(zip_filename))