# -*- coding: utf-8 -*-
"""
============================================================
Tree view of data contained in a french "compte de resultat"
============================================================
"""

TREE_VIEW = {
  "name": "Bénéfices",
  "codeLiasses": [
    "HN",
    "310"
  ],
  "children": {
    "ResultatAvantImpot": {
      "name": "Résultat courant d'avant impôts ",
      "codeLiasses": [
        "GW"
      ],
      "children": {
        "ResultatExploitation": {
          "name": "Résultat d'exploitation ",
          "codeLiasses": [
            "GG",
            "270"
          ],
          "children": {
            "ProduitsExploitation": {
              "name": "Produits d'exploitation ",
              "codeLiasses": [
                "FR",
                "232"
              ],
              "children": {
                "ChiffresAffairesNet": {
                  "name": "Chiffres d'affaires nets ",
                  "codeLiasses": [
                    "FJ"
                  ],
                  "children": {
                    "VenteMarchandises": {
                      "name": "Ventes de marchandises ",
                      "codeLiasses": [
                        "FA"
                      ]
                    },
                    "ProductionVendueDeBiens": {
                      "name": "Production vendues de biens ",
                      "codeLiasses": [
                        "FD"
                      ]
                    },
                    "ProductionVendueDeServices": {
                      "name": "Production vendue de services ",
                      "codeLiasses": [
                        "FG"
                      ]
                    }
                  }
                },
                "ProductionStocked": {
                  "name": "Production stockée ",
                  "codeLiasses": [
                    "FM",
                    "222"
                  ]
                },
                "ProductionImmobilisee": {
                  "name": "Production immobilisée ",
                  "codeLiasses": [
                    "FN",
                    "224"
                  ]
                },
                "SubventionsExploitation": {
                  "name": "Subvention d'exploitation ",
                  "codeLiasses": [
                    "FO",
                    "226"
                  ]
                },
                "RepriseDepreciationProvisionsTransfertChargesExploitation": {
                  "name": "Reprises sur dépréciations, provisions (et amortissements), transfert de charges ",
                  "codeLiasses": [
                    "FP"
                  ]
                },
                "AutresProduits": {
                  "name": "Autres produits ",
                  "codeLiasses": [
                    "FQ",
                    "230"
                  ]
                }
              }
            },
            "ChargesExploitation": {
              "name": "Charges d'exploitation ",
              "codeLiasses": [
                "GF",
                "264"
              ],
              "sign": -1,
              "children": {
                "AchatsDeMarchandises": {
                  "name": "Achats de marchandise (y compris droits de douane)",
                  "codeLiasses": [
                    "FS",
                    "234"
                  ]
                },
                "VariationStockMarchandises": {
                  "name": "Variation de stock (marchandises)",
                  "codeLiasses": [
                    "FT",
                    "236"
                  ]
                },
                "AchatMatierePremiereAutreAppro": {
                  "name": "Achat de matières premières et autres approvisionnements (et droit de douane)",
                  "codeLiasses": [
                    "FU",
                    "238"
                  ]
                },
                "VariationStockMatierePremiereEtAppro": {
                  "name": "Variation de stock (matières premières et approvisionnements)",
                  "codeLiasses": [
                    "FV",
                    "240"
                  ]
                },
                "AutresAchatEtChargesExternes": {
                  "name": "Autres achats et charges externes ",
                  "codeLiasses": [
                    "FW",
                    "242"
                  ]
                },
                "ImpotTaxesEtVersementsAssimiles": {
                  "name": "Impôts, taxes et versements assimilés ",
                  "codeLiasses": [
                    "FX",
                    "244"
                  ]
                },
                "SalairesEtTraitements": {
                  "name": "Salaires et traitements ",
                  "codeLiasses": [
                    "FY",
                    "250"
                  ]
                },
                "ChargesSociales": {
                  "name": "Cotisations sociales ",
                  "codeLiasses": [
                    "FZ",
                    "252"
                  ]
                },
                "DotationAmortissementImmobilisations": {
                  "name": "Sur immobilisations : dotations aux amortissements ",
                  "codeLiasses": [
                    "GA",
                    "254"
                  ]
                },
                "DotationDepreciationImmobilisations": {
                  "name": "Sur immobilisations : dotations aux dépréciations ",
                  "codeLiasses": [
                    "GB"
                  ]
                },
                "DotationDepreciationActifCirculant": {
                  "name": "Sur actif circulant : dotations aux dépréciations ",
                  "codeLiasses": [
                    "GC"
                  ]
                },
                "DotationProvisions": {
                  "name": "Dotations aux provisions ",
                  "codeLiasses": [
                    "GD",
                    "256"
                  ]
                },
                "AutresCharges": {
                  "name": "Autres charges ",
                  "codeLiasses": [
                    "GE",
                    "262"
                  ]
                }
              }
            }
          }
        },
        "ResultatFinancier": {
          "name": "Résultat financier ",
          "codeLiasses": [
            "GV"
          ],
          "children": {
            "ProduitsFinanciers": {
              "name": "Produits financiers ",
              "codeLiasses": [
                "GP",
                "280"
              ],
              "children": {
                "ProduitsFinanciersParticipations": {
                  "name": "Produits financiers de participations",
                  "codeLiasses": [
                    "GJ"
                  ]
                },
                "ProduitsAutresValeursMobiliereEtCreancesActifImmobilise": {
                  "name": "Produits des autres valeurs mobilières et créances de l'actif immobilisé",
                  "codeLiasses": [
                    "GK"
                  ]
                },
                "AutreInteretEtProduitAssimile": {
                  "name": "Autres intérêts et produits assimilés",
                  "codeLiasses": [
                    "GL"
                  ]
                },
                "RepriseDepreciationEtProvisionTransfertsChargesFinancier": {
                  "name": "Reprises sur dépréciations et provisions, transferts de charges",
                  "codeLiasses": [
                    "GM"
                  ]
                },
                "DifferencesPositivesChange": {
                  "name": "Différences positives de change",
                  "codeLiasses": [
                    "GN"
                  ]
                },
                "ProduitsNetsCessionsValeursMobilesPlacement": {
                  "name": "Produits nets sur cessions de valeurs mobilières de placement",
                  "codeLiasses": [
                    "GO"
                  ]
                }
              }
            },
            "ChargesFinancieres": {
              "name": "Charges financières ",
              "codeLiasses": [
                "GU",
                "294"
              ],
              "sign": -1,
              "children": {
                "DotationsFinancieresAmortissementDepreciationProvision": {
                  "name": "Dotations financières aux amortissements, dépréciations et provisions",
                  "codeLiasses": [
                    "GQ"
                  ]
                },
                "InteretEtChargeAssimilees": {
                  "name": "Intérêts et charges assimilées",
                  "codeLiasses": [
                    "GR"
                  ]
                },
                "DifferenceNegativeChange": {
                  "name": "Différences négatives de change",
                  "codeLiasses": [
                    "GS"
                  ]
                },
                "ChargesNetteCessionValeurMobiliereDePlacement": {
                  "name": "Charges nettes sur cessions de valeurs mobilières de placement",
                  "codeLiasses": [
                    "GT"
                  ]
                }
              }
            }
          }
        },
        "BenefAttribueOuPerteTransferee":{
          "name": "Bénéfice attribué ou perte transférée",
          "codeLiasses": [
            "GH"
          ]
        },
        "PerteSupporteeOuBenefTransfere":{
          "name": "Perte supportée ou bénéfice transféré",
          "codeLiasses": [
            "GI"
          ],
          "sign": -1
        }
      }
    },
    "ResultatExceptionnel": {
      "name": "Résultat exceptionnel ",
      "codeLiasses": [
        "HI"
      ],
      "children": {
        "ProduitsExceptionnels": {
          "name": "Produits exceptionnels ",
          "codeLiasses": [
            "HD",
            "290"
          ],
          "children": {
            "ProduitExceptionnelOperationGestion": {
              "name": "Produits exceptionnels sur opérations de gestion",
              "codeLiasses": [
                "HA"
              ]
            },
            "ProduitExceptionnelOperationCapital": {
              "name": "Produits exceptionnels sur opérations en capital",
              "codeLiasses": [
                "HB"
              ]
            },
            "RepriseDepreciationProvisionTransfertChargeExceptionnel": {
              "name": "Reprises sur dépréciations et provisions, transferts de charges",
              "codeLiasses": [
                "HC"
              ]
            }
          }
        },
        "ChargesExceptionnelles": {
          "name": "Charges exceptionnelles ",
          "codeLiasses": [
            "HH",
            "300"
          ],
          "sign": -1,
          "children": {
            "ChargesExceptionnelleOperationGestion": {
              "name": "Charges exceptionnelles sur opérations de gestion",
              "codeLiasses": [
                "HE"
              ]
            },
            "ChargesExceptionnelleOperationCapital": {
              "name": "Charges exceptionnelles sur opérations en capital",
              "codeLiasses": [
                "HF"
              ]
            },
            "DotationExceptionnelleAmortissementDepreciationProvision": {
              "name": "Dotations exceptionnelles aux amortissements, dépréciations et provisions",
              "codeLiasses": [
                "HG"
              ]
            }
          }
        }
      }
    },
    "ParticipationSalariesAuxResultats": {
      "name": "Participation des salarié⋅es aux résultats de l'entreprise ",
      "codeLiasses": [
        "HJ"
      ],
      "sign": -1
    },
    "ImpotsSurLesBenefices": {
      "name": "Impôts sur les bénéfices ",
      "codeLiasses": [
        "HK",
        "306"
      ],
      "sign": -1
    }
  }
}
