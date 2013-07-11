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

	def fetch_benefits_usr(self,interests_ref, user, location, cursor):

		benefits_id = []
		

		if cursor:
			last = None
			cr = self.db.global_feed.find({'location': location}).sort('date-created',pymongo.DESCENDING) 
			count_base = 0
			for entry in cr:
				if entry['_id'] == cursor:
					last = entry
					count_base += 1
					break
				else:
					count_base += 1

			cursor = self.db.global_feed.find({'location': location}, skip = count_base).sort('date-created',pymongo.DESCENDING) 


			count = 0
			for entry in cursor:
				if entry['from']['_id'] in interests_ref:
					benefits_id.append(entry['_id'])
					count += 1
					if count == 5:
						break

		else:

			count= 0
			batch = self.db.global_feed.find({'location': location}).sort('date-created', pymongo.DESCENDING)	
					
			for entry in batch:
				if entry['from']['_id'] in interests_ref:
					benefits_id.append(entry['_id'])
					count += 1
					if count == 5:
						break

							
				

		benefits = []

		for i in benefits_id:
			benefits.append(self.db.benefits.find_one({'_id': i}))

		reserves = user['reserves']

		if len(reserves) == 0 :
			for i in benefits:
				i['message'] = "Reservar" 
		else:
			for i in benefits:
				if i['_id'] in reserves:
					i['message'] = "Reservado"
				else:
					i['message'] = "Reservar"
		return benefits

	#Funcion que utiliza el nombre de usuario  empresa para llamar
	#beneficios
	def fetch_benefits_cmp(self, benefits):

		benefits_ret = []
		if not benefits:
			return None
		for i in benefits:
			benefits_ret.append(self.db.benefits.find_one({'_id':i}))
		return benefits_ret

	#Funcion que se encarga de la publicacion de beneficios

	def publish_benefit(self, request_args, user):
		import base64, uuid
		import datetime
		benefit = {
			"_id":"bene"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "title":request_args['title'][0],
            "description": request_args['description'][0],
            "from": {
            	'id' : user['_id'],
            	'name': user['name']
            },
            'date_published' : '',
            'active': True,
            'reserves': {
            	'data' : [],
            	'count' : 0  
            	}
            ,
            'validations': {
            	'data': [],
            	'count': 0 },

            'benefit_type' :request_args['benefit_type'][0],
		}

		feed = {
			'_id': benefit['_id'],
			'location': {
				'name': user['location']['name']
			},
			'from': {
				'_id': user['_id'],
				'name': user['name']
			} 
		}

		
		if self.validate(benefit):
			self.db.benefits.insert(benefit)
			self.db.global_feed.insert(feed)
			user['benefits'].append(benefit['_id'])
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

			for i in companies:
				if i['_id'] in user_companies:
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
