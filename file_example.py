# 'r' ：只读模式，对文件进行读取操作。
# 'w' ：写入模式，覆盖文件原有内容，如果文件不存在则创建新文件。
# 'a' ：追加模式，在文件末尾追加新内容，如果文件不存在则创建新文件。
# 'x' ：创建模式，创建新文件，如果文件已存在则报错。
# 'b' ：二进制模式，对文件进行二进制读写操作。
if __name__ == '__main__':
    # 以二进制模式打开文件
    with open(r"C:\Users\claer\Desktop\.lemminx.7z", 'rb') as file:
        # 读取文件内容（二进制）
        binary_data = file.read()
    with open(r"C:\Users\claer\Desktop\三一看板优化\boardentsitcenter\images\center\border_bg_center.png", 'ab') as file:
        print(file.tell())
        # 写入文件内容（二进制）
        file.write(binary_data)

    # 获取追加内容的起始位置和长度
    # with open(r"C:\Users\claer\Downloads\alert_bg.png", 'rb') as file:
    #     # 定位到文件末尾
    #     file.seek(0, 2)
    #     end_position = file.tell()  # 记录文件末尾位置
    #     # 计算追加内容的长度
    #     content_length = len(binary_data)
    #     # 定位到追加内容之前的位置
    #     file.seek(end_position - content_length)
    #     start_position = file.tell()  # 记录追加内容起始位置
    #     # 打印追加内容的起始位置和长度
    #     print("起始位置:", start_position)
    #     print("长度:", content_length)

    # 移除二进制文件中部分内容
    # with open(r"C:\Users\claer\Downloads\bg.png", 'rb+') as file:
    #     file.seek(start_position)
    #     remaining_data = file.read()
    #
    #     file.seek(start_position)
    #     file.write(remaining_data[content_length:])
    #
    #     file.truncate(file.tell())