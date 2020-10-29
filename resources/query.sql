-- http://skyserver.sdss.org/dr16/en/help/browser/browser.aspx#&&history=description+SpecObj+V
-- 5,107,045 righe per 304 MB
SELECT spectroFlux_u, spectroFlux_g, spectroFlux_r, spectroFlux_i, spectroFlux_z, class AS source_class, z AS redshift
INTO MyDB.spectral_data_class
FROM SpecObj
-- 	class	count
-- 	GALAXY	2963274
-- 	QSO		1102641
-- 	STAR	1041130

