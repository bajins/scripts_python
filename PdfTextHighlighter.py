import fitz  # PyMuPDF的导入名是fitz

# --- 输入参数 ---
pdf_path = "S203_MB_HWA.0.1.pdf"
search_text = "MP35"
output_path = "S203_MB_HWA.0.1-Python.pdf"

try:
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    print(f"开始在 '{pdf_path}' 中搜索 '{search_text}'...")

    total_hits = 0
    # 遍历每一页
    for page_num, page in enumerate(doc):
        # "text" (默认)	纯文本字符串。PyMuPDF会尽力模拟原始页面的布局，使用空格和换行符。	快速获取页面的可读文本，用于预览或简单的复制粘贴。
        # "words"	单词列表。每个元素是一个元组 (x0, y0, x1, y1, "单词", ...)。	精确的全词匹配，获取每个单词的独立边界框。这是我们之前最终方案的核心。
        # "blocks"	文本块列表。每个元素是一个元组 (x0, y0, x1, y1, "整个文本块\n的内容", ...)。	按段落或逻辑块提取文本，适合处理文章或报告。
        # "dict"	详细的字典。一个嵌套的字典，结构为 {"width": ..., "height": ..., "blocks": [...]}，其中每个块包含行（lines），每行包含片段（spans）。	最强大的结构化数据。可以获取每个文本片段的字体、大小、颜色和精确坐标。
        # "json"	"dict" 格式的JSON字符串。与 "dict" 内容相同，但输出为JSON格式。	方便将提取结果传递给其他系统或Web应用。
        # "html"	HTML。生成一个简单的HTML页面，试图通过 <div> 和 <span> 的 style 属性来保留原始布局。	在Web浏览器中预览文本布局，保留格式。
        # "xhtml"	XHTML。与 "html" 类似，但遵循更严格的XML规范。	用于需要XML兼容性的场景。
        # "xml"	XML。生成一个详细的XML文档，结构与 "dict" 类似，包含每个字符的详细信息。	用于需要XML格式的深度数据分析。
        # "rawdict"	原始字典。与 "dict" 结构相同，但不按阅读顺序排序，而是反映PDF内部的原始对象顺序。	等效于 PDFBox 的 setSortByPosition(false)。用于底层分析。
        # "rawjson"	"rawdict" 格式的JSON字符串。	与 "rawdict" 用途相同。
        # 这是一个包含了页面所有文本信息的复杂字典
        # page_data = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)

        # # 2. 遍历页面中的所有文本“块” (通常是段落)
        # for block in page_data["blocks"]:
        #     if "lines" not in block: continue
        #     # 3. 遍历块中的所有“行”
        #     for line in block["lines"]:
        #         if "spans" not in line: continue
        #         # 4. 遍历行中的所有“片段” (Span)
        #         # 一个Span是具有相同字体、大小、颜色的连续文本
        #         for span in line["spans"]:
        #             if "text" not in span: continue
        #             # 5. 在每个唯一的Span的文本中查找我们的目标
        #             if search_text in span["text"]:
        #                 # span["bbox"] 是这个唯一片段的边界框，一个包含 (x0, y0, x1, y1) 的元组
        #                 rect = fitz.Rect(span["bbox"])
        #
        #                 print(f"PyMuPDF 找到实例 #{found_count}:")
        #                 print(f"  - 页码: {page_num + 1}")
        #                 print(f"  - 文本: '{span['text']}'")
        #                 print(f"  - 坐标 (x0, y0, x1, y1): ({rect[0]:.2f}, {rect[1]:.2f}, {rect[2]:.2f}, {rect[3]:.2f})")
        #                 print("-" * 20)

        # 1. 使用 search_for 查找文本(子字符串和正则表达式搜索)，返回一个Rect对象的列表
        # hits 是一个列表，里面包含了所有找到的文本的矩形边界框
        # hits = page.search_for(search_text)
        # 1. 使用 get_text("words") 获取单词列表
        # 每个 "word" 的格式是: (x0, y0, x1, y1, "单词文本", block_no, line_no, word_no)
        word_list = page.get_text("words")

        # 2. 遍历单词列表，寻找精确匹配
        # 使用集合来存储唯一的矩形坐标元组，实现高效去重
        unique_rects = set()
        for word in word_list:
            word_text = word[4]  # 提取单词的文本内容
            if word_text == search_text:
                # 3. 如果文本完全相等，就提取它的坐标
                # word[:4] 就是 (x0, y0, x1, y1)
                unique_rects.add(word[:4])

        if not unique_rects:
            continue  # 如果当前页没找到，就跳到下一页

        found_count = len(unique_rects)
        total_hits += found_count
        print(f"在第 {page_num + 1} 页找到了 {found_count} 处匹配。")

        # 2. 遍历所有找到的匹配项，并在其位置添加高亮注释
        for rect_tuple in unique_rects:
            rect = fitz.Rect(rect_tuple)  # 将元组转换为Rect对象
            # 打印出精确的坐标
            print(f"  - 坐标: (x0={rect.x0:.2f}, y0={rect.y0:.2f}, x1={rect.x1:.2f}, y1={rect.y1:.2f})")

            # 在该矩形位置添加一个黄色高亮
            highlight = page.add_highlight_annot(rect)
            highlight.update()  # 应用更改

            # 计算正圆的边界框
            # a) 计算原始矩形的中心点
            center = (rect.tl + rect.br) / 2
            # b) 半径取宽度和高度中的较大者的一半，并增加一点边距
            radius = max(rect.width, rect.height) / 2 + 2.0
            # c) 根据中心点和半径，创建一个新的、完全是正方形的边界框
            #    左上角点 = 中心点 - 半径
            #    右下角点 = 中心点 + 半径
            circle_rect = fitz.Rect(center - radius, center + radius)
            print(
                f"  - 绘制正圆于: (x0={circle_rect.x0:.2f}, y0={circle_rect.y0:.2f}, x1={circle_rect.x1:.2f}, y1={circle_rect.y1:.2f})")

            # 现在我们添加一个圆形注释
            circle = page.add_circle_annot(circle_rect)

            # 设置注释的属性：
            # colors={"stroke": (1, 0, 0)} 表示边框(stroke)颜色为RGB的红色
            # fill=None 表示内部不填充任何颜色
            # width=1.5 设置边框的线宽，让圈更明显一点
            circle.set_colors(stroke=(1, 0, 0), fill=None)
            circle.set_border(width=1.5)
            # 应用我们所做的所有更改
            circle.update()

    # 3. 保存带有高亮的新PDF文件
    if total_hits > 0:
        # garbage=4, deflate=True 是为了优化文件大小
        doc.save(output_path, garbage=4, deflate=True)
        print(f"\n成功！已将 {total_hits} 处高亮保存至 '{output_path}'。")
    else:
        print("\n在整个文档中没有找到指定的文本。")

except FileNotFoundError:
    print(f"错误：无法找到文件 '{pdf_path}'。")
except Exception as e:
    print(f"发生未知错误: {e}")
finally:
    # 确保文档对象在使用后被关闭
    if 'doc' in locals() and doc:
        doc.close()
