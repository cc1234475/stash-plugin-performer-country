import os
import sys
import json

import urllib3
import requests
import pycountry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import log

dir_path = os.path.dirname(os.path.realpath(__file__))


def main():
    input = None

    if len(sys.argv) < 2:
        input =json.loads(sys.stdin.read())
        log.LogDebug("Raw input: %s" % json.dumps(input))
    else:
        log.LogDebug("Using command line inputs")
        mode = sys.argv[1]
        log.LogDebug("Command line inputs: {}".format(sys.argv[1:]))

        input = {}
        input["args"] = {"mode": mode}
        input["server_connection"] = {"Scheme": "http", "Port": 9999}

    output = {}
    run(input, output)

    out = json.dumps(output)
    print(out + "\n")


def run(input, output):
    modeArg = input["args"]["mode"]
    try:
        if modeArg == "" or modeArg == "cleanup":
            client = StashInterface(input["server_connection"])
            cleanupPerformers(client)
    except Exception as e:
        raise

    output["output"] = "ok"


def cleanupPerformers(client):
    log.LogInfo("Hello world")

    for i in range(0, 200):
        log.LogInfo(str(i))
        q = """{
    findPerformers(filter: {per_page: 250, page: %s}){
        performers{
        id
        country
        }
    }
    }
    """ % i
        data = client._callGraphQL(q)
        for performer in data['findPerformers']['performers']:
            country = performer['country']
            try:
                e = pycountry.countries.get(alpha_2=country)
                if e and e.name != country:
                    client.update_performer({'id': performer['id'], 'country': e.name})
            except:
                pass


mutate_performer_query = """mutation performerUpdate($input: PerformerUpdateInput!) {
    performerUpdate(input: $input){
        id
    }
}"""

class StashInterface:
    port = ""
    url = ""
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    def __init__(self, conn):
        self._conn = conn
        self.ignore_ssl_warnings = True
        self.server = conn["Scheme"] + "://localhost:" + str(conn["Port"])
        self.url = self.server + "/graphql"
        self.auth_token = None
        if "SessionCookie" in self._conn:
            self.auth_token = self._conn["SessionCookie"]["Value"]

    def _callGraphQL(self, query, variables=None):
        json = {}
        json["query"] = query
        if variables != None:
            json["variables"] = variables

        if self.auth_token:
            response = requests.post(
                self.url,
                json=json,
                headers=self.headers,
                cookies={"session": self.auth_token},
                verify=not self.ignore_ssl_warnings,
            )
        else:
            response = requests.post(
                self.url,
                json=json,
                headers=self.headers,
                verify=not self.ignore_ssl_warnings,
            )

        log.LogInfo(str(response.status_code))

        if response.status_code == 200:
            result = response.json()
            log.LogInfo(str(result))
            if result.get("error", None):
                for error in result["error"]["errors"]:
                    raise Exception("GraphQL error: {}".format(error))
            if result.get("data", None):
                return result.get("data")
        else:
            raise Exception(
                "GraphQL query failed:{} - {}. Query: {}. Variables: {}".format(
                    response.status_code, response.content, query, variables
                )
            )

    def update_performer(self, data):
        return  self._callGraphQL(mutate_performer_query, {"input": data})


main()
