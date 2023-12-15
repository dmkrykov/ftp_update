import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from sqlConnect import SqlCache
import pathlib
from listupdate import ListsUpdate


class XmlGenerator:
    con_db = None

    def __init__(self, gui_msg, srv: str, db: str, usr: str, pwd: str):
        self.con_db = SqlCache(gui_msg, srv, db, usr, pwd)

    def generate_stoplist(self, start_date: str = '2022-01-01'):
        stop_list = self.con_db.select_data(f"SELECT [IDtest], [RInStopTests].[RegionCode], [DateFrom], [DateTo] FROM [OrdersFromCACHE].[dbo].[RInStopTests] FULL JOIN [OrdersFromCACHE].[dbo].[Cities] ON RInStopTests.RegionCode = Cities.RegionCode WHERE DateFrom > '{start_date}'")

        xml_doc = ET.Element('stoplist')

        for i in stop_list:
            date_to = lambda x, y: x if x != 'None' else y
            test = ET.SubElement(xml_doc, 'test')
            ET.SubElement(test, 'TestShortName').text = str(i[0])
            ET.SubElement(test, 'DateTo').text = date_to(str(i[3]), 'NULL')
            ET.SubElement(test, 'DateFrom').text = date_to(str(i[2]), 'NULL')
            ET.SubElement(test, 'CityCode').text = str(i[1])

        xmlstr = ET.tostring(xml_doc, encoding='utf8', method='xml')

        dom = md.parseString(xmlstr)
        pretty_xml_as_string = dom.toprettyxml(encoding='UTF-8')
        #переписать формирование пути на os.path
        with open(f"{pathlib.Path(pathlib.Path.cwd(), 'files', 'stop', 'StopList.xml')}", 'w') as st_list:
            st_list.write(pretty_xml_as_string.decode("utf-8"))

    def compare_stoplist(self, lu: ListsUpdate, start_date: str = '2022-01-01'):
        'Сравнение старой и новой версии, составление списка различий'
        # stop_list = self.con_db.select_data(f"SELECT [IDtest], [RInStopTests].[RegionCode], [DateFrom], [DateTo] FROM [OrdersFromCACHE].[dbo].[RInStopTests] FULL JOIN [OrdersFromCACHE].[dbo].[Cities] ON RInStopTests.RegionCode = Cities.RegionCode WHERE DateFrom > '{start_date}'")
        path_old = str(pathlib.Path(pathlib.Path.cwd(), 'files', 'temp', 'stoplist_comp.xml'))
        path_new = str(pathlib.Path(pathlib.Path.cwd(), 'files', 'stop', 'StopList.xml'))
        lu.download_file('/!Template Folder/Lists', 'stoplist_comp.xml', 'StopList.xml')
        #собираем словарь из старого файла
        tree_old = ET.parse(path_old)
        root_old = tree_old.getroot()
        dict_old = {}
        for child in root_old:
            dict_old[child[0].text] = child[2].text
        #собираем словарь из нового файла
        tree_new = ET.parse(path_new)
        root_new = tree_new.getroot()
        dict_new = {}
        for child in root_new:
            dict_new[child[0].text] = child[2].text
        #собираем словарь новых значений
        dict_added = {}
        for element in dict_new:
            if element not in dict_old:
                dict_added[element] = dict_new[element]
        # собираем словарь удаленных значений из нового списка
        dict_remove = {}
        for element in dict_old:
            if element not in dict_new:
                dict_remove[element] = dict_old[element]

        dict_res = {'added': dict_added, 'remove': dict_remove}
        return dict_res

    def parseXML(self, file_name):
        # Parse XML with ElementTree
        tree = ET.parse(file_name)
        print(tree.getroot())
        root = tree.getroot()
        print("tag=%s, attrib=%s" % (root.tag, root.attrib))
        # get the information via the children!
        print("-" * 40)
        print("Iterating using getchildren()")
        print("-" * 40)
        for child in root:
            print(child[0].text, child[2].text)
