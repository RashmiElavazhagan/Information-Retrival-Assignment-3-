from bs4 import BeautifulSoup
import re

html = """<!DOCTYPE html>
<html>
<head>
    <title>My first web page</title>
</head>
<body>
    <h1>My first web page</h1>
    <h2>What this is tutorial</h2>
    <p>A simple page put together using HTML. <em>I said a simple page.</em>.</p>
    <ul>
        <li>To learn HTML</li>
        <li>
            To show off
            <ol>
                <li>To my boss</li>
                <li>To my friends</li>
                <li>To my cat</li>
                <li>To the little talking duck in my brain</li>
            </ol>
        </li>
        <li>Because I have fallen in love with my computer and want to give her some HTML loving.</li>
    </ul>
    <h3>Where to find the tutorial</h3>
    <p><a href="http://www.aaa.com"><img src="http://www.aaa.com/badge1.gif"></a></p>
    <h4>Some random table</h4>
    <table>
        <tr class="tutorial1">
            <td>Row 1, cell 1</td>
            <td>Row 1, cell 2<img src="http://www.bbb.com/badge2.gif"></td>
            <td>Row 1, cell 3</td>
        </tr>
        <tr class="tutorial2">
            <td>Row 2, cell 1</td>
            <td>Row 2, cell 2</td>
            <td>Row 2, cell 3<img src="http://www.ccc.com/badge3.gif"></td>
        </tr>
    </table>
</body>
</html>"""
soup = BeautifulSoup(html, "html.parser")

#4a
title_text = soup.find("title").text
print(title_text)

#4b
second_li = soup.find_all("ol")[0].find_all("li")[1].text
print(second_li)

#4c

td_tags = soup.find("tr", class_="tutorial1").find_all("td")
for td in td_tags:
    print(td.text.strip())

#4d

h2_texts = soup.find_all("h2", string=re.compile("tutorial", re.IGNORECASE))
for h2 in h2_texts:
    print(h2.text)

#4e

html_texts = [text for text in soup.find_all(string=re.compile(r'HTML'))]
print(html_texts)

#4f

second_row = soup.find("tr", class_="tutorial2").find_all("td")
for td in second_row:
    print(td.text.strip())

#4g
img_tags = soup.find("table").find_all("img")
for img in img_tags:
    print(img["src"])
