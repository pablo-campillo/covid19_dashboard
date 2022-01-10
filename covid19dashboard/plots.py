# Created by Pablo Campillo at 10/1/22

from bokeh.transform import dodge
from bokeh.plotting import figure
from bokeh.palettes import Colorblind, Set1
from bokeh.models import CDSView, ColumnDataSource, GroupFilter, FactorRange, Legend, HoverTool

from .controllers import Observer, CountrySelector, DateRageSelector
from .data_helper import VaccinationData


class PercentageDosePerAgeGroupAndVaccineType(Observer):

    target_data = ['FirstDosePercent', 'SecondDosePercent', 'DoseAdditional1Percent']

    def __init__(self, data: VaccinationData):
        self.plot = None
        self.start_date = None
        self.end_date = None
        self.vaccination_data = data
        self.country_id = 'ES'
        self.vaccine_types = self.vaccination_data.data['Vaccine'].unique().tolist()
        self._compute_data()

    def _compute_data(self):
        aux = self.vaccination_data.data
        if self.start_date is not None and self.end_date is not None:
            aux = aux[(aux.Date >= self.start_date) & (aux.Date < self.end_date)]
        else:
            aux = self.vaccination_data.data
        self.data = aux[['ReportingCountry', 'TargetGroup', 'Vaccine'] + self.target_data].groupby(
            by=['ReportingCountry', 'TargetGroup', 'Vaccine']).sum().stack().reset_index()
        self.data.rename(columns={'level_3': 'DoseType', 0: 'Percentage'}, inplace=True)
        self.data = self.data.pivot(index=['ReportingCountry', 'TargetGroup', 'DoseType'], columns='Vaccine',
                        values='Percentage').reset_index()
        self.data['factor'] = list(zip(self.data.TargetGroup, self.data.DoseType))

    def _recompute_source(self):
        self._compute_data()
        self.source.data = self.data

    def build(self):
        self.source = ColumnDataSource(data=self.data)

        self.country_filter = GroupFilter(column_name='ReportingCountry', group=self.country_id)
        self.view = CDSView(source=self.source, filters=[self.country_filter])

        factors = self.data[self.data['ReportingCountry'] == 'ES'].factor

        regions = self.vaccine_types

        self.source = ColumnDataSource(data=self.data)

        self.country_filter = GroupFilter(column_name='ReportingCountry', group=self.country_id)
        self.view = CDSView(source=self.source, filters=[self.country_filter])

        self.plot = figure(x_range=FactorRange(*factors), height=600, width=1200,
                   toolbar_location="below", tools="pan,wheel_zoom,box_zoom,reset")
        self.plot.add_layout(Legend(), 'right')

        renderers = self.plot.vbar_stack(regions, x='factor', width=0.9, alpha=0.5,
                                         color=Set1[len(self.vaccine_types)],
                                         source=self.source, view=self.view, legend_label=regions)
        for r in renderers:
            vaccine_type = r.name
            hover = HoverTool(tooltips=[
                (f"%s" % vaccine_type, "@%s" % vaccine_type)
            ], renderers=[r])
            self.plot.add_tools(hover)

        self.plot.y_range.start = 0
        self.plot.y_range.end = 100
        self.plot.x_range.range_padding = 0.1
        self.plot.xaxis.major_label_orientation = "vertical"
        self.plot.xgrid.grid_line_color = None

        return self.plot

    def update(self, observable) -> None:
        if isinstance(observable, CountrySelector):
            self.country_id = observable.value
            self.view.filters[0] = GroupFilter(column_name='ReportingCountry', group=self.country_id)
        elif isinstance(observable, DateRageSelector):
            self.start_date = observable.start_date
            self.end_date = observable.end_date
            self._recompute_source()


class PercentageDosePerAgeGroup(Observer):

    def __init__(self, data: VaccinationData):
        self.plot = None
        self.vaccination_data = data
        self.country_id = 'ES'
        target_data = ['FirstDosePercent', 'SecondDosePercent', 'DoseAdditional1Percent']
        self.data = self.vaccination_data.data.groupby(by=['ReportingCountry', 'TargetGroup'])[target_data].sum().reset_index()

    def build(self):
        source = ColumnDataSource(data=self.data)

        self.country_filter = GroupFilter(column_name='ReportingCountry', group=self.country_id)
        self.view = CDSView(source=source, filters=[self.country_filter])

        self.plot = figure(x_range=self.vaccination_data.target_group_list, y_range=(0, 100), height=300,
                   title=f"Percentage of dose per Age group of {self.country_id}", toolbar_location=None, tools="")

        self.plot.vbar(x=dodge('TargetGroup', -0.25, range=self.plot.x_range), top='FirstDosePercent', width=0.2, source=source,
               color="#c9d9d3", legend_label="FirstDosePercent", view=self.view)

        self.plot.vbar(x=dodge('TargetGroup',  0.0,  range=self.plot.x_range), top='SecondDosePercent', width=0.2, source=source,
               color="#718dbf", legend_label="SecondDosePercent", view=self.view)

        self.plot.vbar(x=dodge('TargetGroup',  0.25, range=self.plot.x_range), top='DoseAdditional1Percent', width=0.2, source=source,
               color="#e84d60", legend_label="DoseAdditional1Percent", view=self.view)

        self.plot.x_range.range_padding = 0.1
        self.plot.xgrid.grid_line_color = None
        self.plot.legend.location = "top_left"
        self.plot.legend.orientation = "vertical"
        return self.plot

    def update(self, observable: CountrySelector) -> None:
        self.country_id = observable.value
        self.view.filters[0] = GroupFilter(column_name='ReportingCountry', group=self.country_id)
