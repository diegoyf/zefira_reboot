import pymongo 
import asyncmongo
import memcache

""" Clase que provee todas las funciones de administracion de
datos de toda la aplicacion """ 

class DataManagement():

	#Funcion de inicio de la clase
	#Un parametro: string nombre de la base de datos
	def __init__(self,database):

		if database == "zefira":

			conn = pymongo.Connection("localhost", 27017)
			self.db = conn.zefira

	#Creacion de usuarios		
	def create_user(self, branch, request_args):

		import base64, uuid, hashlib
		#Revisa el branch y ejecuta de acuerdo a su resultado
		self.salt = "2937abbc079c45a2b8ef58ee4943e9dd"
		if branch  == "companies":
			new_user = {
				'_id':"comp"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'email': request_args['email'][0],
                'password': hashlib.sha512(request_args['password'][0] + self.salt).hexdigest(),
                'info' : {
                    'name': request_args['nombre'][0],
                    'description': request_args['description'][0],
                    'address' : ''
                    },
                'benefits' : []
                }
			self.db.companies.save(new_user)
			return "/cbox"

		elif branch == "clientes" :
			new_user = {
				'_id':"user"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'email': request_args['email'][0],
                'password':hashlib.sha512(request_args['password'][0] + self.salt).hexdigest(),
                'profile':{
                	'first_name' : request_args['nombre'][0],
                	'last_name': request_args['apellido'][0],
                	
                	},
                'interests': [],
                'reserves' : [],
                
                }
			self.db.users.save(new_user)
			return "/box"
		else:
			return "/error"

    #Funcion obtiene informacion usuario, depende del BaseHandler
        	
	def fetch_user(self,email,password,branch):
		import hashlib
		self.salt = "2937abbc079c45a2b8ef58ee4943e9dd"
		hashed_pass = hashlib.sha512(password + self.salt).hexdigest()
		try:
			if branch == "clientes":
				user = self.db.users.find_one({'email':email})
			else:
				branch == "companies"
				user = self.db.companies.find_one({"email":email})
			

			if user['password'] == hashed_pass:
				return user
			else:
				raise Exception
		except:
			return None


	#Funcion que utiliza el nombre de usuario para llamar todos sus
	#beneficios y reservas

	def fetch_benefits_usr(self,interests_ref, user):
		companies_followd = []
		benefits_dref = []
		benefits = []

		if len(interests_ref) == 0: 
			return None
		else:
			for i in interests_ref[:7]:
				companies_followd.append(self.db.dereference(i))
			for j in range(len(companies_followd)):
				for i in range(len(companies_followd[j]['benefits'])):
					benefits_dref.append(companies_followd[j]['benefits'][i])
		for i in benefits_dref:
			benefits.append(self.db.dereference(i))

		reserves = user['reserves']
		if len(reserves) == 0 :
			for i in benefits:
				i['message'] = "Reservar" 
		else:
			reserves_dref = []
			for i in range(len(reserves)):
				reserves_dref.append(self.db.dereference(reserves[i]))
			for i in benefits:
				if i in reserves_dref:
					i['message'] = "Reservado"
				else:
					i['message'] = "Reservar"
		return benefits

	#Funcion que utiliza el nombre de usuario  empresa para llamar
	#beneficios

	def fetch_benefits_cmp(self, benefits_ref):

		benefits_deref = []
		if not benefits_ref:
			return None
		for i in range(len(benefits_ref)):
			benefits_deref.append(self.db.dereference(benefits_ref[i]))
		return benefits_deref

	#Funcion que se encarga de la publicacion de beneficios

	def publish_benefit(self, request_args, user):
		import base64, uuid
		import datetime
		benefit = {
			"_id":"bene"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "title":request_args['title'][0],
            "description": request_args['description'][0],
            "company_name": user['info']['name'],
            'date_published' : datetime.datetime.now(),
            'active': True,
            'dates_reserved': [],
            'dates_validated': [],
            'times_reserved': 0,
            'times_validated': 0 ,
            #'picture_id': '',
            'benefit_type' :request_args['benefit_type'][0],
		}

		from bson.dbref import DBRef
		if self.validate(benefit):
			self.db.benefits.save(benefit)
			user['benefits'].append(DBRef('benefits', benefit["_id"]))
			self.db.companies.save(user)
			return True
		else:
			return False

	def validate(self,data):
		branch= data['_id'][:4]

		if branch == 'bene':

			if not self.db.benefits.find_one({'_id': data['_id']}):
				return True
			else:
				return False
		elif branch == "comp":
			if not self.db.companies.find_one({'_id':data['_id']}):
				return True
			else:
				return False
		else:
			if not self.db.users.find_one({'_id': data['_id']}):
				return True
			else:
				return False

	def validate_email(self, email, branch):
		if len(email) == 0:
			return 0
		if branch == "clientes":
			if self.db.users.find_one({'email': email}):
				return 0
			else:
				return 1
		else:
			if self.db.companies.find_one({'email': email}):
				return  0
			else:
				return 1


	def update_activity_queue(self, action,company_id, benefit_id):
		from bson.dbref import DBRef 

		company = self.db.company_queue.find_one({'_id': company_id})
		dbref_obj = DBRef('benefits', benefit_id)
		if action == "reserve":
			company['queue'].append(dbref_obj)
		else: 
			if dbref_obj in company['queue']:
				for i in range(len(company['queue'])):
					if company['queue'][i] == dbref_obj:
						company['queue'].pop(i)
						break
					else: 
						pass	 


		self.db.company_queue.save(company)
		return None

	def fetch_activity_queue(self,company_id):
			record = self.db.company_queue.find_one({'_id':company_id }, limit = 10)
			benefits = []
			if len(record['queue']) == 0:
				return record['queue']
			else:	
				for i in record['queue']:
					benefits.append(self.db.dereference(i))
				return benefits		 		

 	def fetch_companies(self, user_location, user_companies):
 		companies = []
 		if len(user_companies) == 0:
 			for i in self.db.companies.find({'location': user_location}, limit=10):
 				companies.append(i) 
 			for i in range(len(companies)):
 				companies[i]['message'] = "Seguir"
 			return companies
		else:
			for i in self.db.companies.find(limit=10):
				companies.append(i)
			ref = []
			for i in user_companies:
				ref.append(self.db.dereference(i))	

			for i in companies:
				if i in ref:
					i['message'] = "Siguiendo"
				else:
					i['message'] = "Seguir"	
		return companies			

	def update_follow(self, company_id, user, action, callback):
		from bson.dbref import DBRef
		dbref_obj = DBRef('companies', company_id)
 		if action == "seguir":
 			user['interests'].append(dbref_obj)

 		else : 
 			for i in range(len(user['interests'])):
 				if user['interests'][i] == dbref_obj:
 					del user['interests'][i]
 					break
 		self.db.users.save(user)			
 		callback()
