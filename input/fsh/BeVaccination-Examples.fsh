
/* 
========================================================== EXAMPLES ==========================================================
==============================================================================================================================
*/
/*============================================= Example 1 =============================================*/
Instance: toto-hexa1
InstanceOf: BeVaccination 
Usage: #example 
Description: "Toto - First hexavalent vaccination"
Title:   "Toto - First hexavalent vaccination"
* identifier.value = "c448357c-cf6b-4a55-95c2-1618580bc391"
* identifier.system = "https://www.one.be/vaccination/immunisation-register"
* status = #completed
* patient.identifier.system = "https://www.ehealth.fgov.be/standards/fhir/NamingSystem/ssin"
* patient.identifier.value = "16032376921"
* recorded = "2016-05-30"
* extension[vaccination-location].valueReference = Reference(org-one-brussels)
* lotNumber = "L00156"
* occurrenceDateTime = "2016-05-30"
* manufacturer = Reference(org-sanofi)
* doseQuantity.value = 1
* performer[0].actor.identifier.system = "https://www.ehealth.fgov.be/standards/fhir/NamingSystem/nihdi-organization"
* performer[0].actor.identifier.value = "NIHDI_ONE"
* performer[1].actor.identifier.value = "Hospital Midwife 1"
* vaccineCode.coding[0].system = "http://hl7.org/fhir/sid/cvx"
* vaccineCode.coding[0].code = #146
* vaccineCode.coding[1].code = #3050176
* protocolApplied.doseNumberPositiveInt = 1
* protocolApplied.seriesDosesPositiveInt = 4
* extension[administeredProduct].valueReference.identifier.system = "http://snomed.info/sct"
* extension[administeredProduct].valueReference.identifier.value = "3050176"
* extension[vaccination-confirmationStatus].valueCode = #confirmed
