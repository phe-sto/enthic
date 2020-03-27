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
                    "fy": "Salaires et traitements",
                    "di": "Résultat de l’exercice (bénéfice ou perte)",
                    "hi": "Résultat exceptionnel",
                    "hj": "Participation des salariés aux résultats de l’entreprise",
                    "hk": "Impôts sur les bénéfices",
                    "hm": "Total des charges",
                    "fj": "Chiffre d’affaires nets",
                    "vn": "Impôts, taxes et versements assimilés",
                    "yp": "Effectif moyen du personnel",
                    "fo": "Subventions d’exploitation",
                    "gan": "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "dis": "Somme des distributions, FY + HJ",
                    "dir": "Distribution ratio, (FY + HJ) / GAN, i.e pondération de dis par le chiffre d'affaire"
                }
            },
        "S":
            {
                "description": "Pour permettre aux petites entreprises de se développer, un régime de comptabilité simplifiée a été mis en place afin d'alléger leurs obligations comptables et le coût qu'elles impliquent",
                "code": {
                    "fy": "Salaires et traitements",
                    "hi": "Résultat exceptionnel",
                    "290": "Produits exceptionnels",
                    "hj": "Participation des salariés aux résultats de l’entreprise",
                    "hk": "Impôts sur les bénéfices",
                    "310": "Bénéfice ou perte",
                    "fj": "Chiffre d’affaires nets",
                    "244": "Impôts, taxes et versements assimilés",
                    "376": "Effectif moyen du personnel",
                    "226": "Subventions d’exploitation reçues",
                    "gan": "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "dis": "Somme des distributions, FY + HJ",
                    "dir": "Distribution ratio, (FY + HJ) / GAN, i.e pondération de dis par le chiffre d'affaire"
                }
            },
        "K":
            {
                "description": "Les comptes consolidés sont un outil essentiel pour obtenir une vision globale de la santé financière d’un groupe. Il est en effet parfois difficile d’obtenir ces informations dans le cas d’une société détenant de nombreuses filiales.",
                "code": {
                    "fy": "Salaires et traitements",
                    "di": "Résultat de l’exercice (bénéfice ou perte)",
                    "hi": "Résultat exceptionnel",
                    "hj": "Participation des salariés aux résultats de l’entreprise",
                    "hk": "Impôts sur les bénéfices",
                    "gf": "Total des charges d’exploitation",
                    "fj": "Chiffre d’affaires nets",
                    "FX": "Impôts, taxes et versements assimilés",
                    "fo": "Subventions d’exploitation",
                    "gan": "Gain d'une companie, actuellement le chiffre d'affaire uniquement FJ",
                    "dis": "Somme des distributions, FY + HJ",
                    "dir": "Distribution ratio, (FY + HJ) / GAN, i.e pondération de dis par le chiffre d'affaire",
                    "r6": "Résultat Groupe (Résultat net consolidé)"
                }
            },
    },
    "scoring": {
        "distribution": {
            "type": "enum",
            "values": ["TIGHT", "AVERAGE", "GOOD", "UNKNOWN"],
            "description": "Classification d'une companie basée sur le ratio de redistribution DIR. GOOD est 10% en dessous de la moyenne, TIGHT est 10% au dessus, AVERAGE entre les deux. UNKNOWN si impossible à calculer."
        }
    }
}
