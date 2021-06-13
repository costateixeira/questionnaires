Alias: $translation = http://hl7.org/fhir/StructureDefinition/translation


RuleSet: Question(context, linkId, text, type, repeats)
* {context}item[+].linkId = "{linkId}"
* {context}item[=].text = "{text}"
* {context}item[=].type = #{type}
* {context}item[=].repeats = {repeats}


RuleSet: AddTranslation(context,language,text)
* {context}.extension[+].url = $translation
* {context}.extension[=].extension[0].url = "lang"
* {context}.extension[=].extension[=].valueCode = #{language}
* {context}.extension[=].extension[+].url = "content"
* {context}.extension[=].extension[=].valueString = "{text}"
