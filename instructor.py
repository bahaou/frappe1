# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today
from frappe import _
from frappe.student import get_current_term
from frappe.desk.form.linked_with import get_linked_doctypes
from erpnext.education.utils import check_content_completion, check_quiz_completion

def is_instructor(user=None):
	if not user:
		user = frappe.session.user
	#get the name of the instructor using email
	l = [r[0] for r in  frappe.db.sql("""select ins.name from `tabInstructor` as ins, `tabEmployee` as em where ins.employee = em.name and em.user_id=%s """, (user,))]
				
	return len(l)==1
def get_instructorname(user=None):
	if not user:
		user = frappe.session.user
	l = [r[0] for r in  frappe.db.sql("""select tab2.name from `tabEmployee` as tab1 ,`tabInstructor` as tab2 where  tab1.name = tab2.employee and tab1.user_id=%s """, (user,))]
	return l[0] if len(l)>0 else "no"
	
def getnomprenom(user=None):
	if not user:
		user = frappe.session.user
		print(user)
	l = [r[0]+" "+r[1] for r in  frappe.db.sql("""select last_name,first_name from `tabUser` where  email=%s """, (user,))]
	return l[0] if len(l)>0 else "no"
		
		
def get_instructoremail(name):
	l = [r[0] for r in  frappe.db.sql("""select tab1.user_id from `tabEmployee` as tab1 ,`tabInstructor` as tab2 where  tab1.name = tab2.employee and tab2.name=%s """, (name,))]
	return l[0] if len(l)>0 else "no"


def get_classes(user=None):
	term=get_current_term()
	
	if not user:
		user = frappe.session.user
	name = get_instructorname(user)
	l = [r[0] for r in  frappe.db.sql("""select DISTINCT student_group from `tabCourse Schedule` where  instructor=%s and academic_term=%s """, (name,term,))]
	print(name)
	return l
def get_classescourses(user=None):
	term=get_current_term()
	
	if not user:
		user = frappe.session.user
	name = get_instructorname(user)
	l = [r[0][:-8]+"_"+r[1] for r in  frappe.db.sql("""select DISTINCT student_group,course from `tabCourse Schedule` where  instructor=%s and academic_term=%s """, (name,term,))]
	return l
def get_subjects(group,instructor=None):
	term=get_current_term()
	if not instructor:
		l = [list(r[:2]) for r in  frappe.db.sql("""select DISTINCT course,formule from `tabCourse Schedule` where  student_group=%s and academic_term=%s""", (group,term,))]
		return l
	name = get_instructorname(instructor)
	l = [ r[0] for r in  frappe.db.sql("""select DISTINCT course from `tabCourse Schedule` where  instructor=%s and student_group=%s and academic_term=%s""", (name,group,term,))]
	
	return l


def get_students(group,subject=None,instructor=None):
	term=get_current_term()
	if not instructor:
		instructor = frappe.session.user
	name = get_instructorname(instructor)
	if subject:
		l = [r[0] for r in  frappe.db.sql("""select  gr.student from `tabCourse Schedule` as s, `tabStudent Group Student` as gr where gr.parent = s.student_group and s.instructor= %s and s.course =%s and s.student_group=%s and academic_term=%s""", (name,subject,group,term,))]
		return l
	else :
		l = [r[0] for r in  frappe.db.sql("""select  student from `tabStudent Group Student` as tab1, `tabStudent Group` as tab2  where tab2.name=tab1.parent and  tab1.parent =%s and academic_term=%s""", (group,term,))]
		return l

def get_studentsbynotes(course):
	term=get_current_term()
	l = [r[0] for r in  frappe.db.sql("""select DISTINCT student from `tabcourse results` where  course=%s and academic_term=%s """, (course,term,))]
	return l

def get_notes(group,subject,instructor=None):
	if not instructor:
		instructor = frappe.session.user
	name = get_instructorname(instructor)
	term=get_current_term()
	print(term)
	l = [ list( r[:9])+[r[9]+" "+r[10],r[11],r[12]] for r in  frappe.db.sql("""select  gr.student,oral,tp,ecrit,controle1,controle2,synthese,IFNULL(c.comment,''),c.name, s.last_name,s.first_name,s.name,c.academic_term from `tabcourse results` as c, `tabStudent Group Student` as gr, `tabStudent` as s where gr.student = c.student and s.name=gr.student and gr.parent= %s and c.course =%s and c.academic_term=%s order by s.last_name """, (group,subject,term,))]
	
	print(len(l))
	return l
 

		
def getschedule(semaine ,email=None):
	days=weekDays =["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
	if not email:
		email = frappe.session.user
	name = get_instructorname(email)
	l=[]
	term=get_current_term()
	for r in  frappe.db.sql(""" select day,from_time,to_time,course,student_group,classe,emp.type,semaine from `tabEmploi` as emp , `tabCourse Schedule` as s  where emp.parent=s.name and  instructor=%s and ( semaine=%s or semaine ='' or semaine ='groupes' or semaine IS NULL) and s.academic_term=%s""" , (name,semaine,term,)):
		D={}
		D["fromhour"] = ( r[1].seconds // 3600 )
		D["fromminute"] = ( r[1].seconds //60 ) % 60
		D["tohour"] = ( r[2].seconds // 3600 )
		D["tominute"] = ( r[2].seconds //60 ) % 60
		l.append([D,r[0],r[3],r[4],r[5],r[6],r[7]])
	l1=[]
	
	for i in range(8,18):
		n=[ p for p in l if p[0]["fromhour"]==i ]
		new = [ [{},j] for j in range(6)]
		for k in n:
			k[1]=days.index(k[1])
			new[k[1]]=k
		new= [i,new]
		l1.append(new)
	return l1
	
