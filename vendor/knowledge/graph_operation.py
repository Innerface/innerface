# Author: YuYuE (1019303381@qq.com) 2018.03.30
from neo4j.v1 import GraphDatabase


def default_auth_config():
    congif = {
        'host': 'localhost',
        'port': 7687,
        'user': 'neo4j',
        'password': 'neo4j'
    }
    return congif


def set_handle(config=False):
    if config == False:
        config = default_auth_config()
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    return driver


def set_graph_session(driver=False):
    if driver == False:
        driver = set_handle()
    session = driver.session()
    return session


# 添加节点
def add_bank_dots(tx, name):
    tx.run("MERGE (bank:Bank {name: $name})", name=name)


def add_bank_field(tx, key, field):
    tx.run("MERGE (field:Field {field: $key, value: $value})", key=key, value=field)


# 建立联系
def add_dots_link(tx, bank, field, key):
    tx.run("MATCH(bank:Bank {name: $name}),(field:Field {value:$value}) "
           "CREATE (bank)-[LINKED_TO:LINKED_TO {attr:$key}]->(field)", name=bank, value=field, key=key)
