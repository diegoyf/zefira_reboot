import tornado.web

""" Clase que presenta la pagina de inicio
 Tipo Request: GET """

class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render(
            "index.html",
            page_title = "Zefira v-1.0 | Home",
            header_text = "Bienvenidos a Zefira",
            
            )

"""Clase presenta pagina principal area Personas
Tipo Request: GET """

class PersonasHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "clientes.html",
            page_title="Zefira | Clientes",
            header_text = "Zefira Clientes"
            )

"""Clase presente pagina principal area Empresas
tipo Request: GET """        

class EmpresasHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "empresas.html",
            page_title="Zefira | Empresas",
            header_text=" Zefira Empresas"
            )


