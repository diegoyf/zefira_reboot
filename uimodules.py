import tornado.web

class BenefitModule(tornado.web.UIModule):
	def render(self, benefit):
		return self.render_string(
			"modules/benefit.html",
			benefit = benefit,
			)


class BenefitCoModule(tornado.web.UIModule):
	def render(self,benefit):
		return self.render_string(
			"modules/benefitco.html",
			benefit = benefit,
			)

class CompanyModule(tornado.web.UIModule):
	def render(self,company):
		return self.render_string(
			"modules/company.html",
			company = company
			)