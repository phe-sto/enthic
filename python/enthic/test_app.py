# -*- coding: utf-8 -*-
"""
==================================
Test the flask server and it's API
==================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from json import loads

import pytest
from requests import get


@pytest.fixture()
def host():
    """
    Fixture of the API host.
       :return: String representing the host address.
    """
    return "127.0.0.1:5000"


@pytest.mark.parametrize("siren", ("389718115",
                                   "410660492",
                                   "999999999"))  # DOES NOT EXIST
def test_siren(host, siren):
    """
    Test the /company/siren endpoint. Should return a JSON.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren", ("38971811555",  # 11 CHARACTERS
                                   "41066 492",  # 9 CHARACTERS WITH WHITESPACE
                                   "41066d492",  # NON NUMERIC CHARACTER
                                   "9999999"))  # 7 CHARACTERS
def test_wrong_siren(host, siren):
    """
    Test the /company/siren endpoint with wrong SIREN. Should return a JSON.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren)
    assert response.status_code == 200
    assert loads(response.text)["error"] != "", "NO ERROR MESSAGE OR EMPTY"


@pytest.mark.parametrize("denomination", ("RCV PEINTURE",
                                          "RESEAUX ELECTRIQUE & INFORMATIQUE",
                                          "TOTO SASU"))  # DOES NOT EXIST
def test_denomination(host, denomination):
    """
    Test the /company/denomination endpoint. Should return a
       JSON.
       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
    """
    response = get("http://" + host + "/company/denomination/" + denomination)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("page", ("/404.html",
                                  "/index.html"))
def test_html_pages(host, page):
    """
    Test static html page, such as swagger description page and 404.
       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of an HTML page.
    """
    response = get("http://" + host + page)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


def test_swagger_json(host):
    """
    Test static swagger.json.
       :param host: Fixture of the API host.
    """
    response = get("http://" + host + "/swagger.json")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text)["swagger"] == "2.0", \
        "NOT A SWAGGER 2.0 JSON DESCRIPTION"
