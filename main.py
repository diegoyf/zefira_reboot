"""Zefira application v1.0 """

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.gen
import os.path
import datetime
import uimodules
import requesthandlers
import logging


from tornado.options import define, options
from datamanag import DataManagement
from activity import ActivityMixin

define("port", default = 8000, help= "run on given port", type=int)

"""*************************************************************************
Application: Clase principal que inicializa los handlers e inicia la conexion 
con la base de datos. Ademas, asigna los modulosUI, los paths para los archivos
estaticos, templates, y otras settings de seguridad y cookies.

************************************************************************"""


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", requesthandlers.MainHandler),
            (r"/personas", requesthandlers.PersonasHandler),
            (r"/empresas", requesthandlers.EmpresasHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/signup", SignUpHandler),
            (r"/box", BoxHandler),
            (r"/cbox", CBoxHandler),
            (r"/publish", PublishBenefitHandler),
            (r"/activity", ActivityHandler),
            (r"/reserve", ReserveHandler),
            (r"/validate", ValidationHandler),
            (r"/companies", BrandsHandler),
            (r"/follow", FollowHandler),
            (r"/more-posts", MorePostsHandler)
           
            #(r"/error", requesthandlers.ErrorHandler)
            ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            ui_modules={
                "Benefit" : uimodules.BenefitModule,
                "BenefitCo": uimodules.BenefitCoModule,
                "Company" : uimodules.CompanyModule,  
             } ,         
            debug = True,
            cookie_secret = "0azgrztWSuenSRWevq9GAOp/4bDtSET0q8YII0ZfLDc=",
            login_url = "/login",
            xsrf_cookies = True,
            autoescape = None,
        )
        
        self.dataManager = DataManagement("zefira")
        self.ActivityMix = ActivityMixin() 
        tornado.web.Application.__init__(self, handlers, **settings)

""" Clase base de toda la autenticacion de la pagina. """

class BaseHandler(tornado.web.RequestHandler):
    
    #Decorador que retorna una instancia de la clase administrador
    #para ser utilizada por la aplicacion
    @property
    def data_manager(self):
        return self.application.dataManager
    @property

    def activitymix(self):
        return self.application.ActivityMix

    #Funcion que utiliza los parametros seguros de LoginHandler para
    #llamar el usuario y retornar una array con su informacion
    def get_current_user(self):
        user_id  = self.get_secure_cookie("email")
        password = self.get_secure_cookie("password")
        branch = self.get_secure_cookie("branch")
        
        user = self.application.dataManager.fetch_user(user_id, password, branch)
        if user:
            return user
        else:
            self.set_status(404)


""" Clase que maneja el ingreso a la pagina """

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html",
                    page_title ="Zefira | Login",
                    header_text= "Ingresa a Zefira",  
                    )
    def post(self):

        
        self.set_secure_cookie("email", self.get_argument("email"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.set_secure_cookie("branch", self.get_argument("branch"))
        if self.get_argument("branch") == "companies":
            self.redirect("/cbox")
        else:
            self.redirect("/box")

""" Clase que se encarga del borrado de cookies y la salida de 
la aplicacion """

class LogoutHandler(BaseHandler):
    def get(self):
        
        self.clear_cookie("email")
        self.clear_cookie("password")
        self.clear_cookie("branch")
        self.redirect("/")

""" Clase que se encarga de la creacion de usuarios
Tipo Request: POST"""
class SignUpHandler(BaseHandler):
    def post(self):

        branch = self.get_argument("branch")
        self.set_secure_cookie("email", self.get_argument("email"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.set_secure_cookie("branch", self.get_argument("branch"))
        self.redirect(self.data_manager.create_user(branch,self.request.arguments))

"""Clase que maneja la presentacion del layout principal de 
 la aplicacion en el area de los clientes Tipo Request: GET"""       


class BoxHandler(BaseHandler):

    def get(self):
        import datetime

        interests = self.current_user['interests']

        benefits= self.data_manager.fetch_benefits_usr(interests, self.current_user,self.current_user['location'], cursor = None)
        
        companies = self.data_manager.fetch_companies(self.current_user['location'],interests)
        
        cursor = benefits[-1]['_id']            
        self.render(
                "box.html",
                page_title = "Zefira | Inicio",
                header_text = "Box",
                benefits = benefits,
                companies = companies,
                cursor = cursor
                
                )

class MorePostsHandler(BaseHandler):
    def get(self):
        import json
        import urllib
        interests = self.current_user['interests']
        cursor = urllib.unquote(self.get_argument("cursor", None))
        more_posts = self.data_manager.fetch_benefits_usr(
            interests, self.current_user, self.current_user['location'], cursor) 
        more_posts.append({'cursor': more_posts[-1]['_id']}) 
        logging.info(more_posts)
        
        self.write(json.dumps(more_posts)) 
"""Clase que maneja la presentacion del layout principal de 
la aplicacion en el area de las empresas """

class CBoxHandler(BaseHandler):
    def get(self):
        benefits_published = self.current_user['benefits']
        
        
        if len(benefits_published) == 0 or benefits_published == None : 
            benefits_deref = None
        else:

            benefits = self.data_manager.fetch_benefits_cmp(
                benefits_published)

            
              

        self.render(
            "cbox.html",
            page_title = "Zefira | Company Box",
            benefits = benefits,
            company_id = self.current_user['_id']
            )


"""Handler que administra la publicacion de beneficios"""

class PublishBenefitHandler(BaseHandler):
    def post(self):
        if self.data_manager.publish_benefit(self.request.arguments, 
            self.current_user):
            self.redirect("/cbox")
        else:
            self.redirect("/error")


class ReserveHandler(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
       
        action = self.request.arguments['action'][0]
        company_id = self.request.arguments['company_id'][0]
        benefit_id = self.request.arguments['benefit_id'][0]
        self.activitymix.update_queue(benefit_id,company_id)


"""Clase que maneja las respuestas  de la actividad de una empresa"""  

class ActivityHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        import json
        cursor = 0
        company = self.get_argument("company_id")
        self.activitymix.fetch_queue(self.on_updates,company)
        
            
    def on_updates(self, data, confirm_id, company_id) :
        if self.request.connection.stream.closed():
            return
        if confirm_id == company_id:    
            self.finish(data)   
        
        else:
            pass

"""Clase que maneja la validacion de usuarios y correos"""

class ValidationHandler(BaseHandler):
    def post(self):
        branch = self.get_argument("branch")
        response = self.data_manager.validate_email(self.get_argument("email"), branch)
        logging.info(response)
        self.write(str(response))

class BrandsHandler(BaseHandler):
    def get(self):
        interests = self.current_user['interests']
        companies = self.data_manager.fetch_companies(interests)
        self.render(
            "copres.html",
            page_title = "Zefira | Lista Marcas",
            companies = companies
            )
class FollowHandler(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        import json
        company_id = self.get_argument("company_id")
        action = self.get_argument("action")
        self.data_manager.update_follow(company_id, 
            self.current_user ,action, self.on_response)
        

    def on_response(self):
        if self.request.connection.stream.closed():
            return
            
        self.finish()    
        
class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        import json
        from tornado.escape import json_encode
        doc = {
        "products": [
        {
            "pid": "1",
            "name": "iPhone 4S",
            "price": "300.00",
            "created_at": "2012-04-29 02:04:02",
            "updated_at": "0000-00-00 00:00:00"
        },
        {
            "pid": "2",
            "name": "Macbook Pro",
            "price": "600.00",
            "created_at": "2012-04-29 02:04:51",
            "updated_at": "0000-00-00 00:00:00"
        },
        {
            "pid": "3",
            "name": "Macbook Air",
            "price": "800.00",
            "created_at": "2012-04-29 02:05:57",
            "updated_at": "0000-00-00 00:00:00"
        },
        {
            "pid": "4",
            "name": "OS X Lion",
            "price": "100.00",
            "created_at": "2012-04-29 02:07:14",
            "updated_at": "0000-00-00 00:00:00"
        }
        ],
    "success": 1
    }
        
        self.write(json_encode(doc))

"""Funcion principal que levanta la aplicacion """

def main():
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

