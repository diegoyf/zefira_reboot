"""Zefira application v1.0 """

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import os.path
import datetime
import uimodules
import requesthandlers

from tornado.options import define, options
from datamanag import DataManagement

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
            #(r"/publish", requesthandlers.PublishHandler),
            #(r"/companies", requesthandlers.CompaniesHandler),
            #(r"/error", requesthandlers.ErrorHandler)
            ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            ui_modules={
                "Benefit" : uimodules.BenefitModule,
                "BenefitCo": uimodules.BenefitCoModule,
             #   "Company" : uimodules.CompaniesModule},  
             } ,         
            debug = True,
            cookie_secret = "0azgrztWSuenSRWevq9GAOp/4bDtSET0q8YII0ZfLDc=",
            login_url = "/login",
            xsrf_cookies = True,
            autoescape = None,
        )
        
        self.dataManager = DataManagement("zefira")
        
        tornado.web.Application.__init__(self, handlers, **settings)

""" Clase base de toda la autenticacion de la pagina. """

class BaseHandler(tornado.web.RequestHandler):
    
    #Decorador que retorna una instancia de la clase administrador
    #para ser utilizada por la aplicacion
    @property
    def data_manager(self):
        return self.application.dataManager
    

    #Funcion que utiliza los parametros seguros de LoginHandler para
    #llamar el usuario y retornar una array con su informacion
    def get_current_user(self):
        user_id  = self.get_secure_cookie("username")
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

        
        self.set_secure_cookie("username", self.get_argument("username"))
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
        
        self.clear_cookie("username")
        self.clear_cookie("password")
        self.clear_cookie("branch")
        self.redirect("/")

""" Clase que se encarga de la creacion de usuarios
Tipo Request: POST"""
class SignUpHandler(BaseHandler):
    def post(self):

        branch = self.get_argument("branch")
        self.set_secure_cookie("username", self.get_argument("username"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.set_secure_cookie("branch", self.get_argument("branch"))
        self.redirect(self.data_manager.create_user(branch,self.request.arguments))

"""Clase que maneja la presentacion del layout principal de 
 la aplicacion en el area de los clientes Tipo Request: GET"""       


class BoxHandler(BaseHandler):

    def get(self):
        interests = self.current_user['interests']

        benefits = self.data_manager.fetch_benefits_usr(interests, self.current_user)
        
        self.render(
                "box.html",
                page_title = "Zefira | Inicio",
                header_text = "Box",
                benefits = benefits,
                )

"""Clase que maneja la presentacion del layout principal de 
la aplicacion en el area de las empresas """

class CBoxHandler(BaseHandler):
    def get(self):
        benefits_published = self.current_user['benefits']
        if len(benefits_published) == 0 or benefits_published == None : 
            benefits_deref = None
        else:
            benefits_deref = self.data_manager.fetch_benefits_cmp(
                benefits_published) 
        self.render(
            "cbox.html",
            page_title = "Zefira | Company Box",
            benefits = benefits_deref)


"""Funcion principal que levanta la aplicacion """

def main():
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

