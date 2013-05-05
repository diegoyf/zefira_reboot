import pymongo 


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

		import base64, uuid
		#Revisa el branch y ejecuta de acuerdo a su resultado

		if branch  == "companies":
			new_user = {
				'_id':"comp"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'username': request_args['username'][0],
                'password': request_args['password'][0],
                'info' : {
                    'name': request_args['name'][0],
                    'description': request_args['description'][0],
                    'email' : request_args['email'][0],                    },
                'benefits' : []
                }
			self.db.companies.save(new_user)
			return "/cbox"

		elif branch == "clientes" :
			new_user = {
				'_id':"user"+base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
                'username' : request_args['username'][0],
                'password': request_args['password'][0],
                'info':{
                	'email': request_args['email'][0],
                	'name' : request_args['nombre'][0],
                	'last_name': request_args['apellido'][0]
                	},
                'interests': [],
                'reserves' : [],
                'session' : {'benefits': []}
                }
			self.db.users.save(new_user)
			return "/box"
		else:
			return "/error"

    #Funcion obtiene informacion usuario, depende del BaseHandler
        	
	def fetch_user(self,username,password,branch):
		try:
			if branch == "clientes":
				user = self.db.users.find_one({'username':username})
			else:
				branch == "companies"
				user = self.db.companies.find_one({"username":username})
			if user['password'] == password:

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