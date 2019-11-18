#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re

# Quick and dirty script to gather all the tutorial's parts timing into one big JSON file
output = []
folder = "../website/src/aprender"
for f in os.listdir(folder):
    if (f[-5:] == ".html" and f != "index.html"):
        slug = f[:-5]
        print (slug)
        with open(os.path.join(folder, f)) as in_file:
            file_content = in_file.read()
            r = re.search("<title>(.*) - (.*)</title>", file_content)
            if not r:
                print (file_content[:200])
                r = re.search("<title>(.*)</title>", file_content)
                author = None
            else:
                author = r.group(2)
            title = r.group(1)

            begin = file_content.find("var videos = [")
            end = file_content.find("</script>", begin)
            interesting_part = file_content[begin:end]
            # print(interesting_part)
            full_tuto_pos = interesting_part.find("var videosFullTutorial = [")
            # print(full_tuto_pos)
            full_version_pos = interesting_part.find("var fullVersion = ")
            # print(full_version_pos)
            if(full_tuto_pos > 0):
                videos_content = interesting_part[13:full_tuto_pos-8]
            else:
                videos_content = interesting_part[13:full_version_pos-8]
            # print ("ZZ%sZZ" % videos_content)

    #         videos_content = """[
    #     {"id": "-SiG1huU0wA", "start": 50, "end": 57},     // 1
    #     {"id": "ZWL2D6iPjss", "start": 618, "end": 635}    // 36
    #    ]"""
            # Remove comments
            videos_content = re.sub(r'//.*\n', '\n', videos_content)
            videos = json.loads(videos_content)
            # print (videos)

            videos_full_tutorial = []
            if(full_tuto_pos > 0):
                # print(interesting_part)
                videos_full_tutorial_content = interesting_part[full_tuto_pos+25:full_version_pos-8]
                videos_full_tutorial_content = re.sub(r'//.*\n', '\n', videos_full_tutorial_content)
                # print ("ZZ%sZZ" % videos_full_tutorial_content)
                videos_full_tutorial = json.loads(videos_full_tutorial_content)
                # print (videos_full_tutorial)

            full_version = interesting_part[full_version_pos+19:full_version_pos+30]
            # print(full_version)
            # print()

            output.append({"slug": slug, "author": author, "title": title, "videos": videos, "videos_full_tutorial": videos_full_tutorial, "full_version": full_version})
            # break

# print(output)
output_content = json.dumps(output, indent=2)
# print(output_content)
js_content = "var tutoriales = %s;" % output_content
print(js_content)
# Prettier videos lines output


# "videos": [
#       {
#         "id": "cyNkflVYLJY",
#         "start": 440,
#         "end": 450
#       },
#       {
#         "id": "cyNkflVYLJY",
#         "start": 541,
#         "end": 554
#       },

# {"id": "e-0P_fOdDEU", "start": 0, "end": 18},      // 1
js_content = re.sub(r'{\n\s+"id": "(.*)",\n\s+"start": (\d+),\n\s+"end": (\d+)\n\s+}', '{"id": "\g<1>", "start": \g<2>, "end": \g<3>}', js_content)
# re.sub(r'(foo)', r'\g<1>123', 'foobar')
print(js_content)

with open("../website/src/aprender/tutoriales.js", 'w') as out_file:
    out_file.write(js_content)
