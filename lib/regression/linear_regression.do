cd "C:/Users/ajwalker/Documents/GitHub/factors-associated-with-changing-notebook/lib/regression/data"
clear
import delimited data_for_stata.csv

*xtile qof = total, nq(5)
xtile fte = gp_fte_per_10000, nq(5)
xtile imd = deprivationscoreimd2015, nq(5)
xtile list_size_q = list_size, nq(5)
xtile over_65 = aged65years,nq(5)
xtile long_term_health = withalongstandinghealthcondition,nq(5)
encode ruc11cd, gen(rural_urban_code)
encode principal_supplier, gen(ehr)

tabstat aged65years,by(over_65) s(min max)
tabstat withalongstandinghealthcondition,by(long_term_health) s(min max)
tabstat list_size,by(list_size_q) s(min max)
tabstat gp_fte_per_10000,by(fte) s(min max)
tabstat deprivationscoreimd2015,by(imd) s(min max)
*tabstat qof_total,by(qof) s(min max)

foreach depvar in desogestrel trimethoprim {

	foreach indepvar in /*single_handed*/ dispensing_bin fte list_size_q imd ///
			long_term_health over_65 rural_urban_code ehr {
		tabstat `depvar',by(`indepvar') s(mean)
		regress `depvar' i.`indepvar'
	}

	mixed `depvar' ///
		  /*i.single_handed*/ i.dispensing_bin i.fte i.list_size_q i.imd ///
		  i.long_term_health i.over_65 i.rural_urban_code i.ehr ///
		  || pct:

	predict predictions`depvar'
	qui corr `depvar' predictions`depvar'
	di "R-squared - fixed effects (%): " round(r(rho)^2*100,.1)

	qui predict predictionsr`depvar', reffects
	qui corr `depvar' predictionsr`depvar'
	di "R-squared - random effects (%): " round(r(rho)^2*100,.1)

}
