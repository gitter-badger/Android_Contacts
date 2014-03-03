import android
import collections
import re
import sys

QUERY="content://com.android.contacts/data/phones"
COLUMNS=["data1", "account_type", "display_name", "contact_id"]
LAYOUT_FILE_NAME = "layout/contacts_layout.xml"

'''
class Events(object):
	def __init__(self):
		pass
	def eventLoop(self):
'''
class Contact_Info(object):
	def __init__(self, name, phone_number, contact_id):
		self.name = name
		self.phone_number = phone_number
		self.contact_id = contact_id
	
	def __repr__(self):
		return "%s %s"%(self.name, self.phone_number)


class Contacts_Base(object):
	def __init__(self):
		self.droid = android.Android()
		self.contact_list_dict = None
	
	def query_contact_list(self):
		contact_list_dict = self.droid.queryContent(QUERY, COLUMNS).result
		self.contact_list_dict = contact_list_dict
		
	def get_contact_with_multiple_numbers(self):
		duplicate_contact_dict=collections.defaultdict(list)
		for contact_dict in self.contact_list_dict:
			if contact_dict["display_name"] == "Abhilash Joseph":print contact_dict	
			duplicate_contact_dict[contact_dict["contact_id"]].append(contact_dict)

		return duplicate_contact_dict

	def set_duplicate_contact_list(self):
		'''
		1) Create duplicate contact dict where (display_name, data1) tuple as key and contact_obj_list will be value.
		   Example: {("Abhijeet", "99999999999"):[obj1, obj2]}
		'''
		duplicate_contact_dict = collections.defaultdict(list)
		for contact_dict in self.contact_list_dict:
			display_name = contact_dict["display_name"].strip()
			data1 = contact_dict["data1"]
			contact_id = contact_dict["contact_id"]
			contact_obj = Contact_Info(display_name, data1, contact_id)
			duplicate_contact_dict[(display_name, data1)].append(contact_obj)

		return duplicate_contact_dict

	def get_duplicate_contact_dict(self, duplicate_contact_dict):
		'''
		1) Iterate through contact_dict
		2) if length of value_list for any key in dict is > 1 then that contact is duplicate contact.
                   Example: {("Abhijeet", "99999999999"):[obj1, obj2]}
			    In above dict list length is > 1 i.e for "Abhijeet" two same contacts are stored which is duplicate contact.
		3) Add all duplicate contact object in duplicate_contact_list 	
		'''
		duplicate_contact_list = []
		duplicate_contacts = []
		for key in duplicate_contact_dict:
			#data1 = duplicate_contact_dict[key].keys()[0]
			if len(duplicate_contact_dict[key]) > 1:
				duplicate_contact_list.extend(duplicate_contact_dict[key])
				print "key -- %s value -- %s"%(key, duplicate_contact_dict[key])
				duplicate_contacts.append(key)
		print "Total Duplicate Contacts ----%s"%len(duplicate_contacts)
		return duplicate_contact_list

	def display_contacts(self, contact_list):
		
		list_view_list = ["%s %s"%(contact.name, contact.phone_number) for contact in contact_list]
		with open(LAYOUT_FILE_NAME, "r") as f:
			layout = f.read()
		
		self.droid.fullShow(layout)
		
		self.droid.fullSetList("contactlist", list_view_list)
		self.contact_listview_eventLoop(contact_list)
	
	def contact_listview_eventLoop(self, contact_list):
		#Loop to monitor listview events
		while True:
                        result=self.droid.eventWait().result
                        print result
                        if result["name"]=="key":
                                id=result["data"]["key"]
                                if id == "4":
                                        self.droid.fullDismiss()
                                        #self.droid.close()
                                        return
			elif result["name"]=="click":
				id = result["data"]["id"]
				if id == "button1":
					#Call Function which display all contacts
					pass
				elif id == "button3":
					#Call Function to refresh list
					self.droid.fullDismiss()
					return
			elif result["name"] == "itemclick":
				id = result["data"]["position"]
				self.display_contacts_for_id(contact_list[int(id)])

	def display_contacts_for_id(self, contact_obj):
		#Get Contact id
		contact_id = contact_obj.contact_id
		#Query Contacts for given Contact id
		selection = "contact_id=?"
		args = [contact_id]
		
		result = self.droid.queryContent(QUERY, COLUMNS, selection, args).result
		msg = ",".join([contact_dict["data1"] for contact_dict in result])
		self.droid.makeToast(msg)
		return


if __name__ == "__main__":
	cnt=0
	contact_obj=Contacts_Base()
	contact_obj.query_contact_list()
	duplicate_contact_dict=contact_obj.set_duplicate_contact_list()
	duplicate_contact_list = contact_obj.get_duplicate_contact_dict(duplicate_contact_dict)
	contact_obj.display_contacts(duplicate_contact_list)
	print "Total Contacts:----%s"%len(duplicate_contact_dict.keys())
	'''
	duplicate_contact_dict=contact_obj.get_contact_with_multiple_numbers()
	for contact_id, contact_list in duplicate_contact_dict.iteritems():
		if len(contact_list) > 1 and re.search(r"^%s"%sys.argv[1], contact_list[0]["display_name"], re.I):
			print contact_list			
	'''	
