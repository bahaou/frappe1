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
import datetime


def is_student(user=None):
	if not user:
		user = frappe.session.user
	#get the name of the student using email
	l = [r[0] for r in  frappe.db.sql("""select name from `tabStudent`
				where student_email_id=%s """, (user,))]
				
	return len(l) == 1
	
	
def get_birthday(user=None):
	if not user:
		user = frappe.session.user
	l =[ r[0] for r in  frappe.db.sql("""select date_of_birth from `tabStudent`
				where student_email_id=%s """, (user,))]
	return	l[0]	
	
def get_location(user=None):
	translator = Translator()
	if not user:
		user = frappe.session.user
	l =[ r[0] for r in  frappe.db.sql("""select location from `tabStudent`
				where student_email_id=%s """, (user,))]
	loc = translator.translate(l[0], dest='ar') 
	return	loc.text

	
def arabic_name(user):
	if not user:
		user = frappe.session.user
	l =[ r[0] for r in  frappe.db.sql("""select arabic_name from `tabStudent`
				where student_email_id=%s """, (user,))]
	return	l[0] if len(l) > 0 else ""

def number_students(group):
	l =[ r[0] for r in  frappe.db.sql("""select count(student)  from `tabStudent Group Student` where  parent=%s """, (group,))]
	return	l[0] if len(l) > 0 else None

def get_cre():
	doc=frappe.get_doc("Education Settings")
	return(doc.cre)
def get_institut():
	doc=frappe.get_doc("Education Settings")
	return(doc.institut)
def get_student_name(email=None):
	
	if not email:
		email = frappe.session.user
	
	l = [r[0] for r in  frappe.db.sql("""select name from `tabStudent` where student_email_id=%s """, (email,))]
	return l[0]
def get_student_email(name):
	l = [r[0] for r in  frappe.db.sql("""select student_email_id from `tabStudent` where name=%s """, (name,))]
	return l[0]
	

def name_student(code):
	l = [r[0]+" "+r[1] for r in  frappe.db.sql("""select last_name, first_name from `tabStudent` where name=%s """, (code,))]
	return l[0]
def get_student_fullname(email=None):
	if not email:
		email = frappe.session.user
	l = [r[0]+" "+r[1] for r in  frappe.db.sql("""select last_name, first_name from `tabStudent` where student_email_id=%s """, (email,))]
	return l[0]
def get_student_groupe(email=None):
	if not email:
		email = frappe.session.userz  
	name = get_student_name(email)
	l = [r[0] for r in  frappe.db.sql("""select parent from `tabStudent Group Student` where student=%s """, (name,))]
	return l[0] if len(l) >0 else None
	
def get_student_groupe_name(email=None):
	if not email:
		email = frappe.session.userz  
	name = get_student_name(email)
	l = [r[0] for r in  frappe.db.sql("""select student_group_name from `tabStudent Group Student` as tab1 , `tabStudent Group` as tab2  where tab1.parent = tab2.name and student=%s """, (name,))]
	return l[0] if len(l) >0 else None	
def get_student_program(email=None):
	
	if not email:
		
		email = frappe.session.user
	
	groupe = get_student_groupe(email)
	
	l = [r[0] for r in  frappe.db.sql("""select program from `tabStudent Group` where name=%s """, (groupe,))]
	return l[0]

def get_arabic_program(email=None):
	if not email:
		email = frappe.session.user
	p = get_student_program(email)
	l = [r[:2] for r in  frappe.db.sql("""select niveau,specialite from `tabProgram` where name=%s """, (p,))]
	d={}
	d["3"]="ثالثة"
	d["1"]="أولى"
	d["2"]="ثانية"
	d["4"]="رابعة"
	
	d["Mathematiques"]="رياضيات"
	d["Informatique"]="إعلامية"
	d["Science"]="علوم الحياة والأرض"
	d["Technique"]="علوم تقنية"
	d["Lettre"]="اداب"
	d["Economie et Gestion"]="إقتصاد وتصرف"
	s=d[l[0][0]]+" "+d[l[0][1]]
	
	return s




def get_student_courses(email=None):
	if not email:
		email = frappe.session.user
	groupe = get_student_program(email)
	l = [r[0] for r in  frappe.db.sql("""select course from `tabProgram Course` where parent=%s """, (groupe,))]
	return l
	
def get_current_year():
	doc=frappe.get_doc("Education Settings")
	return(doc.current_academic_year)
def get_current_term():
	doc=frappe.get_doc("Education Settings")
	return(doc.current_academic_term)
def get_line(term):
	l = [r[0] for r in  frappe.db.sql("""select line from `tabAcademic Term` where name=%s""",(term,) )]
	return l[0] 
def semaine():
	l = [r[0] for r in  frappe.db.sql("""select semaine from `tabcurrent`""" )]
	return l[0]
	
def get_student_bulletin(email=None):
	
	
	if not email:
		email = frappe.session.user
	name = get_student_name(email)
	l = [[r[0],r[1],r[2],r[3],r[4].strftime("%A %d %B %Y")] for r in  frappe.db.sql("""select academic_term,average,result,name,creation from `tabbulletin`  where student=%s  and published=1 order by creation""" , (name,))]
	for i in range(len(l)):
		p=bulletin_details(l[i][3])
		
		l[i]=l[i]+p
		
	
	return l

	

def get_student_fullbulletin(email=None,term=None,lan=None):
	import googletrans
	if not email:
		email = frappe.session.user
	if not term:
		term = get_current_term()
	name = get_student_name(email)
	program=get_student_program(email)
	group=get_student_groupe(email)
	d={}
	if lan:
		l = [ list(r[:11]) for r in  frappe.db.sql("""select tab1.course,tab2.coefficient,oral,tp,ecrit,controle1,controle2,synthese,tab1.comment,tab2.formule1,tab3.noma from `tabcourse results` as tab1, `tabProgram Course` as tab2 ,`tabCourse` as tab3 where tab2.course = tab1.course and tab1.course = tab3.name and student=%s  and tab1.academic_term=%s and tab2.parent=%s order by tab2.idx""" , (name,term,program,))]
		for i in l:
			d[i[0]]=i[10]
			i=i[:-1]
		
		
		
	else:
		l = [ list(r[:10]) for r in  frappe.db.sql("""select tab1.course,tab2.coefficient,oral,tp,ecrit,controle1,controle2,synthese,tab1.comment,tab2.formule1 from `tabcourse results` as tab1, `tabProgram Course` as tab2  where tab2.course = tab1.course and student=%s  and tab1.academic_term=%s and tab2.parent=%s order by tab2.idx""" , (name,term,program,))]
	translator = googletrans.Translator()
	
	
	
	for i in range(len(l)) :
		
		l[i][1]=float(l[i][1])
		c = l[i][0]
		if lan:
			l[i][0]=d[l[i][0]]
		f=l[i][9]
		al=all_averages(group,c,term)
		
		f=frappe.db.get_value("formule",f, "format")
		
		f=f.replace("oral",str(l[i][2]))
		f=f.replace("tp",str(l[i][3]))
		f=f.replace("ecrit",str(l[i][4]))
		f=f.replace("c1",str(l[i][5]))
		f=f.replace("c2",str(l[i][6]))
		f=f.replace("s",str(l[i][7]))
		
		f=eval(f)
		
		l[i]=l[i][:9]+[float('%.2f' % (f))]
		rang=1
		
		for j in al:
			j[6]=frappe.db.get_value("formule",j[6], "format")
			j[6]=j[6].replace("oral",str(j[0]))
			j[6]=j[6].replace("tp",str(j[1]))
			j[6]=j[6].replace("ecrit",str(j[2]))
			j[6]=j[6].replace("c1",str(j[3]))
			j[6]=j[6].replace("c2",str(j[4]))
			j[6]=j[6].replace("s",str(j[5]))
			
			j[6]=eval(j[6])
			
			if j[6]>f:
				rang=rang+1
		
		inst=get_ins(group,c)
		l[i]=l[i]+[rang,inst]
	
		
		
	
	return l


def all_averages(group,course,term=None):
	if not term:
		term = get_current_term()
	l = [ list(r[:7]) for r in  frappe.db.sql("""select oral,tp,ecrit,controle1,controle2,synthese,tab3.formule1 from `tabcourse results` as tab1, `tabStudent Group Student` as tab2 ,`tabProgram Course` as tab3  where tab3.course = tab1.course  and tab2.student = tab1.student and tab2.parent=%s and tab1.academic_term=%s and tab1.course=%s """ , (group,term,course,))]
	
	return(l)






def bulletin_exist(bulletin):
	l = [r[0] for r in  frappe.db.sql("""select student_email_id from `tabbulletin`, `tabStudent` where tabbulletin.student= tabStudent.name and  tabbulletin.name=%s  """ , (bulletin,))]
	if len(l) > 0 :
		return l[0]
	return "None"

def get_term(bulletin):
	l = [r[0] for r in  frappe.db.sql("""select academic_term from `tabbulletin` where name=%s """,(bulletin,) )]
	return l[0]

def getschedule(email=None,day=None,groupe=None):
	days=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
	if not email:
		email = frappe.session.user
	if not groupe:
		groupe = get_student_groupe(email) 
	l=[]
	if not is_student(email) and not groupe:
		return []
	term=get_current_term()
	if not day:
		for r in  frappe.db.sql(""" select day,emp.from_time,emp.to_time,course,instructor,classe,emp.type,semaine,emp.autre,emp.name from `tabEmploi` as emp , `tabCourse Schedule` as s  where emp.parent=s.name and  student_group=%s and s.academic_term=%s order by emp.from_time""" , (groupe,term,)):	
			D={}
			D["fromhour"] = ( r[1].seconds // 3600 )
			D["fromminute"] = ( r[1].seconds //60 ) % 60
			D["tohour"] = ( r[2].seconds // 3600 )
			D["tominute"] = ( r[2].seconds //60 ) % 60
			l.append([D,r[0],r[3],r[4],r[5],r[6],r[7],r[9],r[8],r[1],r[2]] )
	else:
		for r in  frappe.db.sql(""" select day,from_time,to_time,course,instructor,classe,emp.type,semaine,emp.name,emp.autre from `tabEmploi` as emp , `tabCourse Schedule` as s  where emp.parent=s.name and  student_group=%s  and s.academic_term=%s and day =%s order by from_time""" , (groupeterm,day,)):	
			D={}
			D["fromhour"] = ( r[1].seconds // 3600 )
			D["fromminute"] = ( r[1].seconds //60 ) % 60
			D["tohour"] = ( r[2].seconds // 3600 )
			D["tominute"] = ( r[2].seconds //60 ) % 60
			l.append([D,r[0],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[1],r[2]] )
	if not day:
		l2=[]
		l3=[]
		repeated=[]
		for o in l:
			if o[-3]:
				
				
				p=list(get_course(o[-3],o[1],o[-2],o[-1]))
				o=o[:-3]
				repeated.append(p[-1])
				p=p[:-1]
				o=o+list(p)+['yes']
				l3.append(o)
			else:
				o=o[:-3]
				o.append('')
				l3.append(o)
		
		
		for o in l3:
			
			
			if o[-2]  in repeated:
				l3.remove(o)
						
		
		
		
		
		for d in days:
			n= [d,[ j for j in l3 if j[1]==d ]]
			l2.append(n)
		
		return  l2
	
		
		
		
		
	return l


def get_course(course,day,fro,to):
	
	l = [ [ r[0],r[1],r[2],r[3]] for r in  frappe.db.sql("""select course,instructor,emp.classe,emp.name from `tabCourse Schedule` as sc, tabEmploi as emp where emp.parent=sc.name and sc.name=%s and emp.day=%s and emp.from_time=%s and emp.to_time=%s""" , (course,day,fro,to))]
	return l[0]


def get_result(bulletin):
	l = [r[0] for r in  frappe.db.sql("""select result from `tabbulletin` where name=%s  """ , (bulletin,))]
	return l[0]

def get_program(groupe):
	l = [ list(r[:2])+[float(r[2]) if r[2] is not None else '' ] for r in  frappe.db.sql("""select course,coefficient,volume from `tabProgram Course` where parent =%s""",(groupe,) )]
	
	return l if len(l) > 0 else None		

def get_exams(group):
	l = [[r[0],r[1].strftime("%A %d %B %Y")] for r in  frappe.db.sql("""select academic_term,creation from `tabExamens` where student_group=%s  """ , (group,))]
	
	return l



def get_exam(term,group):
	
	l = [r[:6] for r in  frappe.db.sql("""select course,day,from_time,to_time,room,surveillant1,surveillant2 from `tabExamens` as tab1, `tabExams Schedule` as tab2 where tab1.name = tab2.parent and tab1.academic_term=%s  and tab1.student_group=%s order by from_time""" , (term,group,))]
	days=list(set([i[1] for i in l ]))
	days.sort()
	l2=[]
	for i in days:
		new=[]
		for j in l:
			if j[1]==i:
				new.append(j)
		l2.append(new)
				
	
	return(l2)

def get_exam_startdate(term):
	l = [r[0] for r in  frappe.db.sql("""select from_date from `tabExamens` where academic_term=%s  """ , (term,))]
	return l[0]
def get_exam_enddate(term):
	l = [r[0] for r in  frappe.db.sql("""select to_date from `tabExamens` where academic_term=%s  """ , (term,))]
	return l[0]

def get_myattendance(user):
	if not user:
		user = frappe.session.user
	name = get_student_name(user)
	l = [r[0:3] for r in  frappe.db.sql("""select status,course,sc.academic_term  from `tabStudent Attendance` as a, `tabEmploi` as emp, `tabCourse Schedule` as sc where a.emploi = emp.name and emp.parent=sc.name  and  student=%s and a.docstatus=1  """ , (name,))]
	
	return l

def get_ins(group,course):
	l = [r[0] for r in  frappe.db.sql("""select inn.noma from `tabCourse Schedule` as sc, `tabInstructor` as inn where sc.instructor=inn.name and student_group=%s and course =%s  """ , (group,course,))]
	return l[0] if len(l)>0 else ""






@frappe.whitelist()
def save_notes(notes,subject):
	
	term = get_current_term()
	
	notes=notes.replace("[","")
	notes=notes.replace("]","")
	notes=notes.replace("\"","")
	l=[]
	notes=notes.split(',')
	for j in range(int(len(notes)/8)):
		l.append(notes[:8])
		notes=notes[8:]
	
	
	
	for i in l:
		
		doc = frappe.get_doc("course results", i[0])
		
		doc.oral=i[1]
		doc.tp=i[2]
		doc.ecrit=i[3]
		doc.controle1=i[4]
		doc.controle2=i[5]
		doc.synthese=i[6]
		if i[7]!=str(-1) and i[7]!=-1:
			doc.comment=i[7]
		else:
			doc.comment=""
		doc.save()
		frappe.db.commit()
		
		
	frappe.msgprint(frappe._("Saved"), indicator='green', alert=True)
	return None
	
	
@frappe.whitelist()	
def wrongnumber(c):
	
	frappe.msgprint(frappe._("chiffre incorrect "), indicator='yellow', alert=True)
	return None


	
	

def get_averages(email,term):
	s=0
	c=0
	
	mates=get_mates(email)
	bulletin=get_student_fullbulletin(email,term)
	for i in bulletin:
		c+=i[1]
		s+=i[1]*i[9]
	if c==0:
		c=1
	average=round(s/c,2)
	rank=1
	
	for j in mates:
		s=0
		c=0
		email=get_student_email(j)
		bulletin=get_student_fullbulletin(email,term)
		
		for i in bulletin:
			c+=i[1]
			s+=i[1]*i[9]
		if c==0:
			c=1
		a=round((s/c),2)
		if a> average:
			rank+=1
	return [average,rank,get_termc(term)]
		
	
	
def bulletin_details(bulletin):
	term = get_term(bulletin)
	email=bulletin_exist(bulletin)
	l=get_averages(email,term)
	return l


def get_terms(year):
	l = [r[0] for r in  frappe.db.sql("""select name from `tabAcademic Term` where academic_year=%s   order by creation""" , (year,))]
	return l
def term_year(term):
	l = [r[0] for r in  frappe.db.sql("""select academic_year from `tabAcademic Term` where name=%s   """ , (term,))]
	return l[0] if len(l)>0 else None
		
def get_mates(email):
	group=get_student_groupe(email)
	l = [r[0] for r in  frappe.db.sql("""select student from `tabStudent Group Student` where parent=%s;""" , (group,))]
	return l
	
def nombre_ordinal(email):
	name=get_student_name(email)
	l = [r[0] for r in  frappe.db.sql("""select idx from `tabStudent Group Student` where student=%s;""" , (name,))]
	return(l[0])
	
def get_termc(term):
	l = [r[0] for r in  frappe.db.sql("""select coefficient from `tabAcademic Term` where name=%s;""" , (term,))]
	return l[0]
	
def last_term(term):
	l = [r[0] for r in  frappe.db.sql("""select last from `tabAcademic Term` where name=%s;""" , (term,))]
	return l[0]


def termsstudent(student):
	
	year=get_current_year()
	l = [r[0] for r in  frappe.db.sql("""select academic_term from `tabbulletin` where student=%s and academic_year=%s;""" , (student,year,))]
	return l
def annual(email,year):
	s=0
	c=0
	terms=get_terms(year)
	
	for i in terms:
		p=get_averages(email,i)
		
		s+=p[0]*float(p[2])
		c+=float(p[2])
	
	return (s/c)
	
	
	
def annual_rank(email,year):
	terms=get_terms(year)
	
	mya=annual(email,year)
	rank=1
	mates=get_mates(email)
	for m in mates:
		email=get_student_email(m)
		a=annual(email,year)
		
		if a>mya:
			rank+=1
	return rank
	
	
	
def directeur():
	doc=frappe.get_doc("Education Settings")
	d=doc.directeur
	l = [r[0] for r in  frappe.db.sql("""select noma from tabUser where  email=%s;""",(d,) )]
	return l[0]
	
	
	
def journal(email,year=None):
	if not email:
		email = email = frappe.session.user
	if not year:
		year = get_current_year()
	terms=get_terms(year)
	
	ret=[]
	for term in terms:
		t=term[term.find("(")+1:term.find(")")]
		d={"Semestre 1":"الثلاثي الأول","Semestre 2":"الثلاثي الثاني","Semestre 3":"الثلاثي الثالث"}
		t=d[t]
		k = get_student_fullbulletin(email,term,"a")
		for i in range(len(k)):
			k[i]=[k[i][0],k[i][-3],k[i][-2]]
		ret.append([t,get_termc(term),k])
	return(ret)
	
def events(group):
	now = datetime.datetime.now()
	Nd = datetime.datetime.today() + datetime.timedelta(days=1)
	l = [list(r[:]) for r in  frappe.db.sql("""select objet,description,date,from_time,to_time,instructeur,room,subject from `tabEvents` where DATE(date) >= DATE(NOW()) and groupe=%s order by date;""",(group,) )]
	for i in l:
		i[3] = str(i[3])[:-3]
		i[4] = str(i[4])[:-3]
		if (i[2] == now.date()) :
			i[2] = "aujourd'hui"
		elif (i[2] == Nd.date()) :
			i[2] = "demain"
		else :
			i[2] = i[2].strftime("%d %B %Y")
	
	return l
	
	
	
	
def all_bulletins(term=None):
	if not term:
		term = get_current_term()
	l = [r[0] for r in  frappe.db.sql("""select name from `tabbulletin` where academic_term=%s""",(term,) )]
	return l
	
def get_bulletins(terms,groups):
	if terms[0] =='tous' and groups[0]=='tous':
		l = [r[0] for r in  frappe.db.sql("""select name from `tabbulletin` """)]
		return l
	elif terms[0] !='tous' and groups[0]=='tous':
		sql = "select name from `tabbulletin` where academic_term in ('"+terms[0]+"'"
		for i in terms[1:]:
			sql+=",'"+i+"'"
		sql+=")"
		l = [r[0] for r in  frappe.db.sql(sql )]
		return(l)
	elif terms[0] =='tous' and groups[0]!='tous':
		sql = "select bul.name from `tabbulletin` as bul, `tabStudent Group Student` as s where bul.student=s.student and s.parent in ('"+groups[0]+"'"
		for i in groups[1:]:
			sql+=",'"+i+"'"
		sql+=") order by academic_term asc"
		l = [r[0] for r in  frappe.db.sql(sql )]
		
		return(l)
	else:
		sql = "select bul.name from `tabbulletin` as bul, `tabStudent Group Student` as s where bul.student=s.student and s.parent in ('"+groups[0]+"'"
		for i in groups[1:]:
			sql+=",'"+i+"'"
		sql+=") and academic_term in ('"+terms[0]+"'"
		for i in terms[1:]:
			sql+=",'"+i+"'"
		sql+=") order by academic_term asc"
		l = [r[0] for r in  frappe.db.sql(sql )]
		return(l)
def get_bulletins2(students,terms):
	if terms[0]=='tous':
		sql = "select name from `tabbulletin` where student in ('"+students[0]+"'"
		for i in students[1:]:
			sql+=",'"+i+"'"
		sql+=")"
		l = [r[0] for r in  frappe.db.sql(sql )]
		return(l)
	else:
		sql = "select name from `tabbulletin` where student in ('"+students[0]+"'"
		for i in students[1:]:
			sql+=",'"+i+"'"
		sql+=") and academic_term in ('"+terms[0]+"'"
		for i in terms[1:]:
			sql+=",'"+i+"'"
		sql+=") order by academic_term asc"
		l = [r[0] for r in  frappe.db.sql(sql )]
		return(l)
		
	
		
		
		
		
		
		
		
		
@frappe.whitelist()	
def check_combinations(url):
	url=url.replace('/printbulletin?','')
	terms,groups=url.split('?')
	terms=terms.split('&')
	groups=groups.split('&')
	if (len(get_bulletins(terms,groups))==0):
		frappe.msgprint(frappe._("Les groupes sélectionnés n'existent pas dans ces termes académiques"), indicator='red', alert=False)
	
	
	return (len(get_bulletins(terms,groups))!=0)
	
	
	



def result_years():
	l = [r[0] for r in  frappe.db.sql("""select distinct academic_year from `tabbulletin`""" )]
	return l
def result_terms():
	l = [r[0] for r in  frappe.db.sql("""select distinct academic_term from `tabbulletin`""" )]
	return l	
def result_groups():
	l = [r[0] for r in  frappe.db.sql("""select distinct tab2.parent from `tabbulletin` as tab1 , `tabStudent Group Student` as tab2 where tab1.student = tab2.student;""" )]
	return l
def result_programs():
	gr = result_groups()
	l=[]
	for g in gr:
		k = [r[0] for r in  frappe.db.sql("""select program from `tabStudent Group` where name = %s""",(g,) )]
		l.append(k[0])
	return l
	
def group_color(group):
	l = [r[0] for r in  frappe.db.sql("""select color from `tabStudent Group` where name=%s""",(group,) )]
	
	return l[0] if len(l) > 0 else None

@frappe.whitelist()	
def who():
	who=""
	user = frappe.session.user
	l = [r[0] for r in  frappe.db.sql("""select name from `tabStudent`
				where student_email_id=%s """, (user,))]
				
	if len(l) == 1:
		who="Student"
	
	l = [r[0] for r in  frappe.db.sql("""select u.name from `tabUser` as u, `tabInstructor` as i 
				where  username=i.name and email=%s """, (user,))]
	
	if len(l)==1:
		who="Instructor"
	
	return who
	
	

				
def bulletin_terms():
	l = [r[0] for r in  frappe.db.sql("""select distinct academic_term from `tabbulletin` order by academic_term """)]
	ll=[]
	for i in range(len(l)):
		ll.append([l[i],l[i].replace(' ','').replace('-','').replace(')','').replace('(','')])
	
	return ll
def bulletin_groups():
	l = [r[0].replace(' ','').replace('-','').replace(')','').replace('(','') for r in  frappe.db.sql("""select distinct ss.student_group_name from `tabbulletin` as b,`tabStudent Group Student` as s, `tabStudent Group` as ss where b.student = s.student and s.parent=ss.name order by s.parent """)]
	return l		
def students(group,term=None):
	if not term:
		term = get_current_term()
	l = [r[0].replace(' ','').replace('-','').replace(')','').replace('(','') for r in  frappe.db.sql("""select distinct academic_term from `tabbulletin` order by academic_term """)]

	
	
	
@frappe.whitelist()	
def publier(last):
	
	term=get_current_term()
	if last =="true"  or term[-2]=="3":
		doc = frappe.get_doc('Academic Term', term)
		doc.last=1
		doc.save()
	bulletins=frappe.db.get_list('bulletin', filters={'published': '0',"academic_term":term})
	for b in bulletins:
    		name=b["name"]
    		
    		doc = frappe.get_doc('bulletin', name)
    		doc.published=1
    		
    		doc.save()
	if last =="false":
		year=get_current_year()
		number = int(term[-2])
		if "Semestre" in term:
			t = "Semestre "+str(number+1)
		else:
			t = "Trimestre "+str(number+1)
		doc = frappe.get_doc('System Settings')
		
		if not frappe.db.get_value('Academic Term', {'term_name': t,'academic_year':year},["name"]):
			doc = frappe.get_doc({'doctype': "Academic Term", 'academic_year': year,"term_name":t}).insert()
		
			
			frappe.msgprint(frappe._("bulletins publies avec succès"), indicator='green', alert=False)
			frappe.msgprint(frappe._(t+ " a été créé avec succès."), indicator='green', alert=False)
		else:
			frappe.msgprint(frappe._("bulletins publies avec succès"), indicator='green', alert=False)
			frappe.msgprint(frappe._(t+ " existe déja!"), indicator='green', alert=False)
		
	else:
		frappe.msgprint(frappe._("bulletins publies"), indicator='green', alert=False)
    		
    		
	
    
    




