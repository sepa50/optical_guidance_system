
from pykml import parser
from lxml import etree
from lxml import objectify

with open("myplacesComb2.kml") as f:
    #doc = parser.parse(f)
    root = parser.parse(f).getroot()

n = 0
for i in root.Document.Folder.Placemark:
    i.name = ''.join([i for i in str(i.name) if not i.isdigit()]) + str(n)
    n += 1

for i in root.Document.Folder.Placemark:
    print(i.name)

objectify.deannotate(root, xsi_nil=True)
etree.cleanup_namespaces(root)

outfile = open("myplacesComb2.kml", "wb")
outfile.write(etree.tostring(root, pretty_print=True))

#for i, coordinate_str in enumerate(doc.findall(".//{*}Placemark")):
#    print(i, coordinate_str)
