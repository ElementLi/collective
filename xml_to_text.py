from xml.etree import ElementTree as ET

xml = ET.parse('4_belt_12_items.xml')
root_element = xml.getroot()

ann = open('ann_item.txt', 'a')

for child in root_element:
    if child.tag == 'image':
        name = child.get('name')
        print(name)
        ann.write(name + ' ')
        for data in child:
            label = data.get('label')
            xtl = data.get('xtl')
            ytl = data.get('ytl')
            xbr = data.get('xbr')
            ybr = data.get('ybr')
            ann.write(xtl + ',' + ytl + ',' + xbr + ',' + ybr + ',' + label + ' ')
            print(label, xtl, ytl, xbr, ybr)
        ann.write('\n')