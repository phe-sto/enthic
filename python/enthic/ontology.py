# -*- coding: utf-8 -*-
"""
=========================================
Ontology of the data retrieved by the API
=========================================

In complement, explanation of the data retrieved by the API. Combining data
endpoints and the ontology endpoint should avoid multiplication and backward
compatibility issue.
"""

ONTOLOGY = {"accounting":
    {
        "C":
            {
                "description": "Comptes individuels clients et fournisseurs. A tout moment, vous pouvez ainsi connaître les soldes des comptes souhaités, vos créances client par client et/ou vos dettes fournisseur par fournisseur. En terme de gestion de l’entreprise, la comptabilité complète donne des informations importantes.",
                "code": {
                    "FY": "Salaires et traitements",
                    "DI": "Résultat de l’exercice (bénéfice ou perte)",
                    "HI": "Résultat exceptionnel",
                    "HJ": "Participation des salariés aux résultats de l’entreprise",
                    "HK": "Impôts sur les bénéfices",
                    "HM": "Total des charges",
                    "FJ": "Chiffre d’affaires nets",
                    "VN": "Impôts, taxes et versements assimilés",
                    "YP": "Effectif moyen du personnel",
                    "FO": "Subventions d’exploitation",
                    "GAN": "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "DIR": "Distribution ratio, (FY + HI) / GAN"
                }
            },
        "S":
            {
                "description": "Pour permettre aux petites entreprises de se développer, un régime de comptabilité simplifiée a été mis en place afin d'alléger leurs obligations comptables et le coût qu'elles impliquent",
                "code": {
                    "FY": "Salaires et traitements",
                    "HI": "Résultat exceptionnel",
                    "290": "Produits exceptionnels",
                    "HJ": "Participation des salariés aux résultats de l’entreprise",
                    "HK": "Impôts sur les bénéfices",
                    "310": "Bénéfice ou perte",
                    "FJ": "Chiffre d’affaires nets",
                    "244": "Impôts, taxes et versements assimilés",
                    "376": "Effectif moyen du personnel",
                    "226": "Subventions d’exploitation reçues",
                    "GAN": "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "DIR": "Distribution ratio, (FY + HI) / GAN"
                }
            }
    },
    "scoring": {
        "distribution": {
            "type": "enum",
            "values": ["TIGHT", "AVERAGE", "GOOD", "UNKNOWN"],
            "description": "Classification d'une companie basée sur le ratio de redistribution DIR. GOOD est 10% en dessous de la moyenne, TIGHT est 10% au dessus, AVERAGE entre les deux. UNKNOWN si impossible à calculer."
        }
    }
}
