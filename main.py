import pandas as pd
import os

def txt_to_excel_single_sheet(output_file):
    all_rows = []  # 创建一个空列表来存储所有数据行

    # 遍历当前目录下的所有txt文件
    for filename in os.listdir(os.curdir):
        if filename.endswith('.txt'):
            file_path = os.path.join(os.curdir, filename)
            file_base_name = os.path.splitext(filename)[0]  # 获取不含扩展名的文件名
            with open(file_path, 'r', encoding='utf-8') as file:
                # 逐行读取文件内容
                for line in file:
                    clean_line = line.strip()  # 清除行尾的换行符和额外的空格
                    if clean_line:  # 确保不添加空行
                        all_rows.append([clean_line, file_base_name])

    # 将数据转换成DataFrame
    df = pd.DataFrame(all_rows, columns=['Content', 'Filename'])

    # 保存DataFrame到Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Merged Data')

    print("所有TXT文件的所有行已合并到一个Excel文件的单一工作表中。")

# 调用函数
output_excel = 'merged_output3.xlsx'  # 您想要保存的Excel文件名称
txt_to_excel_single_sheet(output_excel)
