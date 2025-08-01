# HTML to PDF Converter

基于Flask的HTML转PDF服务，可以将HTML内容转换为PDF格式文件。

示例：[https://tool.bajins.com/wp](https://tool.bajins.com/wp)



## 功能特点

- 将HTML网页内容转换为PDF文件
- 支持自定义页面尺寸和边距
- 提供Web界面和RESTful API接口
- 支持两种转换引擎：WeasyPrint（推荐）和xhtml2pdf


## 安装说明

### 环境要求

- Python 3.6+
- Flask
- WeasyPrint 或 xhtml2pdf
- wkhtmltopdf (可选，用于xhtml2pdf)

### 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/bajins/scripts_python.git
cd html2pdf_flask
```

2. 安装依赖：
```bash
pip install -r Flask WeasyPrint xhtml2pdf wkhtmltopdf -y
```

3. 安装PDF转换引擎：
   
   选择1：安装WeasyPrint（推荐）
   ```bash
   pip install weasyprint
   ```
   
   选择2：安装xhtml2pdf
   ```bash
   pip install xhtml2pdf
   ```

4. 启动服务：
```bash
python app.py
```

## 使用方法

### Web界面使用

1. 启动服务后，访问 `http://localhost:8080`
2. 选择要转换的HTML文件
3. 设置页面参数（页面大小、方向、边距等）
4. 选择转换引擎
5. 点击"上传并转换"按钮，系统会自动下载生成的PDF文件

### API接口使用

#### 1. 通过HTML内容生成PDF

**URL**: `/generate-pdf`
**方法**: `POST`
**Content-Type**: `text/html`
**参数**: 请求体中直接包含HTML内容

**示例**:

```bash
curl -X POST \
  http://localhost:8080/generate-pdf \
  -H 'Content-Type: text/html' \
  -d '<h1>Hello World</h1><p>这是一个测试</p>' \
  -o output.pdf
```

## 配置选项

### 页面参数
- `page_size`: 页面尺寸 (A4, A3, Letter, Legal)
- `orientation`: 页面方向 (portrait, landscape)
- `margin_top`: 上边距 (毫米)
- `margin_bottom`: 下边距 (毫米)
- `margin_left`: 左边距 (毫米)
- `margin_right`: 右边距 (毫米)

### 服务配置

在 `scripts_python/html2pdf_flask/app.py` 中修改:
- `host`: 服务监听地址 (默认: 0.0.0.0)
- `port`: 服务监听端口 (默认: 8080)
- `debug`: 调试模式 (默认: True)

## 项目结构

```
html2pdf_flask/
├── app.py                  # 主应用文件
├── README.md              # 说明文档
└── templates/             # HTML模板目录
    └── upload.html        # 上传页面模板
```

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系项目维护者。