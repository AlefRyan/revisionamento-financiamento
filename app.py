import streamlit as st
import numpy_financial as npf
import src.calculados_financiamento as calc
import pandas as pd


st.title("Revisionamente de Financiamento de Veículo")

st.subheader("Dados do financiamento")

col1, col2 = st.columns(2)

with col1:
    valor = float(st.number_input(
        "Valor do veículo",
        help="Preço do veículo informado no contrato ou na nota fiscal."
    ))

    entrada = float(st.number_input(
        "Entrada",
        help="Valor pago no ato da compra que reduziu o valor financiado."
    ))

with col2:

    parcelas = int(st.number_input(
        "Número de parcelas",
        help="Quantidade total de prestações previstas no contrato."
    ))
    
    parcela = float(st.number_input(
        "Valor da parcela",
        help="Valor de cada prestação mensal informada no contrato."
    ))

col3, col4 = st.columns(2)

with col3:
    taxa_contrato = float(st.number_input(
        "Taxa de juros contratada (%)",
        help="Taxa de juros mensal informada no contrato de financiamento."
    ))


st.subheader("Encargos adicionais (possivelmente questionáveis)")

col5, col6 = st.columns(2)

with col5:
    tac = float(st.number_input(
        "Título de Capitalização",
        value=0.0,
        help="Produto financeiro frequentemente vinculado ao financiamento. Pode ser questionado quando imposto como condição para concessão do crédito."
    ))

    tarifa_cadastro = float(st.number_input(
        "Tarifa de cadastro",
        value=0.0,
        help="Tarifa cobrada para abertura de cadastro do cliente na instituição financeira."
    ))
    
    iof = float(st.number_input(
        "IOF",
        help="Imposto sobre Operações Financeiras. Tributo federal obrigatório em operações de crédito."
    ))
    
    gravame = float(st.number_input(
        "Registro de contrato (gravame)"
    ))

with col6:
    seguro = float(st.number_input(
        "Seguro prestamista",
        value=0.0,
        help="Seguro que cobre a dívida em caso de morte ou invalidez. Deve ser opcional."
    ))
    
    tarifa_ava_bem = float(st.number_input(
        "Tarifa de Avaliação de Bem",
        help="Tarifa referente à avaliação de veículo usado como garantia ou parte do pagamento."
    ))

    outros_encargos = float(st.number_input(
        "Outros encargos",
        value=0.0,
        help="Informe aqui outros valores cobrados no contrato, se houver."
    ))
   

data_contrato = st.date_input("Data do contrato", format='DD/MM/YYYY')


dados = pd.read_csv(
    r'dados/STP-20260307161154673.csv',
    sep=';',
    decimal=','
)

dados['Data'] = pd.to_datetime(dados['Data'], format='%d/%m/%Y')


st.divider()


if st.button("Calcular Financiamento"):
    
    # valor financiado
    valor_financiado = (valor - entrada) + iof + tarifa_cadastro + tarifa_ava_bem + tac + outros_encargos + seguro + gravame
    valor_financiado_recalc = (valor - entrada) + iof + tarifa_cadastro 
    
    # taxa média de mercado (CORREÇÃO 1)
    data_contrato = pd.to_datetime(data_contrato).replace(day=1)

    filtro = dados.loc[dados["Data"] == data_contrato, "taxa_media"]

    if filtro.empty:
        st.error("Taxa média de mercado não encontrada para esta data.")
        st.stop()

    tx_media_mercado = filtro.iloc[0] / 100
    
    # taxa efetiva 
    taxa_efetiva = calc.calcular_taxa_implicita(pv=valor_financiado, pmt=parcela, n=parcelas, fv=0)
   
    # taxa que aparece no contrato
    taxa_contrato = taxa_contrato / 100

    if round(taxa_contrato, 3) != round(taxa_efetiva, 3):
        st.warning('A taxa do contrato não corresponde a taxa efetiva calculada')
    
 
    if taxa_efetiva > 1.5 * tx_media_mercado:
        st.warning(f'''A taxa efetiva é abusiva! Enquanto a taxa efetiva foi de {taxa_efetiva:.2%}, 
                   a taxa média de mercado foi de {tx_media_mercado:.2%}, com a taxa efetiva sendo {(taxa_efetiva/tx_media_mercado):.2} maior que a taxa de mercado. 
                   Já é possível ajuizar quando a taxa é 50% maior que a praticada pelo mercado'''
                   )
    
        
    # tabela conforme o banco 
    
    tbl_prc = calc.tabela_price(valor_financiado, taxa=taxa_efetiva, n=parcelas)
    
    st.title('Conforme o Banco')
    st.subheader(f'Valor financiado: {valor_financiado}')
    st.dataframe(tbl_prc, hide_index=True)
    
    
    # recalculo
    
    tbl_recalc = calc.tabela_price(valor_financiado_recalc, taxa=tx_media_mercado, n=parcelas)
    
    st.title('Conforme o Revisionamento')
    st.subheader(f'Valor financiado Recalculado: {valor_financiado_recalc}')
    st.dataframe(tbl_recalc, hide_index=True)
    
    
    # diferença
    
    total_pago_banco = tbl_prc["parcela_total"].sum()
    total_pago_recalc = tbl_recalc["parcela_total"].sum()

    diferenca_total = total_pago_banco - total_pago_recalc

    juros_banco = tbl_prc["juros"].sum()
    juros_recalc = tbl_recalc["juros"].sum()
    
    st.subheader("Resumo da diferença")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total pago ao banco",
            f"R$ {total_pago_banco:,.2f}"
        )

    with col2:
        st.metric(
            "Total correto",
            f"R$ {total_pago_recalc:,.2f}"
        )

    with col3:
        st.metric(
            "Diferença",
            f"R$ {diferenca_total:,.2f}"
        )
        
    st.subheader("Comparação de Financiamento")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Valor financiado no contrato",
            f"R$ {valor_financiado:,.2f}"
        )

    with col2:
        st.metric(
            "Juros no financiamento recalculado",
            f"R$ {valor_financiado_recalc:,.2f}"
        )
        
        
    st.subheader("Comparação de juros")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Juros pagos no contrato",
            f"R$ {juros_banco:,.2f}"
        )

    with col2:
        st.metric(
            "Juros no financiamento recalculado",
            f"R$ {juros_recalc:,.2f}"
        )
        
    st.subheader("Comparação de taxas")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Taxa do contrato",
            f"{taxa_efetiva:.2%}"
        )

    with col2:
        st.metric(
            "Taxa média de mercado",
            f"{tx_media_mercado:.2%}"
        )

    # diferença entre as taxas (em pontos percentuais)
    excesso = taxa_efetiva - tx_media_mercado

    st.divider()

    if excesso <= 0:
        st.success(
            "A taxa do contrato está igual ou abaixo da taxa média de mercado."
        )

    elif excesso <= 0.5 * tx_media_mercado:
        st.warning(
            f"A taxa do contrato está {excesso:.2%} pontos percentuais acima da taxa média de mercado. "
            "Pode haver indício de cobrança elevada, mas normalmente não caracteriza abusividade."
        )

    else:
        st.error(
            f"A taxa do contrato está {excesso:.2%} pontos percentuais acima da taxa média de mercado. "
            "Diferenças muito elevadas podem indicar possível abusividade e justificar análise jurídica para revisão do financiamento."
        )
        
    
    st.subheader('Metodologia')
    
    st.markdown(""" No recálculo do financiamento, considerou-se como valor 
            financiado o preço do veículo descontada a entrada, acrescido
            apenas do IOF e da tarifa de cadastro. Os demais encargos
            informados foram desconsiderados para fins de simulação.
            A nova simulação foi realizada aplicando-se a taxa média de
            mercado para operações de financiamento de veículos para pessoa 
            física, divulgada pelo Banco Central do Brasil para o período do contrato. 
            Dessa forma, o recálculo permite comparar o contrato original com um cenário
            baseado nas condições médias de mercado.""")