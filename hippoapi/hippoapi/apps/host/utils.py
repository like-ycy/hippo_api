import xlrd

from .models import HostCategory
from .serializers import HostModelSerializers


def read_host_excel_data(host_excel_file_path, default_password=''):
    """
    从excel中读取主机列表信息
    host_excel_file_path: 主机列表的字节流
    default_password: 主机的默认登录密码
    """
    # 打开xls文件
    data = xlrd.open_workbook(file_contents=host_excel_file_path.getvalue())
    # 根据索引获取第一个sheet工作簿
    sheet = data.sheet_by_index(0)
    # 获取当前工作博的数据的总行数
    rows_count = sheet.nrows
    # 查询出数据库现有的所有分类数据[ID，name]
    category_list = HostCategory.objects.values_list('id', 'name')

    # 主机列表
    host_info_list = []

    for row_number in range(1, rows_count):  # 从第二行(下标为1)开始读取xls数据，因为首行是表头信息
        one_row_dict = {}  # 单个主机信息
        # print(sheet.cell(row_number, 0))  # 单元格的数据类型和数据值一起获取，  参数：(行号，列号)
        # print(sheet.cell_type(row_number, 0))  # 获取单元格的数据类型，       参数：(行号，列号)
        # print(sheet.cell_value(row_number, 0)) # 获取单元格的数据值
        category = sheet.cell_value(row_number, 0)

        # 由于拿到的是分类名称，所以我们要找到对应名称的分类id，才能去数据库里面存储
        for category_data in category_list:
            # print(category_data[1],type(category_data[1]),category,type(category))
            if category_data[1].strip() == category.strip():
                one_row_dict['category'] = category_data[0]
                break

        # 注意：数据列要对应
        one_row_dict['name'] = sheet.cell_value(row_number, 1)  # 主机别名
        one_row_dict['ip_addr'] = sheet.cell_value(row_number, 2)  # 主机地址
        one_row_dict['port'] = int(sheet.cell_value(row_number, 3))  # 主机端口号
        one_row_dict['username'] = sheet.cell_value(row_number, 4)  # 登录账户名

        excel_pwd = sheet.cell_value(row_number, 5)
        try:
            pwd = str(excel_pwd)  # 这样强转容易报错，最好捕获一下异常，并记录单元格位置，给用户保存信息时，可以提示用户哪个单元格的数据有问题
        except:
            pwd = default_password

        if not pwd.strip():
            pwd = default_password

        one_row_dict['password'] = pwd
        one_row_dict['description'] = sheet.cell_value(row_number, 6)

        host_info_list.append(one_row_dict)

    # 校验主机数据
    # 将做好的主机信息字典数据通过我们添加主机时的序列化器进行校验
    res_data = {}  # 存放上传成功之后需要返回的主机数据和某些错误信息数据
    serializers_host_res_data = []
    res_error_data = []

    for k, host_data in enumerate(host_info_list):
        # 反序列化校验每一个主机信息
        serailizer = HostModelSerializers(data=host_data)
        if serailizer.is_valid():
            new_host_obj = serailizer.save()
            serializers_host_res_data.append(new_host_obj)
        else:
            # 报错，并且错误信息中应该体验错误的数据位置
            res_error_data.append({'error': f'该{k + 1}行数据有误,其他没有问题的数据，已经添加成功了，请求失败数据改完之后，重新上传这个错误数据，成功的数据不需要上传了'})

    # 再次调用序列化器进行数据的序列化，返回给客户端
    serializer = HostModelSerializers(instance=serializers_host_res_data, many=True)
    res_data['data'] = serializer.data
    res_data['error'] = res_error_data

    return res_data
