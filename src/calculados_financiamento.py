def calcular_parcela_price(pv, taxa, n):
    
    parcela = pv * (taxa * (1 + taxa)**n) / ((1 + taxa)**n - 1)
    
    return parcela

import numpy_financial as npf

def calcular_taxa_implicita(pv, pmt, n, fv):

    taxa = npf.rate(nper=n, pmt=-pmt, pv=pv, fv=fv)

    return taxa



import pandas as pd

def tabela_price(pv, taxa, n):

    parcela = calcular_parcela_price(pv, taxa, n)

    saldo = pv

    dados = []

    for i in range(1, n+1):

        juros = saldo * taxa
        amortizacao = parcela - juros
        saldo = saldo - amortizacao

        dados.append({
            "parcela": i,
            "juros": juros,
            "amortizacao": amortizacao,
            "parcela_total": parcela,
            "saldo_devedor": saldo
        })

    df = pd.DataFrame(dados)

    return df


def juros_totais(df):

    return df["juros"].sum()



def total_pago(df):

    return df["parcela_total"].sum()