import requests
import json
import os
from sys import argv
# Updated 02-05-2021





# This was just some test
if (False):
  formschema_filename= os.path.splitext(fileName)[0]+'-form-schema.json'
  filenames = ['forms/form_1.html', 'forms/form_2.html', formschema_filename, 'forms/form_4.html', 'forms/form_5.html']
  with open('forms/form_total.html', 'w') as outfile:
      for fname in filenames:
          with open(fname, "w") as infile:
              outfile.write(infile.read())
  exit(0)


fileName = None
fileName = os.path.join(os.getcwd()+"/output/Questionnaire-mkatz-questionnaire.json")

# Get the filename (for the PoC, from the command line)
if len(argv)>1:
   fileName = os.path.join(os.getcwd()+argv[1])


# See if there is a parameter with a valid file name in it. Exit if not.
def isFile(fileName):
    if(not os.path.isfile(fileName)):
        raise ValueError("You must provide a valid filename as parameter")


    if __name__=="__main__":
      try:
        if not(fileName):
          fileName=argv[1]
          print("Filename: ",fileName)
          isFile(fileName)
          pass

      except Exception as e:
          print("You must provide a valid filename as parameter")
          raise

# OK, now just open it as a json
with open(fileName) as qa:
    questionnaire = json.load(qa)



### Features to add:

# item.prefix
# types: 
    # group+
    # +display+
    # question
    # +boolean+
    # decimal
    # integer
    # +date
    # datetime
    # time
    # +string+
    # text
    # url
    # +choice+ - add valueset
    # open-choice
    # attachment
    # reference
    # quantity
# features:
    # aciveWhen
# extensions:
    # entry mode
    # end point 
    # optional display
    # source queries
    # initial expression
    # candidaate answers expression
    # answer expression
    # answer context expression
    # calculated expression
    # choice column
    # context resources
    # isSubject?
    # item population context
    # item extraction context
    # lookup questionnaire
    # observation link period
    # observation extract
    # source structuremap
    # target structuremap
    # columnWidth
    # enableWhen
    # collapsible
    # minquantity
    # maxquantity
    # choice constraint





def createSingleItem(q_item): # For each item in the questionnaire:
  schema_item = {}
  schema_item["title"] = q_item["text"] # see types here: https://github.com/json-editor/json-editor#format
  if (q_item["type"] == "boolean"):
      schema_item["type"] = "boolean"
      schema_item["format"]: "checkbox"
  elif (q_item["type"] == "display"):
    schema_item["type"] = "info"
  elif (q_item["type"] == "string"):
    schema_item["type"] = "string"
  elif (q_item["type"] == "date"):
    schema_item["type"] = "string"
    schema_item["format"] = "date"
  elif (q_item["type"] == "integer"):
    schema_item["type"] = "number"
  elif (q_item["type"] == "time"):
    schema_item["type"] = "string"
    schema_item["format"] = "time"
  elif (q_item["type"] == "dateTime"):
    schema_item["type"] = "string"
    schema_item["format"] = "datetime"
  elif ((q_item["type"] == "choice") or (q_item["type"] == "open-choice")) :
    schema_item["type"] = "string"
    if "extension" in q_item:
      for ext in q_item["extension"]:
        if ext["url"] == "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl":
          # if there is an itemControl extension...
          if (("valueCodeableConcept" in ext) and ("coding" in ext["valueCodeableConcept"])):
            if (("system" in ext["valueCodeableConcept"]["coding"][0]) and (ext["valueCodeableConcept"]["coding"][0]["system"]=="http://hl7.org/fhir/questionnaire-item-control")): #only expect one code
              if ext["valueCodeableConcept"]["coding"][0]["code"] == "radio-button":
                schema_item["format"] = "radio"

      
    if ("answerValueSet" in q_item):
      if (q_item["answerValueSet"][0] =="#"): # if the resource is contained
        print(q_item["answerValueSet"])  
        if "contained" in questionnaire:
          cont_answer_vs = [cont_vs for cont_vs in questionnaire["contained"] if ('#'+cont_vs["id"] == q_item["answerValueSet"] )]
        if (len(cont_answer_vs) == 1):
          if(("compose" in cont_answer_vs[0]) and ("include" in cont_answer_vs[0]["compose"])): #If the valueset contains "compose"
#            print(cont_answer_vs[0]["compose"]["include"])
            concepts = cont_answer_vs[0]["compose"]["include"][0]["concept"]
            schema_item["enum"] = [concept["code"] for concept in concepts]
            if not("options" in schema_item):
              schema_item["options"] = {}
            schema_item["enum_titles"] = [concept["code"] for concept in concepts]
            schema_item["options"]["enum_titles"] = [concept["display"] for concept in concepts if "display" in concept]
      else: #if not contained
        print("Not contained: " +q_item["answerValueSet"])


    else:
      schema_item["enum"] = ["To Do", "Still to do", "Not done"]
  elif (q_item["type"] == "group"):  # If the item is a group, process the required and then the items
    if ('type' in q_item):
      schema_item["type"] = "object"
      schema_item["required"] = []
      for it in q_item['item']:
        if ('required' in it):
          if (it['required'] == True):
            schema_item['required'].append(it['linkId'])
      schema_item["properties"] ={}
      for child in q_item["item"]: 
        schema_item["properties"].update(createSingleItem(child))

# previous code (delete when safe)
#  elif (item["type"] == "group"):
#    if ('type' in item):
#      sitem["type"] = "object"
#      if ('required' in item):
#        if (item['required'] == True):
#          sitem['required'].add(item['linkId'])
#      sitem["properties"] ={}
#      for child in item["item"]: 
#        sitem["properties"].update(createSingleItem(child))

  return {q_item["linkId"]: schema_item}



def createItem(qitem):
  fitem = {}
  fitem["title"] = qitem["text"]
  tempitem = createSingleItem(qitem)
  if (('repeats' in qitem) and (qitem['repeats']== True)):
    fitem = {"type":"array"}
    fitem["items"] = tempitem[qitem["linkId"]]
    tempitem = {qitem["linkId"]:fitem}
  return(tempitem)    



mainForm = json.loads ('{"title": "","type": "object","required": [],"properties": {}}') 

# Give the form a title if one exists
if ('title' in questionnaire):
  mainForm['title'] = questionnaire['title']


for qitem in questionnaire["item"]: # For each questionnaire.item
  if ('required' in qitem): # The required flag needs to be at the parent level, not under the items in the schema. Perhaps this can be put inside the recursive code.
      if (qitem['required'] == True):
        mainForm['required'].append(qitem['linkId'])
  mainForm["properties"].update(createItem(qitem)) # Start a recursive append of the questionnaire items





formschema_filename= os.path.splitext(fileName)[0]+'-form-schema.json'

with open(formschema_filename, 'w') as outfile:
    json.dump(mainForm, outfile, indent=4, ensure_ascii=False)  

# Ok, the file is saved. It can be tested here: https://pmk65.github.io/jedemov2/dist/demo.html
# in the IG template, integrate this schema in the rest of the json-editor.



filenames = ['forms/form_1.html', 'forms/form_2.html', formschema_filename, 'forms/form_4.html', 'forms/form_5.html']
with open('forms/form_total.html', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())

# https://pmk65.github.io/jedemov2/dist/demo.html?schema=EQbwOgTmB2AE%2BzMALgS2QGwKZIFyOCwFoAhVCZAC1gCUsBzVAZ2QgEM0B7OARQFcsLVN2htyOYABpIMBAWQBPAA4T8STgCMAVlgDGyJNKhwESCFgCOfcQBM8sANoBdI7NPAlETioqpB98GM5OSQ0TFVYQLdg4ND0bHskLDIKajpGFnYuaEMZExiQlGUIpFRoADNOJDyC2ABfV3zY4GhmJgCa2vcwhOA1YAA5AEkAZRHYAApUctgAa2hOAHdoAEpcoK74UOLE4Eyy%2BmqNmIbOmKSiDXIqAH1oPgBbDSwoPsizrrjw3eIr1Nh7k8XpNprA2BhzGwbAo5gtlmspB9atsVLt9tBDsAkQhTsdmn9bkoMGxdBEok1kSh4iVgCkqLAiSSJI1Nlsiqi3uptHoDIi8ZTzFZbPZnCzWUhPN4Xmh%2FG9yazmpROA8ydiFWyejSAILIWBKlUAfnW0XVhUUHP6Gk4nGwbByWP5rLqauCzsd8FxJsK%2BqwNyhNnMTHacpdZupuwAEsqsLAtTYA4Jg2LNiiaZodPpjRSCmZLNZzHY3qLQ%2B5JT4ZcH8PLTQQfTdMlgsLyqyWU1TvpzgFGVWD44Gk63PuyaejMYO5J7s2260pOCxwTddJwbKr3eqvr1%2BgAFOfIcGwJcrrM15rmkesA5HL1O5Pr4B13ToBQdNcKjc0gDCT%2BPJ%2B6O07o5XlOXRuteJwupOlJlEIyB8NkL5gae4adkM0AwXBwj2relJnrs6Y8j%2BbaCvmWCFvgxavqWXjln4lbvJR5zANBYQYdwNyoCu0BoOUfgQDcH4APIkDQEZaghwFvu2m4EKh6HwXyiGSbhAEXhiQEnpBNalGhLHZH6faJuJv7dMh%2FRDJx3G8ZMgnCaJCLYVpw54dymYKRJ4rAMRwpFi4445h41HSrRRnGc0zHoKx0D1qwjbNvRimhe%2BuxxgmQaEaFjHKf0gEOglpqaRlbLhbBemzvOGCLsuq55b%2BSWdju5WwB%2BVXpYVf4WgQOV%2BZsBWFdpcmYYu34hgxtVSZ%2Bw0OW1qZoqpY6jQqoHuT13X1IOS21L1hRKGw5hcQAjCFbaarsW67VgXGwIdblKf%2B%2FT4a5U3NF5BYir5o0SoFviyi2C2ludB13G0R1jSdnbDGMrWOVlnVzepNZbR5O17cg%2B13GwKogyedX9AAYhjqAYDCoiYzdiVOSpECXrly2uk9lLIxdqM3IwABuF3o6Tv01ThpkEAA4qg7NwCTzKrWad2w1Tak0xp60QU9EoA8gABMWP%2BWD27K7Aatk8dktchmvL0%2B4L2kW9JtsmWQU%2FfFtPbcrKtA2lI08xrfNIBDIxQ6aM2U9Tq2I22jNcU7ovq77427PjDyE8TGNi39mUG3scOywjlvNCHqss0LHPh679vux2%2FSC8LAIJz7d4w0gXVJ2to0bQUQcEGz%2BeV4XSke8AH6UITNiwG3Isd5nfvZWnCsukgNgcL6nDlDcBKUBHSElwQAAis%2BwPPsBL1XEsdbXaej8AlQQA8HC7DPyASJPa5xCqNzz4v1zL53HmawQAAqqA9jve%2FpxOIrYAiwsCoHoJQZAfooEAO5rTHGBAADqYCIG6g4LvV%2B8MgFT2APQQQe5sgLjYHgleYY15IH5vgjgmF9zEJjFMGY8wlirCwXTHBlRlw3HMIwFU9o4Fd3IcAXG1oB7cN%2Fhdfe7VzzS0xCfC6jwRSrSQF%2FTgsB15VD1neEYaAMAYFgMgVRNgNGZ0KAMTguojHQFvqNJwd9EJIBVDYVAuhqHcFIVI3Yu12DPk0VBG%2BDw6LVkjp%2FJAABZUizjXFoUkcnQ%2BqcZGsM2nY4CSBiQaBuDfFggTBwIOUfggcH0Kb3RcsbHJnk8zeXIu9Gqn0pTfWyfXJAS5dE8kwu4463dmotP0G03x0MU4PVKfXQoZsyKOGqUXRi1t6ntLvM07APS2LX2qpM6u3cRgqEfLwpqNoFnZFgMsmJoMU45RMY5M%2BF84rT1nok0KLdsbAHma0tiaAuZ2zapldZmzxFwC6XszC%2BjxG3OMvcxyTzFlRQwJwFx8l%2BEfLIdJJAGy9A%2FJ2d0%2FZAAZaFUSjkPJrvEgOwzm5nLbKA8BkDoGVXRb0uF8KNTd2QeStBupXkxh3uC%2BS4tiVcsYjxCALAMn4KfnxJcXEvAYFmXi7uuNyAsH0fg7eEADzcFYDaI0fTppFKltTEld55EPEUUSyOKi1HGJ5VonReiDEHLNUau8ZiLHcGsW7U0ti7UTl1ZSDli5do2DuI8Z4rxaV0tyT3XZPIDy%2BoBAGl4uL%2BlxLri6kCnr%2FLLL9BAKmrMiFQLSZK6G3dN431gEwb52yvF5wHugtJ6rzUTnNU3fKurcxMD4BgZADSk0IppHQFtbaCmdo8Z2QZcbGKjItua2pNFbZBL6uU3t7abi5vfnS%2BQ3cMVsCtFkTgEAfEpv1gmie7qcR7uaKK1VFVAytvbXm4JnSVXitgJevtI7q4nMPQO7BR6NRCqfde5dIao6di%2Fgq39%2FbVm3QPQkwBhVQWR1A5VaAugMB8CYDS95K7V2COaoh5DqG3Eatnfi05tb%2FL6sNR%2Bu8Jr1EvoedowmVrDG2oo5JB1NqrHAsKm65jx6SNsng%2BYcoLx2ASv%2FfC0NdBBMZvBDRj%2Bb6oO8YbhRht6plNJLXMppadRgBAA%3D&value=ETI%3D&code=EQehAIBUAsFNwGYHsA2KkHcCWA7A5uCrrAM7gCGATvALbk4Am5ALkpQJ4WPjXkNI4U7AHTgAmkgCu4AMb0KDBrMklWNWUgbxyAIyQA3bdx2x0GYQB0cWBOAAUAKxKwGWVpXC5V9GbCS3sRkxhACkAZQB5ADkAUVd3AEpwJxc3NmEtVUokdjsEgG4rFPi2cABecBxYDHBA%2FnNw6Li0yjt%2BGUkaWBxmYQBHSVgOMNNYGXc7C2AAYicBAFpU93nkShophIAaZJcWcgKrcHAwYpbhLBkBIh1y8CnkHvIMUiQugBYpw%2BTnEsphZl0KFgAH09JQtB4KghyChnF9Tu4MlgSAAHFDkdjA6gDLDUBjAq6cCrMSiDYBAA%3D&style=EQegVAOgThB2AE8AWAmAXAIwKYDMD2UWA3gMZ6wAuWla8EwdDAhAJYC2ADgRQIaUDcAX2hxESAMyZcBYmUrUKteo3itO3PhSEiEyACxT8hUuSo0VytVyi8BwmLqQBWQzJPzzyy%2B2u2t90WQANldjOTNFC2YfDTsdMBAdHQAbHmxk%2BCIdREQAExYAZw5UgE9aFlhkiqwAWgxkvBIAa35snLYeKABzCrq8Cgo8NloAOgAGQjZWhwDYHRGjNhquqDwAVw5MtsQO7t6MfsHh%2BDGRp0npuFmkhxGSTtyaihYKZKwthxz4XZ7YPoGhqMUOcsFMdLMRhIADTIcQfQKIfCUGoFFgALywtAAjBdwTc4AdciV4bodp1frQxpdSfAkRQajgeGwWMkyvAajwOMVagUSgUqGwoQAhKqwJoAWR4JAAynyBQAxUxQ%2BjSrBdPDvACqAEl6FCAEp4A6DZXAAASWGSADcsM97vAAHJYNZYPUAQSgLB4yVNDv6eHg0r4BT19AAMixsFAeM9yIHg3qCsGUVhPThTW6uW94ABhPANKDwACibDwACsWKHgKr1VrtcXSxWqzWNfAdYGSmwDskq37Brn8wQG%2BXK8BqV86Sj0Zj4DjQeOcpOAO5YFhdJCRPRjKnbeCi2pIVfryJY8aqGI2TTU64ORY1cKrDJZT7wJcsXIUJC0ILbjgAD2pPEHHmVYl3gEZQOfQI3w%2FL9Z23ABSa98VgBYCCWCp9xJRBwDaDApSaFZ1lgR4yALWgAGJ5WohdDzXDdv1%2FAC2hgz9GLGf8Fx%2BXpPWPWgeDWQYuPJXo3hwSIBKEtpuL%2BQYOEpTi8IIXJUyePAOBqMT6WjfI1gKbEOOYl8DigFSoDUjTeI3GodJYPSDMUl8OB4XJ8lgLoFKMwIqD%2FelvTXWA0BIBRU2pEg3k6WhjSQfhEHiRIZhQu8H3zTS0ktKFUnSElcJfSdGWZVlaAAcSwAgeh4GF6AAFXYLACkdLAwMNDo5mAGFarYeqYQKVMWBwBdJ1RDFsQADkcwIyIISjxFm2ijwY%2BAUEMhdWLg5aVukkTZPUhyvN0GTNNwE9NpfHy%2FKqLpAvgKytC2vY%2FlutAsScCbYHCrBIvgaLqQSIC4B0CoOEE7D4A%2Br6frihxcsCOi%2BKW07AhMszsX%2FeACnzd94Ao7cdxfQ65L236EquFC7nzGFyeSGosUpsiabGOnUqxWnwPprEUCZ6nObZ1LxC5mo9AFpwBaCAWAHYBdGgWAE4BckvABeSLola6GnVYZjWWa1nmqc0tXdfp5Wan53nqeNoWzf1moRat42xbttXJcdmppZduWXYVgW2Fyb3HlZvWfc1q2g%2B1kP%2FcN1Kg8j6mg9NwPHkthObb9moHeT53k7d5OPeTr2rYKQUC6WAP6cL4O9fLsPK5LmOUSWOvy%2FjsuliTluU%2BLtOBfLzP2%2Bz9vc%2Fb%2FO9b%2FH0rdH9Xx%2BprFGanmnS9SieOYFie64n5vF%2BptvN47kfqfT%2BmJ97nf%2B53wed4V0HEC4VFY2uwhUmeG0F0QNaDLGJDd2c1yKjVp7Z1evtL4383Jqy0rQYEb0bwA1uMlUwj4r7IAWpEe4yQSAAApTxOFBPAAA1OBMY4sQRsDwUtf8ABKF%2B8AQG%2F1GGMcQRDJgEMYfOFC0DUL3FMn0IkiDmR%2FDhotLEb1gEuVAZSM4uJErAWkXAEYZYeRvgoCQQ8hYoI0kOsaI42ImFWFiFoOgMxgBAA%3D&theme=bootstrap4&iconlib=fontawesome4&object_layout=normal&template=handlebars&show_errors=interaction&required_by_default=0&no_additional_properties=0&display_required_only=0&remove_empty_properties=1&keep_oneof_values=1&ajax=0&ajaxCredentials=0&show_opt_in=0&disable_edit_json=1&disable_collapse=1&disable_properties=1&disable_array_add=0&disable_array_reorder=0&disable_array_delete=0&enable_array_copy=0&array_controls_top=0&disable_array_delete_all_rows=1&disable_array_delete_last_row=0&prompt_before_delete=1&lib_aceeditor=0&lib_autocomplete=0&lib_sceditor=0&lib_simplemde=0&lib_select2=0&lib_selectize=0&lib_choices=0&lib_flatpickr=0&lib_signaturepad=0&lib_mathjs=0&lib_cleavejs=0&lib_jodit=0&lib_jquery=0&lib_dompurify=0


exit(0)
