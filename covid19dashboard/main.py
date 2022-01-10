from bokeh.layouts import column, row

from bokeh.plotting import curdoc

from .controllers import CountrySelector, DateRageSelector
from .data_helper import VaccinationData
from .plots import PercentageDosePerAgeGroup, PercentageDosePerAgeGroupAndVaccineType

vaccination_data = VaccinationData()
vaccination_data.load_file()
vaccination_data.preprocess()

# percet_dose = PercentageDosePerAgeGroup(vaccination_data)
# plot = percet_dose.build()
percet_dose = PercentageDosePerAgeGroupAndVaccineType(vaccination_data)
plot = percet_dose.build()


country_controller = CountrySelector(vaccination_data)
country_controller.attach(percet_dose)
country_selector = country_controller.build()

date_range_controller = DateRageSelector(vaccination_data)
date_range_controller.attach(percet_dose)
date_range_selector = date_range_controller.build()

curdoc().add_root(column(row(date_range_selector, country_selector), plot, name="app_content"))
