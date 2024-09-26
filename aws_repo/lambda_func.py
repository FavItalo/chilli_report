import requests as rq
import pandas as pd
import boto3 as bt

from bs4 import BeautifulSoup


def access_chilli():
    
    url_contador = "https://cuidax.com.br/contador-chilli/"
    
    result = rq.get(url_contador)
    
    if result.status_code == 200:
        counter_element = BeautifulSoup(result.content, "html.parser").find("div").contents[0]
        counter_element = int(counter_element.rstrip("\n"))

        return {"Horario": int(pd.to_datetime("now").timestamp()), "Contagem": counter_element}


def lambda_handler(event, context):
    
    returned_events = access_chilli()
    print("sucess chilli access")
    
    dynamo_db = bt.resource("dynamodb")
    table = dynamo_db.Table("relatorio_nojeira_chilli")
    
    print("success table access")
    
    try:
        table.put_item(Item=returned_events)
        return table.scan()
    except:
        raise