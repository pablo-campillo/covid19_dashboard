# Created by Pablo Campillo at 10/1/22

import pandas as pd
import pathlib


class VaccinationData:
    target_group_list = ['Age00_04', 'Age05_09', 'Age10_14', 'Age15_17', 'Age18_24',
                     'Age25_49', 'Age50_59', 'Age60_69', 'Age70_79', 'Age80+']

    def __init__(self):
        self.file_path = pathlib.Path(__file__).parent.resolve() / 'data/vaccination.csv'
        self.df = None
        self.data = None

    def load_online(self):
        self.df = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/vaccine_tracker/csv/data.csv')
        return self.df

    def save(self):
        self.df.to_csv(self.file_path, index=False)

    def load_file(self):
        self.df = pd.read_csv(self.file_path)
        return self.df

    def preprocess(self):
        self.df['TargetGroup'].replace({'Age0_4': 'Age00_04', 'Age5_9': 'Age05_09'}, inplace=True)

        self.data = self.df[self.df['TargetGroup'].isin(self.target_group_list) &
                            (self.df['ReportingCountry'] == self.df['Region'])].copy()

        self.data[['Year', 'Week']] = self.data['YearWeekISO'].str.split('-', expand=True)
        self.data['Year'] = pd.to_numeric(self.data['Year'])
        self.data['Week'] = pd.to_numeric(self.data['Week'].str[1:])

        self.data['ReportingCountry'] = self.data['ReportingCountry'].astype('category')
        self.data['Region'] = self.data['Region'].astype('category')

        self.data['Vaccine'] = self.data['Vaccine'].astype('category')
        self.data['TargetGroup'] = self.data['TargetGroup'].astype('category')

        self.data['Date'] = pd.to_datetime(self.data.Week.astype(str) +
                                           self.data.Year.astype(str).add('-1'), format='%V%G-%u')

        self.data = self.data.groupby(by=['YearWeekISO', 'ReportingCountry', 'Vaccine', 'TargetGroup']).agg({
            'NumberDosesReceived': 'sum',
            'NumberDosesExported': 'sum',
            'FirstDose': 'sum',
            'FirstDoseRefused': 'sum',
            'SecondDose': 'sum',
            'DoseAdditional1': 'sum',
            'UnknownDose': 'sum',
            'Denominator': 'last',
            'Population': 'last',
            'Year': 'last',
            'Week': 'last',
            'Date': 'last'
        }).reset_index()

        self.data['Vaccine'] = self.data['Vaccine'].replace({
            'AZ': 'AstraZeneca',
            'BECNBG': 'Beijing',
            'BHACOV': 'Covaxin',
            'COM': 'Pfizer',
            'MOD': 'Moderna',
            'JANSS': 'Janssen',
            'SPU': 'Sputnik V',
            'UNK': 'Unknown'
        }).astype('category')

        self.data['FirstDosePercent'] = (self.data['FirstDose'] / self.data['Denominator']) * 100
        self.data['SecondDosePercent'] = (self.data['SecondDose'] / self.data['Denominator']) * 100
        self.data['DoseAdditional1Percent'] = (self.data['DoseAdditional1'] / self.data['Denominator']) * 100

        return self.data

