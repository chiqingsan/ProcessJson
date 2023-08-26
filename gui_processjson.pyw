import tkinter as tk
import json
import math
import os
import re
import sys
import time
import random

from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk


# import shutil


# 列出文件树，并且筛选出JSON文件
def find_json_files(folder_path):
    json_files = []
    # 遍历文件，筛选
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # 要求非文件夹+.json结尾
        if os.path.isfile(file_path) and file_path.endswith('.json'):
            json_files.append(filename)

    return json_files


# 计算两个坐标之间的距离，使用勾股定理
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# 设定路径
# lujing = "C:\\Users\chiqingsan\Desktop\整理\宝箱\稻妻\能直接拿"


# 重命名函数，newname为新名字，newdescription为备注
def rename_json(newname, newdescription):
    fun_start = time.time()
    pr(fr"开始重命名，请耐心等待，本次重命名的名称为{newname}")
    # 筛选json文件， 去掉其他文件和文件夹
    json_files = find_json_files(lujing)

    # 遍历json_files列表，同时获取索引和文件名
    for count, file_path in enumerate(json_files):
        # 以只读模式打开文件，并指定编码为utf-8
        with open(fr"{lujing}\{file_path}", "r", encoding='utf-8') as f:
            # 读取文件内容，并将其解析为Python对象
            json_data = json.load(f)

        # 生成新的文件名，由原来的name字段加上索引加一组成,并格式化数字
        count = f"{count + 1:0{len(str(len(json_files)))}d}"
        json_newname = newname + count
        # 修改json_info中的name字段，加上索引加一
        json_data['name'] = json_newname
        # 如果有填写备注，则写入备注信息
        if not newdescription == "":
            json_data['description'] = newdescription
        # 将json_info转换为字符串，并格式化缩进为4个空格
        json_str = json.dumps(json_data, indent=4)
        # 以写入模式打开文件，并指定编码为utf-8
        pr(fr"开始对：{file_path}进行重命名为：{json_newname}.json")
        with open(fr"{lujing}\{file_path}", "w", encoding='utf-8') as f:
            # 写入json字符串到文件中
            json.dump(json_data, f, indent=4)
        if not str(file_path) == json_newname+".json" :
            try:
                os.rename(fr"{lujing}\{file_path}",fr"{lujing}\{json_newname}.json")
            except FileExistsError as e:
                error_message = str(e)
                pr(error_message)
                pr(f"\n\n\n\n当前输入名称错误，请更换重命名名称。\n现已退出！！！\n\n\n\n")
                break

    fun_end = time.time()
    pr(fr"本次重命名一共花费{round(fun_end - fun_start, 2)}秒。一共重命名{len(json_files)}个Json文件"
       f"\n------------------------------------------")


# 筛选函数，去掉低于阈值距离的点位。juli为设定的阈值
def del_repeat(juli):
    fun_start = time.time()
    pr(fr"开始使用贪婪算法去重，请耐心等待，本次去重的筛选距离为{juli}米")
    # 筛选json文件， 去掉其他文件和文件夹
    json_files = find_json_files(lujing)

    # 定义一个空列表，用于存储坐标和name
    jsonxyn = []
    # 遍历path列表，获取每个文件名
    for file_path in json_files:
        # 拼接文件路径
        jsonpath = os.path.join(lujing, file_path)
        # 以只读模式打开文件，并指定编码为utf-8
        with open(jsonpath, "r", encoding="utf-8") as f:
            # 读取文件内容，并将其解析为Python对象
            json_data = json.load(f)
        # 获取json_data中的position和name字段，并组成一个列表
        jsonxyn_arr = [json_data["position"][0], json_data["position"][2], str(json_data["name"])]
        # 如果内外名称不匹配，这进行处理。
        if not file_path == (str(json_data['name']) + ".json"):
            pr(fr"检测到格式不规范json文件:{file_path}，开始纠正处理。")
            with open(fr"{lujing}\{json_data['name']}.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            # 移除不匹配的文件
            os.remove(fr"{lujing}\{file_path}")
        # 将列表添加到jsonxyn中
        jsonxyn.append(jsonxyn_arr)

    def greedy_algorithm(coordinates):
        # 根据x和y轴坐标排序
        sorted_coordinates = sorted(coordinates, key=lambda coord: (coord[0], coord[1]))
        result = []
        removed_coordinates = []

        while sorted_coordinates:
            # 选择当前列表中最近的坐标作为结果
            current_coord = sorted_coordinates.pop(0)
            result.append(current_coord)

            # 收集距离超过设定距离juli米的坐标
            nearby_coordinates = [coord for coord in sorted_coordinates if distance(coord, current_coord) <= int(juli)]
            removed_coordinates.extend(nearby_coordinates)

            # 从sorted_coordinates中移除已添加到removed_coordinates的坐标
            for coord in nearby_coordinates:
                sorted_coordinates.remove(coord)

            if len(nearby_coordinates) > 0:
                pr(f"当前正在处理的坐标:{current_coord[2]}.json")
                pr(f"准备移除的坐标:{[item[2] + '.json' for item in nearby_coordinates]}")
                for f in nearby_coordinates:
                    pr(f"发现{current_coord[2]}.json距离{f[2]}.json为{round(distance(current_coord, f), 3)}米，已将{f[2]}.json移入筛选的重复文件")
            # 从列表中移除与当前坐标距离小于等于40米的其他坐标
            sorted_coordinates = [coord for coord in sorted_coordinates if distance(coord, current_coord) > 40]

        return result, removed_coordinates

    jsonretain, jsondel = greedy_algorithm(jsonxyn)

    if len(jsondel) > 0:
        if not os.path.exists(fr"{lujing}\筛选的重复文件"):
            os.mkdir(fr"{lujing}\筛选的重复文件")
        for file in jsondel:
            os.replace(fr"{lujing}\{file[2]}.json", fr"{lujing}\筛选的重复文件\{file[2]}.json")
    fun_end = time.time()
    pr(fr"本次使用贪婪算法去重一共花费{round(fun_end - fun_start, 2)}秒。筛选出{len(jsondel)}个重复json文件"
       f"\n------------------------------------------")


# 排列相近的坐标
def arrange_coordinates(newname_a):
    # 开始计时
    fun_start = time.time()
    # 设置新名称的前缀
    newname_a = newname_a + "xj_"

    # 查找目标文件夹中的所有 JSON 文件
    json_files = find_json_files(lujing)

    # 创建一个空列表来存储所有 JSON 文件中的坐标信息
    jsonxyn = []

    for file_path in json_files:
        # 拼接文件路径
        jsonpath = os.path.join(lujing, file_path)

        # 以只读模式打开文件，并指定编码为 utf-8
        with open(jsonpath, "r", encoding="utf-8") as f:
            # 读取文件内容，并将其解析为 Python 对象
            json_data = json.load(f)

        # 获取 JSON 数据中的 position 和 name 字段，并组成一个列表
        jsonxyn_arr = [json_data["position"][0], json_data["position"][2], json_data["name"]]
        # 如果内外名称不匹配，这进行处理。
        if not file_path == (str(json_data['name']) + ".json"):
            pr(fr"检测到格式不规范json文件:{file_path}，开始纠正处理。")
            with open(fr"{lujing}\{json_data['name']}.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            # 移除不匹配的文件
            os.remove(fr"{lujing}\{file_path}")
        # 将列表添加到 jsonxyn 中
        jsonxyn.append(jsonxyn_arr)

    def rearrange_coordinates(coordinates):
        # 将坐标列表按照欧几里得距离进行排列
        sorted_coordinates = [coordinates[0]]  # 先将第一个坐标放入排列后的列表中

        # 从第二个坐标开始，依次找到与已排列坐标列表中最后一个坐标距离最近的坐标
        pr(fr"准备开始寻找两个相近的坐标")
        for coord in coordinates[1:]:
            min_distance = float('inf')
            min_distance_index = None

            for i, sorted_coord in enumerate(sorted_coordinates):
                distance_mi = distance(coord, sorted_coord)
                if distance_mi < min_distance:
                    min_distance = distance_mi
                    min_distance_index = i

            # 将当前坐标插入到已排列坐标列表中最近的坐标之后
            sorted_coordinates.insert(min_distance_index + 1, coord)

        return sorted_coordinates

    # 对坐标进行重新排列
    rearranged_coordinates = rearrange_coordinates(jsonxyn)

    # 输出相近坐标的距离
    for i, json_xy in enumerate(rearranged_coordinates):
        # 检查是否为列表中的最后一个元素（排除最后一个元素）
        if i == len(rearranged_coordinates) - 1:
            continue  # 跳过循环的剩余部分，继续下一次循环

        # 调用 distance 函数计算当前点 json_xy 与下一个点的欧氏距离
        xy_juli = distance(json_xy, rearranged_coordinates[i + 1])

        # 使用 pr() 函数打印当前点与下一个点之间的距离信息
        pr(f"{json_xy[2]} 与 {rearranged_coordinates[i + 1][2]} 相聚 {round(xy_juli, 2)} 米")

    # 输出重新排列后的结果，并开始重命名
    pr("开始对相近的json文件进行重命名")
    for i, coord in enumerate(rearranged_coordinates):
        # 使用新名称前缀和序号创建新的名称
        i = f"{i + 1:0{len(str(len(rearranged_coordinates)))}d}"
        newname = newname_a + i

        # 打开 JSON 文件，并更新其中的 name 字段
        with open(fr"{lujing}\{coord[2]}.json", "r", encoding="utf-8") as fr:
            json_data = json.load(fr)
        # print(fr"开始对：{json_data['name']}.json进行重命名为：{newname}.json")
        json_data["name"] = newname

        # 将更新后的 JSON 数据写入新的 JSON 文件中
        with open(fr"{lujing}\{newname}.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        # 删除原来的 JSON 文件
        os.remove(fr"{lujing}\{coord[2]}.json")

    # 结束计时
    fun_end = time.time()
    # 计算花费时间
    pr(fr"本次相近排列一共花费{round(fun_end - fun_start, 2)}秒，共操作{len(rearranged_coordinates)}个json文件"
       f"\n------------------------------------------")


# 实现打乱
def dislocate():
    fun_start = time.time()
    # 查找目标文件夹中的所有 JSON 文件
    json_files = find_json_files(lujing)

    # 遍历json_files列表，同时获取索引和文件名
    for file_path in json_files:
        # 打印文件名
        # print(file_path)

        # 以只读模式打开文件，并指定编码为utf-8
        with open(fr"{lujing}\{file_path}", "r", encoding="utf-8") as f:
            # 读取文件内容，并将其解析为Python对象
            json_info = json.load(f)
        # 生成新的文件名，由原来的name字段加上索引加一组成
        json_newname = random.randint(10000000000000, 100000000000000)
        # 修改json_info中的name字段，加上索引加一
        json_info['name'] = json_newname
        # 以写入模式打开文件，并指定编码为utf-8
        pr(fr"开始对：{file_path}进行重命名为：{json_newname}.json")
        with open(fr"{lujing}\{json_newname}.json", "w", encoding='utf-8') as f:
            # 写入json字符串到文件中
            json.dump(json_info, f, ensure_ascii=False, indent=4)
        # 写入完毕后，移除旧的文件。
        os.remove(fr"{lujing}\{file_path}")
    fun_end = time.time()
    pr(fr"本次打乱一共花费{round(fun_end - fun_start, 2)}秒。一共打乱{len(json_files)}个json文件"
       f"\n------------------------------------------")


# 校验函数
def verify_json():
    fun_start = time.time()
    num = 0
    # 查找目标文件夹中的所有 JSON 文件
    for root, dirs, files in os.walk(lujing):
        # print(f"当前文件夹：{root}")
        for file in files:
            # print(os.path.join(root, file))
            if file.endswith('.json'):
                num += 1
                if os.path.getsize(fr"{os.path.join(root, file)}") == 0:
                    if not "疑似错误的json" in root:
                        pr(fr"发现错误空文件：{file},已移入文件夹")
                        if not os.path.exists(fr"{root}\疑似错误的json"):
                            os.mkdir(fr"{root}\疑似错误的json")
                        os.rename(fr"{os.path.join(root, file)}", fr"{root}\疑似错误的json\{file}")
                    continue

                try:
                    with open(fr"{os.path.join(root, file)}", "r", encoding='utf-8') as f:
                        json_data = json.load(f)
                except json.JSONDecodeError:
                    pr(fr"发现错误格式的json文件：{file},已移入文件夹")
                    if not "疑似错误的json" in root:
                        if not os.path.exists(fr"{root}\疑似错误的json"):
                            os.mkdir(fr"{root}\疑似错误的json")
                        os.rename(fr"{os.path.join(root, file)}", fr"{root}\疑似错误的json\{file}")
                    continue

                if not hasattr(json_data, "name") and hasattr(json_data, "position"):
                    pr(fr"发现没有name或position属性的json文件：{file},已移入文件夹")
                    if not "疑似错误的json" in root:
                        if not os.path.exists(fr"{root}\疑似错误的json"):
                            os.mkdir(fr"{root}\疑似错误的json")
                        os.rename(fr"{os.path.join(root, file)}", fr"{root}\疑似错误的json\{file}")
                    continue

                if not file == (str(json_data['name']) + ".json"):
                    pr(fr"发现内外名称不一致的json：{file}，已移入文件夹")
                    if not "疑似错误的json" in root:
                        if not os.path.exists(fr"{root}\疑似错误的json"):
                            os.mkdir(fr"{root}\疑似错误的json")
                        os.rename(fr"{os.path.join(root, file)}", fr"{root}\疑似错误的json\{file}")
                    continue

                for element in (json_data["position"]):
                    pattern = r'^[-+]?\d+(\.\d+)?$'
                    if not re.match(pattern, str(element)):
                        pr(fr"发现坐标错误的json：{file}，已移入文件夹")
                        if not "疑似错误的json" in root:
                            if not os.path.exists(fr"{root}\疑似错误的json"):
                                os.mkdir(fr"{lujing}\疑似错误的json")
                            os.rename(fr"{os.path.join(root, file)}", fr"{lujing}\疑似错误的json\{file}")
                        continue

    fun_end = time.time()
    pr(fr"本次校验一共花费{round(fun_end - fun_start, 2)}秒。一共校验{num}个json文件"
       f"\n------------------------------------------")


# 转换kp使用的json坐标函数
def transform_json():
    fun_start = time.time()
    num = 0
    pr(f"开始转换文件夹内的Json文件...")
    # 获取目标文件夹中的 JSON 文件列表。
    for root, dirs, files in os.walk(lujing):
        # print(f"当前文件夹：{root}")
        for file in files:
            if file.endswith('.json'):
                try:
                    with open(os.path.join(root, file), encoding='utf-8', mode="r") as f:
                        # 读取文件内容，并将其解析为 Python 对象（字典、列表等）。
                        json_data = json.load(f)
                except json.JSONDecodeError:
                    if not "疑似错误的json" in root:
                        pr(f"检查到当前点位解析出现问题，已将当前json文件移入疑似错误文件夹...")
                        if not os.path.exists(fr"{root}\疑似错误的json"):
                            os.mkdir(fr"{root}\疑似错误的json")
                        os.rename(fr"{os.path.join(root, file)}", fr"{root}\疑似错误的json\{file}")
                    continue
                # 检查 JSON 数据中是否存在 "checked" 键，并将其删除。
                if "checked" in json_data:
                    num = num + 1
                    del json_data["checked"]
                    pr(f"发现Json文件{file}中出现checked属性，会导致Korepi不能兼容读取，开始转换...")

                json_data_format = {
                    "description": json_data["description"],
                    "name": json_data["name"],
                    "position": json_data["position"]
                }
                # 以写模式打开相同的文件，并指定编码为utf-8。
                with open(os.path.join(root, file), "w", encoding='utf-8') as f:
                    # 将修改后的 JSON 数据重新写入文件，并使用 4 个空格进行缩进。
                    json.dump(json_data_format, f, ensure_ascii=False, indent=4)

    fun_end = time.time()
    # 打印转换所花费的时间。
    pr(fr"本次转换一共花费{round(fun_end - fun_start, 2)}秒。有{num}个json文件需要转换"
       f"\n------------------------------------------")


def choose_directory():
    # 弹出目录选择器对话框
    directory = filedialog.askdirectory()

    # 如果用户选择了目录，更新文本框中的内容
    if directory:
        selected_directory.set(directory)

        # 更新文本内容的时候为全局变量lujing 赋值
        global lujing
        lujing = directory

        # 更新json数据预览
        json_files = find_json_files(directory)
        # 读取第一个json文件，并且解析赋值

        if not len(json_files) == 0:
            with open(f"{lujing}\{json_files[0]}", "r", encoding="utf-8") as f:
                # 读取文件内容，并将其解析为Python对象
                global preview_json
                preview_json = json.load(f)
                preview_text.delete(1.0, tk.END)
                preview_text.insert("insert", json.dumps(preview_json, indent=4))
        else:
            preview_text.delete(1.0, tk.END)
            preview_text.insert("1.0",
                                "当前文件夹内无json文件\n\n校验与转换Json支持遍历文件夹下所有json文件\n\n请谨慎使用！！！")


def show_message():
    messagebox.showinfo("使用说明", "说明：本工具用于处理json文件，暂不支持递归文件夹进行json文件修改，使用前请确保输入的路径下是json文件。"
                                    "\n使用说明："
                                    "\n    重命名：对文件夹内的json文件进行内部和外部的重命名,在输入框中输入你需要重命名的名称后，点击重命名按钮使用"
                                    "\n    备注：对文件夹内的json文件进行备注，如不需要请留空"
                                    "\n    筛选：对文件夹内的json文件进行贪婪算法的筛选，尽可能多的囊括设定范围内的坐标点，去除多余的坐标。在输入框中输入你需要筛选的距离（米）后，点击筛选按钮使用"
                                    "\n    相近排列坐标：对文件夹内的json文件进行最近距离的排序，简单来说就是在传送的时候，优先传送最近的坐标。在输入框中输入你需要重命名的名称后，点击相近排序按钮使用"
                                    "\n    打乱：对文件夹内的json文件进行打乱排序操作"
                                    "\n    校验：对文件夹内的所有json文件进行校验，检测其格式是否错误。"
                                    "\n    转换Json：对文件夹内所有的json进行转换，将其转化为Korepi和Akebi都可以使用的格式"
                                    "\n    Json交流群：1056308869")


def rename_json_b():
    if not entry_newname.get() == "":
        newname = entry_newname.get()
        newdescription = entry_newdescription.get()
        rename_json(newname, newdescription)
    else:
        messagebox.showinfo("提醒", "请输入重命名的名称后使用（不要输入中文）")


def del_repeat_b():
    if not entry_juli.get() == "":
        if entry_juli.get().isnumeric():
            juli = entry_juli.get()
            del_repeat(float(juli))
        else:
            messagebox.showinfo("提醒", "请输入数字，不要输入其他字符")
    else:
        messagebox.showinfo("提醒", "请输入筛选的距离后再使用，单位：米")


def arrange_coordinates_b():
    if not entry_newname_a.get() == "":
        newname_a = entry_newname_a.get()
        arrange_coordinates(newname_a)
    else:
        messagebox.showinfo("提醒", "请输入相近排序的名称后使用（不要输入中文）")


# 从标准输出中读取内容，并写入Text部件
def pr(str_pr):
    # 设定text框为可编辑状态
    output_text["state"] = "normal"
    output_text.insert(tk.END, str_pr + "\n")
    output_text.see(tk.END)

    # 设置行间距
    output_text.tag_configure("line_spacing", spacing1=6)
    # 将行间距样式应用到文本的所有行
    for line in range(1, int(output_text.index("end-1c").split(".")[0]) + 1):
        output_text.tag_add("line_spacing", f"{line}.0", f"{line}.end")
    # 强制更新 GUI
    output_text.update()
    # 设定text框为不可编辑状态
    output_text["state"] = "disabled"


# 输入框验证函数
# 重命名检测函数
def check_cmm(P):
    # if not P == "":
    preview_json["name"] = P
    preview_text.delete(1.0, tk.END)
    preview_text.insert("end", json.dumps(preview_json, indent=4))
    return True


# else:
#     # messagebox.showinfo("提醒", "请输入重命名的名称后使用")
#     return False


# 备注检测函数
def check_bz(P):
    # if not entry_newdescription.get() == "":
    preview_json["description"] = P
    preview_text.delete(1.0, tk.END)
    preview_text.insert("end", json.dumps(preview_json, indent=4))
    return True


# else:
#     # messagebox.showinfo("提醒", "请输入重命名的名称后使用")
#     return False


# -------------------------------------------------------
# 设置变量
lujing = None
preview_json = None

# 创建主应用窗口
root = tk.Tk()
root.title("Process Json Gui  by chiqingsan V1.4.4   编译于：2023年8月22日 12:05:23")

# 设置gui的宽高
root.geometry('600x400+600+300')
# 固定窗口
root.resizable(0, 0)
root.config(background="#F8F1F2")

# 创建一个 ttk.Style 实例
style = ttk.Style()

# 定义按钮样式
style.configure("Custom.TButton",
                foreground="#cd5e3c",  # 按钮前景色
                background="#F0F0F0",  # 按钮背景色
                font=("Helvetica", 10),  # 按钮字体样式
                padding=3  # 按钮文本与边框的间距
                )
style.configure("My.TButton",
                foreground="#393f4c",  # 按钮前景色
                background="#F8F1F2",  # 按钮背景色
                font=("Helvetica", 10),  # 按钮字体样式
                padding=3,  # 按钮文本与边框的间距
                )

# 定义输入框样式
style.configure("My.TEntry",
                foreground="black",  # 文本颜色
                background="#F8F1F2",  # 背景颜色
                font=("Helvetica", 6),  # 字体样式
                padding=2,  # 文本与边框的间距
                )

# 设置布局区块

# 设定目录框架
Frame_mulu = tk.Frame(root, height=50)
Frame_mulu.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=6)

# 设定打印信息框架
Frame_print = tk.Frame(root, bg="#F8F1F2")
Frame_print.grid(row=1, column=1, rowspan=2, sticky="w")

# 设定中央主体信息框架
Frame_content = tk.Frame(root, bg="#F8F1F2")
Frame_content.grid(row=1, column=0, padx=10, pady=4, sticky="w")
#   在设定主体框架中添加输入信息框架
Frame_content_input = tk.Frame(Frame_content, bg="#F8F1F2")
Frame_content_input.grid(row=0, column=0, sticky="n")
#   在设定主体框架中添加附加按钮框架
Frame_content_additional = tk.Frame(Frame_content, bg="#F8F1F2")
Frame_content_additional.grid(row=1, column=0, sticky="s")
#   设定预览信息框架
Frame_preview = tk.Frame(root, bg="#F8F1F2")
Frame_preview.grid(row=2, column=0, sticky="n")

# 用于显示所选目录的文本框

button_mulu = ttk.Button(Frame_mulu, text="选 择 目 录", command=choose_directory, width=10, style="My.TButton")
button_mulu.grid(row=0, column=0)

selected_directory = tk.StringVar()
selected_directory.set("请选择一个文件夹目录")
directory_label = tk.Label(Frame_mulu, textvariable=selected_directory, width=56, bg="#F8F1F2")
directory_label.grid(row=0, column=1)

# 创建一个使用说明按钮
button = ttk.Button(Frame_mulu, text="使 用 说 明", command=show_message, style="Custom.TButton")
button.grid(row=0, column=2)

# 将验证函数 check_cmm 注册到主窗口对象
validate_cmm = root.register(check_cmm)

# 将验证函数 check_bz 注册到主窗口对象
validate_bz = root.register(check_bz)

# 创建输入框 entry_newname，并设置 validate 和 validatecommand 属性
entry_newname = ttk.Entry(Frame_content_input, validate="key", validatecommand=(validate_cmm, '%P'), style="My.TEntry")
entry_newname.grid(row=2, column=1, padx=4)

# 创建输入框 entry_newdescription，并设置 validate 和 validatecommand 属性
entry_newdescription = ttk.Entry(Frame_content_input, validate="key", validatecommand=(validate_bz, '%P'),
                                 style="My.TEntry")
entry_newdescription.grid(row=3, column=1, padx=4)

text_newdescription = tk.Label(Frame_content_input, text="备    注", bg="#F8F1F2")
text_newdescription.grid(row=3, column=0)
button = ttk.Button(Frame_content_input, text="重 命 名", command=rename_json_b, width=8, style="My.TButton")
button.grid(row=2, column=0)

# 创建一个筛选按钮
entry_juli = ttk.Entry(Frame_content_input, style="My.TEntry")
entry_juli.grid(row=5, column=1, padx=4)
button = ttk.Button(Frame_content_input, text="筛    选", command=del_repeat_b, width=8, style="My.TButton")
button.grid(row=5, column=0)

# 创建一个相近排序按钮
entry_newname_a = ttk.Entry(Frame_content_input, style="My.TEntry")
entry_newname_a.grid(row=6, column=1, padx=4)
button = ttk.Button(Frame_content_input, text="相近排序", command=arrange_coordinates_b, width=8, style="My.TButton")
button.grid(row=6, column=0)

# 创建一个打乱按钮
button = ttk.Button(Frame_content_additional, text="打    乱", command=dislocate, width=8, style="My.TButton")
button.grid(row=0, column=0, padx=4)

# 创建一个校验按钮
button = ttk.Button(Frame_content_additional, text="校    验", command=verify_json, width=8, style="My.TButton")
button.grid(row=0, column=1, padx=4)

# 创建一个转换按钮
button = ttk.Button(Frame_content_additional, text="转换Json", command=transform_json, width=8, style="My.TButton")
button.grid(row=0, column=2, padx=4)

# 创建Text部件，用于显示print输出的内容
output_info = tk.Label(Frame_print, text="Json日志记录区：", bg="#F8F1F2")
output_info.grid(row=0, column=0, sticky="w")
output_text = tk.Text(Frame_print, wrap=tk.WORD, width=42, height=23, padx=8, pady=8, fg="#393f4c",
                      bg="#FFFAFA",
                      state="disabled",
                      font=("黑体", 10)
                      )
output_text.grid(row=1, column=0)

# 创建Text部件，用于预览文件夹中json的内容
preview_info = tk.Label(Frame_preview, text="Json内容修改预览区：", anchor="w", bg="#F8F1F2")
preview_info.grid(row=0, column=0, sticky="w")
preview_text = tk.Text(Frame_preview, wrap="char", width=28, height=10, padx=12, pady=16, fg="#393f4c", bg="#FFFAFA",
                       font=("黑体", 10))
preview_text.grid(row=1, column=0)

# 启动主事件循环
root.mainloop()
