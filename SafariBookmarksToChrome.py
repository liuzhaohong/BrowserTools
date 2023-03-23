import json
import plistlib
import xml.etree.ElementTree as ET
import os

"""
------------------------
  Safari书签导入至Chrome  
------------------------
注意事项:
1.执行过程中如果报错: PermissionError: [Errno 1] Operation not permitted: '/Users/用户/Library/Safari/Bookmarks.plist
    解决方式: 可手动从 访达(Finder) 进入并打开此文件再关掉, 然后再次执行python即可成功.
2.此脚本执行成功后，重启Chrome后书签生效；未重启前请勿编辑书签，以免书签被覆盖。
"""

home_path = os.environ['HOME']
chromeBookmarksPath = home_path + '/Library/Application Support/Google/Chrome/Default/Bookmarks'
safariBookmarksPath = home_path + '/Library/Safari/Bookmarks.plist'
safariBookmarksXmlPath = home_path + '/.safari_bookmarks_temp.xml'

# Chrome默认书签json
default_json = '''{"roots":{"bookmark_bar":{"children":[],"name": "书签栏","type": "folder","id": "1"},"other":{"id": "2"},"synced":{"id": "3"}},"version":1}'''
# Chrome书签索引
idx = 3

def readSafariBookmarks():
    # 读取Safari书签文件
    with open(safariBookmarksPath, 'rb') as fp:
        plist = plistlib.load(fp)

    # 将二进制的 plist 格式转换为 XML 格式
    xml_data = plistlib.dumps(plist, fmt=plistlib.FMT_XML)

    # 将 XML 数据保存为一个临时文件
    with open(safariBookmarksXmlPath, 'wb') as fp:
        fp.write(xml_data)

def getChromeBookmarks(xmlPath,root):
    global idx
    # 遍历书签节点，提取名称和URL，并组装Chrome浏览器书签数据
    for bookmark in root.find('array').findall('dict'):
        key = bookmark.find("./key[1]").text
        if key=='Children':
            idx = idx+1
            folderName = bookmark.findtext('string')
            # 排除文件夹:BookmarksBar、com.apple.ReadingList
            if folderName != 'BookmarksBar' and folderName != 'com.apple.ReadingList':
                folder_obj = {"children":[], "type": "folder"}
                folder_obj["name"] = folderName
                folder_obj["id"] = idx
                xmlPath.append(folder_obj)
                path = xmlPath[len(xmlPath)-1]["children"]
            else :
                path = xmlPath
            getChromeBookmarks(path,bookmark)
        elif key=='ReadingListNonSync':
            idx = idx+1
            url = bookmark.findtext('string')
            name = bookmark.find('dict[3]').findtext('string')
            new_obj = {}
            new_obj["name"] = name
            new_obj["url"] = url
            new_obj["type"] = 'url'
            new_obj["id"] = idx
            xmlPath.append(new_obj)

def run():
    readSafariBookmarks()
    chromeBookmark = json.loads(default_json)
    xmlPath = chromeBookmark["roots"]["bookmark_bar"]["children"]
    # 读取 XML 文件
    tree = ET.parse(safariBookmarksXmlPath)
    # 获取根元素
    root = tree.getroot()
    root = root.find('dict')
    getChromeBookmarks(xmlPath,root)
    # chromeBookmarkStr = json.dumps(chromeBookmark,ensure_ascii=False,indent=2)
    # 写入到Chrome浏览器书签文件中
    with open(chromeBookmarksPath, 'w') as write_f:
        json.dump(chromeBookmark,write_f,indent=4,ensure_ascii=False)
    # 删除临时文件
    os.remove(safariBookmarksXmlPath)

if __name__ == '__main__':
    print('*************Safari书签导入至Chrome开始*************')
    run()
    print('*************Safari书签导入至Chrome完成*************')
    print('---------------注意-----------------')
    print('重启Chrome后书签生效 请重启Chrome')
    print('未重启前请勿编辑书签，以免书签被覆盖')
    print('------------------------------------')