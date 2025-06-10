def getTexts(lang):
      result = None
      if lang == "pl":
            result = text_pl.text
      elif lang == "en":
            return text_en.text
      else:
            print("No text resources found for language code: " + lang)
            return text_en.text

      fillRemaining(result)
      return result

def fillRemaining(text):
      for key in text_en.text.keys():
            if key not in text:
                  text[key] = text_en.text[key]

class text_pl:
      text = {
            "title": "owce",
            "sheep": "Owca",
            "footerLabel": "Farma",
            "sheepNameLabel": "Imię: ",
            "sheepHealthLabel": "Zdrowie: ",
            "sheepHappinessLabel": "Zadowolenie: ",
            "sheepHungerLabel": "Głód: ",
            "sheepIdLabel": "id owcy: ",
            "addButton": "Dodaj owcę",
            "deleteButton": "Usuń owcę",
            "attitudesLabel": "Relacje",
            "reversedSortingButton": "Odwróć kolejność",
            "logLabel": "Dziennik zdarzeń",
            "fightingMessage": " walczy z: ",
            "breedingMessage": " rozmnaża się z: ",
            "deathMessage": ", umarła",
            "birthMessage": ", narodziła się"
      }

class text_en:
      text = {
            "title": "Sheep",
            "footerLabel": "Farm",
            "sheepNameLabel": "Name: ",
            "sheepIdLabel": "Sheep id: ",
            "addButton": "Add sheep",
            "deleteButton": "Remove Sheep",
            "reversedSortingButton": "Reverse order",
      }