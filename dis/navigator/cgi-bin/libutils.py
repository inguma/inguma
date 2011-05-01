#!/usr/bin/python

import os
import sys
import cgi

def isCgiMode():
	gateway = os.getenv("GATEWAY_INTERFACE")
	
	if gateway != None and gateway != "":
		return True
	else:
		return False

def dieError(msg):
	if isCgiMode():
		print "<font color='red'>%s</font>" % cgi.escape(msg)
	else:
		print msg
	sys.exit(0)

def printHeader():
    print "content-type: text/html\n\n"

def showWarning(msg):
	
	if isCgiMode():
		warning = """<table border="0" cellpading="0" cellspacing="0">
<tr>
<td valign="center"><img src='/img/warning.png'/></td>
<td><font color='red'>Warning:</font> %s</td>
</tr>
</table>""" % cgi.escape(msg)
	else:
		warning = "Warning: %s" % msg

	print warning

def cleanFile(str):
    return str.replace("..", "").replace("\\", "").replace("/", "").replace("&", "").replace("`", "").replace("|", "").replace(";", "").replace('"', "").replace("'", "").replace("<", "").replace(">", "").replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "").replace("$", "").replace("(", "")

def getJavascript():
    return """
<script>
function toggleShowHide(obj1, obj2)
{
var rep;

	rep  = document.getElementById(obj1);
	rep2 = document.getElementById(obj2);
	
	rep2.style.display = "none";
	rep2.style.visibility="hidden";
	
	rep.style.display="block";
	rep.style.visibility="visible";
}

function changeFunction()
{
	document.forms[0].submit();
}

function adjustMe(objIframe)
{
var miframe;

  miframe = document.getElementById(objIframe);
  miframe.height = screen.height * 0.60;
  miframe.width  = screen.width  * 0.80;
}

function addComment(database, address)
{
var msg;
var idFrame;
var idComment;

	idFrame = document.getElementById('idStatus');
	idComment = document.getElementById('idComment_' + address);
	msg = prompt('Enter comment for database ' + database + ' at ' + address);
	
	if (msg) {
		idStatus.src = '/cgi-bin/addcomment.py?database=' + escape(database) + '&address=' + escape(address) + '&comment=' + escape(msg);
		idComment.innerHTML = '<font color="olive">;' + msg + '</font>';
	}

}

</script>
"""

def getImageJavascript():
	return "<script src='/image.js'></script>"

def getCSS():
    return "<link rel='stylesheet' href='/style.css' type='text/css'>"

def getImageToolbar():
	return """
<div align='left'><input type="button" value="Adjust" onclick="javascript:adjustImage()"></div>
"""

def printBodyHeader():
    print """<html><head>%s%s</head><body><table border="0" cellspacing="0" cellpading="0">
<tr>
    <td background="/img/p.gif" width="35"></td>
    <td background="/img/top.gif" height="35" width="600">&nbsp;</td>
    <td background="/img/q.gif" width="40" height="35">&nbsp;</td>
</tr>
<tr>
  <td background="/img/bg-left.gif"></td>
  <td><div><h1>OpenDis Binary Navigator</h1></div>
""" % (getJavascript(), getCSS())

def printBodyFooter():
    print """
	<h5>Copyright (c) 2008 Joxean Koret</h5>
	<td background="/img/bg-right.gif">&nbsp;</td></td>
    </tr><tr>
    <td background="/img/b.gif" width="35">&nbsp;</td>
    <td background="/img/bg-bottom.gif" height="36" width="35">&nbsp;</td>
    <td background="/img/d.gif" width="35">&nbsp;</td>
</tr>
</table></body></html>"""

def getImageSize(filename):
	import Image
	
	return Image.open(filename).size

