## test sensor


import sensor

hass = ""
config = {"CONF_NAME":"conf_name", "CONF_CODE" : "37077",\
          "CONF_TOKEN" : "72608dd5f2df6da25d529d5ea5c189a75da109e35a2082fb39f532f676814fe2"}
listeEntities = []
print( config.get("CONF_TOKEN"))
def add_entities(
        new_entities, update_before_add = False
    ):
    listeEntities.append(new_entities)


sensor.setup_platform(hass, config, add_entities, discovery_info=None)


for x in listeEntities:
    print("***")
    print(x)
    x[0]._update()
    print( x[0]._attributes)