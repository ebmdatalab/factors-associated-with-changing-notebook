import pandas as pd
from ebmdatalab import bq
import fingertips_py as ft


phe_indicators = [
'Deprivation score (IMD 2015)',
'% who have a positive experience of their GP practice',
'% with a long-standing health condition',
'% aged 65+ years',
'% aged under 18 years'
]

def phe_data():
	"""
	- previously used a csv file
	- now gets data from PHE fingertips python package
	documented here:
	https://fingertips-py.readthedocs.io/en/latest/index.html
	"""
	def get_from_phe(name, IndicatorId):
		df = ft.retrieve_data.get_data_by_indicator_ids(IndicatorId,7)
		#get most recent year
		max_year = df['Time period'].max()
		df = df.loc[df['Time period'] == max_year]
		df = df[['Area Code','Value']]
		df = df.rename(columns={'Value': name})
		return df.set_index('Area Code')

	lookup = ft.retrieve_data.get_all_areas_for_all_indicators()
	lookup = lookup.loc[lookup['AreaTypeId']==7]
	lookup = lookup.set_index('IndicatorName')['IndicatorId']
	df = pd.DataFrame()
	for indicator in phe_indicators:
		series = get_from_phe(indicator, lookup.loc[indicator])
		df = df.join(series,how='outer')
	return df


def qof():
	"""
	Uses data from this zipped file:
	https://files.digital.nhs.uk/A8/491BAC/QOF_1819_v2.zip
	Found here:
	https://digital.nhs.uk/data-and-information/publications/statistical/quality-and-outcomes-framework-achievement-prevalence-and-exceptions-data/2018-19-pas
	"""
	df = pd.read_csv('data/ACHIEVEMENT_1819.csv')
	qof_map = pd.read_csv('data/INDICATOR_MAPPINGS_1819_v2.csv')
	df = df.merge(qof_map[['INDICATOR_CODE','DOMAIN_CODE']], how='inner', on='INDICATOR_CODE', copy=False)
	df = df.loc[df['MEASURE'] == 'ACHIEVED_POINTS'].groupby(['PRACTICE_CODE','DOMAIN_CODE']).sum()
	df = df.unstack(level=1) #.reset_index(col_level=0)
	df.columns = df.columns.droplevel(0)
	df['QOF_TOTAL'] = df['CL'] + df['PH'] + df['PHAS']
	return df

def gps_per_practice():
	"""
	Data from:
	https://files.digital.nhs.uk/A2/457C00/GPWPracticeCSV.0919.zip
	Found here:
	https://digital.nhs.uk/data-and-information/publications/statistical/general-and-personal-medical-services/final-30-september-2019
	https://digital.nhs.uk/data-and-information/publications/statistical/general-and-personal-medical-services
	"""
	df = pd.read_csv('data/General Practice September 2019 Practice Level.csv')
	return df[['PRAC_CODE','TOTAL_GP_HC']].set_index('PRAC_CODE')


###### Data from BigQuery ######

def practice_data():
	q = '''
	SELECT
	  DISTINCT practice,
	  pct
	FROM
	  ebmdatalab.hscic.normalised_prescribing_standard
	LEFT JOIN
	  ebmdatalab.hscic.practices
	ON
	  practice = code
	  AND setting = 4
	ORDER BY
	  practice
	'''
	df = bq.cached_read(q, csv_path='data/cached_practice.csv')
	return df.set_index('practice')

def dispensing():
	q = '''
	SELECT
	  code,
	  dispensing_patients
	FROM
	  ebmdatalab.bsa.dispensing_practices_jan2017
	ORDER BY
	  code ASC
	'''
	df = bq.cached_read(q, csv_path='data/cached_dispensing.csv')
	return df.set_index('code')

def prescribing_volume(year=2018):
	q = f'''
	SELECT
	  practice,
	  SUM(items) AS total_items
	FROM
	  ebmdatalab.hscic.normalised_prescribing_standard
	WHERE
	  month >= TIMESTAMP("{year}-01-01")
	  AND month <= TIMESTAMP("{year}-12-01")
	GROUP BY
	  practice
	'''
	df =  bq.cached_read(q, csv_path='data/cached_prescribing_volume.csv')
	return df.set_index('practice')


def urban_rural():
	q = '''
	SELECT
	  code AS practice, ru.LSOA11NM, SUBSTR(RUC11CD,1,1) AS ruc11cd, RUC11
	FROM
	  ebmdatalab.ONS.small_area_rural_urban ru
	INNER JOIN
	  ebmdatalab.ONS.postcode_to_lsoa_map m
	ON
	  ru.LSOA11CD = m.lsoa11cd
	INNER JOIN
	  ebmdatalab.hscic.practices
	ON
	  pcds = postcode
	'''
	df = bq.cached_read(q, csv_path='data/cached_urban_rural.csv')
	return df.set_index('practice')

def list_size(year=2018):
	q = f'''
	SELECT
	  practice,
	  AVG(total_list_size) as list_size
	FROM
	  ebmdatalab.hscic.practice_statistics
	WHERE
	  month >= TIMESTAMP("{year}-01-01")
	  AND month <= TIMESTAMP("{year}-12-01")
	GROUP BY
	  practice
	ORDER BY
	  practice
	'''
	df = bq.cached_read(q, csv_path='data/cached_list_size.csv')
	return df.set_index('practice')
