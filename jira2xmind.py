#!/usr/bin/env python2
'''
Created on Jul 16, 2015

@author: cpriscal
'''
import argparse
from xml.etree.ElementTree import ElementTree
import xmind
from xmind.core.topic import TopicElement

def add_item(items, key, topic):
    item = items[key]
    t = TopicElement()
    t.setTitle("%s %s" % (key, item['summary']))
    t.setURLHyperlink(item['url'])
    if item['status'] == 'Resolved':
        t.addMarker('task-done')
    elif item['status'] == 'In Progress':
        t.addMarker('task-start')
    description = item['description']
    if description:
        t.setPlainNotes(description.encode('ascii', 'ignore'))
    topic.addSubTopic(t)
    for child in item['children']:
        try:
            add_item(items, child, t)
        except KeyError:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a list of JIRA items in the XML format into an XMind document.')
    parser.add_argument('source', help='xml source file created from a Jira export')
    parser.add_argument('destination', help='XMind destination file')
    args = parser.parse_args()

    tree = ElementTree()
    tree.parse(args.source)
    items = {}
    root_items = []
    # Create all the items
    for i in tree.iter('item'):
        key = i.find('key').text
        summary = i.find('summary').text
        status = i.find('status').text
        description = i.find('description').text
        url = i.find('link').text
        children = [k.text for k in i.findall("issuelinks/issuelinktype[@id='10000']/inwardlinks/issuelink/issuekey")]
        parents = [k.text for k in i.findall("issuelinks/issuelinktype[@id='10000']/outwardlinks/issuelink/issuekey")]
        items[key] = {
            'summary': summary,
            'status': status,
            'url': url,
            'description': description,
            'children': children,
            'parents': parents
        }
        if len(parents) == 0:
            root_items.append(key)
    # Display the Tree
    w = xmind.load('new.xmind')
    s1 = w.getPrimarySheet()
    s1.setTitle("SPHERES Jira tickets")
    r1 = s1.getRootTopic()
    r1.setTitle("SPHERES")
    for k in root_items:
        add_item(items, k, r1)
    xmind.save(w, args.destination)
