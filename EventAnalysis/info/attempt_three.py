# coding: utf-8

import sys
import re
import Momi
import urllib2
import time
import xlwt
import json
import xlrd
from yqnew.settings import *

reload(sys)
sys.setdefaultencoding('utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:35.0) Gecko/20100101 Firefox/35.0'}


class Info(object):  # 根据用户名得到用户基本资料的类

    def __init__(self):  # 初始化
        # self.user = Momi.MoblieWeibo()
        # self.user.login('oktong668an@163.com', 'pachong13')
        self.areas = {
            '其他': 0, '北京': 0, '天津': 0, '上海': 0,
            '重庆': 0, '河北': 0, '山西': 0, '辽宁': 0,
            '吉林': 0, '江苏': 0, '浙江': 0, '广西': 0,
            '安徽': 0, '福建': 0, '江西': 0, '山东': 0,
            '河南': 0, '湖北': 0, '湖南': 0, '广东': 0,
            '海南': 0, '四川': 0, '贵州': 0, '云南': 0,
            '陕西': 0, '甘肃': 0, '青海': 0, '台湾': 0,
            '西藏': 0, '宁夏': 0, '新疆': 0, '澳门': 0,
            '香港': 0, '黑龙江': 0, '内蒙古': 0, '海外': 0
        }
        self.sex = {
            '男': 0,
            '女': 0,
            '其他': 0
        }
        self.age = {
            '1995-': 0,
            '1990-1994': 0,
            '1980-1989': 0,
            '1970-1979': 0,
            '-1970': 0,
            '其他': 0
        }

    def get_page(self, url):
        """
        获取某网页的源代码
        :param url: 某网页的链接
        :return: 某网页的源代码
        """
        try:
            request = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(request)
            page = response.read()
            return page
        except urllib2.URLError as e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
            return None

    def get_firstone_infotable(self, search_page):
        """
        获取搜索结果页面显示的第一个用户信息表格
        :param search_page: 搜索结果页面源代码
        :return: 用户信息表格
        """
        pattern = re.compile('<table>(.*?)</table>')
        firstone_info_table = re.search(pattern, search_page).group()
        return firstone_info_table

    def get_no_attention_uid(self, someone_table):
        """
        获取未关注的用户id
        :param someone_table:用户信息表格
        :return: 用户id
        """
        uid_pattern = re.compile('uid=(.*?)&amp')
        uid = re.search(uid_pattern, someone_table).group(1)
        return uid

    def get_attention_uid(self, someone_table):
        """
        获取已关注的用户id
        :param someone_table:用户信息表格
        :return: 用户id
        """
        index_pattern = re.compile('<td valign="top"><a href="(.*?)">')
        index_part = re.search(index_pattern, someone_table).group(1)
        index_url = 'http://weibo.cn%s' % index_part  # 用户首页链接
        index_page = self.get_page(index_url)
        uid_pattern = re.compile('&nbsp;<a href="/(.*?)/info">资料')
        uid = re.search(uid_pattern, index_page).group(1)
        return uid

    def get_user_info(self, uid):
        """
        获取用户基本信息
        :param uid: 用户id
        :return: 用户基本信息
        """
        user_info_url = 'http://weibo.cn/%s/info' % uid
        user_info_page = self.get_page(user_info_url)
        sex_pattern = re.compile('性别:(.*?)<br/>')
        area_pattern = re.compile('地区:(.*?)<br/>')
        birth_pattern = re.compile('生日:(\d*?)-.*?<br/>')
        sex = re.search(sex_pattern, user_info_page)
        area = re.search(area_pattern, user_info_page)
        birth = re.search(birth_pattern, user_info_page)
        if sex:
            sex = sex.group(1)
        if area:
            area = area.group(1)
        if birth:
            birth = birth.group(1)
            if int(birth) != 0001:  # 将年龄为微博默认设置的用户过滤
                info = {'性别': sex, '地区': area, '年龄': birth}
                return info
        info = {'性别': sex, '地区': area, '年龄': None}
        return info

    def show_user_info(self,path):  # 展示用户信息
        f = open(os.path.join(path,'info.txt'), 'w')
        f.write('##' + '\n' + '性别' + '\n')
        for each in self.sex:
            f.write(each + ':' + str(self.sex[each]) + '\n')
        f.write('##' + '\n' + '年龄' + '\n')
        for each in self.age:
            f.write(each + ':' + str(self.age[each]) + '\n')
        f.write('##' + '\n' + '地区' + '\n')
        for each in self.areas:
            f.write(each + ':' + str(self.areas[each]) + '\n')
        f.close()

    def collect_info(self, user_info):
        """
        收集用户基本信息
        :param user_info: 用户基本信息
        """
        if user_info['性别']:
            for each in self.sex:
                if each in user_info['性别']:
                    self.sex[each] += 1
        else:
            self.sex['其他'] += 1
        if user_info['地区']:
            for each in self.areas:
                if each in user_info['地区']:
                    self.areas[each] += 1
        else:
            self.areas['其他'] += 1
        if user_info['年龄']:
            if int(user_info['年龄']) >= 1995:
                self.age['1995-'] += 1
            elif int(user_info['年龄']) >= 1990:
                self.age['1990-1994'] += 1
            elif int(user_info['年龄']) >= 1980:
                self.age['1980-1989'] += 1
            elif int(user_info['年龄']) >= 1970:
                self.age['1970-1979'] += 1
            else:
                self.age['-1970'] += 1
        else:
            self.age['其他'] += 1

    def main_user_info(self, username):
        search_url = 'http://weibo.cn/find/user?keyword=%s&suser=1' % username  # 搜索结果页面链接
        search_page = self.get_page(search_url)
        firstone_table = self.get_firstone_infotable(search_page)
        if '已关注' in firstone_table:
            user_id = self.get_attention_uid(firstone_table)
        else:
            user_id = self.get_no_attention_uid(firstone_table)
        user_info = self.get_user_info(user_id)
        self.collect_info(user_info)

    def write_xls(self, path):
        """
        把地区信息写入xls文件
        :param path: 生成xls的上级目录
        :return: xls文件路径
        """
        xls = xlwt.Workbook('utf-8')
        # table = xls.add_sheet('age_distribution',True)
        # sorted_dict = sorted(self.age.iteritems())  # [(key,value),()]
        # for row in range(0,len(self.age)):
        #     table.write(row,0,sorted_dict[row][0])
        #     table.write(row,1,sorted_dict[row][1])
        table = xls.add_sheet('map', True)
        sorted_dict = sorted(self.areas.iteritems())  # [(key,value),()]
        for row in range(0, len(self.areas)):
            table.write(row, 0, sorted_dict[row][0])
            table.write(row, 1, sorted_dict[row][1])
        xls_file = os.path.join(path, 'map.xls')
        xls.save(xls_file)
        return xls_file

    def dump_json(self, xls_file, path):
        """
        生成age distribution ,map的json文件
        :param xls_file: xls文件的路径
        :return:
        """
        event_title = path.split('/')[-2]
        folder_path = os.path.join(JSON_DIR,event_title)
        if os.path.exists(folder_path):
            pass
        else:
            os.mkdir(folder_path)
        age = sorted(self.age.values())
        age_dict = {}
        age_dict.setdefault('ageDistribution', age)
        age_json = json.dumps(age_dict, separators=(',', ':'))
        age_file = open(os.path.join(JSON_DIR, event_title, 'age_distribution.json'), 'w+')
        age_file.writelines(age_json)
        age_file.close()

        map_list = []
        xls = xlrd.open_workbook(xls_file)
        table = xls.sheet_by_index(0)
        name_list = table.col_values(0, 0)
        value_list = table.col_values(1, 0)
        for i in range(0, len(name_list)):
            map_dict = {'name': name_list[i], 'value': value_list[i]}
            map_list.append(map_dict)
        data_dict = {'map': map_list}
        map_json = json.dumps(data_dict, separators=(',', ':'))
        map_file = open(os.path.join(JSON_DIR, event_title, 'map.json'), 'w+')
        map_file.writelines(map_json)
        map_file.close()
        print 'finish writing age and map json'
        return True


def main_info(path):
    user_list = []
    user = Info()
    user_file = open(os.path.join(path, 'participants.txt'), 'r')
    participants = user_file.readlines()

    for each in participants:
        user_list.append(each.strip())

    for username in user_list:
        start = time.time()
        try:
            user.main_user_info(username)
        except:
            continue
        print time.time() - start

    user.show_user_info(path)
    xls_file = user.write_xls(path)
    user.dump_json(xls_file, path)

# if __name__ == '__main__':
#     user = Info()
#     user_list = ['今日头条', '央视新闻', '网易新闻', '搜狐新闻', '凤凰新闻']
#     for username in user_list:
#         print username
#         start = time.time()
#         user.main(username)
#         print time.time() - start
#     # user.show_user_info()
#     user.write_xls()
#     user.dump_json()
