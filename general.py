# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today
from frappe import _
from frappe.desk.form.linked_with import get_linked_doctypes
import locale
from googletrans import Translator
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
from datetime import date
from datetime import datetime
import requests,json
import xml.etree.ElementTree as ET
from frappe.student import *
from frappe. instructor import *
import hashlib
from datetime import datetime

@frappe.whitelist()	
def mobile():
	
	doc=frappe.get_doc("Education Settings")
	return(str(doc.mobile))


def images(attached_to):
	l = [r[0] for r in  frappe.db.sql("""select file_url from tabFile where  attached_to_name=%s """, (attached_to,))]
	return (l)
	
def news():
	l = [[r[0],r[1],r[2].strftime('%Y'),int(r[2].strftime('%m')),r[2].strftime('%d'),r[3].strftime("%A %d %B %Y")] for r in  frappe.db.sql("""select title,description,date,creation from tabNews order by creation  """)]
	return (l)
def image(attached_to_field):
	l = [r[0] for r in  frappe.db.sql("""select file_url from tabFile where  attached_to_field=%s """, (attached_to_field,))]
	return l[0] if len(l) > 0 else None
@frappe.whitelist()		
def erreur(err):
	print(err)
	frappe.msgprint(frappe._(err), indicator='red', alert=False)
@frappe.whitelist()		
def students(msg):
	terms,groups=msg.split('?')
	if terms !='tous':
		terms=terms.split('&')
	else :
		terms=['tous']
	if groups !='tous':
		groups=groups.split('&')
	else :
		groups=['tous']
	print(terms)
	print(groups)
	if terms[0] =='tous' and groups[0]=='tous':
		sql = "select distinct s.student,s.student_name from tabbulletin as b, `tabStudent Group Student` as s where b.student = s.student"
	elif terms[0] !='tous' and groups[0]=='tous':
		sql = "select distinct s.student,s.student_name from `tabbulletin` as bul, `tabStudent Group Student` as s where bul.student=s.student and academic_term in ('"+terms[0]+"'"
		for i in terms[1:]:
			sql+=",'"+i+"'"
		sql+=")"

	elif terms[0] =='tous' and groups[0]!='tous':
		sql = "select distinct s.student,s.student_name from `tabbulletin` as bul, `tabStudent Group Student` as s where bul.student=s.student and s.parent in ('"+groups[0]+"'"
		for i in groups[1:]:
			sql+=",'"+i+"'"
		sql+=") order by academic_term asc"
	else:
		sql = "select distinct s.student,s.student_name from `tabbulletin` as bul, `tabStudent Group Student` as s where bul.student=s.student and s.parent in ('"+groups[0]+"'"
		for i in groups[1:]:
			sql+=",'"+i+"'"
		sql+=") and academic_term in ('"+terms[0]+"'"
		for i in terms[1:]:
			sql+=",'"+i+"'"
		sql+=") order by academic_term asc"
	l = [r[:] for r in  frappe.db.sql(sql )]
	r=''
	for i in l:
		r+=i[0]+'&&'+i[1]+'???'
	r=r[:-3]
	
	return(r)

def getmeetings():
	meetings=[]
	doc=frappe.get_doc("Education Settings")
	secret=doc.bbb_secret
	
	code="getMeetings"+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
	response =requests.get("http://bbb.slnee-dev.com/bigbluebutton/api/getMeetings?checksum="+checksum)
	r=response.content
	tree = ET.fromstring(r)

	for child in tree.iter("*"):
		if child.tag=="meetingName":
			meetings.append(child.text)
	
	return meetings

	
def moderatorpw(salle):
	doc=frappe.get_doc("Education Settings")
	secret=doc.bbb_secret
	
	code="getMeetings"+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
	response =requests.get("http://bbb.slnee-dev.com/bigbluebutton/api/getMeetings?checksum="+checksum)
	r=response.content
	tree = ET.fromstring(r)
	take = False
	for child in tree.iter("*"):
		if child.tag=="meetingName" and child.text== salle:
			take = True
		if child.tag=="moderatorPW" and take :
			return child.text
	return ("code-1")
		
def attendeepw(salle):
	doc=frappe.get_doc("Education Settings")
	secret=doc.bbb_secret
	
	code="getMeetings"+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
	response =requests.get("http://bbb.slnee-dev.com/bigbluebutton/api/getMeetings?checksum="+checksum)
	r=response.content
	tree = ET.fromstring(r)
	take = False
	for child in tree.iter("*"):
		if child.tag=="meetingName" and child.text== salle:
			take = True
		if child.tag=="attendeePW" and take :
			return child.text
	return ("code-1")


	

@frappe.whitelist()
def meetingexist(salle):
	term=get_current_term()
	user = frappe.session.user
	
	if  is_student(user):
		group=get_student_groupe()[:-8]

		return  1 if group+"_"+salle in getmeetings() else 0
	if is_instructor(user):
		
		return  1 if salle in getmeetings() else 0
	


@frappe.whitelist()
def joinmeeting(salle):
	doc=frappe.get_doc("Education Settings")
	secret=doc.bbb_secret
	term=get_current_term()
	if is_instructor():
		
		name=getnomprenom()
		mp=moderatorpw(salle)
		
	if is_student():
		name=get_student_fullname()
		group=get_student_groupe()[:-8]
		salle=group+"_"+salle
		mp=attendeepw(salle)
	
	url="fullName="+name+"&meetingID="+salle+"&password="+mp+"&redirect=true"
	url = url.replace(' ','+')
		
	code = "join"+url+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
		
	url="https://bbb.slnee-dev.com/bigbluebutton/api/join?"+url+"&checksum="+checksum
	return url


@frappe.whitelist()
def startmeeting(salle):
	doc=frappe.get_doc("Education Settings")
	secret=doc.bbb_secret
	term=get_current_term()
	print("-"+secret+"-")
	if is_instructor():
		
		name=getnomprenom()
		
	if is_student():
		name=get_student_fullname()
		group=get_student_groupe()[:-8]
		salle=group+"_"+salle
	url ="allowStartStopRecording=true&attendeePW=ap&autoStartRecording=false&meetingID="+salle+"&moderatorPW=mp&name="+salle+"&record=true"
	url = url.replace(' ','+')
		
	code = "create"+url+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
	url="https://bbb.slnee-dev.com/bigbluebutton/api/create?"+url+"&checksum="+checksum
	print(url)
	response =requests.get(url)
	print(response.text)
	mp=moderatorpw(salle)
	url="fullName="+name+"&meetingID="+salle+"&password=mp&redirect=true"
	url = url.replace(' ','+')
		
	code = "join"+url+secret
	code = code.encode('utf-8')
	hash_object = hashlib.sha1(code)
	checksum=hash_object.hexdigest()
		
	url="https://bbb.slnee-dev.com/bigbluebutton/api/join?"+url+"&checksum="+checksum
	
	return url
	
		
def chat(group,course,term,typ):
	
	if typ=="first":
		l = [list(r[:4]) for r in  frappe.db.sql("""select tab1.creation,tab2.full_name,message,tab2.user_image from `tabchat` as tab1,tabUser as tab2 where tab1.sender=tab2.email and   groupe=%s and term=%s and course =%s  order by tab1.creation  asc """, (group,term,course,))]
		
	else:
		l = [list(r[:4]) for r in  frappe.db.sql("""select tab1.creation,tab2.full_name,message,tab2.user_image from `tabchat` as tab1,tabUser as tab2 where tab1.sender=tab2.email and   groupe=%s and term=%s and course =%s  and tab1.id>%s order by tab1.creation  asc  """, (group,term,course,typ,))]
	
	return (l)
	

@frappe.whitelist()
def live(salle,ma):
	user = frappe.session.user
	term=get_current_term()
	if ('_' in salle):
		group,salle=salle.split('_')
		group=group+'-'+get_current_term()[:8]
		
	else :
		group=get_student_groupe()
		
	c=chat(group,salle,term,ma)
	ch=''
	for i in c:
		
		h=i[0].strftime("%m/%d/%Y, %H:%M:%S")+"£"+i[1]+"£"+i[2]+"£"
		if i[3]==None:
			h+="None$"
		else:
			h+=i[3]+"$"
		ch+=h
	m=maxx(group,salle,term)
	
	return(ch+str(m))
	
@frappe.whitelist()
def send(message,salle):
	idi = [r[0] for r in  frappe.db.sql("""select MAX(id) from tabchat; """, ())][0]
	
	user = frappe.session.user
	if ('_' in salle):
		group,salle=salle.split('_')
		group=group+'-'+get_current_term()[:8]
		
	else :
		group=get_student_groupe()
	doc = frappe.new_doc('chat')
	doc.message=message
	if message!='':
		doc.groupe=group
		doc.sender=user
		if idi==None:
			doc.id=0
		else:
			doc.id=idi+1
		doc.term=get_current_term()
		doc.course=salle
		doc.insert(ignore_permissions=True)
	
	
		l = [list(r[:2]) for r in  frappe.db.sql("""select  full_name,user_image from tabUser where email=%s """, (user,))][0]
		now = datetime.now()
		return(now.strftime("%m/%d/%Y, %H:%M:%S")+"$"+str(l[0])+"$"+str(l[1]))

@frappe.whitelist()
def restart(salle):
	user = frappe.session.user
	term=get_current_term()
	if ('_' in salle):
		group,salle=salle.split('_')
		group=group+'-'+get_current_term()[:8]
		
	else :
		group=get_student_groupe()
		
	c=chat(group,salle,term,'first')
	ch=''
	for i in c:
		print(998998,i[3])
		h=i[0].strftime("%m/%d/%Y, %H:%M:%S")+"£"+i[1]+"£"+i[2]+"£"
		if i[3]==None:
			h+="None$"
		else:
			h+=i[3]+"$"
		ch+=h
	m=maxx(group,salle,term)
	
	return(ch+str(m))
	
		


def maxx(group,course,term):
	
	l = [r[0] for r in  frappe.db.sql("""select MAX(id) from `tabchat` as tab1,tabUser as tab2 where tab1.sender=tab2.email and   groupe=%s and term=%s and course =%s  order by tab1.creation  asc """, (group,term,course,))][0]
	if l == None:
		return (-1)
	return(l)













		


	
