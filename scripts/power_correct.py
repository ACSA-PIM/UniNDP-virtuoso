from lxml import etree
import sys
import os
if len(sys.argv) < 2:
    print("Usage: python3 replace.py xxx.xml")
else:
    xml_file_path = sys.argv[1]
    xml_file_path = os.path.abspath(xml_file_path)

parser = etree.XMLParser(remove_comments=False)
tree = etree.parse(xml_file_path, parser)
root = tree.getroot()
dcache_component = root.find(".//component[@id='system.core0.dcache']")
l20_component = root.find(".//component[@id='system.L20']")
l30_component = root.find(".//component[@id='system.L30']")

def update_dcache_from_l20(dcache_component, l20_component):
    """更新 dcache 参数和统计数据从 l20 组件。"""
    if dcache_component is not None and l20_component is not None:
        l2_config = l20_component.find(".//param[@name='L2_config']")
        dcache_config = dcache_component.find(".//param[@name='dcache_config']")
        if l2_config is not None and dcache_config is not None:
            dcache_config.set('value', l2_config.get('value'))

        stats_to_update = ['read_accesses', 'write_accesses', 'read_misses', 'write_misses']
        for stat_name in stats_to_update:
            dcache_stat = dcache_component.find(f".//stat[@name='{stat_name}']")
            l20_stat = l20_component.find(f".//stat[@name='{stat_name}']")
            if dcache_stat is not None and l20_stat is not None:
                dcache_stat.set('value', l20_stat.get('value'))


def update_l30_from_l20(l20_component, l30_component):
    """从 l20 组件更新 l30 组件配置和统计数据。"""
    if l20_component is not None and l30_component is not None:
        l2_config = l20_component.find(".//param[@name='L2_config']")
        l3_config = l30_component.find(".//param[@name='L3_config']")
        if l2_config is not None and l3_config is not None:
            l3_values = l3_config.get('value').split(',')
            l3_values.insert(-1, '0')
            l2_config.set('value', ','.join(l3_values))

        stats_to_update = ['read_accesses', 'write_accesses', 'read_misses', 'write_misses', 'duty_cycle']
        for stat_name in stats_to_update:
            l30_stat = l30_component.find(f".//stat[@name='{stat_name}']")
            l20_stat = l20_component.find(f".//stat[@name='{stat_name}']")
            if l30_stat is not None and l20_stat is not None:
                l30_stat.set('value', l20_stat.get('value'))
    
def update_param_value(param_name, new_value):
    param = root.find(f".//param[@name='{param_name}']")
    if param is not None:
        param.set('value', new_value)

l3_config = root.find(".//param[@name='L3_config']")
if l3_config is not None:
    values = l3_config.get('value').split(',')
    if values[0].strip() == '1024':
        update_dcache_from_l20(dcache_component, l20_component)
        update_param_value('number_of_L2s', '0')
        update_param_value('number_of_L3s', '0')
        update_param_value('Private_L2', '0')
        update_param_value('homogeneous_cores', '1')
        update_param_value('homogeneous_L2s', '1')
        update_param_value('homogeneous_L3s', '1')
        update_param_value('number_cache_levels', '1')
    else:
        update_dcache_from_l20(dcache_component, l20_component)
        update_l30_from_l20(l20_component, l30_component)
        l3_config.set('value', "2097152,64,16, 16, 16, 20,1")
        
else:
    print("L3_config not found")

directory, filename = os.path.split(xml_file_path)
new_filename = "modified_" + filename
new_xml_file_path = os.path.join(directory, new_filename)
tree.write(new_xml_file_path)
